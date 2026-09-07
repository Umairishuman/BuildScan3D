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
  Maximize2,
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

  const getGradientForCategory = (cat: string) => {
    switch (cat) {
      case "MEP Room":
        return "from-blue-950 via-slate-900 to-slate-950 border-blue-500/30";
      case "HVAC Plant":
        return "from-emerald-950 via-slate-900 to-slate-950 border-emerald-500/30";
      case "Corridor":
        return "from-amber-950 via-slate-900 to-slate-950 border-amber-500/30";
      case "Fire Systems":
        return "from-red-950 via-slate-900 to-slate-950 border-red-500/30";
      default:
        return "from-slate-900 via-slate-900 to-slate-950 border-slate-800";
    }
  };

  const CardContent = (
    <div className="h-full flex flex-col justify-between p-5">
      <div>
        {/* Top Header Row: Category & Status Badge */}
        <div className="flex items-center justify-between gap-2 mb-3">
          <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider px-2 py-0.5 rounded bg-slate-800/80 border border-slate-700/50">
            {project.category}
          </span>

          {isReady && (
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <CheckCircle2 className="w-3.5 h-3.5" />
              Ready for Inspection
            </span>
          )}

          {isProcessing && (
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-amber-500/10 text-amber-400 border border-amber-500/20 animate-pulse">
              <Activity className="w-3.5 h-3.5 animate-spin" />
              {project.statusLabel}
            </span>
          )}

          {isDraft && (
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-500/10 text-slate-400 border border-slate-700/50">
              <FileEdit className="w-3.5 h-3.5" />
              Draft (Telemetry Logged)
            </span>
          )}
        </div>

        {/* Title and Location */}
        <h3 className="text-base font-bold text-white group-hover:text-cyan-300 transition-colors line-clamp-1">
          {project.name}
        </h3>
        <p className="text-xs text-slate-400 mt-0.5 mb-3">{project.location}</p>

        {/* Description */}
        <p className="text-xs text-slate-400 line-clamp-2 leading-relaxed mb-4">
          {project.description}
        </p>

        {/* Visual 3D Preview Placeholder / Graphic */}
        <div className="w-full h-32 rounded-lg bg-slate-950/70 border border-slate-800/80 overflow-hidden relative group/canvas flex items-center justify-center p-3 mb-4">
          {/* Simulated 3D Gaussian Splatting / Point Cloud Wireframe */}
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-blue-900/20 via-slate-950/60 to-slate-950" />

          {/* Grid lines */}
          <div className="absolute inset-0 bg-[linear-gradient(to_right,#1e293b_1px,transparent_1px),linear-gradient(to_bottom,#1e293b_1px,transparent_1px)] bg-[size:16px_16px] opacity-40" />

          {/* Graphical elements representing 3D scan */}
          <div className="relative z-10 flex flex-col items-center justify-center text-center">
            {isReady ? (
              <>
                <div className="flex items-center gap-2 text-cyan-400 mb-1">
                  <Sparkles className="w-5 h-5 animate-pulse" />
                  <span className="font-mono text-xs font-bold tracking-wider">
                    3D GAUSSIAN SPLAT
                  </span>
                </div>
                <div className="flex items-center gap-3 text-[11px] text-slate-300 font-mono">
                  <span className="flex items-center gap-1">
                    <Layers className="w-3 h-3 text-blue-400" />
                    {project.gaussianCount} Splats
                  </span>
                  <span>•</span>
                  <span className="flex items-center gap-1">
                    <Ruler className="w-3 h-3 text-emerald-400" />
                    {project.accuracy} Accuracy
                  </span>
                </div>
              </>
            ) : isProcessing ? (
              <div className="space-y-2 w-full px-4">
                <div className="flex justify-between text-[11px] text-amber-300 font-mono">
                  <span>Training (splatfacto)...</span>
                  <span>{project.progressPercent}%</span>
                </div>
                <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
                  <div
                    className="bg-gradient-to-r from-amber-500 to-orange-400 h-full rounded-full transition-all duration-500"
                    style={{ width: `${project.progressPercent}%` }}
                  />
                </div>
                <p className="text-[10px] text-slate-400 truncate">
                  {project.currentStep}
                </p>
              </div>
            ) : (
              <div className="text-slate-400 text-xs flex flex-col items-center gap-1">
                <Clock className="w-5 h-5 text-slate-500" />
                <span>Raw 120Hz Telemetry & Video Ready</span>
              </div>
            )}
          </div>
        </div>

        {/* Metadata Details */}
        <div className="grid grid-cols-2 gap-2 text-[11px] text-slate-400 border-t border-slate-800/80 pt-3">
          <div className="flex items-center gap-1.5 truncate">
            <Calendar className="w-3.5 h-3.5 text-slate-500 shrink-0" />
            <span className="truncate">{project.dateCaptured}</span>
          </div>
          <div className="flex items-center gap-1.5 truncate">
            <Smartphone className="w-3.5 h-3.5 text-slate-500 shrink-0" />
            <span className="truncate">{project.captureDevice}</span>
          </div>
        </div>
      </div>

      {/* Bottom Action Button */}
      <div className="mt-4 pt-3 border-t border-slate-800/80">
        {isReady && (
          <div className="flex items-center justify-between text-xs font-semibold text-cyan-400 group-hover:text-cyan-300">
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
            className="w-full flex items-center justify-center gap-2 py-1.5 rounded-lg bg-amber-500/10 hover:bg-amber-500/20 text-amber-300 border border-amber-500/30 text-xs font-semibold transition-colors"
          >
            <Activity className="w-3.5 h-3.5" />
            <span>Inspect Active Pipeline Queue</span>
          </button>
        )}
        {isDraft && (
          <div className="flex items-center justify-between text-xs font-medium text-slate-400">
            <span>Upload to Nerfstudio Queue</span>
            <Maximize2 className="w-3.5 h-3.5" />
          </div>
        )}
      </div>
    </div>
  );

  if (isReady) {
    return (
      <Link
        href={`/viewer/${project.id}`}
        className={`group block rounded-2xl bg-gradient-to-b ${getGradientForCategory(
          project.category
        )} border shadow-xl hover:shadow-cyan-500/10 hover:border-cyan-500/50 transition-all duration-300`}
      >
        {CardContent}
      </Link>
    );
  }

  return (
    <div
      onClick={() => isProcessing && onOpenProcessingModal(project)}
      className={`group block rounded-2xl bg-gradient-to-b ${getGradientForCategory(
        project.category
      )} border shadow-xl ${
        isProcessing
          ? "cursor-pointer hover:border-amber-500/50 hover:shadow-amber-500/10"
          : "opacity-85"
      } transition-all duration-300`}
    >
      {CardContent}
    </div>
  );
};
