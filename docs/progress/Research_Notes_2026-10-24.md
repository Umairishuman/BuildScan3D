# Research notes — faster training, cleaner walls/corners, featureless tracking (2026-10-24)

Goal (user, 2026-10-23): cut processing time, get cleaner 3DGS — especially far walls and corners, which are
not flat when viewed off the camera path — a better web viewer, and solutions for featureless tracking and
corner detection in plain (drywall) rooms. Figures below are the papers' own; not independently verified.

**Outcome (morning of 2026-10-24, details in Problems_and_Solutions 4.15):** DashGaussian + the SfM-anchored
priors at 15k iterations train in **30 min instead of 64 min** with equal or better off-path quality (SSIM
0.8281 vs 0.8241, cleanest on the hardest off-path frame). Stronger priors over-smooth; the mono-depth dense
init alone (12 s) is not yet a replacement for COLMAP PatchMatch. The web viewer now streams a 12.5 MB `.spz`.

## 1. Faster 3DGS training

| Method | Idea | Reported | Fit for us |
|---|---|---|---|
| [DashGaussian](https://openaccess.thecvf.com/content/CVPR2025/papers/Chen_DashGaussian_Optimizing_3D_Gaussian_Splatting_in_200_Seconds_CVPR_2025_paper.pdf) (CVPR 2025, [code](https://github.com/YouyuChen0207/DashGaussian)) | Schedule only: train at low resolution first, raising it along a frequency-energy curve; grow the Gaussian count with a momentum budget tied to resolution | ~46% faster across backbones, same quality; Taming-3DGS + Dash ≈ 200 s on a consumer GPU | **Implemented tonight** (resolution part) in `geo_splatfacto.py --dash_res_steps`: no CUDA changes needed |
| [FastGS](https://arxiv.org/html/2511.04283v3) (CVPR 2026) | Multi-view-consistency densification / pruning | ~100 s/scene (1.93 min vs DashGaussian 6.35 min on Mip-NeRF 360), slightly lower PSNR | Needs its own CUDA rasterizer; our gsplat is a prebuilt binary, so later / cloud |
| Taming-3DGS | Budget-controlled densification | 5.4 min on Mip-NeRF 360 (FastGS table) | Budget idea portable (cap + score-based densify) |
| Speedy-Splat | Hessian-based pruning | ~13 min, lower quality | Low priority |

Our measured bottleneck after ARCore-guided matching (SfM ≈ 5 min) is training: ~60 min for the v6 recipe on
the RTX 3070 (R0 = 64 min). DashGaussian targets exactly this.

## 2. Flat walls and sharp corners in plain indoor rooms

- **Why it fails:** plain walls give the photometric loss nothing to lock onto, so Gaussians spread in depth.
  The model looks right from the training views but is fuzzy or bent off-path. This is the user's "far walls
  and corners not flat" problem.
- [PGSR](https://arxiv.org/html/2406.06521v2) (in `docs/Research Papers`): flat Gaussians + single-view
  depth/normal consistency + multi-view homography consistency. No learned priors. A 2026 study
  ([Textureless-Splatter](https://www.tandfonline.com/doi/full/10.1080/20964471.2026.2634534)) reports it
  **loses its advantage in low-texture regions**.
- [DN-Splatter](https://openaccess.thecvf.com/content/WACV2025/papers/Turkulainen_DN-Splatter_Depth_and_Normal_Priors_for_Gaussian_Splatting_and_Meshing_WACV_2025_paper.pdf)
  (WACV 2025): depth + normal priors, designed for textureless indoor scenes (white walls); edge-aware.
- [PlanarGS](https://arxiv.org/abs/2510.23930) (NeurIPS 2025, [code](https://github.com/SJTU-ViSYS-team/PlanarGS)):
  vision-language plane segmentation (language-prompted planar priors) verified across views, plus depth/normal
  priors from a multi-view foundation model; co-planarity + flattening losses. Reports up to 37–43% better
  accuracy, Chamfer < 5 cm on MuSHRoom / Replica.
- Textureless-Splatter: monocular depth **supervised by SfM points** for textureless scenes.

**Implemented tonight** (`src/arcore3dgs/mono_prior.py` + `geo_splatfacto.py`): Metric3D depth per frame,
aligned to that frame's metric SfM points by robust least squares (raw Metric3D median error 19.5% → aligned
**2.7%** on newRoom). Normals come from the aligned depth. Two losses are added to splatfacto: relative depth,
and an edge-aware depth-normal consistency (PGSR single-view form, weighted by (1−|∇I|)²) so real corners stay
sharp. **Next:** planar-region masks (PlanarGS-style) and a flattening term on wall/floor regions only.

## 3. Featureless tracking (plain walls)

- Point features vanish on plain walls; **line features + the Manhattan assumption** are the standard fix in VIO:
  - [PL-VIO / structural lines](https://arxiv.org/html/2105.04064): Manhattan-aligned structural lines cut drift;
    PL-VINS without global Manhattan constraints still drifts in orientation;
  - [MLINE-VINS](https://arxiv.org/pdf/2503.01571) (2025): Manhattan + line tracking in the back end;
  - [vanishing points in VIO](https://www.researchgate.net/publication/378573895_Visual-Inertial_Odometry_of_Structured_and_Unstructured_Lines_Based_on_Vanishing_Points_in_Indoor_Environments).
- We cannot change ARCore's tracker, but the same ideas apply in our **offline** pipeline:
  - [LIMAP](https://github.com/cvg/limap) ([paper](https://arxiv.org/abs/2303.17504)): line mapping + point-line
    SfM / BA, COLMAP-compatible, with [DeepLSD](https://arxiv.org/pdf/2212.07766) lines. Adding lines to SfM
    helps exactly in textureless areas;
  - **COLMAP 4.2 already ships learned ALIKED features + LightGlue matching** (official ONNX models). These
    are more robust than SIFT on blur and low texture. Planned test: register rate, reprojection error and SfM
    time vs SIFT on newRoom.
- Live side (app): keep an edge or corner in view (it makes ARCore track better too), the feature-starvation
  warning, and IMU bridging (our fallback, `fallback.py`).

## 4. Corner / room-layout detection

- Single-image layout networks (RoomNet, LayoutNet, [ST-RoomNet](https://openaccess.thecvf.com/content/CVPR2023W/VOCVALC/papers/Ibrahem_ST-RoomNet_Learning_Room_Layout_Estimation_From_Single_Image_Through_Unsupervised_CVPRW_2023_paper.pdf),
  [uLayout](https://openaccess.thecvf.com/content/WACV2025/papers/Lee_uLayout_Unified_Room_Layout_Estimation_for_Perspective_and_Panoramic_Images_WACV_2025_paper.pdf), WACV 2025)
  mostly rely on vanishing points, which are weak in textureless rooms ([review](https://www.researchgate.net/publication/342596994_Review_on_Room_Layout_Estimation_from_a_Single_Image)).
- Posed-video methods are closer to us: [DeepPerimeter](https://arxiv.org/pdf/1904.11595) estimates the room
  perimeter from a posed monocular sequence (depth → wall planes → perimeter).
  [Flat2Layout](https://arxiv.org/pdf/1905.12571) handles non-box rooms.
- Our desktop route already works this way (`structure.py`: gravity-aware wall planes from the metric model →
  corners as plane intersections; 6.65–6.68 × 4.45–4.48 m on newRoom). It gets cleaner as walls get flatter
  (section 2) and can use the Metric3D normals for wall / floor / ceiling labelling (semantic step).

## 5. Web viewer

The old viser viewer rendered every frame on the server and streamed JPEGs, hence the lag. SuperSplat (PlayCanvas)
renders in the browser. **Implemented tonight:** [Spark](https://sparkjs.dev) (World Labs, Three.js, MIT) in
`prototype/web-ui` (`SplatCanvas.tsx`): real splats render in the BuildScan viewer, with fly controls and
click-to-measure on the splat surface. Next: compressed `.spz` / `.sog` delivery (~10× smaller than PLY).
