"use client";

import React from "react";
import { BuildingFloor } from "@/lib/mockData";

interface FloorTabStripProps {
  floors: readonly BuildingFloor[];
  activeFloorId: string;
  onSelect: (floorId: string) => void;
}

export const FloorTabStrip: React.FC<FloorTabStripProps> = ({
  floors,
  activeFloorId,
  onSelect,
}) => (
  <div
    role="tablist"
    aria-label="Floors"
    className="inline-flex items-center gap-0.5 p-1 rounded-xl bg-[#f1f5f9] border border-[#e2e8f0]"
  >
    {floors.map((floor) => {
      const isActive = floor.id === activeFloorId;
      return (
        <button
          key={floor.id}
          role="tab"
          aria-selected={isActive}
          onClick={() => onSelect(floor.id)}
          className={`flex flex-col items-start px-4 py-1.5 rounded-lg transition-all cursor-pointer ${
            isActive
              ? "bg-white shadow-sm"
              : "hover:bg-white/60"
          }`}
        >
          <span
            className={`text-[11px] font-bold ${
              isActive ? "text-[#2563eb]" : "text-[#0f172a]"
            }`}
          >
            {floor.label}
          </span>
          <span
            className={`text-[10px] font-medium ${
              isActive ? "text-[#64748b]" : "text-[#94a3b8]"
            }`}
          >
            {floor.discipline}
          </span>
        </button>
      );
    })}
  </div>
);
