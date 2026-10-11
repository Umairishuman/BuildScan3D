package com.google.ar.core.examples.java.helloar;

import com.google.ar.core.Pose;
import java.util.HashMap;
import java.util.Locale;
import java.util.Map;

/**
 * Live coverage map for capture guidance (IQA tier 2).
 *
 * ARCore raw depth (5 Hz, from CaptureLogger) is back-projected into world space and accumulated in a
 * 10 cm voxel grid. Each voxel remembers from which DIRECTIONS it has been seen (8 azimuth x 2 elevation
 * bins of the voxel->camera ray). 3DGS needs every surface seen from several directions; a surface seen
 * from one direction only reconstructs as smears/floaters when viewed from elsewhere.
 *
 * project() returns the voxels visible in the current view, coloured by how many directions they have:
 *   red = 1 direction, yellow = 2-3, green = >= 4. Unmapped surfaces show no dots.
 * A coarse screen-space z-buffer hides voxels behind nearer surfaces.
 */
public class CoverageMap {
  private static final float VOXEL = 0.10f;
  private static final int STRIDE = 3;            // depth pixel stride (160x90 raw depth)
  private static final int MIN_CONF = 128;         // raw depth confidence 0-255
  private static final float MAX_DEPTH = 5.0f;

  public static final int RED = 0xCCE53935, YELLOW = 0xCCFDD835, GREEN = 0xCC43A047;

  private final HashMap<Long, int[]> cells = new HashMap<>();   // key -> {directionMask, hits}

  public synchronized void clear() {
    cells.clear();
  }

  private static long key(int x, int y, int z) {
    return ((long) (x + 32768) << 32) | ((long) (y + 32768) << 16) | (long) (z + 32768);
  }

  /** depth: uint16 little-endian mm (w*h), conf: uint8; intrinsics of the CPU image (imgW x imgH). */
  public void addDepth(byte[] depth, byte[] conf, int w, int h, Pose pose,
                       float[] focal, float[] principal, int imgW, int imgH) {
    float sx = (float) w / imgW, sy = (float) h / imgH;
    float fx = focal[0] * sx, fy = focal[1] * sy, cx = principal[0] * sx, cy = principal[1] * sy;
    float[] cam = pose.getTranslation();
    float[] pc = new float[3];
    synchronized (this) {
      for (int v = 0; v < h; v += STRIDE) {
        for (int u = 0; u < w; u += STRIDE) {
          int i = v * w + u;
          if ((conf[i] & 0xFF) < MIN_CONF) continue;
          float z = ((depth[2 * i] & 0xFF) | ((depth[2 * i + 1] & 0xFF) << 8)) / 1000f;
          if (z < 0.2f || z > MAX_DEPTH) continue;
          // sensor image (landscape) -> OpenGL camera frame (x right, y up, looking -z)
          pc[0] = (u + 0.5f - cx) / fx * z;
          pc[1] = -(v + 0.5f - cy) / fy * z;
          pc[2] = -z;
          float[] p = pose.transformPoint(pc);
          float dx = cam[0] - p[0], dy = cam[1] - p[1], dz = cam[2] - p[2];
          float len = (float) Math.sqrt(dx * dx + dy * dy + dz * dz);
          double az = Math.atan2(dx, dz) + Math.PI;                       // 0..2pi
          int azBin = Math.min(7, (int) (az / (Math.PI / 4)));
          int elBin = (dy / len) > 0.17f ? 1 : 0;                          // looking down at it vs level/up
          int bit = 1 << (azBin * 2 + elBin);
          long k = key((int) Math.floor(p[0] / VOXEL), (int) Math.floor(p[1] / VOXEL), (int) Math.floor(p[2] / VOXEL));
          int[] c = cells.get(k);
          if (c == null) {
            cells.put(k, new int[] {bit, 1});
          } else {
            c[0] |= bit;
            c[1]++;
          }
        }
      }
    }
  }

  /** Result of a projection: normalised device coords (x right, y up, -1..1) + colours. */
  public static class Projection {
    public float[] ndc = new float[0];
    public int[] colors = new int[0];
    public int n = 0;
  }

  /** Project voxels into the current view. mvp = projection * view (column-major, from ARCore). */
  public Projection project(float[] mvp, float[] camPos) {
    final int GW = 48, GH = 27;
    Projection out = new Projection();
    int cap;
    float[] xs, ys, ds;
    int[] cols;
    synchronized (this) {
      cap = cells.size();
      xs = new float[cap]; ys = new float[cap]; ds = new float[cap]; cols = new int[cap];
      int m = 0;
      for (Map.Entry<Long, int[]> e : cells.entrySet()) {
        long k = e.getKey();
        float x = (((k >> 32) & 0xFFFF) - 32768 + 0.5f) * VOXEL;
        float y = (((k >> 16) & 0xFFFF) - 32768 + 0.5f) * VOXEL;
        float z = ((k & 0xFFFF) - 32768 + 0.5f) * VOXEL;
        float cw = mvp[3] * x + mvp[7] * y + mvp[11] * z + mvp[15];
        if (cw <= 0.05f) continue;
        float nx = (mvp[0] * x + mvp[4] * y + mvp[8] * z + mvp[12]) / cw;
        float ny = (mvp[1] * x + mvp[5] * y + mvp[9] * z + mvp[13]) / cw;
        if (nx < -1 || nx > 1 || ny < -1 || ny > 1) continue;
        float dx = x - camPos[0], dy = y - camPos[1], dz = z - camPos[2];
        float d = (float) Math.sqrt(dx * dx + dy * dy + dz * dz);
        if (d > MAX_DEPTH) continue;
        int dirs = Integer.bitCount(e.getValue()[0]);
        xs[m] = nx; ys[m] = ny; ds[m] = d;
        cols[m] = dirs >= 4 ? GREEN : (dirs >= 2 ? YELLOW : RED);
        m++;
      }
      cap = m;
    }
    // coarse screen-space z-buffer: keep voxels within 30 cm of the nearest one in their screen cell
    float[] near = new float[GW * GH];
    java.util.Arrays.fill(near, Float.MAX_VALUE);
    int[] cellOf = new int[cap];
    for (int i = 0; i < cap; i++) {
      int gx = Math.min(GW - 1, (int) ((xs[i] + 1) * 0.5f * GW));
      int gy = Math.min(GH - 1, (int) ((ys[i] + 1) * 0.5f * GH));
      cellOf[i] = gy * GW + gx;
      if (ds[i] < near[cellOf[i]]) near[cellOf[i]] = ds[i];
    }
    out.ndc = new float[cap * 2];
    out.colors = new int[cap];
    int n = 0;
    for (int i = 0; i < cap; i++) {
      if (ds[i] > near[cellOf[i]] + 0.3f) continue;
      out.ndc[2 * n] = xs[i]; out.ndc[2 * n + 1] = ys[i]; out.colors[n] = cols[i];
      n++;
    }
    out.n = n;
    return out;
  }

  /** e.g. "Mapped 1234 cells: 61% well covered (>=4 directions), 22% partly, 17% one direction". */
  public synchronized String summary() {
    int good = 0, mid = 0, bad = 0;
    for (int[] c : cells.values()) {
      int d = Integer.bitCount(c[0]);
      if (d >= 4) good++; else if (d >= 2) mid++; else bad++;
    }
    int t = Math.max(1, good + mid + bad);
    return String.format(Locale.US, "Mapped %d cells: %d%% well covered (>=4 directions), %d%% partly, %d%% one direction only",
        good + mid + bad, 100 * good / t, 100 * mid / t, 100 * bad / t);
  }
}
