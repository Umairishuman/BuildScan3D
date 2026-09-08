"use client";

import React from "react";
import Link from "next/link";
import { Activity, HardHat, Search, ShieldCheck } from "lucide-react";

interface NavbarProps {
  onOpenJobStatus?: () => void;
  activeProcessingCount?: number;
}

export const Navbar: React.FC<NavbarProps> = ({
  onOpenJobStatus,
  activeProcessingCount = 1,
}) => {
  return (
    <header className="sticky top-0 z-40 w-full border-b border-[#e2e8f0] bg-white/90 backdrop-blur-md text-[#0f172a]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-4">
        {/* Brand & System Tag */}
        <div className="flex items-center gap-8">
          <Link href="/dashboard" className="flex items-center gap-2.5 group">
            {/* Isometric 3D Cube Icon */}
            <svg
              className="w-8 h-8 text-[#2563eb] group-hover:scale-105 transition-transform"
              viewBox="0 0 48 48"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M24 4L42 14.3923V35.1769L24 45.5692L6 35.1769V14.3923L24 4Z"
                stroke="currentColor"
                strokeWidth="3.2"
                strokeLinejoin="round"
              />
              <path
                d="M24 4V24.5M24 24.5L42 14.5M24 24.5L6 14.5M24 24.5V45.5"
                stroke="currentColor"
                strokeWidth="2.8"
                strokeLinecap="round"
              />
              <circle cx="24" cy="24.5" r="3" fill="currentColor" />
              <circle cx="15" cy="19.5" r="1.5" fill="currentColor" />
              <circle cx="33" cy="19.5" r="1.5" fill="currentColor" />
              <circle cx="24" cy="35" r="1.5" fill="currentColor" />
            </svg>

            <div>
              <div className="flex items-center gap-1.5">
                <span className="font-bold text-base tracking-tight text-[#0f172a]">
                  BuildScan <span className="text-[#2563eb]">3D</span>
                </span>
                <span className="text-[10px] font-semibold uppercase tracking-wider px-1.5 py-0.5 rounded bg-blue-50 text-[#2563eb] border border-blue-200">
                  Enterprise
                </span>
              </div>
              <p className="text-[10px] text-[#64748b] leading-none">
                Spatial Intelligence & 3DGS
              </p>
            </div>
          </Link>

          <nav className="hidden md:flex items-center gap-1 text-xs font-semibold text-[#64748b]">
            <Link
              href="/dashboard"
              className="px-3 py-1.5 rounded-lg text-[#2563eb] bg-blue-50 font-bold transition-colors"
            >
              Projects & Scans
            </Link>
            <Link
              href="/viewer/sector-4-mep"
              className="px-3 py-1.5 rounded-lg hover:text-[#0f172a] hover:bg-slate-100 transition-colors"
            >
              3D Workspace
            </Link>
          </nav>
        </div>

        {/* Global Search */}
        <div className="hidden lg:flex items-center flex-1 max-w-xs relative">
          <Search className="w-3.5 h-3.5 text-[#94a3b8] absolute left-3 pointer-events-none" />
          <input
            type="text"
            placeholder="Search scans, sectors, rooms..."
            className="w-full pl-8 pr-4 py-1.5 bg-[#f8fafc] border border-[#e2e8f0] rounded-xl text-xs text-[#0f172a] placeholder-[#94a3b8] focus:outline-none focus:border-[#2563eb] focus:bg-white transition-all"
          />
        </div>

        {/* Right Section: Status Indicator & Profile */}
        <div className="flex items-center gap-3">
          {/* Active Job Trigger Button */}
          {activeProcessingCount > 0 && onOpenJobStatus && (
            <button
              onClick={onOpenJobStatus}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-amber-50 border border-amber-200 text-amber-700 hover:bg-amber-100 text-xs font-semibold transition-all cursor-pointer"
              title="Click to view live 3DGS training queue"
            >
              <Activity className="w-3.5 h-3.5 text-amber-600 animate-spin" />
              <span>1 Pipeline Active (68%)</span>
            </button>
          )}

          {/* Defense Badge */}
          <div className="hidden sm:flex items-center gap-1.5 text-xs text-emerald-700 bg-emerald-50 border border-emerald-200 px-2.5 py-1 rounded-xl">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
            <span className="font-mono text-[11px] font-semibold">FAST-NUCES PoC</span>
          </div>

          <div className="h-5 w-[1px] bg-[#e2e8f0] hidden sm:block" />

          {/* User Profile Snippet */}
          <div className="flex items-center gap-2.5 pl-1">
            <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-blue-600 to-cyan-500 flex items-center justify-center text-white font-bold text-xs shadow-sm">
              SJ
            </div>
            <div className="hidden xl:block text-left">
              <div className="text-xs font-bold text-[#0f172a]">
                Sarah Jenkins
              </div>
              <div className="text-[10px] text-[#64748b] flex items-center gap-1">
                <HardHat className="w-2.5 h-2.5 text-amber-500" />
                <span>Lead MEP Manager</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};
