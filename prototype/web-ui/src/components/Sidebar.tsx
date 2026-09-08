"use client";

import React, { useEffect } from "react";
import Link from "next/link";
import Image from "next/image";
import {
  LayoutDashboard,
  FolderKanban,
  ScanLine,
  Map,
  FileText,
  Users,
  Settings,
  X,
} from "lucide-react";

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
  currentTab: "dashboard" | "floorplan" | "projects" | "scans" | "reports" | "team" | "settings";
  onSelectTab: (tab: "dashboard" | "floorplan" | "projects" | "scans" | "reports" | "team" | "settings") => void;
  onOpenProject: (projectId: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  isOpen,
  onClose,
  currentTab,
  onSelectTab,
  onOpenProject,
}) => {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape" && isOpen) {
        onClose();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const mainNav = [
    { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
    { id: "projects", label: "Projects", icon: FolderKanban },
    { id: "scans", label: "Scans", icon: ScanLine },
    { id: "floorplan", label: "Floor Plan", icon: Map },
    { id: "reports", label: "Reports", icon: FileText },
    { id: "team", label: "Team", icon: Users },
    { id: "settings", label: "Settings", icon: Settings },
  ] as const;

  const recentSites = [
    { id: "sector-4-mep", name: "Sector 4 MEP Room", status: "Processing", color: "bg-amber-400" },
    { id: "tower-a-floors-5-8", name: "Tower A - Floors 5-8", status: "Ready", color: "bg-emerald-500" },
    { id: "west-wing", name: "West Wing", status: "Complete", color: "bg-teal-500" },
    { id: "parking-garage", name: "Parking Garage", status: "Draft", color: "bg-slate-400" },
  ];

  return (
    <>
      {/* Backdrop overlay for quick dismissal */}
      <div
        onClick={onClose}
        className="fixed inset-0 bg-slate-900/25 backdrop-blur-[2px] z-40 transition-opacity animate-in fade-in duration-200"
      />

      {/* Floating Menu Box */}
      <aside className="fixed top-18 left-4 sm:left-6 w-80 max-h-[calc(100vh-5.5rem)] overflow-y-auto bg-white/95 backdrop-blur-xl border border-[#e2e8f0] rounded-2xl shadow-[0_20px_50px_rgba(15,23,42,0.18)] p-4 flex flex-col justify-between select-none z-50 ring-1 ring-black/5 animate-in fade-in zoom-in-95 duration-150">
        <div className="space-y-4">
          {/* Menu Box Header: Brand Logo + Name + Close Button */}
          <div className="flex items-center justify-between pb-3 border-b border-[#f1f5f9] px-1">
            <Link
              href="/dashboard"
              onClick={onClose}
              className="flex items-center gap-2.5 group"
            >
              <div className="relative w-7 h-7 shrink-0">
                <Image
                  src="/images/logo-new-removebg-preview.png"
                  alt="BuildScan 3D"
                  fill
                  className="object-contain group-hover:scale-105 transition-transform"
                />
              </div>
              <div className="flex items-center gap-1.5">
                <span className="font-extrabold text-sm tracking-tight text-[#0f172a]">
                  BuildScan
                </span>
                <span className="text-[10px] font-black px-1.5 py-0.5 rounded bg-blue-50 text-[#2563eb] border border-blue-100">
                  3D
                </span>
              </div>
            </Link>

            <button
              onClick={onClose}
              className="p-1.5 rounded-lg text-[#64748b] hover:text-[#0f172a] hover:bg-slate-100 transition-colors cursor-pointer"
              title="Close menu"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Main Navigation Links */}
          <nav className="space-y-1">
            <div className="text-[10px] font-bold text-[#94a3b8] uppercase tracking-wider px-2 py-1">
              Menu Navigation
            </div>
            {mainNav.map((item) => {
              const Icon = item.icon;
              const isActive = currentTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => {
                    onSelectTab(item.id);
                    onClose();
                  }}
                  className={`w-full flex items-center justify-between px-3 py-2 rounded-xl text-xs font-semibold transition-all cursor-pointer ${
                    isActive
                      ? "text-[#2563eb] bg-blue-50/90 font-bold shadow-xs"
                      : "text-[#64748b] hover:text-[#0f172a] hover:bg-slate-50"
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <Icon
                      className={`w-4 h-4 ${
                        isActive ? "text-[#2563eb]" : "text-[#94a3b8]"
                      }`}
                    />
                    <span>{item.label}</span>
                  </div>
                  {isActive && (
                    <span className="w-1.5 h-1.5 rounded-full bg-[#2563eb]" />
                  )}
                </button>
              );
            })}
          </nav>
        </div>

        {/* Recent Sites Section inside Menu Box */}
        <div className="mt-4 pt-3 border-t border-[#f1f5f9] space-y-2">
          <div className="flex items-center justify-between px-2">
            <h4 className="text-[10px] font-bold text-[#94a3b8] uppercase tracking-wider">
              Recent Sites
            </h4>
            <span className="text-[10px] text-[#2563eb] font-semibold">Active</span>
          </div>
          <div className="space-y-1">
            {recentSites.map((site) => (
              <button
                key={site.id}
                onClick={() => {
                  onOpenProject(site.id);
                  onClose();
                }}
                className="w-full text-left px-2.5 py-1.5 rounded-lg hover:bg-slate-50 transition-colors group cursor-pointer flex items-center justify-between"
              >
                <div className="flex items-center gap-2 truncate pr-2">
                  <span className={`w-2 h-2 rounded-full ${site.color} shrink-0`} />
                  <span className="text-xs font-semibold text-[#0f172a] group-hover:text-[#2563eb] truncate">
                    {site.name}
                  </span>
                </div>
                <span className="text-[10px] text-[#64748b] shrink-0 font-medium">
                  {site.status}
                </span>
              </button>
            ))}
          </div>
        </div>
      </aside>
    </>
  );
};
