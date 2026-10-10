import os

base_dir = r"d:\FYP\prototype\web-ui"

# Navbar.tsx
navbar_tsx = """\"use client\";

import React from "react";
import Link from "next/link";
import { Activity, HardHat, Search, ShieldCheck } from "lucide-react";

interface NavbarProps {
  onOpenJobStatus?: () => void;
  activeProcessingCount?: number;
}

export const Navbar: React.FC<NavbarProps> = ({
  onOpenJobStatus,
  activeProcessingCount = 1,
}) => {
  return (
    <header className="sticky top-0 z-40 w-full border-b border-[#e2e8f0] bg-white/90 backdrop-blur-md text-[#0f172a]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-4">
        {/* Brand & System Tag */}
        <div className="flex items-center gap-8">
          <Link href="/dashboard" className="flex items-center gap-2.5 group">
            {/* Isometric 3D Cube Icon */}
            <svg
              className="w-8 h-8 text-[#2563eb] group-hover:scale-105 transition-transform"
              viewBox="0 0 48 48"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M24 4L42 14.3923V35.1769L24 45.5692L6 35.1769V14.3923L24 4Z"
                stroke="currentColor"
                strokeWidth="3.2"
                strokeLinejoin="round"
              />
              <path
                d="M24 4V24.5M24 24.5L42 14.5M24 24.5L6 14.5M24 24.5V45.5"
                stroke="currentColor"
                strokeWidth="2.8"
                strokeLinecap="round"
              />
              <circle cx="24" cy="24.5" r="3" fill="currentColor" />
              <circle cx="15" cy="19.5" r="1.5" fill="currentColor" />
              <circle cx="33" cy="19.5" r="1.5" fill="currentColor" />
              <circle cx="24" cy="35" r="1.5" fill="currentColor" />
            </svg>

            <div>
              <div className="flex items-center gap-1.5">
                <span className="font-bold text-base tracking-tight text-[#0f172a]">
                  BuildScan <span className="text-[#2563eb]">3D</span>
                </span>
                <span className="text-[10px] font-semibold uppercase tracking-wider px-1.5 py-0.5 rounded bg-blue-50 text-[#2563eb] border border-blue-200">
                  Enterprise
                </span>
              </div>
              <p className="text-[10px] text-[#64748b] leading-none">
                Spatial Intelligence & 3DGS
              </p>
            </div>
          </Link>

          <nav className="hidden md:flex items-center gap-1 text-xs font-semibold text-[#64748b]">
            <Link
              href="/dashboard"
              className="px-3 py-1.5 rounded-lg text-[#2563eb] bg-blue-50 font-bold transition-colors"
            >
              Projects & Scans
            </Link>
            <Link
              href="/viewer/sector-4-mep"
              className="px-3 py-1.5 rounded-lg hover:text-[#0f172a] hover:bg-slate-100 transition-colors"
            >
              3D Workspace
            </Link>
          </nav>
        </div>

        {/* Global Search */}
        <div className="hidden lg:flex items-center flex-1 max-w-xs relative">
          <Search className="w-3.5 h-3.5 text-[#94a3b8] absolute left-3 pointer-events-none" />
          <input
            type="text"
            placeholder="Search scans, sectors, rooms..."
            className="w-full pl-8 pr-4 py-1.5 bg-[#f8fafc] border border-[#e2e8f0] rounded-xl text-xs text-[#0f172a] placeholder-[#94a3b8] focus:outline-none focus:border-[#2563eb] focus:bg-white transition-all"
          />
        </div>

        {/* Right Section: Status Indicator & Profile */}
        <div className="flex items-center gap-3">
          {/* Active Job Trigger Button */}
          {activeProcessingCount > 0 && onOpenJobStatus && (
            <button
              onClick={onOpenJobStatus}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-amber-50 border border-amber-200 text-amber-700 hover:bg-amber-100 text-xs font-semibold transition-all cursor-pointer"
              title="Click to view live 3DGS training queue"
            >
              <Activity className="w-3.5 h-3.5 text-amber-600 animate-spin" />
              <span>1 Pipeline Active (68%)</span>
            </button>
          )}

          {/* Defense Badge */}
          <div className="hidden sm:flex items-center gap-1.5 text-xs text-emerald-700 bg-emerald-50 border border-emerald-200 px-2.5 py-1 rounded-xl">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
            <span className="font-mono text-[11px] font-semibold">FAST-NUCES PoC</span>
          </div>

          <div className="h-5 w-[1px] bg-[#e2e8f0] hidden sm:block" />

          {/* User Profile Snippet */}
          <div className="flex items-center gap-2.5 pl-1">
            <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-blue-600 to-cyan-500 flex items-center justify-center text-white font-bold text-xs shadow-sm">
              SJ
            </div>
            <div className="hidden xl:block text-left">
              <div className="text-xs font-bold text-[#0f172a]">
                Sarah Jenkins
              </div>
              <div className="text-[10px] text-[#64748b] flex items-center gap-1">
                <HardHat className="w-2.5 h-2.5 text-amber-500" />
                <span>Lead MEP Manager</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};
"""

# ProjectCard.tsx
project_card_tsx = """\"use client\";

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
"""

# JobStatusModal.tsx
job_status_modal_tsx = """\"use client\";

import React, { useState, useEffect } from "react";
import { Project, MOCK_PIPELINE_STEPS, MOCK_TERMINAL_LOGS } from "@/lib/mockData";
import {
  X,
  CheckCircle2,
  Activity,
  Terminal,
  Cpu,
  Database,
  AlertCircle,
} from "lucide-react";

interface JobStatusModalProps {
  isOpen: boolean;
  onClose: () => void;
  project?: Project | null;
}

export const JobStatusModal: React.FC<JobStatusModalProps> = ({
  isOpen,
  onClose,
  project,
}) => {
  const [logs] = useState<string[]>(MOCK_TERMINAL_LOGS);
  const [iter, setIter] = useState(20400);
  const [psnr, setPsnr] = useState(29.4);
  const [loss, setLoss] = useState(0.0031);

  useEffect(() => {
    if (!isOpen) return;

    const interval = setInterval(() => {
      setIter((prev) => {
        const next = prev + 50;
        if (next > 30000) return 30000;
        return next;
      });

      setPsnr((prev) => +(prev + 0.02).toFixed(2));
      setLoss((prev) => +(Math.max(0.0018, prev - 0.00005)).toFixed(4));
    }, 1200);

    return () => clearInterval(interval);
  }, [isOpen]);

  if (!isOpen) return null;

  const currentPercent = Math.round((iter / 30000) * 100);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm animate-in fade-in duration-200">
      <div
        className="relative w-full max-w-4xl max-h-[90vh] flex flex-col bg-white border border-[#e2e8f0] rounded-2xl shadow-2xl overflow-hidden text-[#0f172a]"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-[#e2e8f0] bg-[#f8fafc]">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-amber-50 border border-amber-200 flex items-center justify-center">
              <Activity className="w-5 h-5 text-amber-600 animate-spin" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-base font-bold text-[#0f172a]">
                  Active Cloud Pipeline Orchestration
                </h2>
                <span className="px-2 py-0.5 rounded-full text-[11px] font-semibold bg-amber-50 text-amber-700 border border-amber-200">
                  Step 4 of 6: 3DGS Training
                </span>
              </div>
              <p className="text-xs text-[#64748b]">
                {project?.name || "Basement HVAC Main Duct & Chillers"} • Job ID:{" "}
                <span className="font-mono text-[#2563eb] font-semibold">job_8f9a2c_4090</span>
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-2 rounded-xl text-[#64748b] hover:text-[#0f172a] hover:bg-slate-100 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body: Two Column Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 p-6 overflow-y-auto bg-white">
          {/* Left Column: Pipeline Architecture Checklist (7 cols) */}
          <div className="lg:col-span-7 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-bold text-[#475569] uppercase tracking-wider flex items-center gap-2">
                <Database className="w-4 h-4 text-[#2563eb]" />
                <span>Sequential Pipeline Architecture</span>
              </h3>
              <span className="text-xs font-mono text-amber-700 font-bold">
                Overall Progress: {currentPercent}%
              </span>
            </div>

            {/* Overall Progress Bar */}
            <div className="w-full bg-slate-100 rounded-full h-2.5 overflow-hidden border border-[#e2e8f0]">
              <div
                className="bg-gradient-to-r from-[#2563eb] via-amber-500 to-emerald-500 h-full rounded-full transition-all duration-300"
                style={{ width: `${currentPercent}%` }}
              />
            </div>

            {/* Steps Timeline List */}
            <div className="space-y-2.5 pt-1">
              {MOCK_PIPELINE_STEPS.map((step, idx) => {
                const isComplete = step.status === "complete";
                const isInProgress = step.status === "in_progress";
                const isPending = step.status === "pending";

                return (
                  <div
                    key={step.id}
                    className={`p-3.5 rounded-xl border transition-all ${
                      isInProgress
                        ? "bg-amber-50/50 border-amber-300 shadow-sm"
                        : isComplete
                        ? "bg-[#f8fafc] border-[#e2e8f0]"
                        : "bg-white border-[#f1f5f9] opacity-50"
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      {/* Step Indicator Icon */}
                      <div className="mt-0.5 shrink-0">
                        {isComplete && (
                          <div className="w-6 h-6 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center">
                            <CheckCircle2 className="w-4 h-4" />
                          </div>
                        )}
                        {isInProgress && (
                          <div className="w-6 h-6 rounded-full bg-amber-100 text-amber-700 flex items-center justify-center">
                            <Activity className="w-4 h-4 animate-spin" />
                          </div>
                        )}
                        {isPending && (
                          <div className="w-6 h-6 rounded-full bg-slate-100 text-slate-400 flex items-center justify-center text-xs font-mono">
                            {idx + 1}
                          </div>
                        )}
                      </div>

                      {/* Content */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between gap-2">
                          <h4 className="text-xs font-bold text-[#0f172a] truncate">
                            {step.title}
                          </h4>
                          {step.duration && (
                            <span className="text-[10px] font-mono text-[#64748b] shrink-0 font-medium">
                              {isInProgress
                                ? `${Math.round(iter / 300)}s elapsed`
                                : step.duration}
                            </span>
                          )}
                        </div>

                        <p className="text-[11px] font-mono text-[#2563eb] mt-0.5 font-medium">
                          {step.subtitle}
                        </p>

                        <p className="text-[11px] text-[#64748b] mt-1 leading-relaxed">
                          {isInProgress
                            ? `Iter ${iter.toLocaleString()} / 30,000. Loss: ${loss} | PSNR: ${psnr} dB | Gaussians: 1,248,320`
                            : step.details}
                        </p>

                        {/* In Progress Mini Bar */}
                        {isInProgress && (
                          <div className="mt-2 w-full bg-slate-200 rounded-full h-1.5 overflow-hidden">
                            <div
                              className="bg-amber-500 h-full rounded-full transition-all duration-300"
                              style={{ width: `${(iter / 30000) * 100}%` }}
                            />
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Right Column: Live Cloud GPU & Terminal Logs (5 cols) */}
          <div className="lg:col-span-5 flex flex-col gap-4">
            {/* GPU Telemetry Card */}
            <div className="p-4 rounded-xl bg-[#f8fafc] border border-[#e2e8f0] space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-[#0f172a] flex items-center gap-1.5">
                  <Cpu className="w-4 h-4 text-emerald-600" />
                  <span>Cloud GPU Instance</span>
                </span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-200 font-semibold">
                  NVIDIA RTX 4090 24GB
                </span>
              </div>

              <div className="grid grid-cols-2 gap-2 text-xs font-mono">
                <div className="p-2 rounded-lg bg-white border border-[#e2e8f0]">
                  <span className="text-[10px] text-[#64748b] block font-sans">
                    VRAM ALLOCATION
                  </span>
                  <span className="text-[#2563eb] font-bold">5.8 / 24.0 GB</span>
                </div>
                <div className="p-2 rounded-lg bg-white border border-[#e2e8f0]">
                  <span className="text-[10px] text-[#64748b] block font-sans">
                    GPU UTILIZATION
                  </span>
                  <span className="text-emerald-700 font-bold">98% Compute</span>
                </div>
                <div className="p-2 rounded-lg bg-white border border-[#e2e8f0]">
                  <span className="text-[10px] text-[#64748b] block font-sans">
                    SPLATS (GAUSSIANS)
                  </span>
                  <span className="text-amber-700 font-bold">1,248,320</span>
                </div>
                <div className="p-2 rounded-lg bg-white border border-[#e2e8f0]">
                  <span className="text-[10px] text-[#64748b] block font-sans">
                    CURRENT PSNR
                  </span>
                  <span className="text-purple-700 font-bold">{psnr} dB</span>
                </div>
              </div>
            </div>

            {/* Live Terminal Log Streamer */}
            <div className="flex-1 flex flex-col rounded-xl bg-[#0f172a] border border-slate-800 overflow-hidden min-h-[200px]">
              <div className="flex items-center justify-between px-3 py-2 bg-[#1e293b] text-[11px] font-mono text-slate-300">
                <div className="flex items-center gap-2">
                  <Terminal className="w-3.5 h-3.5 text-[#38bdf8]" />
                  <span>train_splatfacto.log</span>
                </div>
                <span className="flex items-center gap-1 text-emerald-400 font-semibold text-[10px]">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
                  STREAMING
                </span>
              </div>

              <div className="p-3 font-mono text-[10px] text-slate-300 space-y-1.5 overflow-y-auto max-h-52 leading-relaxed">
                {logs.map((log, index) => (
                  <div
                    key={index}
                    className={
                      log.includes("[ACTIVE]")
                        ? "text-amber-300 font-bold animate-pulse"
                        : log.includes("NERFSTUDIO")
                        ? "text-purple-300"
                        : log.includes("SCALE")
                        ? "text-emerald-300"
                        : log.includes("TRANSFORMS")
                        ? "text-cyan-300"
                        : "text-slate-400"
                    }
                  >
                    {log.includes("[ACTIVE]")
                      ? `[00:04:12] [TRAIN] Step ${iter.toLocaleString()}/30,000 | Loss: ${loss} | PSNR: ${psnr} dB | Gaussians: 1,248,320 [ACTIVE]`
                      : log}
                  </div>
                ))}
              </div>
            </div>

            {/* Committee Explanation Note */}
            <div className="p-3 rounded-xl bg-blue-50 border border-blue-200 text-xs text-[#1e40af] flex items-start gap-2">
              <AlertCircle className="w-4 h-4 text-[#2563eb] shrink-0 mt-0.5" />
              <p className="text-[11px] leading-relaxed">
                <strong className="text-[#0f172a]">FYP Architecture Note:</strong> ARCore
                poses remove the slow COLMAP SfM stage, training photorealistic
                3DGS models in under 5 minutes per scan.
              </p>
            </div>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="flex items-center justify-between px-6 py-4 border-t border-[#e2e8f0] bg-[#f8fafc]">
          <div className="text-xs text-[#64748b]">
            Estimated time remaining:{" "}
            <span className="font-bold text-[#0f172a] font-mono">1m 45s</span>
          </div>

          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl bg-[#2563eb] hover:bg-[#1d4ed8] text-xs font-semibold text-white transition-colors cursor-pointer"
          >
            Close Inspector
          </button>
        </div>
      </div>
    </div>
  );
};
"""

# NewCaptureModal.tsx
new_capture_modal_tsx = """\"use client\";

import React, { useState } from "react";
import {
  X,
  Smartphone,
  UploadCloud,
  CheckCircle2,
  QrCode,
  Sparkles,
} from "lucide-react";

interface NewCaptureModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const NewCaptureModal: React.FC<NewCaptureModalProps> = ({
  isOpen,
  onClose,
}) => {
  const [activeTab, setActiveTab] = useState<"mobile_qr" | "direct_upload">(
    "mobile_qr"
  );
  const [isSimulatingUpload, setIsSimulatingUpload] = useState(false);
  const [uploadComplete, setUploadComplete] = useState(false);

  if (!isOpen) return null;

  const handleSimulateUpload = () => {
    setIsSimulatingUpload(true);
    setTimeout(() => {
      setIsSimulatingUpload(false);
      setUploadComplete(true);
    }, 1800);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm animate-in fade-in duration-200">
      <div
        className="relative w-full max-w-lg bg-white border border-[#e2e8f0] rounded-2xl shadow-2xl overflow-hidden text-[#0f172a]"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-[#e2e8f0] bg-[#f8fafc]">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-blue-50 border border-blue-200 flex items-center justify-center text-[#2563eb]">
              <Smartphone className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-[#0f172a]">
                Initiate New Site Capture
              </h2>
              <p className="text-xs text-[#64748b]">
                Sync Mobile AR Telemetry or Direct Upload
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-[#64748b] hover:text-[#0f172a] hover:bg-slate-100"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-4">
          <div className="flex rounded-xl bg-slate-100 p-1 border border-slate-200">
            <button
              onClick={() => {
                setActiveTab("mobile_qr");
                setUploadComplete(false);
              }}
              className={`flex-1 py-1.5 text-xs font-semibold rounded-lg transition-all cursor-pointer ${
                activeTab === "mobile_qr"
                  ? "bg-white text-[#2563eb] shadow-sm font-bold"
                  : "text-[#64748b] hover:text-[#0f172a]"
              }`}
            >
              Scan with Mobile App
            </button>
            <button
              onClick={() => {
                setActiveTab("direct_upload");
                setUploadComplete(false);
              }}
              className={`flex-1 py-1.5 text-xs font-semibold rounded-lg transition-all cursor-pointer ${
                activeTab === "direct_upload"
                  ? "bg-white text-[#2563eb] shadow-sm font-bold"
                  : "text-[#64748b] hover:text-[#0f172a]"
              }`}
            >
              Direct Dataset Upload (.tar.gz)
            </button>
          </div>

          {activeTab === "mobile_qr" ? (
            <div className="flex flex-col items-center text-center p-6 rounded-2xl bg-[#f8fafc] border border-[#e2e8f0] space-y-3">
              <div className="p-4 bg-white rounded-2xl shadow-sm border border-slate-200">
                <QrCode className="w-28 h-28 text-[#0f172a]" />
              </div>
              <p className="text-xs font-mono text-[#2563eb] font-bold">
                PAIR CODE: #BST-8842-NUCES
              </p>
              <p className="text-xs text-[#64748b] max-w-xs">
                Open the <strong>BuildScan Mobile App</strong> on your phone and
                scan this code to stream 120Hz AR telemetry directly to this
                project.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="border-2 border-dashed border-[#cbd5e1] hover:border-[#2563eb] rounded-2xl p-6 text-center space-y-2 bg-[#f8fafc] transition-colors">
                <UploadCloud className="w-8 h-8 text-[#2563eb] mx-auto animate-bounce" />
                <div className="text-xs text-[#0f172a] font-bold">
                  Drag & drop raw scan bundle
                </div>
                <p className="text-[11px] text-[#64748b]">
                  Accepts <code className="text-[#2563eb] font-semibold">video.mp4</code>,{" "}
                  <code className="text-[#2563eb] font-semibold">poses.csv</code>, and{" "}
                  <code className="text-[#2563eb] font-semibold">points.csv</code>
                </p>
              </div>

              {!uploadComplete ? (
                <button
                  onClick={handleSimulateUpload}
                  disabled={isSimulatingUpload}
                  className="w-full py-2.5 rounded-xl bg-[#2563eb] hover:bg-[#1d4ed8] text-white text-xs font-bold transition-colors flex items-center justify-center gap-2 shadow-sm cursor-pointer"
                >
                  {isSimulatingUpload ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                      <span>Packaging & Dispatching to GPU Worker...</span>
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-4 h-4" />
                      <span>Simulate Dispatch to GPU Worker</span>
                    </>
                  )}
                </button>
              ) : (
                <div className="p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs flex items-center gap-2 font-medium">
                  <CheckCircle2 className="w-4 h-4 shrink-0 text-emerald-600" />
                  <span>
                    Dispatched job to RTX 4090 cloud queue! View in Active Jobs.
                  </span>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-3 border-t border-[#e2e8f0] bg-[#f8fafc] flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-xs font-semibold text-[#0f172a] cursor-pointer"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
"""

with open(os.path.join(base_dir, "src", "components", "Navbar.tsx"), "w", encoding="utf-8") as f:
    f.write(navbar_tsx)

with open(os.path.join(base_dir, "src", "components", "ProjectCard.tsx"), "w", encoding="utf-8") as f:
    f.write(project_card_tsx)

with open(os.path.join(base_dir, "src", "components", "JobStatusModal.tsx"), "w", encoding="utf-8") as f:
    f.write(job_status_modal_tsx)

with open(os.path.join(base_dir, "src", "components", "NewCaptureModal.tsx"), "w", encoding="utf-8") as f:
    f.write(new_capture_modal_tsx)

print("Navbar, ProjectCard, JobStatusModal, NewCaptureModal updated successfully.")

