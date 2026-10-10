"use client";

import React, { useEffect, useMemo, useRef } from "react";
import {
  AlertTriangle,
  Archive,
  ArrowRight,
  Bell,
  CheckCircle2,
  Clock,
  MessageSquare,
  Ruler,
} from "lucide-react";
import {
  NotificationCategory,
  NotificationItem,
  NotificationKind,
} from "@/lib/mockData";

const TABS: { id: NotificationCategory | "all"; label: string }[] = [
  { id: "all", label: "All" },
  { id: "scans", label: "Scans" },
  { id: "projects", label: "Projects" },
  { id: "system", label: "System" },
];

interface KindStyle {
  Icon: React.ComponentType<{ className?: string }>;
  bg: string;
  fg: string;
  ring?: string;
}

const KIND_STYLES: Record<NotificationKind, KindStyle> = {
  scan_processing: {
    Icon: Clock,
    bg: "bg-amber-50",
    fg: "text-[#d97706]",
    ring: "ring-amber-100",
  },
  scan_completed: {
    Icon: CheckCircle2,
    bg: "bg-emerald-50",
    fg: "text-[#059669]",
    ring: "ring-emerald-100",
  },
  scan_failed: {
    Icon: AlertTriangle,
    bg: "bg-red-50",
    fg: "text-[#dc2626]",
    ring: "ring-red-100",
  },
  measurement_added: {
    Icon: Ruler,
    bg: "bg-blue-50",
    fg: "text-[#2563eb]",
    ring: "ring-blue-100",
  },
  comment: {
    Icon: MessageSquare,
    bg: "bg-slate-100",
    fg: "text-[#475569]",
    ring: "ring-slate-200",
  },
  project_archived: {
    Icon: Archive,
    bg: "bg-slate-100",
    fg: "text-[#475569]",
    ring: "ring-slate-200",
  },
};

interface NotificationsPanelProps {
  isOpen: boolean;
  onClose: () => void;
  activeTab: NotificationCategory | "all";
  onSelectTab: (tab: NotificationCategory | "all") => void;
  onMarkAllRead: () => void;
  notifications: NotificationItem[];
}

export const NotificationsPanel: React.FC<NotificationsPanelProps> = ({
  isOpen,
  onClose,
  activeTab,
  onSelectTab,
  onMarkAllRead,
  notifications,
}) => {
  const panelRef = useRef<HTMLDivElement>(null);

  const filtered = useMemo(() => {
    if (activeTab === "all") return notifications;
    return notifications.filter((n) => n.category === activeTab);
  }, [activeTab, notifications]);

  const unreadCount = notifications.filter((n) => n.unread).length;

  // Dismiss on outside click / Escape. Bound in a `mousedown` handler so that
  // clicking the bell (which toggles isOpen) does not race with the close.
  useEffect(() => {
    if (!isOpen) return;

    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as Node | null;
      if (!target || !panelRef.current) return;
      if (panelRef.current.contains(target)) return;
      // The bell button carries this data attribute so clicking it doesn't
      // both close (via outside-click) and re-open (via its own toggle).
      const el = target as Element | null;
      if (el && "closest" in el && el.closest?.("[data-notifications-toggle]"))
        return;
      onClose();
    };

    const handleKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") onClose();
    };

    document.addEventListener("mousedown", handleClickOutside);
    document.addEventListener("keydown", handleKey);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
      document.removeEventListener("keydown", handleKey);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div
      ref={panelRef}
      role="dialog"
      aria-label="Notifications"
      className="absolute top-full right-0 mt-2 w-[380px] max-h-[calc(100vh-6rem)] rounded-2xl bg-white border border-[#e2e8f0] shadow-2xl z-40 flex flex-col overflow-hidden"
    >
      {/* Header */}
      <div className="px-4 py-3 border-b border-[#f1f5f9] flex items-center justify-between shrink-0">
        <div className="flex items-center gap-2">
          <Bell className="w-4 h-4 text-[#2563eb]" />
          <h2 className="text-sm font-bold text-[#0f172a]">Notifications</h2>
          {unreadCount > 0 && (
            <span className="text-[10px] font-bold px-1.5 py-0.5 rounded-full bg-red-50 text-[#dc2626] border border-red-100">
              {unreadCount} new
            </span>
          )}
        </div>
        <button
          onClick={onMarkAllRead}
          disabled={unreadCount === 0}
          className="text-[10px] font-bold text-[#2563eb] hover:text-[#1d4ed8] disabled:text-[#cbd5e1] disabled:cursor-not-allowed cursor-pointer transition-colors"
        >
          Mark all read
        </button>
      </div>

      {/* Tabs */}
      <div className="px-3 pt-3 shrink-0">
        <div
          role="tablist"
          aria-label="Notification category"
          className="flex items-center gap-0.5 p-1 rounded-xl bg-[#f1f5f9]"
        >
          {TABS.map((tab) => {
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                role="tab"
                aria-selected={isActive}
                onClick={() => onSelectTab(tab.id)}
                className={`flex-1 px-2 py-1.5 rounded-lg text-[11px] font-bold transition-all cursor-pointer ${
                  isActive
                    ? "bg-white text-[#2563eb] shadow-sm"
                    : "text-[#64748b] hover:text-[#0f172a]"
                }`}
              >
                {tab.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* List */}
      <div className="flex-1 min-h-0 overflow-y-auto px-2 py-2">
        {filtered.length === 0 ? (
          <div className="flex flex-col items-center justify-center text-center gap-2 px-4 py-10">
            <Bell className="w-5 h-5 text-[#cbd5e1]" />
            <p className="text-[11px] text-[#94a3b8] leading-relaxed">
              Nothing in this bucket.
            </p>
          </div>
        ) : (
          <ul className="space-y-0.5">
            {filtered.map((item) => (
              <NotificationRow key={item.id} item={item} />
            ))}
          </ul>
        )}
      </div>

      {/* Footer */}
      <div className="px-3 py-3 border-t border-[#f1f5f9] shrink-0">
        <button className="w-full inline-flex items-center justify-center gap-1.5 py-2 rounded-lg text-[11px] font-bold text-[#2563eb] hover:bg-blue-50 transition-colors cursor-pointer">
          <span>View all activity</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  );
};

/* ---------------------------- Row ---------------------------- */

const NotificationRow: React.FC<{ item: NotificationItem }> = ({ item }) => {
  const style = KIND_STYLES[item.kind];
  const { Icon } = style;
  return (
    <li>
      <button
        type="button"
        className="group w-full flex items-start gap-2.5 p-2.5 rounded-xl hover:bg-slate-50 transition-colors text-left cursor-pointer"
      >
        <span
          className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${
            style.bg
          } ${style.fg} ${style.ring ? `ring-1 ${style.ring}` : ""}`}
        >
          <Icon className="w-4 h-4" />
        </span>
        <div className="flex-1 min-w-0">
          <div className="flex items-baseline justify-between gap-2">
            <span className="text-[12px] font-bold text-[#0f172a] truncate">
              {item.title}
            </span>
            <span className="text-[10px] text-[#94a3b8] shrink-0 whitespace-nowrap">
              {item.timeAgo}
            </span>
          </div>
          <p className="text-[11px] text-[#64748b] leading-snug mt-0.5 line-clamp-2">
            {item.description}
          </p>
        </div>
        {item.unread && (
          <span
            className="mt-1 w-1.5 h-1.5 rounded-full bg-[#2563eb] shrink-0"
            aria-label="Unread"
          />
        )}
      </button>
    </li>
  );
};
