"use client";

import React, { useState } from "react";
import Link from "next/link";
import { Calendar, Layers, MoreHorizontal, Sparkles, Trash2 } from "lucide-react";
import { BuildingPlan } from "@/lib/mockData";

interface UserPlanCardProps {
  plan: BuildingPlan;
  onDelete: (projectId: string) => void;
}

/**
 * Card variant for user-uploaded floor plans. Same visual footprint as
 * `ProjectCard` so they mix cleanly in the same grid, but the thumbnail comes
 * from the first floor's uploaded image and the overflow menu exposes a
 * Delete action (only user plans are deletable).
 */
export const UserPlanCard: React.FC<UserPlanCardProps> = ({
  plan,
  onDelete,
}) => {
  const [menuOpen, setMenuOpen] = useState(false);
  const [confirmingDelete, setConfirmingDelete] = useState(false);

  const heroFloor =
    plan.floors.find((f) => f.planImageDataUrl) ?? plan.floors[0];
  const heroImage = heroFloor?.planImageDataUrl;
  const totalRooms = plan.floors.reduce((acc, f) => acc + f.rooms.length, 0);
  const created = plan.createdAt
    ? new Date(plan.createdAt).toLocaleDateString(undefined, {
        month: "short",
        day: "numeric",
        year: "numeric",
      })
    : "—";

  const openMenu = (event: React.MouseEvent) => {
    event.preventDefault();
    event.stopPropagation();
    setMenuOpen((v) => !v);
  };

  const requestDelete = (event: React.MouseEvent) => {
    event.preventDefault();
    event.stopPropagation();
    setMenuOpen(false);
    setConfirmingDelete(true);
  };

  const confirmDelete = (event: React.MouseEvent) => {
    event.preventDefault();
    event.stopPropagation();
    onDelete(plan.projectId);
  };

  const cancelDelete = (event: React.MouseEvent) => {
    event.preventDefault();
    event.stopPropagation();
    setConfirmingDelete(false);
  };

  return (
    <Link
      href={`/floorplan/${plan.projectId}`}
      className="group block cursor-pointer"
    >
      <div className="bg-white rounded-2xl border border-[#e2e8f0] overflow-hidden shadow-sm hover:shadow-md hover:border-[#cbd5e1] transition-all duration-200 flex flex-col justify-between">
        <div>
          {/* Thumbnail (uploaded plan image, or a placeholder) */}
          <div className="relative w-full h-44 bg-slate-100 overflow-hidden">
            {heroImage ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img
                src={heroImage}
                alt={`${plan.buildingName} plan preview`}
                className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
              />
            ) : (
              <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-slate-100 to-slate-200 text-[#94a3b8]">
                <Layers className="w-8 h-8" />
              </div>
            )}

            {/* User-created badge */}
            <div className="absolute bottom-2.5 left-2.5 max-w-[calc(100%-1.25rem)]">
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[11px] font-bold bg-emerald-50/95 backdrop-blur text-[#065f46] border border-emerald-300 shadow-sm">
                <Sparkles className="w-3 h-3" />
                User-created
              </span>
            </div>

            {/* Overflow menu (top-right) */}
            <div className="absolute top-2.5 right-2.5">
              <button
                onClick={openMenu}
                aria-label="Open plan menu"
                className="p-1.5 rounded-lg bg-white/95 backdrop-blur border border-[#e2e8f0] text-[#64748b] hover:text-[#0f172a] shadow-sm cursor-pointer"
              >
                <MoreHorizontal className="w-3.5 h-3.5" />
              </button>
              {menuOpen && (
                <>
                  <div
                    className="fixed inset-0 z-10"
                    onClick={(e) => {
                      e.preventDefault();
                      e.stopPropagation();
                      setMenuOpen(false);
                    }}
                    aria-hidden
                  />
                  <div className="absolute top-full right-0 mt-1 z-20 w-40 p-1 rounded-xl bg-white border border-[#e2e8f0] shadow-lg">
                    <button
                      onClick={requestDelete}
                      className="w-full text-left flex items-center gap-2 px-2.5 py-1.5 rounded-lg text-[11px] font-bold text-[#dc2626] hover:bg-red-50 cursor-pointer"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                      Delete plan
                    </button>
                  </div>
                </>
              )}
            </div>
          </div>

          {/* Text content */}
          <div className="p-4 space-y-1">
            <h3 className="text-sm font-bold text-[#0f172a] group-hover:text-[#2563eb] transition-colors line-clamp-1">
              {plan.buildingName}
            </h3>
            <p className="text-xs text-[#64748b]">
              {plan.floors.length} floor{plan.floors.length === 1 ? "" : "s"} · {totalRooms} room
              {totalRooms === 1 ? "" : "s"}
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="px-4 py-3 border-t border-[#f1f5f9] flex items-center justify-between text-xs text-[#64748b]">
          <div className="flex items-center gap-1.5">
            <Calendar className="w-3.5 h-3.5 text-[#94a3b8]" />
            <span>{created}</span>
          </div>
          <div className="flex items-center gap-1 text-[#2563eb] font-bold">
            <Layers className="w-3.5 h-3.5" />
            <span>Floor plan</span>
          </div>
        </div>
      </div>

      {/* Delete confirmation overlay */}
      {confirmingDelete && (
        <div
          onClick={(e) => {
            e.preventDefault();
            e.stopPropagation();
          }}
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm"
        >
          <div className="w-full max-w-sm bg-white border border-[#e2e8f0] rounded-2xl shadow-2xl p-5 space-y-3">
            <div className="flex items-center gap-2.5">
              <div className="w-9 h-9 rounded-xl bg-red-50 border border-red-100 flex items-center justify-center text-[#dc2626]">
                <Trash2 className="w-4 h-4" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-[#0f172a]">
                  Delete this plan?
                </h3>
                <p className="text-[11px] text-[#64748b]">
                  {plan.buildingName} will be removed from this browser.
                </p>
              </div>
            </div>
            <div className="flex items-center justify-end gap-2 pt-1">
              <button
                onClick={cancelDelete}
                className="px-3 py-1.5 rounded-xl bg-white border border-[#e2e8f0] text-xs font-bold text-[#0f172a] hover:bg-slate-50 cursor-pointer"
              >
                Cancel
              </button>
              <button
                onClick={confirmDelete}
                className="px-3.5 py-1.5 rounded-xl bg-[#dc2626] hover:bg-[#b91c1c] text-white text-xs font-bold cursor-pointer inline-flex items-center gap-1.5"
              >
                <Trash2 className="w-3.5 h-3.5" />
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </Link>
  );
};
