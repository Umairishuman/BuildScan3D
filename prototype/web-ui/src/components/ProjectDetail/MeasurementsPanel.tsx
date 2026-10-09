"use client";

import React, { useMemo, useState } from "react";
import {
  ArrowUpDown,
  MoreHorizontal,
  MoveVertical,
  Plus,
  Ruler,
  Search,
  Slash,
  Trash2,
  Waves,
} from "lucide-react";
import { MeasurementRecord } from "@/components/Viewer3D/MeasurementTool";
import {
  MOCK_SAVED_MEASUREMENTS,
  SavedMeasurement,
  SavedMeasurementKind,
} from "@/lib/mockData";

export type MeasurementSubTab = "saved" | "current" | "tools";

interface MeasurementsPanelProps {
  subTab: MeasurementSubTab;
  measurements: MeasurementRecord[];
  isMeasureMode: boolean;
  onToggleMeasureMode: () => void;
  onDeleteMeasurement: (id: string) => void;
  onClearAll: () => void;
}

const KIND_ICON: Record<SavedMeasurementKind, React.ComponentType<{ className?: string }>> = {
  length: Ruler,
  height: MoveVertical,
  pipe: Waves,
  width: ArrowUpDown,
  beam: Slash,
};

const KIND_TINT: Record<SavedMeasurementKind, string> = {
  length: "bg-blue-50 text-[#2563eb]",
  height: "bg-emerald-50 text-[#059669]",
  pipe: "bg-sky-50 text-[#0369a1]",
  width: "bg-amber-50 text-[#d97706]",
  beam: "bg-slate-100 text-[#475569]",
};

export const MeasurementsPanel: React.FC<MeasurementsPanelProps> = ({
  subTab,
  measurements,
  isMeasureMode,
  onToggleMeasureMode,
  onDeleteMeasurement,
  onClearAll,
}) => {
  return (
    <div className="flex-1 min-h-0 flex flex-col">
      <div className="flex-1 min-h-0 overflow-y-auto px-3 pb-3">
        {subTab === "saved" && <SavedTab />}
        {subTab === "current" && (
          <CurrentTab
            measurements={measurements}
            isMeasureMode={isMeasureMode}
            onDelete={onDeleteMeasurement}
            onClearAll={onClearAll}
          />
        )}
        {subTab === "tools" && (
          <ToolsTab
            isMeasureMode={isMeasureMode}
            onToggleMeasureMode={onToggleMeasureMode}
            hasMeasurements={measurements.length > 0}
            onClearAll={onClearAll}
          />
        )}
      </div>

      <div className="px-3 pb-4 pt-2 border-t border-[#f1f5f9] shrink-0">
        <button
          onClick={onToggleMeasureMode}
          className={`w-full flex items-center justify-center gap-2 px-3 py-2.5 rounded-xl text-[11px] font-bold shadow-sm transition-colors cursor-pointer ${
            isMeasureMode
              ? "bg-[#0f172a] hover:bg-[#1e293b] text-white"
              : "bg-[#2563eb] hover:bg-[#1d4ed8] text-white"
          }`}
        >
          <Plus className="w-3.5 h-3.5" />
          <span>
            {isMeasureMode ? "Finish Measuring" : "New Measurement"}
          </span>
        </button>
      </div>
    </div>
  );
};

/* ---------------------------- Saved ---------------------------- */

const SavedTab: React.FC = () => {
  const [query, setQuery] = useState("");

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return MOCK_SAVED_MEASUREMENTS;
    return MOCK_SAVED_MEASUREMENTS.filter(
      (m) =>
        m.label.toLowerCase().includes(q) ||
        m.value.toLowerCase().includes(q)
    );
  }, [query]);

  return (
    <div className="pt-1">
      <div className="relative mb-3">
        <Search className="w-3.5 h-3.5 text-[#94a3b8] absolute left-2.5 top-1/2 -translate-y-1/2" />
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search measurements..."
          className="w-full pl-8 pr-3 py-2 text-[11px] font-medium text-[#0f172a] placeholder:text-[#94a3b8] bg-slate-50 border border-[#e2e8f0] rounded-lg focus:outline-none focus:border-[#2563eb] focus:bg-white transition-colors"
        />
      </div>

      {filtered.length === 0 ? (
        <EmptyState label="No saved measurements match that search." />
      ) : (
        <ul className="space-y-1.5">
          {filtered.map((m) => (
            <SavedRow key={m.id} measurement={m} />
          ))}
        </ul>
      )}
    </div>
  );
};

const SavedRow: React.FC<{ measurement: SavedMeasurement }> = ({ measurement }) => {
  const Icon = KIND_ICON[measurement.kind];
  return (
    <li className="group flex items-start gap-2.5 p-2.5 rounded-xl border border-transparent hover:border-[#e2e8f0] hover:bg-slate-50 transition-colors">
      <span
        className={`w-7 h-7 rounded-lg flex items-center justify-center shrink-0 ${
          KIND_TINT[measurement.kind]
        }`}
      >
        <Icon className="w-3.5 h-3.5" />
      </span>
      <div className="flex-1 min-w-0">
        <div className="flex items-baseline justify-between gap-2">
          <span className="text-[13px] font-bold font-mono text-[#0f172a] truncate">
            {measurement.value}
          </span>
          <span className="text-[10px] text-[#94a3b8] shrink-0 whitespace-nowrap">
            {measurement.timestamp}
          </span>
        </div>
        <p className="text-[11px] text-[#64748b] truncate">{measurement.label}</p>
      </div>
      <button
        type="button"
        className="opacity-0 group-hover:opacity-100 p-1 rounded-md text-[#94a3b8] hover:text-[#0f172a] hover:bg-white transition-all cursor-pointer"
        aria-label="More options"
      >
        <MoreHorizontal className="w-3.5 h-3.5" />
      </button>
    </li>
  );
};

/* ---------------------------- Current ---------------------------- */

interface CurrentTabProps {
  measurements: MeasurementRecord[];
  isMeasureMode: boolean;
  onDelete: (id: string) => void;
  onClearAll: () => void;
}

const CurrentTab: React.FC<CurrentTabProps> = ({
  measurements,
  isMeasureMode,
  onDelete,
  onClearAll,
}) => {
  if (measurements.length === 0) {
    return (
      <div className="pt-1">
        <EmptyState
          label={
            isMeasureMode
              ? "Measure mode is on — click two points on the model."
              : "No measurements captured in this session yet."
          }
        />
      </div>
    );
  }

  return (
    <div className="pt-1">
      <div className="flex items-center justify-between mb-2 px-1">
        <span className="text-[10px] font-bold uppercase tracking-wider text-[#94a3b8]">
          Session · {measurements.length}
        </span>
        <button
          onClick={onClearAll}
          className="text-[10px] font-bold text-[#dc2626] hover:text-[#b91c1c] cursor-pointer"
        >
          Clear all
        </button>
      </div>
      <ul className="space-y-1.5">
        {measurements.map((m, idx) => (
          <li
            key={m.id}
            className="group flex items-start gap-2.5 p-2.5 rounded-xl border border-transparent hover:border-[#e2e8f0] hover:bg-slate-50 transition-colors"
          >
            <span className="w-7 h-7 rounded-lg flex items-center justify-center shrink-0 bg-sky-50 text-[#0369a1]">
              <Ruler className="w-3.5 h-3.5" />
            </span>
            <div className="flex-1 min-w-0">
              <div className="flex items-baseline justify-between gap-2">
                <span className="text-[13px] font-bold font-mono text-[#0f172a]">
                  {m.distanceMeters.toFixed(2)} m
                </span>
                <span className="text-[10px] text-[#94a3b8] font-mono shrink-0">
                  #{idx + 1}
                </span>
              </div>
              <p className="text-[11px] text-[#64748b] truncate">{m.name}</p>
            </div>
            <button
              type="button"
              onClick={() => onDelete(m.id)}
              className="opacity-0 group-hover:opacity-100 p-1 rounded-md text-[#94a3b8] hover:text-[#dc2626] hover:bg-white transition-all cursor-pointer"
              aria-label={`Delete ${m.name}`}
            >
              <Trash2 className="w-3.5 h-3.5" />
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
};

/* ---------------------------- Tools ---------------------------- */

interface ToolsTabProps {
  isMeasureMode: boolean;
  onToggleMeasureMode: () => void;
  hasMeasurements: boolean;
  onClearAll: () => void;
}

const ToolsTab: React.FC<ToolsTabProps> = ({
  isMeasureMode,
  onToggleMeasureMode,
  hasMeasurements,
  onClearAll,
}) => {
  return (
    <div className="pt-1 space-y-3">
      <div className="p-3 rounded-xl border border-[#e2e8f0] bg-white">
        <div className="flex items-center justify-between gap-2">
          <div className="min-w-0">
            <p className="text-[11px] font-bold text-[#0f172a]">Measure Mode</p>
            <p className="text-[10px] text-[#64748b] mt-0.5 leading-relaxed">
              Click two points on the 3D model to record a metric distance.
            </p>
          </div>
          <button
            role="switch"
            aria-checked={isMeasureMode}
            onClick={onToggleMeasureMode}
            className={`relative w-9 h-5 rounded-full shrink-0 transition-colors cursor-pointer ${
              isMeasureMode ? "bg-[#2563eb]" : "bg-slate-200"
            }`}
          >
            <span
              className={`absolute top-0.5 w-4 h-4 rounded-full bg-white shadow-sm transition-transform ${
                isMeasureMode ? "translate-x-4" : "translate-x-0.5"
              }`}
            />
          </button>
        </div>
      </div>

      <div className="p-3 rounded-xl border border-[#e2e8f0] bg-white">
        <p className="text-[11px] font-bold text-[#0f172a] mb-2">Measurement Type</p>
        <div className="grid grid-cols-3 gap-1.5">
          {(["length", "height", "pipe", "width", "beam"] as SavedMeasurementKind[]).map(
            (kind) => {
              const Icon = KIND_ICON[kind];
              const isActive = kind === "length";
              return (
                <button
                  key={kind}
                  className={`flex flex-col items-center gap-1 px-2 py-2 rounded-lg text-[10px] font-bold capitalize transition-colors cursor-pointer ${
                    isActive
                      ? "bg-blue-50 text-[#2563eb] border border-blue-100"
                      : "bg-slate-50 text-[#64748b] border border-transparent hover:bg-slate-100"
                  }`}
                >
                  <Icon className="w-3.5 h-3.5" />
                  <span>{kind}</span>
                </button>
              );
            }
          )}
        </div>
        <p className="text-[10px] text-[#94a3b8] mt-2 leading-relaxed">
          Length is the only mode wired into the canvas in this build; the rest ship in Stage 5.
        </p>
      </div>

      <div className="p-3 rounded-xl border border-[#e2e8f0] bg-white">
        <p className="text-[11px] font-bold text-[#0f172a] mb-2">Session</p>
        <button
          onClick={onClearAll}
          disabled={!hasMeasurements}
          className="w-full flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg text-[11px] font-bold border border-[#e2e8f0] text-[#dc2626] hover:bg-red-50 hover:border-red-200 disabled:text-[#cbd5e1] disabled:hover:bg-transparent disabled:hover:border-[#e2e8f0] disabled:cursor-not-allowed cursor-pointer transition-colors"
        >
          <Trash2 className="w-3.5 h-3.5" />
          <span>Clear session measurements</span>
        </button>
      </div>
    </div>
  );
};

/* ---------------------------- Shared ---------------------------- */

const EmptyState: React.FC<{ label: string }> = ({ label }) => (
  <div className="flex flex-col items-center justify-center text-center gap-2 px-4 py-8 rounded-xl border border-dashed border-[#e2e8f0] bg-[#f8fafc]">
    <Ruler className="w-5 h-5 text-[#cbd5e1]" />
    <p className="text-[11px] text-[#94a3b8] leading-relaxed">{label}</p>
  </div>
);
