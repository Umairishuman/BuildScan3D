import {
  LayoutDashboard,
  FolderKanban,
  ScanLine,
  Map,
  FileText,
  Users,
  Settings,
  type LucideIcon,
} from "lucide-react";
import { MOCK_PROJECTS, Project } from "./mockData";

export type NavId =
  | "dashboard"
  | "projects"
  | "scans"
  | "floorplan"
  | "reports"
  | "team"
  | "settings";

export interface NavItem {
  id: NavId;
  label: string;
  icon: LucideIcon;
  /**
   * Route for this nav item, or null when the screen has not been built yet.
   * AppShell only navigates for items that have a real href, so nothing in the
   * menu can dead-end on a 404. Flip these to a path as each screen lands.
   */
  href: string | null;
}

export const NAV_ITEMS: readonly NavItem[] = [
  { id: "dashboard", label: "Dashboard", icon: LayoutDashboard, href: "/dashboard" },
  { id: "projects", label: "Projects", icon: FolderKanban, href: "/projects" },
  { id: "scans", label: "Scans", icon: ScanLine, href: null },
  { id: "floorplan", label: "Floor Plan", icon: Map, href: "/floorplan/tower-a-floors-5-8" },
  { id: "reports", label: "Reports", icon: FileText, href: null },
  { id: "team", label: "Team", icon: Users, href: null },
  { id: "settings", label: "Settings", icon: Settings, href: null },
] as const;

/** Status dot colour used by the Recent Sites list in the menu. */
export const STATUS_DOT: Record<Project["status"], string> = {
  ready: "bg-[#10b981]",
  processing: "bg-[#f59e0b]",
  complete: "bg-[#14b8a6]",
  draft: "bg-[#94a3b8]",
  archived: "bg-slate-500",
};

export interface RecentSite {
  id: string;
  name: string;
  status: Project["status"];
  statusLabel: string;
  dot: string;
}

/**
 * Recent Sites shown under the menu nav. Derived from the project fixtures so
 * the ids always resolve to a real project instead of drifting out of sync.
 */
export const RECENT_SITES: readonly RecentSite[] = MOCK_PROJECTS.slice(0, 4).map(
  (project) => ({
    id: project.id,
    name: project.name,
    status: project.status,
    statusLabel: project.statusLabel,
    dot: STATUS_DOT[project.status],
  })
);
