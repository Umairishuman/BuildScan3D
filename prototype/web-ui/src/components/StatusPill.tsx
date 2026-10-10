"use client";

import React from "react";
import { Project } from "@/lib/mockData";

type Status = Project["status"];

/** Dot + tinted background per the design system's status colours. */
const STATUS_STYLES: Record<Status, { dot: string; pill: string; label: string }> = {
  ready: {
    dot: "bg-[#10b981]",
    pill: "bg-[#ecfdf5] text-[#065f46] border-emerald-200",
    label: "Ready",
  },
  processing: {
    dot: "bg-[#f59e0b]",
    pill: "bg-[#fffbeb] text-[#b45309] border-amber-200",
    label: "Processing",
  },
  complete: {
    dot: "bg-[#14b8a6]",
    pill: "bg-[#f0fdfa] text-[#115e59] border-teal-200",
    label: "Complete",
  },
  draft: {
    dot: "bg-[#94a3b8]",
    pill: "bg-[#f3f4f6] text-[#475569] border-slate-200",
    label: "Draft",
  },
  archived: {
    dot: "bg-slate-500",
    pill: "bg-[#f1f5f9] text-[#334155] border-slate-300",
    label: "Archived",
  },
};

interface StatusPillProps {
  status: Status;
  /** Override the default label, e.g. a project's own statusLabel. */
  label?: string;
  size?: "sm" | "md";
  /** Pulse the dot — used for work still in flight. */
  animated?: boolean;
}

export const StatusPill: React.FC<StatusPillProps> = ({
  status,
  label,
  size = "md",
  animated = false,
}) => {
  const style = STATUS_STYLES[status];
  const shouldPulse = animated && status === "processing";

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border font-bold ${
        style.pill
      } ${size === "sm" ? "px-2 py-0.5 text-[10px]" : "px-2.5 py-1 text-[11px]"}`}
    >
      <span
        className={`w-1.5 h-1.5 rounded-full ${style.dot} ${
          shouldPulse ? "animate-pulse" : ""
        }`}
      />
      {label ?? style.label}
    </span>
  );
};
