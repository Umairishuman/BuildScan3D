export interface Project {
  id: string;
  name: string;
  location: string;
  category: "MEP Room" | "Corridor" | "HVAC Plant" | "Structure" | "Fire Systems";
  dateCaptured: string;
  status: "ready" | "processing" | "draft";
  statusLabel: string;
  thumbnail: string;
  gaussianCount?: string;
  accuracy?: string;
  captureDevice?: string;
  duration?: string;
  progressPercent?: number;
  currentStep?: string;
  description: string;
}

export const MOCK_PROJECTS: Project[] = [
  {
    id: "sector-4-mep",
    name: "Sector 4 — MEP Mechanical Room",
    location: "Block B, Basement Level 1",
    category: "MEP Room",
    dateCaptured: "Sep 5, 2026",
    status: "ready",
    statusLabel: "Ready for Inspection",
    thumbnail: "/thumbnails/mep_room.jpg",
    gaussianCount: "1,240,000",
    accuracy: "±1.2 mm",
    captureDevice: "Pixel 9 Pro (ARCore 120Hz)",
    duration: "2m 45s (4,950 frames)",
    description: "Main mechanical distribution room with high-pressure chilled water supply, primary return headers, and 480V motor control center conduit feeds."
  },
  {
    id: "basement-hvac-duct",
    name: "Basement HVAC Main Duct & Chillers",
    location: "Central Utility Plant, Zone 2",
    category: "HVAC Plant",
    dateCaptured: "Sep 7, 2026",
    status: "processing",
    statusLabel: "Processing (68%)",
    progressPercent: 68,
    currentStep: "3D Gaussian Splatting Training (splatfacto @ 20,400/30,000 iters)",
    thumbnail: "/thumbnails/hvac_plant.jpg",
    gaussianCount: "890,000 (Training)",
    accuracy: "±1.5 mm (Target)",
    captureDevice: "Galaxy S24 Ultra (ARCore 120Hz)",
    duration: "3m 12s (5,760 frames)",
    description: "Large volume primary supply air duct run transitioning into ceiling plenum with pneumatic damper actuators."
  },
  {
    id: "level-2-electrical",
    name: "Level 2 Electrical Corridor & Cable Trays",
    location: "Tower A, 2nd Floor East Wing",
    category: "Corridor",
    dateCaptured: "Sep 2, 2026",
    status: "ready",
    statusLabel: "Ready for Inspection",
    thumbnail: "/thumbnails/electrical.jpg",
    gaussianCount: "850,000",
    accuracy: "±1.4 mm",
    captureDevice: "iPhone 16 Pro (ARKit 120Hz)",
    duration: "1m 50s (3,300 frames)",
    description: "High-density cable tray routing carrying redundant 3-phase feeds and emergency lighting branch circuits."
  },
  {
    id: "podium-fire-suppression",
    name: "Podium Level Fire Suppression & Standpipe",
    location: "Parking Podium P1, Grid C-4",
    category: "Fire Systems",
    dateCaptured: "Aug 22, 2026",
    status: "ready",
    statusLabel: "Ready for Inspection",
    thumbnail: "/thumbnails/fire.jpg",
    gaussianCount: "920,000",
    accuracy: "±1.1 mm",
    captureDevice: "Pixel 8 Pro (ARCore 120Hz)",
    duration: "2m 10s (3,900 frames)",
    description: "Wet sprinkler main riser with flow alarm switches, check valves, and Siamese connection branch piping."
  },
  {
    id: "ground-floor-framing",
    name: "Ground Floor Structural Framing & Drywall",
    location: "Main Entrance Atrium",
    category: "Structure",
    dateCaptured: "Aug 29, 2026",
    status: "draft",
    statusLabel: "Draft (Telemetry Saved)",
    thumbnail: "/thumbnails/framing.jpg",
    captureDevice: "Pixel 9 Pro (ARCore 120Hz)",
    duration: "1m 15s (2,250 frames)",
    description: "Light-gauge steel stud framing inspection prior to acoustic insulation and gypsum board enclosure."
  },
  {
    id: "roof-chiller-plant",
    name: "Roof Level Chiller Plant & Risers",
    location: "Rooftop Sector C",
    category: "HVAC Plant",
    dateCaptured: "Aug 25, 2026",
    status: "ready",
    statusLabel: "Ready for Inspection",
    thumbnail: "/thumbnails/roof.jpg",
    gaussianCount: "1,650,000",
    accuracy: "±1.8 mm",
    captureDevice: "Pixel 9 Pro (ARCore 120Hz)",
    duration: "4m 05s (7,350 frames)",
    description: "Outdoor package chillers with dual vibration isolators, condenser loop piping, and acoustic wind baffles."
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
    details: "Ingested 5,760 visual frames @ 3840x2160 with timestamp-synchronized 6-DoF odometry and sparse feature points."
  },
  {
    id: "step-2",
    title: "Pose Prior Matrix Conversion",
    subtitle: "Quaternion [qx, qy, qz, qw] -> 3x3 SO(3) & OpenGL -> OpenCV",
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
    details: "Will project classified 2D masks into 3D space to isolate Pipes (Hydronics), Conduits (Electrical), and HVAC Ducts."
  },
  {
    id: "step-6",
    title: ".ksplat WebGPU Packaging",
    subtitle: "LOD Octree Chunking & Streaming Optimization",
    status: "pending",
    details: "Will compress float32 Gaussians into quantized 16-bit .ksplat for 60 FPS in-browser WebGPU rendering."
  }
];

export const MOCK_TERMINAL_LOGS = [
  "[00:00:01] [INFO] Connection established with BuildScan Edge Worker #4 (NVIDIA RTX 4090 24GB)",
  "[00:00:03] [INGEST] Received payload scan_hvac_zone2.tar.gz (520 MB)",
  "[00:00:18] [INGEST] Extracted 5,760 video frames and poses.csv (23,040 IMU records @ 120Hz)",
  "[00:00:21] [TRANSFORMS] Running build_transforms.py --csv poses.csv --points points.csv",
  "[00:00:22] [TRANSFORMS] Exported 4,280 sparse ARCore feature points to points3D.ply",
  "[00:00:25] [TRANSFORMS] Generated transforms.json with fl_x=1662.77, camera_angle_x=1.0472 rad",
  "[00:00:26] [SCALE] Applied metric scale anchor: 1 scene unit = 1.000000 meter (SE(3) Sim(3) locked)",
  "[00:00:30] [NERFSTUDIO] Initializing splatfacto model on CUDA:0...",
  "[00:01:00] [TRAIN] Step 5,000/30,000 | Loss: 0.0124 | PSNR: 22.1 dB | Gaussians: 342,000",
  "[00:02:00] [TRAIN] Step 10,000/30,000 | Loss: 0.0078 | PSNR: 25.6 dB | Gaussians: 680,500",
  "[00:03:00] [TRAIN] Step 15,000/30,000 | Loss: 0.0049 | PSNR: 27.9 dB | Gaussians: 994,100",
  "[00:04:12] [TRAIN] Step 20,400/30,000 | Loss: 0.0031 | PSNR: 29.4 dB | Gaussians: 1,248,320 [ACTIVE]"
];
