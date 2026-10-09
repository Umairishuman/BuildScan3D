package com.google.ar.core.examples.java.helloar;

import android.media.Image;
import com.google.ar.core.Camera;
import com.google.ar.core.Frame;
import com.google.ar.core.Pose;
import com.google.ar.core.TrackingFailureReason;
import com.google.ar.core.TrackingState;
import com.google.ar.core.exceptions.NotYetAvailableException;
import java.nio.ByteBuffer;
import java.util.Arrays;
import java.util.Locale;

/**
 * Live image-quality assessment (IQA) for capture. Runs on the GL thread once per frame and tells
 * the user, in priority order, what is wrong with the footage right now:
 *   1. tracking lost / degraded (ARCore state + failure reason)
 *   2. moving / turning too fast (pose delta between frames -> calibration-free motion-blur predictor)
 *   3. too little texture (absolute Laplacian variance; plain walls/ceilings -> tracking loss), then
 *      blurry image (Laplacian variance relative to the recent median)
 *   4. too dark / overexposed (mean luma, saturated-pixel fraction)
 * Plus a lightweight coverage checklist: has the user looked at the ceiling, the floor, and all
 * horizontal directions while recording.
 */
public class QualityMonitor {
  public enum Level { GOOD, WARN, BAD }

  public static class Result {
    public Level level = Level.GOOD;
    public String message = "";
    public float sharpness = -1, sharpnessRel = -1, brightness = -1, overexposed = -1;
    public float angSpeedDeg, linSpeed;
    public boolean tracking;
    public String csv(long ts) {
      return String.format(Locale.US, "%d,%s,%.1f,%.3f,%.1f,%.3f,%.2f,%.3f,%d\n", ts, level.name(), sharpness,
          sharpnessRel, brightness, overexposed, angSpeedDeg, linSpeed, tracking ? 1 : 0);
    }
  }

  // ---- thresholds (tuned for handheld 30 fps indoor capture) ----
  private static final float ANG_WARN = 30f, ANG_BAD = 60f;       // deg/s
  private static final float LIN_WARN = 0.40f, LIN_BAD = 0.80f;   // m/s
  private static final float SHARP_WARN = 0.60f, SHARP_BAD = 0.40f; // fraction of recent median sharpness
  private static final float DARK_WARN = 60f, DARK_BAD = 35f;     // mean luma 0..255
  // absolute texture (Laplacian variance of the subsampled Y plane). Calibrated on roomAttemptSadness2:
  // 2 s before ARCore lost tracking the median was 14.5 vs 63 during normal tracking; < 15 flags ~52% of
  // pre-loss frames and ~2% of normal frames. Plain white walls / ceilings are the main cause of lost
  // tracking, failed stereo depth and floating geometry, so this warns BEFORE tracking drops.
  private static final float TEX_WARN = 22f, TEX_BAD = 13f;
  private static final float OVER_WARN = 0.12f, OVER_BAD = 0.25f; // fraction of pixels >= 245
  private static final int IMAGE_EVERY = 3;                       // analyse every 3rd camera image
  private static final int STEP = 5;                              // pixel subsampling stride
  private static final float CEIL_PITCH = 35f, FLOOR_PITCH = -35f;// deg
  private static final int COVER_FRAMES = 45;                     // ~1.5 s of looking counts as covered

  private Pose lastPose = null;
  private long lastTs = 0;
  private float angEma = 0, linEma = 0;
  private int frameCount = 0;
  private final float[] sharpHist = new float[90];
  private int sharpN = 0, sharpIdx = 0;
  private float lastSharp = -1, lastSharpRel = -1, lastBright = -1, lastOver = -1;

  // session stats (only while recording)
  private int nGood, nWarn, nBad, ceilingFrames, floorFrames;
  private final int[] yawFrames = new int[8];

  public void resetSession() {
    nGood = nWarn = nBad = ceilingFrames = floorFrames = 0;
    Arrays.fill(yawFrames, 0);
  }

  public Result update(Frame frame, Camera camera, boolean recording) {
    Result r = new Result();
    long ts = frame.getTimestamp();
    r.tracking = camera.getTrackingState() == TrackingState.TRACKING;

    // ---- motion from pose deltas ----
    if (r.tracking) {
      Pose p = camera.getPose();
      if (lastPose != null && ts > lastTs) {
        float dt = (ts - lastTs) / 1e9f;
        if (dt > 0 && dt < 0.5f) {
          float[] a = p.getTranslation(), b = lastPose.getTranslation();
          float dx = a[0] - b[0], dy = a[1] - b[1], dz = a[2] - b[2];
          float lin = (float) Math.sqrt(dx * dx + dy * dy + dz * dz) / dt;
          float[] qa = p.getRotationQuaternion(), qb = lastPose.getRotationQuaternion();
          float dot = Math.abs(qa[0] * qb[0] + qa[1] * qb[1] + qa[2] * qb[2] + qa[3] * qb[3]);
          float ang = (float) Math.toDegrees(2 * Math.acos(Math.min(1f, dot))) / dt;
          angEma = 0.7f * angEma + 0.3f * ang;
          linEma = 0.7f * linEma + 0.3f * lin;
        }
      }
      lastPose = p;
      lastTs = ts;
      if (recording) updateCoverage(p);
    } else {
      lastPose = null;
    }
    r.angSpeedDeg = angEma;
    r.linSpeed = linEma;

    // ---- image statistics (every few frames, cheap subsampled pass) ----
    if (frameCount++ % IMAGE_EVERY == 0) analyseImage(frame);
    r.sharpness = lastSharp; r.sharpnessRel = lastSharpRel; r.brightness = lastBright; r.overexposed = lastOver;

    // ---- decide, highest priority first ----
    if (!r.tracking) {
      r.level = Level.BAD;
      r.message = trackingMessage(camera.getTrackingFailureReason());
    } else if (angEma > ANG_BAD || linEma > LIN_BAD) {
      r.level = Level.BAD;
      r.message = angEma > ANG_BAD ? "Turning far too fast - slow down" : "Moving far too fast - slow down";
    } else if (lastSharp >= 0 && lastSharp < TEX_BAD && lastBright > DARK_BAD) {
      r.level = Level.BAD;
      r.message = "Too plain - include edges, corners or objects";
    } else if (lastSharpRel >= 0 && lastSharpRel < SHARP_BAD) {
      r.level = Level.BAD;
      r.message = "Image blurry - hold steady";
    } else if (lastBright >= 0 && lastBright < DARK_BAD) {
      r.level = Level.BAD;
      r.message = "Too dark - add light";
    } else if (lastOver >= OVER_BAD) {
      r.level = Level.BAD;
      r.message = "Overexposed - avoid windows / lamps";
    } else if (angEma > ANG_WARN || linEma > LIN_WARN) {
      r.level = Level.WARN;
      r.message = angEma > ANG_WARN ? "Turning a bit fast" : "Moving a bit fast";
    } else if (lastSharp >= 0 && lastSharp < TEX_WARN && lastBright > DARK_BAD) {
      r.level = Level.WARN;
      r.message = "Low texture - keep some detail in view";
    } else if (lastSharpRel >= 0 && lastSharpRel < SHARP_WARN) {
      r.level = Level.WARN;
      r.message = "Slightly blurry";
    } else if (lastBright >= 0 && lastBright < DARK_WARN) {
      r.level = Level.WARN;
      r.message = "A bit dark";
    } else if (lastOver >= OVER_WARN) {
      r.level = Level.WARN;
      r.message = "Bright spots - may overexpose";
    } else {
      r.level = Level.GOOD;
      r.message = "Good - keep going";
    }

    if (recording) {
      if (r.level == Level.GOOD) nGood++; else if (r.level == Level.WARN) nWarn++; else nBad++;
    }
    return r;
  }

  private void analyseImage(Frame frame) {
    try (Image img = frame.acquireCameraImage()) {
      Image.Plane yPlane = img.getPlanes()[0];
      ByteBuffer y = yPlane.getBuffer();
      int rs = yPlane.getRowStride(), ps = yPlane.getPixelStride();
      int w = img.getWidth(), h = img.getHeight();
      double sum = 0, sumL = 0, sumL2 = 0;
      int n = 0, over = 0;
      for (int yy = STEP; yy < h - STEP; yy += STEP) {
        int row = yy * rs;
        for (int xx = STEP; xx < w - STEP; xx += STEP) {
          int i = row + xx * ps;
          int c = y.get(i) & 0xFF;
          int lap = 4 * c - (y.get(i - rs) & 0xFF) - (y.get(i + rs) & 0xFF)
              - (y.get(i - ps) & 0xFF) - (y.get(i + ps) & 0xFF);
          sum += c; sumL += lap; sumL2 += (double) lap * lap;
          if (c >= 245) over++;
          n++;
        }
      }
      if (n == 0) return;
      float mean = (float) (sum / n);
      float varL = (float) (sumL2 / n - (sumL / n) * (sumL / n));
      lastBright = mean;
      lastOver = (float) over / n;
      lastSharp = varL;
      // sharpness relative to the recent median (scene-independent); ignore very dark frames
      if (mean > DARK_BAD && varL >= TEX_BAD) {
        sharpHist[sharpIdx] = varL; sharpIdx = (sharpIdx + 1) % sharpHist.length;
        sharpN = Math.min(sharpN + 1, sharpHist.length);
      }
      if (sharpN >= 15) {
        float[] s = Arrays.copyOf(sharpHist, sharpN);
        Arrays.sort(s);
        float med = s[sharpN / 2];
        lastSharpRel = med > 1e-3f ? varL / med : -1;
      }
    } catch (NotYetAvailableException | IllegalStateException e) {
      // camera image not ready this frame
    }
  }

  private void updateCoverage(Pose p) {
    // camera looks along its -Z axis (OpenGL); world +Y is up
    float[] fwd = p.getZAxis();
    float fx = -fwd[0], fy = -fwd[1], fz = -fwd[2];
    float pitch = (float) Math.toDegrees(Math.asin(Math.max(-1f, Math.min(1f, fy))));
    if (pitch > CEIL_PITCH) ceilingFrames++;
    else if (pitch < FLOOR_PITCH) floorFrames++;
    else {
      double yaw = Math.toDegrees(Math.atan2(fx, -fz)) + 360.0;
      yawFrames[(int) ((yaw + 22.5) / 45.0) % 8]++;
    }
  }

  public int directionsCovered() {
    int c = 0;
    for (int f : yawFrames) if (f >= COVER_FRAMES) c++;
    return c;
  }

  public String coverageText() {
    return String.format(Locale.US, "Ceiling %s  ·  Floor %s  ·  Directions %d/8",
        ceilingFrames >= COVER_FRAMES ? "✓" : "✗", floorFrames >= COVER_FRAMES ? "✓" : "✗",
        directionsCovered());
  }

  public String summary() {
    int total = Math.max(1, nGood + nWarn + nBad);
    return String.format(Locale.US, "Good %d%% · OK %d%% · Bad %d%%\n%s",
        100 * nGood / total, 100 * nWarn / total, 100 * nBad / total, coverageText());
  }

  private static String trackingMessage(TrackingFailureReason reason) {
    switch (reason) {
      case INSUFFICIENT_LIGHT: return "Tracking lost - too dark";
      case EXCESSIVE_MOTION: return "Tracking lost - moving too fast";
      case INSUFFICIENT_FEATURES: return "Tracking lost - aim at more texture";
      case CAMERA_UNAVAILABLE: return "Camera unavailable";
      case BAD_STATE: return "Tracking error - restart recording";
      default: return "Tracking lost - move slowly, look at textured areas";
    }
  }
}
