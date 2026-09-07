"use client";

import React, { useState } from "react";
import { Navbar } from "@/components/Navbar";
import { ProjectCard } from "@/components/ProjectCard";
import { JobStatusModal } from "@/components/JobStatusModal";
import { NewCaptureModal } from "@/components/NewCaptureModal";
import { MOCK_PROJECTS, Project } from "@/lib/mockData";
import {
  Layers,
  Sparkles,
  Activity,
  CheckCircle2,
  Plus,
  Ruler,
  HardHat,
  Filter,
  Search,
  ArrowUpRight,
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
    <div className="min-h-screen w-full bg-slate-950 text-slate-100 flex flex-col">
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
                <h1 className="text-2xl font-extrabold text-white tracking-tight">
                  Project Workspace
                </h1>
                <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
                  Site: Metro Tower B
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-1">
                Field telemetry fused with 3D Gaussian Splatting for millimeter-grade MEP validation
              </p>
            </div>

            <button
              onClick={() => setIsNewCaptureModalOpen(true)}
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 via-indigo-600 to-cyan-500 hover:from-blue-500 hover:to-cyan-400 text-white text-xs font-bold shadow-lg shadow-blue-500/20 transition-all cursor-pointer"
            >
              <Plus className="w-4 h-4" />
              <span>Initiate New Capture</span>
            </button>
          </div>

          {/* Metric KPI Row */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            {/* KPI 1 */}
            <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 backdrop-blur-sm space-y-1">
              <div className="flex items-center justify-between text-slate-400">
                <span className="text-xs font-semibold">Total Site Scans</span>
                <Database className="w-4 h-4 text-blue-400" />
              </div>
              <div className="text-2xl font-bold text-white font-mono">12</div>
              <div className="text-[11px] text-slate-400 flex items-center gap-1">
                <span className="text-emerald-400 font-bold">+3 scans</span> this week
              </div>
            </div>

            {/* KPI 2 */}
            <div
              onClick={() => {
                setSelectedJobProject(projects.find((p) => p.status === "processing") || null);
                setIsJobModalOpen(true);
              }}
              className="p-4 rounded-2xl bg-gradient-to-b from-amber-950/30 to-slate-900/80 border border-amber-500/30 backdrop-blur-sm space-y-1 cursor-pointer hover:border-amber-500/60 transition-colors"
            >
              <div className="flex items-center justify-between text-amber-300">
                <span className="text-xs font-semibold">Active Cloud Jobs</span>
                <Activity className="w-4 h-4 text-amber-400 animate-spin" />
              </div>
              <div className="text-2xl font-bold text-white font-mono flex items-center gap-2">
                <span>1</span>
                <span className="text-xs font-sans text-amber-400 font-medium">Training (68%)</span>
              </div>
              <div className="text-[11px] text-amber-300/80 flex items-center gap-1">
                Click to inspect live pipeline queue →
              </div>
            </div>

            {/* KPI 3 */}
            <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 backdrop-blur-sm space-y-1">
              <div className="flex items-center justify-between text-slate-400">
                <span className="text-xs font-semibold">Ready for Inspection</span>
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              </div>
              <div className="text-2xl font-bold text-white font-mono">{readyCount}</div>
              <div className="text-[11px] text-emerald-400 flex items-center gap-1 font-mono">
                1:1 Metric Ground Truth Active
              </div>
            </div>

            {/* KPI 4 */}
            <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 backdrop-blur-sm space-y-1">
              <div className="flex items-center justify-between text-slate-400">
                <span className="text-xs font-semibold">Avg Metric Accuracy</span>
                <Ruler className="w-4 h-4 text-cyan-400" />
              </div>
              <div className="text-2xl font-bold text-cyan-300 font-mono">±1.2 mm</div>
              <div className="text-[11px] text-slate-400">
                Calibrated against ARCore 120Hz VIO
              </div>
            </div>
          </div>
        </div>

        {/* Filter and Search Bar */}
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4 pt-4 border-t border-slate-800/80">
          {/* Filter Tabs */}
          <div className="flex items-center gap-1.5 p-1 rounded-xl bg-slate-900 border border-slate-800 overflow-x-auto">
            <button
              onClick={() => setFilter("all")}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors whitespace-nowrap ${
                filter === "all"
                  ? "bg-blue-600 text-white shadow"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              All Scans ({projects.length})
            </button>
            <button
              onClick={() => setFilter("ready")}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors whitespace-nowrap ${
                filter === "ready"
                  ? "bg-emerald-600 text-white shadow"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              Ready for Inspection ({readyCount})
            </button>
            <button
              onClick={() => setFilter("processing")}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors whitespace-nowrap ${
                filter === "processing"
                  ? "bg-amber-600 text-white shadow"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              Processing ({processingCount})
            </button>
            <button
              onClick={() => setFilter("draft")}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors whitespace-nowrap ${
                filter === "draft"
                  ? "bg-slate-700 text-white shadow"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              Drafts ({draftCount})
            </button>
          </div>

          {/* Search box */}
          <div className="relative w-full sm:w-72">
            <Search className="w-4 h-4 text-slate-500 absolute left-3 top-2.5 pointer-events-none" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by sector or room name..."
              className="w-full pl-9 pr-4 py-2 bg-slate-900 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition-colors"
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

      {/* Screen 3: Active Job Status Modal (Pipeline Architecture Inspector) */}
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
