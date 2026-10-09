"use client";

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
