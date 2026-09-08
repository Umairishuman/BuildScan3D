"use client";

import React from "react";
import Link from "next/link";
import Image from "next/image";
import { Search, Bell, ChevronDown, Menu, X } from "lucide-react";

interface NavbarProps {
  onOpenNewCapture: () => void;
  searchQuery: string;
  onSearchChange: (q: string) => void;
  isMenuOpen?: boolean;
  onToggleMenu?: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  onOpenNewCapture,
  searchQuery,
  onSearchChange,
  isMenuOpen = false,
  onToggleMenu,
}) => {
  return (
    <header className="h-16 w-full px-4 sm:px-6 flex items-center justify-between border-b border-[#e2e8f0] bg-white/90 backdrop-blur-md text-[#0f172a] sticky top-0 z-30">
      {/* Left: 3-Bar Menu Toggle + Brand Logo & Name + Project Selector */}
      <div className="flex items-center gap-3 sm:gap-4">
        {/* 3-Bar Hamburger Menu Button */}
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
          {isMenuOpen ? (
            <X className="w-5 h-5" />
          ) : (
            <Menu className="w-5 h-5" />
          )}
        </button>

        {/* Brand Logo + Name Lockup */}
        <Link href="/dashboard" className="flex items-center gap-2.5 group">
          <div className="relative w-8 h-8 shrink-0">
            <Image
              src="/images/logo-new-removebg-preview.png"
              alt="BuildScan 3D Logo"
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

        <div className="hidden md:block h-5 w-[1px] bg-[#e2e8f0]" />

        {/* Project Selector Dropdown */}
        <button className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-[#e2e8f0] bg-white hover:bg-slate-50 text-xs font-bold text-[#0f172a] transition-all shadow-sm cursor-pointer">
          <span>All Projects</span>
          <ChevronDown className="w-3.5 h-3.5 text-[#64748b]" />
        </button>

        {/* Search Pill Input */}
        <div className="relative w-52 md:w-72 hidden sm:block">
          <Search className="w-3.5 h-3.5 text-[#94a3b8] absolute left-3.5 top-2.5 pointer-events-none" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder="Search projects, scans, or sites..."
            className="w-full pl-9 pr-4 py-2 bg-slate-50 border border-[#e2e8f0] rounded-full text-xs text-[#0f172a] placeholder-[#94a3b8] focus:outline-none focus:border-[#2563eb] focus:bg-white transition-all shadow-inner"
          />
        </div>
      </div>

      {/* Right: Notifications, Team Avatars, User Profile */}
      <div className="flex items-center gap-3 sm:gap-4">
        {/* Notification Bell with Badge */}
        <button
          className="relative p-2 rounded-xl text-[#64748b] hover:text-[#0f172a] hover:bg-slate-100 transition-colors cursor-pointer"
          title="Notifications"
        >
          <Bell className="w-4 h-4" />
          <span className="absolute top-1 right-1 w-4 h-4 rounded-full bg-red-500 text-white text-[9px] font-bold flex items-center justify-center">
            3
          </span>
        </button>

        {/* Team Avatars Overlapping Stack */}
        <div className="hidden lg:flex items-center -space-x-2 overflow-hidden pl-1">
          <div className="w-7 h-7 rounded-full bg-slate-300 border-2 border-white flex items-center justify-center text-[10px] font-bold text-slate-700">
            JD
          </div>
          <div className="w-7 h-7 rounded-full bg-blue-500 border-2 border-white flex items-center justify-center text-[10px] font-bold text-white">
            SK
          </div>
          <div className="w-7 h-7 rounded-full bg-emerald-500 border-2 border-white flex items-center justify-center text-[10px] font-bold text-white">
            MR
          </div>
        </div>

        <div className="h-5 w-[1px] bg-[#e2e8f0]" />

        {/* User Profile Snippet (Ahmad Raza) */}
        <div className="flex items-center gap-2.5 pl-1">
          <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center text-white font-bold text-xs shadow-sm">
            AR
          </div>
          <div className="text-left hidden sm:block">
            <div className="text-xs font-bold text-[#0f172a]">Ahmad Raza</div>
            <div className="text-[10px] text-[#64748b]">Project Manager</div>
          </div>
        </div>
      </div>
    </header>
  );
};
