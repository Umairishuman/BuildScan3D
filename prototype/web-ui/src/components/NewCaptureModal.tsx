"use client";

import React, { useState } from "react";
import {
  X,
  Smartphone,
  UploadCloud,
  CheckCircle2,
  QrCode,
  Sparkles,
  ArrowRight,
  ShieldAlert,
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
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div
        className="relative w-full max-w-lg bg-slate-950 border border-slate-800 rounded-2xl shadow-2xl shadow-blue-500/10 overflow-hidden text-slate-100"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-900/60">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-blue-500/10 border border-blue-500/30 flex items-center justify-center text-blue-400">
              <Smartphone className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white">
                Initiate New Site Capture
              </h2>
              <p className="text-xs text-slate-400">
                Sync Mobile AR Telemetry or Direct Upload
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-4">
          <div className="flex rounded-lg bg-slate-900 p-1 border border-slate-800">
            <button
              onClick={() => {
                setActiveTab("mobile_qr");
                setUploadComplete(false);
              }}
              className={`flex-1 py-1.5 text-xs font-semibold rounded-md transition-colors ${
                activeTab === "mobile_qr"
                  ? "bg-blue-600 text-white shadow"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              Scan with Mobile App
            </button>
            <button
              onClick={() => {
                setActiveTab("direct_upload");
                setUploadComplete(false);
              }}
              className={`flex-1 py-1.5 text-xs font-semibold rounded-md transition-colors ${
                activeTab === "direct_upload"
                  ? "bg-blue-600 text-white shadow"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              Direct Dataset Upload (.tar.gz)
            </button>
          </div>

          {activeTab === "mobile_qr" ? (
            <div className="flex flex-col items-center text-center p-4 rounded-xl bg-slate-900/50 border border-slate-800 space-y-3">
              <div className="p-4 bg-white rounded-xl shadow-inner">
                {/* Visual QR Placeholder */}
                <div className="w-32 h-32 border-4 border-slate-900 p-1 flex items-center justify-center">
                  <QrCode className="w-28 h-28 text-slate-900" />
                </div>
              </div>
              <p className="text-xs font-mono text-cyan-400">
                PAIR CODE: #BST-8842-NUCES
              </p>
              <p className="text-xs text-slate-400 max-w-xs">
                Open the <strong>BuildScan Mobile App</strong> on an ARCore/ARKit
                supported phone and scan this code to link telemetry directly to
                this project.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="border-2 border-dashed border-slate-800 hover:border-blue-500/50 rounded-xl p-6 text-center space-y-2 transition-colors">
                <UploadCloud className="w-8 h-8 text-blue-400 mx-auto animate-bounce" />
                <div className="text-xs text-slate-200 font-semibold">
                  Drag & drop raw scan bundle
                </div>
                <p className="text-[11px] text-slate-400">
                  Accepts <code className="text-cyan-400">video.mp4</code>,{" "}
                  <code className="text-cyan-400">poses.csv</code>, and{" "}
                  <code className="text-cyan-400">points.csv</code>
                </p>
              </div>

              {!uploadComplete ? (
                <button
                  onClick={handleSimulateUpload}
                  disabled={isSimulatingUpload}
                  className="w-full py-2.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold transition-colors flex items-center justify-center gap-2"
                >
                  {isSimulatingUpload ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                      <span>Packaging & Dispatching to RunPod...</span>
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-4 h-4" />
                      <span>Simulate Dispatch to GPU Worker</span>
                    </>
                  )}
                </button>
              ) : (
                <div className="p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 shrink-0" />
                  <span>
                    Dispatched job to RTX 4090 cloud queue! View in Active Jobs.
                  </span>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-3 border-t border-slate-800 bg-slate-900/60 flex justify-end">
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
