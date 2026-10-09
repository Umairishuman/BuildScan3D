"use client";

import React from "react";
import Link from "next/link";
import {
  AlertTriangle,
  Archive,
  ArrowRight,
  Bell,
  CheckCircle2,
  ChevronRight,
  Circle,
  Clock,
  Cpu,
  MessageSquare,
  Ruler,
  Sparkles,
} from "lucide-react";
import {
  MOCK_NOTIFICATIONS,
  MOCK_PIPELINE_STEPS,
  NotificationItem,
  NotificationKind,
  PipelineStep,
} from "@/lib/mockData";

interface KindStyle {
  Icon: React.ComponentType<{ className?: string }>;
  bg: string;
  fg: string;
}

const KIND_STYLES: Record<NotificationKind, KindStyle> = {
  scan_processing: { Icon: Clock, bg: "bg-amber-50", fg: "text-[#d97706]" },
  scan_completed: { Icon: CheckCircle2, bg: "bg-emerald-50", fg: "text-[#059669]" },
  scan_failed: { Icon: AlertTriangle, bg: "bg-red-50", fg: "text-[#dc2626]" },
  measurement_added: { Icon: Ruler, bg: "bg-blue-50", fg: "text-[#2563eb]" },
  comment: { Icon: MessageSquare, bg: "bg-slate-100", fg: "text-[#475569]" },
  project_archived: { Icon: Archive, bg: "bg-slate-100", fg: "text-[#475569]" },
};

export const ActivityColumn: React.FC = () => (
  <aside className="w-full lg:w-[360px] shrink-0 flex flex-col gap-3">
    <ActivityFeed items={MOCK_NOTIFICATIONS.slice(0, 5)} />
    <WorkerStatusCard steps={MOCK_PIPELINE_STEPS} />
  </aside>
);

/* ---------------------------- Activity ---------------------------- */

const ActivityFeed: React.FC<{ items: NotificationItem[] }> = ({ items }) => (
  <section className="rounded-2xl bg-white border border-[#e2e8f0] shadow-sm overflow-hidden flex flex-col">
    <div className="px-4 py-3 flex items-center justify-between border-b border-[#f1f5f9] shrink-0">
      <div className="flex items-center gap-2">
        <Bell className="w-4 h-4 text-[#2563eb]" />
        <h2 className="text-sm font-bold text-[#0f172a]">Recent Activity</h2>
      </div>
      <button
        type="button"
        className="inline-flex items-center gap-1 text-[11px] font-bold text-[#2563eb] hover:text-[#1d4ed8] cursor-pointer"
      >
        View all <ArrowRight className="w-3 h-3" />
      </button>
    </div>
    <ul className="p-2 space-y-0.5">
      {items.map((item) => (
        <ActivityRow key={item.id} item={item} />
      ))}
    </ul>
  </section>
);

const ActivityRow: React.FC<{ item: NotificationItem }> = ({ item }) => {
  const style = KIND_STYLES[item.kind];
  const { Icon } = style;
  return (
    <li className="flex items-start gap-2.5 p-2.5 rounded-xl hover:bg-slate-50 transition-colors">
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
      {item.unread && (
        <span
          className="mt-1 w-1.5 h-1.5 rounded-full bg-[#2563eb] shrink-0"
          aria-label="Unread"
        />
      )}
    </li>
  );
};

/* ---------------------------- Worker Status ---------------------------- */

const WorkerStatusCard: React.FC<{ steps: PipelineStep[] }> = ({ steps }) => {
  const inProgress = steps.find((s) => s.status === "in_progress");
  const completed = steps.filter((s) => s.status === "complete").length;

  return (
    <section className="rounded-2xl bg-white border border-[#e2e8f0] shadow-sm overflow-hidden">
      <div className="px-4 py-3 flex items-center justify-between border-b border-[#f1f5f9]">
        <div className="flex items-center gap-2">
          <span className="relative flex w-2 h-2">
            <span className="absolute inline-flex w-full h-full rounded-full bg-[#10b981] animate-ping opacity-75" />
            <span className="relative inline-flex w-2 h-2 rounded-full bg-[#10b981]" />
          </span>
          <h2 className="text-sm font-bold text-[#0f172a]">Worker Status</h2>
        </div>
        <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-50 text-[#059669] border border-emerald-100">
          Online
        </span>
      </div>

      <div className="p-3 space-y-3">
        {/* Worker identity */}
        <div className="flex items-center gap-3 p-2.5 rounded-xl bg-gradient-to-br from-[#0f172a] to-[#1e293b] text-white">
          <span className="w-9 h-9 rounded-lg bg-white/10 flex items-center justify-center shrink-0">
            <Cpu className="w-4 h-4 text-[#38bdf8]" />
          </span>
          <div className="flex-1 min-w-0">
            <p className="text-[11px] font-bold">BuildScan Edge Worker</p>
            <p className="text-[10px] text-white/70 font-mono">
              NVIDIA RTX 4090 · 24 GB VRAM
            </p>
          </div>
          <span className="text-[10px] font-mono font-bold text-[#38bdf8]">
            {completed}/{steps.length}
          </span>
        </div>

        {/* Current step */}
        {inProgress && (
          <div className="space-y-1.5">
            <div className="flex items-center justify-between text-[11px]">
              <span className="font-bold text-[#0f172a]">{inProgress.title}</span>
              <span className="font-mono font-bold text-[#d97706]">
                {inProgress.progress ?? 0}%
              </span>
            </div>
            <div className="h-1.5 rounded-full bg-slate-100 overflow-hidden">
              <div
                className="h-full rounded-full bg-gradient-to-r from-[#f59e0b] to-[#d97706] transition-all"
                style={{ width: `${inProgress.progress ?? 0}%` }}
              />
            </div>
            <p className="text-[10px] text-[#94a3b8]">{inProgress.details}</p>
          </div>
        )}

        {/* Queue */}
        <div className="pt-1 border-t border-[#f1f5f9]">
          <p className="text-[10px] font-bold uppercase tracking-wider text-[#94a3b8] mb-1.5">
            Queue
          </p>
          <ul className="space-y-1">
            {steps.map((step) => (
              <QueueRow key={step.id} step={step} />
            ))}
          </ul>
        </div>

        <Link
          href="/viewer/sector-4-mep"
          className="inline-flex items-center justify-center gap-1 w-full py-1.5 rounded-lg text-[11px] font-bold text-[#2563eb] hover:bg-blue-50 transition-colors cursor-pointer"
        >
          Open live scan <ChevronRight className="w-3 h-3" />
        </Link>
      </div>
    </section>
  );
};

const QueueRow: React.FC<{ step: PipelineStep }> = ({ step }) => {
  const isComplete = step.status === "complete";
  const isInProgress = step.status === "in_progress";
  return (
    <li className="flex items-center gap-2 text-[10px]">
      <span className="w-4 flex items-center justify-center shrink-0">
        {isComplete ? (
          <CheckCircle2 className="w-3 h-3 text-[#059669]" />
        ) : isInProgress ? (
          <Sparkles className="w-3 h-3 text-[#d97706] animate-pulse" />
        ) : (
          <Circle className="w-3 h-3 text-[#cbd5e1]" />
        )}
      </span>
      <span
        className={`flex-1 truncate font-semibold ${
          isComplete
            ? "text-[#64748b] line-through decoration-[#cbd5e1]"
            : isInProgress
            ? "text-[#0f172a]"
            : "text-[#94a3b8]"
        }`}
      >
        {step.title}
      </span>
      {step.duration && (
        <span className="font-mono text-[#94a3b8]">{step.duration.split(" ")[0]}</span>
      )}
    </li>
  );
};
