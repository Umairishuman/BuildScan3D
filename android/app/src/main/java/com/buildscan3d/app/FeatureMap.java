package com.buildscan3d.app;

import com.google.ar.core.PointCloud;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.FloatBuffer;
import java.nio.IntBuffer;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;

/**
 * Persistent, smoothed map of ARCore feature points for the camera preview (GL thread only).
 *
 * ARCore's PointCloud holds only the few points tracked in the latest update (~10 Hz, often fewer than 10 on plain
 * walls) and their positions are re-estimated every update. Drawing it directly made the dots vanish, flicker and
 * float. Here every point is kept by its ARCore id:
 *   - shown once it has been seen MIN_OBS times with confidence >= MIN_CONF, at its running-mean position;
 *   - kept on screen after ARCore stops reporting it (until the map is full, then the oldest are dropped);
 *   - reset (hidden again) if a new estimate jumps more than JUMP_M from its mean.
 */
public class FeatureMap {
  private static final int MIN_OBS = 3;
  private static final float MIN_CONF = 0.3f;
  private static final float JUMP_M = 0.15f;
  private static final int MAX_POINTS = 20000;
  private static final int MEAN_WINDOW = 20;

  private static class P {
    float x, y, z;
    int obs;
    long lastSeen;
  }

  private final HashMap<Integer, P> pts = new HashMap<>();
  private FloatBuffer buf = null;
  private int shown = 0;
  private boolean dirty = false;

  public void clear() {
    pts.clear();
    shown = 0;
    dirty = true;
  }

  /** Feed a new ARCore point cloud (call only when its timestamp changed). */
  public void update(PointCloud pc) {
    FloatBuffer p = pc.getPoints();
    IntBuffer ids = pc.getIds();
    long ts = pc.getTimestamp();
    int n = Math.min(p.limit() / 4, ids.limit());
    for (int j = 0; j < n; j++) {
      float x = p.get(4 * j), y = p.get(4 * j + 1), z = p.get(4 * j + 2), c = p.get(4 * j + 3);
      if (!(c >= MIN_CONF) || Float.isNaN(x) || Float.isNaN(y) || Float.isNaN(z)) continue;
      int id = ids.get(j);
      P q = pts.get(id);
      if (q == null) {
        q = new P();
        q.x = x; q.y = y; q.z = z; q.obs = 1;
        pts.put(id, q);
      } else {
        float dx = x - q.x, dy = y - q.y, dz = z - q.z;
        if (dx * dx + dy * dy + dz * dz > JUMP_M * JUMP_M) {
          q.x = x; q.y = y; q.z = z; q.obs = 1;          // estimate jumped: start over, hidden until it settles
        } else {
          q.obs++;
          float w = 1f / Math.min(q.obs, MEAN_WINDOW);
          q.x += dx * w; q.y += dy * w; q.z += dz * w;
        }
      }
      q.lastSeen = ts;
    }
    if (pts.size() > MAX_POINTS) evictOldest(pts.size() - MAX_POINTS);
    dirty = true;
  }

  private void evictOldest(int count) {
    // rare (only when the map is full): drop the points not seen for the longest time
    long[] seen = new long[pts.size()];
    int i = 0;
    for (P q : pts.values()) seen[i++] = q.lastSeen;
    java.util.Arrays.sort(seen);
    long cut = seen[Math.min(count, seen.length - 1)];
    Iterator<Map.Entry<Integer, P>> it = pts.entrySet().iterator();
    while (it.hasNext()) {
      if (it.next().getValue().lastSeen < cut) it.remove();
    }
  }

  /** Vertex data (x, y, z, 1) of the settled points, or null when unchanged since the last call. */
  public FloatBuffer takeIfChanged() {
    if (!dirty) return null;
    dirty = false;
    int cap = pts.size() * 4;
    if (buf == null || buf.capacity() < cap) {
      buf = ByteBuffer.allocateDirect(Math.max(cap, 1024) * 4).order(ByteOrder.nativeOrder()).asFloatBuffer();
    }
    buf.clear();
    shown = 0;
    for (P q : pts.values()) {
      if (q.obs < MIN_OBS) continue;
      buf.put(q.x).put(q.y).put(q.z).put(1f);
      shown++;
    }
    buf.flip();
    return buf;
  }

  public int shownCount() {
    return shown;
  }
}
