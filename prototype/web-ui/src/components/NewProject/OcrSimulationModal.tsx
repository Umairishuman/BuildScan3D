"use client";

import React, { useEffect, useState } from "react";
import { CheckCircle2, Loader2, X } from "lucide-react";

interface OcrSimulationModalProps {
  fileName: string;
  onComplete: () => void;
  onCancel: () => void;
}

interface LogLine {
  icon: "check" | "spinner";
  text: string;
  tone: "success" | "progress";
}

/** Cadence for the three-step simulation. Numbers chosen so the whole thing
 *  reads in ~4 seconds without feeling instant. */
const STEPS: { delayMs: number; line: LogLine }[] = [
  {
    delayMs: 400,
    line: { icon: "check", text: "Ingested: Site_Plans.pdf", tone: "success" },
  },
  {
    delayMs: 1500,
    line: {
      icon: "spinner",
      text: "Rasterizing vector sheets & running OCR on Title Blocks...",
      tone: "progress",
    },
  },
  {
    delayMs: 2600,
    line: {
      icon: "check",
      text: "Extraction complete: Level 01 & Level 02 ready for field mapping.",
      tone: "success",
    },
  },
];

/** Everything ready → hand off to the parent after a short beat. */
const COMPLETE_HAND_OFF_MS = 800;

export const OcrSimulationModal: React.FC<OcrSimulationModalProps> = ({
  fileName,
  onComplete,
  onCancel,
}) => {
  const [lines, setLines] = useState<LogLine[]>([]);
  const [isDone, setIsDone] = useState(false);

  useEffect(() => {
    const timers: number[] = [];
    STEPS.forEach((step) => {
      timers.push(
        window.setTimeout(() => {
          setLines((prev) => [...prev, step.line]);
        }, step.delayMs)
      );
    });
    timers.push(
      window.setTimeout(() => {
        setIsDone(true);
      }, STEPS[STEPS.length - 1].delayMs + 200)
    );
    timers.push(
      window.setTimeout(
        onComplete,
        STEPS[STEPS.length - 1].delayMs + COMPLETE_HAND_OFF_MS
      )
    );

    return () => {
      timers.forEach((t) => window.clearTimeout(t));
    };
    // Only re-run when the parent hands us a new file to process.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [fileName]);

  // Convert the last log line's spinner to a check once its follow-up log
  // arrives, so the "in progress" indicator resolves as steps complete.
  const renderedLines = lines.map((line, idx) => {
    const isCurrent = idx === lines.length - 1 && !isDone;
    const displayIcon = isCurrent ? line.icon : "check";
    const displayTone = isCurrent ? line.tone : "success";
    return { ...line, icon: displayIcon, tone: displayTone };
  });

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
      <div
        role="dialog"
        aria-label="Plan extraction in progress"
        className="w-full max-w-xl bg-white border border-[#e2e8f0] rounded-2xl shadow-2xl overflow-hidden text-[#0f172a]"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-3 border-b border-[#e2e8f0] bg-[#f8fafc]">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-slate-900 flex items-center justify-center">
              <span className="text-[10px] font-mono font-bold text-emerald-400">
                {">_"}
              </span>
            </div>
            <div>
              <h2 className="text-sm font-bold text-[#0f172a]">
                Extracting spatial grids
              </h2>
              <p className="text-[10px] text-[#64748b] font-mono truncate max-w-xs">
                {fileName}
              </p>
            </div>
          </div>
          <button
            onClick={onCancel}
            className="p-1 rounded-md text-[#94a3b8] hover:text-[#0f172a] hover:bg-slate-100 cursor-pointer"
            aria-label="Cancel"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Terminal body */}
        <div className="p-4 bg-[#0f172a] font-mono text-[12px] min-h-[220px] max-h-[280px] overflow-y-auto">
          <div className="text-[#38bdf8] mb-2">
            $ buildscan-plan-ingest --file &quot;{fileName}&quot;
          </div>
          <ul className="space-y-1.5">
            {renderedLines.map((line, idx) => (
              <li key={idx} className="flex items-start gap-2">
                <span className="w-4 shrink-0 mt-0.5">
                  {line.icon === "check" ? (
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                  ) : (
                    <Loader2 className="w-3.5 h-3.5 text-amber-400 animate-spin" />
                  )}
                </span>
                <span
                  className={`${
                    line.tone === "success"
                      ? "text-emerald-300"
                      : "text-amber-300"
                  } leading-relaxed`}
                >
                  [{line.icon === "check" ? "✔" : "⏳"}] {line.text}
                </span>
              </li>
            ))}
            {lines.length < STEPS.length && (
              <li className="flex items-center gap-2 text-[#64748b] pl-6">
                <span className="w-1.5 h-3 bg-emerald-400 animate-pulse" />
              </li>
            )}
          </ul>
          {isDone && (
            <div className="mt-4 pt-3 border-t border-slate-700 text-emerald-400 text-[11px]">
              Handing off to the Floor Plan Viewer…
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
