"use client";

import React, { useState } from "react";
import Link from "next/link";
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
        {/* Left: Back & Project Title */}
        <div className="flex items-center gap-3 pointer-events-auto bg-white/95 backdrop-blur-md border border-[#e2e8f0] p-2 pl-3 pr-4 rounded-2xl shadow-md text-[#0f172a]">
          <Link
            href="/dashboard"
            className="p-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-[#0f172a] transition-colors"
            title="Back to Dashboard"
          >
            <ArrowLeft className="w-4 h-4" />
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

        {/* Right: Export & Toggle Sidebar */}
        <div className="flex items-center gap-2 pointer-events-auto">
          <button
            onClick={onOpenExportModal}
            className="flex items-center gap-2 px-3.5 py-2 rounded-2xl bg-[#2563eb] hover:bg-[#1d4ed8] text-white text-xs font-bold shadow-md shadow-blue-500/10 transition-all cursor-pointer"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export BIM / Data</span>
          </button>

          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2.5 rounded-2xl bg-white/95 backdrop-blur-md border border-[#e2e8f0] text-[#64748b] hover:text-[#0f172a] shadow-md"
            title="Toggle Inspector Sidebar"
          >
            {sidebarOpen ? (
              <ChevronRight className="w-4 h-4" />
            ) : (
              <ChevronLeft className="w-4 h-4" />
            )}
          </button>
        </div>
      </div>

      {/* Left Floating Toolbar: Measurement & View Presets */}
      <div className="absolute left-4 top-24 z-30 flex flex-col gap-2 pointer-events-auto">
        {/* Measurement Mode Button */}
        <div className="p-1.5 rounded-2xl bg-white/95 backdrop-blur-md border border-[#e2e8f0] shadow-md flex flex-col gap-1.5">
          <button
            onClick={onToggleMeasureMode}
            className={`flex items-center gap-2 px-3.5 py-2.5 rounded-xl text-xs font-bold transition-all cursor-pointer ${
              isMeasureMode
                ? "bg-[#2563eb] text-white shadow-sm"
                : "bg-slate-50 text-[#0f172a] hover:bg-slate-100 border border-slate-200"
            }`}
            title="Measure real-world metric distance between points"
          >
            <Ruler className="w-4 h-4" />
            <span>{isMeasureMode ? "Measuring Active" : "Measure Distance"}</span>
          </button>
        </div>

        {/* View Presets Palette */}
        <div className="p-2 rounded-2xl bg-white/95 backdrop-blur-md border border-[#e2e8f0] shadow-md flex flex-col gap-1 text-xs">
          <span className="text-[10px] font-bold text-[#64748b] px-2 py-1 uppercase tracking-wider">
            View Angle
          </span>
          <button
            onClick={() => onSelectPresetView("perspective")}
            className={`px-3 py-1.5 rounded-xl text-left font-semibold transition-colors ${
              activePresetView === "perspective"
                ? "bg-blue-50 text-[#2563eb]"
                : "text-[#64748b] hover:text-[#0f172a] hover:bg-slate-50"
            }`}
          >
            Perspective 3D
          </button>
          <button
            onClick={() => onSelectPresetView("top")}
            className={`px-3 py-1.5 rounded-xl text-left font-semibold transition-colors ${
              activePresetView === "top"
                ? "bg-blue-50 text-[#2563eb]"
                : "text-[#64748b] hover:text-[#0f172a] hover:bg-slate-50"
            }`}
          >
            Top (Plan View)
          </button>
          <button
            onClick={() => onSelectPresetView("front")}
            className={`px-3 py-1.5 rounded-xl text-left font-semibold transition-colors ${
              activePresetView === "front"
                ? "bg-blue-50 text-[#2563eb]"
                : "text-[#64748b] hover:text-[#0f172a] hover:bg-slate-50"
            }`}
          >
            Front Elevation
          </button>
          <button
            onClick={() => onSelectPresetView("side")}
            className={`px-3 py-1.5 rounded-xl text-left font-semibold transition-colors ${
              activePresetView === "side"
                ? "bg-blue-50 text-[#2563eb]"
                : "text-[#64748b] hover:text-[#0f172a] hover:bg-slate-50"
            }`}
          >
            Side Section
          </button>

          <div className="h-[1px] bg-[#e2e8f0] my-1" />

          {/* Wireframe Mode Toggle */}
          <button
            onClick={onToggleWireframe}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-xl font-semibold transition-colors ${
              wireframeMode
                ? "bg-cyan-50 text-cyan-800 border border-cyan-200 font-bold"
                : "text-[#64748b] hover:text-[#0f172a] hover:bg-slate-50"
            }`}
          >
            <Grid className="w-3.5 h-3.5" />
            <span>Wireframe Mode</span>
          </button>
        </div>
      </div>

      {/* Right Sidebar: Semantic Layers & Measurements Schedule */}
      {sidebarOpen && (
        <div className="absolute right-4 top-20 bottom-6 w-80 z-30 flex flex-col gap-4 pointer-events-auto bg-white/95 backdrop-blur-md border border-[#e2e8f0] rounded-2xl shadow-xl p-4 overflow-y-auto text-[#0f172a] animate-in slide-in-from-right duration-200">
          {/* Section 1: AI Semantic Segmentation Layers (YOLOv8-Seg) */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-purple-600" />
                <h3 className="text-xs font-bold text-[#0f172a] uppercase tracking-wider">
                  AI Semantic Layers
                </h3>
              </div>
              <span className="text-[10px] font-mono text-purple-700 font-semibold px-2 py-0.5 rounded-full bg-purple-50 border border-purple-200">
                YOLOv8-Seg 3D
              </span>
            </div>

            <p className="text-[11px] text-[#64748b]">
              Toggle segmented building systems identified by 3D projection:
            </p>

            <div className="space-y-1.5">
              {/* Layer 1: Base Geometry */}
              <button
                onClick={() => onToggleLayer("base")}
                className={`w-full flex items-center justify-between p-2 rounded-xl border text-xs transition-all ${
                  semanticLayers.base
                    ? "bg-slate-50 border-slate-300 text-[#0f172a] font-semibold"
                    : "bg-white border-[#f1f5f9] text-slate-400"
                }`}
              >
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded bg-slate-500" />
                  <span>Raw Architectural Structure</span>
                </div>
                {semanticLayers.base ? (
                  <Eye className="w-3.5 h-3.5 text-[#0f172a]" />
                ) : (
                  <EyeOff className="w-3.5 h-3.5" />
                )}
              </button>

              {/* Layer 2: Pipes (Blue) */}
              <button
                onClick={() => onToggleLayer("pipes")}
                className={`w-full flex items-center justify-between p-2 rounded-xl border text-xs transition-all ${
                  semanticLayers.pipes
                    ? "bg-blue-50 border-blue-200 text-[#1e40af] font-semibold"
                    : "bg-white border-[#f1f5f9] text-slate-400"
                }`}
              >
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded bg-[#2563eb]" />
                  <div>
                    <div className="font-semibold text-left">Chilled Water & Pipes</div>
                    <div className="text-[10px] text-[#2563eb]">96.4% confidence</div>
                  </div>
                </div>
                {semanticLayers.pipes ? (
                  <Eye className="w-3.5 h-3.5 text-[#2563eb]" />
                ) : (
                  <EyeOff className="w-3.5 h-3.5" />
                )}
              </button>

              {/* Layer 3: Electrical Conduits (Amber) */}
              <button
                onClick={() => onToggleLayer("conduits")}
                className={`w-full flex items-center justify-between p-2 rounded-xl border text-xs transition-all ${
                  semanticLayers.conduits
                    ? "bg-amber-50 border-amber-200 text-amber-900 font-semibold"
                    : "bg-white border-[#f1f5f9] text-slate-400"
                }`}
              >
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded bg-amber-500" />
                  <div>
                    <div className="font-semibold text-left">Electrical Conduits</div>
                    <div className="text-[10px] text-amber-700">91.8% confidence</div>
                  </div>
                </div>
                {semanticLayers.conduits ? (
                  <Eye className="w-3.5 h-3.5 text-amber-700" />
                ) : (
                  <EyeOff className="w-3.5 h-3.5" />
                )}
              </button>

              {/* Layer 4: HVAC Ductwork (Emerald) */}
              <button
                onClick={() => onToggleLayer("hvac")}
                className={`w-full flex items-center justify-between p-2 rounded-xl border text-xs transition-all ${
                  semanticLayers.hvac
                    ? "bg-emerald-50 border-emerald-200 text-emerald-900 font-semibold"
                    : "bg-white border-[#f1f5f9] text-slate-400"
                }`}
              >
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded bg-emerald-500" />
                  <div>
                    <div className="font-semibold text-left">HVAC Ductwork</div>
                    <div className="text-[10px] text-emerald-700">94.2% confidence</div>
                  </div>
                </div>
                {semanticLayers.hvac ? (
                  <Eye className="w-3.5 h-3.5 text-emerald-700" />
                ) : (
                  <EyeOff className="w-3.5 h-3.5" />
                )}
              </button>

              {/* Layer 5: Fire Sprinklers (Red) */}
              <button
                onClick={() => onToggleLayer("fire")}
                className={`w-full flex items-center justify-between p-2 rounded-xl border text-xs transition-all ${
                  semanticLayers.fire
                    ? "bg-red-50 border-red-200 text-red-900 font-semibold"
                    : "bg-white border-[#f1f5f9] text-slate-400"
                }`}
              >
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded bg-red-500" />
                  <div>
                    <div className="font-semibold text-left">Fire Suppression</div>
                    <div className="text-[10px] text-red-700">98.1% confidence</div>
                  </div>
                </div>
                {semanticLayers.fire ? (
                  <Eye className="w-3.5 h-3.5 text-red-700" />
                ) : (
                  <EyeOff className="w-3.5 h-3.5" />
                )}
              </button>

              {/* Layer 6: Gaussian Point Cloud Particles */}
              <button
                onClick={() => onToggleLayer("pointcloud")}
                className={`w-full flex items-center justify-between p-2 rounded-xl border text-xs transition-all ${
                  semanticLayers.pointcloud
                    ? "bg-cyan-50 border-cyan-200 text-cyan-900 font-semibold"
                    : "bg-white border-[#f1f5f9] text-slate-400"
                }`}
              >
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded bg-cyan-500" />
                  <span>Raw Gaussian Point Cloud</span>
                </div>
                {semanticLayers.pointcloud ? (
                  <Eye className="w-3.5 h-3.5 text-cyan-700" />
                ) : (
                  <EyeOff className="w-3.5 h-3.5" />
                )}
              </button>
            </div>
          </div>

          <div className="h-[1px] bg-[#e2e8f0]" />

          {/* Section 2: Metric Measurements Schedule */}
          <div className="space-y-3 flex-1 flex flex-col">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Ruler className="w-4 h-4 text-[#2563eb]" />
                <h3 className="text-xs font-bold text-[#0f172a] uppercase tracking-wider">
                  Metric Dimensions ({measurements.length})
                </h3>
              </div>
              {measurements.length > 0 && (
                <button
                  onClick={onClearMeasurements}
                  className="text-[10px] text-[#64748b] hover:text-red-600 transition-colors font-semibold"
                >
                  Clear All
                </button>
              )}
            </div>

            {measurements.length === 0 ? (
              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 text-center text-xs text-[#64748b]">
                No active dimensions. Click &quot;Measure Distance&quot; on the left to snap
                points in 3D.
              </div>
            ) : (
              <div className="space-y-2 overflow-y-auto max-h-48 pr-1">
                {measurements.map((m) => (
                  <div
                    key={m.id}
                    className="p-2.5 rounded-xl bg-[#f8fafc] border border-[#e2e8f0] flex items-center justify-between gap-2 text-xs"
                  >
                    <div>
                      <div className="font-semibold text-[#0f172a]">{m.name}</div>
                      <div className="font-mono text-[#2563eb] font-bold text-sm">
                        {m.distanceMeters.toFixed(2)} m
                      </div>
                    </div>
                    <button
                      onClick={() => onDeleteMeasurement(m.id)}
                      className="p-1.5 rounded-lg text-[#64748b] hover:text-red-600 hover:bg-slate-100"
                      title="Delete measurement"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </>
  );
};
