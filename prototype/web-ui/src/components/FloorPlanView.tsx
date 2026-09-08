"use client";

import React, { useState } from "react";
import Link from "next/link";
import { MOCK_FLOOR_PLAN_SECTORS, FloorPlanSector } from "@/lib/mockData";
import { MapPin, Box, ArrowRight, Layers, Eye, CheckCircle2, Activity } from "lucide-react";

export const FloorPlanView: React.FC = () => {
  const [selectedSector, setSelectedSector] = useState<FloorPlanSector>(
    MOCK_FLOOR_PLAN_SECTORS[0]
  );
  const [hoveredSector, setHoveredSector] = useState<FloorPlanSector | null>(null);

  return (
    <div className="space-y-6">
      {/* Floor Plan Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold text-[#0f172a]">
            Interactive Spatial Floor Plan
          </h2>
          <p className="text-xs text-[#64748b]">
            Select any sector or room to view spatial telemetry and jump into the 3D model.
          </p>
        </div>

        <div className="flex items-center gap-2 text-xs font-semibold text-[#0f172a]">
          <span className="px-3 py-1.5 rounded-xl bg-white border border-[#e2e8f0] shadow-sm">
            Level 3 Architectural Plan (1:100 Scale)
          </span>
        </div>
      </div>

      {/* Main Floor Plan Interactive Canvas + Sector Details Drawer */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* 2D Architectural CAD Blueprint Viewport (8 cols) */}
        <div className="lg:col-span-8 bg-white rounded-2xl border border-[#e2e8f0] p-6 shadow-sm relative min-h-[440px] flex flex-col justify-between overflow-hidden">
          {/* Subtle CAD Grid Background */}
          <div className="absolute inset-0 bg-[linear-gradient(to_right,#e2e8f0_1px,transparent_1px),linear-gradient(to_bottom,#e2e8f0_1px,transparent_1px)] bg-[size:24px_24px] opacity-40 pointer-events-none" />

          {/* Interactive Sectors Canvas */}
          <div className="relative w-full h-[380px] border-2 border-dashed border-[#cbd5e1] rounded-xl bg-[#f8fbfe] overflow-hidden p-4">
            {/* Architectural Outer Wall Outlines */}
            <div className="absolute inset-4 border-2 border-[#94a3b8] rounded-lg pointer-events-none opacity-50" />

            {/* Clickable Sectors */}
            {MOCK_FLOOR_PLAN_SECTORS.map((sector) => {
              const isSelected = selectedSector.id === sector.id;
              const isHovered = hoveredSector?.id === sector.id;

              return (
                <div
                  key={sector.id}
                  onClick={() => setSelectedSector(sector)}
                  onMouseEnter={() => setHoveredSector(sector)}
                  onMouseLeave={() => setHoveredSector(null)}
                  style={{
                    left: `${sector.xPercent}%`,
                    top: `${sector.yPercent}%`,
                    width: `${sector.widthPercent}%`,
                    height: `${sector.heightPercent}%`,
                  }}
                  className={`absolute rounded-xl border-2 transition-all duration-200 cursor-pointer p-3 flex flex-col justify-between ${
                    isSelected
                      ? "bg-[#2563eb]/15 border-[#2563eb] shadow-lg shadow-blue-500/10 scale-[1.02] z-10"
                      : isHovered
                      ? "bg-[#2563eb]/10 border-[#3b82f6] z-10"
                      : "bg-white/80 border-[#cbd5e1] hover:border-[#94a3b8]"
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="font-mono text-[10px] font-bold text-[#2563eb]">
                        {sector.sectorCode}
                      </div>
                      <div className="text-xs font-bold text-[#0f172a] line-clamp-1">
                        {sector.name}
                      </div>
                    </div>

                    <span
                      className="w-2.5 h-2.5 rounded-full"
                      style={{ backgroundColor: sector.statusColor }}
                    />
                  </div>

                  <div className="flex items-center justify-between text-[10px] text-[#64748b] font-medium">
                    <span>{sector.area}</span>
                    <span className="flex items-center gap-0.5 text-[#2563eb] font-bold">
                      <MapPin className="w-2.5 h-2.5" />
                      3D Splat
                    </span>
                  </div>
                </div>
              );
            })}
          </div>

          <div className="text-[11px] text-[#64748b] pt-2 flex items-center justify-between">
            <span>Click any highlighted zone on the floor plan to inspect telemetry</span>
            <span className="font-mono text-[#2563eb] font-semibold">ARCore IMU Anchors: Synced</span>
          </div>
        </div>

        {/* Selected Sector Inspector & 3D Launcher (4 cols) */}
        <div className="lg:col-span-4 bg-white rounded-2xl border border-[#e2e8f0] p-6 shadow-sm flex flex-col justify-between space-y-4">
          <div className="space-y-4">
            <div className="flex items-center justify-between border-b border-[#f1f5f9] pb-3">
              <span className="text-[11px] font-bold text-[#2563eb] font-mono px-2 py-0.5 rounded bg-blue-50 border border-blue-200">
                {selectedSector.sectorCode}
              </span>

              <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
                <CheckCircle2 className="w-3.5 h-3.5" />
                {selectedSector.status === "ready" ? "Ready for 3D" : selectedSector.status}
              </span>
            </div>

            <div>
              <h3 className="text-base font-bold text-[#0f172a]">
                {selectedSector.name}
              </h3>
              <p className="text-xs text-[#64748b] mt-0.5">
                {selectedSector.level} • {selectedSector.area}
              </p>
            </div>

            <p className="text-xs text-[#64748b] leading-relaxed">
              {selectedSector.description}
            </p>

            <div className="grid grid-cols-2 gap-2 pt-2 text-xs font-mono">
              <div className="p-2.5 rounded-xl bg-[#f8fafc] border border-[#e2e8f0]">
                <span className="text-[10px] text-[#64748b] font-sans block">ACCURACY</span>
                <span className="font-bold text-[#0f172a]">{selectedSector.accuracy}</span>
              </div>
              <div className="p-2.5 rounded-xl bg-[#f8fafc] border border-[#e2e8f0]">
                <span className="text-[10px] text-[#64748b] font-sans block">SCANS CAPTURED</span>
                <span className="font-bold text-[#2563eb]">{selectedSector.scansCount} Sets</span>
              </div>
            </div>
          </div>

          {/* Launch 3D Gaussian Splat Button */}
          <Link
            href={`/viewer/${selectedSector.targetProjectId}`}
            className="w-full py-3 px-4 rounded-xl bg-[#2563eb] hover:bg-[#1d4ed8] active:bg-[#1e40af] text-white font-bold text-xs shadow-md shadow-blue-500/15 transition-all flex items-center justify-center gap-2 cursor-pointer"
          >
            <Box className="w-4 h-4" />
            <span>Launch 3D Gaussian Splat</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </div>
    </div>
  );
};
