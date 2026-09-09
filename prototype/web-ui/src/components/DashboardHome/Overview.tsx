"use client";

import React from "react";
import Image from "next/image";
import Link from "next/link";
import {
  ArrowRight,
  Box,
  Calendar,
  CheckCircle2,
  ChevronRight,
  Flag,
  FolderKanban,
  Loader2,
  Map,
  Play,
  Plus,
} from "lucide-react";
import {
  MOCK_CHANGE_LOG,
  MOCK_PROJECTS,
  Project,
} from "@/lib/mockData";

const STATUS_STYLES: Record<
  Project["status"],
  { bg: string; fg: string; dot: string; label: string }
> = {
  ready: { bg: "bg-emerald-50", fg: "text-[#065f46]", dot: "bg-[#10b981]", label: "Ready" },
  processing: { bg: "bg-amber-50", fg: "text-[#92400e]", dot: "bg-[#f59e0b]", label: "Processing" },
  complete: { bg: "bg-teal-50", fg: "text-[#115e59]", dot: "bg-[#14b8a6]", label: "Complete" },
  draft: { bg: "bg-slate-100", fg: "text-[#334155]", dot: "bg-[#94a3b8]", label: "Draft" },
  archived: { bg: "bg-slate-100", fg: "text-[#475569]", dot: "bg-[#64748b]", label: "Archived" },
};

interface OverviewProps {
  onQuickCapture: () => void;
}

export const DashboardOverview: React.FC<OverviewProps> = ({ onQuickCapture }) => {
  const total = MOCK_PROJECTS.length;
  const active = MOCK_PROJECTS.filter((p) => p.status === "processing").length;
  const ready = MOCK_PROJECTS.filter(
    (p) => p.status === "ready" || p.status === "complete"
  ).length;
  const flagged = MOCK_CHANGE_LOG.filter((c) => c.flagged).length;

  const featured =
    MOCK_PROJECTS.find((p) => p.status === "processing") ?? MOCK_PROJECTS[0];
  const recentProjects = MOCK_PROJECTS.filter((p) => p.id !== featured.id).slice(
    0,
    3
  );

  return (
    <div className="space-y-4">
      {/* Page title */}
      <div className="flex items-end justify-between gap-3">
        <div>
          <h1 className="text-xl font-extrabold text-[#0f172a] tracking-tight">
            Operations Overview
          </h1>
          <p className="text-[11px] text-[#64748b] mt-0.5">
            Everything running across your BuildScan workspace, at a glance.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Link
            href="/projects"
            className="hidden sm:inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-[#e2e8f0] bg-white text-[11px] font-bold text-[#0f172a] hover:bg-slate-50 shadow-sm cursor-pointer"
          >
            <FolderKanban className="w-3.5 h-3.5" />
            All Projects
          </Link>
          <button
            onClick={onQuickCapture}
            className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-[#2563eb] hover:bg-[#1d4ed8] text-white text-[11px] font-bold shadow-sm cursor-pointer"
          >
            <Plus className="w-3.5 h-3.5" />
            New Capture
          </button>
        </div>
      </div>

      {/* KPI row */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <KpiCard
          label="Total Projects"
          value={String(total)}
          Icon={FolderKanban}
          tone="blue"
          delta="+2 this month"
        />
        <KpiCard
          label="Active Scans"
          value={String(active)}
          Icon={Loader2}
          tone="amber"
          delta={`${active === 0 ? "Idle" : "Training on RTX 4090"}`}
          animated
        />
        <KpiCard
          label="Ready Models"
          value={String(ready)}
          Icon={CheckCircle2}
          tone="emerald"
          delta="Available for review"
        />
        <KpiCard
          label="Flagged Issues"
          value={String(flagged)}
          Icon={Flag}
          tone="rose"
          delta={flagged === 0 ? "Nothing to escalate" : "Needs coordinator sign-off"}
        />
      </div>

      {/* Featured active + quick actions */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-3">
        <div className="lg:col-span-2">
          <FeaturedActiveCard project={featured} />
        </div>
        <QuickActionsCard onNewCapture={onQuickCapture} />
      </div>

      {/* Recent projects strip */}
      <section className="rounded-2xl bg-white border border-[#e2e8f0] shadow-sm">
        <div className="px-4 py-3 flex items-center justify-between border-b border-[#f1f5f9]">
          <div>
            <h2 className="text-sm font-bold text-[#0f172a]">Recent Projects</h2>
            <p className="text-[10px] text-[#64748b] mt-0.5">
              Latest captures across your portfolio
            </p>
          </div>
          <Link
            href="/projects"
            className="inline-flex items-center gap-1 text-[11px] font-bold text-[#2563eb] hover:text-[#1d4ed8] cursor-pointer"
          >
            View all projects <ArrowRight className="w-3 h-3" />
          </Link>
        </div>
        <div className="p-3 grid grid-cols-1 md:grid-cols-3 gap-3">
          {recentProjects.map((project) => (
            <MiniProjectCard key={project.id} project={project} />
          ))}
        </div>
      </section>
    </div>
  );
};

/* ---------------------------- KPI ---------------------------- */

type Tone = "blue" | "amber" | "emerald" | "rose";

const TONE_STYLES: Record<Tone, { chip: string; iconBg: string; iconFg: string }> = {
  blue: {
    chip: "text-[#2563eb]",
    iconBg: "bg-blue-50",
    iconFg: "text-[#2563eb]",
  },
  amber: {
    chip: "text-[#d97706]",
    iconBg: "bg-amber-50",
    iconFg: "text-[#d97706]",
  },
  emerald: {
    chip: "text-[#059669]",
    iconBg: "bg-emerald-50",
    iconFg: "text-[#059669]",
  },
  rose: {
    chip: "text-[#dc2626]",
    iconBg: "bg-red-50",
    iconFg: "text-[#dc2626]",
  },
};

const KpiCard: React.FC<{
  label: string;
  value: string;
  Icon: React.ComponentType<{ className?: string }>;
  tone: Tone;
  delta: string;
  animated?: boolean;
}> = ({ label, value, Icon, tone, delta, animated }) => {
  const t = TONE_STYLES[tone];
  return (
    <div className="p-4 rounded-2xl bg-white border border-[#e2e8f0] shadow-sm">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-[10px] font-bold uppercase tracking-wider text-[#94a3b8]">
            {label}
          </p>
          <p className="mt-1 text-2xl font-extrabold text-[#0f172a] font-mono tabular-nums leading-none">
            {value}
          </p>
        </div>
        <span
          className={`w-9 h-9 rounded-xl flex items-center justify-center ${t.iconBg} ${t.iconFg}`}
        >
          <Icon className={`w-4 h-4 ${animated ? "animate-spin [animation-duration:3s]" : ""}`} />
        </span>
      </div>
      <p className={`text-[10px] font-bold mt-3 ${t.chip}`}>{delta}</p>
    </div>
  );
};

/* ------------------- Featured active card ------------------- */

const FeaturedActiveCard: React.FC<{ project: Project }> = ({ project }) => {
  const status = STATUS_STYLES[project.status];
  const isProcessing = project.status === "processing";

  return (
    <div className="relative h-full rounded-2xl bg-white border border-[#e2e8f0] shadow-sm overflow-hidden">
      <div className="grid grid-cols-1 sm:grid-cols-[1.15fr_1fr] h-full">
        {/* Hero panel */}
        <div className="relative min-h-[220px] bg-[#f8fafc]">
          <Image
            src="/images/dashboard background.png"
            alt={`${project.name} render`}
            fill
            className="object-contain object-center"
          />
          <span
            className={`absolute top-3 left-3 inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-bold border ${status.bg} ${status.fg}`}
            style={{ borderColor: "rgba(15,23,42,0.05)" }}
          >
            <span className={`w-1.5 h-1.5 rounded-full ${status.dot} ${isProcessing ? "animate-pulse" : ""}`} />
            {status.label}
          </span>
        </div>

        {/* Meta panel */}
        <div className="p-4 flex flex-col gap-3">
          <div>
            <p className="text-[10px] font-bold uppercase tracking-wider text-[#94a3b8]">
              {isProcessing ? "Active Now" : "Featured Project"}
            </p>
            <h3 className="mt-1 text-base font-extrabold text-[#0f172a] leading-tight">
              {project.name}
            </h3>
            <p className="text-[11px] text-[#64748b] mt-1">
              {project.floor} · {project.block} · {project.area}
            </p>
          </div>

          {/* Progress mini strip (fake but grounded in fixture) */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between text-[10px]">
              <span className="font-bold text-[#0f172a]">3DGS Training</span>
              <span className="font-mono font-bold text-[#d97706]">68%</span>
            </div>
            <div className="h-1.5 rounded-full bg-slate-100 overflow-hidden">
              <div
                className="h-full rounded-full bg-gradient-to-r from-[#f59e0b] to-[#d97706]"
                style={{ width: "68%" }}
              />
            </div>
            <p className="text-[10px] text-[#94a3b8]">
              Step 4 of 6 · Iter 20,400 / 30,000 · PSNR 29.4 dB
            </p>
          </div>

          {/* Stats trio */}
          <div className="grid grid-cols-3 gap-2 pt-1">
            <MetaStat label="Scans" value={String(project.scansCount)} />
            <MetaStat label="Accuracy" value={project.accuracy ?? "—"} mono />
            <MetaStat
              label="Gaussians"
              value={project.gaussianCount ? formatShort(project.gaussianCount) : "—"}
              mono
            />
          </div>

          {/* CTAs */}
          <div className="mt-auto flex items-center gap-2 pt-2">
            <Link
              href={`/viewer/${project.id}`}
              className="flex-1 inline-flex items-center justify-center gap-1.5 px-3 py-2 rounded-xl bg-[#2563eb] hover:bg-[#1d4ed8] text-white text-[11px] font-bold shadow-sm cursor-pointer"
            >
              <Box className="w-3.5 h-3.5" />
              Open 3D
            </Link>
            <Link
              href={`/floorplan/tower-a-floors-5-8`}
              className="inline-flex items-center gap-1.5 px-3 py-2 rounded-xl border border-[#e2e8f0] bg-white text-[11px] font-bold text-[#0f172a] hover:bg-slate-50 cursor-pointer"
            >
              <Map className="w-3.5 h-3.5" />
              Plans
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

const MetaStat: React.FC<{ label: string; value: string; mono?: boolean }> = ({
  label,
  value,
  mono,
}) => (
  <div className="p-2 rounded-lg bg-slate-50 border border-[#f1f5f9]">
    <p className="text-[9px] text-[#94a3b8] uppercase tracking-wider">{label}</p>
    <p
      className={`text-[12px] font-extrabold text-[#0f172a] leading-tight ${
        mono ? "font-mono" : ""
      }`}
    >
      {value}
    </p>
  </div>
);

const formatShort = (n: string) => {
  const num = Number(n.replace(/,/g, ""));
  if (isNaN(num)) return n;
  if (num >= 1_000_000) return `${(num / 1_000_000).toFixed(2)}M`;
  if (num >= 1_000) return `${(num / 1_000).toFixed(0)}K`;
  return String(num);
};

/* ------------------- Quick actions ------------------- */

const QuickActionsCard: React.FC<{ onNewCapture: () => void }> = ({
  onNewCapture,
}) => (
  <div className="p-4 rounded-2xl bg-gradient-to-br from-[#2563eb] to-[#1d4ed8] text-white shadow-sm flex flex-col">
    <div>
      <p className="text-[10px] font-bold uppercase tracking-wider text-white/70">
        Quick Actions
      </p>
      <h3 className="mt-1 text-base font-extrabold">Jump into work</h3>
    </div>

    <div className="mt-3 space-y-1.5">
      <QuickAction
        Icon={Plus}
        label="New Capture"
        subtitle="Kick off from the mobile app"
        onClick={onNewCapture}
      />
      <QuickAction
        Icon={Map}
        label="Open Floor Plan"
        subtitle="Tower A · Floors 5-8"
        href="/floorplan/tower-a-floors-5-8"
      />
      <QuickAction
        Icon={Play}
        label="Review Latest Scan"
        subtitle="Sector 4 MEP Room"
        href="/viewer/sector-4-mep"
      />
    </div>
  </div>
);

const QuickAction: React.FC<{
  Icon: React.ComponentType<{ className?: string }>;
  label: string;
  subtitle: string;
  href?: string;
  onClick?: () => void;
}> = ({ Icon, label, subtitle, href, onClick }) => {
  const body = (
    <div className="w-full flex items-center gap-3 p-2.5 rounded-xl bg-white/10 hover:bg-white/20 transition-colors cursor-pointer">
      <span className="w-8 h-8 rounded-lg bg-white/15 flex items-center justify-center">
        <Icon className="w-4 h-4" />
      </span>
      <div className="flex-1 min-w-0 text-left">
        <p className="text-[12px] font-bold leading-tight">{label}</p>
        <p className="text-[10px] text-white/70 leading-tight">{subtitle}</p>
      </div>
      <ChevronRight className="w-4 h-4 text-white/70" />
    </div>
  );

  if (href) return <Link href={href}>{body}</Link>;
  return (
    <button type="button" onClick={onClick} className="w-full">
      {body}
    </button>
  );
};

/* ------------------- Mini project card ------------------- */

const MiniProjectCard: React.FC<{ project: Project }> = ({ project }) => {
  const status = STATUS_STYLES[project.status];
  const isProcessing = project.status === "processing";
  const canOpen = project.status === "ready" || project.status === "complete";
  const href = canOpen ? `/viewer/${project.id}` : `/projects`;

  const cardClass = `group rounded-xl border border-[#e2e8f0] bg-white overflow-hidden ${
    canOpen
      ? "hover:border-[#cbd5e1] hover:shadow-md transition-all cursor-pointer"
      : ""
  }`;

  const body = (
    <>
      <div className="relative h-24 bg-slate-100">
        <Image
          src={project.thumbnail}
          alt={project.name}
          fill
          className="object-cover group-hover:scale-105 transition-transform duration-300"
        />
        <span
          className={`absolute bottom-2 left-2 inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[9px] font-bold border ${status.bg} ${status.fg}`}
          style={{ borderColor: "rgba(15,23,42,0.05)" }}
        >
          <span
            className={`w-1 h-1 rounded-full ${status.dot} ${
              isProcessing ? "animate-pulse" : ""
            }`}
          />
          {status.label}
        </span>
      </div>
      <div className="p-3 space-y-1">
        <p className="text-[12px] font-bold text-[#0f172a] truncate">
          {project.name}
        </p>
        <p className="text-[10px] text-[#64748b]">
          {project.floor} · {project.block} · {project.area}
        </p>
        <div className="flex items-center gap-2 pt-1 text-[10px] text-[#94a3b8]">
          <Calendar className="w-3 h-3" />
          <span>{project.dateCaptured}</span>
          <span>·</span>
          <span>{project.scansCount} scans</span>
        </div>
      </div>
    </>
  );

  if (canOpen) {
    return (
      <Link href={href} className={cardClass}>
        {body}
      </Link>
    );
  }
  return <div className={cardClass}>{body}</div>;
};
