"""Extract the IMU (gyroscope + accelerometer) that ARCore's Recording API stores inside dataset.mp4.

The MP4 has protobuf 'mett' data tracks. Each sample message holds:
  field 2 = sensor type (1 = accelerometer, 3 = gyroscope in this recording), fields 3/4/5 = x/y/z
  (float32; m/s^2 or rad/s, Android sensor axes), field 6 = timestamp (ns, same clock as ARCore frames).
No IMU logging in the app is needed: every ARCore recording already contains it.

  extract_imu(dataset_dir) -> {"gyro": (t_ns[N], xyz[N,3]), "accel": (t_ns[M], xyz[M,3])}
Results are cached as <dataset>/imu.npz.
"""
import os, struct, subprocess, json
import numpy as np


def _varint(b, i):
    r = s = 0
    while True:
        c = b[i]; i += 1
        r |= (c & 0x7F) << s
        if c < 0x80:
            return r, i
        s += 7


def _walk(b, out, depth=0):
    """Recursively find sample messages (type varint + 3 floats + timestamp) in a protobuf blob."""
    i, n = 0, len(b)
    fields = {}
    subs = []
    try:
        while i < n:
            key, i = _varint(b, i)
            fn, wt = key >> 3, key & 7
            if wt == 0:
                v, i = _varint(b, i); fields.setdefault(fn, v)
            elif wt == 5:
                fields.setdefault(fn, struct.unpack_from("<f", b, i)[0]); i += 4
            elif wt == 1:
                i += 8
            elif wt == 2:
                ln, i = _varint(b, i)
                if depth < 6:
                    subs.append(b[i:i + ln])
                i += ln
            else:
                return False
    except (IndexError, struct.error):
        return False
    if all(k in fields for k in (2, 3, 4, 5, 6)) and isinstance(fields[3], float):
        out.append((fields[2], fields[6], fields[3], fields[4], fields[5]))
    for sb in subs:
        _walk(sb, out, depth + 1)
    return True


def extract_imu(dataset_dir, force=False):
    cache = os.path.join(dataset_dir, "imu.npz")
    if os.path.exists(cache) and not force:
        z = np.load(cache)
        return {"gyro": (z["gt"], z["g"]), "accel": (z["at"], z["a"])}
    mp4 = os.path.join(dataset_dir, "dataset.mp4")
    info = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries",
                                               "stream=index,codec_type,codec_tag_string", "-of", "json", mp4]))
    samples = []
    for st in info["streams"]:
        if st.get("codec_type") != "data":
            continue
        raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", mp4, "-map", f"0:{st['index']}",
                                       "-c", "copy", "-f", "data", "-"])
        _walk(raw, samples)
    S = np.array(samples, dtype=np.float64)
    if len(S) == 0:
        raise RuntimeError("no IMU samples found in dataset.mp4")
    types, counts = np.unique(S[:, 0].astype(int), return_counts=True)
    # identify sensors by magnitude: accelerometer ~ 9.81 m/s^2, gyroscope ~ 0 rad/s
    acc_t = gyr_t = None
    for t_ in types:
        mag = np.median(np.linalg.norm(S[S[:, 0] == t_, 2:5], axis=1))
        if 8.0 < mag < 11.5 and acc_t is None:
            acc_t = t_
        elif mag < 3.0 and gyr_t is None:
            gyr_t = t_
    out = {}
    for name, t_ in (("gyro", gyr_t), ("accel", acc_t)):
        sel = S[S[:, 0] == t_]
        sel = sel[np.argsort(sel[:, 1], kind="stable")]
        _, u = np.unique(sel[:, 1], return_index=True)
        out[name] = (sel[u, 1].astype(np.int64), sel[u, 2:5])
    np.savez(cache, gt=out["gyro"][0], g=out["gyro"][1], at=out["accel"][0], a=out["accel"][1])
    return out


if __name__ == "__main__":
    import sys
    d = extract_imu(sys.argv[1], force=True)
    for k, (t, x) in d.items():
        dur = (t[-1] - t[0]) / 1e9
        print(f"{k}: {len(t)} samples over {dur:.1f} s ({len(t) / dur:.0f} Hz), median |v| {np.median(np.linalg.norm(x, axis=1)):.3f}")
