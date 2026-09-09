"use client";

import React from "react";
import { ChevronDown, Smartphone, ShieldCheck, Sparkles } from "lucide-react";
import { Project } from "@/lib/mockData";
import { StatusPill } from "@/components/StatusPill";
import { DETAIL_TABS, DetailTab } from "@/components/ProjectDetail/DetailSidebar";

interface ProjectDetailTopBarProps {
  project: Project;
  activeTab: DetailTab;
  onSelectTab: (tab: DetailTab) => void;
}

/**
 * Horizontal replacement for the left DetailSidebar — puts identity + tab
 * navigation + capture provenance in a single strip so the 3D viewport gets
 * the whole viewport width.
 */
export const ProjectDetailTopBar: React.FC<ProjectDetailTopBarProps> = ({
  project,
  activeTab,
  onSelectTab,
}) => (
  <header className="shrink-0 border-b border-[#e2e8f0] bg-white">
    <div className="px-5 py-3 flex items-center gap-4 flex-wrap lg:flex-nowrap">
      {/* Identity block */}
      <div className="flex items-center gap-3 min-w-0 shrink-0">
        <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-[#2563eb] to-[#1d4ed8] flex items-center justify-center shrink-0">
          <Sparkles className="w-4 h-4 text-white" />
        </div>
        <div className="min-w-0">
          <h1 className="text-sm font-extrabold text-[#0f172a] tracking-tight leading-tight truncate">
            {project.name}
          </h1>
          <p className="text-[10px] text-[#64748b] leading-tight">
            {project.floor} · {project.block} · {project.area} · {project.scansCount} scans
          </p>
        </div>
      </div>

      <StatusPill status={project.status} label={project.statusLabel} animated />

      {/* Tabs — flex grow so they sit centre-right */}
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
              className={`shrink-0 inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-[11px] font-bold transition-all cursor-pointer ${
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

      {/* Capture provenance */}
      <div className="hidden xl:flex items-center gap-3 shrink-0 pl-3 border-l border-[#f1f5f9]">
        <ProvenanceChip
          Icon={Smartphone}
          label="Device"
          value={project.captureDevice ?? "—"}
        />
        <ProvenanceChip
          Icon={ShieldCheck}
          label="Accuracy"
          value={project.accuracy ?? "—"}
          tint="emerald"
        />
        <ProvenanceChip
          Icon={Sparkles}
          label="Gaussians"
          value={project.gaussianCount ?? "—"}
          tint="blue"
        />
      </div>

      {/* Mobile-only provenance popover trigger */}
      <button className="xl:hidden flex items-center gap-1 px-2 py-1 rounded-lg border border-[#e2e8f0] bg-white text-[10px] font-bold text-[#0f172a] shrink-0 cursor-pointer">
        <span>Capture</span>
        <ChevronDown className="w-3 h-3 text-[#64748b]" />
      </button>
    </div>
  </header>
);

/* ---------------------------- pieces ---------------------------- */

const ProvenanceChip: React.FC<{
  Icon: React.ComponentType<{ className?: string }>;
  label: string;
  value: string;
  tint?: "blue" | "emerald" | "slate";
}> = ({ Icon, label, value, tint = "slate" }) => {
  const iconClass =
    tint === "blue"
      ? "text-[#2563eb]"
      : tint === "emerald"
      ? "text-[#059669]"
      : "text-[#94a3b8]";
  const valueClass =
    tint === "blue"
      ? "text-[#2563eb]"
      : tint === "emerald"
      ? "text-[#059669]"
      : "text-[#0f172a]";
  return (
    <div className="flex items-center gap-1.5">
      <Icon className={`w-3.5 h-3.5 ${iconClass}`} />
      <div className="leading-tight">
        <p className="text-[9px] font-bold uppercase tracking-wider text-[#94a3b8]">
          {label}
        </p>
        <p className={`text-[10px] font-mono font-bold ${valueClass} truncate max-w-[160px]`}>
          {value}
        </p>
      </div>
    </div>
  );
};
