"use client";

import React from "react";
import Link from "next/link";
import Image from "next/image";
import { Project } from "@/lib/mockData";
import { Calendar, Shield, MoreHorizontal } from "lucide-react";

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
  const isComplete = project.status === "complete";
  const isDraft = project.status === "draft";

  const CardBody = (
    <div className="bg-white rounded-2xl border border-[#e2e8f0] overflow-hidden shadow-sm hover:shadow-md hover:border-[#cbd5e1] transition-all duration-200 flex flex-col justify-between">
      <div>
        {/* Card Thumbnail with Status Badge */}
        <div className="relative w-full h-44 bg-slate-100 overflow-hidden group/img">
          <Image
            src={project.thumbnail}
            alt={project.name}
            fill
            className="object-cover group-hover/img:scale-105 transition-transform duration-300"
          />

          {/* Status Badge Overlay */}
          <div className="absolute bottom-2.5 left-2.5">
            {isProcessing && (
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[11px] font-bold bg-[#fef3c7]/95 backdrop-blur text-[#b45309] border border-amber-300 shadow-sm">
                <span className="w-1.5 h-1.5 rounded-full bg-[#f59e0b] animate-ping" />
                Processing
              </span>
            )}
            {isReady && (
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[11px] font-bold bg-[#d1fae5]/95 backdrop-blur text-[#065f46] border border-emerald-300 shadow-sm">
                <span className="w-1.5 h-1.5 rounded-full bg-[#10b981]" />
                Ready
              </span>
            )}
            {isComplete && (
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[11px] font-bold bg-[#ccfbf1]/95 backdrop-blur text-[#115e59] border border-teal-300 shadow-sm">
                <span className="w-1.5 h-1.5 rounded-full bg-[#14b8a6]" />
                Complete
              </span>
            )}
            {isDraft && (
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[11px] font-bold bg-[#f1f5f9]/95 backdrop-blur text-[#475569] border border-slate-300 shadow-sm">
                <span className="w-1.5 h-1.5 rounded-full bg-[#94a3b8]" />
                Draft
              </span>
            )}
          </div>
        </div>

        {/* Card Text Content */}
        <div className="p-4 space-y-1">
          <h3 className="text-sm font-bold text-[#0f172a] group-hover:text-[#2563eb] transition-colors line-clamp-1">
            {project.name}
          </h3>
          <p className="text-xs text-[#64748b]">
            {project.floor} • {project.block} • {project.area}
          </p>
        </div>
      </div>

      {/* Card Footer */}
      <div className="px-4 py-3 border-t border-[#f1f5f9] flex items-center justify-between text-xs text-[#64748b]">
        <div className="flex items-center gap-1.5">
          <Calendar className="w-3.5 h-3.5 text-[#94a3b8]" />
          <span>{project.dateCaptured}</span>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1">
            <Shield className="w-3.5 h-3.5 text-[#94a3b8]" />
            <span>{project.scansCount} scans</span>
          </div>

          <button
            onClick={(e) => {
              e.preventDefault();
              e.stopPropagation();
            }}
            className="p-1 rounded text-[#94a3b8] hover:text-[#0f172a] hover:bg-slate-100 transition-colors"
          >
            <MoreHorizontal className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );

  if (isReady || isComplete) {
    return (
      <Link href={`/viewer/${project.id}`} className="group block cursor-pointer">
        {CardBody}
      </Link>
    );
  }

  return (
    <div
      onClick={() => isProcessing && onOpenProcessingModal(project)}
      className={`group block ${isProcessing ? "cursor-pointer" : ""}`}
    >
      {CardBody}
    </div>
  );
};
