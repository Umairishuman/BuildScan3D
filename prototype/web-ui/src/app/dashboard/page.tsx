"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { AppShell } from "@/components/AppShell";
import { ProjectCard } from "@/components/ProjectCard";
import { FloorPlanView } from "@/components/FloorPlanView";
import { JobStatusModal } from "@/components/JobStatusModal";
import { NewCaptureModal } from "@/components/NewCaptureModal";
import { MOCK_PROJECTS, Project } from "@/lib/mockData";
import { NavId } from "@/lib/navigation";
import {
  Plus,
  LayoutGrid,
  List,
  Calendar,
  ChevronDown,
} from "lucide-react";

export default function DashboardPage() {
  const router = useRouter();
  const [projects] = useState<Project[]>(MOCK_PROJECTS);
  const [currentTab, setCurrentTab] = useState<NavId>("dashboard");
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
    if (!proj) return;
    // A scan still training has nothing to render yet, so show its job status
    // instead of dropping the user into an empty workspace.
    if (proj.status === "processing") {
      handleOpenProcessing(proj);
      return;
    }
    router.push(`/viewer/${proj.id}`);
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
    <AppShell
      activeNav={currentTab}
      onSelectNav={(item) => setCurrentTab(item.id)}
      searchQuery={searchQuery}
      onSearchChange={setSearchQuery}
      onOpenRecentSite={handleOpenProjectFromRecent}
    >
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

          {/* Project Cards Grid */}
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
    </AppShell>
  );
}
