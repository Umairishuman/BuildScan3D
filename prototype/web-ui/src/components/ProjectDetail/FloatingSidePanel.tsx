"use client";

import React from "react";
import { X } from "lucide-react";

interface FloatingSidePanelProps {
  title: string;
  Icon: React.ComponentType<{ className?: string }>;
  badge?: React.ReactNode;
  onClose: () => void;
  children: React.ReactNode;
  /** Optional pill row (e.g. sub-tabs) that sits under the header. */
  header?: React.ReactNode;
  /** Optional CTA / row that sits pinned to the bottom of the panel. */
  footer?: React.ReactNode;
}

/**
 * Right-side floating popover used for Layers and Measurements now that the
 * persistent RightDock is gone. Positioned by the parent (`absolute` inside
 * the relatively-positioned viewport wrapper).
 */
export const FloatingSidePanel: React.FC<FloatingSidePanelProps> = ({
  title,
  Icon,
  badge,
  onClose,
  children,
  header,
  footer,
}) => (
  <div className="w-[320px] max-h-[calc(100vh-9rem)] rounded-2xl bg-white/95 backdrop-blur-md border border-[#e2e8f0] shadow-2xl flex flex-col overflow-hidden">
    <div className="px-4 py-3 border-b border-[#f1f5f9] flex items-center justify-between shrink-0">
      <div className="flex items-center gap-2 min-w-0">
        <Icon className="w-4 h-4 text-[#2563eb]" />
        <h2 className="text-sm font-bold text-[#0f172a] truncate">{title}</h2>
        {badge}
      </div>
      <button
        onClick={onClose}
        aria-label={`Close ${title}`}
        className="p-1.5 rounded-lg text-[#94a3b8] hover:text-[#0f172a] hover:bg-slate-100 transition-colors cursor-pointer"
      >
        <X className="w-4 h-4" />
      </button>
    </div>

    {header && <div className="p-3 shrink-0">{header}</div>}

    <div className="flex-1 min-h-0 overflow-y-auto px-3 pb-3">{children}</div>

    {footer && (
      <div className="px-3 pb-3 pt-2 border-t border-[#f1f5f9] shrink-0">
        {footer}
      </div>
    )}
  </div>
);
