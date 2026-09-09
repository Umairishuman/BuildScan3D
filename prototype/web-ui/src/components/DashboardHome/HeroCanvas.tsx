"use client";

import React from "react";
import Image from "next/image";
import Link from "next/link";
import {
  Box,
  ChevronRight,
  Compass,
  GitCompare,
  Hand,
  Layers3,
  Ruler,
  Scissors,
  Sun,
  Target,
  Rotate3d,
} from "lucide-react";

type Tool = "orbit" | "pan" | "measure" | "section" | "compare";

interface Measurement {
  label: string;
  x: number; // % from left
  y: number; // % from top
  tone: "blue" | "amber" | "green";
}

const MEASUREMENTS: Measurement[] = [
  { label: "32.418 m", x: 54, y: 22, tone: "blue" },
  { label: "18.736 m", x: 24, y: 46, tone: "blue" },
  { label: "12.405 m", x: 72, y: 55, tone: "blue" },
];

interface HeroCanvasProps {
  activeTool: Tool;
  onSelectTool: (tool: Tool) => void;
  viewMode: "2d" | "3d";
  onSelectViewMode: (mode: "2d" | "3d") => void;
  activeFloor: string;
  onSelectFloor: (floor: string) => void;
  projectHref: string;
}

const FLOORS = ["F5", "F4", "F3", "F2", "B1"] as const;

export const HeroCanvas: React.FC<HeroCanvasProps> = ({
  activeTool,
  onSelectTool,
  viewMode,
  onSelectViewMode,
  activeFloor,
  onSelectFloor,
  projectHref,
}) => (
  <div className="relative w-full h-full rounded-2xl border border-[#e2e8f0] bg-white overflow-hidden shadow-sm">
    {/* Background render — the reference dashboard background image */}
    <Image
      src="/images/dashboard background.png"
      alt="Sector 4 MEP Room isometric scan"
      fill
      priority
      className="object-contain object-center pointer-events-none select-none"
    />

    {/* Soft grid overlay behind the image, subtle CAD feel */}
    <div
      aria-hidden
      className="absolute inset-0 opacity-40 pointer-events-none -z-10"
      style={{
        backgroundImage:
          "linear-gradient(to right, #e2e8f0 1px, transparent 1px), linear-gradient(to bottom, #e2e8f0 1px, transparent 1px)",
        backgroundSize: "48px 48px",
      }}
    />

    {/* Project identity card, top-left */}
    <div className="absolute top-4 left-4 z-10 max-w-[320px] p-4 rounded-2xl bg-white/95 backdrop-blur-md border border-[#e2e8f0] shadow-md space-y-1.5">
      <div className="flex items-center gap-1 text-[10px] font-bold text-[#64748b]">
        <Link href="/projects" className="hover:text-[#2563eb] cursor-pointer">
          All Projects
        </Link>
        <ChevronRight className="w-3 h-3" />
        <span className="text-[#2563eb]">Sector 4 MEP Room</span>
      </div>
      <div className="flex items-center gap-2 flex-wrap">
        <h1 className="text-base font-extrabold text-[#0f172a] tracking-tight">
          Sector 4 MEP Room
        </h1>
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-emerald-50 text-[#065f46] text-[10px] font-bold border border-emerald-100">
          <span className="relative flex w-1.5 h-1.5">
            <span className="absolute inline-flex w-full h-full rounded-full bg-[#10b981] animate-ping opacity-75" />
            <span className="relative inline-flex w-1.5 h-1.5 rounded-full bg-[#10b981]" />
          </span>
          Live Scan
        </span>
      </div>
      <p className="text-[11px] text-[#64748b] leading-tight">
        Floor 3 · Block B · 847 m²
      </p>
      <p className="text-[10px] text-[#94a3b8] font-mono">
        33.68449° N, 73.6479° E
      </p>
      <Link
        href={projectHref}
        className="inline-flex items-center gap-1 text-[11px] font-bold text-[#2563eb] hover:text-[#1d4ed8] cursor-pointer pt-1"
      >
        Open 3D viewer <ChevronRight className="w-3 h-3" />
      </Link>
    </div>

    {/* Top-centre tool pill */}
    <div className="absolute top-4 left-1/2 -translate-x-1/2 z-10">
      <ToolPill active={activeTool} onSelect={onSelectTool} />
    </div>

    {/* Top-right: 2D / 3D toggle */}
    <div className="absolute top-4 right-4 z-10">
      <ViewModeSwitch value={viewMode} onChange={onSelectViewMode} />
    </div>

    {/* Left vertical icon rail */}
    <div className="absolute top-1/2 left-4 -translate-y-1/2 z-10">
      <IconRail />
    </div>

    {/* Measurement callouts overlaid on the render */}
    {MEASUREMENTS.map((m) => (
      <MeasurementBadge key={m.label} measurement={m} />
    ))}

    {/* Bottom-left: compass rose */}
    <div className="absolute bottom-4 left-4 z-10">
      <CompassRose />
    </div>

    {/* Bottom-right: floor selector */}
    <div className="absolute bottom-4 right-4 z-10">
      <FloorSelector
        active={activeFloor}
        onSelect={onSelectFloor}
      />
    </div>
  </div>
);

/* ------------------------- pieces ------------------------- */

const TOOLS: { id: Tool; label: string; Icon: React.ComponentType<{ className?: string }> }[] = [
  { id: "orbit", label: "Orbit", Icon: Rotate3d },
  { id: "pan", label: "Pan", Icon: Hand },
  { id: "measure", label: "Measure", Icon: Ruler },
  { id: "section", label: "Section", Icon: Scissors },
  { id: "compare", label: "Compare", Icon: GitCompare },
];

const ToolPill: React.FC<{ active: Tool; onSelect: (t: Tool) => void }> = ({
  active,
  onSelect,
}) => (
  <div
    role="group"
    aria-label="Canvas tools"
    className="flex items-center gap-1 p-1.5 rounded-2xl bg-white/95 backdrop-blur-md border border-[#e2e8f0] shadow-md"
  >
    {TOOLS.map((tool) => {
      const isActive = active === tool.id;
      const { Icon } = tool;
      return (
        <button
          key={tool.id}
          onClick={() => onSelect(tool.id)}
          aria-pressed={isActive}
          className={`flex flex-col items-center gap-0.5 px-2.5 py-1.5 rounded-xl transition-all cursor-pointer min-w-[54px] ${
            isActive
              ? "bg-[#2563eb] text-white shadow-sm"
              : "text-[#64748b] hover:text-[#0f172a] hover:bg-slate-100"
          }`}
        >
          <Icon className="w-4 h-4" />
          <span className="text-[10px] font-bold">{tool.label}</span>
        </button>
      );
    })}
  </div>
);

const ViewModeSwitch: React.FC<{
  value: "2d" | "3d";
  onChange: (mode: "2d" | "3d") => void;
}> = ({ value, onChange }) => (
  <div className="flex items-center gap-0.5 p-1 rounded-xl bg-white/95 backdrop-blur-md border border-[#e2e8f0] shadow-md">
    {(["2d", "3d"] as const).map((mode) => {
      const isActive = value === mode;
      return (
        <button
          key={mode}
          onClick={() => onChange(mode)}
          aria-pressed={isActive}
          className={`px-3 py-1.5 rounded-lg text-[11px] font-bold uppercase transition-all cursor-pointer ${
            isActive
              ? "bg-[#2563eb] text-white shadow-sm"
              : "text-[#64748b] hover:text-[#0f172a]"
          }`}
        >
          {mode}
        </button>
      );
    })}
  </div>
);

const IconRail: React.FC = () => (
  <div className="flex flex-col items-center gap-1 p-1.5 rounded-2xl bg-white/95 backdrop-blur-md border border-[#e2e8f0] shadow-md">
    {[
      { Icon: Box, active: true, label: "3D Model" },
      { Icon: Target, active: false, label: "Center on target" },
      { Icon: Layers3, active: false, label: "Layers" },
      { Icon: Sun, active: false, label: "Lighting" },
    ].map(({ Icon, active, label }) => (
      <button
        key={label}
        title={label}
        aria-label={label}
        className={`p-2 rounded-xl transition-colors cursor-pointer ${
          active
            ? "bg-blue-50 text-[#2563eb]"
            : "text-[#64748b] hover:text-[#0f172a] hover:bg-slate-100"
        }`}
      >
        <Icon className="w-4 h-4" />
      </button>
    ))}
  </div>
);

const MeasurementBadge: React.FC<{ measurement: Measurement }> = ({
  measurement,
}) => (
  <div
    className="absolute z-[5] pointer-events-none"
    style={{ left: `${measurement.x}%`, top: `${measurement.y}%` }}
  >
    <div className="px-2.5 py-1 rounded-lg bg-[#0f172a] text-white shadow-lg flex items-center gap-1.5">
      <Ruler className="w-3 h-3 text-[#38bdf8]" />
      <span className="text-[11px] font-mono font-bold">{measurement.label}</span>
    </div>
    <span className="absolute top-full left-1/2 -translate-x-1/2 w-1.5 h-1.5 rounded-full bg-[#38bdf8] ring-2 ring-white/60 mt-1" />
  </div>
);

const CompassRose: React.FC = () => (
  <div className="w-16 h-16 rounded-2xl bg-white/95 backdrop-blur-md border border-[#e2e8f0] shadow-md relative flex items-center justify-center">
    <Compass className="w-6 h-6 text-[#2563eb] absolute opacity-25" />
    <svg viewBox="0 0 60 60" className="w-full h-full">
      {/* Cardinal labels */}
      <text x="30" y="10" textAnchor="middle" fontSize="8" fontWeight="700" fill="#0f172a">N</text>
      <text x="30" y="56" textAnchor="middle" fontSize="8" fontWeight="700" fill="#94a3b8">S</text>
      <text x="6" y="33" textAnchor="middle" fontSize="8" fontWeight="700" fill="#94a3b8">W</text>
      <text x="54" y="33" textAnchor="middle" fontSize="8" fontWeight="700" fill="#94a3b8">E</text>
      {/* Axes */}
      <line x1="30" y1="30" x2="46" y2="42" stroke="#dc2626" strokeWidth="1.5" strokeLinecap="round" />
      <line x1="30" y1="30" x2="14" y2="42" stroke="#059669" strokeWidth="1.5" strokeLinecap="round" />
      <line x1="30" y1="30" x2="30" y2="16" stroke="#2563eb" strokeWidth="1.5" strokeLinecap="round" />
      <text x="48" y="46" fontSize="6" fontWeight="700" fill="#dc2626">X</text>
      <text x="10" y="46" fontSize="6" fontWeight="700" fill="#059669">Y</text>
      <text x="32" y="14" fontSize="6" fontWeight="700" fill="#2563eb">Z</text>
      <circle cx="30" cy="30" r="1.5" fill="#0f172a" />
    </svg>
  </div>
);

const FloorSelector: React.FC<{
  active: string;
  onSelect: (floor: string) => void;
}> = ({ active, onSelect }) => (
  <div className="flex items-stretch gap-2 p-2 rounded-2xl bg-white/95 backdrop-blur-md border border-[#e2e8f0] shadow-md">
    {/* Miniature floor plan preview */}
    <div className="w-24 h-24 rounded-xl bg-[#f8fafc] border border-[#e2e8f0] flex items-center justify-center relative overflow-hidden">
      <svg viewBox="0 0 100 100" className="w-full h-full">
        <rect x="8" y="8" width="84" height="84" fill="none" stroke="#94a3b8" strokeWidth="1.5" rx="2" />
        <line x1="8" y1="42" x2="52" y2="42" stroke="#cbd5e1" strokeWidth="1" />
        <line x1="52" y1="8" x2="52" y2="92" stroke="#cbd5e1" strokeWidth="1" />
        <line x1="52" y1="65" x2="92" y2="65" stroke="#cbd5e1" strokeWidth="1" />
        <polygon points="42,54 58,54 62,64 38,64" fill="#2563eb" opacity="0.7" />
        <circle cx="50" cy="59" r="3" fill="#2563eb" />
      </svg>
    </div>
    {/* Floor picker */}
    <div className="flex flex-col gap-0.5">
      {FLOORS.map((floor) => {
        const isActive = floor === active;
        return (
          <button
            key={floor}
            onClick={() => onSelect(floor)}
            aria-pressed={isActive}
            className={`px-2.5 py-1 rounded-lg text-[10px] font-bold text-center transition-all cursor-pointer min-w-[36px] ${
              isActive
                ? "bg-[#2563eb] text-white shadow-sm"
                : "text-[#64748b] hover:text-[#0f172a] hover:bg-slate-100"
            }`}
          >
            {floor}
          </button>
        );
      })}
    </div>
  </div>
);

