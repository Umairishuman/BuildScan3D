"use client";

import React, { useState } from "react";
import {
  X,
  Download,
  FileSpreadsheet,
  Box,
  Layers,
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
    setTimeout(() => {
      setDownloadedFormat(null);
    }, 2500);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm animate-in fade-in duration-200">
      <div
        className="relative w-full max-w-md bg-white border border-[#e2e8f0] rounded-2xl shadow-2xl overflow-hidden text-[#0f172a]"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between px-5 py-4 border-b border-[#e2e8f0] bg-[#f8fafc]">
          <div className="flex items-center gap-2.5">
            <Download className="w-5 h-5 text-[#2563eb]" />
            <h3 className="text-sm font-bold text-[#0f172a]">
              Export Site Intelligence & BIM
            </h3>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-[#64748b] hover:text-[#0f172a] hover:bg-slate-100"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="p-5 space-y-3 bg-white">
          <p className="text-xs text-[#64748b]">
            Export metric dimensions, classified point cloud masks, and 3D geometry
            for <strong>{projectName}</strong>:
          </p>

          {/* Option 1: CSV Report */}
          <div className="p-3 rounded-xl bg-[#f8fafc] border border-[#e2e8f0] hover:border-[#cbd5e1] flex items-center justify-between gap-3 transition-colors">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center shrink-0 border border-emerald-200">
                <FileSpreadsheet className="w-5 h-5" />
              </div>
              <div>
                <div className="text-xs font-bold text-[#0f172a]">
                  Metric Measurements Schedule (.csv)
                </div>
                <div className="text-[11px] text-[#64748b]">
                  {measurementsCount} Active Measurements + Tolerances
                </div>
              </div>
            </div>
            <button
              onClick={() =>
                handleDownload("csv", `${projectName}_measurements.csv`)
              }
              className="px-3 py-1.5 rounded-xl bg-[#2563eb] hover:bg-[#1d4ed8] text-white text-xs font-bold shadow-sm"
            >
              {downloadedFormat === "csv" ? "Downloaded!" : "Export"}
            </button>
          </div>

          {/* Option 2: IFC / BIM Model */}
          <div className="p-3 rounded-xl bg-[#f8fafc] border border-[#e2e8f0] hover:border-[#cbd5e1] flex items-center justify-between gap-3 transition-colors">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-blue-50 text-[#2563eb] flex items-center justify-center shrink-0 border border-blue-200">
                <Box className="w-5 h-5" />
              </div>
              <div>
                <div className="text-xs font-bold text-[#0f172a]">
                  BIM Geometry (.ifc / .obj)
                </div>
                <div className="text-[11px] text-[#64748b]">
                  Classified MEP Objects (Pipes, Ducts, Trays)
                </div>
              </div>
            </div>
            <button
              onClick={() => handleDownload("ifc", `${projectName}_bim.ifc`)}
              className="px-3 py-1.5 rounded-xl bg-[#2563eb] hover:bg-[#1d4ed8] text-white text-xs font-bold shadow-sm"
            >
              {downloadedFormat === "ifc" ? "Downloaded!" : "Export"}
            </button>
          </div>

          {/* Option 3: WebGPU .ksplat */}
          <div className="p-3 rounded-xl bg-[#f8fafc] border border-[#e2e8f0] hover:border-[#cbd5e1] flex items-center justify-between gap-3 transition-colors">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center shrink-0 border border-purple-200">
                <Layers className="w-5 h-5" />
              </div>
              <div>
                <div className="text-xs font-bold text-[#0f172a]">
                  3D Gaussian Splat (.ksplat)
                </div>
                <div className="text-[11px] text-[#64748b]">
                  Compressed WebGPU Model (1.2M Gaussians)
                </div>
              </div>
            </div>
            <button
              onClick={() => handleDownload("ksplat", `${projectName}.ksplat`)}
              className="px-3 py-1.5 rounded-xl bg-[#2563eb] hover:bg-[#1d4ed8] text-white text-xs font-bold shadow-sm"
            >
              {downloadedFormat === "ksplat" ? "Downloaded!" : "Export"}
            </button>
          </div>
        </div>

        <div className="px-5 py-3 border-t border-[#e2e8f0] bg-[#f8fafc] flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-xs font-semibold text-[#0f172a]"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
