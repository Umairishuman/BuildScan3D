"use client";

import React, { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { AppShell } from "@/components/AppShell";
import { ProjectCard } from "@/components/ProjectCard";
import { UserPlanCard } from "@/components/UserPlanCard";
import { JobStatusModal } from "@/components/JobStatusModal";
import { NewCaptureModal } from "@/components/NewCaptureModal";
import { CreateProjectModal } from "@/components/CreateProjectModal";
import { ProjectsBackdrop } from "@/components/ProjectsBackdrop";
import { BuildingPlan, MOCK_PROJECTS, Project } from "@/lib/mockData";
import { deleteUserPlan, loadUserPlans } from "@/lib/userPlans";
import {
  Plus,
  LayoutGrid,
  List,
  Calendar,
  ChevronDown,
  UploadCloud,
} from "lucide-react";

type StatusFilter = "all" | "ready" | "processing" | "complete" | "draft" | "archived";

const FILTER_STYLES: Record<
  StatusFilter,
  { dot: string; activeBg: string }
> = {
  all: { dot: "", activeBg: "bg-[#2563eb]" },
  ready: { dot: "bg-[#10b981]", activeBg: "bg-[#10b981]" },
  processing: { dot: "bg-[#f59e0b]", activeBg: "bg-[#f59e0b]" },
  complete: { dot: "bg-[#14b8a6]", activeBg: "bg-[#14b8a6]" },
  draft: { dot: "bg-[#94a3b8]", activeBg: "bg-[#64748b]" },
  archived: { dot: "bg-slate-400", activeBg: "bg-slate-700" },
};

const FILTERS: { id: StatusFilter; label: string }[] = [
  { id: "all", label: "All" },
  { id: "ready", label: "Ready" },
  { id: "processing", label: "Processing" },
  { id: "complete", label: "Signed Off" },
  { id: "draft", label: "Draft" },
  { id: "archived", label: "Archived" },
];

export default function ProjectsPage() {
  const router = useRouter();
  const [projects] = useState<Project[]>(MOCK_PROJECTS);
  const [filter, setFilter] = useState<StatusFilter>("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [viewMode, setViewMode] = useState<"grid" | "list">("grid");
  const [isJobModalOpen, setIsJobModalOpen] = useState(false);
  const [selectedJobProject, setSelectedJobProject] = useState<Project | null>(null);
  const [isNewCaptureModalOpen, setIsNewCaptureModalOpen] = useState(false);
  const [isCreateProjectModalOpen, setIsCreateProjectModalOpen] = useState(false);
  const [userPlans, setUserPlans] = useState<BuildingPlan[]>([]);

  const refreshUserPlans = useCallback(() => {
    setUserPlans(loadUserPlans());
  }, []);

  // Rehydrate from localStorage on mount and whenever the create modal closes
  // (so newly-created plans appear without a full page reload).
  useEffect(() => {
    refreshUserPlans();
  }, [refreshUserPlans]);

  const handleDeleteUserPlan = (projectId: string) => {
    deleteUserPlan(projectId);
    refreshUserPlans();
  };

  const handleCloseCreateModal = () => {
    setIsCreateProjectModalOpen(false);
    refreshUserPlans();
  };

  const handleOpenProcessing = (project: Project) => {
    setSelectedJobProject(project);
    setIsJobModalOpen(true);
  };

  const handleOpenProjectFromRecent = (projectId: string) => {
    const proj = projects.find((p) => p.id === projectId);
    if (!proj) return;
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

  const counts = {
    ready: projects.filter((p) => p.status === "ready").length,
    processing: projects.filter((p) => p.status === "processing").length,
    complete: projects.filter((p) => p.status === "complete").length,
  };

  return (
    <AppShell
      activeNav="projects"
      searchQuery={searchQuery}
      onSearchChange={setSearchQuery}
      onOpenRecentSite={handleOpenProjectFromRecent}
    >
      <div className="relative">
        <ProjectsBackdrop />

        <div className="relative z-10 space-y-6">
          {/* Header row */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <h1 className="text-2xl font-extrabold text-[#0f172a] tracking-tight">
                Projects Portfolio
              </h1>
              <p className="text-xs text-[#64748b] mt-0.5">
                {projects.length} sites captured ·{" "}
                <span className="font-bold text-[#059669]">{counts.ready} ready to review</span>
                {" · "}
                <span className="font-bold text-[#d97706]">{counts.processing} in training</span>
                {" · "}
                <span className="font-bold text-[#0f766e]">{counts.complete} signed off</span>
              </p>
            </div>

            <div className="flex items-center gap-2">
              <div className="flex items-center rounded-xl bg-white border border-[#e2e8f0] p-1 shadow-sm">
                <button
                  onClick={() => setViewMode("grid")}
                  className={`p-1.5 rounded-lg transition-colors cursor-pointer ${
                    viewMode === "grid"
                      ? "bg-slate-100 text-[#2563eb]"
                      : "text-[#94a3b8] hover:text-[#0f172a]"
                  }`}
                  title="Grid view"
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
                  title="List view"
                >
                  <List className="w-4 h-4" />
                </button>
              </div>

              <button
                onClick={() => setIsCreateProjectModalOpen(true)}
                className="px-3.5 py-2 rounded-xl bg-white border border-[#e2e8f0] hover:bg-slate-50 hover:border-blue-200 text-xs font-bold text-[#0f172a] shadow-sm transition-all flex items-center gap-1.5 cursor-pointer"
              >
                <UploadCloud className="w-4 h-4 text-[#2563eb]" />
                <span>Upload Floor Plan</span>
              </button>

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

          {/* Filter pills + date */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div className="flex items-center gap-2 overflow-x-auto pb-1 sm:pb-0">
              {FILTERS.map((f) => {
                const isActive = filter === f.id;
                const s = FILTER_STYLES[f.id];
                return (
                  <button
                    key={f.id}
                    onClick={() => setFilter(f.id)}
                    className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-full text-xs font-bold transition-all cursor-pointer ${
                      isActive
                        ? `${s.activeBg} text-white shadow-sm`
                        : "bg-white text-[#64748b] border border-[#e2e8f0] hover:text-[#0f172a]"
                    }`}
                  >
                    {s.dot && <span className={`w-1.5 h-1.5 rounded-full ${s.dot}`} />}
                    <span>{f.label}</span>
                  </button>
                );
              })}
            </div>

            <button className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-white border border-[#e2e8f0] text-xs font-semibold text-[#0f172a] shadow-sm hover:bg-slate-50 cursor-pointer">
              <Calendar className="w-3.5 h-3.5 text-[#64748b]" />
              <span>Apr 1, 2025 - Apr 30, 2025</span>
              <ChevronDown className="w-3.5 h-3.5 text-[#64748b]" />
            </button>
          </div>

          {/* Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 pt-2">
            {filteredProjects.map((project) => (
              <ProjectCard
                key={project.id}
                project={project}
                onOpenProcessingModal={handleOpenProcessing}
              />
            ))}
          </div>

          {filteredProjects.length === 0 && (
            <div className="py-16 text-center rounded-2xl border border-dashed border-[#cbd5e1] bg-white/60">
              <p className="text-sm font-bold text-[#0f172a]">
                No projects match this filter
              </p>
              <p className="text-xs text-[#64748b] mt-1">
                Try clearing the search or switching status filter to All.
              </p>
            </div>
          )}
        </div>
      </div>

      <JobStatusModal
        isOpen={isJobModalOpen}
        onClose={() => setIsJobModalOpen(false)}
        project={selectedJobProject}
      />

      <NewCaptureModal
        isOpen={isNewCaptureModalOpen}
        onClose={() => setIsNewCaptureModalOpen(false)}
      />

      <CreateProjectModal
        isOpen={isCreateProjectModalOpen}
        onClose={() => setIsCreateProjectModalOpen(false)}
      />
    </AppShell>
  );
}
