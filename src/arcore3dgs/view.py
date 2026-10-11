"""Minimal browser viewer for an exported splat.ply (INRIA format), rendered with gsplat.

  python view.py --ply <work>/gs/splat.ply   ->  open http://localhost:7010
Also shows the metric scale: click two points in the scene to measure the distance (metres).
"""
import time, argparse
import numpy as np, torch, torch.nn.functional as F, viser
from plyfile import PlyData
from scipy.spatial.transform import Rotation as R
from gsplat import rasterization

ap = argparse.ArgumentParser()
ap.add_argument("--ply", required=True)
ap.add_argument("--port", type=int, default=7010)
ap.add_argument("--max_res", type=int, default=1024)
# The phone frames cover ~63x38 deg; a wider viewer FOV shows directions/distances never filmed, where 3DGS smears.
ap.add_argument("--fov", type=float, default=45.0, help="vertical field of view (deg)")
ap.add_argument("--near", type=float, default=0.15, help="skip splats closer than this (m): avoids walking through floaters")
ap.add_argument("--debug", action="store_true")
ap.add_argument("--min_opacity", type=float, default=0.02)
ap.add_argument("--fps", type=float, default=60, help="max frames/s sent while moving (half resolution); lower it if the browser lags")
ap.add_argument("--stress", type=float, default=0, help="test: orbit camera for N seconds, log timings")
args = ap.parse_args()

dev = torch.device("cuda")
v = PlyData.read(args.ply)["vertex"]
names = v.data.dtype.names
col = lambda n: torch.tensor(np.asarray(v[n]), dtype=torch.float32, device=dev)
means = torch.stack([col("x"), col("y"), col("z")], 1)
sh0 = torch.stack([col(f"f_dc_{i}") for i in range(3)], 1)[:, None]
n_rest = len([n for n in names if n.startswith("f_rest_")])
shN = torch.stack([col(f"f_rest_{i}") for i in range(n_rest)], 1).reshape(len(means), 3, -1).transpose(1, 2)
colors = torch.cat([sh0, shN], 1)
sh_deg = int(round(np.sqrt(colors.shape[1]))) - 1
opac = torch.sigmoid(col("opacity"))
scales = torch.exp(torch.stack([col(f"scale_{i}") for i in range(3)], 1))
quats = F.normalize(torch.stack([col(f"rot_{i}") for i in range(4)], 1), dim=-1)
keep = opac > args.min_opacity                     # near-invisible splats cost GPU time for no visual gain
n_all = len(means)
means, colors, opac, scales, quats = means[keep], colors[keep], opac[keep], scales[keep], quats[keep]
import json as _json, os as _os
_mj = _os.path.join(_os.path.dirname(_os.path.abspath(args.ply)), "metrics.json")
AA = "antialiased" if _os.path.exists(_mj) and _json.load(open(_mj)).get("antialiased") else "classic"
print(f"Loaded {n_all} gaussians, rendering {len(means)} (dropped opacity < {args.min_opacity}), SH degree {sh_deg}")

# warm-up on the main thread: loads the gsplat CUDA extension + context here; doing it first inside a
# worker thread stalls on Windows
with torch.no_grad():
    _K = torch.tensor([[[500.0, 0, 320], [0, 500, 240], [0, 0, 1]]], device=dev)
    rasterization(means[:1000], quats[:1000], scales[:1000], opac[:1000], colors[:1000],
                  torch.eye(4, device=dev)[None], _K, 640, 480, sh_degree=sh_deg)
    torch.cuda.synchronize()
print("Renderer ready")

server = viser.ViserServer(port=args.port)
server.scene.set_up_direction("+y")          # ARCore world is +Y up
info = server.gui.add_markdown("Drag to orbit, right-drag to pan, scroll / WASD to move. Press *Measure distance* to measure.")
fov_slider = server.gui.add_slider("Field of view (deg)", min=25, max=90, step=1, initial_value=args.fov)
near_slider = server.gui.add_slider("Near clip (m)", min=0.02, max=0.6, step=0.01, initial_value=args.near)
picked = []


# start at a real capture camera if the pipeline's frames.json is next to the splat
import os, json, threading
start_pos, start_look = means.mean(0).cpu().numpy(), None
fj = os.path.join(os.path.dirname(os.path.abspath(args.ply)), "..", "frames.json")
if os.path.exists(fj):
    fr = json.load(open(fj))["frames"]
    c2w0 = np.array(fr[len(fr) // 2]["c2w"])            # OpenGL camera: looks along -Z
    start_pos, start_look = c2w0[:3, 3], c2w0[:3, 3] - c2w0[:3, 2]

dirty = {}          # client_id -> camera changed since last render
stats = {"n": 0, "ms": 0.0}


@torch.no_grad()
def render(client, res):
    cam = client.camera
    if args.debug: print('  r: got camera', flush=True)
    aspect = cam.aspect if cam.aspect and cam.aspect > 0 else 16 / 9
    W = res
    H = int(W / aspect)
    if H > res:
        H = res; W = int(H * aspect)
    fy = 0.5 * H / np.tan(cam.fov / 2)                  # viser fov is vertical, radians
    K = torch.tensor([[fy, 0, W / 2], [0, fy, H / 2], [0, 0, 1]], dtype=torch.float32, device=dev)
    c2w = np.eye(4)
    c2w[:3, :3] = R.from_quat(np.roll(cam.wxyz, -1)).as_matrix()   # viser camera: OpenCV axes
    c2w[:3, 3] = cam.position
    w2c = torch.tensor(np.linalg.inv(c2w), dtype=torch.float32, device=dev)[None]
    t_r = time.time()
    if args.debug: print(f'  r: params W={W} H={H} fov={cam.fov} aspect={cam.aspect} pos={cam.position} wxyz={cam.wxyz}', flush=True)
    out, _, _ = rasterization(means, quats, scales, opac, colors, w2c, K[None], W, H, sh_degree=sh_deg,
                              near_plane=float(near_slider.value), rasterize_mode=AA)
    img = (out[0].clamp(0, 1).cpu().numpy() * 255).astype(np.uint8)
    if args.debug: print('  r: rasterized', flush=True)
    client.scene.set_background_image(img, format="jpeg", jpeg_quality=80)
    stats["n"] += 1; stats["ms"] = (time.time() - t_r) * 1000
    if args.debug:
        print(f"render {W}x{H} mean={img.mean():.1f} pos={np.round(cam.position, 2)} fov={cam.fov:.2f} aspect={cam.aspect}")


def render_loop():
    # Flow control: the browser receives frames in a web worker, so it never pushes back on the server;
    # sending more than it can decode makes latency grow without bound. So: while the camera moves, send
    # at most --fps half-resolution frames; once it has been still for 0.25 s, send one full-res frame.
    last_move, sharp_done, last_sent = {}, {}, 0.0
    while True:
        now = time.time()
        for cid, client in list(server.get_clients().items()):
            if dirty.pop(cid, False):
                last_move[cid] = now
                sharp_done[cid] = False
            moving = now - last_move.get(cid, 0) < 0.25
            try:
                if moving and now - last_sent >= 1.0 / args.fps:
                    render(client, args.max_res // 2)
                    last_sent = time.time()
                elif not moving and not sharp_done.get(cid, True):
                    render(client, args.max_res)
                    sharp_done[cid] = True
                    last_sent = time.time()
            except Exception as e:
                print("render error:", e)
        time.sleep(0.01)


@server.on_client_connect
def _(client):
    if args.debug: print('connect handler start', flush=True)
    client.camera.position = start_pos
    client.camera.fov = np.radians(fov_slider.value)
    if args.debug: print('set position ok', flush=True)
    if start_look is not None:
        client.camera.look_at = start_look

    @client.camera.on_update
    def _(_):
        dirty[client.client_id] = True

    # Measuring: viser disables mouse orbit while a click listener exists, so the listener is only
    # registered after pressing the button and removed again once two points are picked.
    measure_btn = client.gui.add_button("Measure distance (click 2 points)")
    clear_btn = client.gui.add_button("Clear markers")
    pts, handles = [], []

    def on_click(ev):
        # ray-pick: nearest opaque gaussian centre along the click ray
        o = torch.tensor(ev.ray_origin, dtype=torch.float32, device=dev)
        d = F.normalize(torch.tensor(ev.ray_direction, dtype=torch.float32, device=dev), dim=0)
        rel = means - o
        t = rel @ d
        dist = (rel - t[:, None] * d).norm(dim=1)
        dist[(t < 0) | (opac < 0.5)] = 1e9
        p = means[dist.argmin()].cpu().numpy()
        pts.append(p)
        handles.append(client.scene.add_icosphere(f"/measure/p{len(picked)}_{len(pts)}", radius=0.01, color=(255, 0, 0), position=p))
        if len(pts) == 1:
            info.content = "Now click the **second** point."
        else:
            picked.append(pts[:])
            info.content = f"Distance: **{np.linalg.norm(pts[0] - pts[1]):.3f} m**  (drag to orbit again)"
            handles.append(client.scene.add_spline_catmull_rom(f"/measure/l{len(picked)}", np.stack(pts), color=(255, 0, 0), line_width=3))
            pts.clear()
            client.scene.remove_pointer_callback()
            measure_btn.disabled = False

    @measure_btn.on_click
    def _(_):
        pts.clear()
        measure_btn.disabled = True
        info.content = "Click the **first** point (mouse orbit paused until 2 points are picked)."
        client.scene.on_pointer_event(event_type="click")(on_click)

    @clear_btn.on_click
    def _(_):
        for h in handles:
            h.remove()
        handles.clear()
        info.content = "Press *Measure distance* and click two surface points."

    dirty[client.client_id] = True
    if args.debug: print('connect handler done', client.client_id, flush=True)


@fov_slider.on_update
def _(_):
    for cid, c in list(server.get_clients().items()):
        c.camera.fov = np.radians(fov_slider.value)
        dirty[cid] = True


@near_slider.on_update
def _(_):
    for cid in list(server.get_clients()):
        dirty[cid] = True


threading.Thread(target=render_loop, daemon=True).start()

if args.stress:
    import psutil
    def stress():
        while not server.get_clients():
            time.sleep(0.5)
        t0 = time.time(); n0 = stats["n"]
        while time.time() - t0 < args.stress:
            a = (time.time() - t0) * 0.5
            for c in list(server.get_clients().values()):
                c.camera.position = start_pos + 0.5 * np.array([np.cos(a), 0, np.sin(a)])
                c.camera.look_at = start_look
            time.sleep(1 / 60)
            if int((time.time() - t0) * 2) % 10 == 0 and time.time() - stats.get("last", 0) > 4:
                stats["last"] = time.time()
                print(f"t={time.time()-t0:5.1f}s renders={stats['n']-n0} last_ms={stats['ms']:.1f} "
                      f"rss={psutil.Process().memory_info().rss/1e9:.2f}GB gpu={torch.cuda.memory_allocated()/1e9:.2f}GB", flush=True)
        os._exit(0)
    threading.Thread(target=stress, daemon=True).start()
print(f"Viewer on http://localhost:{server.get_port()}", flush=True)
while True:
    time.sleep(1.0)
