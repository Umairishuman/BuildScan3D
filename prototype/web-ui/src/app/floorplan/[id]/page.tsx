"use client";

import React, { use, useEffect, useState } from "react";
import Link from "next/link";
import { ArrowLeft, Info, Loader2, Plus, Smartphone } from "lucide-react";
import { AppShell } from "@/components/AppShell";
import { FloorPlanCanvas } from "@/components/FloorPlan/FloorPlanCanvas";
import { FloorTabStrip } from "@/components/FloorPlan/FloorTabStrip";
import { BuildingPlan, MOCK_PROJECTS } from "@/lib/mockData";
import { findAnyBuildingPlan } from "@/lib/userPlans";

interface FloorPlanPageProps {
  params: Promise<{ id: string }>;
}

/**
 * The plan lookup consults `localStorage` for user-created plans, which is
 * only available in the browser. So we defer resolution to a `useEffect` on
 * the client: `undefined` = still loading (SSR + first render), `null` = the
 * lookup finished and there's nothing, `BuildingPlan` = ready to render.
 */
type PlanState = BuildingPlan | null | undefined;

export default function FloorPlanPage({ params }: FloorPlanPageProps) {
  const { id: projectId } = use(params);
  const [plan, setPlan] = useState<PlanState>(undefined);

  useEffect(() => {
    // Sync from localStorage (external system) into React state — the setState
    // is intentional here; suppress the effect-purity rule for this line.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setPlan(findAnyBuildingPlan(projectId) ?? null);
  }, [projectId]);

  if (plan === undefined) return <FloorPlanLoading />;
  if (plan === null) return <FloorPlanNotFound projectId={projectId} />;
  return <FloorPlanWorkspace plan={plan} />;
}

/* --------------------------- Loading + Not-Found --------------------------- */

const FloorPlanLoading: React.FC = () => (
  <AppShell activeNav="floorplan">
    <div className="flex-1 min-h-0 flex items-center justify-center p-8">
      <div className="flex items-center gap-2 text-[#64748b]">
        <Loader2 className="w-4 h-4 animate-spin" />
        <span className="text-xs font-bold">Loading floor plan…</span>
      </div>
    </div>
  </AppShell>
);

const FloorPlanNotFound: React.FC<{ projectId: string }> = ({ projectId }) => (
  <AppShell activeNav="floorplan">
    <div className="flex-1 min-h-0 flex items-center justify-center p-8">
      <div className="max-w-md text-center space-y-3 p-8 rounded-2xl bg-white border border-dashed border-[#e2e8f0] shadow-sm">
        <h2 className="text-sm font-bold text-[#0f172a]">
          Floor plan not found
        </h2>
        <p className="text-xs text-[#64748b] leading-relaxed">
          No plan matches <span className="font-mono">{projectId}</span>. User-
          uploaded plans live in the browser they were created in — if you saved
          it in another browser, it won&apos;t be visible here.
        </p>
        <Link
          href="/projects"
          className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-[#2563eb] hover:bg-[#1d4ed8] text-white text-xs font-bold shadow-sm cursor-pointer"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          Back to Projects
        </Link>
      </div>
    </div>
  </AppShell>
);

/* --------------------------- Workspace --------------------------- */

function FloorPlanWorkspace({ plan }: { plan: BuildingPlan }) {
  const [activeFloorId, setActiveFloorId] = useState(plan.floors[0].id);
  const activeFloor =
    plan.floors.find((f) => f.id === activeFloorId) ?? plan.floors[0];

  // For mock plans the URL id matches a MOCK_PROJECTS row; user plans don't
  // have one, so fall back to the building name.
  const mockProject = MOCK_PROJECTS.find((p) => p.id === plan.projectId);
  const displayName = mockProject?.name ?? plan.buildingName;

  const readyCount = activeFloor.rooms.filter((r) => r.status === "ready").length;
  const processingCount = activeFloor.rooms.filter((r) => r.status === "processing").length;
  const completeCount = activeFloor.rooms.filter((r) => r.status === "complete").length;

  return (
    <AppShell
      variant="fluid"
      activeNav="floorplan"
      breadcrumbs={[
        { label: "All Projects", href: "/projects" },
        { label: displayName },
      ]}
    >
      <div className="flex-1 min-h-0 flex flex-col bg-[#eef3f9]">
        {/* Header strip: title + floor tabs + right-side actions */}
        <div className="shrink-0 px-6 py-4 border-b border-[#e2e8f0] bg-white flex items-center justify-between gap-4">
          <div className="min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <h1 className="text-base font-bold text-[#0f172a] truncate">
                {plan.buildingName} — Floor Plan
              </h1>
              <span className="text-[11px] px-2 py-0.5 rounded-full bg-blue-50 text-[#2563eb] font-bold border border-blue-100">
                {plan.floors.length} floors
              </span>
              {plan.isUserCreated && (
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-50 text-[#059669] font-bold border border-emerald-100">
                  User-created
                </span>
              )}
            </div>
            <p className="text-[11px] text-[#64748b]">
              {activeFloor.label} · {activeFloor.discipline} ·{" "}
              <span className="font-mono font-bold text-[#0f172a]">
                {activeFloor.totalArea}
              </span>{" "}
              · {activeFloor.rooms.length} rooms
            </p>
          </div>

          <div className="flex items-center gap-3">
            <FloorTabStrip
              floors={plan.floors}
              activeFloorId={activeFloorId}
              onSelect={setActiveFloorId}
            />

            <NewCaptureButton />
          </div>
        </div>

        {/* Canvas */}
        <div className="relative flex-1 min-h-0">
          <FloorPlanCanvas
            floor={activeFloor}
            buildingName={plan.buildingName}
            targetProjectId={plan.projectId}
          />

          {/* Floating legend, top-right of the plan */}
          <div className="absolute top-4 right-4 z-10">
            <LegendCard
              readyCount={readyCount}
              processingCount={processingCount}
              completeCount={completeCount}
            />
          </div>
        </div>
      </div>
    </AppShell>
  );
}

/* ------------------------------------------------------------------ */
/* Legend                                                              */
/* ------------------------------------------------------------------ */

interface LegendCardProps {
  readyCount: number;
  processingCount: number;
  completeCount: number;
}

const LegendCard: React.FC<LegendCardProps> = ({
  readyCount,
  processingCount,
  completeCount,
}) => (
  <div className="w-56 p-3 rounded-xl bg-white/95 backdrop-blur-md border border-[#e2e8f0] shadow-md">
    <div className="flex items-center gap-1.5 mb-2">
      <Info className="w-3.5 h-3.5 text-[#2563eb]" />
      <h3 className="text-[11px] font-bold text-[#0f172a]">Room Status</h3>
    </div>

    <ul className="space-y-1.5">
      <LegendRow color="#10b981" label="Ready" count={readyCount} description="Open in 3D" />
      <LegendRow
        color="#f59e0b"
        label="Processing"
        count={processingCount}
        description="Scan in progress"
        animated
      />
      <LegendRow
        color="#14b8a6"
        label="Complete"
        count={completeCount}
        description="Signed-off scan"
      />
    </ul>

    <p className="mt-2 pt-2 border-t border-[#f1f5f9] text-[10px] text-[#64748b] leading-relaxed">
      Click any Ready or Complete room to open its captured 3D model.
    </p>
  </div>
);

const LegendRow: React.FC<{
  color: string;
  label: string;
  count: number;
  description: string;
  animated?: boolean;
}> = ({ color, label, count, description, animated = false }) => (
  <li className="flex items-center gap-2">
    <span className="relative flex items-center justify-center w-4 shrink-0">
      <span
        className="w-2.5 h-2.5 rounded-full"
        style={{ backgroundColor: color }}
      />
      {animated && (
        <span
          className="absolute w-2.5 h-2.5 rounded-full animate-ping"
          style={{ backgroundColor: color, opacity: 0.5 }}
        />
      )}
    </span>
    <div className="flex-1 min-w-0 flex items-baseline justify-between gap-2">
      <span className="text-[11px] font-bold text-[#0f172a]">{label}</span>
      <span className="text-[10px] text-[#64748b] truncate">{description}</span>
    </div>
    <span className="text-[10px] font-mono font-bold text-[#0f172a] tabular-nums">
      {count}
    </span>
  </li>
);

/* ------------------------------------------------------------------ */
/* New Capture button (disabled with mobile-app tooltip)               */
/* ------------------------------------------------------------------ */

const NewCaptureButton: React.FC = () => (
  <div className="relative group">
    <button
      disabled
      className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-slate-100 text-[#94a3b8] text-[11px] font-bold border border-[#e2e8f0] cursor-not-allowed"
    >
      <Plus className="w-3.5 h-3.5" />
      New Capture
    </button>
    <div className="pointer-events-none absolute top-full right-0 mt-2 w-56 opacity-0 group-hover:opacity-100 transition-opacity">
      <div className="p-2 rounded-xl bg-[#0f172a] text-white shadow-lg flex items-center gap-2">
        <Smartphone className="w-3.5 h-3.5 text-[#38bdf8] shrink-0" />
        <p className="text-[10px] leading-snug">
          Initiate captures from the BuildScan mobile app.
        </p>
      </div>
    </div>
  </div>
);
