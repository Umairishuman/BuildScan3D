"use client";

import React, { useState } from "react";
import Link from "next/link";
import Image from "next/image";
import { SemanticLayersState } from "./SceneBuilder";
import { MeasurementRecord } from "./MeasurementTool";
import {
  ArrowLeft,
  Ruler,
  Eye,
  EyeOff,
  Sparkles,
  Download,
  Trash2,
  Grid,
  ChevronRight,
  ChevronLeft,
} from "lucide-react";

interface ViewerHUDProps {
  projectName: string;
  location: string;
  semanticLayers: SemanticLayersState;
  onToggleLayer: (layer: keyof SemanticLayersState) => void;
  isMeasureMode: boolean;
  onToggleMeasureMode: () => void;
  measurements: MeasurementRecord[];
  onDeleteMeasurement: (id: string) => void;
  onClearMeasurements: () => void;
  activePresetView: "perspective" | "top" | "front" | "side";
  onSelectPresetView: (view: "perspective" | "top" | "front" | "side") => void;
  wireframeMode: boolean;
  onToggleWireframe: () => void;
  onOpenExportModal: () => void;
}

export const ViewerHUD: React.FC<ViewerHUDProps> = ({
  projectName,
  location,
  semanticLayers,
  onToggleLayer,
  isMeasureMode,
  onToggleMeasureMode,
  measurements,
  onDeleteMeasurement,
  onClearMeasurements,
  activePresetView,
  onSelectPresetView,
  wireframeMode,
  onToggleWireframe,
  onOpenExportModal,
}) => {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  return (
    <>
      {/* Top Navigation Bar */}
      <div className="absolute top-0 left-0 right-0 z-30 flex items-center justify-between p-4 pointer-events-none">
        {/* Left: Back, Logo, Project Title */}
        <div className="flex items-center gap-3 pointer-events-auto bg-white/95 backdrop-blur-md border border-[#e2e8f0] p-2 pl-3 pr-4 rounded-2xl shadow-md text-[#0f172a]">
          <Link
            href="/dashboard"
            className="p-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-[#0f172a] transition-colors"
            title="Back to Dashboard"
          >
            <ArrowLeft className="w-4 h-4" />
          </Link>

          <Link href="/dashboard" className="hidden sm:flex items-center gap-1.5 border-r border-[#e2e8f0] pr-3 mr-1">
            <div className="relative w-6 h-6 shrink-0">
              <Image
                src="/images/logo-new-removebg-preview.png"
                alt="BuildScan 3D"
                fill
                className="object-contain"
              />
            </div>
            <span className="font-extrabold text-xs tracking-tight text-[#0f172a]">
              BuildScan <span className="text-[#2563eb]">3D</span>
            </span>
          </Link>

          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-sm font-bold text-[#0f172a]">{projectName}</h1>
              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
                1:1 Metric Model
              </span>
            </div>
            <p className="text-[11px] text-[#64748b]">{location}</p>
          </div>
        </div>

        {/* Center: Metric Accuracy Badges */}
        <div className="hidden md:flex items-center gap-2 pointer-events-auto bg-white/95 backdrop-blur-md border border-[#e2e8f0] px-3.5 py-2 rounded-2xl text-xs font-mono shadow-md text-[#0f172a]">
          <div className="flex items-center gap-1.5 text-[#2563eb] font-semibold">
            <span className="w-2 h-2 rounded-full bg-[#2563eb] animate-pulse" />
            <span>ARCore 120Hz VIO</span>
          </div>
          <span className="text-slate-300">|</span>
          <div className="text-emerald-700 font-semibold">Ground Truth: ±1.2mm</div>
          <span className="text-slate-300">|</span>
          <div className="text-purple-700 font-semibold">1.24M Gaussians (WebGPU)</div>
        </div>

        {/* Right: Export Button */}
        <button
          onClick={onOpenExportModal}
          className="pointer-events-auto px-4 py-2 rounded-2xl bg-[#2563eb] hover:bg-[#1d4ed8] text-white text-xs font-bold shadow-md transition-all flex items-center gap-1.5 cursor-pointer"
        >
          <Download className="w-4 h-4" />
          <span>Export 3D Model</span>
        </button>
      </div>

      {/* Floating Right Semantic AI & Tools Sidebar */}
      <div
        className={`absolute top-20 right-4 bottom-4 w-72 z-20 transition-transform duration-300 pointer-events-auto ${
          sidebarOpen ? "translate-x-0" : "translate-x-[calc(100%+1.5rem)]"
        }`}
      >
        <div className="h-full bg-white/95 backdrop-blur-md border border-[#e2e8f0] rounded-2xl p-4 shadow-xl flex flex-col justify-between overflow-y-auto text-[#0f172a]">
          {/* Header */}
          <div className="space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-[#e2e8f0]">
              <div className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-[#2563eb]" />
                <h2 className="text-xs font-bold uppercase tracking-wider text-[#0f172a]">
                  Semantic AI Layers
                </h2>
              </div>
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-blue-50 text-[#2563eb] font-bold">
                YOLOv8-Seg
              </span>
            </div>

            {/* Semantic Layer Toggles */}
            <div className="space-y-2">
              {[
                { key: "pipes", label: "Pipes & Plumbing", color: "bg-blue-500", count: "12 Segments" },
                { key: "conduits", label: "Electrical Conduits", color: "bg-amber-500", count: "18 Runs" },
                { key: "hvac", label: "HVAC Ductwork", color: "bg-emerald-500", count: "4 Units" },
                { key: "fire", label: "Fire Protection", color: "bg-red-500", count: "8 Sprinklers" },
                { key: "base", label: "Structural Base & Walls", color: "bg-slate-400", count: "Architecture" },
                { key: "pointcloud", label: "Gaussian Splats (Raw)", color: "bg-indigo-500", count: "1.24M Points" },
              ].map((item) => {
                const isVisible = semanticLayers[item.key as keyof SemanticLayersState];
                return (
                  <button
                    key={item.key}
                    onClick={() => onToggleLayer(item.key as keyof SemanticLayersState)}
                    className={`w-full flex items-center justify-between p-2.5 rounded-xl border text-xs font-semibold transition-all cursor-pointer ${
                      isVisible
                        ? "bg-white border-[#e2e8f0] shadow-sm text-[#0f172a]"
                        : "bg-slate-50 border-transparent text-[#94a3b8] opacity-60"
                    }`}
                  >
                    <div className="flex items-center gap-2.5">
                      <span className={`w-2.5 h-2.5 rounded-full ${item.color}`} />
                      <span className="text-xs">{item.label}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] text-[#64748b]">{item.count}</span>
                      {isVisible ? (
                        <Eye className="w-3.5 h-3.5 text-[#2563eb]" />
                      ) : (
                        <EyeOff className="w-3.5 h-3.5 text-[#94a3b8]" />
                      )}
                    </div>
                  </button>
                );
              })}
            </div>

            {/* Measurement Tools Section */}
            <div className="pt-3 border-t border-[#e2e8f0] space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Ruler className="w-4 h-4 text-[#2563eb]" />
                  <h3 className="text-xs font-bold text-[#0f172a]">Metric Measurement</h3>
                </div>
                {measurements.length > 0 && (
                  <button
                    onClick={onClearMeasurements}
                    className="text-[10px] text-red-600 hover:underline flex items-center gap-1 cursor-pointer"
                  >
                    <Trash2 className="w-3 h-3" /> Clear
                  </button>
                )}
              </div>

              <button
                onClick={onToggleMeasureMode}
                className={`w-full py-2 px-3 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-2 cursor-pointer ${
                  isMeasureMode
                    ? "bg-red-500 hover:bg-red-600 text-white shadow-md animate-pulse"
                    : "bg-slate-100 hover:bg-slate-200 text-[#0f172a]"
                }`}
              >
                <Ruler className="w-3.5 h-3.5" />
                <span>{isMeasureMode ? "Measuring (Click 2 Points)" : "Point-to-Point Ruler"}</span>
              </button>

              {/* Measurements List */}
              {measurements.length > 0 && (
                <div className="space-y-1.5 max-h-32 overflow-y-auto pr-1">
                  {measurements.map((m, idx) => (
                    <div
                      key={m.id}
                      className="flex items-center justify-between text-[11px] font-mono bg-slate-50 p-1.5 rounded-lg border border-[#e2e8f0]"
                    >
                      <span className="font-bold text-[#2563eb]">#{idx + 1}</span>
                      <span className="font-bold text-[#0f172a]">{m.distanceMeters.toFixed(3)} m</span>
                      <button
                        onClick={() => onDeleteMeasurement(m.id)}
                        className="text-[#94a3b8] hover:text-red-600 cursor-pointer"
                      >
                        <Trash2 className="w-3 h-3" />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* View Camera Presets */}
            <div className="pt-3 border-t border-[#e2e8f0] space-y-2">
              <h3 className="text-xs font-bold text-[#0f172a]">Camera Presets</h3>
              <div className="grid grid-cols-4 gap-1">
                {(["perspective", "top", "front", "side"] as const).map((view) => (
                  <button
                    key={view}
                    onClick={() => onSelectPresetView(view)}
                    className={`py-1 rounded-lg text-[10px] font-bold uppercase transition-all cursor-pointer ${
                      activePresetView === view
                        ? "bg-[#2563eb] text-white"
                        : "bg-slate-100 text-[#64748b] hover:text-[#0f172a]"
                    }`}
                  >
                    {view.slice(0, 4)}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Bottom Wireframe Toggle */}
          <div className="pt-3 border-t border-[#e2e8f0]">
            <button
              onClick={onToggleWireframe}
              className={`w-full py-2 px-3 rounded-xl text-xs font-bold border transition-all flex items-center justify-center gap-2 cursor-pointer ${
                wireframeMode
                  ? "bg-slate-900 text-white border-slate-900"
                  : "bg-white text-[#64748b] border-[#e2e8f0] hover:bg-slate-50"
              }`}
            >
              <Grid className="w-3.5 h-3.5" />
              <span>{wireframeMode ? "BIM Wireframe: ON" : "BIM Wireframe: OFF"}</span>
            </button>
          </div>
        </div>

        {/* Sidebar Collapse Toggle Button */}
        <button
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="absolute -left-9 top-1/2 -translate-y-1/2 p-2 rounded-l-xl bg-white/95 backdrop-blur-md border border-r-0 border-[#e2e8f0] text-[#0f172a] shadow-md hover:bg-slate-50 transition-colors cursor-pointer"
          title={sidebarOpen ? "Collapse Panel" : "Expand Panel"}
        >
          {sidebarOpen ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
        </button>
      </div>
    </>
  );
};
