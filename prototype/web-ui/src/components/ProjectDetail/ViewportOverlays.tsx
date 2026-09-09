"use client";

import React from "react";
import {
  Rotate3d,
  Hand,
  ZoomIn,
  ZoomOut,
  RefreshCw,
  Maximize2,
  Expand,
  Diamond,
  ChevronDown,
} from "lucide-react";
import { ViewMode, InteractionMode } from "@/components/Viewer3D/Canvas3D";
import { RenderMode } from "@/components/Viewer3D/SceneBuilder";

/* ------------------------------------------------------------------ */
/* View-mode segmented control (top-left of the canvas)                */
/* ------------------------------------------------------------------ */

const VIEW_MODES: { id: ViewMode; label: string }[] = [
  { id: "3d", label: "3D" },
  { id: "2d", label: "2D" },
  { id: "top", label: "Top" },
  { id: "side", label: "Side" },
  { id: "front", label: "Front" },
];

interface ViewModeToggleProps {
  value: ViewMode;
  onChange: (mode: ViewMode) => void;
}

export const ViewModeToggle: React.FC<ViewModeToggleProps> = ({
  value,
  onChange,
}) => (
  <div
    role="group"
    aria-label="View mode"
    className="inline-flex items-center gap-0.5 p-1 rounded-xl bg-[#f1f5f9]/95 backdrop-blur-md border border-[#e2e8f0] shadow-sm"
  >
    {VIEW_MODES.map((mode) => {
      const isActive = value === mode.id;
      return (
        <button
          key={mode.id}
          onClick={() => onChange(mode.id)}
          aria-pressed={isActive}
          className={`px-3 py-1 rounded-lg text-[11px] font-bold transition-all cursor-pointer ${
            isActive
              ? "bg-white text-[#2563eb] shadow-sm"
              : "text-[#64748b] hover:text-[#0f172a]"
          }`}
        >
          {mode.label}
        </button>
      );
    })}
  </div>
);

/* ------------------------------------------------------------------ */
/* Vertical tool rail (right edge of the canvas)                       */
/* ------------------------------------------------------------------ */

interface ToolRailProps {
  interactionMode: InteractionMode;
  onSetInteractionMode: (mode: InteractionMode) => void;
  onZoomIn: () => void;
  onZoomOut: () => void;
  onResetView: () => void;
  onFitToScreen: () => void;
  /** Orbit/pan are meaningless in the orthographic plan view. */
  disableOrbit?: boolean;
}

export const ViewportToolRail: React.FC<ToolRailProps> = ({
  interactionMode,
  onSetInteractionMode,
  onZoomIn,
  onZoomOut,
  onResetView,
  onFitToScreen,
  disableOrbit = false,
}) => {
  const railButton =
    "p-2 rounded-lg transition-colors cursor-pointer disabled:cursor-not-allowed disabled:opacity-35";

  return (
    <div className="flex flex-col items-center gap-0.5 p-1 rounded-2xl bg-white/95 backdrop-blur-md border border-[#e2e8f0] shadow-md">
      <button
        onClick={() => onSetInteractionMode("orbit")}
        disabled={disableOrbit}
        title="Rotate (orbit)"
        aria-label="Rotate"
        aria-pressed={!disableOrbit && interactionMode === "orbit"}
        className={`${railButton} ${
          !disableOrbit && interactionMode === "orbit"
            ? "bg-blue-50 text-[#2563eb]"
            : "text-[#64748b] hover:text-[#0f172a] hover:bg-slate-100"
        }`}
      >
        <Rotate3d className="w-4 h-4" />
      </button>

      <button
        onClick={() => onSetInteractionMode("pan")}
        title="Pan"
        aria-label="Pan"
        aria-pressed={disableOrbit || interactionMode === "pan"}
        className={`${railButton} ${
          disableOrbit || interactionMode === "pan"
            ? "bg-blue-50 text-[#2563eb]"
            : "text-[#64748b] hover:text-[#0f172a] hover:bg-slate-100"
        }`}
      >
        <Hand className="w-4 h-4" />
      </button>

      <div className="w-6 h-px bg-[#e2e8f0] my-0.5" />

      <button
        onClick={onZoomIn}
        title="Zoom in"
        aria-label="Zoom in"
        className={`${railButton} text-[#64748b] hover:text-[#0f172a] hover:bg-slate-100`}
      >
        <ZoomIn className="w-4 h-4" />
      </button>

      <button
        onClick={onZoomOut}
        title="Zoom out"
        aria-label="Zoom out"
        className={`${railButton} text-[#64748b] hover:text-[#0f172a] hover:bg-slate-100`}
      >
        <ZoomOut className="w-4 h-4" />
      </button>

      <div className="w-6 h-px bg-[#e2e8f0] my-0.5" />

      <button
        onClick={onResetView}
        title="Reset view"
        aria-label="Reset view"
        className={`${railButton} text-[#64748b] hover:text-[#0f172a] hover:bg-slate-100`}
      >
        <RefreshCw className="w-4 h-4" />
      </button>

      <button
        onClick={onFitToScreen}
        title="Fit to screen"
        aria-label="Fit to screen"
        className={`${railButton} text-[#64748b] hover:text-[#0f172a] hover:bg-slate-100`}
      >
        <Maximize2 className="w-4 h-4" />
      </button>
    </div>
  );
};

/* ------------------------------------------------------------------ */
/* XYZ axis gizmo (bottom-left of the canvas)                          */
/* ------------------------------------------------------------------ */

interface AxisGizmoProps {
  /** Camera azimuth and elevation in radians. */
  theta: number;
  phi: number;
}

/**
 * Projects the three world axes into screen space using the same spherical
 * camera the canvas uses, so the gizmo tracks the real orbit rather than
 * approximating it.
 */
export const AxisGizmo: React.FC<AxisGizmoProps> = ({ theta, phi }) => {
  const sinPhi = Math.sin(phi);
  const cosPhi = Math.cos(phi);

  // Direction from target toward the camera.
  const dir = {
    x: sinPhi * Math.sin(theta),
    y: cosPhi,
    z: sinPhi * Math.cos(theta),
  };
  const forward = { x: -dir.x, y: -dir.y, z: -dir.z };

  // Looking straight down makes world-up parallel to forward; pick another up.
  const worldUp =
    Math.abs(forward.y) > 0.999 ? { x: 0, y: 0, z: -1 } : { x: 0, y: 1, z: 0 };

  const cross = (
    a: { x: number; y: number; z: number },
    b: { x: number; y: number; z: number }
  ) => ({
    x: a.y * b.z - a.z * b.y,
    y: a.z * b.x - a.x * b.z,
    z: a.x * b.y - a.y * b.x,
  });
  const normalize = (v: { x: number; y: number; z: number }) => {
    const len = Math.hypot(v.x, v.y, v.z) || 1;
    return { x: v.x / len, y: v.y / len, z: v.z / len };
  };
  const dot = (
    a: { x: number; y: number; z: number },
    b: { x: number; y: number; z: number }
  ) => a.x * b.x + a.y * b.y + a.z * b.z;

  const right = normalize(cross(forward, worldUp));
  const up = normalize(cross(right, forward));

  const axes = [
    { name: "X", vec: { x: 1, y: 0, z: 0 }, color: "#dc2626" },
    { name: "Y", vec: { x: 0, y: 1, z: 0 }, color: "#059669" },
    { name: "Z", vec: { x: 0, y: 0, z: 1 }, color: "#2563eb" },
  ];

  const cx = 26;
  const cy = 26;
  const len = 16;

  return (
    <svg
      width="52"
      height="52"
      viewBox="0 0 52 52"
      className="pointer-events-none"
      aria-label="Orientation axes"
      role="img"
    >
      <circle
        cx={cx}
        cy={cy}
        r="24"
        fill="rgba(255,255,255,0.9)"
        stroke="#e2e8f0"
      />
      {axes.map((axis) => {
        // SVG y grows downward, so negate the projected up component.
        const px = cx + dot(axis.vec, right) * len;
        const py = cy - dot(axis.vec, up) * len;
        return (
          <g key={axis.name}>
            <line
              x1={cx}
              y1={cy}
              x2={px}
              y2={py}
              stroke={axis.color}
              strokeWidth="1.75"
              strokeLinecap="round"
            />
            <text
              x={px}
              y={py}
              dx={px >= cx ? 3 : -3}
              dy={py >= cy ? 5 : -2}
              fill={axis.color}
              fontSize="8"
              fontWeight="700"
              textAnchor={px >= cx ? "start" : "end"}
            >
              {axis.name}
            </text>
          </g>
        );
      })}
    </svg>
  );
};

/* ------------------------------------------------------------------ */
/* Bottom toolbar: splat toggle, fullscreen, render-mode dropdown      */
/* ------------------------------------------------------------------ */

const RENDER_MODE_LABELS: Record<RenderMode, string> = {
  pointcloud: "Point Cloud",
  mesh: "Mesh",
  textured: "Textured",
};

interface ViewportBottomBarProps {
  renderMode: RenderMode;
  onChangeRenderMode: (mode: RenderMode) => void;
  splatsVisible: boolean;
  onToggleSplats: () => void;
  onToggleFullscreen: () => void;
  isFullscreen: boolean;
}

export const ViewportBottomBar: React.FC<ViewportBottomBarProps> = ({
  renderMode,
  onChangeRenderMode,
  splatsVisible,
  onToggleSplats,
  onToggleFullscreen,
  isFullscreen,
}) => {
  const [isOpen, setIsOpen] = React.useState(false);

  return (
    <div className="flex items-center gap-1 p-1 rounded-2xl bg-white/95 backdrop-blur-md border border-[#e2e8f0] shadow-md">
      <button
        onClick={onToggleSplats}
        title={splatsVisible ? "Hide raw Gaussian splats" : "Show raw Gaussian splats"}
        aria-pressed={splatsVisible}
        className={`p-2 rounded-lg transition-colors cursor-pointer ${
          splatsVisible
            ? "bg-blue-50 text-[#2563eb]"
            : "text-[#64748b] hover:text-[#0f172a] hover:bg-slate-100"
        }`}
      >
        <Diamond className="w-4 h-4" />
      </button>

      <button
        onClick={onToggleFullscreen}
        title={isFullscreen ? "Exit fullscreen" : "Fullscreen viewport"}
        aria-pressed={isFullscreen}
        className="p-2 rounded-lg text-[#64748b] hover:text-[#0f172a] hover:bg-slate-100 transition-colors cursor-pointer"
      >
        <Expand className="w-4 h-4" />
      </button>

      <div className="w-px h-5 bg-[#e2e8f0] mx-0.5" />

      {/* Render-mode dropdown */}
      <div className="relative">
        <button
          onClick={() => setIsOpen((prev) => !prev)}
          aria-haspopup="listbox"
          aria-expanded={isOpen}
          className="flex items-center gap-1.5 pl-2.5 pr-2 py-1.5 rounded-lg text-[11px] font-bold text-[#0f172a] hover:bg-slate-100 transition-colors cursor-pointer"
        >
          <span>{RENDER_MODE_LABELS[renderMode]}</span>
          <ChevronDown
            className={`w-3.5 h-3.5 text-[#64748b] transition-transform ${
              isOpen ? "rotate-180" : ""
            }`}
          />
        </button>

        {isOpen && (
          <>
            <div
              className="fixed inset-0 z-10"
              onClick={() => setIsOpen(false)}
              aria-hidden
            />
            <ul
              role="listbox"
              className="absolute bottom-full right-0 mb-2 w-36 z-20 p-1 rounded-xl bg-white border border-[#e2e8f0] shadow-lg"
            >
              {(Object.keys(RENDER_MODE_LABELS) as RenderMode[]).map((mode) => (
                <li key={mode}>
                  <button
                    role="option"
                    aria-selected={renderMode === mode}
                    onClick={() => {
                      onChangeRenderMode(mode);
                      setIsOpen(false);
                    }}
                    className={`w-full text-left px-2.5 py-1.5 rounded-lg text-[11px] font-semibold transition-colors cursor-pointer ${
                      renderMode === mode
                        ? "bg-blue-50 text-[#2563eb]"
                        : "text-[#64748b] hover:text-[#0f172a] hover:bg-slate-50"
                    }`}
                  >
                    {RENDER_MODE_LABELS[mode]}
                  </button>
                </li>
              ))}
            </ul>
          </>
        )}
      </div>
    </div>
  );
};
