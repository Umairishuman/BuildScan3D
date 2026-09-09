"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { Sidebar } from "@/components/Sidebar";
import { DashboardTopBar } from "@/components/DashboardHome/TopBar";
import { HeroCanvas } from "@/components/DashboardHome/HeroCanvas";
import { ProjectSidebar } from "@/components/DashboardHome/ProjectSidebar";
import { ScansStrip } from "@/components/DashboardHome/ScansStrip";
import { NavItem } from "@/lib/navigation";
import { MOCK_PROJECTS } from "@/lib/mockData";

type CanvasTool = "orbit" | "pan" | "measure" | "section" | "compare";

/** The featured project this dashboard is a workspace for. */
const FEATURED_PROJECT_ID = "sector-4-mep";

export default function DashboardPage() {
  const router = useRouter();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [activeTool, setActiveTool] = useState<CanvasTool>("orbit");
  const [viewMode, setViewMode] = useState<"2d" | "3d">("3d");
  const [activeFloor, setActiveFloor] = useState("F3");

  const featured =
    MOCK_PROJECTS.find((p) => p.id === FEATURED_PROJECT_ID) ?? MOCK_PROJECTS[0];
  const projectHref = `/viewer/${featured.id}`;

  const handleSelectNav = (item: NavItem) => {
    setIsMenuOpen(false);
    if (item.href) router.push(item.href);
  };

  const handleOpenRecentSite = (projectId: string) => {
    setIsMenuOpen(false);
    router.push(`/viewer/${projectId}`);
  };

  const handleExport = () => {
    router.push(projectHref);
  };

  return (
    <div className="min-h-screen w-full flex flex-col bg-[#f8fafc] text-[#0f172a]">
      <DashboardTopBar
        isMenuOpen={isMenuOpen}
        onToggleMenu={() => setIsMenuOpen((v) => !v)}
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
      />

      <Sidebar
        isOpen={isMenuOpen}
        onClose={() => setIsMenuOpen(false)}
        activeNav="dashboard"
        onSelectNav={handleSelectNav}
        onOpenRecentSite={handleOpenRecentSite}
      />

      {/* Body */}
      <main className="flex-1 min-h-0 px-4 sm:px-6 py-4 flex flex-col gap-3 overflow-hidden">
        {/* Top: hero + right sidebar */}
        <div className="flex-1 min-h-0 flex gap-3">
          <div className="flex-1 min-w-0 min-h-[520px]">
            <HeroCanvas
              activeTool={activeTool}
              onSelectTool={setActiveTool}
              viewMode={viewMode}
              onSelectViewMode={setViewMode}
              activeFloor={activeFloor}
              onSelectFloor={setActiveFloor}
              projectHref={projectHref}
            />
          </div>
          <ProjectSidebar
            projectHref={projectHref}
            onExport={handleExport}
          />
        </div>

        {/* Bottom scans strip */}
        <div className="shrink-0">
          <ScansStrip />
        </div>
      </main>
    </div>
  );
}
