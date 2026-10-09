"use client";

import React from "react";
import Link from "next/link";
import Image from "next/image";
import {
  Bell,
  Command,
  Loader2,
  Menu,
  Radar,
  Search,
  ShieldCheck,
  Sparkles,
  X,
} from "lucide-react";

interface StatusPillDef {
  label: string;
  value: string;
  Icon: React.ComponentType<{ className?: string }>;
  tone: "green" | "amber" | "blue" | "slate";
  animated?: boolean;
}

const PILLS: StatusPillDef[] = [
  {
    label: "Metric Verified",
    value: "98.7% accuracy",
    Icon: ShieldCheck,
    tone: "green",
  },
  {
    label: "3DGS Rendering Active",
    value: "Real-time · 60 FPS",
    Icon: Sparkles,
    tone: "amber",
    animated: true,
  },
  {
    label: "AR Spatial Syncing",
    value: "Device: iPad Pro",
    Icon: Radar,
    tone: "blue",
  },
  {
    label: "Awaiting Point Cloud",
    value: "0 pending",
    Icon: Loader2,
    tone: "slate",
  },
];

const TONE_STYLES: Record<
  StatusPillDef["tone"],
  { bg: string; fg: string; dot: string; border: string }
> = {
  green: { bg: "bg-emerald-50", fg: "text-[#065f46]", dot: "bg-[#10b981]", border: "border-emerald-100" },
  amber: { bg: "bg-amber-50", fg: "text-[#92400e]", dot: "bg-[#f59e0b]", border: "border-amber-100" },
  blue: { bg: "bg-blue-50", fg: "text-[#1e40af]", dot: "bg-[#2563eb]", border: "border-blue-100" },
  slate: { bg: "bg-slate-100", fg: "text-[#334155]", dot: "bg-[#94a3b8]", border: "border-slate-200" },
};

interface DashboardTopBarProps {
  isMenuOpen: boolean;
  onToggleMenu: () => void;
  searchQuery: string;
  onSearchChange: (value: string) => void;
}

export const DashboardTopBar: React.FC<DashboardTopBarProps> = ({
  isMenuOpen,
  onToggleMenu,
  searchQuery,
  onSearchChange,
}) => (
  <header className="h-16 shrink-0 px-4 sm:px-6 flex items-center gap-4 border-b border-[#e2e8f0] bg-white/95 backdrop-blur-md sticky top-0 z-30">
    {/* Menu + brand */}
    <div className="flex items-center gap-3 shrink-0">
      <button
        onClick={onToggleMenu}
        aria-label="Toggle navigation menu"
        className={`p-2 rounded-xl border transition-all cursor-pointer flex items-center justify-center ${
          isMenuOpen
            ? "bg-blue-50 border-blue-200 text-[#2563eb]"
            : "bg-slate-50 hover:bg-slate-100 border-[#e2e8f0] text-[#0f172a]"
        }`}
        title={isMenuOpen ? "Close menu" : "Open navigation menu"}
      >
        {isMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
      </button>

      <Link href="/dashboard" className="flex items-center gap-2.5 group">
        <div className="relative w-8 h-8 shrink-0">
          <Image
            src="/images/logo-new-removebg-preview.png"
            alt="BuildScan 3D"
            fill
            className="object-contain group-hover:scale-105 transition-transform"
            priority
          />
        </div>
        <div className="flex items-center gap-1.5 select-none">
          <span className="font-extrabold text-base tracking-tight text-[#0f172a]">
            BuildScan
          </span>
          <span className="text-[11px] font-black px-1.5 py-0.5 rounded-md bg-blue-50 text-[#2563eb] border border-blue-100 leading-none">
            3D
          </span>
        </div>
      </Link>
    </div>

    {/* Search */}
    <div className="relative flex-1 max-w-md">
      <Search className="w-3.5 h-3.5 text-[#94a3b8] absolute left-3.5 top-1/2 -translate-y-1/2" />
      <input
        type="text"
        value={searchQuery}
        onChange={(e) => onSearchChange(e.target.value)}
        placeholder="Search projects, scans, or coordinates..."
        className="w-full pl-9 pr-14 py-2 bg-slate-50 border border-[#e2e8f0] rounded-full text-xs text-[#0f172a] placeholder-[#94a3b8] focus:outline-none focus:border-[#2563eb] focus:bg-white transition-all shadow-inner"
      />
      <span className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-0.5 text-[10px] font-mono font-bold text-[#94a3b8]">
        <Command className="w-3 h-3" />
        <span>K</span>
      </span>
    </div>

    {/* Status pills */}
    <div className="hidden xl:flex items-center gap-2 flex-1 justify-center">
      {PILLS.map((pill) => (
        <StatusPill key={pill.label} pill={pill} />
      ))}
    </div>

    {/* Notification + User */}
    <div className="flex items-center gap-3 shrink-0 ml-auto">
      <button
        aria-label="Notifications"
        className="relative p-2 rounded-xl text-[#64748b] hover:text-[#0f172a] hover:bg-slate-100 transition-colors cursor-pointer"
      >
        <Bell className="w-4 h-4" />
        <span className="absolute top-1 right-1 min-w-4 h-4 px-1 rounded-full bg-red-500 text-white text-[9px] font-bold flex items-center justify-center">
          3
        </span>
      </button>

      <div className="h-6 w-px bg-[#e2e8f0]" />

      <div className="flex items-center gap-2.5">
        <div className="w-9 h-9 rounded-full bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center text-white font-bold text-xs shadow-sm">
          AR
        </div>
        <div className="text-left hidden md:block leading-tight">
          <div className="text-xs font-bold text-[#0f172a]">Ahmad Raza</div>
          <div className="text-[10px] text-[#64748b]">Project Manager</div>
        </div>
      </div>
    </div>
  </header>
);

const StatusPill: React.FC<{ pill: StatusPillDef }> = ({ pill }) => {
  const tone = TONE_STYLES[pill.tone];
  const { Icon } = pill;
  return (
    <div
      className={`flex items-center gap-2 pl-2 pr-3 py-1.5 rounded-full border ${tone.bg} ${tone.border}`}
    >
      <span className="relative w-4 h-4 flex items-center justify-center">
        <Icon
          className={`w-3.5 h-3.5 ${tone.fg} ${
            pill.animated ? "animate-spin [animation-duration:6s]" : ""
          }`}
        />
      </span>
      <div className="flex flex-col leading-tight">
        <span className={`text-[10px] font-bold ${tone.fg}`}>{pill.label}</span>
        <span className="text-[9px] text-[#64748b]">{pill.value}</span>
      </div>
    </div>
  );
};
