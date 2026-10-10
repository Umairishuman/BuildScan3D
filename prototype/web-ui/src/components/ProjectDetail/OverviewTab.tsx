"use client";

import React from "react";
import Image from "next/image";
import {
  Activity,
  AlertTriangle,
  Archive,
  Box,
  Calendar,
  CheckCircle2,
  Clock,
  Flag,
  Layers,
  MessageSquare,
  Ruler,
  Sparkles,
} from "lucide-react";
import {
  MOCK_CHANGE_LOG,
  MOCK_NOTIFICATIONS,
  NotificationItem,
  NotificationKind,
  Project,
} from "@/lib/mockData";

interface OverviewTabProps {
  project: Project;
}

interface StatCard {
  label: string;
  value: string;
  hint: string;
  Icon: React.ComponentType<{ className?: string }>;
  tone: "blue" | "amber" | "emerald" | "rose";
}

interface LayerRow {
  key: string;
  label: string;
  count: number;
  color: string;
}

const LAYER_SUMMARY: LayerRow[] = [
  { key: "plumbing", label: "Plumbing", count: 12, color: "#0369a1" },
  { key: "electrical", label: "Electrical Conduits", count: 18, color: "#d97706" },
  { key: "hvac", label: "HVAC Ductwork", count: 4, color: "#059669" },
  { key: "fire", label: "Fire Protection", count: 8, color: "#dc2626" },
  { key: "structural", label: "Structural", count: 26, color: "#94a3b8" },
];

const TONE_STYLES: Record<StatCard["tone"], { bg: string; fg: string }> = {
  blue: { bg: "bg-blue-50", fg: "text-[#2563eb]" },
  amber: { bg: "bg-amber-50", fg: "text-[#d97706]" },
  emerald: { bg: "bg-emerald-50", fg: "text-[#059669]" },
  rose: { bg: "bg-red-50", fg: "text-[#dc2626]" },
};

const NOTIF_STYLES: Record<
  NotificationKind,
  { Icon: React.ComponentType<{ className?: string }>; bg: string; fg: string }
> = {
  scan_processing: { Icon: Clock, bg: "bg-amber-50", fg: "text-[#d97706]" },
  scan_completed: { Icon: CheckCircle2, bg: "bg-emerald-50", fg: "text-[#059669]" },
  scan_failed: { Icon: AlertTriangle, bg: "bg-red-50", fg: "text-[#dc2626]" },
  measurement_added: { Icon: Ruler, bg: "bg-blue-50", fg: "text-[#2563eb]" },
  comment: { Icon: MessageSquare, bg: "bg-slate-100", fg: "text-[#475569]" },
  project_archived: { Icon: Archive, bg: "bg-slate-100", fg: "text-[#475569]" },
};

export const OverviewTab: React.FC<OverviewTabProps> = ({ project }) => {
  const flagged = MOCK_CHANGE_LOG.filter((c) => c.flagged).length;
  const totalLayerElements = LAYER_SUMMARY.reduce((acc, l) => acc + l.count, 0);
  const activity = MOCK_NOTIFICATIONS.slice(0, 4);

  const stats: StatCard[] = [
    { label: "Total Area", value: project.area, hint: `${project.floor} · ${project.block}`, Icon: Ruler, tone: "blue" },
    { label: "Scan Count", value: String(project.scansCount), hint: "Captured with ARCore 120 Hz", Icon: Box, tone: "emerald" },
    { label: "Last Updated", value: project.dateCaptured, hint: `Accuracy ${project.accuracy ?? "±1.2 mm"}`, Icon: Calendar, tone: "amber" },
    { label: "Flagged Issues", value: String(flagged), hint: flagged === 0 ? "Nothing to escalate" : "Needs coordinator sign-off", Icon: Flag, tone: "rose" },
  ];

  return (
    <div className="flex-1 min-h-0 overflow-y-auto p-5 space-y-4 bg-[#eef3f9]">
      {/* Stat cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        {stats.map((s) => (
          <StatCardView key={s.label} card={s} />
        ))}
      </div>

      {/* 3D thumbnail + Layer Summary side-by-side */}
      <div className="grid grid-cols-1 lg:grid-cols-[1.4fr_1fr] gap-3">
        <ScanPreviewCard project={project} />
        <LayerSummaryCard total={totalLayerElements} />
      </div>

      {/* Recent activity */}
      <RecentActivityCard items={activity} projectName={project.name} />
    </div>
  );
};

/* --------------------------- Sub-components --------------------------- */

const StatCardView: React.FC<{ card: StatCard }> = ({ card }) => {
  const tone = TONE_STYLES[card.tone];
  const { Icon } = card;
  return (
    <div className="p-4 rounded-2xl bg-white border border-[#e2e8f0] shadow-sm">
      <div className="flex items-start justify-between">
        <div className="min-w-0">
          <p className="text-[10px] font-bold uppercase tracking-wider text-[#94a3b8]">
            {card.label}
          </p>
          <p className="mt-1 text-xl font-extrabold text-[#0f172a] font-mono tabular-nums leading-tight">
            {card.value}
          </p>
        </div>
        <span
          className={`w-8 h-8 rounded-xl flex items-center justify-center shrink-0 ${tone.bg} ${tone.fg}`}
        >
          <Icon className="w-4 h-4" />
        </span>
      </div>
      <p className="text-[10px] text-[#64748b] mt-2 truncate">{card.hint}</p>
    </div>
  );
};

const ScanPreviewCard: React.FC<{ project: Project }> = ({ project }) => (
  <section className="rounded-2xl bg-white border border-[#e2e8f0] shadow-sm overflow-hidden">
    <div className="px-4 py-3 flex items-center justify-between border-b border-[#f1f5f9]">
      <div className="flex items-center gap-2">
        <Box className="w-4 h-4 text-[#2563eb]" />
        <h3 className="text-sm font-bold text-[#0f172a]">3D Preview</h3>
      </div>
      <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-blue-50 text-[#2563eb] border border-blue-100">
        3DGS · {project.gaussianCount ?? "—"} splats
      </span>
    </div>
    <div className="relative h-64 bg-[#eef3f9]">
      <Image
        src="/images/dashboard background.png"
        alt={`${project.name} isometric render`}
        fill
        className="object-contain object-center"
      />
      <div className="absolute bottom-3 left-3 flex items-center gap-2 px-2.5 py-1.5 rounded-xl bg-white/95 backdrop-blur-md border border-[#e2e8f0] shadow-sm">
        <Sparkles className="w-3.5 h-3.5 text-[#2563eb]" />
        <span className="text-[10px] font-bold text-[#0f172a]">
          Textured render · 60 FPS
        </span>
      </div>
    </div>
  </section>
);

const LayerSummaryCard: React.FC<{ total: number }> = ({ total }) => (
  <section className="rounded-2xl bg-white border border-[#e2e8f0] shadow-sm">
    <div className="px-4 py-3 flex items-center justify-between border-b border-[#f1f5f9]">
      <div className="flex items-center gap-2">
        <Layers className="w-4 h-4 text-[#2563eb]" />
        <h3 className="text-sm font-bold text-[#0f172a]">Layer Summary</h3>
      </div>
      <span className="text-[10px] font-mono font-bold text-[#0f172a]">
        {total} elements
      </span>
    </div>
    <ul className="p-3 space-y-1.5">
      {LAYER_SUMMARY.map((layer) => {
        const pct = Math.round((layer.count / total) * 100);
        return (
          <li key={layer.key} className="space-y-1">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 min-w-0">
                <span
                  className="w-2 h-2 rounded-full shrink-0"
                  style={{ backgroundColor: layer.color }}
                />
                <span className="text-[11px] font-bold text-[#0f172a] truncate">
                  {layer.label}
                </span>
              </div>
              <span className="text-[11px] font-mono font-bold text-[#0f172a]">
                {layer.count}
              </span>
            </div>
            <div className="h-1 rounded-full bg-slate-100 overflow-hidden">
              <div
                className="h-full rounded-full"
                style={{ width: `${pct}%`, backgroundColor: layer.color }}
              />
            </div>
          </li>
        );
      })}
    </ul>
  </section>
);

const RecentActivityCard: React.FC<{
  items: NotificationItem[];
  projectName: string;
}> = ({ items, projectName }) => (
  <section className="rounded-2xl bg-white border border-[#e2e8f0] shadow-sm">
    <div className="px-4 py-3 flex items-center justify-between border-b border-[#f1f5f9]">
      <div className="flex items-center gap-2">
        <Activity className="w-4 h-4 text-[#2563eb]" />
        <h3 className="text-sm font-bold text-[#0f172a]">Recent Activity</h3>
      </div>
      <span className="text-[10px] text-[#64748b]">Scoped to {projectName}</span>
    </div>
    <ul className="p-2 space-y-0.5">
      {items.map((item) => {
        const style = NOTIF_STYLES[item.kind];
        const { Icon } = style;
        return (
          <li
            key={item.id}
            className="flex items-start gap-2.5 p-2.5 rounded-xl hover:bg-slate-50 transition-colors"
          >
            <span
              className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${style.bg} ${style.fg}`}
            >
              <Icon className="w-4 h-4" />
            </span>
            <div className="flex-1 min-w-0">
              <div className="flex items-baseline justify-between gap-2">
                <span className="text-[12px] font-bold text-[#0f172a] truncate">
                  {item.title}
                </span>
                <span className="text-[10px] text-[#94a3b8] shrink-0 whitespace-nowrap">
                  {item.timeAgo}
                </span>
              </div>
              <p className="text-[11px] text-[#64748b] leading-snug line-clamp-2">
                {item.description}
              </p>
            </div>
          </li>
        );
      })}
    </ul>
  </section>
);
