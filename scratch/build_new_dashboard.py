import os

base_dir = r"d:\FYP\prototype\web-ui"

# 1. mockData.ts
mock_data_ts = """export interface Project {
  id: string;
  name: string;
  floor: string;
  block: string;
  area: string;
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
"""

with open(os.path.join(base_dir, "src", "lib", "mockData.ts"), "w", encoding="utf-8") as f:
    f.write(mock_data_ts)

# 2. Sidebar.tsx
sidebar_tsx = """\"use client\";

import React from "react";
import Link from "next/link";
import Image from "next/image";
import {
  LayoutDashboard,
  FolderKanban,
  ScanLine,
  Map,
  FileText,
  Users,
  Settings,
} from "lucide-react";

interface SidebarProps {
  currentTab: "dashboard" | "floorplan" | "projects" | "scans" | "reports" | "team" | "settings";
  onSelectTab: (tab: "dashboard" | "floorplan" | "projects" | "scans" | "reports" | "team" | "settings") => void;
  onOpenProject: (projectId: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentTab,
  onSelectTab,
  onOpenProject,
}) => {
  const mainNav = [
    { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
    { id: "projects", label: "Projects", icon: FolderKanban },
    { id: "scans", label: "Scans", icon: ScanLine },
    { id: "floorplan", label: "Floor Plan", icon: Map },
    { id: "reports", label: "Reports", icon: FileText },
    { id: "team", label: "Team", icon: Users },
    { id: "settings", label: "Settings", icon: Settings },
  ] as const;

  const recentSites = [
    { id: "sector-4-mep", name: "Sector 4 MEP Room", status: "Processing", color: "bg-amber-400" },
    { id: "tower-a-floors-5-8", name: "Tower A - Floors 5-8", status: "Ready", color: "bg-emerald-500" },
    { id: "west-wing", name: "West Wing", status: "Complete", color: "bg-teal-500" },
    { id: "parking-garage", name: "Parking Garage", status: "Draft", color: "bg-slate-400" },
  ];

  return (
    <aside className="w-56 shrink-0 min-h-screen bg-white border-r border-[#e2e8f0] flex flex-col justify-between p-4 select-none z-30">
      <div className="space-y-6">
        {/* Brand Logo */}
        <Link href="/dashboard" className="flex items-center gap-2 px-2 py-1.5 group">
          <div className="relative w-36 h-9">
            <Image
              src="/images/logo-new-removebg-preview.png"
              alt="BuildScan 3D"
              fill
              className="object-contain group-hover:scale-105 transition-transform"
              priority
            />
          </div>
        </Link>

        {/* Main Navigation Links */}
        <nav className="space-y-1">
          {mainNav.map((item) => {
            const Icon = item.icon;
            const isActive = currentTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onSelectTab(item.id)}
                className={`w-full flex items-center gap-3 px-3 py-2 rounded-xl text-xs font-semibold transition-all cursor-pointer relative ${
                  isActive
                    ? "text-[#2563eb] bg-blue-50/80 font-bold"
                    : "text-[#64748b] hover:text-[#0f172a] hover:bg-slate-50"
                }`}
              >
                {isActive && (
                  <span className="absolute left-0 top-1.5 bottom-1.5 w-1 bg-[#2563eb] rounded-r-full" />
                )}
                <Icon className={`w-4 h-4 ${isActive ? "text-[#2563eb]" : "text-[#94a3b8]"}`} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Recent Sites Section */}
      <div className="pt-6 border-t border-[#f1f5f9] space-y-3">
        <h4 className="text-[11px] font-bold text-[#64748b] uppercase tracking-wider px-2">
          Recent Sites
        </h4>
        <div className="space-y-2">
          {recentSites.map((site) => (
            <button
              key={site.id}
              onClick={() => onOpenProject(site.id)}
              className="w-full text-left px-2 py-1.5 rounded-lg hover:bg-slate-50 transition-colors group cursor-pointer"
            >
              <div className="flex items-center gap-2">
                <span className={`w-2 h-2 rounded-full ${site.color} shrink-0`} />
                <span className="text-xs font-semibold text-[#0f172a] group-hover:text-[#2563eb] truncate">
                  {site.name}
                </span>
              </div>
              <span className="text-[10px] text-[#64748b] pl-4 block">
                {site.status}
              </span>
            </button>
          ))}
        </div>
      </div>
    </aside>
  );
};
"""

with open(os.path.join(base_dir, "src", "components", "Sidebar.tsx"), "w", encoding="utf-8") as f:
    f.write(sidebar_tsx)

# 3. Navbar.tsx
navbar_tsx = """\"use client\";

import React from "react";
import { Search, Bell, ChevronDown } from "lucide-react";

interface NavbarProps {
  onOpenNewCapture: () => void;
  searchQuery: string;
  onSearchChange: (q: string) => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  onOpenNewCapture,
  searchQuery,
  onSearchChange,
}) => {
  return (
    <header className="h-16 w-full px-6 flex items-center justify-between border-b border-[#e2e8f0] bg-white/80 backdrop-blur-md text-[#0f172a] sticky top-0 z-20">
      {/* Left: Project Selector Dropdown */}
      <div className="flex items-center gap-3">
        <button className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-[#e2e8f0] bg-white hover:bg-slate-50 text-xs font-bold text-[#0f172a] transition-all shadow-sm cursor-pointer">
          <span>All Projects</span>
          <ChevronDown className="w-3.5 h-3.5 text-[#64748b]" />
        </button>

        {/* Search Pill Input */}
        <div className="relative w-80">
          <Search className="w-3.5 h-3.5 text-[#94a3b8] absolute left-3.5 top-2.5 pointer-events-none" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder="Search projects, scans, or sites..."
            className="w-full pl-9 pr-4 py-2 bg-slate-50 border border-[#e2e8f0] rounded-full text-xs text-[#0f172a] placeholder-[#94a3b8] focus:outline-none focus:border-[#2563eb] focus:bg-white transition-all shadow-inner"
          />
        </div>
      </div>

      {/* Right: Notifications, Team Avatars, User Profile */}
      <div className="flex items-center gap-4">
        {/* Notification Bell with Badge */}
        <button
          className="relative p-2 rounded-xl text-[#64748b] hover:text-[#0f172a] hover:bg-slate-100 transition-colors cursor-pointer"
          title="Notifications"
        >
          <Bell className="w-4 h-4" />
          <span className="absolute top-1 right-1 w-4 h-4 rounded-full bg-red-500 text-white text-[9px] font-bold flex items-center justify-center">
            3
          </span>
        </button>

        {/* Team Avatars Overlapping Stack */}
        <div className="flex items-center -space-x-2 overflow-hidden pl-1">
          <div className="w-7 h-7 rounded-full bg-slate-300 border-2 border-white flex items-center justify-center text-[10px] font-bold text-slate-700">
            JD
          </div>
          <div className="w-7 h-7 rounded-full bg-blue-500 border-2 border-white flex items-center justify-center text-[10px] font-bold text-white">
            SK
          </div>
          <div className="w-7 h-7 rounded-full bg-emerald-500 border-2 border-white flex items-center justify-center text-[10px] font-bold text-white">
            MR
          </div>
        </div>

        <div className="h-5 w-[1px] bg-[#e2e8f0]" />

        {/* User Profile Snippet (Ahmad Raza) */}
        <div className="flex items-center gap-2.5 pl-1">
          <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center text-white font-bold text-xs shadow-sm">
            AR
          </div>
          <div className="text-left">
            <div className="text-xs font-bold text-[#0f172a]">Ahmad Raza</div>
            <div className="text-[10px] text-[#64748b]">Project Manager</div>
          </div>
        </div>
      </div>
    </header>
  );
};
"""

with open(os.path.join(base_dir, "src", "components", "Navbar.tsx"), "w", encoding="utf-8") as f:
    f.write(navbar_tsx)

# 4. ProjectCard.tsx
project_card_tsx = """\"use client\";

import React from "react";
import Link from "next/link";
import Image from "next/image";
import { Project } from "@/lib/mockData";
import { Calendar, Shield, MoreHorizontal } from "lucide-react";

interface ProjectCardProps {
  project: Project;
  onOpenProcessingModal: (project: Project) => void;
}

export const ProjectCard: React.FC<ProjectCardProps> = ({
  project,
  onOpenProcessingModal,
}) => {
  const isReady = project.status === "ready";
  const isProcessing = project.status === "processing";
  const isComplete = project.status === "complete";
  const isDraft = project.status === "draft";

  const CardBody = (
    <div className="bg-white rounded-2xl border border-[#e2e8f0] overflow-hidden shadow-sm hover:shadow-md hover:border-[#cbd5e1] transition-all duration-200 flex flex-col justify-between">
      <div>
        {/* Card Thumbnail with Status Badge */}
        <div className="relative w-full h-44 bg-slate-100 overflow-hidden group/img">
          <Image
            src={project.thumbnail}
            alt={project.name}
            fill
            className="object-cover group-hover/img:scale-105 transition-transform duration-300"
          />

          {/* Status Badge Overlay */}
          <div className="absolute bottom-2.5 left-2.5">
            {isProcessing && (
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[11px] font-bold bg-[#fef3c7]/95 backdrop-blur text-[#b45309] border border-amber-300 shadow-sm">
                <span className="w-1.5 h-1.5 rounded-full bg-[#f59e0b] animate-ping" />
                Processing
              </span>
            )}
            {isReady && (
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[11px] font-bold bg-[#d1fae5]/95 backdrop-blur text-[#065f46] border border-emerald-300 shadow-sm">
                <span className="w-1.5 h-1.5 rounded-full bg-[#10b981]" />
                Ready
              </span>
            )}
            {isComplete && (
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[11px] font-bold bg-[#ccfbf1]/95 backdrop-blur text-[#115e59] border border-teal-300 shadow-sm">
                <span className="w-1.5 h-1.5 rounded-full bg-[#14b8a6]" />
                Complete
              </span>
            )}
            {isDraft && (
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[11px] font-bold bg-[#f1f5f9]/95 backdrop-blur text-[#475569] border border-slate-300 shadow-sm">
                <span className="w-1.5 h-1.5 rounded-full bg-[#94a3b8]" />
                Draft
              </span>
            )}
          </div>
        </div>

        {/* Card Text Content */}
        <div className="p-4 space-y-1">
          <h3 className="text-sm font-bold text-[#0f172a] group-hover:text-[#2563eb] transition-colors line-clamp-1">
            {project.name}
          </h3>
          <p className="text-xs text-[#64748b]">
            {project.floor} • {project.block} • {project.area}
          </p>
        </div>
      </div>

      {/* Card Footer */}
      <div className="px-4 py-3 border-t border-[#f1f5f9] flex items-center justify-between text-xs text-[#64748b]">
        <div className="flex items-center gap-1.5">
          <Calendar className="w-3.5 h-3.5 text-[#94a3b8]" />
          <span>{project.dateCaptured}</span>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1">
            <Shield className="w-3.5 h-3.5 text-[#94a3b8]" />
            <span>{project.scansCount} scans</span>
          </div>

          <button
            onClick={(e) => {
              e.preventDefault();
              e.stopPropagation();
            }}
            className="p-1 rounded text-[#94a3b8] hover:text-[#0f172a] hover:bg-slate-100 transition-colors"
          >
            <MoreHorizontal className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );

  if (isReady || isComplete) {
    return (
      <Link href={`/viewer/${project.id}`} className="group block cursor-pointer">
        {CardBody}
      </Link>
    );
  }

  return (
    <div
      onClick={() => isProcessing && onOpenProcessingModal(project)}
      className={`group block ${isProcessing ? "cursor-pointer" : ""}`}
    >
      {CardBody}
    </div>
  );
};
"""

with open(os.path.join(base_dir, "src", "components", "ProjectCard.tsx"), "w", encoding="utf-8") as f:
    f.write(project_card_tsx)

# 5. FloorPlanView.tsx (Interactive Floor Plan Tab)
floor_plan_tsx = """\"use client\";

import React, { useState } from "react";
import Link from "next/link";
import { MOCK_FLOOR_PLAN_SECTORS, FloorPlanSector } from "@/lib/mockData";
import { MapPin, Box, ArrowRight, Layers, Eye, CheckCircle2, Activity } from "lucide-react";

export const FloorPlanView: React.FC = () => {
  const [selectedSector, setSelectedSector] = useState<FloorPlanSector>(
    MOCK_FLOOR_PLAN_SECTORS[0]
  );
  const [hoveredSector, setHoveredSector] = useState<FloorPlanSector | null>(null);

  return (
    <div className="space-y-6">
      {/* Floor Plan Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold text-[#0f172a]">
            Interactive Spatial Floor Plan
          </h2>
          <p className="text-xs text-[#64748b]">
            Select any sector or room to view spatial telemetry and jump into the 3D model.
          </p>
        </div>

        <div className="flex items-center gap-2 text-xs font-semibold text-[#0f172a]">
          <span className="px-3 py-1.5 rounded-xl bg-white border border-[#e2e8f0] shadow-sm">
            Level 3 Architectural Plan (1:100 Scale)
          </span>
        </div>
      </div>

      {/* Main Floor Plan Interactive Canvas + Sector Details Drawer */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* 2D Architectural CAD Blueprint Viewport (8 cols) */}
        <div className="lg:col-span-8 bg-white rounded-2xl border border-[#e2e8f0] p-6 shadow-sm relative min-h-[440px] flex flex-col justify-between overflow-hidden">
          {/* Subtle CAD Grid Background */}
          <div className="absolute inset-0 bg-[linear-gradient(to_right,#e2e8f0_1px,transparent_1px),linear-gradient(to_bottom,#e2e8f0_1px,transparent_1px)] bg-[size:24px_24px] opacity-40 pointer-events-none" />

          {/* Interactive Sectors Canvas */}
          <div className="relative w-full h-[380px] border-2 border-dashed border-[#cbd5e1] rounded-xl bg-[#f8fbfe] overflow-hidden p-4">
            {/* Architectural Outer Wall Outlines */}
            <div className="absolute inset-4 border-2 border-[#94a3b8] rounded-lg pointer-events-none opacity-50" />

            {/* Clickable Sectors */}
            {MOCK_FLOOR_PLAN_SECTORS.map((sector) => {
              const isSelected = selectedSector.id === sector.id;
              const isHovered = hoveredSector?.id === sector.id;

              return (
                <div
                  key={sector.id}
                  onClick={() => setSelectedSector(sector)}
                  onMouseEnter={() => setHoveredSector(sector)}
                  onMouseLeave={() => setHoveredSector(null)}
                  style={{
                    left: `${sector.xPercent}%`,
                    top: `${sector.yPercent}%`,
                    width: `${sector.widthPercent}%`,
                    height: `${sector.heightPercent}%`,
                  }}
                  className={`absolute rounded-xl border-2 transition-all duration-200 cursor-pointer p-3 flex flex-col justify-between ${
                    isSelected
                      ? "bg-[#2563eb]/15 border-[#2563eb] shadow-lg shadow-blue-500/10 scale-[1.02] z-10"
                      : isHovered
                      ? "bg-[#2563eb]/10 border-[#3b82f6] z-10"
                      : "bg-white/80 border-[#cbd5e1] hover:border-[#94a3b8]"
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="font-mono text-[10px] font-bold text-[#2563eb]">
                        {sector.sectorCode}
                      </div>
                      <div className="text-xs font-bold text-[#0f172a] line-clamp-1">
                        {sector.name}
                      </div>
                    </div>

                    <span
                      className="w-2.5 h-2.5 rounded-full"
                      style={{ backgroundColor: sector.statusColor }}
                    />
                  </div>

                  <div className="flex items-center justify-between text-[10px] text-[#64748b] font-medium">
                    <span>{sector.area}</span>
                    <span className="flex items-center gap-0.5 text-[#2563eb] font-bold">
                      <MapPin className="w-2.5 h-2.5" />
                      3D Splat
                    </span>
                  </div>
                </div>
              );
            })}
          </div>

          <div className="text-[11px] text-[#64748b] pt-2 flex items-center justify-between">
            <span>Click any highlighted zone on the floor plan to inspect telemetry</span>
            <span className="font-mono text-[#2563eb] font-semibold">ARCore IMU Anchors: Synced</span>
          </div>
        </div>

        {/* Selected Sector Inspector & 3D Launcher (4 cols) */}
        <div className="lg:col-span-4 bg-white rounded-2xl border border-[#e2e8f0] p-6 shadow-sm flex flex-col justify-between space-y-4">
          <div className="space-y-4">
            <div className="flex items-center justify-between border-b border-[#f1f5f9] pb-3">
              <span className="text-[11px] font-bold text-[#2563eb] font-mono px-2 py-0.5 rounded bg-blue-50 border border-blue-200">
                {selectedSector.sectorCode}
              </span>

              <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
                <CheckCircle2 className="w-3.5 h-3.5" />
                {selectedSector.status === "ready" ? "Ready for 3D" : selectedSector.status}
              </span>
            </div>

            <div>
              <h3 className="text-base font-bold text-[#0f172a]">
                {selectedSector.name}
              </h3>
              <p className="text-xs text-[#64748b] mt-0.5">
                {selectedSector.level} • {selectedSector.area}
              </p>
            </div>

            <p className="text-xs text-[#64748b] leading-relaxed">
              {selectedSector.description}
            </p>

            <div className="grid grid-cols-2 gap-2 pt-2 text-xs font-mono">
              <div className="p-2.5 rounded-xl bg-[#f8fafc] border border-[#e2e8f0]">
                <span className="text-[10px] text-[#64748b] font-sans block">ACCURACY</span>
                <span className="font-bold text-[#0f172a]">{selectedSector.accuracy}</span>
              </div>
              <div className="p-2.5 rounded-xl bg-[#f8fafc] border border-[#e2e8f0]">
                <span className="text-[10px] text-[#64748b] font-sans block">SCANS CAPTURED</span>
                <span className="font-bold text-[#2563eb]">{selectedSector.scansCount} Sets</span>
              </div>
            </div>
          </div>

          {/* Launch 3D Gaussian Splat Button */}
          <Link
            href={`/viewer/${selectedSector.targetProjectId}`}
            className="w-full py-3 px-4 rounded-xl bg-[#2563eb] hover:bg-[#1d4ed8] active:bg-[#1e40af] text-white font-bold text-xs shadow-md shadow-blue-500/15 transition-all flex items-center justify-center gap-2 cursor-pointer"
          >
            <Box className="w-4 h-4" />
            <span>Launch 3D Gaussian Splat</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </div>
    </div>
  );
};
"""

with open(os.path.join(base_dir, "src", "components", "FloorPlanView.tsx"), "w", encoding="utf-8") as f:
    f.write(floor_plan_tsx)

# 6. dashboard/page.tsx
dashboard_page_tsx = """\"use client\";

import React, { useState } from "react";
import { Sidebar } from "@/components/Sidebar";
import { Navbar } from "@/components/Navbar";
import { ProjectCard } from "@/components/ProjectCard";
import { FloorPlanView } from "@/components/FloorPlanView";
import { JobStatusModal } from "@/components/JobStatusModal";
import { NewCaptureModal } from "@/components/NewCaptureModal";
import { MOCK_PROJECTS, Project } from "@/lib/mockData";
import {
  Plus,
  LayoutGrid,
  List,
  Calendar,
  ChevronDown,
} from "lucide-react";

export default function DashboardPage() {
  const [projects] = useState<Project[]>(MOCK_PROJECTS);
  const [currentTab, setCurrentTab] = useState<
    "dashboard" | "floorplan" | "projects" | "scans" | "reports" | "team" | "settings"
  >("dashboard");
  const [filter, setFilter] = useState<"all" | "ready" | "processing" | "draft" | "archived">("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [viewMode, setViewMode] = useState<"grid" | "list">("grid");
  const [isJobModalOpen, setIsJobModalOpen] = useState(false);
  const [selectedJobProject, setSelectedJobProject] = useState<Project | null>(null);
  const [isNewCaptureModalOpen, setIsNewCaptureModalOpen] = useState(false);

  const handleOpenProcessing = (project: Project) => {
    setSelectedJobProject(project);
    setIsJobModalOpen(true);
  };

  const handleOpenProjectFromRecent = (projectId: string) => {
    const proj = projects.find((p) => p.id === projectId);
    if (proj?.status === "processing") {
      handleOpenProcessing(proj);
    }
  };

  const filteredProjects = projects.filter((p) => {
    const matchesFilter = filter === "all" || p.status === filter;
    const matchesSearch =
      p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.block.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.floor.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  return (
    <div className="min-h-screen w-full flex bg-[#f6fafd] text-[#0f172a] relative">
      {/* High-Definition Isometric CAD Blueprint Grid Background (Image 2 style) */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#e0edf8_1px,transparent_1px),linear-gradient(to_bottom,#e0edf8_1px,transparent_1px)] bg-[size:32px_32px] opacity-45 pointer-events-none" />

      {/* Left Sidebar Navigation */}
      <Sidebar
        currentTab={currentTab}
        onSelectTab={setCurrentTab}
        onOpenProject={handleOpenProjectFromRecent}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 z-10">
        {/* Top Navbar */}
        <Navbar
          onOpenNewCapture={() => setIsNewCaptureModalOpen(true)}
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
        />

        {/* Dashboard Body */}
        <main className="flex-1 p-6 md:p-8 space-y-6 max-w-7xl w-full mx-auto">
          {currentTab === "floorplan" ? (
            <FloorPlanView />
          ) : (
            <>
              {/* Header Title & Actions Row */}
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div>
                  <h1 className="text-2xl font-extrabold text-[#0f172a] tracking-tight">
                    All Projects
                  </h1>
                  <p className="text-xs text-[#64748b] mt-0.5">
                    Manage and view your construction sites and scans.
                  </p>
                </div>

                <div className="flex items-center gap-2">
                  {/* Grid / List View Toggle */}
                  <div className="flex items-center rounded-xl bg-white border border-[#e2e8f0] p-1 shadow-sm">
                    <button
                      onClick={() => setViewMode("grid")}
                      className={`p-1.5 rounded-lg transition-colors cursor-pointer ${
                        viewMode === "grid"
                          ? "bg-slate-100 text-[#2563eb]"
                          : "text-[#94a3b8] hover:text-[#0f172a]"
                      }`}
                      title="Grid View"
                    >
                      <LayoutGrid className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => setViewMode("list")}
                      className={`p-1.5 rounded-lg transition-colors cursor-pointer ${
                        viewMode === "list"
                          ? "bg-slate-100 text-[#2563eb]"
                          : "text-[#94a3b8] hover:text-[#0f172a]"
                      }`}
                      title="List View"
                    >
                      <List className="w-4 h-4" />
                    </button>
                  </div>

                  {/* + New Capture Button with Tooltip Subtitle */}
                  <div className="relative group">
                    <button
                      onClick={() => setIsNewCaptureModalOpen(true)}
                      className="px-4 py-2 rounded-xl bg-[#2563eb] hover:bg-[#1d4ed8] text-white text-xs font-bold shadow-sm transition-all flex items-center gap-1.5 cursor-pointer"
                    >
                      <Plus className="w-4 h-4" />
                      <span>New Capture</span>
                    </button>
                    <div className="absolute right-0 top-full mt-1 hidden group-hover:block z-20 px-2.5 py-1 bg-slate-900 text-white text-[10px] rounded-lg whitespace-nowrap shadow-lg">
                      Initiate from BuildScan mobile app
                    </div>
                  </div>
                </div>
              </div>

              {/* Filter Pills Row & Date Range Picker */}
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pt-1">
                {/* Filter Pills */}
                <div className="flex items-center gap-2 overflow-x-auto pb-1 sm:pb-0">
                  <button
                    onClick={() => setFilter("all")}
                    className={`px-3.5 py-1.5 rounded-full text-xs font-bold transition-all cursor-pointer ${
                      filter === "all"
                        ? "bg-[#2563eb] text-white shadow-sm"
                        : "bg-white text-[#64748b] border border-[#e2e8f0] hover:text-[#0f172a]"
                    }`}
                  >
                    All
                  </button>
                  <button
                    onClick={() => setFilter("ready")}
                    className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-full text-xs font-bold transition-all cursor-pointer ${
                      filter === "ready"
                        ? "bg-[#10b981] text-white shadow-sm"
                        : "bg-white text-[#64748b] border border-[#e2e8f0] hover:text-[#0f172a]"
                    }`}
                  >
                    <span className="w-1.5 h-1.5 rounded-full bg-[#10b981]" />
                    <span>Ready</span>
                  </button>
                  <button
                    onClick={() => setFilter("processing")}
                    className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-full text-xs font-bold transition-all cursor-pointer ${
                      filter === "processing"
                        ? "bg-[#f59e0b] text-white shadow-sm"
                        : "bg-white text-[#64748b] border border-[#e2e8f0] hover:text-[#0f172a]"
                    }`}
                  >
                    <span className="w-1.5 h-1.5 rounded-full bg-[#f59e0b]" />
                    <span>Processing</span>
                  </button>
                  <button
                    onClick={() => setFilter("draft")}
                    className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-full text-xs font-bold transition-all cursor-pointer ${
                      filter === "draft"
                        ? "bg-[#64748b] text-white shadow-sm"
                        : "bg-white text-[#64748b] border border-[#e2e8f0] hover:text-[#0f172a]"
                    }`}
                  >
                    <span className="w-1.5 h-1.5 rounded-full bg-[#94a3b8]" />
                    <span>Draft</span>
                  </button>
                  <button
                    onClick={() => setFilter("archived")}
                    className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-full text-xs font-bold transition-all cursor-pointer ${
                      filter === "archived"
                        ? "bg-slate-700 text-white shadow-sm"
                        : "bg-white text-[#64748b] border border-[#e2e8f0] hover:text-[#0f172a]"
                    }`}
                  >
                    <span className="w-1.5 h-1.5 rounded-full bg-slate-400" />
                    <span>Archived</span>
                  </button>
                </div>

                {/* Date Range Selector */}
                <button className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-white border border-[#e2e8f0] text-xs font-semibold text-[#0f172a] shadow-sm hover:bg-slate-50 cursor-pointer">
                  <Calendar className="w-3.5 h-3.5 text-[#64748b]" />
                  <span>Apr 1, 2025 - Apr 30, 2025</span>
                  <ChevronDown className="w-3.5 h-3.5 text-[#64748b]" />
                </button>
              </div>

              {/* Project Cards Grid (3 columns matching Image 1) */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 pt-2">
                {filteredProjects.map((project) => (
                  <ProjectCard
                    key={project.id}
                    project={project}
                    onOpenProcessingModal={handleOpenProcessing}
                  />
                ))}
              </div>
            </>
          )}
        </main>
      </div>

      {/* Screen 3: Active Job Status Modal */}
      <JobStatusModal
        isOpen={isJobModalOpen}
        onClose={() => setIsJobModalOpen(false)}
        project={selectedJobProject}
      />

      {/* Mobile Sync / Direct Upload Modal */}
      <NewCaptureModal
        isOpen={isNewCaptureModalOpen}
        onClose={() => setIsNewCaptureModalOpen(false)}
      />
    </div>
  );
}
"""

with open(os.path.join(base_dir, "src", "app", "dashboard", "page.tsx"), "w", encoding="utf-8") as f:
    f.write(dashboard_page_tsx)

print("Successfully wrote mockData.ts, Sidebar.tsx, Navbar.tsx, ProjectCard.tsx, FloorPlanView.tsx, and dashboard/page.tsx.")
