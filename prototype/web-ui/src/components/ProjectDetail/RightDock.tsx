"use client";

import React from "react";
import { Eye, EyeOff, LayoutGrid, Sparkles, Ruler } from "lucide-react";
import { SemanticLayersState } from "@/components/Viewer3D/SceneBuilder";

export type DockTab = "saved" | "current" | "tools" | "layers";

const DOCK_TABS: { id: DockTab; label: string }[] = [
  { id: "saved", label: "Saved" },
  { id: "current", label: "Current" },
  { id: "tools", label: "Tools" },
  { id: "layers", label: "Layers" },
];

interface LayerMeta {
  key: keyof SemanticLayersState;
  label: string;
  dot: string;
  count: string;
}

/** Counts mirror the seeded YOLOv8-Seg fixture used across the demo. */
const LAYERS: LayerMeta[] = [
  { key: "pipes", label: "Pipes & Plumbing", dot: "bg-[#0369a1]", count: "12 Segments" },
  { key: "conduits", label: "Electrical Conduits", dot: "bg-[#d97706]", count: "18 Runs" },
  { key: "hvac", label: "HVAC Ductwork", dot: "bg-[#059669]", count: "4 Units" },
  { key: "fire", label: "Fire Protection", dot: "bg-[#dc2626]", count: "8 Sprinklers" },
  { key: "base", label: "Structural Base & Walls", dot: "bg-[#94a3b8]", count: "Architecture" },
  { key: "pointcloud", label: "Gaussian Splats (Raw)", dot: "bg-[#6366f1]", count: "1.24M Points" },
];

interface RightDockProps {
  activeTab: DockTab;
  onSelectTab: (tab: DockTab) => void;
  semanticLayers: SemanticLayersState;
  onToggleLayer: (layer: keyof SemanticLayersState) => void;
  measurementCount: number;
}

export const RightDock: React.FC<RightDockProps> = ({
  activeTab,
  onSelectTab,
  semanticLayers,
  onToggleLayer,
  measurementCount,
}) => {
  const isLayers = activeTab === "layers";

  return (
    <aside className="w-[320px] shrink-0 border-l border-[#e2e8f0] bg-white flex flex-col overflow-hidden">
      {/* Header */}
      <div className="px-4 py-3.5 border-b border-[#f1f5f9] flex items-center justify-between shrink-0">
        <div className="flex items-center gap-2">
          {isLayers ? (
            <Sparkles className="w-4 h-4 text-[#2563eb]" />
          ) : (
            <Ruler className="w-4 h-4 text-[#2563eb]" />
          )}
          <h2 className="text-sm font-bold text-[#0f172a]">
            {isLayers ? "Semantic Layers" : "Measurements"}
          </h2>
        </div>

        {isLayers ? (
          <span className="text-[10px] px-2 py-0.5 rounded-full bg-blue-50 text-[#2563eb] font-bold border border-blue-100">
            YOLOv8-Seg
          </span>
        ) : (
          <button
            className="p-1.5 rounded-lg text-[#94a3b8] hover:text-[#0f172a] hover:bg-slate-100 transition-colors cursor-pointer"
            title="Panel layout"
            aria-label="Panel layout"
          >
            <LayoutGrid className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Segmented tabs */}
      <div className="p-3 shrink-0">
        <div
          role="tablist"
          aria-label="Panel section"
          className="flex items-center gap-0.5 p-1 rounded-xl bg-[#f1f5f9]"
        >
          {DOCK_TABS.map((tab) => {
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                role="tab"
                aria-selected={isActive}
                onClick={() => onSelectTab(tab.id)}
                className={`flex-1 px-2 py-1.5 rounded-lg text-[11px] font-bold transition-all cursor-pointer ${
                  isActive
                    ? "bg-white text-[#2563eb] shadow-sm"
                    : "text-[#64748b] hover:text-[#0f172a]"
                }`}
              >
                {tab.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 min-h-0 overflow-y-auto px-3 pb-4">
        {isLayers ? (
          <div className="space-y-2">
            {LAYERS.map((layer) => {
              const isVisible = semanticLayers[layer.key];
              return (
                <button
                  key={layer.key}
                  onClick={() => onToggleLayer(layer.key)}
                  aria-pressed={isVisible}
                  className={`w-full flex items-center justify-between p-2.5 rounded-xl border text-xs font-semibold transition-all cursor-pointer ${
                    isVisible
                      ? "bg-white border-[#e2e8f0] shadow-sm text-[#0f172a]"
                      : "bg-slate-50 border-transparent text-[#94a3b8]"
                  }`}
                >
                  <div className="flex items-center gap-2.5 min-w-0">
                    <span
                      className={`w-2.5 h-2.5 rounded-full shrink-0 ${layer.dot} ${
                        isVisible ? "" : "opacity-40"
                      }`}
                    />
                    <span className="truncate">{layer.label}</span>
                  </div>
                  <div className="flex items-center gap-2 shrink-0 pl-2">
                    <span className="text-[10px] text-[#64748b]">{layer.count}</span>
                    {isVisible ? (
                      <Eye className="w-3.5 h-3.5 text-[#2563eb]" />
                    ) : (
                      <EyeOff className="w-3.5 h-3.5 text-[#cbd5e1]" />
                    )}
                  </div>
                </button>
              );
            })}
          </div>
        ) : (
          /* Saved / Current / Tools land in the next component (spec S4a). */
          <div className="h-full min-h-[220px] flex flex-col items-center justify-center text-center gap-2 px-4 rounded-xl border border-dashed border-[#e2e8f0] bg-[#f8fafc]">
            <Ruler className="w-5 h-5 text-[#cbd5e1]" />
            <p className="text-xs font-bold text-[#64748b]">
              Measurements panel
            </p>
            <p className="text-[11px] text-[#94a3b8] leading-relaxed">
              {measurementCount > 0
                ? `${measurementCount} measurement${
                    measurementCount === 1 ? "" : "s"
                  } captured in this session.`
                : "No measurements captured yet."}
              <br />
              This tab is built in the next step.
            </p>
          </div>
        )}
      </div>
    </aside>
  );
};
