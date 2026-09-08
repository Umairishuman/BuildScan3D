"use client";

import React from "react";
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
} from "lucide-react";

interface SidebarProps {
  currentTab: "dashboard" | "floorplan" | "projects" | "scans" | "reports" | "team" | "settings";
  onSelectTab: (tab: "dashboard" | "floorplan" | "projects" | "scans" | "reports" | "team" | "settings") => void;
  onOpenProject: (projectId: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentTab,
  onSelectTab,
  onOpenProject,
}) => {
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
    <aside className="w-56 shrink-0 min-h-screen bg-white border-r border-[#e2e8f0] flex flex-col justify-between p-4 select-none z-30">
      <div className="space-y-6">
        {/* Brand Logo */}
        <Link href="/dashboard" className="flex items-center gap-2 px-2 py-1.5 group">
          <div className="relative w-36 h-9">
            <Image
              src="/images/logo-new-removebg-preview.png"
              alt="BuildScan 3D"
              fill
              className="object-contain group-hover:scale-105 transition-transform"
              priority
            />
          </div>
        </Link>

        {/* Main Navigation Links */}
        <nav className="space-y-1">
          {mainNav.map((item) => {
            const Icon = item.icon;
            const isActive = currentTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onSelectTab(item.id)}
                className={`w-full flex items-center gap-3 px-3 py-2 rounded-xl text-xs font-semibold transition-all cursor-pointer relative ${
                  isActive
                    ? "text-[#2563eb] bg-blue-50/80 font-bold"
                    : "text-[#64748b] hover:text-[#0f172a] hover:bg-slate-50"
                }`}
              >
                {isActive && (
                  <span className="absolute left-0 top-1.5 bottom-1.5 w-1 bg-[#2563eb] rounded-r-full" />
                )}
                <Icon className={`w-4 h-4 ${isActive ? "text-[#2563eb]" : "text-[#94a3b8]"}`} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Recent Sites Section */}
      <div className="pt-6 border-t border-[#f1f5f9] space-y-3">
        <h4 className="text-[11px] font-bold text-[#64748b] uppercase tracking-wider px-2">
          Recent Sites
        </h4>
        <div className="space-y-2">
          {recentSites.map((site) => (
            <button
              key={site.id}
              onClick={() => onOpenProject(site.id)}
              className="w-full text-left px-2 py-1.5 rounded-lg hover:bg-slate-50 transition-colors group cursor-pointer"
            >
              <div className="flex items-center gap-2">
                <span className={`w-2 h-2 rounded-full ${site.color} shrink-0`} />
                <span className="text-xs font-semibold text-[#0f172a] group-hover:text-[#2563eb] truncate">
                  {site.name}
                </span>
              </div>
              <span className="text-[10px] text-[#64748b] pl-4 block">
                {site.status}
              </span>
            </button>
          ))}
        </div>
      </div>
    </aside>
  );
};
