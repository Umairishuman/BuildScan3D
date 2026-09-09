"use client";

import React, { useState } from "react";
import {
  Box,
  Download,
  File as FileIcon,
  FileImage,
  FileJson,
  FileSpreadsheet,
  FileText,
  Files as FilesIcon,
  Sparkles,
  Trash2,
  UploadCloud,
} from "lucide-react";
import {
  MOCK_PROJECT_FILES,
  ProjectFile,
  ProjectFileKind,
} from "@/lib/mockData";

const KIND_STYLES: Record<
  ProjectFileKind,
  { Icon: React.ComponentType<{ className?: string }>; bg: string; fg: string; label: string }
> = {
  ply: { Icon: Sparkles, bg: "bg-blue-50", fg: "text-[#2563eb]", label: "PLY" },
  ksplat: { Icon: Sparkles, bg: "bg-indigo-50", fg: "text-[#4f46e5]", label: "KSPLAT" },
  obj: { Icon: Box, bg: "bg-emerald-50", fg: "text-[#059669]", label: "OBJ" },
  pdf: { Icon: FileText, bg: "bg-red-50", fg: "text-[#dc2626]", label: "PDF" },
  csv: { Icon: FileSpreadsheet, bg: "bg-teal-50", fg: "text-[#0f766e]", label: "CSV" },
  png: { Icon: FileImage, bg: "bg-amber-50", fg: "text-[#d97706]", label: "PNG" },
  json: { Icon: FileJson, bg: "bg-slate-100", fg: "text-[#475569]", label: "JSON" },
};

export const FilesTab: React.FC = () => {
  const [files, setFiles] = useState<ProjectFile[]>(() =>
    MOCK_PROJECT_FILES.map((f) => ({ ...f }))
  );
  const [isDragOver, setIsDragOver] = useState(false);

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setIsDragOver(false);
    const list = Array.from(event.dataTransfer.files);
    if (list.length === 0) return;
    const additions: ProjectFile[] = list.map((f, idx) => ({
      id: `local-${Date.now()}-${idx}`,
      name: f.name,
      kind: inferKind(f.name),
      sizeLabel: formatBytes(f.size),
      uploadedAt: "Just now",
      author: "You (local drop)",
    }));
    setFiles((prev) => [...additions, ...prev]);
  };

  const handleDelete = (id: string) =>
    setFiles((prev) => prev.filter((f) => f.id !== id));

  return (
    <div className="flex-1 min-h-0 overflow-y-auto p-5 space-y-4 bg-[#eef3f9]">
      {/* Upload dropzone */}
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragOver(true);
        }}
        onDragLeave={() => setIsDragOver(false)}
        onDrop={handleDrop}
        className={`rounded-2xl border-2 border-dashed p-8 flex flex-col items-center justify-center gap-2 text-center transition-colors ${
          isDragOver
            ? "border-[#2563eb] bg-blue-50/60"
            : "border-[#cbd5e1] bg-white hover:border-[#94a3b8]"
        }`}
      >
        <span
          className={`w-11 h-11 rounded-2xl flex items-center justify-center ${
            isDragOver ? "bg-[#2563eb] text-white" : "bg-blue-50 text-[#2563eb]"
          }`}
        >
          <UploadCloud className="w-5 h-5" />
        </span>
        <div>
          <p className="text-sm font-bold text-[#0f172a]">
            Drag files here or click to upload
          </p>
          <p className="text-[11px] text-[#64748b] mt-0.5">
            PLY · KSPLAT · OBJ · PDF · CSV · PNG · JSON, up to 500 MB per file.
          </p>
        </div>
        <button
          type="button"
          className="mt-1 inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-[#2563eb] hover:bg-[#1d4ed8] text-white text-[11px] font-bold shadow-sm cursor-pointer"
        >
          <UploadCloud className="w-3.5 h-3.5" />
          Browse files
        </button>
      </div>

      {/* File list */}
      <section className="rounded-2xl bg-white border border-[#e2e8f0] shadow-sm">
        <div className="px-4 py-3 flex items-center justify-between border-b border-[#f1f5f9]">
          <div className="flex items-center gap-2">
            <FilesIcon className="w-4 h-4 text-[#2563eb]" />
            <h3 className="text-sm font-bold text-[#0f172a]">Files</h3>
            <span className="text-[10px] font-mono font-bold text-[#64748b]">
              {files.length}
            </span>
          </div>
          <span className="text-[10px] text-[#94a3b8]">
            Sorted by upload date · newest first
          </span>
        </div>

        {files.length === 0 ? (
          <div className="py-10 flex flex-col items-center gap-2">
            <FileIcon className="w-6 h-6 text-[#cbd5e1]" />
            <p className="text-[11px] text-[#94a3b8]">
              No files uploaded for this scan yet.
            </p>
          </div>
        ) : (
          <ul className="divide-y divide-[#f1f5f9]">
            {files.map((file) => (
              <FileRow
                key={file.id}
                file={file}
                onDelete={() => handleDelete(file.id)}
              />
            ))}
          </ul>
        )}
      </section>
    </div>
  );
};

const FileRow: React.FC<{ file: ProjectFile; onDelete: () => void }> = ({
  file,
  onDelete,
}) => {
  const style = KIND_STYLES[file.kind];
  const { Icon } = style;
  return (
    <li className="group px-4 py-2.5 flex items-center gap-3 hover:bg-slate-50 transition-colors">
      <span
        className={`w-9 h-9 rounded-xl flex items-center justify-center shrink-0 ${style.bg} ${style.fg}`}
      >
        <Icon className="w-4 h-4" />
      </span>
      <div className="flex-1 min-w-0">
        <div className="flex items-baseline gap-2">
          <span className="text-[13px] font-bold text-[#0f172a] truncate font-mono">
            {file.name}
          </span>
          <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-slate-100 text-[#475569] shrink-0">
            {style.label}
          </span>
        </div>
        <p className="text-[10px] text-[#64748b] mt-0.5">
          {file.author} · Uploaded {file.uploadedAt}
        </p>
      </div>
      <span className="text-[11px] font-mono font-bold text-[#64748b] shrink-0 mr-1 tabular-nums">
        {file.sizeLabel}
      </span>
      <div className="flex items-center gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity">
        <button
          type="button"
          aria-label={`Download ${file.name}`}
          className="p-1.5 rounded-lg text-[#64748b] hover:text-[#2563eb] hover:bg-blue-50 cursor-pointer"
        >
          <Download className="w-3.5 h-3.5" />
        </button>
        <button
          type="button"
          onClick={onDelete}
          aria-label={`Delete ${file.name}`}
          className="p-1.5 rounded-lg text-[#64748b] hover:text-[#dc2626] hover:bg-red-50 cursor-pointer"
        >
          <Trash2 className="w-3.5 h-3.5" />
        </button>
      </div>
    </li>
  );
};

const inferKind = (name: string): ProjectFileKind => {
  const ext = name.split(".").pop()?.toLowerCase() ?? "";
  if (ext === "ply") return "ply";
  if (ext === "ksplat") return "ksplat";
  if (ext === "obj") return "obj";
  if (ext === "pdf") return "pdf";
  if (ext === "csv") return "csv";
  if (ext === "png" || ext === "jpg" || ext === "jpeg" || ext === "webp") return "png";
  if (ext === "json") return "json";
  return "json";
};

const formatBytes = (bytes: number): string => {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  return `${(bytes / (1024 * 1024 * 1024)).toFixed(2)} GB`;
};
