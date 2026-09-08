import os

base_dir = r"d:\FYP\prototype\web-ui"

# 1. page.tsx
page_tsx = """\"use client\";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";
import { Mail, Lock, Eye, EyeOff, ShieldCheck } from "lucide-react";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("pm.jenkins@buildscan3d.ai");
  const [password, setPassword] = useState("password123");
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleSignIn = (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setTimeout(() => {
      router.push("/dashboard");
    }, 400);
  };

  return (
    <div className="min-h-screen w-full flex flex-col md:flex-row bg-white">
      {/* LEFT COLUMN: Architectural 3D Graphic Panel */}
      <div className="relative w-full md:w-[46%] lg:w-[44%] bg-[#edf5fc] min-h-[340px] md:min-h-screen p-8 md:p-12 flex flex-col justify-between overflow-hidden select-none border-r border-[#e2edf8]">
        {/* Top Text */}
        <div className="relative z-10 space-y-1">
          <h2 className="text-sm md:text-base font-semibold text-[#1e293b] tracking-tight">
            Real sites. 3D truth.
          </h2>
          <p className="text-xs md:text-sm text-[#64748b]">
            Verify. Measure. Build better.
          </p>
        </div>

        {/* Center Blueprint / Point Cloud Illustration */}
        <div className="relative my-auto py-6 flex items-center justify-center">
          <div className="relative w-full max-w-[420px] aspect-[4/3] drop-shadow-sm">
            <Image
              src="/images/login-left-panel.png"
              alt="3D Spatial BIM Scan"
              fill
              className="object-contain"
              priority
            />
          </div>
        </div>

        {/* Bottom Text */}
        <div className="relative z-10">
          <p className="text-[11px] md:text-xs text-[#64748b] font-normal">
            Powered by spatial data. Built for construction.
          </p>
        </div>
      </div>

      {/* RIGHT COLUMN: Clean Enterprise Authentication Form */}
      <div className="flex-1 flex flex-col items-center justify-center p-6 sm:p-10 md:p-16 bg-white">
        <div className="w-full max-w-[380px] flex flex-col items-center">
          {/* Logo & Brand Name */}
          <div className="flex flex-col items-center text-center mb-8">
            <div className="flex items-center gap-2.5 mb-2">
              {/* Isometric 3D Cube Icon */}
              <svg
                className="w-9 h-9 text-[#2563eb]"
                viewBox="0 0 48 48"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M24 4L42 14.3923V35.1769L24 45.5692L6 35.1769V14.3923L24 4Z"
                  stroke="currentColor"
                  strokeWidth="3.2"
                  strokeLinejoin="round"
                />
                <path
                  d="M24 4V24.5M24 24.5L42 14.5M24 24.5L6 14.5M24 24.5V45.5"
                  stroke="currentColor"
                  strokeWidth="2.8"
                  strokeLinecap="round"
                />
                <circle cx="24" cy="24.5" r="3" fill="currentColor" />
                <circle cx="15" cy="19.5" r="1.5" fill="currentColor" />
                <circle cx="33" cy="19.5" r="1.5" fill="currentColor" />
                <circle cx="24" cy="35" r="1.5" fill="currentColor" />
              </svg>

              <h1 className="text-2xl font-bold tracking-tight text-[#0f172a]">
                BuildScan <span className="text-[#2563eb]">3D</span>
              </h1>
            </div>
            <p className="text-xs text-[#64748b]">
              Construction Spatial Intelligence Platform
            </p>
          </div>

          {/* Form */}
          <form onSubmit={handleSignIn} className="w-full space-y-4">
            {/* Email Field */}
            <div className="relative flex items-center border border-[#e2e8f0] rounded-xl px-3.5 py-3 bg-white focus-within:border-[#2563eb] focus-within:ring-2 focus-within:ring-[#2563eb]/10 transition-all shadow-[0_1px_2px_rgba(0,0,0,0.02)]">
              <Mail className="w-4 h-4 text-[#64748b] mr-3 shrink-0" />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@company.com"
                className="w-full text-xs sm:text-sm text-[#0f172a] placeholder-[#94a3b8] bg-transparent focus:outline-none"
                required
              />
            </div>

            {/* Password Field */}
            <div className="relative flex items-center border border-[#e2e8f0] rounded-xl px-3.5 py-3 bg-white focus-within:border-[#2563eb] focus-within:ring-2 focus-within:ring-[#2563eb]/10 transition-all shadow-[0_1px_2px_rgba(0,0,0,0.02)]">
              <Lock className="w-4 h-4 text-[#64748b] mr-3 shrink-0" />
              <input
                type={showPassword ? "text" : "password"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••••••"
                className="w-full text-xs sm:text-sm text-[#0f172a] placeholder-[#94a3b8] bg-transparent focus:outline-none font-mono"
                required
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="text-[#64748b] hover:text-[#0f172a] ml-2 shrink-0 transition-colors"
                title={showPassword ? "Hide password" : "Show password"}
              >
                {showPassword ? (
                  <EyeOff className="w-4 h-4" />
                ) : (
                  <Eye className="w-4 h-4" />
                )}
              </button>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-3 px-4 rounded-xl bg-[#2563eb] hover:bg-[#1d4ed8] active:bg-[#1e40af] text-white font-medium text-xs sm:text-sm shadow-sm transition-all flex items-center justify-center gap-2 cursor-pointer mt-5"
            >
              {isLoading ? (
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                "Sign In"
              )}
            </button>

            {/* Forgot password link */}
            <div className="text-center pt-1">
              <button
                type="button"
                onClick={() => alert("Password reset link sent to demo email")}
                className="text-xs text-[#2563eb] hover:text-[#1d4ed8] hover:underline font-medium transition-colors"
              >
                Forgot password?
              </button>
            </div>
          </form>

          {/* Security & Compliance Badges */}
          <div className="w-full flex items-center justify-center gap-3 mt-12 pt-4">
            <div className="flex-1 flex items-center justify-center gap-2 py-2 px-3 rounded-xl border border-[#e2e8f0] bg-white text-[11px] font-medium text-[#64748b] shadow-[0_1px_2px_rgba(0,0,0,0.02)]">
              <Lock className="w-3.5 h-3.5 text-[#64748b]" />
              <span>256-bit encrypted</span>
            </div>
            <div className="flex-1 flex items-center justify-center gap-2 py-2 px-3 rounded-xl border border-[#e2e8f0] bg-white text-[11px] font-medium text-[#64748b] shadow-[0_1px_2px_rgba(0,0,0,0.02)]">
              <ShieldCheck className="w-3.5 h-3.5 text-[#64748b]" />
              <span>SOC 2 compliant</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
"""

# 2. dashboard/page.tsx
dashboard_tsx = """\"use client\";

import React, { useState } from "react";
import { Navbar } from "@/components/Navbar";
import { ProjectCard } from "@/components/ProjectCard";
import { JobStatusModal } from "@/components/JobStatusModal";
import { NewCaptureModal } from "@/components/NewCaptureModal";
import { MOCK_PROJECTS, Project } from "@/lib/mockData";
import {
  Activity,
  CheckCircle2,
  Plus,
  Ruler,
  Search,
  Database,
} from "lucide-react";

export default function DashboardPage() {
  const [projects] = useState<Project[]>(MOCK_PROJECTS);
  const [filter, setFilter] = useState<"all" | "ready" | "processing" | "draft">("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [isJobModalOpen, setIsJobModalOpen] = useState(false);
  const [selectedJobProject, setSelectedJobProject] = useState<Project | null>(null);
  const [isNewCaptureModalOpen, setIsNewCaptureModalOpen] = useState(false);

  const handleOpenProcessing = (project: Project) => {
    setSelectedJobProject(project);
    setIsJobModalOpen(true);
  };

  const filteredProjects = projects.filter((p) => {
    const matchesFilter = filter === "all" || p.status === filter;
    const matchesSearch =
      p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.location.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.category.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  const readyCount = projects.filter((p) => p.status === "ready").length;
  const processingCount = projects.filter((p) => p.status === "processing").length;
  const draftCount = projects.filter((p) => p.status === "draft").length;

  return (
    <div className="min-h-screen w-full bg-[#f8fafc] text-[#0f172a] flex flex-col">
      {/* Top Navigation */}
      <Navbar
        onOpenJobStatus={() => {
          setSelectedJobProject(projects.find((p) => p.status === "processing") || null);
          setIsJobModalOpen(true);
        }}
        activeProcessingCount={processingCount}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Hero Banner & KPI Metric Cards */}
        <div className="space-y-6">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-2xl font-extrabold text-[#0f172a] tracking-tight">
                  Project Workspace
                </h1>
                <span className="text-xs font-mono font-bold px-2.5 py-0.5 rounded-full bg-blue-50 text-[#2563eb] border border-blue-200">
                  Site: Metro Tower B
                </span>
              </div>
              <p className="text-xs text-[#64748b] mt-1">
                Field telemetry fused with 3D Gaussian Splatting for millimeter-grade MEP validation
              </p>
            </div>

            <button
              onClick={() => setIsNewCaptureModalOpen(true)}
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-[#2563eb] hover:bg-[#1d4ed8] text-white text-xs font-bold shadow-sm transition-all cursor-pointer"
            >
              <Plus className="w-4 h-4" />
              <span>Initiate New Capture</span>
            </button>
          </div>

          {/* Metric KPI Row */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            {/* KPI 1 */}
            <div className="p-4 rounded-2xl bg-white border border-[#e2e8f0] shadow-sm space-y-1">
              <div className="flex items-center justify-between text-[#64748b]">
                <span className="text-xs font-semibold">Total Site Scans</span>
                <Database className="w-4 h-4 text-[#2563eb]" />
              </div>
              <div className="text-2xl font-bold text-[#0f172a] font-mono">12</div>
              <div className="text-[11px] text-[#64748b] flex items-center gap-1">
                <span className="text-emerald-600 font-bold">+3 scans</span> this week
              </div>
            </div>

            {/* KPI 2 */}
            <div
              onClick={() => {
                setSelectedJobProject(projects.find((p) => p.status === "processing") || null);
                setIsJobModalOpen(true);
              }}
              className="p-4 rounded-2xl bg-gradient-to-b from-amber-50/50 to-white border border-amber-200 shadow-sm space-y-1 cursor-pointer hover:border-amber-300 transition-colors"
            >
              <div className="flex items-center justify-between text-amber-700">
                <span className="text-xs font-semibold">Active Cloud Jobs</span>
                <Activity className="w-4 h-4 text-amber-600 animate-spin" />
              </div>
              <div className="text-2xl font-bold text-[#0f172a] font-mono flex items-center gap-2">
                <span>1</span>
                <span className="text-xs font-sans text-amber-700 font-bold">Training (68%)</span>
              </div>
              <div className="text-[11px] text-amber-700 flex items-center gap-1">
                Click to inspect live pipeline queue →
              </div>
            </div>

            {/* KPI 3 */}
            <div className="p-4 rounded-2xl bg-white border border-[#e2e8f0] shadow-sm space-y-1">
              <div className="flex items-center justify-between text-[#64748b]">
                <span className="text-xs font-semibold">Ready for Inspection</span>
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              </div>
              <div className="text-2xl font-bold text-[#0f172a] font-mono">{readyCount}</div>
              <div className="text-[11px] text-emerald-700 flex items-center gap-1 font-mono font-medium">
                1:1 Metric Ground Truth Active
              </div>
            </div>

            {/* KPI 4 */}
            <div className="p-4 rounded-2xl bg-white border border-[#e2e8f0] shadow-sm space-y-1">
              <div className="flex items-center justify-between text-[#64748b]">
                <span className="text-xs font-semibold">Avg Metric Accuracy</span>
                <Ruler className="w-4 h-4 text-[#2563eb]" />
              </div>
              <div className="text-2xl font-bold text-[#2563eb] font-mono">±1.2 mm</div>
              <div className="text-[11px] text-[#64748b]">
                Calibrated against ARCore 120Hz VIO
              </div>
            </div>
          </div>
        </div>

        {/* Filter and Search Bar */}
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4 pt-4 border-t border-[#e2e8f0]">
          {/* Filter Tabs */}
          <div className="flex items-center gap-1.5 p-1 rounded-xl bg-slate-100 border border-slate-200 overflow-x-auto">
            <button
              onClick={() => setFilter("all")}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all whitespace-nowrap ${
                filter === "all"
                  ? "bg-white text-[#2563eb] shadow-sm font-bold"
                  : "text-[#64748b] hover:text-[#0f172a]"
              }`}
            >
              All Scans ({projects.length})
            </button>
            <button
              onClick={() => setFilter("ready")}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all whitespace-nowrap ${
                filter === "ready"
                  ? "bg-white text-emerald-700 shadow-sm font-bold"
                  : "text-[#64748b] hover:text-[#0f172a]"
              }`}
            >
              Ready for Inspection ({readyCount})
            </button>
            <button
              onClick={() => setFilter("processing")}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all whitespace-nowrap ${
                filter === "processing"
                  ? "bg-white text-amber-700 shadow-sm font-bold"
                  : "text-[#64748b] hover:text-[#0f172a]"
              }`}
            >
              Processing ({processingCount})
            </button>
            <button
              onClick={() => setFilter("draft")}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all whitespace-nowrap ${
                filter === "draft"
                  ? "bg-white text-slate-700 shadow-sm font-bold"
                  : "text-[#64748b] hover:text-[#0f172a]"
              }`}
            >
              Drafts ({draftCount})
            </button>
          </div>

          {/* Search box */}
          <div className="relative w-full sm:w-72">
            <Search className="w-3.5 h-3.5 text-[#94a3b8] absolute left-3 top-2.5 pointer-events-none" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by sector or room name..."
              className="w-full pl-8 pr-4 py-2 bg-white border border-[#e2e8f0] rounded-xl text-xs text-[#0f172a] placeholder-[#94a3b8] focus:outline-none focus:border-[#2563eb] transition-all shadow-sm"
            />
          </div>
        </div>

        {/* Project Cards Grid (Screen 2 Core) */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredProjects.map((project) => (
            <ProjectCard
              key={project.id}
              project={project}
              onOpenProcessingModal={handleOpenProcessing}
            />
          ))}
        </div>
      </main>

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

# 3. ExportModal.tsx
export_modal_tsx = """\"use client\";

import React, { useState } from "react";
import {
  X,
  Download,
  FileSpreadsheet,
  Box,
  Layers,
} from "lucide-react";

interface ExportModalProps {
  isOpen: boolean;
  onClose: () => void;
  projectName: string;
  measurementsCount: number;
}

export const ExportModal: React.FC<ExportModalProps> = ({
  isOpen,
  onClose,
  projectName,
  measurementsCount,
}) => {
  const [downloadedFormat, setDownloadedFormat] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleDownload = (format: string, filename: string) => {
    setDownloadedFormat(format);
    setTimeout(() => {
      setDownloadedFormat(null);
    }, 2500);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm animate-in fade-in duration-200">
      <div
        className="relative w-full max-w-md bg-white border border-[#e2e8f0] rounded-2xl shadow-2xl overflow-hidden text-[#0f172a]"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between px-5 py-4 border-b border-[#e2e8f0] bg-[#f8fafc]">
          <div className="flex items-center gap-2.5">
            <Download className="w-5 h-5 text-[#2563eb]" />
            <h3 className="text-sm font-bold text-[#0f172a]">
              Export Site Intelligence & BIM
            </h3>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-[#64748b] hover:text-[#0f172a] hover:bg-slate-100"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="p-5 space-y-3 bg-white">
          <p className="text-xs text-[#64748b]">
            Export metric dimensions, classified point cloud masks, and 3D geometry
            for <strong>{projectName}</strong>:
          </p>

          {/* Option 1: CSV Report */}
          <div className="p-3 rounded-xl bg-[#f8fafc] border border-[#e2e8f0] hover:border-[#cbd5e1] flex items-center justify-between gap-3 transition-colors">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center shrink-0 border border-emerald-200">
                <FileSpreadsheet className="w-5 h-5" />
              </div>
              <div>
                <div className="text-xs font-bold text-[#0f172a]">
                  Metric Measurements Schedule (.csv)
                </div>
                <div className="text-[11px] text-[#64748b]">
                  {measurementsCount} Active Measurements + Tolerances
                </div>
              </div>
            </div>
            <button
              onClick={() =>
                handleDownload("csv", `${projectName}_measurements.csv`)
              }
              className="px-3 py-1.5 rounded-xl bg-[#2563eb] hover:bg-[#1d4ed8] text-white text-xs font-bold shadow-sm"
            >
              {downloadedFormat === "csv" ? "Downloaded!" : "Export"}
            </button>
          </div>

          {/* Option 2: IFC / BIM Model */}
          <div className="p-3 rounded-xl bg-[#f8fafc] border border-[#e2e8f0] hover:border-[#cbd5e1] flex items-center justify-between gap-3 transition-colors">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-blue-50 text-[#2563eb] flex items-center justify-center shrink-0 border border-blue-200">
                <Box className="w-5 h-5" />
              </div>
              <div>
                <div className="text-xs font-bold text-[#0f172a]">
                  BIM Geometry (.ifc / .obj)
                </div>
                <div className="text-[11px] text-[#64748b]">
                  Classified MEP Objects (Pipes, Ducts, Trays)
                </div>
              </div>
            </div>
            <button
              onClick={() => handleDownload("ifc", `${projectName}_bim.ifc`)}
              className="px-3 py-1.5 rounded-xl bg-[#2563eb] hover:bg-[#1d4ed8] text-white text-xs font-bold shadow-sm"
            >
              {downloadedFormat === "ifc" ? "Downloaded!" : "Export"}
            </button>
          </div>

          {/* Option 3: WebGPU .ksplat */}
          <div className="p-3 rounded-xl bg-[#f8fafc] border border-[#e2e8f0] hover:border-[#cbd5e1] flex items-center justify-between gap-3 transition-colors">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center shrink-0 border border-purple-200">
                <Layers className="w-5 h-5" />
              </div>
              <div>
                <div className="text-xs font-bold text-[#0f172a]">
                  3D Gaussian Splat (.ksplat)
                </div>
                <div className="text-[11px] text-[#64748b]">
                  Compressed WebGPU Model (1.2M Gaussians)
                </div>
              </div>
            </div>
            <button
              onClick={() => handleDownload("ksplat", `${projectName}.ksplat`)}
              className="px-3 py-1.5 rounded-xl bg-[#2563eb] hover:bg-[#1d4ed8] text-white text-xs font-bold shadow-sm"
            >
              {downloadedFormat === "ksplat" ? "Downloaded!" : "Export"}
            </button>
          </div>
        </div>

        <div className="px-5 py-3 border-t border-[#e2e8f0] bg-[#f8fafc] flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-xs font-semibold text-[#0f172a]"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
"""

# 4. ViewerHUD.tsx
viewer_hud_tsx = """\"use client\";

import React, { useState } from "react";
import Link from "next/link";
import { SemanticLayersState } from "./SceneBuilder";
import { MeasurementRecord } from "./MeasurementTool";
import {
  ArrowLeft,
  Ruler,
  Eye,
  EyeOff,
  Sparkles,
  Download,
  Trash2,
  Grid,
  ChevronRight,
  ChevronLeft,
} from "lucide-react";

interface ViewerHUDProps {
  projectName: string;
  location: string;
  semanticLayers: SemanticLayersState;
  onToggleLayer: (layer: keyof SemanticLayersState) => void;
  isMeasureMode: boolean;
  onToggleMeasureMode: () => void;
  measurements: MeasurementRecord[];
  onDeleteMeasurement: (id: string) => void;
  onClearMeasurements: () => void;
  activePresetView: "perspective" | "top" | "front" | "side";
  onSelectPresetView: (view: "perspective" | "top" | "front" | "side") => void;
  wireframeMode: boolean;
  onToggleWireframe: () => void;
  onOpenExportModal: () => void;
}

export const ViewerHUD: React.FC<ViewerHUDProps> = ({
  projectName,
  location,
  semanticLayers,
  onToggleLayer,
  isMeasureMode,
  onToggleMeasureMode,
  measurements,
  onDeleteMeasurement,
  onClearMeasurements,
  activePresetView,
  onSelectPresetView,
  wireframeMode,
  onToggleWireframe,
  onOpenExportModal,
}) => {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  return (
    <>
      {/* Top Navigation Bar */}
      <div className="absolute top-0 left-0 right-0 z-30 flex items-center justify-between p-4 pointer-events-none">
        {/* Left: Back & Project Title */}
        <div className="flex items-center gap-3 pointer-events-auto bg-white/95 backdrop-blur-md border border-[#e2e8f0] p-2 pl-3 pr-4 rounded-2xl shadow-md text-[#0f172a]">
          <Link
            href="/dashboard"
            className="p-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-[#0f172a] transition-colors"
            title="Back to Dashboard"
          >
            <ArrowLeft className="w-4 h-4" />
          </Link>

          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-sm font-bold text-[#0f172a]">{projectName}</h1>
              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
                1:1 Metric Model
              </span>
            </div>
            <p className="text-[11px] text-[#64748b]">{location}</p>
          </div>
        </div>

        {/* Center: Metric Accuracy Badges */}
        <div className="hidden md:flex items-center gap-2 pointer-events-auto bg-white/95 backdrop-blur-md border border-[#e2e8f0] px-3.5 py-2 rounded-2xl text-xs font-mono shadow-md text-[#0f172a]">
          <div className="flex items-center gap-1.5 text-[#2563eb] font-semibold">
            <span className="w-2 h-2 rounded-full bg-[#2563eb] animate-pulse" />
            <span>ARCore 120Hz VIO</span>
          </div>
          <span className="text-slate-300">|</span>
          <div className="text-emerald-700 font-semibold">Ground Truth: ±1.2mm</div>
          <span className="text-slate-300">|</span>
          <div className="text-purple-700 font-semibold">1.24M Gaussians (WebGPU)</div>
        </div>

        {/* Right: Export & Toggle Sidebar */}
        <div className="flex items-center gap-2 pointer-events-auto">
          <button
            onClick={onOpenExportModal}
            className="flex items-center gap-2 px-3.5 py-2 rounded-2xl bg-[#2563eb] hover:bg-[#1d4ed8] text-white text-xs font-bold shadow-md shadow-blue-500/10 transition-all cursor-pointer"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export BIM / Data</span>
          </button>

          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2.5 rounded-2xl bg-white/95 backdrop-blur-md border border-[#e2e8f0] text-[#64748b] hover:text-[#0f172a] shadow-md"
            title="Toggle Inspector Sidebar"
          >
            {sidebarOpen ? (
              <ChevronRight className="w-4 h-4" />
            ) : (
              <ChevronLeft className="w-4 h-4" />
            )}
          </button>
        </div>
      </div>

      {/* Left Floating Toolbar: Measurement & View Presets */}
      <div className="absolute left-4 top-24 z-30 flex flex-col gap-2 pointer-events-auto">
        {/* Measurement Mode Button */}
        <div className="p-1.5 rounded-2xl bg-white/95 backdrop-blur-md border border-[#e2e8f0] shadow-md flex flex-col gap-1.5">
          <button
            onClick={onToggleMeasureMode}
            className={`flex items-center gap-2 px-3.5 py-2.5 rounded-xl text-xs font-bold transition-all cursor-pointer ${
              isMeasureMode
                ? "bg-[#2563eb] text-white shadow-sm"
                : "bg-slate-50 text-[#0f172a] hover:bg-slate-100 border border-slate-200"
            }`}
            title="Measure real-world metric distance between points"
          >
            <Ruler className="w-4 h-4" />
            <span>{isMeasureMode ? "Measuring Active" : "Measure Distance"}</span>
          </button>
        </div>

        {/* View Presets Palette */}
        <div className="p-2 rounded-2xl bg-white/95 backdrop-blur-md border border-[#e2e8f0] shadow-md flex flex-col gap-1 text-xs">
          <span className="text-[10px] font-bold text-[#64748b] px-2 py-1 uppercase tracking-wider">
            View Angle
          </span>
          <button
            onClick={() => onSelectPresetView("perspective")}
            className={`px-3 py-1.5 rounded-xl text-left font-semibold transition-colors ${
              activePresetView === "perspective"
                ? "bg-blue-50 text-[#2563eb]"
                : "text-[#64748b] hover:text-[#0f172a] hover:bg-slate-50"
            }`}
          >
            Perspective 3D
          </button>
          <button
            onClick={() => onSelectPresetView("top")}
            className={`px-3 py-1.5 rounded-xl text-left font-semibold transition-colors ${
              activePresetView === "top"
                ? "bg-blue-50 text-[#2563eb]"
                : "text-[#64748b] hover:text-[#0f172a] hover:bg-slate-50"
            }`}
          >
            Top (Plan View)
          </button>
          <button
            onClick={() => onSelectPresetView("front")}
            className={`px-3 py-1.5 rounded-xl text-left font-semibold transition-colors ${
              activePresetView === "front"
                ? "bg-blue-50 text-[#2563eb]"
                : "text-[#64748b] hover:text-[#0f172a] hover:bg-slate-50"
            }`}
          >
            Front Elevation
          </button>
          <button
            onClick={() => onSelectPresetView("side")}
            className={`px-3 py-1.5 rounded-xl text-left font-semibold transition-colors ${
              activePresetView === "side"
                ? "bg-blue-50 text-[#2563eb]"
                : "text-[#64748b] hover:text-[#0f172a] hover:bg-slate-50"
            }`}
          >
            Side Section
          </button>

          <div className="h-[1px] bg-[#e2e8f0] my-1" />

          {/* Wireframe Mode Toggle */}
          <button
            onClick={onToggleWireframe}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-xl font-semibold transition-colors ${
              wireframeMode
                ? "bg-cyan-50 text-cyan-800 border border-cyan-200 font-bold"
                : "text-[#64748b] hover:text-[#0f172a] hover:bg-slate-50"
            }`}
          >
            <Grid className="w-3.5 h-3.5" />
            <span>Wireframe Mode</span>
          </button>
        </div>
      </div>

      {/* Right Sidebar: Semantic Layers & Measurements Schedule */}
      {sidebarOpen && (
        <div className="absolute right-4 top-20 bottom-6 w-80 z-30 flex flex-col gap-4 pointer-events-auto bg-white/95 backdrop-blur-md border border-[#e2e8f0] rounded-2xl shadow-xl p-4 overflow-y-auto text-[#0f172a] animate-in slide-in-from-right duration-200">
          {/* Section 1: AI Semantic Segmentation Layers (YOLOv8-Seg) */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-purple-600" />
                <h3 className="text-xs font-bold text-[#0f172a] uppercase tracking-wider">
                  AI Semantic Layers
                </h3>
              </div>
              <span className="text-[10px] font-mono text-purple-700 font-semibold px-2 py-0.5 rounded-full bg-purple-50 border border-purple-200">
                YOLOv8-Seg 3D
              </span>
            </div>

            <p className="text-[11px] text-[#64748b]">
              Toggle segmented building systems identified by 3D projection:
            </p>

            <div className="space-y-1.5">
              {/* Layer 1: Base Geometry */}
              <button
                onClick={() => onToggleLayer("base")}
                className={`w-full flex items-center justify-between p-2 rounded-xl border text-xs transition-all ${
                  semanticLayers.base
                    ? "bg-slate-50 border-slate-300 text-[#0f172a] font-semibold"
                    : "bg-white border-[#f1f5f9] text-slate-400"
                }`}
              >
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded bg-slate-500" />
                  <span>Raw Architectural Structure</span>
                </div>
                {semanticLayers.base ? (
                  <Eye className="w-3.5 h-3.5 text-[#0f172a]" />
                ) : (
                  <EyeOff className="w-3.5 h-3.5" />
                )}
              </button>

              {/* Layer 2: Pipes (Blue) */}
              <button
                onClick={() => onToggleLayer("pipes")}
                className={`w-full flex items-center justify-between p-2 rounded-xl border text-xs transition-all ${
                  semanticLayers.pipes
                    ? "bg-blue-50 border-blue-200 text-[#1e40af] font-semibold"
                    : "bg-white border-[#f1f5f9] text-slate-400"
                }`}
              >
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded bg-[#2563eb]" />
                  <div>
                    <div className="font-semibold text-left">Chilled Water & Pipes</div>
                    <div className="text-[10px] text-[#2563eb]">96.4% confidence</div>
                  </div>
                </div>
                {semanticLayers.pipes ? (
                  <Eye className="w-3.5 h-3.5 text-[#2563eb]" />
                ) : (
                  <EyeOff className="w-3.5 h-3.5" />
                )}
              </button>

              {/* Layer 3: Electrical Conduits (Amber) */}
              <button
                onClick={() => onToggleLayer("conduits")}
                className={`w-full flex items-center justify-between p-2 rounded-xl border text-xs transition-all ${
                  semanticLayers.conduits
                    ? "bg-amber-50 border-amber-200 text-amber-900 font-semibold"
                    : "bg-white border-[#f1f5f9] text-slate-400"
                }`}
              >
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded bg-amber-500" />
                  <div>
                    <div className="font-semibold text-left">Electrical Conduits</div>
                    <div className="text-[10px] text-amber-700">91.8% confidence</div>
                  </div>
                </div>
                {semanticLayers.conduits ? (
                  <Eye className="w-3.5 h-3.5 text-amber-700" />
                ) : (
                  <EyeOff className="w-3.5 h-3.5" />
                )}
              </button>

              {/* Layer 4: HVAC Ductwork (Emerald) */}
              <button
                onClick={() => onToggleLayer("hvac")}
                className={`w-full flex items-center justify-between p-2 rounded-xl border text-xs transition-all ${
                  semanticLayers.hvac
                    ? "bg-emerald-50 border-emerald-200 text-emerald-900 font-semibold"
                    : "bg-white border-[#f1f5f9] text-slate-400"
                }`}
              >
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded bg-emerald-500" />
                  <div>
                    <div className="font-semibold text-left">HVAC Ductwork</div>
                    <div className="text-[10px] text-emerald-700">94.2% confidence</div>
                  </div>
                </div>
                {semanticLayers.hvac ? (
                  <Eye className="w-3.5 h-3.5 text-emerald-700" />
                ) : (
                  <EyeOff className="w-3.5 h-3.5" />
                )}
              </button>

              {/* Layer 5: Fire Sprinklers (Red) */}
              <button
                onClick={() => onToggleLayer("fire")}
                className={`w-full flex items-center justify-between p-2 rounded-xl border text-xs transition-all ${
                  semanticLayers.fire
                    ? "bg-red-50 border-red-200 text-red-900 font-semibold"
                    : "bg-white border-[#f1f5f9] text-slate-400"
                }`}
              >
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded bg-red-500" />
                  <div>
                    <div className="font-semibold text-left">Fire Suppression</div>
                    <div className="text-[10px] text-red-700">98.1% confidence</div>
                  </div>
                </div>
                {semanticLayers.fire ? (
                  <Eye className="w-3.5 h-3.5 text-red-700" />
                ) : (
                  <EyeOff className="w-3.5 h-3.5" />
                )}
              </button>

              {/* Layer 6: Gaussian Point Cloud Particles */}
              <button
                onClick={() => onToggleLayer("pointcloud")}
                className={`w-full flex items-center justify-between p-2 rounded-xl border text-xs transition-all ${
                  semanticLayers.pointcloud
                    ? "bg-cyan-50 border-cyan-200 text-cyan-900 font-semibold"
                    : "bg-white border-[#f1f5f9] text-slate-400"
                }`}
              >
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded bg-cyan-500" />
                  <span>Raw Gaussian Point Cloud</span>
                </div>
                {semanticLayers.pointcloud ? (
                  <Eye className="w-3.5 h-3.5 text-cyan-700" />
                ) : (
                  <EyeOff className="w-3.5 h-3.5" />
                )}
              </button>
            </div>
          </div>

          <div className="h-[1px] bg-[#e2e8f0]" />

          {/* Section 2: Metric Measurements Schedule */}
          <div className="space-y-3 flex-1 flex flex-col">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Ruler className="w-4 h-4 text-[#2563eb]" />
                <h3 className="text-xs font-bold text-[#0f172a] uppercase tracking-wider">
                  Metric Dimensions ({measurements.length})
                </h3>
              </div>
              {measurements.length > 0 && (
                <button
                  onClick={onClearMeasurements}
                  className="text-[10px] text-[#64748b] hover:text-red-600 transition-colors font-semibold"
                >
                  Clear All
                </button>
              )}
            </div>

            {measurements.length === 0 ? (
              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 text-center text-xs text-[#64748b]">
                No active dimensions. Click &quot;Measure Distance&quot; on the left to snap
                points in 3D.
              </div>
            ) : (
              <div className="space-y-2 overflow-y-auto max-h-48 pr-1">
                {measurements.map((m) => (
                  <div
                    key={m.id}
                    className="p-2.5 rounded-xl bg-[#f8fafc] border border-[#e2e8f0] flex items-center justify-between gap-2 text-xs"
                  >
                    <div>
                      <div className="font-semibold text-[#0f172a]">{m.name}</div>
                      <div className="font-mono text-[#2563eb] font-bold text-sm">
                        {m.distanceMeters.toFixed(2)} m
                      </div>
                    </div>
                    <button
                      onClick={() => onDeleteMeasurement(m.id)}
                      className="p-1.5 rounded-lg text-[#64748b] hover:text-red-600 hover:bg-slate-100"
                      title="Delete measurement"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </>
  );
};
"""

# 5. Canvas3D.tsx
canvas_3d_tsx = """\"use client\";

import React, { useEffect, useRef, useState } from "react";
import * as THREE from "three";
import { SceneBuilder, SemanticLayersState } from "./SceneBuilder";
import { MeasurementManager, MeasurementRecord } from "./MeasurementTool";

interface Canvas3DProps {
  semanticLayers: SemanticLayersState;
  isMeasureMode: boolean;
  onMeasurementsChange: (measurements: MeasurementRecord[]) => void;
  activePresetView: "perspective" | "top" | "front" | "side";
  wireframeMode: boolean;
}

export const Canvas3D: React.FC<Canvas3DProps> = ({
  semanticLayers,
  isMeasureMode,
  onMeasurementsChange,
  activePresetView,
  wireframeMode,
}) => {
  const mountRef = useRef<HTMLDivElement>(null);
  const sceneBuilderRef = useRef<SceneBuilder | null>(null);
  const measurementManagerRef = useRef<MeasurementManager | null>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);

  // Orbit state
  const isDraggingRef = useRef(false);
  const isRightClickRef = useRef(false);
  const previousMousePositionRef = useRef({ x: 0, y: 0 });
  const cameraTargetRef = useRef(new THREE.Vector3(0, 2, 0));
  const sphericalRef = useRef({ radius: 9, theta: Math.PI / 4, phi: Math.PI / 3 });

  const [hoveredCoordinate, setHoveredCoordinate] = useState<string | null>(null);

  useEffect(() => {
    if (!mountRef.current) return;

    const container = mountRef.current;
    const width = container.clientWidth;
    const height = container.clientHeight;

    // 1. Scene & Camera
    const sceneBuilder = new SceneBuilder();
    sceneBuilderRef.current = sceneBuilder;

    const camera = new THREE.PerspectiveCamera(55, width / height, 0.1, 100);
    cameraRef.current = camera;
    updateCameraPosition();

    // 2. Renderer
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.1;
    container.innerHTML = "";
    container.appendChild(renderer.domElement);
    rendererRef.current = renderer;

    // 3. Measurement Manager
    const measurementManager = new MeasurementManager(
      sceneBuilder.scene,
      camera,
      container
    );
    measurementManagerRef.current = measurementManager;
    onMeasurementsChange([...measurementManager.measurements]);

    // 4. Raycaster for clicking & measuring
    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();

    const handlePointerDown = (e: MouseEvent) => {
      isDraggingRef.current = true;
      isRightClickRef.current = e.button === 2;
      previousMousePositionRef.current = { x: e.clientX, y: e.clientY };
    };

    const handlePointerMove = (e: MouseEvent) => {
      const rect = container.getBoundingClientRect();
      mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

      // Coordinate HUD readout on hover
      raycaster.setFromCamera(mouse, camera);
      const hits = raycaster.intersectObjects(sceneBuilder.interactiveMeshes, true);
      if (hits.length > 0) {
        const p = hits[0].point;
        setHoveredCoordinate(
          `X: ${p.x >= 0 ? "+" : ""}${p.x.toFixed(2)}m  Y: ${p.y.toFixed(
            2
          )}m  Z: ${p.z >= 0 ? "+" : ""}${p.z.toFixed(2)}m`
        );
      }

      if (!isDraggingRef.current) return;

      const deltaX = e.clientX - previousMousePositionRef.current.x;
      const deltaY = e.clientY - previousMousePositionRef.current.y;
      previousMousePositionRef.current = { x: e.clientX, y: e.clientY };

      if (isRightClickRef.current) {
        // Pan
        const panSpeed = 0.008 * (sphericalRef.current.radius / 10);
        const forward = new THREE.Vector3();
        camera.getWorldDirection(forward);
        const right = new THREE.Vector3().crossVectors(forward, camera.up).normalize();
        const up = new THREE.Vector3().crossVectors(right, forward).normalize();

        cameraTargetRef.current.addScaledVector(right, -deltaX * panSpeed);
        cameraTargetRef.current.addScaledVector(up, deltaY * panSpeed);
      } else {
        // Orbit
        sphericalRef.current.theta -= deltaX * 0.006;
        sphericalRef.current.phi = Math.max(
          0.05,
          Math.min(Math.PI / 2 + 0.1, sphericalRef.current.phi - deltaY * 0.006)
        );
      }

      updateCameraPosition();
    };

    const handlePointerUp = (e: MouseEvent) => {
      const deltaMove =
        Math.abs(e.clientX - previousMousePositionRef.current.x) +
        Math.abs(e.clientY - previousMousePositionRef.current.y);

      isDraggingRef.current = false;

      // Treat as Click if minimal movement
      if (deltaMove < 5 && e.button === 0 && measurementManagerRef.current?.isMeasureModeActive) {
        const rect = container.getBoundingClientRect();
        mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
        mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

        raycaster.setFromCamera(mouse, camera);
        const intersects = raycaster.intersectObjects(
          sceneBuilder.interactiveMeshes,
          true
        );

        if (intersects.length > 0) {
          const clickedPoint = intersects[0].point;
          measurementManagerRef.current.handlePointClick(clickedPoint);
          onMeasurementsChange([...measurementManagerRef.current.measurements]);
        }
      }
    };

    const handleWheel = (e: WheelEvent) => {
      e.preventDefault();
      const zoomSpeed = 0.002;
      sphericalRef.current.radius = Math.max(
        1.5,
        Math.min(25, sphericalRef.current.radius + e.deltaY * zoomSpeed)
      );
      updateCameraPosition();
    };

    const handleContextMenu = (e: MouseEvent) => e.preventDefault();

    container.addEventListener("mousedown", handlePointerDown);
    window.addEventListener("mousemove", handlePointerMove);
    window.addEventListener("mouseup", handlePointerUp);
    container.addEventListener("wheel", handleWheel, { passive: false });
    container.addEventListener("contextmenu", handleContextMenu);

    // 5. Animation Loop
    let animationFrameId: number;
    const animate = () => {
      animationFrameId = requestAnimationFrame(animate);
      renderer.render(sceneBuilder.scene, camera);
    };
    animate();

    // 6. Resize Observer
    const resizeObserver = new ResizeObserver(() => {
      if (!container || !renderer || !camera) return;
      const w = container.clientWidth;
      const h = container.clientHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    });
    resizeObserver.observe(container);

    return () => {
      cancelAnimationFrame(animationFrameId);
      container.removeEventListener("mousedown", handlePointerDown);
      window.removeEventListener("mousemove", handlePointerMove);
      window.removeEventListener("mouseup", handlePointerUp);
      container.removeEventListener("wheel", handleWheel);
      container.removeEventListener("contextmenu", handleContextMenu);
      resizeObserver.disconnect();
      renderer.dispose();
    };
  }, []);

  function updateCameraPosition() {
    if (!cameraRef.current) return;
    const { radius, theta, phi } = sphericalRef.current;
    const target = cameraTargetRef.current;

    cameraRef.current.position.set(
      target.x + radius * Math.sin(phi) * Math.sin(theta),
      target.y + radius * Math.cos(phi),
      target.z + radius * Math.sin(phi) * Math.cos(theta)
    );
    cameraRef.current.lookAt(target);
  }

  // Update measurement mode active state
  useEffect(() => {
    if (measurementManagerRef.current) {
      measurementManagerRef.current.isMeasureModeActive = isMeasureMode;
    }
  }, [isMeasureMode]);

  // Update semantic layers
  useEffect(() => {
    if (sceneBuilderRef.current) {
      sceneBuilderRef.current.updateSemanticLayers(semanticLayers);
    }
  }, [semanticLayers]);

  // Handle Preset Views
  useEffect(() => {
    if (!cameraRef.current) return;

    if (activePresetView === "perspective") {
      sphericalRef.current = { radius: 9, theta: Math.PI / 4, phi: Math.PI / 3 };
      cameraTargetRef.current.set(0, 2, 0);
    } else if (activePresetView === "top") {
      sphericalRef.current = { radius: 10, theta: 0, phi: 0.05 };
      cameraTargetRef.current.set(0, 1, 0);
    } else if (activePresetView === "front") {
      sphericalRef.current = { radius: 9, theta: 0, phi: Math.PI / 2 };
      cameraTargetRef.current.set(0, 2, -1);
    } else if (activePresetView === "side") {
      sphericalRef.current = { radius: 9, theta: Math.PI / 2, phi: Math.PI / 2 };
      cameraTargetRef.current.set(0, 2, -1);
    }

    updateCameraPosition();
  }, [activePresetView]);

  // Wireframe toggle
  useEffect(() => {
    if (!sceneBuilderRef.current) return;
    sceneBuilderRef.current.scene.traverse((obj) => {
      if ((obj as THREE.Mesh).isMesh) {
        const mesh = obj as THREE.Mesh;
        if (Array.isArray(mesh.material)) {
          mesh.material.forEach((m) => {
            if ("wireframe" in m) {
              (m as THREE.MeshStandardMaterial).wireframe = wireframeMode;
            }
          });
        } else if (mesh.material && "wireframe" in mesh.material) {
          (mesh.material as THREE.MeshStandardMaterial).wireframe = wireframeMode;
        }
      }
    });
  }, [wireframeMode]);

  return (
    <div className="relative w-full h-full select-none overflow-hidden bg-[#0a0f1d]">
      <div ref={mountRef} className="w-full h-full cursor-grab active:cursor-grabbing" />

      {/* Real-time Hovered 3D Coordinate Ticker (AR Metric Anchor) */}
      {hoveredCoordinate && (
        <div className="absolute bottom-4 left-4 z-20 px-3.5 py-2 rounded-xl bg-white/95 backdrop-blur-md border border-[#e2e8f0] text-xs font-mono text-[#0f172a] shadow-md pointer-events-none flex items-center gap-2.5">
          <span className="w-2 h-2 rounded-full bg-[#2563eb] animate-pulse" />
          <span className="font-bold">{hoveredCoordinate}</span>
          <span className="text-[#64748b] font-sans text-[11px] font-medium">
            [Metric SE(3) 1:1 Scale]
          </span>
        </div>
      )}

      {/* Measurement Mode Helper Callout */}
      {isMeasureMode && (
        <div className="absolute top-4 left-1/2 -translate-x-1/2 z-20 px-4 py-2.5 rounded-2xl bg-[#2563eb] text-white shadow-xl text-xs font-bold flex items-center gap-2 animate-bounce">
          <span>📐 Click two points on the 3D model to measure metric distance</span>
        </div>
      )}
    </div>
  );
};
"""

with open(os.path.join(base_dir, "src", "app", "page.tsx"), "w", encoding="utf-8") as f:
    f.write(page_tsx)

with open(os.path.join(base_dir, "src", "app", "dashboard", "page.tsx"), "w", encoding="utf-8") as f:
    f.write(dashboard_tsx)

with open(os.path.join(base_dir, "src", "components", "ExportModal.tsx"), "w", encoding="utf-8") as f:
    f.write(export_modal_tsx)

with open(os.path.join(base_dir, "src", "components", "Viewer3D", "ViewerHUD.tsx"), "w", encoding="utf-8") as f:
    f.write(viewer_hud_tsx)

with open(os.path.join(base_dir, "src", "components", "Viewer3D", "Canvas3D.tsx"), "w", encoding="utf-8") as f:
    f.write(canvas_3d_tsx)

print("All files rewritten cleanly and synchronized.")
