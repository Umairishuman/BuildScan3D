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
  Layers,
  Sparkles,
  Download,
  Trash2,
  Maximize,
  Compass,
  Grid,
  Info,
  ShieldCheck,
  CheckCircle2,
  Box,
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
        <div className="flex items-center gap-3 pointer-events-auto bg-slate-950/85 backdrop-blur-md border border-slate-800 p-2 pl-3 pr-4 rounded-xl shadow-xl">
          <Link
            href="/dashboard"
            className="p-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-300 hover:text-white transition-colors"
            title="Back to Dashboard"
          >
            <ArrowLeft className="w-4 h-4" />
          </Link>

          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-sm font-bold text-white">{projectName}</h1>
              <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                1:1 Metric Model
              </span>
            </div>
            <p className="text-[11px] text-slate-400">{location}</p>
          </div>
        </div>

        {/* Center: Metric Accuracy Badges */}
        <div className="hidden md:flex items-center gap-2 pointer-events-auto bg-slate-950/85 backdrop-blur-md border border-slate-800 px-3 py-1.5 rounded-xl text-xs font-mono">
          <div className="flex items-center gap-1.5 text-cyan-300">
            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
            <span>ARCore 120Hz VIO</span>
          </div>
          <span className="text-slate-600">|</span>
          <div className="text-emerald-400">Ground Truth: ±1.2mm</div>
          <span className="text-slate-600">|</span>
          <div className="text-purple-400">1.24M Gaussians (WebGPU)</div>
        </div>

        {/* Right: Export & Toggle Sidebar */}
        <div className="flex items-center gap-2 pointer-events-auto">
          <button
            onClick={onOpenExportModal}
            className="flex items-center gap-2 px-3 py-2 rounded-xl bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white text-xs font-bold shadow-lg shadow-blue-500/20 transition-all"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export BIM / Data</span>
          </button>

          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2 rounded-xl bg-slate-950/85 backdrop-blur-md border border-slate-800 text-slate-300 hover:text-white"
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
        <div className="p-1.5 rounded-xl bg-slate-950/90 backdrop-blur-md border border-slate-800 shadow-xl flex flex-col gap-1.5">
          <button
            onClick={onToggleMeasureMode}
            className={`flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-semibold transition-all ${
              isMeasureMode
                ? "bg-blue-600 text-white shadow-md shadow-blue-500/30"
                : "bg-slate-900 text-slate-300 hover:text-white hover:bg-slate-800"
            }`}
            title="Measure real-world metric distance between points"
          >
            <Ruler className="w-4 h-4 text-cyan-300" />
            <span>{isMeasureMode ? "Measuring Active" : "Measure Distance"}</span>
          </button>
        </div>

        {/* View Presets Palette */}
        <div className="p-1.5 rounded-xl bg-slate-950/90 backdrop-blur-md border border-slate-800 shadow-xl flex flex-col gap-1 text-xs">
          <span className="text-[10px] font-bold text-slate-400 px-2 py-1 uppercase tracking-wider">
            View Angle
          </span>
          <button
            onClick={() => onSelectPresetView("perspective")}
            className={`px-2.5 py-1.5 rounded-lg text-left font-medium transition-colors ${
              activePresetView === "perspective"
                ? "bg-slate-800 text-white"
                : "text-slate-400 hover:text-white hover:bg-slate-900"
            }`}
          >
            Perspective 3D
          </button>
          <button
            onClick={() => onSelectPresetView("top")}
            className={`px-2.5 py-1.5 rounded-lg text-left font-medium transition-colors ${
              activePresetView === "top"
                ? "bg-slate-800 text-white"
                : "text-slate-400 hover:text-white hover:bg-slate-900"
            }`}
          >
            Top (Plan View)
          </button>
          <button
            onClick={() => onSelectPresetView("front")}
            className={`px-2.5 py-1.5 rounded-lg text-left font-medium transition-colors ${
              activePresetView === "front"
                ? "bg-slate-800 text-white"
                : "text-slate-400 hover:text-white hover:bg-slate-900"
            }`}
          >
            Front Elevation
          </button>
          <button
            onClick={() => onSelectPresetView("side")}
            className={`px-2.5 py-1.5 rounded-lg text-left font-medium transition-colors ${
              activePresetView === "side"
                ? "bg-slate-800 text-white"
                : "text-slate-400 hover:text-white hover:bg-slate-900"
            }`}
          >
            Side Section
          </button>

          <div className="h-[1px] bg-slate-800 my-1" />

          {/* Wireframe Mode Toggle */}
          <button
            onClick={onToggleWireframe}
            className={`flex items-center gap-2 px-2.5 py-1.5 rounded-lg font-medium transition-colors ${
              wireframeMode
                ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/30"
                : "text-slate-400 hover:text-white hover:bg-slate-900"
            }`}
          >
            <Grid className="w-3.5 h-3.5" />
            <span>Wireframe Mode</span>
          </button>
        </div>
      </div>

      {/* Right Sidebar: Semantic Layers & Measurements Schedule */}
      {sidebarOpen && (
        <div className="absolute right-4 top-20 bottom-6 w-80 z-30 flex flex-col gap-4 pointer-events-auto bg-slate-950/95 backdrop-blur-md border border-slate-800 rounded-2xl shadow-2xl p-4 overflow-y-auto text-slate-100 animate-in slide-in-from-right duration-200">
          {/* Section 1: AI Semantic Segmentation Layers (YOLOv8-Seg) */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-purple-400" />
                <h3 className="text-xs font-bold text-white uppercase tracking-wider">
                  AI Semantic Layers
                </h3>
              </div>
              <span className="text-[10px] font-mono text-purple-300 px-1.5 py-0.5 rounded bg-purple-500/10 border border-purple-500/20">
                YOLOv8-Seg 3D
              </span>
            </div>

            <p className="text-[11px] text-slate-400">
              Toggle segmented building systems identified by 3D projection:
            </p>

            <div className="space-y-1.5">
              {/* Layer 1: Base Geometry */}
              <button
                onClick={() => onToggleLayer("base")}
                className={`w-full flex items-center justify-between p-2 rounded-lg border text-xs transition-colors ${
                  semanticLayers.base
                    ? "bg-slate-900 border-slate-700 text-white"
                    : "bg-slate-950/40 border-slate-900 text-slate-500"
                }`}
              >
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded bg-slate-400" />
                  <span className="font-medium">Raw Architectural Structure</span>
                </div>
                {semanticLayers.base ? (
                  <Eye className="w-3.5 h-3.5 text-slate-300" />
                ) : (
                  <EyeOff className="w-3.5 h-3.5" />
                )}
              </button>

              {/* Layer 2: Pipes (Blue) */}
              <button
                onClick={() => onToggleLayer("pipes")}
                className={`w-full flex items-center justify-between p-2 rounded-lg border text-xs transition-colors ${
                  semanticLayers.pipes
                    ? "bg-blue-950/40 border-blue-500/40 text-blue-200"
                    : "bg-slate-950/40 border-slate-900 text-slate-500"
                }`}
              >
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded bg-blue-500" />
                  <div>
                    <div className="font-medium text-left">Chilled Water & Pipes</div>
                    <div className="text-[10px] text-blue-400">96.4% confidence</div>
                  </div>
                </div>
                {semanticLayers.pipes ? (
                  <Eye className="w-3.5 h-3.5 text-blue-400" />
                ) : (
                  <EyeOff className="w-3.5 h-3.5" />
                )}
              </button>

              {/* Layer 3: Electrical Conduits (Amber) */}
              <button
                onClick={() => onToggleLayer("conduits")}
                className={`w-full flex items-center justify-between p-2 rounded-lg border text-xs transition-colors ${
                  semanticLayers.conduits
                    ? "bg-amber-950/40 border-amber-500/40 text-amber-200"
                    : "bg-slate-950/40 border-slate-900 text-slate-500"
                }`}
              >
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded bg-amber-500" />
                  <div>
                    <div className="font-medium text-left">Electrical Conduits</div>
                    <div className="text-[10px] text-amber-400">91.8% confidence</div>
                  </div>
                </div>
                {semanticLayers.conduits ? (
                  <Eye className="w-3.5 h-3.5 text-amber-400" />
                ) : (
                  <EyeOff className="w-3.5 h-3.5" />
                )}
              </button>

              {/* Layer 4: HVAC Ductwork (Emerald) */}
              <button
                onClick={() => onToggleLayer("hvac")}
                className={`w-full flex items-center justify-between p-2 rounded-lg border text-xs transition-colors ${
                  semanticLayers.hvac
                    ? "bg-emerald-950/40 border-emerald-500/40 text-emerald-200"
                    : "bg-slate-950/40 border-slate-900 text-slate-500"
                }`}
              >
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded bg-emerald-500" />
                  <div>
                    <div className="font-medium text-left">HVAC Ductwork</div>
                    <div className="text-[10px] text-emerald-400">94.2% confidence</div>
                  </div>
                </div>
                {semanticLayers.hvac ? (
                  <Eye className="w-3.5 h-3.5 text-emerald-400" />
                ) : (
                  <EyeOff className="w-3.5 h-3.5" />
                )}
              </button>

              {/* Layer 5: Fire Sprinklers (Red) */}
              <button
                onClick={() => onToggleLayer("fire")}
                className={`w-full flex items-center justify-between p-2 rounded-lg border text-xs transition-colors ${
                  semanticLayers.fire
                    ? "bg-red-950/40 border-red-500/40 text-red-200"
                    : "bg-slate-950/40 border-slate-900 text-slate-500"
                }`}
              >
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded bg-red-500" />
                  <div>
                    <div className="font-medium text-left">Fire Suppression</div>
                    <div className="text-[10px] text-red-400">98.1% confidence</div>
                  </div>
                </div>
                {semanticLayers.fire ? (
                  <Eye className="w-3.5 h-3.5 text-red-400" />
                ) : (
                  <EyeOff className="w-3.5 h-3.5" />
                )}
              </button>

              {/* Layer 6: Gaussian Point Cloud Particles */}
              <button
                onClick={() => onToggleLayer("pointcloud")}
                className={`w-full flex items-center justify-between p-2 rounded-lg border text-xs transition-colors ${
                  semanticLayers.pointcloud
                    ? "bg-cyan-950/40 border-cyan-500/40 text-cyan-200"
                    : "bg-slate-950/40 border-slate-900 text-slate-500"
                }`}
              >
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded bg-cyan-400" />
                  <span className="font-medium">Raw Gaussian Point Cloud</span>
                </div>
                {semanticLayers.pointcloud ? (
                  <Eye className="w-3.5 h-3.5 text-cyan-400" />
                ) : (
                  <EyeOff className="w-3.5 h-3.5" />
                )}
              </button>
            </div>
          </div>

          <div className="h-[1px] bg-slate-800" />

          {/* Section 2: Metric Measurements Schedule */}
          <div className="space-y-3 flex-1 flex flex-col">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Ruler className="w-4 h-4 text-cyan-400" />
                <h3 className="text-xs font-bold text-white uppercase tracking-wider">
                  Metric Dimensions ({measurements.length})
                </h3>
              </div>
              {measurements.length > 0 && (
                <button
                  onClick={onClearMeasurements}
                  className="text-[10px] text-slate-400 hover:text-red-400 transition-colors"
                >
                  Clear All
                </button>
              )}
            </div>

            {measurements.length === 0 ? (
              <div className="p-4 rounded-xl bg-slate-900/50 border border-slate-800 text-center text-xs text-slate-500">
                No active dimensions. Click &quot;Measure Distance&quot; on the left to snap
                points in 3D.
              </div>
            ) : (
              <div className="space-y-2 overflow-y-auto max-h-48 pr-1">
                {measurements.map((m) => (
                  <div
                    key={m.id}
                    className="p-2.5 rounded-lg bg-slate-900 border border-slate-800 flex items-center justify-between gap-2 text-xs"
                  >
                    <div>
                      <div className="font-semibold text-white">{m.name}</div>
                      <div className="font-mono text-cyan-300 font-bold text-sm">
                        {m.distanceMeters.toFixed(2)} m
                      </div>
                    </div>
                    <button
                      onClick={() => onDeleteMeasurement(m.id)}
                      className="p-1 rounded text-slate-500 hover:text-red-400 hover:bg-slate-800"
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
