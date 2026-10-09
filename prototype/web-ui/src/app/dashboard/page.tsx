"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { Sidebar } from "@/components/Sidebar";
import { NewCaptureModal } from "@/components/NewCaptureModal";
import { DashboardTopBar } from "@/components/DashboardHome/TopBar";
import { DashboardOverview } from "@/components/DashboardHome/Overview";
import { ActivityColumn } from "@/components/DashboardHome/ActivityColumn";
import { NavItem } from "@/lib/navigation";

export default function DashboardPage() {
  const router = useRouter();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [isNewCaptureOpen, setIsNewCaptureOpen] = useState(false);

  const handleSelectNav = (item: NavItem) => {
    setIsMenuOpen(false);
    if (item.href) router.push(item.href);
  };

  const handleOpenRecentSite = (projectId: string) => {
    setIsMenuOpen(false);
    router.push(`/viewer/${projectId}`);
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

      <main className="flex-1 px-4 sm:px-6 py-5">
        <div className="max-w-[1400px] mx-auto flex flex-col lg:flex-row gap-4">
          <div className="flex-1 min-w-0">
            <DashboardOverview
              onQuickCapture={() => setIsNewCaptureOpen(true)}
            />
          </div>
          <ActivityColumn />
        </div>
      </main>

      <NewCaptureModal
        isOpen={isNewCaptureOpen}
        onClose={() => setIsNewCaptureOpen(false)}
      />
    </div>
  );
}
