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
}

export const MOCK_PROJECTS: Project[] = [
  {
    id: "sector-4-mep",
    name: "Sector 4 MEP Room",
    floor: "Floor 3",
    block: "Block B",
    area: "847 m²",
    location: "Floor 3 • Block B • 847 m²",
    dateCaptured: "Apr 22, 2025",
    status: "processing",
    statusLabel: "Processing",
    thumbnail: "/thumbnails/card1_mep.png",
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
    statusLabel: "Ready",
    thumbnail: "/thumbnails/card2_tower_a.png",
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
    statusLabel: "Complete",
    thumbnail: "/thumbnails/card3_west_wing.png",
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
    statusLabel: "Draft",
    thumbnail: "/thumbnails/card4_parking.png",
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
    statusLabel: "Ready",
    thumbnail: "/thumbnails/card5_north_tower.png",
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
    statusLabel: "Processing",
    thumbnail: "/thumbnails/card6_east_wing.png",
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
