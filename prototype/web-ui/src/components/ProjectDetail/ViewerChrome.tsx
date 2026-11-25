"use client";

import React, { useEffect, useRef, useState } from "react";
import Link from "next/link";
import {
  ArrowLeft,
  ChevronDown,
  Info,
  Menu,
  MoreHorizontal,
  RotateCcw,
  X,
  ZoomIn,
  ZoomOut,
} from "lucide-react";
import type { Project } from "@/lib/mockData";
import type { ViewMode } from "@/components/Viewer3D/Canvas3D";
import type { RenderMode } from "@/components/Viewer3D/SceneBuilder";

/*
 * Floating chrome for the full-window 3D viewer (2026-11-25, Tayyab: the stacked navbar + breadcrumb + project bar
 * took ~150 px above the model, and many controls were placeholders). Everything here floats over the canvas, is
 * small, and only offers controls that work for the project being shown.
 */

const CARD = "bg-white/95 backdrop-blur-md border border-[#e2e8f0] shadow-md";

/* ------------------------------ icon button ------------------------------ */

export const ChromeIconButton: React.FC<{
  Icon: React.ComponentType<{ className?: string }>;
  label: string;
  onClick?: () => void;
  href?: string;
  download?: boolean;
  active?: boolean;
  badge?: number;
}> = ({ Icon, label, onClick, href, download, active, badge }) => {
  const cls = `relative inline-flex items-center justify-center w-9 h-9 rounded-xl transition-colors cursor-pointer ${
    active ? "bg-[#2563eb] text-white shadow-md" : `${CARD} text-[#0f172a] hover:text-[#2563eb]`
  }`;
  const inner = (
    <>
      <Icon className="w-4 h-4" />
      {typeof badge === "number" && badge > 0 && (
        <span className="absolute -top-1 -right-1 min-w-[16px] h-4 px-1 rounded-full bg-[#2563eb] text-white text-[9px] font-mono font-bold flex items-center justify-center border-2 border-white">
          {badge}
        </span>
      )}
    </>
  );
  if (href) {
    return (
      <a href={href} download={download} title={label} aria-label={label} className={cls}>
        {inner}
      </a>
    );
  }
  return (
    <button onClick={onClick} title={label} aria-label={label} aria-pressed={active} className={cls}>
      {inner}
    </button>
  );
};

/* ------------------------------ title chip ------------------------------ */

export interface MoreItem {
  label: string;
  onSelect: () => void;
}

export const ViewerTitleChip: React.FC<{
  project: Project;
  backHref: string;
  onOpenMenu: () => void;
  infoOpen: boolean;
  onToggleInfo: () => void;
  moreItems?: MoreItem[];
}> = ({ project, backHref, onOpenMenu, infoOpen, onToggleInfo, moreItems }) => {
  const [moreOpen, setMoreOpen] = useState(false);
  const moreRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (!moreOpen) return;
    const close = (e: MouseEvent) => {
      if (moreRef.current && !moreRef.current.contains(e.target as Node)) setMoreOpen(false);
    };
    window.addEventListener("mousedown", close);
    return () => window.removeEventListener("mousedown", close);
  }, [moreOpen]);
  const dot =
    project.status === "ready" || project.status === "complete"
      ? "bg-[#059669]"
      : project.status === "processing"
        ? "bg-[#d97706]"
        : "bg-[#94a3b8]";
  return (
    <div className={`flex items-center gap-1 pl-1 pr-1.5 py-1 rounded-2xl ${CARD} max-w-[min(560px,calc(100vw-2rem))]`}>
      <button
        onClick={onOpenMenu}
        title="Menu"
        aria-label="Open menu"
        className="w-8 h-8 inline-flex items-center justify-center rounded-xl text-[#64748b] hover:text-[#0f172a] hover:bg-slate-100 cursor-pointer"
      >
        <Menu className="w-4 h-4" />
      </button>
      <Link
        href={backHref}
        title="All projects"
        aria-label="Back to all projects"
        className="w-8 h-8 inline-flex items-center justify-center rounded-xl text-[#64748b] hover:text-[#2563eb] hover:bg-slate-100"
      >
        <ArrowLeft className="w-4 h-4" />
      </Link>
      <span className={`w-2 h-2 rounded-full shrink-0 ${dot}`} title={project.statusLabel} />
      <h1 className="px-1.5 text-[13px] font-extrabold text-[#0f172a] tracking-tight truncate">{project.name}</h1>
      <button
        onClick={onToggleInfo}
        title="Scan details"
        aria-label="Scan details"
        aria-pressed={infoOpen}
        className={`w-8 h-8 shrink-0 inline-flex items-center justify-center rounded-xl cursor-pointer ${
          infoOpen ? "bg-blue-50 text-[#2563eb]" : "text-[#64748b] hover:text-[#0f172a] hover:bg-slate-100"
        }`}
      >
        <Info className="w-4 h-4" />
      </button>
      {moreItems && moreItems.length > 0 && (
        <div ref={moreRef} className="relative shrink-0">
          <button
            onClick={() => setMoreOpen((v) => !v)}
            title="More"
            aria-label="More sections"
            aria-expanded={moreOpen}
            className="w-8 h-8 inline-flex items-center justify-center rounded-xl text-[#64748b] hover:text-[#0f172a] hover:bg-slate-100 cursor-pointer"
          >
            <MoreHorizontal className="w-4 h-4" />
          </button>
          {moreOpen && (
            <div className={`absolute left-0 top-full mt-2 w-44 p-1 rounded-xl ${CARD} shadow-xl z-40`}>
              {moreItems.map((it) => (
                <button
                  key={it.label}
                  onClick={() => {
                    setMoreOpen(false);
                    it.onSelect();
                  }}
                  className="w-full text-left px-3 py-2 rounded-lg text-[12px] font-semibold text-[#0f172a] hover:bg-slate-50 cursor-pointer"
                >
                  {it.label}
                </button>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

/* ------------------------------ info card ------------------------------ */

export const ViewerInfoCard: React.FC<{ project: Project; onClose: () => void }> = ({ project, onClose }) => {
  const rows: [string, string | undefined][] = [
    ["Status", project.statusLabel],
    ["Splats", project.gaussianCount],
    ["Accuracy", project.accuracy],
    ["Captured", project.dateCaptured],
    ["Device", project.captureDevice],
    ["Location", project.location],
  ];
  return (
    <div className={`w-[340px] max-w-[calc(100vw-2rem)] max-h-[60vh] overflow-y-auto rounded-2xl ${CARD} shadow-2xl p-4`}>
      <div className="flex items-start justify-between gap-2 mb-2">
        <h2 className="text-sm font-bold text-[#0f172a]">{project.name}</h2>
        <button
          onClick={onClose}
          aria-label="Close details"
          className="p-1 rounded-lg text-[#94a3b8] hover:text-[#0f172a] hover:bg-slate-100 cursor-pointer"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
      {project.description && (
        <p className="text-[12px] leading-relaxed text-[#475569] mb-3">{project.description}</p>
      )}
      <dl className="grid grid-cols-[88px_1fr] gap-x-2 gap-y-1.5 text-[11px]">
        {rows
          .filter(([, v]) => v)
          .map(([k, v]) => (
            <React.Fragment key={k}>
              <dt className="text-[#94a3b8] font-semibold">{k}</dt>
              <dd className="text-[#0f172a] font-medium break-words">{v}</dd>
            </React.Fragment>
          ))}
      </dl>
    </div>
  );
};

/* ------------------------------ bottom toolbar ------------------------------ */

const RENDER_LABEL: Partial<Record<RenderMode, string>> = { textured: "Splats", mesh: "Mesh", pointcloud: "Points" };
const VIEW_LABEL: Record<ViewMode, string> = { "3d": "3D", top: "Top", "2d": "Plan", side: "Side", front: "Front" };

export const ViewerToolbar: React.FC<{
  viewModes: ViewMode[];
  viewMode: ViewMode;
  onViewMode: (m: ViewMode) => void;
  onZoomIn: () => void;
  onZoomOut: () => void;
  onReset: () => void;
  renderModes?: RenderMode[];
  renderMode: RenderMode;
  onRenderMode: (m: RenderMode) => void;
  dimmed: boolean;
  /** extra on / off switches (the demo scene's X-ray) */
  toggles?: { label: string; active: boolean; onClick: () => void }[];
}> = ({ viewModes, viewMode, onViewMode, onZoomIn, onZoomOut, onReset, renderModes, renderMode, onRenderMode, dimmed, toggles }) => {
  const [renderOpen, setRenderOpen] = useState(false);
  const sep = <span className="w-px h-5 bg-[#e2e8f0] mx-0.5" />;
  const btn = "w-8 h-8 inline-flex items-center justify-center rounded-lg text-[#475569] hover:text-[#2563eb] hover:bg-slate-100 cursor-pointer";
  return (
    <div
      className={`flex items-center gap-0.5 p-1 rounded-2xl ${CARD} transition-opacity duration-500 ${
        dimmed ? "opacity-40 hover:opacity-100" : "opacity-100"
      }`}
    >
      {viewModes.length > 1 && (
        <>
          <div role="group" aria-label="View" className="flex items-center gap-0.5">
            {viewModes.map((m) => (
              <button
                key={m}
                onClick={() => onViewMode(m)}
                aria-pressed={viewMode === m}
                className={`px-2.5 h-8 rounded-lg text-[11px] font-bold cursor-pointer ${
                  viewMode === m ? "bg-blue-50 text-[#2563eb]" : "text-[#64748b] hover:text-[#0f172a]"
                }`}
              >
                {VIEW_LABEL[m]}
              </button>
            ))}
          </div>
          {sep}
        </>
      )}
      <button onClick={onZoomOut} title="Zoom out" aria-label="Zoom out" className={btn}>
        <ZoomOut className="w-4 h-4" />
      </button>
      <button onClick={onZoomIn} title="Zoom in" aria-label="Zoom in" className={btn}>
        <ZoomIn className="w-4 h-4" />
      </button>
      <button onClick={onReset} title="Reset view" aria-label="Reset view" className={btn}>
        <RotateCcw className="w-4 h-4" />
      </button>
      {toggles && toggles.length > 0 && (
        <>
          {sep}
          {toggles.map((tg) => (
            <button
              key={tg.label}
              onClick={tg.onClick}
              aria-pressed={tg.active}
              className={`px-2.5 h-8 rounded-lg text-[11px] font-bold cursor-pointer ${
                tg.active ? "bg-[#2563eb] text-white" : "text-[#64748b] hover:text-[#0f172a] hover:bg-slate-100"
              }`}
            >
              {tg.label}
            </button>
          ))}
        </>
      )}
      {renderModes && renderModes.length > 1 && (
        <>
          {sep}
          <div className="relative">
            <button
              onClick={() => setRenderOpen((v) => !v)}
              aria-expanded={renderOpen}
              className="px-2.5 h-8 inline-flex items-center gap-1 rounded-lg text-[11px] font-bold text-[#0f172a] hover:bg-slate-100 cursor-pointer"
            >
              {RENDER_LABEL[renderMode] ?? renderMode}
              <ChevronDown className="w-3.5 h-3.5 text-[#94a3b8]" />
            </button>
            {renderOpen && (
              <div className={`absolute bottom-full mb-2 right-0 w-32 p-1 rounded-xl ${CARD} shadow-xl`}>
                {renderModes.map((m) => (
                  <button
                    key={m}
                    onClick={() => {
                      onRenderMode(m);
                      setRenderOpen(false);
                    }}
                    className={`w-full text-left px-3 py-1.5 rounded-lg text-[12px] font-semibold cursor-pointer ${
                      m === renderMode ? "text-[#2563eb] bg-blue-50" : "text-[#0f172a] hover:bg-slate-50"
                    }`}
                  >
                    {RENDER_LABEL[m] ?? m}
                  </button>
                ))}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
};

/* ------------------------------ coordinates ------------------------------ */

export const CoordinateReadout: React.FC<{ value: string | null }> = ({ value }) =>
  value ? (
    <div className={`px-2.5 py-1.5 rounded-xl ${CARD} text-[11px] font-mono font-bold text-[#0f172a]`}>{value}</div>
  ) : null;
