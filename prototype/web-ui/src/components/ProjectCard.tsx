"use client";

import React from "react";
import Link from "next/link";
import { Project } from "@/lib/mockData";
import {
  Layers,
  Sparkles,
  Calendar,
  Smartphone,
  CheckCircle2,
  Clock,
  FileEdit,
  ArrowRight,
  Activity,
  Ruler,
} from "lucide-react";

interface ProjectCardProps {
  project: Project;
  onOpenProcessingModal: (project: Project) => void;
}

export const ProjectCard: React.FC<ProjectCardProps> = ({
  project,
  onOpenProcessingModal,
}) => {
  const isReady = project.status === "ready";
  const isProcessing = project.status === "processing";
  const isDraft = project.status === "draft";

  const CardContent = (
    <div className="h-full flex flex-col justify-between p-5 bg-white rounded-2xl border border-[#e2e8f0] shadow-sm hover:shadow-md hover:border-[#cbd5e1] transition-all duration-200">
      <div>
        {/* Top Header Row: Category & Status Badge */}
        <div className="flex items-center justify-between gap-2 mb-3">
          <span className="text-[11px] font-bold text-[#475569] uppercase tracking-wider px-2 py-0.5 rounded bg-slate-100 border border-slate-200">
            {project.category}
          </span>

          {isReady && (
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
              Ready for Inspection
            </span>
          )}

          {isProcessing && (
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-50 text-amber-700 border border-amber-200 animate-pulse">
              <Activity className="w-3.5 h-3.5 text-amber-600 animate-spin" />
              {project.statusLabel}
            </span>
          )}

          {isDraft && (
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-100 text-slate-600 border border-slate-200">
              <FileEdit className="w-3.5 h-3.5" />
              Draft (Telemetry Logged)
            </span>
          )}
        </div>

        {/* Title and Location */}
        <h3 className="text-base font-bold text-[#0f172a] group-hover:text-[#2563eb] transition-colors line-clamp-1">
          {project.name}
        </h3>
        <p className="text-xs text-[#64748b] mt-0.5 mb-3">{project.location}</p>

        {/* Description */}
        <p className="text-xs text-[#64748b] line-clamp-2 leading-relaxed mb-4">
          {project.description}
        </p>

        {/* Visual 3D Preview Placeholder / Graphic */}
        <div className="w-full h-32 rounded-xl bg-[#f0f7fd] border border-[#d9e8f8] overflow-hidden relative group/canvas flex items-center justify-center p-3 mb-4">
          {/* Blueprint Grid lines */}
          <div className="absolute inset-0 bg-[linear-gradient(to_right,#cbd5e1_1px,transparent_1px),linear-gradient(to_bottom,#cbd5e1_1px,transparent_1px)] bg-[size:16px_16px] opacity-35" />

          {/* Graphical elements representing 3D scan */}
          <div className="relative z-10 flex flex-col items-center justify-center text-center">
            {isReady ? (
              <>
                <div className="flex items-center gap-1.5 text-[#2563eb] mb-1">
                  <Sparkles className="w-4 h-4" />
                  <span className="font-mono text-xs font-bold tracking-wider">
                    3D GAUSSIAN SPLAT
                  </span>
                </div>
                <div className="flex items-center gap-3 text-[11px] text-[#334155] font-mono font-medium">
                  <span className="flex items-center gap-1">
                    <Layers className="w-3 h-3 text-[#2563eb]" />
                    {project.gaussianCount} Splats
                  </span>
                  <span>•</span>
                  <span className="flex items-center gap-1">
                    <Ruler className="w-3 h-3 text-emerald-600" />
                    {project.accuracy} Accuracy
                  </span>
                </div>
              </>
            ) : isProcessing ? (
              <div className="space-y-2 w-full px-4">
                <div className="flex justify-between text-[11px] text-amber-800 font-mono font-semibold">
                  <span>Training (splatfacto)...</span>
                  <span>{project.progressPercent}%</span>
                </div>
                <div className="w-full bg-slate-200 rounded-full h-2 overflow-hidden">
                  <div
                    className="bg-gradient-to-r from-amber-500 to-[#2563eb] h-full rounded-full transition-all duration-500"
                    style={{ width: `${project.progressPercent}%` }}
                  />
                </div>
                <p className="text-[10px] text-[#64748b] truncate">
                  {project.currentStep}
                </p>
              </div>
            ) : (
              <div className="text-[#64748b] text-xs flex flex-col items-center gap-1">
                <Clock className="w-5 h-5 text-[#94a3b8]" />
                <span>Raw 120Hz Telemetry & Video Ready</span>
              </div>
            )}
          </div>
        </div>

        {/* Metadata Details */}
        <div className="grid grid-cols-2 gap-2 text-[11px] text-[#64748b] border-t border-[#f1f5f9] pt-3">
          <div className="flex items-center gap-1.5 truncate">
            <Calendar className="w-3.5 h-3.5 text-[#94a3b8] shrink-0" />
            <span className="truncate">{project.dateCaptured}</span>
          </div>
          <div className="flex items-center gap-1.5 truncate">
            <Smartphone className="w-3.5 h-3.5 text-[#94a3b8] shrink-0" />
            <span className="truncate">{project.captureDevice}</span>
          </div>
        </div>
      </div>

      {/* Bottom Action Button */}
      <div className="mt-4 pt-3 border-t border-[#f1f5f9]">
        {isReady && (
          <div className="flex items-center justify-between text-xs font-bold text-[#2563eb] group-hover:text-[#1d4ed8]">
            <span>Launch 3D Workspace</span>
            <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </div>
        )}
        {isProcessing && (
          <button
            type="button"
            onClick={(e) => {
              e.preventDefault();
              onOpenProcessingModal(project);
            }}
            className="w-full flex items-center justify-center gap-1.5 py-1.5 rounded-xl bg-amber-50 hover:bg-amber-100 text-amber-700 border border-amber-200 text-xs font-bold transition-colors cursor-pointer"
          >
            <Activity className="w-3.5 h-3.5" />
            <span>Inspect Cloud Queue</span>
          </button>
        )}
        {isDraft && (
          <div className="flex items-center justify-between text-xs font-semibold text-[#64748b]">
            <span>Upload to Reconstruction Pipeline</span>
            <ArrowRight className="w-4 h-4" />
          </div>
        )}
      </div>
    </div>
  );

  if (isReady) {
    return (
      <Link href={`/viewer/${project.id}`} className="group block">
        {CardContent}
      </Link>
    );
  }

  return (
    <div
      onClick={() => isProcessing && onOpenProcessingModal(project)}
      className={`group block ${isProcessing ? "cursor-pointer" : "opacity-90"}`}
    >
      {CardContent}
    </div>
  );
};
