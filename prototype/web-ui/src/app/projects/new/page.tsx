"use client";

import React, { useRef, useState } from "react";
import Link from "next/link";
import {
  AlertTriangle,
  ArrowLeft,
  Layers,
  ShieldCheck,
  UploadCloud,
} from "lucide-react";
import { AppShell } from "@/components/AppShell";
import { OcrSimulationModal } from "@/components/NewProject/OcrSimulationModal";
import { ReadyForCaptureViewport } from "@/components/NewProject/ReadyForCaptureViewport";

type Phase = "empty" | "ingesting" | "ready";

const ACCEPT = ".pdf,.dwg,application/pdf,image/vnd.dwg,image/x-dwg,image/*";

export default function NewProjectPage() {
  const [phase, setPhase] = useState<Phase>("empty");
  const [fileName, setFileName] = useState<string>("Site_Plans.pdf");
  const [projectName, setProjectName] = useState<string>("New Site — Level 01");
  const [dragOver, setDragOver] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const beginIngest = (file: File | null) => {
    if (!file) return;
    // Theatrical — the demo doesn't parse the file, it just plays the OCR
    // sequence back with whatever filename the user picked. Any file type
    // works, but nudge on obviously wrong ones.
    if (file.size > 50 * 1024 * 1024) {
      setError("File is larger than 50 MB — smaller demos please.");
      return;
    }
    setError(null);
    setFileName(file.name || "Site_Plans.pdf");
    setPhase("ingesting");
  };

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setDragOver(false);
    beginIngest(event.dataTransfer.files?.[0] ?? null);
  };

  if (phase === "ready") {
    return (
      <AppShell
        variant="fluid"
        activeNav="projects"
        breadcrumbs={[
          { label: "All Projects", href: "/projects" },
          { label: projectName },
        ]}
      >
        <ReadyForCaptureViewport projectName={projectName} />
      </AppShell>
    );
  }

  return (
    <AppShell
      activeNav="projects"
      breadcrumbs={[
        { label: "All Projects", href: "/projects" },
        { label: "New Project" },
      ]}
    >
      <div className="max-w-3xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-extrabold text-[#0f172a] tracking-tight">
              Create New Project
            </h1>
            <p className="text-xs text-[#64748b] mt-0.5">
              Upload the architectural plans to initialize spatial tracking.
              This is a strict prerequisite — the mobile app can&apos;t attach
              3D scans until a plan exists to map them onto.
            </p>
          </div>
          <Link
            href="/projects"
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-[#e2e8f0] bg-white text-xs font-bold text-[#0f172a] hover:bg-slate-50 shadow-sm cursor-pointer"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            Cancel
          </Link>
        </div>

        {/* Prerequisite callout */}
        <div className="flex items-start gap-2.5 p-3 rounded-xl bg-amber-50 border border-amber-200 text-[11px]">
          <ShieldCheck className="w-4 h-4 text-[#d97706] shrink-0 mt-0.5" />
          <div className="text-[#92400e] leading-snug">
            <span className="font-bold">Step 1 of 2 · Setup:</span> the system
            can&apos;t accept 3D scans until a map exists to attach them to.
            Upload the 2D blueprints first, then the field team can capture
            rooms against them from the BuildScan mobile app.
          </div>
        </div>

        {/* Project name */}
        <div className="space-y-1.5">
          <label className="text-[11px] font-bold text-[#0f172a] uppercase tracking-wider">
            Project name
          </label>
          <input
            type="text"
            value={projectName}
            onChange={(e) => setProjectName(e.target.value)}
            placeholder="e.g. Riverside Tower — Level 01"
            className="w-full px-3.5 py-2 rounded-xl border border-[#e2e8f0] bg-white text-sm text-[#0f172a] placeholder-[#94a3b8] focus:outline-none focus:border-[#2563eb] focus:ring-2 focus:ring-blue-100 transition-all"
          />
        </div>

        {/* Dropzone */}
        <div
          onDragOver={(e) => {
            e.preventDefault();
            setDragOver(true);
          }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`p-10 rounded-2xl border-2 border-dashed cursor-pointer transition-all flex flex-col items-center justify-center gap-3 text-center ${
            dragOver
              ? "border-[#2563eb] bg-blue-50/60"
              : "border-[#cbd5e1] bg-white hover:border-[#94a3b8] hover:bg-slate-50/60"
          }`}
        >
          <div
            className={`w-14 h-14 rounded-2xl flex items-center justify-center ${
              dragOver ? "bg-[#2563eb] text-white" : "bg-blue-50 text-[#2563eb]"
            }`}
          >
            <UploadCloud className="w-7 h-7" />
          </div>

          <div className="space-y-1">
            <p className="text-sm font-extrabold text-[#0f172a]">
              Upload Architectural Plans
            </p>
            <p className="text-[12px] text-[#64748b] font-mono">
              .pdf, .dwg — to initialize spatial tracking grids.
            </p>
          </div>

          <div className="flex items-center gap-1.5 text-[10px] text-[#94a3b8]">
            <span>Drag &amp; drop here</span>
            <span>·</span>
            <span>or click to browse</span>
          </div>

          <input
            ref={fileInputRef}
            type="file"
            accept={ACCEPT}
            onChange={(e) => {
              beginIngest(e.target.files?.[0] ?? null);
              if (fileInputRef.current) fileInputRef.current.value = "";
            }}
            className="hidden"
          />
        </div>

        {error && (
          <p className="flex items-center gap-1.5 text-[11px] font-bold text-[#dc2626]">
            <AlertTriangle className="w-3.5 h-3.5" />
            {error}
          </p>
        )}

        {/* What happens next preview */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2">
          <NextStep
            index={1}
            title="OCR Extraction"
            body="Rasterize the PDF & pull title blocks from the vector sheets."
          />
          <NextStep
            index={2}
            title="Field Mapping"
            body="Blueprint appears in the mobile app for the on-site team."
          />
          <NextStep
            index={3}
            title="3D Reconstruction"
            body="Nodes light up on the plan as scans finish training."
          />
        </div>
      </div>

      {phase === "ingesting" && (
        <OcrSimulationModal
          fileName={fileName}
          onComplete={() => setPhase("ready")}
          onCancel={() => setPhase("empty")}
        />
      )}
    </AppShell>
  );
}

/* ------------------------------------------------------------------ */
/* NextStep card                                                       */
/* ------------------------------------------------------------------ */

const NextStep: React.FC<{ index: number; title: string; body: string }> = ({
  index,
  title,
  body,
}) => (
  <div className="p-3 rounded-xl border border-[#e2e8f0] bg-white space-y-1.5">
    <div className="flex items-center gap-2">
      <span className="w-5 h-5 rounded-full bg-blue-50 text-[#2563eb] text-[10px] font-mono font-bold flex items-center justify-center">
        {index}
      </span>
      <span className="text-[11px] font-bold text-[#0f172a] flex items-center gap-1">
        <Layers className="w-3 h-3 text-[#94a3b8]" />
        {title}
      </span>
    </div>
    <p className="text-[10px] text-[#64748b] leading-snug">{body}</p>
  </div>
);
