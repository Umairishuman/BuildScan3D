"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { ChevronRight, Home } from "lucide-react";
import { Navbar } from "./Navbar";
import { Sidebar } from "./Sidebar";
import { NavId, NavItem } from "@/lib/navigation";

export interface Crumb {
  label: string;
  /** Omit on the final crumb — it renders as the current page, not a link. */
  href?: string;
}

interface AppShellProps {
  children: React.ReactNode;

  /** Which menu entry renders as active. */
  activeNav?: NavId;
  /**
   * Intercept menu clicks. When omitted, AppShell routes to the item's href and
   * ignores items whose screen has not been built yet (href === null).
   */
  onSelectNav?: (item: NavItem) => void;

  /** Breadcrumb trail rendered in a strip under the top bar. Omit to hide it. */
  breadcrumbs?: Crumb[];

  /** Global search. Omit both to render the field read-only. */
  searchQuery?: string;
  onSearchChange?: (q: string) => void;

  /**
   * Clicking a site in the menu's Recent Sites list. Defaults to opening that
   * project's workspace.
   */
  onOpenRecentSite?: (projectId: string) => void;

  /**
   * `contained` — scrolling page, centred max-width column with padding (lists,
   * dashboards). `fluid` — locks to the viewport and hands the full remaining
   * box to children with no padding (3D workspace, floor plan canvas).
   */
  variant?: "contained" | "fluid";

  /** Extra classes on <main>, e.g. a different max-width for a wide table. */
  className?: string;
}

export const AppShell: React.FC<AppShellProps> = ({
  children,
  activeNav = "dashboard",
  onSelectNav,
  breadcrumbs,
  searchQuery,
  onSearchChange,
  onOpenRecentSite,
  variant = "contained",
  className = "",
}) => {
  const router = useRouter();
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const isFluid = variant === "fluid";

  const handleSelectNav = (item: NavItem) => {
    if (onSelectNav) {
      onSelectNav(item);
      return;
    }
    // No page-level handler: navigate only where a screen actually exists.
    if (item.href) router.push(item.href);
  };

  const handleOpenRecentSite = (projectId: string) => {
    if (onOpenRecentSite) {
      onOpenRecentSite(projectId);
      return;
    }
    router.push(`/viewer/${projectId}`);
  };

  return (
    <div
      className={`w-full flex flex-col bg-[#f6fafd] text-[#0f172a] relative ${
        isFluid ? "h-screen overflow-hidden" : "min-h-screen"
      }`}
    >
      {/* High-Definition Isometric CAD Blueprint Grid Background */}
      <div
        aria-hidden
        className="absolute inset-0 bg-[linear-gradient(to_right,#e0edf8_1px,transparent_1px),linear-gradient(to_bottom,#e0edf8_1px,transparent_1px)] bg-[size:32px_32px] opacity-45 pointer-events-none"
      />

      <Navbar
        searchQuery={searchQuery}
        onSearchChange={onSearchChange}
        isMenuOpen={isMenuOpen}
        onToggleMenu={() => setIsMenuOpen((prev) => !prev)}
      />

      <Sidebar
        isOpen={isMenuOpen}
        onClose={() => setIsMenuOpen(false)}
        activeNav={activeNav}
        onSelectNav={handleSelectNav}
        onOpenRecentSite={handleOpenRecentSite}
      />

      <div
        className={`flex-1 flex flex-col min-w-0 z-10 ${isFluid ? "min-h-0" : ""}`}
      >
        {breadcrumbs && breadcrumbs.length > 0 && (
          <nav
            aria-label="Breadcrumb"
            className="shrink-0 h-11 px-4 sm:px-6 flex items-center gap-1.5 border-b border-[#e2e8f0] bg-white/70 backdrop-blur-sm"
          >
            <Link
              href="/dashboard"
              className="p-1 rounded-lg text-[#94a3b8] hover:text-[#2563eb] hover:bg-slate-100 transition-colors shrink-0"
              title="Back to Dashboard"
              aria-label="Back to Dashboard"
            >
              <Home className="w-3.5 h-3.5" />
            </Link>

            <ol className="flex items-center gap-1.5 min-w-0">
              {breadcrumbs.map((crumb, index) => {
                const isLast = index === breadcrumbs.length - 1;
                return (
                  <li key={`${crumb.label}-${index}`} className="flex items-center gap-1.5 min-w-0">
                    <ChevronRight className="w-3.5 h-3.5 text-[#cbd5e1] shrink-0" />
                    {crumb.href && !isLast ? (
                      <Link
                        href={crumb.href}
                        className="text-xs font-semibold text-[#64748b] hover:text-[#2563eb] transition-colors truncate"
                      >
                        {crumb.label}
                      </Link>
                    ) : (
                      <span
                        aria-current={isLast ? "page" : undefined}
                        className={`text-xs truncate ${
                          isLast
                            ? "font-bold text-[#0f172a]"
                            : "font-semibold text-[#64748b]"
                        }`}
                      >
                        {crumb.label}
                      </span>
                    )}
                  </li>
                );
              })}
            </ol>
          </nav>
        )}

        <main
          className={
            isFluid
              ? `flex-1 min-h-0 min-w-0 flex flex-col ${className}`
              : `flex-1 p-6 md:p-8 space-y-6 w-full mx-auto ${
                  className || "max-w-7xl"
                }`
          }
        >
          {children}
        </main>
      </div>
    </div>
  );
};
