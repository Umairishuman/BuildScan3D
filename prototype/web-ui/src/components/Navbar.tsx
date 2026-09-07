"use client";

import React from "react";
import Link from "next/link";
import { Box, Activity, HardHat, Bell, Search, ShieldCheck } from "lucide-react";

interface NavbarProps {
  onOpenJobStatus?: () => void;
  activeProcessingCount?: number;
}

export const Navbar: React.FC<NavbarProps> = ({
  onOpenJobStatus,
  activeProcessingCount = 1,
}) => {
  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-800 bg-slate-950/80 backdrop-blur-md text-slate-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-4">
        {/* Brand & System Tag */}
        <div className="flex items-center gap-6">
          <Link href="/dashboard" className="flex items-center gap-3 group">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 via-indigo-600 to-cyan-400 p-[1px] shadow-lg shadow-blue-500/20">
              <div className="w-full h-full bg-slate-950 rounded-[11px] flex items-center justify-center group-hover:bg-slate-900 transition-colors">
                <Box className="w-5 h-5 text-cyan-400 group-hover:scale-110 transition-transform" />
              </div>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-lg tracking-tight text-white">
                  BuildScan<span className="text-cyan-400">3D</span>
                </span>
                <span className="text-[10px] font-semibold uppercase tracking-wider px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
                  Enterprise
                </span>
              </div>
              <p className="text-[11px] text-slate-400 leading-none">
                AR Telemetry & 3DGS Metric Inspection
              </p>
            </div>
          </Link>

          <nav className="hidden md:flex items-center gap-1 text-sm font-medium text-slate-400">
            <Link
              href="/dashboard"
              className="px-3 py-1.5 rounded-lg text-white bg-slate-800/60 hover:text-white transition-colors"
            >
              Projects & Scans
            </Link>
            <Link
              href="/viewer/sector-4-mep"
              className="px-3 py-1.5 rounded-lg hover:text-white hover:bg-slate-800/40 transition-colors"
            >
              3D Workspace
            </Link>
          </nav>
        </div>

        {/* Global Search */}
        <div className="hidden lg:flex items-center flex-1 max-w-xs relative">
          <Search className="w-4 h-4 text-slate-500 absolute left-3 pointer-events-none" />
          <input
            type="text"
            placeholder="Search scans, sectors, rooms..."
            className="w-full pl-9 pr-4 py-1.5 bg-slate-900 border border-slate-800 rounded-lg text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500 transition-colors"
          />
        </div>

        {/* Right Section: Status Indicator & Profile */}
        <div className="flex items-center gap-3">
          {/* Active Job Trigger Button */}
          {activeProcessingCount > 0 && onOpenJobStatus && (
            <button
              onClick={onOpenJobStatus}
              className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-amber-500/10 border border-amber-500/30 text-amber-300 hover:bg-amber-500/20 text-xs font-medium transition-all animate-pulse"
              title="Click to view live 3DGS training queue"
            >
              <Activity className="w-3.5 h-3.5 text-amber-400 animate-spin" />
              <span>1 Cloud Pipeline Active (68%)</span>
            </button>
          )}

          {/* Defense Badge */}
          <div className="hidden sm:flex items-center gap-1.5 text-xs text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-2.5 py-1 rounded-lg">
            <ShieldCheck className="w-3.5 h-3.5" />
            <span className="font-mono text-[11px]">FAST-NUCES PoC</span>
          </div>

          <div className="h-5 w-[1px] bg-slate-800 hidden sm:block" />

          {/* User Profile Snippet */}
          <div className="flex items-center gap-3 pl-1">
            <div className="w-9 h-9 rounded-full bg-gradient-to-tr from-cyan-600 to-blue-700 flex items-center justify-center text-white font-semibold text-xs ring-2 ring-slate-800">
              SJ
            </div>
            <div className="hidden xl:block text-left">
              <div className="text-xs font-semibold text-slate-200">
                Sarah Jenkins
              </div>
              <div className="text-[10px] text-slate-400 flex items-center gap-1">
                <HardHat className="w-2.5 h-2.5 text-amber-400" />
                <span>Lead MEP Project Manager</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

