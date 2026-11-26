export interface Project {
  id: string;
  name: string;
  floor: string;
  block: string;
  area: string;
  location: string;
  dateCaptured: string;
  status: "ready" | "processing" | "complete" | "draft" | "archived";
  statusLabel: string;
  thumbnail: string;
  scansCount: number;
  gaussianCount?: string;
  accuracy?: string;
  captureDevice?: string;
  description: string;
  /** Real captured scan: a 3DGS .ply served from /public. When set, the viewer renders it with Spark. */
  splatUrl?: string;
  /** Camera start pose for the splat viewer, in the scan's metric coordinates (+Y up). */
  splatStart?: { position: [number, number, number]; target: [number, number, number] };
  /**
   * Labelled real scan: folder under /public with scan.json, one .spz per semantic group and mesh.glb
   * (written by src/arcore3dgs/export_web.py). Takes precedence over splatUrl.
   */
  scanUrl?: string;
}

export const MOCK_PROJECTS: Project[] = [
  {
    id: "newroom-scan",
    name: "Living Room Scan (Real Capture)",
    floor: "Ground Floor",
    block: "Residence",
    area: "≈ 29 m²",
    location: "Ground Floor • Residence • ≈ 29 m²",
    dateCaptured: "Oct 10, 2026",
    status: "ready",
    statusLabel: "3DGS Ready · 605K splats · labelled",
    thumbnail: "/thumbnails/newroom_v6.jpg",
    scansCount: 1,
    gaussianCount: "605,481",
    accuracy: "Room 6.60 × 4.36 m auto-measured (tape 6.70 m)",
    captureDevice: "realme RMX5111 (ARCore)",
    description:
      "Real 4-minute phone video reconstructed with the BuildScan pipeline (v9: retrieval SfM scaled by ARCore, fast dense init, geometry priors, motion-blur model, PGSR-lite) and labelled automatically: walls, floor, ceiling, doors, switches, sockets and lights, plus a surface mesh. Floor 28.8 m², ceiling 2.72 m.",
    scanUrl: "/scans/newroom/",
    splatStart: { position: [-0.98, -0.06, -0.2], target: [-1.98, -0.36, -0.2] },
  },
  {
    // Scan #8 (scan_008_7b486c855ed6), run R-039 (tag r1116w9, --window 9, D-073). Numbers from the bundle's
    // scan.json and layout.json. The bundle is gitignored (D-061): it exists only on the Ubuntu PC that ran it.
    id: "scan-008",
    name: "Scan #8 (Real Capture)",
    floor: "Room not named yet",
    block: "Residence",
    area: "≈ 21 m²",
    location: "Scan #8 • R-039 • ≈ 21 m²",
    dateCaptured: "Nov 16, 2026",
    status: "ready",
    statusLabel: "3DGS Ready · 2.51M splats · labelled",
    thumbnail: "/thumbnails/scan_008_plan.png",
    scansCount: 1,
    gaussianCount: "2,506,236",
    accuracy: "Room 6.03 × 4.40 m auto-measured (no tape check yet)",
    captureDevice: "Infinix X6833B (ARCore)",
    description:
      "Real 6-minute phone video reconstructed with the BuildScan pipeline (R-023 recipe, every 9th frame) and labelled automatically: walls, floor, ceiling, a door, two windows, four switches, three sockets and a ceiling light, plus a surface mesh. Floor 21.3 m², ceiling 3.19 m (not checked against a tape).",
    scanUrl: "/scans/scan_008_7b486c855ed6_r1116w9/",
    // Middle of the detected fixtures, 1.5 m above the floor (floor y = -3.12), looking at door_1.
    splatStart: { position: [7.7, -1.6, 4.0], target: [9.85, -1.9, 2.32] },
  },
  {
    // R-069 (2026-11-14). Bundle is local only (git-ignored, other.spz > CI's 10 MB limit): rebuild with run_full.sh.
    id: "bedroom-scan",
    name: "Bedroom Scan (Real Capture)",
    floor: "Ground Floor",
    block: "Residence",
    area: "≈ 12 m²",
    location: "Ground Floor • Residence • ≈ 12 m²",
    dateCaptured: "Oct 9, 2026",
    status: "ready",
    statusLabel: "3DGS Ready · 1.45M splats · labelled",
    thumbnail: "/thumbnails/room2_v9.jpg",
    scansCount: 1,
    gaussianCount: "1,445,529",
    accuracy: "Not tape-checked yet",
    captureDevice: "realme RMX5111 (ARCore)",
    description:
      "Second room (roomAttemptSadness2) through the full v9 + PGSR pipeline: 1,000 of 1,042 frames registered, scaled by ARCore (median 3.3 cm). Labelled walls, floor, ceiling, openings and 22 fixtures (not yet checked by a person) plus a surface mesh. Floor 11.9 m², ceiling 2.82 m.",
    scanUrl: "/scans/roomAttemptSadness2_v9pgsr8/",
  },
  {
    // R-020 (2026-10-26), saved_models/2026-10-26_v9_e2e. File is local only (git-ignored, > 10 MB).
    id: "newroom-v9e2e",
    name: "Living Room · v9 end-to-end (unlabelled)",
    floor: "Ground Floor",
    block: "Residence",
    area: "≈ 29 m²",
    location: "Ground Floor • Residence • ≈ 29 m²",
    dateCaptured: "Oct 10, 2026",
    status: "ready",
    statusLabel: "3DGS Ready · 619K splats",
    thumbnail: "/thumbnails/newroom_v6.jpg",
    scansCount: 1,
    gaussianCount: "619,056",
    accuracy: "Off-path PSNR 25.16 dB / SSIM 0.825 (79 held-out views)",
    captureDevice: "realme RMX5111 (ARCore)",
    description:
      "The same living-room capture as the v9 recipe without PGSR or labels (R-020): retrieval SfM scaled by ARCore, fast dense init, geometry priors and the motion-blur model, 42.5 min training. Trained without the 79 held-out test views.",
    splatUrl: "/splats/newroom_v9e2e.spz",
    splatStart: { position: [-0.98, -0.06, -0.2], target: [-1.98, -0.36, -0.2] },
  },
  {
    // R-068 (2026-11-12), dataset/scan_3028a4de8fa0 gs_v10inc. File is local only (git-ignored, > 10 MB).
    id: "lecture-hall-scan",
    name: "Lecture Hall Scan (Real Capture)",
    floor: "—",
    block: "University",
    area: "Not measured",
    location: "University • lecture hall",
    dateCaptured: "Nov 12, 2026",
    status: "ready",
    statusLabel: "3DGS Ready · 637K splats",
    thumbnail: "/thumbnails/hall_v10inc.jpg",
    scansCount: 1,
    gaussianCount: "637,318",
    accuracy: "Scaled by ARCore (100 frames, median 6.6 cm); table length not re-measured",
    captureDevice: "realme RMX5111 (ARCore)",
    description:
      "Lecture hall (scan_3028a4de8fa0) with the fast recipe on the incremental-mapper SfM (R-068): 572 of 842 frames, no shrunken 'mini room'. The right-hand part of the walk did not register, so that side is built only from the opposite side. Unlabelled.",
    splatUrl: "/splats/hall_v10inc.spz",
  },
  {
    // R-045 (2026-11-15), dataset/scan_009_057ed3beb4fc gs_v9pgsr. File is local only (git-ignored).
    id: "scan-009",
    name: "Scan 009 · partial (failed capture check)",
    floor: "—",
    block: "Residence",
    area: "Not measured",
    location: "scan_009_057ed3beb4fc • partial model",
    dateCaptured: "Nov 15, 2026",
    status: "draft",
    statusLabel: "Partial · 87 of 5,629 frames · scale unreliable",
    thumbnail: "/thumbnails/scan009_v9pgsr.jpg",
    scansCount: 1,
    gaussianCount: "353,628",
    accuracy: "Scale unreliable (23 ARCore inliers; ARCore and Metric3D scales ~30% apart)",
    captureDevice: "realme RMX5111 (ARCore)",
    description:
      "v9 + PGSR on a recording that failed check_capture (tracking lost on 64% of frames, median blur 21.7 px). Only 87 frames from 115-162 s of the video registered, so this is a fragment (around a bathroom doorway). Kept to show what a bad capture produces; record again.",
    splatUrl: "/splats/scan009_v9pgsr.spz",
    splatStart: { position: [1.09, 0.79, -4.4], target: [1.38, 0.89, -3.45] },
  },
  {
    // R-046 (2026-11-15), dataset/scan_009_057ed3beb4fc gs_v9pf. File is local only (git-ignored, > 10 MB).
    id: "scan-009-posefree",
    name: "Scan 009 · pose-free selection + ALIKED SfM",
    floor: "—",
    block: "Residence",
    area: "Not measured",
    location: "scan_009_057ed3beb4fc • whole walk, rough",
    dateCaptured: "Nov 15, 2026",
    status: "draft",
    statusLabel: "Experimental · 535 of 894 keyframes · scale unreliable",
    thumbnail: "/thumbnails/scan009_v9pgsr.jpg",
    scansCount: 1,
    gaussianCount: "534,096",
    accuracy: "Scale unreliable (ARCore drifted; 26 inliers)",
    captureDevice: "realme RMX5111 (ARCore)",
    description:
      "Same recording as Scan 009, with keyframes kept even where ARCore lost tracking and ALIKED + LightGlue matching (R-046): one SfM model of 761 frames, 535 kept, covering the whole 188 s walk (R-045: 87 frames). Some cameras are still misplaced and the floor was hardly filmed, so the room is not clean and has no layout.",
    splatUrl: "/splats/scan009_v9pf.spz",
    splatStart: { position: [2.1, 0.19, 0.04], target: [2.89, 0.37, 0.63] },
  },
  {
    // R-047 (2026-11-18): R-046's model with the gyro rotation check. File is local only (git-ignored).
    id: "scan-009-gyro",
    name: "Scan 009 · gyro-checked cameras (best so far)",
    floor: "—",
    block: "Residence",
    area: "Not measured",
    location: "scan_009_057ed3beb4fc • gyro-checked, rough",
    dateCaptured: "Nov 15, 2026",
    status: "draft",
    statusLabel: "Experimental · 370 of 894 keyframes · scale unreliable",
    thumbnail: "/thumbnails/scan009_v9pgsr.jpg",
    scansCount: 1,
    gaussianCount: "562,769",
    accuracy: "Scale unreliable (ARCore barely tracked this room)",
    captureDevice: "realme RMX5111 (ARCore)",
    description:
      "Same recording as Scan 009. Cameras whose rotation disagreed with the phone's gyroscope were dropped before training (R-047): 370 keyframes instead of 535, half as many jumps in the camera path, sharper in some views (about +1 dB on shared training views). The best model of this recording so far; parts of the room are still smeared and the size is not reliable.",
    splatUrl: "/splats/scan009_v9pfg.spz",
    splatStart: { position: [0.22, -0.04, 1.82], target: [-0.33, -0.07, 0.99] },
  },
  {
    // R-071 (2026-11-19): gyro + accelerometer camera path, gyro bias fitted on far-apart image pairs (loop closed),
    // refined by bundle adjustment with sensor priors. File is local only (git-ignored).
    id: "scan-009-loop",
    name: "Scan 009 · sensor camera path, loop closed",
    floor: "—",
    block: "Residence",
    area: "Not measured",
    location: "scan_009_057ed3beb4fc • gyro + accelerometer path",
    dateCaptured: "Nov 15, 2026",
    status: "draft",
    statusLabel: "Experimental · 680 of 894 keyframes · scale ~2× too large",
    thumbnail: "/thumbnails/scan009_v9pgsr.jpg",
    scansCount: 1,
    gaussianCount: "454,442",
    accuracy: "Scale unknown (estimates say the model is about 2× too large)",
    captureDevice: "realme RMX5111 (ARCore)",
    description:
      "Same recording as Scan 009, with the camera path built from the phone's gyroscope and accelerometer and refined with the images (R-071). The start and end of the walk now line up, and 680 keyframes are used instead of 370. Quality on the training views is about the same as the gyro-checked model: cleaner on some walls and doors, smeared in others. Sizes are not reliable.",
    splatUrl: "/splats/scan009_v9pfl.spz",
    splatStart: { position: [0.09, -0.02, -0.11], target: [0.0, -0.19, 0.87] },
  },
  {
    // R-081 (2026-11-20): R-080's camera path (video point tracks steer the sensor path in the low-texture stretches,
    // bundle adjustment with adaptive priors), trained with R-071's recipe. File is local only (git-ignored).
    id: "scan-009-tracks",
    name: "Scan 009 · track-corrected camera path",
    floor: "—",
    block: "Residence",
    area: "Not measured",
    location: "scan_009_057ed3beb4fc • gyro + accelerometer + video tracks",
    dateCaptured: "Nov 15, 2026",
    status: "draft",
    statusLabel: "Experimental · 622 of 894 keyframes · scale ~2× too large",
    thumbnail: "/thumbnails/scan009_v9pgsr.jpg",
    scansCount: 1,
    gaussianCount: "542,469",
    accuracy: "Scale unknown (estimates say the model is about 2× too large)",
    captureDevice: "realme RMX5111 (ARCore)",
    description:
      "Same recording as Scan 009. The camera path from the phone's sensors is corrected with points tracked through every video frame, which fixes the stretch around 90–105 s; the stretch around 45–60 s has too little texture and still rests on the sensors (R-080, R-081). On the training views it is slightly sharper than the loop-closed model (better on 61% of frames): the start wall, the corner at 106 s and the AC and curtain at the end are cleaner; one door corner at 137 s is worse. Sizes are not reliable.",
    splatUrl: "/splats/scan009_v9pfz.spz",
    splatStart: { position: [-0.15, -0.03, -0.11], target: [-0.22, -0.21, 0.87] },
  },
  {
    // R-132 (2026-11-26): R-128 with Depth Anything 3 (DA3-BASE, Apache 2.0, D-098) depth priors instead of
    // Metric3D; frames without SfM points get a chained-scale prior. File is local only (git-ignored).
    id: "scan-009-da3",
    name: "Scan 009 · DA3 depth priors (R-132)",
    floor: "—",
    block: "Residence",
    area: "Not measured",
    location: "scan_009_057ed3beb4fc • R-128 with Depth Anything 3 (BASE) depth guidance on every frame",
    dateCaptured: "Nov 15, 2026",
    status: "draft",
    statusLabel: "Experimental · 787 training frames · scale not measured",
    thumbnail: "/thumbnails/scan009_v9pgsr.jpg",
    scansCount: 1,
    gaussianCount: "409,397",
    accuracy: "Scale not measured",
    captureDevice: "realme RMX5111 (ARCore)",
    description:
      "R-128 (same frames, cameras and settings) with depth guidance from Depth Anything 3 (BASE, Apache 2.0) instead of Metric3D, including the 338 frames that had none before. Held-out frames 23.76 dB (R-128 24.25): equal or better everywhere except 134–140 s (15.98 vs 18.30). From off-path viewpoints the walls and door look cleaner.",
    splatUrl: "/splats/scan009_v9pda.spz",
    splatStart: { position: [-0.47, 0.06, -0.41], target: [-0.51, -0.12, 0.57] },
  },
  {
    // R-128 (2026-11-25): R-120's recipe plus 266 extra video frames between keyframes in weak / featureless
    // windows (densify_frames.py), 69 frames held out. Best held-out score so far. File is local only (git-ignored).
    id: "scan-009-dense",
    name: "Scan 009 · more frames in weak stretches (R-128)",
    floor: "—",
    block: "Residence",
    area: "Not measured",
    location: "scan_009_057ed3beb4fc • loop-closed cameras + extra video frames where tracking is weak",
    dateCaptured: "Nov 15, 2026",
    status: "draft",
    statusLabel: "Experimental · 787 training frames · scale not measured",
    thumbnail: "/thumbnails/scan009_v9pgsr.jpg",
    scansCount: 1,
    gaussianCount: "415,966",
    accuracy: "Scale not measured",
    captureDevice: "realme RMX5111 (ARCore)",
    description:
      "R-120's recipe, plus extra video frames (one between each pair of keyframes) in the stretches the analyzer marks weak or featureless: fast pans, blur, little texture. Held-out frames match the photos best of all scan_009 models so far (24.25 dB after pose alignment, R-120 23.96), most in the featureless 30–60 s stretch. Processing time +3.6 min. The bathroom doorway is still not reconstructed.",
    splatUrl: "/splats/scan009_v9pld.spz",
    splatStart: { position: [-0.47, 0.06, -0.41], target: [-0.51, -0.12, 0.57] },
  },
  {
    // R-126 (2026-11-24): R-120's recipe with room-plane anchoring during training (plane_anchor.py,
    // --plane_anchor), 69 frames held out. File is local only (git-ignored).
    id: "scan-009-planes",
    name: "Scan 009 · plane anchoring in training (R-126)",
    floor: "—",
    block: "Residence",
    area: "Not measured",
    location: "scan_009_057ed3beb4fc • walls / floor / ceiling held on shared planes while training",
    dateCaptured: "Nov 15, 2026",
    status: "draft",
    statusLabel: "Experimental · 518 training keyframes · scale not measured",
    thumbnail: "/thumbnails/scan009_v9pgsr.jpg",
    scansCount: 1,
    gaussianCount: "413,544",
    accuracy: "Scale not measured",
    captureDevice: "realme RMX5111 (ARCore)",
    description:
      "Same cameras and recipe as R-120, but while training, the splats near each wall, the floor and the ceiling are moved onto one shared plane per surface every 100 steps, so copies of a wall merge. Walls are flatter (3.8 cm vs 6.1 cm) and straighter from above; held-out frames match the photos less well (−1.9 dB). Compare it with R-120.",
    splatUrl: "/splats/scan009_v9pla.spz",
    splatStart: { position: [-0.47, 0.06, -0.41], target: [-0.51, -0.12, 0.57] },
  },
  {
    // R-125 (2026-11-24): preview, no training. R-120's model (69 frames held out) with the splats near one shared
    // plane per wall / floor / ceiling snapped onto it (plane_snap.py). File is local only (git-ignored).
    id: "scan-009-planesnap",
    name: "Scan 009 · plane-snap preview (R-125)",
    floor: "—",
    block: "Residence",
    area: "Not measured",
    location: "scan_009_057ed3beb4fc • R-120 with walls / floor snapped to shared planes",
    dateCaptured: "Nov 15, 2026",
    status: "draft",
    statusLabel: "Preview · no training · scale not measured",
    thumbnail: "/thumbnails/scan009_v9pgsr.jpg",
    scansCount: 1,
    gaussianCount: "521,417",
    accuracy: "Scale not measured",
    captureDevice: "realme RMX5111 (ARCore)",
    description:
      "A preview of room-plane anchoring, made without retraining: in the camera-refined model (R-120), the splats lying along a wall, the floor or the ceiling are moved onto one shared plane per surface, so copies of the same wall merge into one thin layer. Furniture and other splats are unchanged. Compare it with 'loops closed + camera refinement (R-120)'.",
    splatUrl: "/splats/scan009_r125snap.spz",
    splatStart: { position: [-0.47, 0.06, -0.41], target: [-0.51, -0.12, 0.57] },
  },
  {
    // R-120 (2026-11-22): R-096's cameras + --pose_opt, 69 frames held out; the model R-125's preview starts from.
    // File is local only (git-ignored).
    id: "scan-009-r120",
    name: "Scan 009 · loops closed + camera refinement (R-120)",
    floor: "—",
    block: "Residence",
    area: "Not measured",
    location: "scan_009_057ed3beb4fc • loop-closed cameras, refined in training, 69 frames held out",
    dateCaptured: "Nov 15, 2026",
    status: "draft",
    statusLabel: "Experimental · 518 training keyframes · scale not measured",
    thumbnail: "/thumbnails/scan009_v9pgsr.jpg",
    scansCount: 1,
    gaussianCount: "521,417",
    accuracy: "Scale not measured",
    captureDevice: "realme RMX5111 (ARCore)",
    description:
      "The camera-refined model as trained for scoring (69 frames held out). Shown next to the plane-snap preview (R-125), which starts from exactly this model.",
    splatUrl: "/splats/scan009_v9plo.spz",
    splatStart: { position: [-0.47, 0.06, -0.41], target: [-0.51, -0.12, 0.57] },
  },
  {
    // R-122 (2026-11-23): R-096's loop-closed cameras plus camera refinement during training (--pose_opt, R-120's
    // recipe), trained on all 581 frames. File is local only (git-ignored).
    id: "scan-009-poseopt",
    name: "Scan 009 · loops closed + camera refinement",
    floor: "—",
    block: "Residence",
    area: "Not measured",
    location: "scan_009_057ed3beb4fc • loop-closed cameras, refined in training",
    dateCaptured: "Nov 15, 2026",
    status: "draft",
    statusLabel: "Experimental · 581 of 894 keyframes · scale not measured",
    thumbnail: "/thumbnails/scan009_v9pgsr.jpg",
    scansCount: 1,
    gaussianCount: "521,715",
    accuracy: "Scale not measured",
    captureDevice: "realme RMX5111 (ARCore)",
    description:
      "Same recording and cameras as 'loops closed', but each camera is also fine-tuned while the model trains. With 63 frames held out, the held-out frames match the photos a little better (+0.33 dB after pose alignment, R-120). This model uses every frame. The bathroom doorway stays smeared: the video passes it in a fast, blurred pan (125–133 s) that no method could place.",
    splatUrl: "/splats/scan009_v9plq.spz",
    splatStart: { position: [-0.47, 0.06, -0.41], target: [-0.51, -0.12, 0.57] },
  },
  {
    // R-099 (2026-11-22): R-096's recipe (camera-path loops closed with image pairs that see the same place at
    // different times, loop_path.py + prior_ba.py --pair_priors) trained on all 581 frames. File is local only
    // (git-ignored).
    id: "scan-009-loops",
    name: "Scan 009 · loops closed (featureless 11.d)",
    floor: "—",
    block: "Residence",
    area: "Not measured",
    location: "scan_009_057ed3beb4fc • sensors + loop-closing image pairs",
    dateCaptured: "Nov 15, 2026",
    status: "draft",
    statusLabel: "Experimental · 581 of 894 keyframes · scale not measured",
    thumbnail: "/thumbnails/scan009_v9pgsr.jpg",
    scansCount: 1,
    gaussianCount: "513,603",
    accuracy: "Scale not measured",
    captureDevice: "realme RMX5111 (ARCore)",
    description:
      "Same recording as Scan 009. The camera path drifted along the walk, so walls seen early and late were built in different places. Here the path is corrected with image pairs that see the same place at different times. With the same recipe and 63 frames held out, the held-out frames match the photos better (+0.96 dB after pose alignment, R-096), and views from the room centre show one room instead of overlapping walls. This model uses every frame. Walls are still somewhat thick and sizes are not reliable.",
    splatUrl: "/splats/scan009_v9plf.spz",
    splatStart: { position: [-0.47, 0.06, -0.41], target: [-0.51, -0.12, 0.57] },
  },
  {
    // R-092 (2026-11-21): R-081's cameras, Gaussians reaching into the camera path pruned during training, and depth
    // priors for the 77 frames without SfM points (mono_prior.py --fill_scale). Trained with 69 held-out frames.
    // File is local only (git-ignored).
    id: "scan-009-depthfill",
    name: "Scan 009 · depth priors filled + path pruning",
    floor: "—",
    block: "Residence",
    area: "Not measured",
    location: "scan_009_057ed3beb4fc • gyro + accelerometer + video tracks",
    dateCaptured: "Nov 15, 2026",
    status: "draft",
    statusLabel: "Experimental · 553 of 894 keyframes · scale ~2× too large",
    thumbnail: "/thumbnails/scan009_v9pgsr.jpg",
    scansCount: 1,
    gaussianCount: "591,387",
    accuracy: "Scale unknown (estimates say the model is about 2× too large)",
    captureDevice: "realme RMX5111 (ARCore)",
    description:
      "Same camera path as the track-corrected model. Two changes aimed at the depth seen from off-path angles: frames that had no depth guidance (no tracked points, mostly the low-texture stretches) now get one, and splats floating in the camera's own path are removed during training. On frames held out from training the walls are flatter (6.8 vs 9.9 cm) and no view is blocked; colour match is about the same. 69 frames were held out, so a few views have less detail. Sizes are not reliable.",
    splatUrl: "/splats/scan009_v9pfu.spz",
    splatStart: { position: [-0.15, -0.03, -0.11], target: [-0.22, -0.21, 0.87] },
  },
  {
    // R-012 (2026-10-12), saved_models/2026-10-12_sharp_mvs_v6. File is local only (git-ignored, > 10 MB).
    id: "newroom-v6",
    name: "Living Room · v6 sharp frames + MVS (older)",
    floor: "Ground Floor",
    block: "Residence",
    area: "≈ 29 m²",
    location: "Ground Floor • Residence • ≈ 29 m²",
    dateCaptured: "Oct 10, 2026",
    status: "complete",
    statusLabel: "Older version · 597K splats",
    thumbnail: "/thumbnails/newroom_v6.jpg",
    scansCount: 1,
    gaussianCount: "596,638",
    accuracy: "See R-012 / D-018",
    captureDevice: "realme RMX5111 (ARCore)",
    description:
      "Earlier best model of the living room (R-012): gyro-selected sharp frames, COLMAP PatchMatch dense init, splatfacto. About 4 h end to end; superseded by the v9 recipe.",
    splatUrl: "/splats/newroom_v6.spz",
    splatStart: { position: [-0.98, -0.06, -0.2], target: [-1.98, -0.36, -0.2] },
  },
  {
    // R-009 (2026-10-11), saved_models/2026-10-11_sfm_v3. File is local only (git-ignored, > 10 MB).
    id: "newroom-v3",
    name: "Living Room · v3 first SfM pipeline (older)",
    floor: "Ground Floor",
    block: "Residence",
    area: "≈ 29 m²",
    location: "Ground Floor • Residence • ≈ 29 m²",
    dateCaptured: "Oct 10, 2026",
    status: "complete",
    statusLabel: "Older version · 528K splats",
    thumbnail: "/thumbnails/newroom_v6.jpg",
    scansCount: 1,
    gaussianCount: "528,227",
    accuracy: "See R-009 / D-014",
    captureDevice: "realme RMX5111 (ARCore)",
    description:
      "First SfM-pose model of the living room (R-009): COLMAP global mapper scaled to ARCore, splatfacto 30k from sparse points. Kept for comparison with the later versions.",
    splatUrl: "/splats/newroom_v3.spz",
    splatStart: { position: [-0.98, -0.06, -0.2], target: [-1.98, -0.36, -0.2] },
  },
  {
    id: "sector-4-mep",
    name: "Sector 4 MEP Room",
    floor: "Floor 3",
    block: "Block B",
    area: "847 m²",
    location: "Floor 3 • Block B • 847 m²",
    dateCaptured: "Apr 22, 2025",
    status: "processing",
    statusLabel: "Training · RTX 4090",
    thumbnail: "/thumbnails/card1_mep.jpg",
    scansCount: 6,
    gaussianCount: "1,240,000",
    accuracy: "±1.2 mm",
    captureDevice: "Pixel 9 Pro (ARCore 120Hz)",
    description: "Main mechanical distribution room with chilled water headers, primary pump sets, and motor control centers."
  },
  {
    id: "tower-a-floors-5-8",
    name: "Tower A - Floors 5-8",
    floor: "Floor 6",
    block: "Block A",
    area: "1,240 m²",
    location: "Floor 6 • Block A • 1,240 m²",
    dateCaptured: "Apr 28, 2025",
    status: "ready",
    statusLabel: "3DGS Ready · 1.45M splats",
    thumbnail: "/thumbnails/card2_tower_a.jpg",
    scansCount: 8,
    gaussianCount: "1,450,000",
    accuracy: "±1.1 mm",
    captureDevice: "Galaxy S24 Ultra (ARCore 120Hz)",
    description: "Multi-floor vertical risers and acoustic ceiling plenum coordination scan."
  },
  {
    id: "west-wing",
    name: "West Wing",
    floor: "Floor 2",
    block: "Block C",
    area: "956 m²",
    location: "Floor 2 • Block C • 956 m²",
    dateCaptured: "Apr 22, 2025",
    status: "complete",
    statusLabel: "Signed Off · Handed to Coordinator",
    thumbnail: "/thumbnails/card3_west_wing.jpg",
    scansCount: 12,
    gaussianCount: "1,820,000",
    accuracy: "±0.9 mm",
    captureDevice: "iPhone 16 Pro (ARKit 120Hz)",
    description: "Completed framing, rough-in mechanical ducts, and cable tray validation."
  },
  {
    id: "parking-garage",
    name: "Parking Garage",
    floor: "Floor 1",
    block: "Block D",
    area: "2,301 m²",
    location: "Floor 1 • Block D • 2,301 m²",
    dateCaptured: "Apr 18, 2025",
    status: "draft",
    statusLabel: "Draft · Awaiting Capture",
    thumbnail: "/thumbnails/card4_parking.jpg",
    scansCount: 3,
    gaussianCount: "620,000",
    accuracy: "±1.5 mm",
    captureDevice: "Pixel 8 Pro (ARCore 120Hz)",
    description: "Ground floor parking deck structural columns and overhead drainage runs."
  },
  {
    id: "north-tower",
    name: "North Tower",
    floor: "Floor 7",
    block: "Block A",
    area: "1,620 m²",
    location: "Floor 7 • Block A • 1,620 m²",
    dateCaptured: "Apr 15, 2025",
    status: "ready",
    statusLabel: "3DGS Ready · 1.65M splats",
    thumbnail: "/thumbnails/card5_north_tower.jpg",
    scansCount: 10,
    gaussianCount: "1,650,000",
    accuracy: "±1.2 mm",
    captureDevice: "Pixel 9 Pro (ARCore 120Hz)",
    description: "High-density tenant fit-out zone with perimeter VAV boxes and sprinkler drops."
  },
  {
    id: "east-wing",
    name: "East Wing",
    floor: "Floor 4",
    block: "Block B",
    area: "1,087 m²",
    location: "Floor 4 • Block B • 1,087 m²",
    dateCaptured: "Apr 12, 2025",
    status: "processing",
    statusLabel: "Queued · 2 of 6 workers",
    thumbnail: "/thumbnails/card6_east_wing.jpg",
    scansCount: 7,
    gaussianCount: "990,000",
    accuracy: "±1.4 mm",
    captureDevice: "Galaxy S24 Ultra (ARCore 120Hz)",
    description: "Emergency power distribution corridor and high-voltage feeder routing."
  }
];

export interface FloorPlanSector {
  id: string;
  name: string;
  sectorCode: string;
  level: string;
  area: string;
  status: "ready" | "processing" | "complete";
  statusColor: string;
  targetProjectId: string;
  xPercent: number;
  yPercent: number;
  widthPercent: number;
  heightPercent: number;
  scansCount: number;
  accuracy: string;
  description: string;
}

export const MOCK_FLOOR_PLAN_SECTORS: FloorPlanSector[] = [
  {
    id: "sec-mep",
    name: "Sector 4 MEP Room",
    sectorCode: "SEC-4-MEP",
    level: "Level 3 - Block B",
    area: "847 m²",
    status: "ready",
    statusColor: "#2563eb",
    targetProjectId: "sector-4-mep",
    xPercent: 18,
    yPercent: 22,
    widthPercent: 28,
    heightPercent: 32,
    scansCount: 6,
    accuracy: "±1.2 mm",
    description: "Chilled water headers, valve manifolds, and primary electrical distribution panels."
  },
  {
    id: "sec-tower-a",
    name: "Tower A Corridor & Shaft",
    sectorCode: "TOW-A-CORR",
    level: "Level 6 - Block A",
    area: "1,240 m²",
    status: "ready",
    statusColor: "#10b981",
    targetProjectId: "tower-a-floors-5-8",
    xPercent: 50,
    yPercent: 18,
    widthPercent: 38,
    heightPercent: 28,
    scansCount: 8,
    accuracy: "±1.1 mm",
    description: "Central riser shafts, HVAC main supply run, and data cable tray trunks."
  },
  {
    id: "sec-west-wing",
    name: "West Wing Fit-Out",
    sectorCode: "WW-FL2",
    level: "Level 2 - Block C",
    area: "956 m²",
    status: "complete",
    statusColor: "#059669",
    targetProjectId: "west-wing",
    xPercent: 14,
    yPercent: 58,
    widthPercent: 34,
    heightPercent: 32,
    scansCount: 12,
    accuracy: "±0.9 mm",
    description: "Drywall stud framing, branch hydronic piping, and lighting circuits."
  },
  {
    id: "sec-east-wing",
    name: "East Wing Power Corridor",
    sectorCode: "EW-FL4",
    level: "Level 4 - Block B",
    area: "1,087 m²",
    status: "processing",
    statusColor: "#d97706",
    targetProjectId: "east-wing",
    xPercent: 52,
    yPercent: 52,
    widthPercent: 36,
    heightPercent: 38,
    scansCount: 7,
    accuracy: "±1.4 mm",
    description: "High-voltage switchgear feeder conduit banks and emergency generator runs."
  }
];

export interface PipelineStep {
  id: string;
  title: string;
  subtitle: string;
  status: "complete" | "in_progress" | "pending";
  progress?: number;
  duration?: string;
  details: string;
}

export const MOCK_PIPELINE_STEPS: PipelineStep[] = [
  {
    id: "step-1",
    title: "Mobile Telemetry Ingest",
    subtitle: "30 FPS 4K Visual Frames + 120 Hz ARCore IMU",
    status: "complete",
    duration: "18s",
    details: "Ingested visual frames with timestamp-synchronized 6-DoF odometry and sparse feature points."
  },
  {
    id: "step-2",
    title: "Pose Prior Matrix Conversion",
    subtitle: "Quaternion -> 3x3 SO(3) & OpenGL -> OpenCV",
    status: "complete",
    duration: "4s",
    details: "Executed build_transforms.py: inverting Y & Z axes to prevent ray divergence and exporting points3D.ply initial seed."
  },
  {
    id: "step-3",
    title: "Metric Scale Normalization",
    subtitle: "Absolute Real-World Scale Calibration",
    status: "complete",
    duration: "12s",
    details: "Fused physical millimeter scale priors from phone visual-inertial state estimator. Enforces 1.0 scene unit = 1.000 meter."
  },
  {
    id: "step-4",
    title: "3D Gaussian Splatting Training",
    subtitle: "Nerfstudio splatfacto (30,000 Iterations)",
    status: "in_progress",
    progress: 68,
    duration: "4m 12s elapsed (est. 1m 55s left)",
    details: "Iter 20,400 / 30,000. Current Loss: 0.0031 | PSNR: 29.4 dB | Active Gaussians: 1,248,320."
  },
  {
    id: "step-5",
    title: "AI Semantic Segmentation",
    subtitle: "YOLOv8-Seg 2D Masks -> 3D Point Projection",
    status: "pending",
    details: "Projects classified 2D masks into 3D space to isolate Pipes, Conduits, and HVAC Ducts."
  },
  {
    id: "step-6",
    title: ".ksplat WebGPU Packaging",
    subtitle: "LOD Octree Chunking & Streaming Optimization",
    status: "pending",
    details: "Compresses float32 Gaussians into quantized 16-bit .ksplat for 60 FPS in-browser WebGPU rendering."
  }
];

/* -------------------------------------------------------------------------- */
/* Building floor plans (S2.5)                                                */
/* -------------------------------------------------------------------------- */

export type FloorPlanRoomKind =
  | "mep"
  | "office"
  | "conference"
  | "utility"
  | "lobby"
  | "corridor";

export type FloorPlanRoomStatus = "ready" | "processing" | "complete";

export interface FloorPlanRoom {
  id: string;
  name: string;
  kind: FloorPlanRoomKind;
  status: FloorPlanRoomStatus;
  scanCount: number;
  /** Rectangle in the plan's 1000×620 viewBox. */
  x: number;
  y: number;
  w: number;
  h: number;

  /**
   * Where clicking this room's node should navigate. Optional — set through
   * the Room Editor to map an uploaded plan's rooms onto existing captured
   * projects. When unset, `FloorPlanCanvas` falls back to the plan-level
   * `targetProjectId` prop.
   */
  targetProjectId?: string;
}

/** Door swing arc — small ¼ circle rendered on top of walls. */
export interface FloorPlanDoor {
  cx: number;
  cy: number;
  radius: number;
  /** Quadrant of the arc: "tr" | "tl" | "br" | "bl". */
  quadrant: "tr" | "tl" | "br" | "bl";
}

export interface BuildingFloor {
  id: string;
  label: string;
  discipline: string;
  totalArea: string;
  rooms: FloorPlanRoom[];
  doors: FloorPlanDoor[];

  /**
   * Optional user-uploaded background. When set, `FloorPlanCanvas` renders
   * this image inside the 1000×620 viewBox instead of the hand-authored walls
   * / dimensions / compass. Nodes still position by absolute viewBox coords
   * so they don't care which base layer is drawn beneath them. Stored as a
   * base64 data URL because uploaded plans live in `localStorage`, not on
   * disk.
   */
  planImageDataUrl?: string;
  /** Natural pixel dimensions of the uploaded image, for aspect preservation. */
  planImageWidth?: number;
  planImageHeight?: number;
}

export interface BuildingPlan {
  projectId: string;
  buildingName: string;
  floors: BuildingFloor[];

  /** True for plans uploaded through the Create Project flow. */
  isUserCreated?: boolean;
  /** ISO timestamp of first save. Only set on user-created plans. */
  createdAt?: string;
}

export const MOCK_BUILDING_PLANS: BuildingPlan[] = [
  {
    projectId: "tower-a-floors-5-8",
    buildingName: "Tower A",
    floors: [
      {
        id: "floor-5",
        label: "Floor 5",
        discipline: "Mechanical Plant",
        totalArea: "1,240 m²",
        rooms: [
          { id: "f5-chiller", name: "Chiller Plant", kind: "mep", status: "ready", scanCount: 6, x: 60, y: 60, w: 340, h: 220 },
          { id: "f5-boiler", name: "Boiler Room", kind: "mep", status: "processing", scanCount: 3, x: 60, y: 300, w: 220, h: 260 },
          { id: "f5-pump", name: "Pump Skid Room", kind: "utility", status: "ready", scanCount: 4, x: 300, y: 320, w: 220, h: 240 },
          { id: "f5-corridor", name: "Service Corridor", kind: "corridor", status: "complete", scanCount: 2, x: 540, y: 60, w: 400, h: 90 },
          { id: "f5-electrical", name: "Main Electrical", kind: "mep", status: "ready", scanCount: 5, x: 540, y: 170, w: 400, h: 190 },
          { id: "f5-tank", name: "Water Tank Room", kind: "utility", status: "processing", scanCount: 2, x: 540, y: 380, w: 400, h: 180 },
        ],
        doors: [
          { cx: 400, cy: 200, radius: 22, quadrant: "tr" },
          { cx: 300, cy: 400, radius: 22, quadrant: "tl" },
          { cx: 540, cy: 240, radius: 22, quadrant: "tl" },
          { cx: 540, cy: 460, radius: 22, quadrant: "tl" },
        ],
      },
      {
        id: "floor-6",
        label: "Floor 6",
        discipline: "Open Office",
        totalArea: "1,340 m²",
        rooms: [
          { id: "f6-lobby", name: "Lobby & Reception", kind: "lobby", status: "complete", scanCount: 4, x: 60, y: 60, w: 260, h: 180 },
          { id: "f6-conf-a", name: "Conference Room A", kind: "conference", status: "ready", scanCount: 3, x: 60, y: 260, w: 260, h: 160 },
          { id: "f6-conf-b", name: "Conference Room B", kind: "conference", status: "processing", scanCount: 2, x: 60, y: 440, w: 260, h: 120 },
          { id: "f6-open-office", name: "Open Office Bay", kind: "office", status: "ready", scanCount: 8, x: 340, y: 60, w: 460, h: 360 },
          { id: "f6-huddle", name: "Huddle Zone", kind: "office", status: "ready", scanCount: 3, x: 340, y: 440, w: 220, h: 120 },
          { id: "f6-break", name: "Break Room", kind: "utility", status: "complete", scanCount: 2, x: 580, y: 440, w: 360, h: 120 },
          { id: "f6-corridor", name: "West Corridor", kind: "corridor", status: "complete", scanCount: 1, x: 820, y: 60, w: 120, h: 360 },
        ],
        doors: [
          { cx: 320, cy: 130, radius: 22, quadrant: "tl" },
          { cx: 320, cy: 340, radius: 22, quadrant: "tl" },
          { cx: 320, cy: 500, radius: 22, quadrant: "tl" },
          { cx: 820, cy: 240, radius: 22, quadrant: "tr" },
          { cx: 580, cy: 500, radius: 22, quadrant: "tr" },
        ],
      },
      {
        id: "floor-7",
        label: "Floor 7",
        discipline: "Executive Suites",
        totalArea: "1,280 m²",
        rooms: [
          { id: "f7-reception", name: "Executive Reception", kind: "lobby", status: "ready", scanCount: 3, x: 60, y: 60, w: 380, h: 160 },
          { id: "f7-ceo", name: "CEO Office", kind: "office", status: "complete", scanCount: 4, x: 60, y: 240, w: 240, h: 200 },
          { id: "f7-boardroom", name: "Boardroom", kind: "conference", status: "ready", scanCount: 6, x: 320, y: 240, w: 320, h: 200 },
          { id: "f7-vp-1", name: "VP Office 1", kind: "office", status: "processing", scanCount: 2, x: 460, y: 60, w: 220, h: 160 },
          { id: "f7-vp-2", name: "VP Office 2", kind: "office", status: "processing", scanCount: 2, x: 700, y: 60, w: 240, h: 160 },
          { id: "f7-lounge", name: "Executive Lounge", kind: "office", status: "ready", scanCount: 3, x: 660, y: 240, w: 280, h: 200 },
          { id: "f7-corridor", name: "South Corridor", kind: "corridor", status: "complete", scanCount: 1, x: 60, y: 460, w: 880, h: 100 },
        ],
        doors: [
          { cx: 300, cy: 300, radius: 22, quadrant: "tr" },
          { cx: 320, cy: 320, radius: 22, quadrant: "tl" },
          { cx: 700, cy: 320, radius: 22, quadrant: "tr" },
          { cx: 460, cy: 140, radius: 22, quadrant: "tr" },
          { cx: 700, cy: 140, radius: 22, quadrant: "tr" },
          { cx: 500, cy: 460, radius: 22, quadrant: "bl" },
        ],
      },
      {
        id: "floor-8",
        label: "Floor 8",
        discipline: "Rooftop Utilities",
        totalArea: "980 m²",
        rooms: [
          { id: "f8-hvac", name: "Rooftop HVAC", kind: "mep", status: "ready", scanCount: 5, x: 60, y: 60, w: 460, h: 260 },
          { id: "f8-elevator", name: "Elevator Overrun", kind: "utility", status: "complete", scanCount: 2, x: 540, y: 60, w: 200, h: 260 },
          { id: "f8-solar", name: "Solar Array Shed", kind: "utility", status: "processing", scanCount: 3, x: 760, y: 60, w: 180, h: 260 },
          { id: "f8-mech-corridor", name: "Rooftop Walkway", kind: "corridor", status: "complete", scanCount: 1, x: 60, y: 340, w: 880, h: 100 },
          { id: "f8-storage", name: "Maintenance Store", kind: "utility", status: "ready", scanCount: 2, x: 60, y: 460, w: 340, h: 100 },
          { id: "f8-antenna", name: "Antenna Deck", kind: "utility", status: "ready", scanCount: 3, x: 420, y: 460, w: 520, h: 100 },
        ],
        doors: [
          { cx: 540, cy: 180, radius: 22, quadrant: "tl" },
          { cx: 760, cy: 180, radius: 22, quadrant: "tl" },
          { cx: 200, cy: 340, radius: 22, quadrant: "tr" },
          { cx: 400, cy: 460, radius: 22, quadrant: "tr" },
        ],
      },
    ],
  },
];

export const findBuildingPlan = (projectId: string): BuildingPlan | undefined =>
  MOCK_BUILDING_PLANS.find((plan) => plan.projectId === projectId);

export const hasBuildingPlan = (projectId: string): boolean =>
  MOCK_BUILDING_PLANS.some((plan) => plan.projectId === projectId);

export type SavedMeasurementKind =
  | "length"
  | "height"
  | "pipe"
  | "width"
  | "beam";

export interface SavedMeasurement {
  id: string;
  kind: SavedMeasurementKind;
  value: string;
  label: string;
  timestamp: string;
  projectId: string;
}

export const MOCK_SAVED_MEASUREMENTS: SavedMeasurement[] = [
  {
    id: "sm-1",
    kind: "length",
    value: "12.48 m",
    label: "Main Supply Duct Length",
    timestamp: "Apr 28, 10:42 AM",
    projectId: "sector-4-mep",
  },
  {
    id: "sm-2",
    kind: "height",
    value: "3.20 m",
    label: "Slab-to-Ceiling Clear Height",
    timestamp: "Apr 28, 10:36 AM",
    projectId: "sector-4-mep",
  },
  {
    id: "sm-3",
    kind: "pipe",
    value: "168 mm",
    label: "Chilled Water Pipe OD",
    timestamp: "Apr 27, 4:18 PM",
    projectId: "sector-4-mep",
  },
  {
    id: "sm-4",
    kind: "width",
    value: "1.42 m",
    label: "HVAC Duct Width",
    timestamp: "Apr 27, 2:05 PM",
    projectId: "sector-4-mep",
  },
  {
    id: "sm-5",
    kind: "beam",
    value: "6.75 m",
    label: "Structural Beam Span",
    timestamp: "Apr 26, 11:22 AM",
    projectId: "sector-4-mep",
  },
];

/* -------------------------------------------------------------------------- */
/* Project files (S8)                                                         */
/* -------------------------------------------------------------------------- */

export type ProjectFileKind = "ply" | "ksplat" | "obj" | "pdf" | "csv" | "png" | "json";

export interface ProjectFile {
  id: string;
  name: string;
  kind: ProjectFileKind;
  sizeLabel: string;
  uploadedAt: string;
  author: string;
}

export const MOCK_PROJECT_FILES: ProjectFile[] = [
  {
    id: "pf-1",
    name: "sector4_mep_raw.ply",
    kind: "ply",
    sizeLabel: "412 MB",
    uploadedAt: "Apr 22, 2025",
    author: "BuildScan Edge Worker",
  },
  {
    id: "pf-2",
    name: "sector4_mep.ksplat",
    kind: "ksplat",
    sizeLabel: "84.3 MB",
    uploadedAt: "Apr 22, 2025",
    author: "BuildScan Edge Worker",
  },
  {
    id: "pf-3",
    name: "sector4_mep_mesh.obj",
    kind: "obj",
    sizeLabel: "126 MB",
    uploadedAt: "Apr 22, 2025",
    author: "Nerfstudio Export",
  },
  {
    id: "pf-4",
    name: "coordination_report_v3.pdf",
    kind: "pdf",
    sizeLabel: "2.8 MB",
    uploadedAt: "Apr 24, 2025",
    author: "Ahmad Raza",
  },
  {
    id: "pf-5",
    name: "duct_measurements.csv",
    kind: "csv",
    sizeLabel: "18 KB",
    uploadedAt: "Apr 28, 2025",
    author: "Sarah Khan",
  },
  {
    id: "pf-6",
    name: "clash_snapshot.png",
    kind: "png",
    sizeLabel: "1.4 MB",
    uploadedAt: "Apr 28, 2025",
    author: "Sarah Khan",
  },
  {
    id: "pf-7",
    name: "transforms.json",
    kind: "json",
    sizeLabel: "42 KB",
    uploadedAt: "Apr 22, 2025",
    author: "build_transforms.py",
  },
];

/* -------------------------------------------------------------------------- */
/* Comparison view (S4b)                                                      */
/* -------------------------------------------------------------------------- */

export interface ComparisonScan {
  id: string;
  label: string;
  date: string;
  hexColor: string;   // tint for the render + legend swatch
  gaussians: string;
  captureDevice: string;
}

export interface ComparisonPair {
  older: ComparisonScan;
  newer: ComparisonScan;
}

export const MOCK_COMPARISON_PAIR: ComparisonPair = {
  older: {
    id: "scan-a",
    label: "Scan A",
    date: "Apr 12, 2025",
    hexColor: "#2563eb",
    gaussians: "1,180,320",
    captureDevice: "Pixel 9 Pro (ARCore 120Hz)",
  },
  newer: {
    id: "scan-b",
    label: "Scan B",
    date: "Apr 28, 2025",
    hexColor: "#059669",
    gaussians: "1,248,320",
    captureDevice: "Pixel 9 Pro (ARCore 120Hz)",
  },
};

export type ChangeType = "added" | "removed" | "modified";

export interface ChangeLogEntry {
  id: string;
  element: string;
  changeType: ChangeType;
  layer: string;
  delta: string;
  flagged: boolean;
}

export const MOCK_CHANGE_LOG: ChangeLogEntry[] = [
  {
    id: "cl-1",
    element: "HVAC Duct Run 3B",
    changeType: "modified",
    layer: "HVAC",
    delta: "+0.24 m offset",
    flagged: true,
  },
  {
    id: "cl-2",
    element: "Sprinkler Head SP-042",
    changeType: "added",
    layer: "Fire Protection",
    delta: "+1 element",
    flagged: false,
  },
  {
    id: "cl-3",
    element: "Conduit Run E-14",
    changeType: "removed",
    layer: "Electrical",
    delta: "-3.20 m routing",
    flagged: true,
  },
  {
    id: "cl-4",
    element: "Chilled Water Pipe P-08",
    changeType: "modified",
    layer: "Plumbing",
    delta: "+12 mm OD",
    flagged: false,
  },
  {
    id: "cl-5",
    element: "Support Bracket B-201",
    changeType: "added",
    layer: "Structural",
    delta: "+1 element",
    flagged: false,
  },
];

/* -------------------------------------------------------------------------- */
/* Notifications (S6)                                                         */
/* -------------------------------------------------------------------------- */

export type NotificationKind =
  | "scan_processing"
  | "scan_completed"
  | "scan_failed"
  | "measurement_added"
  | "comment"
  | "project_archived";

export type NotificationCategory = "scans" | "projects" | "system";

export interface NotificationItem {
  id: string;
  kind: NotificationKind;
  category: NotificationCategory;
  title: string;
  description: string;
  timeAgo: string;
  unread: boolean;
}

export const MOCK_NOTIFICATIONS: NotificationItem[] = [
  {
    id: "n-1",
    kind: "scan_processing",
    category: "scans",
    title: "Scan Processing",
    description: "Sector 4 MEP Room is training on RTX 4090 (20,400 / 30,000 iters).",
    timeAgo: "12m ago",
    unread: true,
  },
  {
    id: "n-2",
    kind: "scan_completed",
    category: "scans",
    title: "Scan Ready",
    description: "Tower A — Floor 6 finished capture with 1.45M active Gaussians.",
    timeAgo: "1h ago",
    unread: true,
  },
  {
    id: "n-3",
    kind: "measurement_added",
    category: "projects",
    title: "New Measurement",
    description: "Sarah Khan added “Duct Length — 12.48 m” to West Wing.",
    timeAgo: "3h ago",
    unread: true,
  },
  {
    id: "n-4",
    kind: "comment",
    category: "projects",
    title: "New Comment",
    description: "Ahmad Raza commented on the North Tower coordination report.",
    timeAgo: "5h ago",
    unread: false,
  },
  {
    id: "n-5",
    kind: "project_archived",
    category: "system",
    title: "Project Archived",
    description: "Basement Level 1 was archived by the workspace admin.",
    timeAgo: "Yesterday",
    unread: false,
  },
  {
    id: "n-6",
    kind: "scan_failed",
    category: "scans",
    title: "Scan Failed",
    description: "East Wing Corridor capture rejected — motion blur above threshold.",
    timeAgo: "2d ago",
    unread: false,
  },
];

export const MOCK_TERMINAL_LOGS = [
  "[00:00:01] [INFO] Connection established with BuildScan Edge Worker (NVIDIA RTX 4090 24GB)",
  "[00:00:03] [INGEST] Received payload scan_sector4_mep.tar.gz",
  "[00:00:18] [INGEST] Extracted 4,950 video frames and poses.csv (19,800 IMU records @ 120Hz)",
  "[00:00:21] [TRANSFORMS] Running build_transforms.py --csv poses.csv --points points.csv",
  "[00:00:22] [TRANSFORMS] Exported 4,280 sparse ARCore feature points to points3D.ply",
  "[00:00:25] [TRANSFORMS] Generated transforms.json with fl_x=1662.77, camera_angle_x=1.0472 rad",
  "[00:00:26] [SCALE] Applied metric scale anchor: 1 scene unit = 1.000000 meter",
  "[00:00:30] [NERFSTUDIO] Initializing splatfacto model on CUDA:0...",
  "[00:01:00] [TRAIN] Step 5,000/30,000 | Loss: 0.0124 | PSNR: 22.1 dB",
  "[00:02:00] [TRAIN] Step 10,000/30,000 | Loss: 0.0078 | PSNR: 25.6 dB",
  "[00:03:00] [TRAIN] Step 15,000/30,000 | Loss: 0.0049 | PSNR: 27.9 dB",
  "[00:04:12] [TRAIN] Step 20,400/30,000 | Loss: 0.0031 | PSNR: 29.4 dB | Gaussians: 1,248,320 [ACTIVE]"
];
