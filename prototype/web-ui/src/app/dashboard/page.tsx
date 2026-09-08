"use client";

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
