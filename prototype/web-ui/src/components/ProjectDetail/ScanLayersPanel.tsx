"use client";

import React from "react";
import { Eye, EyeOff, Crosshair } from "lucide-react";
import { FIXTURE_COLORS, ScanInfo } from "@/components/Viewer3D/scanTypes";

/**
 * Layers panel for labelled scans (scan bundles, see scanTypes.ts): room summary, semantic groups with
 * show / hide, tint-by-class and fixture-marker switches, wall areas and the detected fixtures (click to
 * fly the camera there). The mock projects keep their own Semantic Layers panel.
 */
const GROUP_LABELS: Record<string, string> = {
  floor: "Floor",
  ceiling: "Ceiling",
  walls: "Walls",
  openings: "Doors & windows",
  electrical: "Switches, sockets & lights",
  other: "Furniture & other",
};

const pretty = (id: string) => {
  const m = id.match(/^(.*)_(\d+)$/);
  const name = (m ? m[1] : id).replace(/_/g, " ");
  return `${name.charAt(0).toUpperCase()}${name.slice(1)}${m ? ` ${m[2]}` : ""}`;
};

const splatCount = (n: number) => (n >= 1000 ? `${(n / 1000).toFixed(n >= 100000 ? 0 : 1)}k splats` : `${n} splats`);

interface ScanLayersPanelProps {
  scan: ScanInfo | null;
  hiddenGroups: string[];
  onToggleGroup: (key: string) => void;
  tintByClass: boolean;
  onToggleTint: () => void;
  showFixtures: boolean;
  onToggleFixtures: () => void;
  onFlyTo: (point: [number, number, number]) => void;
}

const Switch: React.FC<{ label: string; on: boolean; onClick: () => void }> = ({ label, on, onClick }) => (
  <button
    onClick={onClick}
    aria-pressed={on}
    className={`flex-1 px-2.5 py-1.5 rounded-lg text-[11px] font-bold transition-colors cursor-pointer border ${
      on ? "bg-blue-50 text-[#2563eb] border-blue-100" : "bg-white text-[#64748b] border-[#e2e8f0] hover:text-[#0f172a]"
    }`}
  >
    {label}
  </button>
);

export const ScanLayersPanel: React.FC<ScanLayersPanelProps> = ({
  scan,
  hiddenGroups,
  onToggleGroup,
  tintByClass,
  onToggleTint,
  showFixtures,
  onToggleFixtures,
  onFlyTo,
}) => {
  if (!scan) {
    return <p className="pt-3 text-xs text-[#64748b]">Loading scan labels…</p>;
  }
  const netWall = scan.walls.reduce((s, w) => s + w.net_area, 0);
  return (
    <div className="space-y-4 pt-2">
      <div className="grid grid-cols-3 gap-2">
        {[
          ["Floor", scan.floor_area !== null ? `${scan.floor_area.toFixed(1)} m²` : "–"],
          ["Ceiling", scan.ceiling_height !== null ? `${scan.ceiling_height.toFixed(2)} m` : "–"],
          ["Net walls", `${netWall.toFixed(1)} m²`],
        ].map(([k, v]) => (
          <div key={k} className="p-2 rounded-xl bg-slate-50 border border-[#f1f5f9]">
            <div className="text-[10px] text-[#64748b] font-semibold">{k}</div>
            <div className="text-xs font-bold text-[#0f172a]">{v}</div>
          </div>
        ))}
      </div>

      <div className="space-y-2">
        {scan.groups.map((g) => {
          const isVisible = !hiddenGroups.includes(g.key);
          return (
            <button
              key={g.key}
              onClick={() => onToggleGroup(g.key)}
              aria-pressed={isVisible}
              className={`w-full flex items-center justify-between p-2.5 rounded-xl border text-xs font-semibold transition-all cursor-pointer ${
                isVisible ? "bg-white border-[#e2e8f0] shadow-sm text-[#0f172a]" : "bg-slate-50 border-transparent text-[#94a3b8]"
              }`}
            >
              <div className="flex items-center gap-2.5 min-w-0">
                <span className={`w-2.5 h-2.5 rounded-full shrink-0 ${isVisible ? "" : "opacity-40"}`} style={{ background: g.color }} />
                <span className="truncate">{GROUP_LABELS[g.key] ?? g.key}</span>
              </div>
              <div className="flex items-center gap-2 shrink-0 pl-2">
                <span className="text-[10px] text-[#64748b]">{splatCount(g.splats)}</span>
                {isVisible ? <Eye className="w-3.5 h-3.5 text-[#2563eb]" /> : <EyeOff className="w-3.5 h-3.5" />}
              </div>
            </button>
          );
        })}
      </div>

      <div className="flex gap-2">
        <Switch label="Tint by class" on={tintByClass} onClick={onToggleTint} />
        <Switch label="Fixture markers" on={showFixtures} onClick={onToggleFixtures} />
      </div>

      <div>
        <h3 className="text-[11px] font-bold text-[#0f172a] mb-2">Walls</h3>
        <div className="space-y-1">
          {scan.walls.map((w) => (
            <div key={w.id} className="flex items-center justify-between text-[11px] text-[#334155]">
              <span>
                Wall {w.id} · {w.length.toFixed(2)} × {w.height.toFixed(2)} m
              </span>
              <span className="text-[#64748b]">
                {w.net_area.toFixed(1)} m² net{w.openings.length ? ` · ${w.openings.length} opening${w.openings.length > 1 ? "s" : ""}` : ""}
              </span>
            </div>
          ))}
        </div>
      </div>

      <div>
        <h3 className="text-[11px] font-bold text-[#0f172a] mb-2">Detected fixtures ({scan.fixtures.length})</h3>
        <div className="space-y-1.5">
          {scan.fixtures.map((f) => (
            <button
              key={f.id}
              onClick={() => onFlyTo(f.position)}
              title="Show in 3D"
              className="w-full flex items-center justify-between gap-2 p-2 rounded-xl border border-[#f1f5f9] bg-white hover:border-blue-100 hover:bg-blue-50/40 text-left transition-colors cursor-pointer"
            >
              <div className="flex items-center gap-2 min-w-0">
                <span className="w-2.5 h-2.5 rounded-full shrink-0" style={{ background: FIXTURE_COLORS[f.cls] ?? "#94a3b8" }} />
                <div className="min-w-0">
                  <div className="text-[11px] font-bold text-[#0f172a] truncate">{pretty(f.id)}</div>
                  <div className="text-[10px] text-[#64748b] truncate">
                    {f.wall !== null ? `Wall ${f.wall} · ` : ""}
                    {f.height_above_floor.toFixed(2)} m up · {f.width.toFixed(2)} × {f.height.toFixed(2)} m · {f.views} views
                  </div>
                </div>
              </div>
              <Crosshair className="w-3.5 h-3.5 text-[#94a3b8] shrink-0" />
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
