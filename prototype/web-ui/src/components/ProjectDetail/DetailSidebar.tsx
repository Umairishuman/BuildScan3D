"use client";

import React from "react";
import {
  LayoutPanelLeft,
  Box,
  Ruler,
  History,
  Files,
  FileText,
  type LucideIcon,
} from "lucide-react";
import { Project } from "@/lib/mockData";
import { StatusPill } from "@/components/StatusPill";

export type DetailTab =
  | "overview"
  | "viewer"
  | "measurements"
  | "history"
  | "files"
  | "report";

interface DetailTabItem {
  id: DetailTab;
  label: string;
  icon: LucideIcon;
  /** Screens still to be built get a marker instead of a dead click. */
  ready: boolean;
}

export const DETAIL_TABS: readonly DetailTabItem[] = [
  { id: "overview", label: "Overview", icon: LayoutPanelLeft, ready: false },
  { id: "viewer", label: "3D Viewer", icon: Box, ready: true },
  { id: "measurements", label: "Measurements", icon: Ruler, ready: false },
  { id: "history", label: "History", icon: History, ready: false },
  { id: "files", label: "Files", icon: Files, ready: false },
  { id: "report", label: "Report", icon: FileText, ready: false },
] as const;

interface DetailSidebarProps {
  project: Project;
  activeTab: DetailTab;
  onSelectTab: (tab: DetailTab) => void;
}

export const DetailSidebar: React.FC<DetailSidebarProps> = ({
  project,
  activeTab,
  onSelectTab,
}) => {
  return (
    <aside className="w-[260px] shrink-0 border-r border-[#e2e8f0] bg-white flex flex-col overflow-y-auto">
      {/* Project identity block */}
      <div className="p-5 border-b border-[#f1f5f9] space-y-2.5">
        <h1 className="text-base font-extrabold text-[#0f172a] tracking-tight leading-snug">
          {project.name}
        </h1>

        <StatusPill
          status={project.status}
          label={project.statusLabel}
          animated
        />

        <p className="text-[11px] text-[#64748b] leading-relaxed">
          {project.floor} · {project.block} · {project.area} · {project.scansCount} scans
        </p>
      </div>

      {/* Secondary navigation */}
      <nav className="p-3 space-y-1">
        {DETAIL_TABS.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => onSelectTab(tab.id)}
              aria-current={isActive ? "page" : undefined}
              className={`w-full flex items-center justify-between px-3 py-2 rounded-xl text-xs font-semibold transition-all cursor-pointer ${
                isActive
                  ? "text-[#2563eb] bg-blue-50/90 font-bold shadow-xs"
                  : "text-[#64748b] hover:text-[#0f172a] hover:bg-slate-50"
              }`}
            >
              <div className="flex items-center gap-3">
                <Icon
                  className={`w-4 h-4 ${
                    isActive ? "text-[#2563eb]" : "text-[#94a3b8]"
                  }`}
                />
                <span>{tab.label}</span>
              </div>
              {isActive && <span className="w-1.5 h-1.5 rounded-full bg-[#2563eb]" />}
            </button>
          );
        })}
      </nav>

      {/* Capture provenance — grounds the demo in the ARCore pipeline */}
      <div className="mt-auto p-4 border-t border-[#f1f5f9] space-y-2.5">
        <h4 className="text-[10px] font-bold text-[#94a3b8] uppercase tracking-wider">
          Capture Source
        </h4>
        <dl className="space-y-1.5">
          <div className="flex items-center justify-between gap-2">
            <dt className="text-[10px] text-[#64748b]">Device</dt>
            <dd className="text-[10px] font-semibold text-[#0f172a] truncate max-w-[150px] text-right">
              {project.captureDevice ?? "—"}
            </dd>
          </div>
          <div className="flex items-center justify-between gap-2">
            <dt className="text-[10px] text-[#64748b]">Accuracy</dt>
            <dd className="text-[10px] font-mono font-bold text-emerald-700">
              {project.accuracy ?? "—"}
            </dd>
          </div>
          <div className="flex items-center justify-between gap-2">
            <dt className="text-[10px] text-[#64748b]">Gaussians</dt>
            <dd className="text-[10px] font-mono font-bold text-[#2563eb]">
              {project.gaussianCount ?? "—"}
            </dd>
          </div>
        </dl>
      </div>
    </aside>
  );
};
