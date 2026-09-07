"use client";

import React, { useState, useEffect } from "react";
import { Project, MOCK_PIPELINE_STEPS, MOCK_TERMINAL_LOGS } from "@/lib/mockData";
import {
  X,
  CheckCircle2,
  Activity,
  Clock,
  Terminal,
  Cpu,
  Database,
  Layers,
  Sparkles,
  Download,
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
  const [logs, setLogs] = useState<string[]>(MOCK_TERMINAL_LOGS);
  const [iter, setIter] = useState(20400);
  const [psnr, setPsnr] = useState(29.4);
  const [loss, setLoss] = useState(0.0031);

  // Live simulation ticker for demonstration effect
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
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div
        className="relative w-full max-w-4xl max-h-[90vh] flex flex-col bg-slate-950 border border-slate-800 rounded-2xl shadow-2xl shadow-blue-500/10 overflow-hidden text-slate-100"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-900/60">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center">
              <Activity className="w-5 h-5 text-amber-400 animate-spin" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-base font-bold text-white">
                  Active Cloud Pipeline Orchestration
                </h2>
                <span className="px-2 py-0.5 rounded-full text-[11px] font-semibold bg-amber-500/15 text-amber-300 border border-amber-500/30">
                  Step 4 of 6: 3DGS Training
                </span>
              </div>
              <p className="text-xs text-slate-400">
                {project?.name || "Basement HVAC Main Duct & Chillers"} • Job ID:{" "}
                <span className="font-mono text-cyan-400">job_8f9a2c_4090</span>
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body: Two Column Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 p-6 overflow-y-auto">
          {/* Left Column: Pipeline Architecture Checklist (7 cols) */}
          <div className="lg:col-span-7 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
                <Database className="w-4 h-4 text-blue-400" />
                <span>Sequential Pipeline Architecture</span>
              </h3>
              <span className="text-xs font-mono text-amber-400 font-semibold">
                Overall Progress: {currentPercent}%
              </span>
            </div>

            {/* Overall Progress Bar */}
            <div className="w-full bg-slate-900 rounded-full h-2.5 overflow-hidden border border-slate-800">
              <div
                className="bg-gradient-to-r from-blue-500 via-amber-500 to-emerald-400 h-full rounded-full transition-all duration-300"
                style={{ width: `${currentPercent}%` }}
              />
            </div>

            {/* Steps Timeline List */}
            <div className="space-y-3 pt-2">
              {MOCK_PIPELINE_STEPS.map((step, idx) => {
                const isComplete = step.status === "complete";
                const isInProgress = step.status === "in_progress";
                const isPending = step.status === "pending";

                return (
                  <div
                    key={step.id}
                    className={`p-3.5 rounded-xl border transition-all ${
                      isInProgress
                        ? "bg-amber-500/5 border-amber-500/40 shadow-lg shadow-amber-500/5"
                        : isComplete
                        ? "bg-slate-900/70 border-slate-800/80"
                        : "bg-slate-950/40 border-slate-900 opacity-60"
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      {/* Step Indicator Icon */}
                      <div className="mt-0.5 shrink-0">
                        {isComplete && (
                          <div className="w-6 h-6 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center">
                            <CheckCircle2 className="w-4 h-4" />
                          </div>
                        )}
                        {isInProgress && (
                          <div className="w-6 h-6 rounded-full bg-amber-500/20 text-amber-400 flex items-center justify-center">
                            <Activity className="w-4 h-4 animate-spin" />
                          </div>
                        )}
                        {isPending && (
                          <div className="w-6 h-6 rounded-full bg-slate-800 text-slate-500 flex items-center justify-center text-xs font-mono">
                            {idx + 1}
                          </div>
                        )}
                      </div>

                      {/* Content */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between gap-2">
                          <h4 className="text-xs font-bold text-white truncate">
                            {step.title}
                          </h4>
                          {step.duration && (
                            <span className="text-[10px] font-mono text-slate-400 shrink-0">
                              {isInProgress
                                ? `${Math.round(iter / 300)}s elapsed`
                                : step.duration}
                            </span>
                          )}
                        </div>

                        <p className="text-[11px] font-mono text-cyan-400/90 mt-0.5">
                          {step.subtitle}
                        </p>

                        <p className="text-[11px] text-slate-400 mt-1 leading-relaxed">
                          {isInProgress
                            ? `Iter ${iter.toLocaleString()} / 30,000. Current Loss: ${loss} | PSNR: ${psnr} dB | Gaussians: 1,248,320`
                            : step.details}
                        </p>

                        {/* In Progress Mini Bar */}
                        {isInProgress && (
                          <div className="mt-2 w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                            <div
                              className="bg-amber-400 h-full rounded-full transition-all duration-300"
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
            <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-300 flex items-center gap-1.5">
                  <Cpu className="w-4 h-4 text-emerald-400" />
                  <span>Cloud GPU Instance</span>
                </span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  NVIDIA RTX 4090 24GB
                </span>
              </div>

              <div className="grid grid-cols-2 gap-2 text-xs font-mono">
                <div className="p-2 rounded-lg bg-slate-950 border border-slate-800/80">
                  <span className="text-[10px] text-slate-500 block">
                    VRAM ALLOCATION
                  </span>
                  <span className="text-cyan-300 font-bold">5.8 / 24.0 GB</span>
                </div>
                <div className="p-2 rounded-lg bg-slate-950 border border-slate-800/80">
                  <span className="text-[10px] text-slate-500 block">
                    GPU UTILIZATION
                  </span>
                  <span className="text-emerald-300 font-bold">98% Compute</span>
                </div>
                <div className="p-2 rounded-lg bg-slate-950 border border-slate-800/80">
                  <span className="text-[10px] text-slate-500 block">
                    SPLATS (GAUSSIANS)
                  </span>
                  <span className="text-amber-300 font-bold">1,248,320</span>
                </div>
                <div className="p-2 rounded-lg bg-slate-950 border border-slate-800/80">
                  <span className="text-[10px] text-slate-500 block">
                    CURRENT PSNR
                  </span>
                  <span className="text-purple-300 font-bold">{psnr} dB</span>
                </div>
              </div>
            </div>

            {/* Live Terminal Log Streamer */}
            <div className="flex-1 flex flex-col rounded-xl bg-black border border-slate-800 overflow-hidden min-h-[220px]">
              <div className="flex items-center justify-between px-3 py-2 bg-slate-900/90 border-b border-slate-800 text-[11px] font-mono text-slate-400">
                <div className="flex items-center gap-2">
                  <Terminal className="w-3.5 h-3.5 text-blue-400" />
                  <span>train_splatfacto.log</span>
                </div>
                <span className="flex items-center gap-1 text-emerald-400">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
                  STREAMING
                </span>
              </div>

              <div className="p-3 font-mono text-[10px] text-slate-300 space-y-1.5 overflow-y-auto max-h-56 leading-relaxed">
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
            <div className="p-3 rounded-lg bg-blue-500/10 border border-blue-500/20 text-xs text-blue-300 flex items-start gap-2">
              <AlertCircle className="w-4 h-4 text-blue-400 shrink-0 mt-0.5" />
              <p className="text-[11px] leading-relaxed">
                <strong className="text-white">FYP Architecture Note:</strong> ARCore
                poses remove the slow COLMAP SfM stage, training photorealistic
                3DGS models in under 5 minutes per scan.
              </p>
            </div>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="flex items-center justify-between px-6 py-4 border-t border-slate-800 bg-slate-900/60">
          <div className="text-xs text-slate-400">
            Estimated time remaining:{" "}
            <span className="font-bold text-white font-mono">1m 45s</span>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={onClose}
              className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-white transition-colors"
            >
              Close Inspector
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

