"use client";

import React from "react";
import { ShieldCheck, Sparkles } from "lucide-react";
import { Project } from "@/lib/mockData";
import { StatusPill } from "@/components/StatusPill";
import { DETAIL_TABS, DetailTab } from "@/components/ProjectDetail/DetailSidebar";

interface ProjectDetailTopBarProps {
  project: Project;
  activeTab: DetailTab;
  onSelectTab: (tab: DetailTab) => void;
}

/**
 * Compact horizontal strip that owns identity + tabs + provenance. Kept short
 * (~44 px) so the 3D viewport gets as much room as possible, with an idle-hide
 * dance handled by the viewer page.
 */
export const ProjectDetailTopBar: React.FC<ProjectDetailTopBarProps> = ({
  project,
  activeTab,
  onSelectTab,
}) => (
  <header className="shrink-0 border-b border-[#e2e8f0] bg-white/95 backdrop-blur-md">
    <div className="px-4 py-1.5 flex items-center gap-3 flex-wrap lg:flex-nowrap">
      {/* Identity — no icon block, just name + one-line meta */}
      <div className="flex items-baseline gap-2 min-w-0 shrink-0">
        <h1 className="text-[13px] font-extrabold text-[#0f172a] tracking-tight truncate">
          {project.name}
        </h1>
        <span className="text-[10px] text-[#94a3b8] truncate hidden md:inline">
          {project.floor} · {project.block} · {project.area}
        </span>
      </div>

      <StatusPill status={project.status} label={project.statusLabel} animated />

      {/* Tabs — flex-grow so they sit centre-right */}
      <nav
        role="tablist"
        aria-label="Project sections"
        className="flex-1 min-w-0 flex items-center gap-0.5 overflow-x-auto"
      >
        {DETAIL_TABS.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              role="tab"
              aria-selected={isActive}
              onClick={() => onSelectTab(tab.id)}
              className={`shrink-0 inline-flex items-center gap-1 px-2 py-1 rounded-lg text-[11px] font-bold transition-all cursor-pointer ${
                isActive
                  ? "bg-blue-50 text-[#2563eb]"
                  : "text-[#64748b] hover:text-[#0f172a] hover:bg-slate-50"
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </nav>

      {/* Provenance — tiny mono chips on the right, xl+ only */}
      <div className="hidden xl:flex items-center gap-3 shrink-0 pl-3 border-l border-[#f1f5f9] text-[10px] font-mono">
        <span className="inline-flex items-center gap-1 text-[#059669]">
          <ShieldCheck className="w-3 h-3" />
          <span className="font-bold">{project.accuracy ?? "—"}</span>
        </span>
        <span className="inline-flex items-center gap-1 text-[#2563eb]">
          <Sparkles className="w-3 h-3" />
          <span className="font-bold">{project.gaussianCount ?? "—"}</span>
        </span>
      </div>
    </div>
  </header>
);
