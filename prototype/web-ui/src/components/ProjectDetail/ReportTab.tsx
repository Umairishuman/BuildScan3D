"use client";

import React, { useState } from "react";
import Image from "next/image";
import {
  Building2,
  CheckCircle2,
  Download,
  FileText,
  Flag,
  Minus,
  Plus,
  RefreshCcw,
  Sparkles,
} from "lucide-react";
import {
  ChangeType,
  MOCK_CHANGE_LOG,
  Project,
} from "@/lib/mockData";

interface ReportTabProps {
  project: Project;
}

const CHANGE_STYLE: Record<
  ChangeType,
  { label: string; text: string; bg: string; Icon: React.ComponentType<{ className?: string }> }
> = {
  added: { label: "Added", text: "text-[#059669]", bg: "bg-emerald-50", Icon: Plus },
  removed: { label: "Removed", text: "text-[#dc2626]", bg: "bg-red-50", Icon: Minus },
  modified: { label: "Modified", text: "text-[#d97706]", bg: "bg-amber-50", Icon: RefreshCcw },
};

export const ReportTab: React.FC<ReportTabProps> = ({ project }) => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedAt, setGeneratedAt] = useState<string | null>(
    "Apr 28, 2025 · 4:12 PM"
  );

  const flaggedIssues = MOCK_CHANGE_LOG;

  const handleGenerate = () => {
    setIsGenerating(true);
    window.setTimeout(() => {
      setIsGenerating(false);
      const now = new Date();
      setGeneratedAt(
        `${now.toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" })} · ${now.toLocaleTimeString(undefined, { hour: "numeric", minute: "2-digit" })}`
      );
    }, 900);
  };

  return (
    <div className="flex-1 min-h-0 overflow-y-auto bg-[#eef3f9]">
      {/* Sub-toolbar */}
      <div className="sticky top-0 z-10 px-5 py-3 bg-[#eef3f9]/95 backdrop-blur-md border-b border-[#e2e8f0] flex items-center justify-between gap-3 flex-wrap">
        <div className="flex items-center gap-2">
          <FileText className="w-4 h-4 text-[#2563eb]" />
          <h2 className="text-sm font-bold text-[#0f172a]">Coordination Report</h2>
          {generatedAt && (
            <span className="text-[10px] text-[#64748b]">
              Last generated {generatedAt}
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handleGenerate}
            disabled={isGenerating}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-[#2563eb] hover:bg-[#1d4ed8] disabled:bg-[#94a3b8] text-white text-[11px] font-bold shadow-sm cursor-pointer disabled:cursor-wait"
          >
            {isGenerating ? (
              <>
                <RefreshCcw className="w-3.5 h-3.5 animate-spin" />
                Generating...
              </>
            ) : (
              <>
                <Sparkles className="w-3.5 h-3.5" />
                Generate Report
              </>
            )}
          </button>
          <button className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-[#e2e8f0] bg-white text-[11px] font-bold text-[#0f172a] hover:bg-slate-50 shadow-sm cursor-pointer">
            <Download className="w-3.5 h-3.5" />
            Export as PDF
          </button>
        </div>
      </div>

      {/* PDF-style preview page */}
      <div className="p-6 flex justify-center">
        <article className="w-full max-w-[820px] bg-white shadow-xl rounded-md border border-[#e2e8f0] overflow-hidden">
          {/* Header */}
          <header className="px-10 py-8 border-b border-[#f1f5f9] flex items-start justify-between gap-4">
            <div>
              <p className="text-[10px] font-bold uppercase tracking-widest text-[#94a3b8]">
                BuildScan 3D · Coordination Report
              </p>
              <h1 className="mt-1 text-2xl font-extrabold text-[#0f172a] tracking-tight">
                {project.name}
              </h1>
              <p className="text-[12px] text-[#64748b] mt-1">
                {project.floor} · {project.block} · {project.area}
              </p>
            </div>
            <div className="text-right space-y-1">
              <div className="flex items-center gap-1.5 justify-end">
                <Building2 className="w-3.5 h-3.5 text-[#2563eb]" />
                <span className="text-[11px] font-bold text-[#0f172a]">
                  Report #BS-2025-04-{project.id.slice(-3).toUpperCase()}
                </span>
              </div>
              <p className="text-[10px] text-[#94a3b8]">
                Generated {generatedAt ?? "—"}
              </p>
              <p className="text-[10px] text-[#94a3b8]">
                Prepared by Ahmad Raza · Project Manager
              </p>
            </div>
          </header>

          {/* Site info */}
          <section className="px-10 py-6 grid grid-cols-2 sm:grid-cols-4 gap-4 border-b border-[#f1f5f9]">
            <ReportStat label="Total Area" value={project.area} />
            <ReportStat label="Scans" value={String(project.scansCount)} />
            <ReportStat label="Accuracy" value={project.accuracy ?? "±1.2 mm"} mono />
            <ReportStat label="Gaussians" value={project.gaussianCount ?? "—"} mono />
          </section>

          {/* Snapshot */}
          <section className="px-10 py-6 border-b border-[#f1f5f9]">
            <h2 className="text-[13px] font-bold text-[#0f172a] mb-3">
              3D Snapshot
            </h2>
            <div className="relative w-full h-64 rounded-lg bg-[#eef3f9] border border-[#e2e8f0] overflow-hidden">
              <Image
                src="/images/dashboard background.png"
                alt={`${project.name} snapshot`}
                fill
                className="object-contain object-center"
              />
            </div>
            <p className="text-[10px] text-[#94a3b8] mt-2 text-center italic">
              Fig. 1 · Textured 3DGS render — camera facing north-east, HVAC & plumbing layers on.
            </p>
          </section>

          {/* Summary */}
          <section className="px-10 py-6 border-b border-[#f1f5f9]">
            <h2 className="text-[13px] font-bold text-[#0f172a] mb-2">
              Executive Summary
            </h2>
            <p className="text-[12px] text-[#334155] leading-relaxed">
              This report captures the coordination status of {project.name} following the
              latest capture on {project.dateCaptured}. The scan achieved{" "}
              <span className="font-bold">{project.accuracy ?? "±1.2 mm"}</span> metric
              accuracy and yielded a Gaussian Splatting model of{" "}
              <span className="font-mono">{project.gaussianCount ?? "—"}</span> active
              splats. {flaggedIssues.filter((c) => c.flagged).length} elements were flagged
              for coordinator sign-off — see the register below. All flagged items should be
              reviewed against the current shop drawings before construction proceeds.
            </p>
          </section>

          {/* Flagged issues */}
          <section className="px-10 py-6">
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-[13px] font-bold text-[#0f172a]">
                Flagged Issues Register
              </h2>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-red-50 text-[#dc2626] border border-red-100">
                {flaggedIssues.filter((c) => c.flagged).length} flagged
              </span>
            </div>
            <table className="w-full text-left border-t border-[#e2e8f0]">
              <thead>
                <tr className="text-[10px] font-bold uppercase tracking-wider text-[#94a3b8]">
                  <th className="py-2 pr-3">#</th>
                  <th className="py-2 pr-3">Element</th>
                  <th className="py-2 pr-3">Layer</th>
                  <th className="py-2 pr-3">Change</th>
                  <th className="py-2 pr-3 text-right">Delta</th>
                  <th className="py-2 pl-3 text-right">Status</th>
                </tr>
              </thead>
              <tbody>
                {flaggedIssues.map((row, idx) => {
                  const style = CHANGE_STYLE[row.changeType];
                  const { Icon } = style;
                  return (
                    <tr
                      key={row.id}
                      className="border-t border-[#f1f5f9] text-[11px] text-[#334155]"
                    >
                      <td className="py-2.5 pr-3 font-mono font-bold text-[#94a3b8]">
                        {String(idx + 1).padStart(2, "0")}
                      </td>
                      <td className="py-2.5 pr-3 font-bold text-[#0f172a]">
                        {row.element}
                      </td>
                      <td className="py-2.5 pr-3">{row.layer}</td>
                      <td className="py-2.5 pr-3">
                        <span
                          className={`inline-flex items-center gap-1 px-1.5 py-0.5 rounded-md text-[10px] font-bold ${style.text} ${style.bg}`}
                        >
                          <Icon className="w-3 h-3" />
                          {style.label}
                        </span>
                      </td>
                      <td className="py-2.5 pr-3 text-right font-mono font-bold text-[#0f172a]">
                        {row.delta}
                      </td>
                      <td className="py-2.5 pl-3 text-right">
                        {row.flagged ? (
                          <span className="inline-flex items-center gap-1 text-[10px] font-bold text-[#dc2626]">
                            <Flag className="w-3 h-3" />
                            Flagged
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 text-[10px] font-bold text-[#059669]">
                            <CheckCircle2 className="w-3 h-3" />
                            Cleared
                          </span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </section>

          {/* Footer */}
          <footer className="px-10 py-4 border-t border-[#f1f5f9] flex items-center justify-between text-[10px] text-[#94a3b8]">
            <span>Page 1 of 1</span>
            <span>BuildScan 3D · Construction Spatial Intelligence Platform</span>
          </footer>
        </article>
      </div>
    </div>
  );
};

const ReportStat: React.FC<{ label: string; value: string; mono?: boolean }> = ({
  label,
  value,
  mono,
}) => (
  <div>
    <p className="text-[9px] font-bold uppercase tracking-wider text-[#94a3b8]">
      {label}
    </p>
    <p
      className={`text-[14px] font-extrabold text-[#0f172a] leading-tight ${
        mono ? "font-mono" : ""
      }`}
    >
      {value}
    </p>
  </div>
);
