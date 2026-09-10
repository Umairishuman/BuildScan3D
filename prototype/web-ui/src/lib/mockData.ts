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
