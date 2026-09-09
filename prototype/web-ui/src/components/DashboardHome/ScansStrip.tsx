"use client";

import React, { useState } from "react";
import Image from "next/image";
import { Box, Check, Clock, Loader2, MoreHorizontal } from "lucide-react";

type StripTab = "scans" | "plans" | "reports";

interface Scan {
  id: string;
  label: string;
  date: string;
  time: string;
  status: "processed" | "processing" | "queued" | "complete";
  thumbnail: string;
}

const SCANS: Scan[] = [
  {
    id: "scan-001",
    label: "Scan 001",
    date: "Apr 22, 2025",
    time: "08:14 AM",
    status: "complete",
    thumbnail: "/thumbnails/card1_mep.png",
  },
  {
    id: "scan-002",
    label: "Scan 002",
    date: "Apr 22, 2025",
    time: "09:02 AM",
    status: "processing",
    thumbnail: "/thumbnails/card2_tower_a.png",
  },
  {
    id: "scan-003",
    label: "Scan 003",
    date: "Apr 22, 2025",
    time: "10:24 AM",
    status: "processed",
    thumbnail: "/thumbnails/card3_west_wing.png",
  },
  {
    id: "scan-004",
    label: "Scan 004",
    date: "Apr 22, 2025",
    time: "11:37 AM",
    status: "queued",
    thumbnail: "/thumbnails/card4_parking.png",
  },
  {
    id: "scan-005",
    label: "Scan 005",
    date: "Apr 22, 2025",
    time: "12:15 PM",
    status: "queued",
    thumbnail: "/thumbnails/card5_north_tower.png",
  },
  {
    id: "scan-006",
    label: "Scan 006",
    date: "Apr 22, 2025",
    time: "01:03 PM",
    status: "queued",
    thumbnail: "/thumbnails/card6_east_wing.png",
  },
];

const TABS: { id: StripTab; label: string; count: number }[] = [
  { id: "scans", label: "Scans", count: 6 },
  { id: "plans", label: "Floor Plans", count: 2 },
  { id: "reports", label: "Reports", count: 3 },
];

export const ScansStrip: React.FC = () => {
  const [active, setActive] = useState<StripTab>("scans");
  const [selectedScan, setSelectedScan] = useState<string>("scan-001");

  return (
    <section className="rounded-2xl bg-white border border-[#e2e8f0] shadow-sm">
      {/* Tabs */}
      <div className="px-4 pt-3 flex items-center gap-1 border-b border-[#f1f5f9]">
        {TABS.map((tab) => {
          const isActive = tab.id === active;
          return (
            <button
              key={tab.id}
              onClick={() => setActive(tab.id)}
              aria-pressed={isActive}
              className={`flex items-center gap-1.5 px-3 pb-3 pt-1 text-[12px] font-bold transition-colors border-b-2 cursor-pointer ${
                isActive
                  ? "border-[#2563eb] text-[#2563eb]"
                  : "border-transparent text-[#64748b] hover:text-[#0f172a]"
              }`}
            >
              <span>{tab.label}</span>
              <span
                className={`text-[10px] px-1.5 py-0.5 rounded-full font-mono ${
                  isActive
                    ? "bg-blue-50 text-[#2563eb]"
                    : "bg-slate-100 text-[#64748b]"
                }`}
              >
                {tab.count}
              </span>
            </button>
          );
        })}
      </div>

      <div className="p-3">
        {active === "scans" ? (
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2.5">
            {SCANS.map((scan) => (
              <ScanCard
                key={scan.id}
                scan={scan}
                isSelected={scan.id === selectedScan}
                onSelect={() => setSelectedScan(scan.id)}
              />
            ))}
          </div>
        ) : (
          <EmptyStripTab label={active === "plans" ? "Floor plans" : "Reports"} />
        )}
      </div>
    </section>
  );
};

const ScanCard: React.FC<{
  scan: Scan;
  isSelected: boolean;
  onSelect: () => void;
}> = ({ scan, isSelected, onSelect }) => (
  <button
    onClick={onSelect}
    className={`text-left rounded-xl border overflow-hidden bg-white transition-all cursor-pointer ${
      isSelected
        ? "border-[#2563eb] ring-2 ring-blue-100 shadow-sm"
        : "border-[#e2e8f0] hover:border-[#cbd5e1]"
    }`}
  >
    <div className="relative h-16 bg-slate-100 overflow-hidden">
      <Image src={scan.thumbnail} alt={scan.label} fill className="object-cover" />
      <button
        onClick={(e) => e.stopPropagation()}
        aria-label="More"
        className="absolute top-1 right-1 p-1 rounded-md bg-white/95 text-[#64748b] hover:text-[#0f172a] cursor-pointer"
      >
        <MoreHorizontal className="w-3 h-3" />
      </button>
      {isSelected && (
        <span className="absolute top-1 left-1 w-4 h-4 rounded-full bg-[#2563eb] flex items-center justify-center">
          <Check className="w-2.5 h-2.5 text-white" />
        </span>
      )}
    </div>
    <div className="px-2 py-1.5 space-y-1">
      <p className="text-[11px] font-bold text-[#0f172a]">{scan.label}</p>
      <p className="text-[9px] text-[#94a3b8]">
        {scan.date} · {scan.time}
      </p>
      <StatusBadge status={scan.status} />
    </div>
  </button>
);

const StatusBadge: React.FC<{ status: Scan["status"] }> = ({ status }) => {
  if (status === "complete") {
    return (
      <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded-md bg-blue-50 text-[#2563eb] text-[9px] font-bold border border-blue-100">
        <Box className="w-2.5 h-2.5" />
        Complete
      </span>
    );
  }
  if (status === "processing") {
    return (
      <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded-md bg-amber-50 text-[#d97706] text-[9px] font-bold border border-amber-100">
        <Loader2 className="w-2.5 h-2.5 animate-spin" />
        Processing
      </span>
    );
  }
  if (status === "processed") {
    return (
      <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded-md bg-emerald-50 text-[#059669] text-[9px] font-bold border border-emerald-100">
        <Check className="w-2.5 h-2.5" />
        3DGS
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded-md bg-slate-100 text-[#64748b] text-[9px] font-bold border border-slate-200">
      <Clock className="w-2.5 h-2.5" />
      Queued
    </span>
  );
};

const EmptyStripTab: React.FC<{ label: string }> = ({ label }) => (
  <div className="py-8 flex flex-col items-center justify-center text-center gap-1.5">
    <p className="text-[11px] font-bold text-[#64748b]">{label} will appear here</p>
    <p className="text-[10px] text-[#94a3b8]">
      Wire this tab in a follow-up step.
    </p>
  </div>
);
