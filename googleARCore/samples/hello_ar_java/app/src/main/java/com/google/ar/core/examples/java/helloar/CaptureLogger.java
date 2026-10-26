package com.google.ar.core.examples.java.helloar;

import android.media.Image;
import android.util.Log;
import com.google.ar.core.Camera;
import com.google.ar.core.CameraConfig;
import com.google.ar.core.CameraIntrinsics;
import com.google.ar.core.Anchor;
import com.google.ar.core.Frame;
import com.google.ar.core.ImageMetadata;
import com.google.ar.core.PointCloud;
import com.google.ar.core.Pose;
import com.google.ar.core.Session;
import com.google.ar.core.TrackingState;
import com.google.ar.core.exceptions.NotYetAvailableException;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileOutputStream;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.FloatBuffer;
import java.nio.IntBuffer;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

/**
 * Writes the capture side-channel (poses, tracking state, feature points, ARCore depth) from a
 * background thread so the GL/AR thread never blocks on file I/O (blocking caused dropped poses).
 *
 * Files in the scan folder (dataset.mp4 is written by ARCore's recorder):
 *   poses.csv     timestamp_ns,tx,ty,tz,qx,qy,qz,qw,fx,fy,cx,cy   (camera.getPose(), image intrinsics)
 *   tracking.csv  timestamp_ns,state,failure_reason              (every frame, incl. non-TRACKING)
 *   points.csv    timestamp_ns,x,y,z,id,confidence                (world-space feature points)
 *   quality.csv   live IQA per frame (level, sharpness, brightness, motion; see QualityMonitor)
 *   camera.csv    timestamp_ns,exposure_ns,rolling_shutter_skew_ns,frame_duration_ns,iso,focus_distance_diopter,
 *                 ae_state,awb_state,lens_state   (per-frame sensor metadata: exposure time + rolling-shutter
 *                 readout are what motion-blur / rolling-shutter modelling in 3DGS needs; -1 = not reported)
 *   anchors.csv   timestamp_ns,anchor_id,tracking_state,tx,ty,tz,qx,qy,qz,qw   (5 Hz) An anchor is dropped at
 *                 the camera every ANCHOR_INTERVAL_NS. ARCore moves anchors when it silently corrects its world
 *                 frame (map merge / loop closure); a jump in an anchor's logged pose = a re-anchor event, and
 *                 its size is the correction (newRoomAttemptSadness had an unlogged ~1 m / 28 deg one).
 *   lens_metadata.json, camera_characteristics.json   lens calibration/distortion (ARCore metadata, Camera2)
 *   depth/<timestamp_ns>.depth  raw uint16 mm, depth/<timestamp_ns>.conf  uint8 (ARCore raw depth)
 *   meta.json     camera config, image + depth resolution, device
 */
public class CaptureLogger {
  private static final String TAG = "CaptureLogger";
  private static final long DEPTH_INTERVAL_NS = 200_000_000L; // 5 Hz
  private static final long ANCHOR_INTERVAL_NS = 10_000_000_000L; // new reference anchor every 10 s
  private static final long ANCHOR_LOG_NS = 200_000_000L;         // log all anchors at 5 Hz
  private static final int MAX_ANCHORS = 40;

  private final File dir;
  private final ExecutorService io = Executors.newSingleThreadExecutor();
  private BufferedWriter poses, tracking, points, quality, cameraMeta, anchorsOut;
  private long lastDepthTs = 0;
  private long lastDepthImageTs = -1;
  private final List<Anchor> anchors = new ArrayList<>();
  private long lastAnchorCreateTs = 0, lastAnchorLogTs = 0;
  private boolean wroteLensMeta = false;
  private boolean wroteMeta = false;
  private CoverageMap coverage = null;

  /** Live coverage map fed from the raw depth stream (may be null). */
  public void setCoverage(CoverageMap c) {
    coverage = c;
  }

  public CaptureLogger(File dir) throws IOException {
    this.dir = dir;
    new File(dir, "depth").mkdirs();
    poses = new BufferedWriter(new FileWriter(new File(dir, "poses.csv")), 1 << 16);
    tracking = new BufferedWriter(new FileWriter(new File(dir, "tracking.csv")), 1 << 16);
    points = new BufferedWriter(new FileWriter(new File(dir, "points.csv")), 1 << 16);
    quality = new BufferedWriter(new FileWriter(new File(dir, "quality.csv")), 1 << 16);
    quality.write("timestamp_ns,level,sharpness,sharpness_rel,brightness,overexposed_frac,ang_speed_deg_s,lin_speed_m_s,tracking,pred_blur_px,exposure_ms\n");
    cameraMeta = new BufferedWriter(new FileWriter(new File(dir, "camera.csv")), 1 << 16);
    cameraMeta.write("timestamp_ns,exposure_ns,rolling_shutter_skew_ns,frame_duration_ns,iso,focus_distance_diopter,ae_state,awb_state,lens_state\n");
    anchorsOut = new BufferedWriter(new FileWriter(new File(dir, "anchors.csv")), 1 << 16);
    anchorsOut.write("timestamp_ns,anchor_id,tracking_state,tx,ty,tz,qx,qy,qz,qw\n");
  }

  /** Per-frame live-IQA record (see QualityMonitor). */
  public void logQuality(String line) {
    post(() -> write(quality, line));
  }

  /** Call once per frame from the GL thread, after session.update(). */
  public void onFrame(Session session, Frame frame, Camera camera) {
    final long ts = frame.getTimestamp();
    final TrackingState state = camera.getTrackingState();
    final String reason = camera.getTrackingFailureReason().name();
    post(() -> write(tracking, ts + "," + state.name() + "," + reason + "\n"));
    logSensorMetadata(frame, ts);
    logAnchors(session, camera, ts, state);

    if (state != TrackingState.TRACKING) return;

    Pose pose = camera.getPose();
    float[] t = pose.getTranslation();
    float[] q = pose.getRotationQuaternion();
    CameraIntrinsics intr = camera.getImageIntrinsics();
    float[] f = intr.getFocalLength();
    float[] c = intr.getPrincipalPoint();
    final String line = String.format(Locale.US, "%d,%.6f,%.6f,%.6f,%.7f,%.7f,%.7f,%.7f,%.4f,%.4f,%.4f,%.4f\n",
        ts, t[0], t[1], t[2], q[0], q[1], q[2], q[3], f[0], f[1], c[0], c[1]);
    post(() -> write(poses, line));

    if (!wroteMeta) {
      wroteMeta = true;
      writeMeta(session, intr);
    }
    if (ts - lastDepthTs >= DEPTH_INTERVAL_NS) {
      if (saveRawDepth(frame, ts, pose, intr)) lastDepthTs = ts;
    }
  }

  /** Call from the GL thread when a new point cloud is available. */
  public void onPointCloud(PointCloud pc) {
    final long ts = pc.getTimestamp();
    FloatBuffer p = pc.getPoints();
    IntBuffer ids = pc.getIds();
    StringBuilder sb = new StringBuilder();
    for (int i = 0, j = 0; i + 3 < p.limit(); i += 4, j++) {
      float conf = p.get(i + 3);
      // !(conf >= 0.3f) also rejects NaN (NaN < 0.3f is false, which let NaN rows through before)
      if (!(conf >= 0.3f) || Float.isNaN(p.get(i)) || Float.isNaN(p.get(i + 1)) || Float.isNaN(p.get(i + 2))) continue;
      sb.append(ts).append(',').append(p.get(i)).append(',').append(p.get(i + 1)).append(',')
          .append(p.get(i + 2)).append(',').append(ids.get(j)).append(',').append(conf).append('\n');
    }
    final String s = sb.toString();
    post(() -> write(points, s));
  }

  private boolean saveRawDepth(Frame frame, long ts, Pose pose, CameraIntrinsics intr) {
    try (Image depth = frame.acquireRawDepthImage16Bits();
         Image conf = frame.acquireRawDepthConfidenceImage()) {
      if (depth.getTimestamp() == lastDepthImageTs) {
        return false;                                   // ARCore has not produced a new depth map yet
      }
      lastDepthImageTs = depth.getTimestamp();
      final byte[] d = copyPlane(depth);
      final byte[] cf = copyPlane(conf);
      final int w = depth.getWidth(), h = depth.getHeight();
      final CoverageMap cov = coverage;
      if (cov != null) {
        final float[] fl = intr.getFocalLength(), pp = intr.getPrincipalPoint();
        final int[] dims = intr.getImageDimensions();
        post(() -> cov.addDepth(d, cf, w, h, pose, fl, pp, dims[0], dims[1]));
      }
      post(() -> {
        writeBytes(new File(dir, "depth/" + ts + ".depth"), d);
        writeBytes(new File(dir, "depth/" + ts + ".conf"), cf);
        if (!new File(dir, "depth/size.txt").exists()) {
          writeBytes(new File(dir, "depth/size.txt"), (w + " " + h + "\n").getBytes());
        }
      });
      return true;
    } catch (NotYetAvailableException | IllegalStateException e) {
      return false; // depth not ready yet / unsupported device
    }
  }

  private static byte[] copyPlane(Image img) {
    Image.Plane plane = img.getPlanes()[0];
    ByteBuffer buf = plane.getBuffer();
    int rowBytes = img.getWidth() * plane.getPixelStride();
    byte[] out = new byte[rowBytes * img.getHeight()];
    for (int y = 0; y < img.getHeight(); y++) {
      buf.position(y * plane.getRowStride());
      buf.get(out, y * rowBytes, rowBytes);
    }
    return out;
  }

  private static long metaLong(ImageMetadata md, int key) {
    try {
      return md.getLong(key);
    } catch (Exception e) {
      return -1;
    }
  }

  private static int metaInt(ImageMetadata md, int key) {
    try {
      return md.getInt(key);
    } catch (Exception e) {
      return -1;
    }
  }

  private static String metaFloats(ImageMetadata md, int key) {
    try {
      return arr(md.getFloatArray(key));
    } catch (Exception e) {
      return "null";
    }
  }

  /** Per-frame exposure / rolling-shutter / ISO / focus metadata -> camera.csv. */
  private void logSensorMetadata(Frame frame, long ts) {
    final ImageMetadata md;
    try {
      md = frame.getImageMetadata();
    } catch (Exception e) {
      return;                                           // not available for this frame
    }
    float focus = -1;
    try {
      focus = md.getFloat(ImageMetadata.LENS_FOCUS_DISTANCE);
    } catch (Exception ignored) {
    }
    final String line = String.format(Locale.US, "%d,%d,%d,%d,%d,%.4f,%d,%d,%d\n", ts,
        metaLong(md, ImageMetadata.SENSOR_EXPOSURE_TIME), metaLong(md, ImageMetadata.SENSOR_ROLLING_SHUTTER_SKEW),
        metaLong(md, ImageMetadata.SENSOR_FRAME_DURATION), metaInt(md, ImageMetadata.SENSOR_SENSITIVITY), focus,
        metaInt(md, ImageMetadata.CONTROL_AE_STATE), metaInt(md, ImageMetadata.CONTROL_AWB_STATE),
        metaInt(md, ImageMetadata.LENS_STATE));
    post(() -> write(cameraMeta, line));
    if (!wroteLensMeta) {                               // lens calibration as ARCore reports it per frame
      wroteLensMeta = true;
      final String json = "{\n \"image_metadata_lens_intrinsic_calibration\": " + metaFloats(md, ImageMetadata.LENS_INTRINSIC_CALIBRATION)
          + ",\n \"image_metadata_lens_radial_distortion\": " + metaFloats(md, ImageMetadata.LENS_RADIAL_DISTORTION)
          + ",\n \"image_metadata_lens_focal_length_mm\": " + metaFloats(md, ImageMetadata.LENS_FOCAL_LENGTH) + "\n}\n";
      post(() -> writeBytes(new File(dir, "lens_metadata.json"), json.getBytes()));
    }
  }

  /** Re-anchor detection: drop a reference anchor every 10 s and log every anchor's pose at 5 Hz. */
  private void logAnchors(Session session, Camera camera, long ts, TrackingState state) {
    if (state == TrackingState.TRACKING && anchors.size() < MAX_ANCHORS
        && (anchors.isEmpty() || ts - lastAnchorCreateTs >= ANCHOR_INTERVAL_NS)) {
      try {
        anchors.add(session.createAnchor(camera.getPose()));
        lastAnchorCreateTs = ts;
      } catch (Exception e) {
        Log.w(TAG, "anchor creation failed", e);
      }
    }
    if (anchors.isEmpty() || ts - lastAnchorLogTs < ANCHOR_LOG_NS) return;
    lastAnchorLogTs = ts;
    StringBuilder sb = new StringBuilder();
    for (int i = 0; i < anchors.size(); i++) {
      Anchor a = anchors.get(i);
      Pose p = a.getPose();
      float[] t = p.getTranslation(), q = p.getRotationQuaternion();
      sb.append(String.format(Locale.US, "%d,%d,%s,%.6f,%.6f,%.6f,%.7f,%.7f,%.7f,%.7f\n", ts, i, a.getTrackingState().name(),
          t[0], t[1], t[2], q[0], q[1], q[2], q[3]));
    }
    final String s = sb.toString();
    post(() -> write(anchorsOut, s));
  }

  /** Factory lens calibration of the camera ARCore uses (Camera2), once per recording. */
  public void writeCameraCharacteristics(android.content.Context ctx, Session session) {
    try {
      String id = session.getCameraConfig().getCameraId();
      android.hardware.camera2.CameraManager cm = ctx.getSystemService(android.hardware.camera2.CameraManager.class);
      android.hardware.camera2.CameraCharacteristics ch = cm.getCameraCharacteristics(id);
      StringBuilder sb = new StringBuilder("{\n");
      sb.append(" \"camera_id\": \"").append(id).append("\",\n");
      sb.append(" \"lens_intrinsic_calibration_fx_fy_cx_cy_s\": ")
          .append(arr(ch.get(android.hardware.camera2.CameraCharacteristics.LENS_INTRINSIC_CALIBRATION))).append(",\n");
      if (android.os.Build.VERSION.SDK_INT >= 28) {
        sb.append(" \"lens_distortion_k1_k2_k3_p1_p2\": ")
            .append(arr(ch.get(android.hardware.camera2.CameraCharacteristics.LENS_DISTORTION))).append(",\n");
      }
      sb.append(" \"lens_focal_lengths_mm\": ")
          .append(arr(ch.get(android.hardware.camera2.CameraCharacteristics.LENS_INFO_AVAILABLE_FOCAL_LENGTHS))).append(",\n");
      android.util.SizeF phys = ch.get(android.hardware.camera2.CameraCharacteristics.SENSOR_INFO_PHYSICAL_SIZE);
      sb.append(" \"sensor_physical_size_mm\": ").append(phys == null ? "null" : "[" + phys.getWidth() + ", " + phys.getHeight() + "]").append(",\n");
      android.graphics.Rect act = ch.get(android.hardware.camera2.CameraCharacteristics.SENSOR_INFO_ACTIVE_ARRAY_SIZE);
      sb.append(" \"sensor_active_array\": ")
          .append(act == null ? "null" : "[" + act.left + ", " + act.top + ", " + act.right + ", " + act.bottom + "]").append(",\n");
      Integer src = ch.get(android.hardware.camera2.CameraCharacteristics.SENSOR_INFO_TIMESTAMP_SOURCE);
      sb.append(" \"sensor_timestamp_source\": ").append(src == null ? "null" : src.toString()).append(",\n");
      sb.append(" \"note\": \"Camera2 intrinsics are in sensor active-array pixels; ARCore images are a scaled/cropped view\"\n}\n");
      final String json = sb.toString();
      post(() -> writeBytes(new File(dir, "camera_characteristics.json"), json.getBytes()));
    } catch (Exception e) {
      Log.w(TAG, "camera characteristics unavailable", e);
    }
  }

  private static String arr(float[] v) {
    if (v == null) return "null";
    StringBuilder sb = new StringBuilder("[");
    for (int i = 0; i < v.length; i++) sb.append(i > 0 ? ", " : "").append(v[i]);
    return sb.append("]").toString();
  }

  private void writeMeta(Session session, CameraIntrinsics intr) {
    CameraConfig cfg = session.getCameraConfig();
    int[] dims = intr.getImageDimensions();
    final String json = String.format(Locale.US,
        "{\n \"device\": \"%s %s\",\n \"cpu_image_size\": [%d, %d],\n \"texture_size\": [%d, %d],\n"
            + " \"fps_range\": [%d, %d],\n \"intrinsics_image_dimensions\": [%d, %d],\n"
            + " \"pose_convention\": \"camera.getPose(): c2w, OpenGL camera axes, sensor (landscape) orientation\",\n"
            + " \"depth_format\": \"uint16 little-endian millimetres, size in depth/size.txt; .conf uint8 0-255\"\n}\n",
        android.os.Build.MANUFACTURER, android.os.Build.MODEL,
        cfg.getImageSize().getWidth(), cfg.getImageSize().getHeight(),
        cfg.getTextureSize().getWidth(), cfg.getTextureSize().getHeight(),
        cfg.getFpsRange().getLower(), cfg.getFpsRange().getUpper(), dims[0], dims[1]);
    post(() -> writeBytes(new File(dir, "meta.json"), json.getBytes()));
  }

  private static void write(BufferedWriter w, String s) {
    try {
      w.write(s);
    } catch (IOException e) {
      Log.e(TAG, "write failed", e);
    }
  }

  private static void writeBytes(File f, byte[] b) {
    try (FileOutputStream o = new FileOutputStream(f)) {
      o.write(b);
    } catch (IOException e) {
      Log.e(TAG, "write failed " + f, e);
    }
  }

  private void post(Runnable r) {
    try {
      io.execute(r);
    } catch (java.util.concurrent.RejectedExecutionException ignored) {
      // logger already closed; a late frame from the GL thread is dropped
    }
  }

  /** Flush and close everything; blocks until pending writes finish. */
  public void close() {
    for (Anchor a : anchors) {
      try {
        a.detach();
      } catch (Exception ignored) {
      }
    }
    anchors.clear();
    post(() -> {
      try {
        poses.close();
        tracking.close();
        points.close();
        quality.close();
        cameraMeta.close();
        anchorsOut.close();
      } catch (IOException e) {
        Log.e(TAG, "close failed", e);
      }
    });
    io.shutdown();
    try {
      io.awaitTermination(10, TimeUnit.SECONDS);
    } catch (InterruptedException ignored) {
    }
  }
}
