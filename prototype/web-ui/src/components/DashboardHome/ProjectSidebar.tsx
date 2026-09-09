"use client";

import React from "react";
import Link from "next/link";
import Image from "next/image";
import {
  Building2,
  Calendar,
  Check,
  ChevronRight,
  Circle,
  Clock,
  Download,
  Gauge,
  MoreHorizontal,
  Ruler,
  Sparkles,
  Target,
  Zap,
} from "lucide-react";

interface PipelineStep {
  id: string;
  Icon: React.ComponentType<{ className?: string }>;
  label: string;
  status: "complete" | "in_progress" | "pending";
}

const PIPELINE: PipelineStep[] = [
  { id: "3dgs", Icon: Sparkles, label: "3DGS Reconstruction", status: "complete" },
  { id: "metric", Icon: Gauge, label: "Metric Verification", status: "complete" },
  { id: "align", Icon: Target, label: "Spatial Alignment", status: "in_progress" },
  { id: "anomaly", Icon: Zap, label: "Anomaly Detection", status: "pending" },
];

interface QuickStat {
  Icon: React.ComponentType<{ className?: string }>;
  label: string;
  value: string;
}

const QUICK_STATS: QuickStat[] = [
  { Icon: Ruler, label: "Area Scanned", value: "847 m²" },
  { Icon: Circle, label: "Point Count", value: "12.4 M" },
  { Icon: Target, label: "Avg. GSD", value: "2.3 cm/px" },
  { Icon: Gauge, label: "Accuracy", value: "98.7%" },
];

interface ProjectSidebarProps {
  projectHref: string;
  onExport: () => void;
}

export const ProjectSidebar: React.FC<ProjectSidebarProps> = ({
  projectHref,
  onExport,
}) => (
  <aside className="w-[360px] shrink-0 flex flex-col gap-3 min-h-0 overflow-y-auto pr-1">
    {/* Date/time + Export */}
    <div className="flex items-center gap-2">
      <button className="flex-1 flex items-center justify-between gap-2 px-3 py-2 rounded-xl bg-white border border-[#e2e8f0] text-[#0f172a] shadow-sm hover:bg-slate-50 transition-colors cursor-pointer">
        <div className="flex items-center gap-2">
          <Calendar className="w-3.5 h-3.5 text-[#64748b]" />
          <span className="text-[11px] font-bold">Apr 22, 2025 · 10:24 AM</span>
        </div>
        <ChevronRight className="w-3.5 h-3.5 text-[#94a3b8] rotate-90" />
      </button>
      <button
        onClick={onExport}
        className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-[#2563eb] hover:bg-[#1d4ed8] text-white text-[11px] font-bold shadow-sm transition-colors cursor-pointer"
      >
        <Download className="w-3.5 h-3.5" />
        Export
      </button>
    </div>

    {/* Project Overview card */}
    <section className="rounded-2xl bg-white border border-[#e2e8f0] shadow-sm overflow-hidden">
      <div className="px-4 py-3 flex items-center justify-between border-b border-[#f1f5f9]">
        <div className="flex items-center gap-2">
          <Building2 className="w-4 h-4 text-[#2563eb]" />
          <h2 className="text-sm font-bold text-[#0f172a]">Project Overview</h2>
        </div>
        <button
          className="p-1 rounded-md text-[#94a3b8] hover:text-[#0f172a] hover:bg-slate-100 transition-colors cursor-pointer"
          aria-label="More"
        >
          <MoreHorizontal className="w-4 h-4" />
        </button>
      </div>

      <div className="relative h-40 bg-slate-100">
        <Image
          src="/thumbnails/card1_mep.png"
          alt="Sector 4 MEP Room thumbnail"
          fill
          className="object-cover"
        />
        <span className="absolute top-2 left-2 inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-white/95 text-[#2563eb] shadow-sm">
          <Sparkles className="w-3 h-3" /> 3DGS
        </span>
      </div>

      <div className="px-4 py-3 flex items-start justify-between gap-2 border-b border-[#f1f5f9]">
        <div className="min-w-0">
          <p className="text-[13px] font-bold text-[#0f172a] truncate">
            Sector 4 MEP Room
          </p>
          <p className="text-[11px] text-[#64748b]">Floor 3 · Block B · 847 m²</p>
        </div>
        <Link
          href={projectHref}
          className="p-1.5 rounded-lg bg-blue-50 text-[#2563eb] hover:bg-blue-100 transition-colors cursor-pointer"
          aria-label="Open project"
        >
          <ChevronRight className="w-4 h-4" />
        </Link>
      </div>

      {/* Verification progress */}
      <div className="px-4 py-3 space-y-2 border-b border-[#f1f5f9]">
        <div className="flex items-center justify-between">
          <span className="text-[11px] font-bold text-[#065f46]">
            Verification Progress
          </span>
          <span className="text-[11px] font-mono font-bold text-[#0f172a]">
            74%
          </span>
        </div>
        <div className="h-1.5 rounded-full bg-slate-100 overflow-hidden">
          <div
            className="h-full rounded-full bg-gradient-to-r from-[#10b981] to-[#059669]"
            style={{ width: "74%" }}
          />
        </div>
      </div>

      {/* Scan trio */}
      <div className="grid grid-cols-3 divide-x divide-[#f1f5f9]">
        <ScanStat label="Total Scans" value="6" />
        <ScanStat label="Processed" value="4" />
        <ScanStat label="Pending" value="2" />
      </div>
    </section>

    {/* Computer Vision Pipeline */}
    <section className="rounded-2xl bg-white border border-[#e2e8f0] shadow-sm">
      <div className="px-4 py-3 flex items-center gap-2 border-b border-[#f1f5f9]">
        <span className="relative flex w-2 h-2">
          <span className="absolute inline-flex w-full h-full rounded-full bg-[#10b981] animate-ping opacity-75" />
          <span className="relative inline-flex w-2 h-2 rounded-full bg-[#10b981]" />
        </span>
        <h2 className="text-sm font-bold text-[#0f172a]">Computer Vision Pipeline</h2>
      </div>
      <ul className="p-2 space-y-0.5">
        {PIPELINE.map((step) => (
          <PipelineRow key={step.id} step={step} />
        ))}
      </ul>
    </section>

    {/* Quick Stats */}
    <section className="rounded-2xl bg-white border border-[#e2e8f0] shadow-sm">
      <div className="px-4 py-3 flex items-center gap-2 border-b border-[#f1f5f9]">
        <Gauge className="w-4 h-4 text-[#2563eb]" />
        <h2 className="text-sm font-bold text-[#0f172a]">Quick Stats</h2>
      </div>
      <div className="p-3 grid grid-cols-2 gap-2">
        {QUICK_STATS.map((stat) => (
          <QuickStatCard key={stat.label} stat={stat} />
        ))}
      </div>
    </section>
  </aside>
);

/* ------------------------ pieces ------------------------ */

const ScanStat: React.FC<{ label: string; value: string }> = ({ label, value }) => (
  <div className="flex flex-col items-center justify-center py-3">
    <span className="text-[10px] text-[#64748b] mb-1">{label}</span>
    <span className="text-lg font-extrabold text-[#0f172a] font-mono">{value}</span>
  </div>
);

const PipelineRow: React.FC<{ step: PipelineStep }> = ({ step }) => {
  const { Icon } = step;
  const isComplete = step.status === "complete";
  const isInProgress = step.status === "in_progress";
  const isPending = step.status === "pending";

  return (
    <li className="flex items-center gap-2.5 px-2 py-2 rounded-lg hover:bg-slate-50 transition-colors">
      <span
        className={`w-7 h-7 rounded-lg flex items-center justify-center shrink-0 ${
          isComplete
            ? "bg-emerald-50 text-[#059669]"
            : isInProgress
            ? "bg-amber-50 text-[#d97706]"
            : "bg-slate-100 text-[#94a3b8]"
        }`}
      >
        <Icon className="w-3.5 h-3.5" />
      </span>
      <span className="flex-1 text-[12px] font-bold text-[#0f172a]">
        {step.label}
      </span>
      {isComplete && (
        <span className="inline-flex items-center gap-1 text-[10px] font-bold text-[#059669]">
          Completed
          <span className="w-4 h-4 rounded-full bg-emerald-100 flex items-center justify-center">
            <Check className="w-2.5 h-2.5" />
          </span>
        </span>
      )}
      {isInProgress && (
        <span className="inline-flex items-center gap-1 text-[10px] font-bold text-[#d97706]">
          In Progress
          <span className="w-4 h-4 rounded-full border-2 border-amber-300 border-t-transparent animate-spin" />
        </span>
      )}
      {isPending && (
        <span className="inline-flex items-center gap-1 text-[10px] font-bold text-[#94a3b8]">
          Pending
          <Clock className="w-3 h-3" />
        </span>
      )}
    </li>
  );
};

const QuickStatCard: React.FC<{ stat: QuickStat }> = ({ stat }) => {
  const { Icon } = stat;
  return (
    <div className="flex items-center gap-2 p-2.5 rounded-xl bg-slate-50 border border-[#f1f5f9]">
      <span className="w-8 h-8 rounded-lg bg-white flex items-center justify-center text-[#2563eb] border border-blue-100 shrink-0">
        <Icon className="w-3.5 h-3.5" />
      </span>
      <div className="min-w-0">
        <p className="text-[10px] text-[#64748b] leading-tight">{stat.label}</p>
        <p className="text-[13px] font-extrabold font-mono text-[#0f172a] leading-tight">
          {stat.value}
        </p>
      </div>
    </div>
  );
};
