"use client";

import React from "react";
import { notFound } from "next/navigation";
import { ViewerWorkspace } from "@/app/viewer/[id]/page";
import { MOCK_PROJECTS } from "@/lib/mockData";

/**
 * Dedicated route the "Simulate Mobile Upload" node lands on. Renders the
 * same 3D viewer we ship for `/viewer/sector-4-mep`, but re-brands the
 * project surface as "Boiler Room" so the demo story reads coherently
 * (uploaded plans → simulated field capture → boiler-room reconstruction).
 */
export default function BoilerRoomPage() {
  const base = MOCK_PROJECTS.find((p) => p.id === "sector-4-mep");
  if (!base) notFound();

  const boilerRoom = {
    ...base,
    id: "boiler-room",
    name: "Boiler Room",
    statusLabel: "3DGS Ready · Field-captured",
    description:
      "Boiler room captured via BuildScan mobile app after the Level 01 plan was ingested.",
  };

  return <ViewerWorkspace project={boilerRoom} />;
}
