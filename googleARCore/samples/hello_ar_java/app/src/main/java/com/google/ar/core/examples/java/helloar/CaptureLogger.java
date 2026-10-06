package com.google.ar.core.examples.java.helloar;

import android.media.Image;
import android.util.Log;
import com.google.ar.core.Camera;
import com.google.ar.core.CameraConfig;
import com.google.ar.core.CameraIntrinsics;
import com.google.ar.core.Frame;
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
 *   depth/<timestamp_ns>.depth  raw uint16 mm, depth/<timestamp_ns>.conf  uint8 (ARCore raw depth)
 *   meta.json     camera config, image + depth resolution, device
 */
public class CaptureLogger {
  private static final String TAG = "CaptureLogger";
  private static final long DEPTH_INTERVAL_NS = 200_000_000L; // 5 Hz

  private final File dir;
  private final ExecutorService io = Executors.newSingleThreadExecutor();
  private BufferedWriter poses, tracking, points;
  private long lastDepthTs = 0;
  private boolean wroteMeta = false;

  public CaptureLogger(File dir) throws IOException {
    this.dir = dir;
    new File(dir, "depth").mkdirs();
    poses = new BufferedWriter(new FileWriter(new File(dir, "poses.csv")), 1 << 16);
    tracking = new BufferedWriter(new FileWriter(new File(dir, "tracking.csv")), 1 << 16);
    points = new BufferedWriter(new FileWriter(new File(dir, "points.csv")), 1 << 16);
  }

  /** Call once per frame from the GL thread, after session.update(). */
  public void onFrame(Session session, Frame frame, Camera camera) {
    final long ts = frame.getTimestamp();
    final TrackingState state = camera.getTrackingState();
    final String reason = camera.getTrackingFailureReason().name();
    post(() -> write(tracking, ts + "," + state.name() + "," + reason + "\n"));

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
      if (saveRawDepth(frame, ts)) lastDepthTs = ts;
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
      if (conf < 0.3f) continue;   // keep more points than before; confidence is stored for filtering
      sb.append(ts).append(',').append(p.get(i)).append(',').append(p.get(i + 1)).append(',')
          .append(p.get(i + 2)).append(',').append(ids.get(j)).append(',').append(conf).append('\n');
    }
    final String s = sb.toString();
    post(() -> write(points, s));
  }

  private boolean saveRawDepth(Frame frame, long ts) {
    try (Image depth = frame.acquireRawDepthImage16Bits();
         Image conf = frame.acquireRawDepthConfidenceImage()) {
      final byte[] d = copyPlane(depth);
      final byte[] cf = copyPlane(conf);
      final int w = depth.getWidth(), h = depth.getHeight();
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
    post(() -> {
      try {
        poses.close();
        tracking.close();
        points.close();
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
