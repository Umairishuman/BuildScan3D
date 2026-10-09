"use client";

import React, { useCallback, useEffect, useRef, useState } from "react";
import {
  ArrowLeft,
  Expand,
  Flag,
  GitCompare,
  Minus,
  Plus,
  RefreshCcw,
} from "lucide-react";
import {
  ChangeLogEntry,
  ChangeType,
  ComparisonPair,
  MOCK_CHANGE_LOG,
  MOCK_COMPARISON_PAIR,
} from "@/lib/mockData";

type CompareMode = "overlay" | "split";

const CHANGE_STYLE: Record<
  ChangeType,
  { label: string; text: string; bg: string; border: string; Icon: React.ComponentType<{ className?: string }> }
> = {
  added: {
    label: "Added",
    text: "text-[#059669]",
    bg: "bg-emerald-50",
    border: "border-emerald-100",
    Icon: Plus,
  },
  removed: {
    label: "Removed",
    text: "text-[#dc2626]",
    bg: "bg-red-50",
    border: "border-red-100",
    Icon: Minus,
  },
  modified: {
    label: "Modified",
    text: "text-[#d97706]",
    bg: "bg-amber-50",
    border: "border-amber-100",
    Icon: RefreshCcw,
  },
};

interface ComparisonViewProps {
  onBack: () => void;
  pair?: ComparisonPair;
  changeLog?: readonly ChangeLogEntry[];
}

export const ComparisonView: React.FC<ComparisonViewProps> = ({
  onBack,
  pair = MOCK_COMPARISON_PAIR,
  changeLog = MOCK_CHANGE_LOG,
}) => {
  const [mode, setMode] = useState<CompareMode>("overlay");
  const [wipePercent, setWipePercent] = useState(50);
  const [flagged, setFlagged] = useState<Record<string, boolean>>(() =>
    changeLog.reduce<Record<string, boolean>>((acc, row) => {
      acc[row.id] = row.flagged;
      return acc;
    }, {})
  );

  return (
    <div className="flex-1 min-h-0 flex flex-col overflow-hidden">
      {/* Sub-header */}
      <div className="shrink-0 px-5 py-3 border-b border-[#e2e8f0] bg-white flex items-center justify-between gap-3">
        <div className="flex items-center gap-2 min-w-0">
          <button
            onClick={onBack}
            aria-label="Back to viewer"
            className="p-1.5 rounded-lg text-[#64748b] hover:text-[#0f172a] hover:bg-slate-100 transition-colors cursor-pointer"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <GitCompare className="w-4 h-4 text-[#2563eb]" />
          <h2 className="text-sm font-bold text-[#0f172a] truncate">
            Comparison View
          </h2>
          <span className="text-[10px] font-bold px-1.5 py-0.5 rounded-full bg-blue-50 text-[#2563eb] border border-blue-100">
            2 scans
          </span>
        </div>

        <ModeToggle mode={mode} onChange={setMode} />
      </div>

      {/* Legend row */}
      <div className="shrink-0 px-5 py-3 border-b border-[#f1f5f9] bg-white flex items-center justify-between gap-3 flex-wrap">
        <div className="flex items-center gap-5">
          <ScanChip scan={pair.older} suffix="older" />
          <div className="w-px h-6 bg-[#e2e8f0]" />
          <ScanChip scan={pair.newer} suffix="newer" />
        </div>
        <p className="text-[10px] font-medium text-[#64748b]">
          {mode === "overlay"
            ? "Drag the divider to wipe between scans"
            : "Both scans rendered side-by-side"}
        </p>
      </div>

      {/* Canvas */}
      <div className="flex-1 min-h-0 p-5 bg-[#eef3f9]">
        <div className="relative w-full h-full rounded-2xl border border-[#e2e8f0] bg-white shadow-sm overflow-hidden">
          {mode === "overlay" ? (
            <OverlayCanvas
              pair={pair}
              wipePercent={wipePercent}
              onWipeChange={setWipePercent}
            />
          ) : (
            <SplitCanvas pair={pair} />
          )}

          {/* Persistent chip bottom-left */}
          <div className="pointer-events-none absolute bottom-3 left-3 flex items-center gap-2 px-2.5 py-1.5 rounded-xl bg-white/95 backdrop-blur-md border border-[#e2e8f0] shadow-sm">
            <ChipSwatch color={pair.older.hexColor} />
            <span className="text-[10px] font-bold text-[#0f172a]">
              {pair.older.label} (older)
            </span>
            <span className="text-[10px] text-[#94a3b8]">·</span>
            <ChipSwatch color={pair.newer.hexColor} />
            <span className="text-[10px] font-bold text-[#0f172a]">
              {pair.newer.label} (newer)
            </span>
          </div>

          <button
            className="absolute bottom-3 right-3 p-2 rounded-xl bg-white/95 backdrop-blur-md border border-[#e2e8f0] shadow-sm text-[#64748b] hover:text-[#0f172a] hover:bg-white transition-colors cursor-pointer"
            title="Fullscreen"
            aria-label="Fullscreen"
          >
            <Expand className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Change-log table */}
      <div className="shrink-0 max-h-[42%] overflow-y-auto border-t border-[#e2e8f0] bg-white">
        <ChangeLogTable
          entries={changeLog}
          flagged={flagged}
          onToggleFlag={(id) =>
            setFlagged((prev) => ({ ...prev, [id]: !prev[id] }))
          }
        />
      </div>
    </div>
  );
};

/* ------------------------------------------------------------------ */
/* Header pieces                                                       */
/* ------------------------------------------------------------------ */

const ModeToggle: React.FC<{
  mode: CompareMode;
  onChange: (mode: CompareMode) => void;
}> = ({ mode, onChange }) => (
  <div
    role="group"
    aria-label="Comparison mode"
    className="inline-flex items-center gap-0.5 p-1 rounded-xl bg-[#f1f5f9] border border-[#e2e8f0]"
  >
    {(["overlay", "split"] as CompareMode[]).map((option) => {
      const isActive = option === mode;
      return (
        <button
          key={option}
          onClick={() => onChange(option)}
          aria-pressed={isActive}
          className={`px-3 py-1 rounded-lg text-[11px] font-bold transition-all cursor-pointer ${
            isActive
              ? "bg-white text-[#2563eb] shadow-sm"
              : "text-[#64748b] hover:text-[#0f172a]"
          }`}
        >
          {option === "overlay" ? "Overlay" : "Split View"}
        </button>
      );
    })}
  </div>
);

const ScanChip: React.FC<{
  scan: ComparisonPair["older"];
  suffix: "older" | "newer";
}> = ({ scan, suffix }) => (
  <div className="flex items-center gap-2">
    <span
      className="w-2.5 h-2.5 rounded-full"
      style={{ backgroundColor: scan.hexColor }}
    />
    <div className="flex flex-col leading-tight">
      <span className="text-[11px] font-bold text-[#0f172a]">
        {scan.label}
        <span className="text-[#94a3b8] font-medium"> · {suffix}</span>
      </span>
      <span className="text-[10px] text-[#64748b]">
        {scan.date} ·{" "}
        <span className="font-mono">{scan.gaussians} Gaussians</span>
      </span>
    </div>
  </div>
);

const ChipSwatch: React.FC<{ color: string }> = ({ color }) => (
  <span className="w-2 h-2 rounded-full" style={{ backgroundColor: color }} />
);

/* ------------------------------------------------------------------ */
/* Overlay canvas + wipe slider                                        */
/* ------------------------------------------------------------------ */

interface OverlayCanvasProps {
  pair: ComparisonPair;
  wipePercent: number;
  onWipeChange: (percent: number) => void;
}

const OverlayCanvas: React.FC<OverlayCanvasProps> = ({
  pair,
  wipePercent,
  onWipeChange,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const draggingRef = useRef(false);

  const updateFromClientX = useCallback(
    (clientX: number) => {
      const el = containerRef.current;
      if (!el) return;
      const rect = el.getBoundingClientRect();
      const percent = ((clientX - rect.left) / rect.width) * 100;
      onWipeChange(Math.max(2, Math.min(98, percent)));
    },
    [onWipeChange]
  );

  useEffect(() => {
    const handleMove = (e: MouseEvent) => {
      if (!draggingRef.current) return;
      updateFromClientX(e.clientX);
    };
    const handleUp = () => {
      draggingRef.current = false;
    };
    window.addEventListener("mousemove", handleMove);
    window.addEventListener("mouseup", handleUp);
    return () => {
      window.removeEventListener("mousemove", handleMove);
      window.removeEventListener("mouseup", handleUp);
    };
  }, [updateFromClientX]);

  return (
    <div ref={containerRef} className="relative w-full h-full select-none">
      {/* Older scan: full-width base */}
      <div className="absolute inset-0">
        <ScanScene scan={pair.older} variant="older" />
      </div>

      {/* Newer scan: clipped to right of the wipe */}
      <div
        className="absolute inset-0 overflow-hidden"
        style={{ clipPath: `inset(0 0 0 ${wipePercent}%)` }}
      >
        <ScanScene scan={pair.newer} variant="newer" />
      </div>

      {/* Wipe handle */}
      <div
        role="slider"
        aria-label="Wipe between scans"
        aria-valuenow={Math.round(wipePercent)}
        aria-valuemin={0}
        aria-valuemax={100}
        tabIndex={0}
        onMouseDown={(e) => {
          draggingRef.current = true;
          updateFromClientX(e.clientX);
        }}
        onKeyDown={(e) => {
          if (e.key === "ArrowLeft")
            onWipeChange(Math.max(2, wipePercent - 2));
          if (e.key === "ArrowRight")
            onWipeChange(Math.min(98, wipePercent + 2));
        }}
        className="absolute top-0 bottom-0 -translate-x-1/2 cursor-ew-resize group"
        style={{ left: `${wipePercent}%` }}
      >
        <div className="w-0.5 h-full bg-white shadow-[0_0_0_1px_rgba(15,23,42,0.15)]" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-9 h-9 rounded-full bg-white border-2 border-[#2563eb] shadow-lg flex items-center justify-center text-[#2563eb] group-hover:scale-110 transition-transform">
          <svg viewBox="0 0 24 24" className="w-4 h-4" fill="currentColor">
            <path d="M8 5l-6 7 6 7V5zm8 0l6 7-6 7V5z" />
          </svg>
        </div>
      </div>

      {/* Top-edge tint labels */}
      <div className="pointer-events-none absolute top-3 left-3 px-2.5 py-1 rounded-full text-[10px] font-bold text-white shadow-md"
        style={{ backgroundColor: pair.older.hexColor }}>
        {pair.older.label}
      </div>
      <div className="pointer-events-none absolute top-3 right-3 px-2.5 py-1 rounded-full text-[10px] font-bold text-white shadow-md"
        style={{ backgroundColor: pair.newer.hexColor }}>
        {pair.newer.label}
      </div>
    </div>
  );
};

/* ------------------------------------------------------------------ */
/* Split canvas                                                        */
/* ------------------------------------------------------------------ */

const SplitCanvas: React.FC<{ pair: ComparisonPair }> = ({ pair }) => (
  <div className="w-full h-full grid grid-cols-2 divide-x divide-[#e2e8f0]">
    {[pair.older, pair.newer].map((scan, i) => (
      <div key={scan.id} className="relative">
        <ScanScene scan={scan} variant={i === 0 ? "older" : "newer"} />
        <div
          className="absolute top-3 left-3 px-2.5 py-1 rounded-full text-[10px] font-bold text-white shadow-md"
          style={{ backgroundColor: scan.hexColor }}
        >
          {scan.label} · {scan.date}
        </div>
      </div>
    ))}
  </div>
);

/* ------------------------------------------------------------------ */
/* Change-log table                                                    */
/* ------------------------------------------------------------------ */

interface ChangeLogTableProps {
  entries: readonly ChangeLogEntry[];
  flagged: Record<string, boolean>;
  onToggleFlag: (id: string) => void;
}

const ChangeLogTable: React.FC<ChangeLogTableProps> = ({
  entries,
  flagged,
  onToggleFlag,
}) => (
  <div>
    <div className="px-5 py-2.5 flex items-center justify-between border-b border-[#f1f5f9]">
      <h3 className="text-[11px] font-bold text-[#0f172a]">
        Change Log · {entries.length} differences
      </h3>
      <p className="text-[10px] text-[#64748b]">
        Flag anything a coordinator should sign off before construction moves on.
      </p>
    </div>
    <table className="w-full text-left">
      <thead>
        <tr className="text-[10px] font-bold uppercase tracking-wider text-[#94a3b8] bg-[#f8fafc]">
          <th className="px-5 py-2 w-2/6">Element</th>
          <th className="px-2 py-2 w-1/6">Change Type</th>
          <th className="px-2 py-2 w-1/6">Layer</th>
          <th className="px-2 py-2 w-1/6">Delta</th>
          <th className="px-5 py-2 w-1/6 text-right">Flagged</th>
        </tr>
      </thead>
      <tbody>
        {entries.map((row) => {
          const style = CHANGE_STYLE[row.changeType];
          const { Icon } = style;
          const isFlagged = flagged[row.id];
          return (
            <tr
              key={row.id}
              className="border-t border-[#f1f5f9] hover:bg-slate-50 transition-colors"
            >
              <td className="px-5 py-2.5">
                <span className="text-[12px] font-bold text-[#0f172a]">
                  {row.element}
                </span>
              </td>
              <td className="px-2 py-2.5">
                <span
                  className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold border ${style.text} ${style.bg} ${style.border}`}
                >
                  <Icon className="w-3 h-3" />
                  {style.label}
                </span>
              </td>
              <td className="px-2 py-2.5 text-[11px] text-[#64748b]">
                {row.layer}
              </td>
              <td className="px-2 py-2.5 text-[11px] font-mono font-bold text-[#0f172a]">
                {row.delta}
              </td>
              <td className="px-5 py-2.5 text-right">
                <button
                  onClick={() => onToggleFlag(row.id)}
                  aria-pressed={isFlagged}
                  aria-label={
                    isFlagged
                      ? `Unflag ${row.element}`
                      : `Flag ${row.element} for review`
                  }
                  className={`inline-flex items-center gap-1 px-2 py-1 rounded-lg text-[10px] font-bold transition-colors cursor-pointer ${
                    isFlagged
                      ? "bg-red-50 text-[#dc2626] border border-red-100"
                      : "bg-slate-50 text-[#94a3b8] border border-transparent hover:bg-slate-100 hover:text-[#475569]"
                  }`}
                >
                  <Flag className="w-3 h-3" />
                  {isFlagged ? "Flagged" : "Flag"}
                </button>
              </td>
            </tr>
          );
        })}
      </tbody>
    </table>
  </div>
);

/* ------------------------------------------------------------------ */
/* Stylised scan scene                                                 */
/* ------------------------------------------------------------------ */

/**
 * Hand-drawn isometric-ish MEP scene. Both scans share the shell; per-variant
 * flags flip small differences (added sprinkler on newer, missing conduit on
 * newer, shifted duct) so the wipe reveals real change spots.
 */
const ScanScene: React.FC<{
  scan: ComparisonPair["older"];
  variant: "older" | "newer";
}> = ({ scan, variant }) => {
  const isNewer = variant === "newer";
  const stroke = scan.hexColor;

  return (
    <div
      className="w-full h-full"
      style={{
        backgroundColor: isNewer ? "#f0fdf4" : "#eff6ff",
        backgroundImage:
          "linear-gradient(to right, rgba(148, 163, 184, 0.15) 1px, transparent 1px), linear-gradient(to bottom, rgba(148, 163, 184, 0.15) 1px, transparent 1px)",
        backgroundSize: "36px 36px",
      }}
    >
      <svg
        viewBox="0 0 800 500"
        preserveAspectRatio="xMidYMid meet"
        className="w-full h-full"
        role="img"
        aria-label={`${scan.label} render`}
      >
        <defs>
          <linearGradient id={`floor-${variant}`} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stopColor={stroke} stopOpacity="0.06" />
            <stop offset="1" stopColor={stroke} stopOpacity="0.14" />
          </linearGradient>
        </defs>

        {/* Room shell (isometric-ish) */}
        <polygon
          points="120,360 400,440 680,360 400,290"
          fill={`url(#floor-${variant})`}
          stroke={stroke}
          strokeWidth="1.5"
          opacity="0.9"
        />

        {/* Back walls */}
        <polyline
          points="120,360 120,180 400,110 400,290"
          fill="none"
          stroke={stroke}
          strokeWidth="1.5"
          opacity="0.7"
        />
        <polyline
          points="400,110 680,180 680,360 400,290"
          fill="none"
          stroke={stroke}
          strokeWidth="1.5"
          opacity="0.7"
        />

        {/* Main HVAC duct — shifted in the newer scan (the +0.24m delta) */}
        <g
          stroke={stroke}
          strokeWidth={isNewer ? 10 : 8}
          strokeLinecap="round"
          opacity={0.75}
        >
          <line
            x1="160"
            y1={isNewer ? 220 : 232}
            x2="640"
            y2={isNewer ? 220 : 232}
          />
        </g>
        <g
          stroke={stroke}
          strokeWidth="4"
          strokeLinecap="round"
          opacity={0.5}
        >
          <line x1="240" y1={isNewer ? 220 : 232} x2="240" y2="360" />
          <line x1="420" y1={isNewer ? 220 : 232} x2="420" y2="360" />
          <line x1="560" y1={isNewer ? 220 : 232} x2="560" y2="360" />
        </g>

        {/* Chilled water pipe — thicker in the newer scan (+12mm OD) */}
        <line
          x1="140"
          y1="300"
          x2="660"
          y2="300"
          stroke={stroke}
          strokeWidth={isNewer ? 8 : 6}
          strokeDasharray="12 6"
          opacity="0.55"
        />

        {/* Electrical conduit run — present only on the older scan (removed) */}
        {!isNewer && (
          <g stroke={stroke} strokeWidth="3" opacity="0.55" fill="none">
            <path d="M 180 380 L 360 380 L 360 260" strokeDasharray="4 3" />
            <circle cx="180" cy="380" r="4" fill={stroke} />
            <circle cx="360" cy="260" r="4" fill={stroke} />
          </g>
        )}

        {/* Newer-only additions: sprinkler + support bracket */}
        {isNewer && (
          <g fill={stroke} opacity="0.9">
            <circle cx="500" cy="180" r="7" />
            <line
              x1="500"
              y1="187"
              x2="500"
              y2="220"
              stroke={stroke}
              strokeWidth="2"
            />
          </g>
        )}
        {isNewer && (
          <g stroke={stroke} strokeWidth="2" fill="none" opacity="0.9">
            <rect x="592" y="292" width="20" height="10" />
            <line x1="602" y1="302" x2="602" y2="320" />
          </g>
        )}

        {/* Row of static columns to anchor the scene */}
        <g fill={stroke} opacity="0.35">
          <rect x="184" y="340" width="12" height="80" />
          <rect x="384" y="380" width="12" height="80" />
          <rect x="584" y="340" width="12" height="80" />
        </g>

        {/* Scan watermark */}
        <text
          x="20"
          y="490"
          fontSize="12"
          fontWeight="700"
          fill={stroke}
          opacity="0.5"
        >
          {scan.label} · captured {scan.date}
        </text>
      </svg>
    </div>
  );
};
