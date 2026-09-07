"use client";

import React, { useState } from "react";
import {
  X,
  Download,
  FileSpreadsheet,
  Box,
  Layers,
  CheckCircle2,
  FileCode,
} from "lucide-react";

interface ExportModalProps {
  isOpen: boolean;
  onClose: () => void;
  projectName: string;
  measurementsCount: number;
}

export const ExportModal: React.FC<ExportModalProps> = ({
  isOpen,
  onClose,
  projectName,
  measurementsCount,
}) => {
  const [downloadedFormat, setDownloadedFormat] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleDownload = (format: string, filename: string) => {
    setDownloadedFormat(format);
    // Simulate instantaneous download
    setTimeout(() => {
      setDownloadedFormat(null);
    }, 2500);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div
        className="relative w-full max-w-md bg-slate-950 border border-slate-800 rounded-2xl shadow-2xl shadow-blue-500/10 overflow-hidden text-slate-100"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between px-5 py-4 border-b border-slate-800 bg-slate-900/60">
          <div className="flex items-center gap-2.5">
            <Download className="w-5 h-5 text-cyan-400" />
            <h3 className="text-sm font-bold text-white">
              Export Site Intelligence & BIM
            </h3>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="p-5 space-y-3">
          <p className="text-xs text-slate-400">
            Export metric dimensions, classified point cloud masks, and 3D geometry
            for <strong>{projectName}</strong>:
          </p>

          {/* Option 1: CSV Report */}
          <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 hover:border-slate-700 flex items-center justify-between gap-3">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-lg bg-emerald-500/10 text-emerald-400 flex items-center justify-center shrink-0">
                <FileSpreadsheet className="w-5 h-5" />
              </div>
              <div>
                <div className="text-xs font-bold text-white">
                  Metric Measurements Schedule (.csv)
                </div>
                <div className="text-[11px] text-slate-400">
                  {measurementsCount} Active Measurements + Tolerances
                </div>
              </div>
            </div>
            <button
              onClick={() =>
                handleDownload("csv", `${projectName}_measurements.csv`)
              }
              className="px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold"
            >
              {downloadedFormat === "csv" ? "Downloaded!" : "Export"}
            </button>
          </div>

          {/* Option 2: IFC / BIM Model */}
          <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 hover:border-slate-700 flex items-center justify-between gap-3">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-lg bg-blue-500/10 text-blue-400 flex items-center justify-center shrink-0">
                <Box className="w-5 h-5" />
              </div>
              <div>
                <div className="text-xs font-bold text-white">
                  BIM Geometry (.ifc / .obj)
                </div>
                <div className="text-[11px] text-slate-400">
                  Classified MEP Objects (Pipes, Ducts, Trays)
                </div>
              </div>
            </div>
            <button
              onClick={() => handleDownload("ifc", `${projectName}_bim.ifc`)}
              className="px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold"
            >
              {downloadedFormat === "ifc" ? "Downloaded!" : "Export"}
            </button>
          </div>

          {/* Option 3: WebGPU .ksplat */}
          <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 hover:border-slate-700 flex items-center justify-between gap-3">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-lg bg-purple-500/10 text-purple-400 flex items-center justify-center shrink-0">
                <Layers className="w-5 h-5" />
              </div>
              <div>
                <div className="text-xs font-bold text-white">
                  3D Gaussian Splat (.ksplat)
                </div>
                <div className="text-[11px] text-slate-400">
                  Compressed WebGPU Model (1.2M Gaussians)
                </div>
              </div>
            </div>
            <button
              onClick={() => handleDownload("ksplat", `${projectName}.ksplat`)}
              className="px-3 py-1.5 rounded-lg bg-purple-600 hover:bg-purple-500 text-white text-xs font-semibold"
            >
              {downloadedFormat === "ksplat" ? "Downloaded!" : "Export"}
            </button>
          </div>
        </div>

        <div className="px-5 py-3 border-t border-slate-800 bg-slate-900/60 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-white"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

