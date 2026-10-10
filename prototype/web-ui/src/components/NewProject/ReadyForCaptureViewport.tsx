"use client";

import React, { useState } from "react";
import Link from "next/link";
import {
  ArrowLeft,
  CheckCircle2,
  Info,
  Loader2,
  Smartphone,
  Terminal,
} from "lucide-react";
import { FloorPlanCanvas } from "@/components/FloorPlan/FloorPlanCanvas";
import { MOCK_BUILDING_PLANS } from "@/lib/mockData";

type NodeState = "empty" | "syncing" | "verified";

/** Where the "Simulate Mobile Upload" node lands on the plan. */
const NODE_TOP_PCT = 54;
const NODE_LEFT_PCT = 72;
const SYNC_MS = 3000;

/**
 * The "extracted plan" surfaced by the OCR simulation is — for POC — one of
 * our hand-authored Tower A floors. Same visual language as everywhere else
 * in the app, no rendering fork, just displayed with status nodes hidden
 * (fresh site, nothing scanned yet). If the fixture is ever removed the
 * viewport quietly falls back to a placeholder message.
 */
const EXTRACTED_PLAN = MOCK_BUILDING_PLANS[0]; // Tower A
const EXTRACTED_FLOOR = EXTRACTED_PLAN?.floors[0] ?? null; // Floor 5

interface ReadyForCaptureViewportProps {
  projectName: string;
}

export const ReadyForCaptureViewport: React.FC<ReadyForCaptureViewportProps> = ({
  projectName,
}) => {
  const [nodeState, setNodeState] = useState<NodeState>("empty");

  const startSimulation = () => {
    if (nodeState !== "empty") return;
    setNodeState("syncing");
    window.setTimeout(() => setNodeState("verified"), SYNC_MS);
  };

  const resetSimulation = () => setNodeState("empty");

  return (
    <div className="flex flex-col h-full min-h-0 bg-[#eef3f9]">
      {/* Persistent instruction banner */}
      <div className="shrink-0 flex items-center gap-3 px-5 py-3 bg-[#0f172a] text-white border-b border-slate-800">
        <Smartphone className="w-4 h-4 text-[#38bdf8] shrink-0" />
        <p className="text-[12px] font-medium leading-snug">
          <span className="font-bold text-white">Grid initialized.</span>{" "}
          <span className="text-slate-300">
            Open the BuildScan mobile app on-site, select a zone on this map,
            and initiate a spatial capture to begin 3D reconstruction.
          </span>
        </p>
        <div className="ml-auto flex items-center gap-2 shrink-0">
          <span className="inline-flex items-center gap-1 text-[10px] font-mono font-bold text-emerald-400">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            AWAITING FIELD SYNC
          </span>
        </div>
      </div>

      {/* Header strip: project title + dev toggle */}
      <div className="shrink-0 flex items-center justify-between gap-3 px-5 py-3 border-b border-[#e2e8f0] bg-white">
        <div className="flex items-center gap-3 min-w-0">
          <Link
            href="/projects"
            className="p-1.5 rounded-lg text-[#64748b] hover:text-[#0f172a] hover:bg-slate-100 cursor-pointer"
            aria-label="Back to Projects"
          >
            <ArrowLeft className="w-4 h-4" />
          </Link>
          <div className="min-w-0">
            <h1 className="text-sm font-extrabold text-[#0f172a] tracking-tight truncate">
              {projectName}
            </h1>
            <p className="text-[10px] text-[#64748b]">
              Level 01 · Ready for capture · 0 rooms scanned
            </p>
          </div>
        </div>

        <button
          onClick={nodeState === "empty" ? startSimulation : resetSimulation}
          disabled={nodeState === "syncing"}
          className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[10px] font-mono font-bold cursor-pointer transition-colors border ${
            nodeState === "empty"
              ? "bg-slate-900 border-slate-800 text-emerald-400 hover:bg-slate-800"
              : nodeState === "syncing"
              ? "bg-amber-50 border-amber-200 text-[#92400e] cursor-wait"
              : "bg-emerald-50 border-emerald-200 text-[#065f46]"
          }`}
        >
          <Terminal className="w-3 h-3" />
          {nodeState === "empty" && "SIMULATE MOBILE UPLOAD"}
          {nodeState === "syncing" && "STREAMING TELEMETRY..."}
          {nodeState === "verified" && "RESET DEMO"}
        </button>
      </div>

      {/* Plan viewport — reuses the app's own FloorPlanCanvas so the
          extracted plan looks like every other floor plan in the product
          (walls, doors, dimension ruler, compass, room labels). Status
          nodes are suppressed until the field team runs a real capture. */}
      <div className="relative flex-1 min-h-0">
        {EXTRACTED_FLOOR ? (
          <FloorPlanCanvas
            floor={EXTRACTED_FLOOR}
            buildingName={projectName}
            targetProjectId="not-used-in-ready-state"
            hideStatusNodes
          />
        ) : (
          <div className="absolute inset-6 rounded-2xl border border-dashed border-[#cbd5e1] bg-white flex items-center justify-center text-xs text-[#94a3b8]">
            Extracted plan preview unavailable.
          </div>
        )}

        {/* Scan node — only visible once the simulation has started */}
        {nodeState !== "empty" && (
          <ScanNode
            state={nodeState}
            topPct={NODE_TOP_PCT}
            leftPct={NODE_LEFT_PCT}
          />
        )}

        {/* Empty-state helper card, centred over the plan while no scans exist */}
        {nodeState === "empty" && (
          <div className="pointer-events-none absolute inset-0 flex items-center justify-center">
            <div className="px-4 py-3 rounded-2xl bg-white/95 backdrop-blur-md border border-dashed border-[#cbd5e1] shadow-md flex items-center gap-2.5">
              <Info className="w-4 h-4 text-[#2563eb] shrink-0" />
              <div>
                <p className="text-[12px] font-bold text-[#0f172a]">
                  No 3D scans yet
                </p>
                <p className="text-[10px] text-[#64748b]">
                  Nodes appear here as the field team captures rooms.
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

/* --------------------------- Scan node --------------------------- */

interface ScanNodeProps {
  state: Exclude<NodeState, "empty">;
  topPct: number;
  leftPct: number;
}

const ScanNode: React.FC<ScanNodeProps> = ({ state, topPct, leftPct }) => {
  const isSyncing = state === "syncing";

  const nodeInner = (
    <div className="relative -translate-x-1/2 -translate-y-1/2">
      {/* Pulse ring for syncing state */}
      {isSyncing && (
        <span
          className="absolute inset-0 -m-2 rounded-full animate-ping"
          style={{ backgroundColor: "rgba(245, 158, 11, 0.45)" }}
        />
      )}

      {/* Core node */}
      <div
        className={`relative w-8 h-8 rounded-full flex items-center justify-center shadow-lg border-4 border-white ${
          isSyncing ? "bg-[#f59e0b]" : "bg-[#10b981]"
        }`}
      >
        {isSyncing ? (
          <Loader2 className="w-3.5 h-3.5 text-white animate-spin" />
        ) : (
          <CheckCircle2 className="w-4 h-4 text-white" />
        )}
      </div>

      {/* Label chip below */}
      <div className="absolute top-full left-1/2 -translate-x-1/2 mt-2 whitespace-nowrap">
        <div
          className={`px-2.5 py-1 rounded-lg shadow-md text-[10px] font-bold flex items-center gap-1.5 ${
            isSyncing
              ? "bg-amber-50 text-[#92400e] border border-amber-200"
              : "bg-emerald-50 text-[#065f46] border border-emerald-200"
          }`}
        >
          <span
            className="w-1.5 h-1.5 rounded-full"
            style={{ backgroundColor: isSyncing ? "#f59e0b" : "#10b981" }}
          />
          {isSyncing ? "Syncing · 3DGS Training" : "Metric Verified"}
        </div>
      </div>
    </div>
  );

  if (isSyncing) {
    return (
      <div
        className="absolute cursor-wait"
        style={{ top: `${topPct}%`, left: `${leftPct}%` }}
        aria-label="Scan syncing"
        role="img"
      >
        {nodeInner}
      </div>
    );
  }

  // Verified — clickable, routes to /workspace/boiler-room.
  return (
    <Link
      href="/workspace/boiler-room"
      className="absolute cursor-pointer group"
      style={{ top: `${topPct}%`, left: `${leftPct}%` }}
      aria-label="Open Boiler Room 3D model"
    >
      <div className="group-hover:scale-110 transition-transform">
        {nodeInner}
      </div>
    </Link>
  );
};
