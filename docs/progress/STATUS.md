# BuildScan3D: Current Status

Last updated: 2026-11-06. Branch `feature/semantics-mesh`.

One page on where the project stands. History and reasoning are in
[Problems_and_Solutions.md](Problems_and_Solutions.md) (§4.15–4.18 for v8–v10); the full task list is in
[TODO.md](TODO.md); the web viewer has its own [STATUS.md](../../prototype/web-ui/STATUS.md).

## Best model

`saved_models/2026-10-27_v9_semantic_pgsr/newRoomAttemptSadness/` (see its `README.txt`).

| Item | Value |
|---|---|
| Capture | newRoomAttemptSadness, realme RMX5111, ARCore app, slow walk |
| Model | 605,481 Gaussians, metric, +Y up; `splat.ply` 150 MB, `splat.spz` 11.6 MB |
| Recipe | v9 pipeline + PGSR-lite, trained on all 1165 frames, 15k steps, 46 min |
| Labels | `semantic_v10/` (newest), `semantic/` (v9) |
| Mesh, layout | `mesh/` (TSDF, shell denoised, `.glb` for the web), `layout/` |
| Web demo | `prototype/web-ui/public/scans/newroom/`, page `/viewer/newroom-scan` |

`saved_models/2026-10-26_v9_e2e/` is the same recipe with 79 frames held out, used for the numbers below.
`saved_models/2026-10-24_v8_geofast15` has a training bug (priors on the wrong images); don't use it.

## Results

| Goal | Result | Verdict |
|---|---|---|
| Image quality (79 held-out frames) | PSNR 25.16, SSIM 0.825, sharpness 0.80 (PGSR-lite: 0.88) | Best so far; the hardest off-path view is complete for the first time |
| Processing time | 96 min end to end on the RTX 3070 (SfM 22, priors 8, init 20, training 43) | Was ~4 h (v6); goal < 15 min not reached |
| Metric scale | Room length 6.60 m (tape 6.70 m), −1.5% | Open: the Sim3-to-ARCore scale varies between SfM runs |
| Flat walls | Off-path flatness 0.77 cm; mesh walls 0.03–0.78 cm after shell denoising | Good; wall 3 and the ceiling stay rough (ceiling seen only at grazing angles) |
| Room measurements | 4 walls with gross / opening / net areas, floor 28.8 m², ceiling 2.73 m | Works on one room |
| Fixtures (v10) | 15/15 detections correct, 15/17 visible fixtures found | Tuned and scored on the same room: not a general accuracy figure |

v10 still misses the socket under the ironing table and one round light (taken by the "clock" decoy). The three new
v10 detections (`door_1`, `door_6`, `tube_light_1`) still need the user's confirmation.

## How to run

Setup: three Python environments, see the README "Quick Start Guide" and `requirements*.txt`.
From the repo root, `S` = `dataset/<capture>/work_v9_sfm`, `M` = `$S/gs_v9`:

```powershell
# 1. Capture -> metric 3DGS (96 min). System Python; nerfstudio steps switch to nerfstudio-env themselves.
python src/arcore3dgs/run_v8.py --dataset dataset/<capture> --tag v9 --sfm_args "--retrieval 20" --init fmvs --planar 0.2 --blur 0.0222
#    The best model adds --pgsr: rerun the train stage with geo_splatfacto.py --pgsr (same arguments run_v8.py prints).

# 2. Room layout (walls, corners, dimensions)
nerfstudio-env\Scripts\python.exe src/arcore3dgs/layout.py --ply $M/splat.ply --work $S --out $M/layout

# 3. Semantics: 2D proposals (38 min), 3D labels, CLIP check of switches / sockets, then 3D labels again
semantic-env\Scripts\python.exe -W ignore src/arcore3dgs/semantic2d.py --work $S --every 2 --box_thr 0.28 --tiles 640 --out semantic2d_v10
nerfstudio-env\Scripts\python.exe -W ignore src/arcore3dgs/semantic3d.py --ply $M/splat.ply --work $S --layout $M/layout/layout.json --out $M/semantic_v10 --sem2d semantic2d_v10
semantic-env\Scripts\python.exe src/arcore3dgs/verify_fixtures.py --work $S --sem2d semantic2d_v10 --semantic $M/semantic_v10
nerfstudio-env\Scripts\python.exe -W ignore src/arcore3dgs/semantic3d.py --ply $M/splat.ply --work $S --layout $M/layout/layout.json --out $M/semantic_v10 --sem2d semantic2d_v10 --verdicts $M/semantic_v10/verdicts.json

# 4. Mesh (PGSR models: --depth unbiased), labelled mesh, web bundle
nerfstudio-env\Scripts\python.exe src/arcore3dgs/mesh.py --ply $M/splat.ply --work $S --out $M/mesh --depth unbiased
nerfstudio-env\Scripts\python.exe src/arcore3dgs/mesh_labels.py --mesh $M/mesh/mesh.ply --ply $M/splat.ply --semantic $M/semantic_v10 --layout $M/layout/layout.json --clean 0.01 --glb 400000
nerfstudio-env\Scripts\python.exe src/arcore3dgs/export_web.py --ply $M/splat.ply --semantic $M/semantic_v10 --glb $M/mesh/mesh_web.glb --out prototype/web-ui/public/scans/<name>
```

Check each script's docstring for its full options. Don't run other GPU jobs while training with `--blur` (OOM on 8 GB).

The phone-upload server (`server/`, [PROCESSING_GUIDE.md](../PROCESSING_GUIDE.md)) still runs the older, simpler
splatfacto pipeline, not the one above.

## Known limits

- **One room.** Every result above is on newRoomAttemptSadness; the semantics rules were tuned on it.
- **Speed.** 96 min plus ~40 min for semantics; the v10 tile pass made the 2D stage 5× slower.
- **Metric scale** is 1.5–2% off and not stable between SfM runs.
- **Semantics margins are thin:** false sockets scored 0.45–0.47 in the CLIP check against a 0.5 threshold.
- **Open doorways without a door leaf** are found only when their frame strips merge; plain wall gaps aren't used yet.
- **Ceiling** is the weakest surface (seen at grazing angles from chest height).
- PGSR is single-view only ("lite"); the multi-view terms that remove faint wall stripes aren't implemented.

## Next steps

1. **Second room** (roomAttemptSadness2): full pipeline + semantics (~2 h GPU), then a room check by the user. The real test of v10.
2. **Metric scale:** a more robust Sim3 to ARCore (several segments, `anchors.csv` corrections), checked against tape measurements.
3. **Speed:** the SfM (22 min) and dense init (20 min) are the biggest remaining stages after training.
