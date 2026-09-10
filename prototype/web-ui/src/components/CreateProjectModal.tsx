"use client";

import React, { useCallback, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import {
  AlertTriangle,
  CheckCircle2,
  FileImage,
  Info,
  Loader2,
  Plus,
  Trash2,
  UploadCloud,
  X,
} from "lucide-react";
import {
  BuildingFloor,
  BuildingPlan,
  FloorPlanRoom,
} from "@/lib/mockData";
import { newUserPlanId, saveUserPlan } from "@/lib/userPlans";

interface CreateProjectModalProps {
  isOpen: boolean;
  onClose: () => void;
}

/** In-memory state for a floor being edited before save. */
interface DraftFloor {
  id: string;
  label: string;
  discipline: string;
  totalArea: string;
  fileName?: string;
  planImageDataUrl?: string;
  planImageWidth?: number;
  planImageHeight?: number;
  error?: string;
}

const ACCEPT = "image/png,image/jpeg,image/svg+xml";
const MAX_BYTES = 5 * 1024 * 1024;

const newDraftId = () =>
  `floor-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 6)}`;

const emptyFloor = (index: number): DraftFloor => ({
  id: newDraftId(),
  label: `Floor ${index + 1}`,
  discipline: "General",
  totalArea: "",
});

export const CreateProjectModal: React.FC<CreateProjectModalProps> = ({
  isOpen,
  onClose,
}) => {
  const router = useRouter();
  const [buildingName, setBuildingName] = useState("");
  const [floors, setFloors] = useState<DraftFloor[]>(() => [emptyFloor(0)]);
  const [globalError, setGlobalError] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);

  const reset = useCallback(() => {
    setBuildingName("");
    setFloors([emptyFloor(0)]);
    setGlobalError(null);
    setIsSaving(false);
  }, []);

  const handleClose = () => {
    if (isSaving) return;
    reset();
    onClose();
  };

  const patchFloor = (id: string, patch: Partial<DraftFloor>) =>
    setFloors((prev) => prev.map((f) => (f.id === id ? { ...f, ...patch } : f)));

  const addFloor = () =>
    setFloors((prev) => [...prev, emptyFloor(prev.length)]);

  const removeFloor = (id: string) =>
    setFloors((prev) =>
      prev.length === 1 ? prev : prev.filter((f) => f.id !== id)
    );

  const handleFilePicked = async (id: string, file: File | null) => {
    if (!file) return;
    if (!file.type.match(/^image\/(png|jpeg|svg\+xml)$/)) {
      patchFloor(id, {
        error: "Unsupported file type — PNG, JPG, or SVG only.",
      });
      return;
    }
    if (file.size > MAX_BYTES) {
      patchFloor(id, {
        error: `File is ${(file.size / 1024 / 1024).toFixed(1)} MB — max 5 MB.`,
      });
      return;
    }
    try {
      const { dataUrl, width, height } = await readImage(file);
      patchFloor(id, {
        fileName: file.name,
        planImageDataUrl: dataUrl,
        planImageWidth: width,
        planImageHeight: height,
        error: undefined,
      });
    } catch (err) {
      patchFloor(id, {
        error: err instanceof Error ? err.message : "Could not read the image.",
      });
    }
  };

  const handleSave = () => {
    setGlobalError(null);

    const trimmedBuilding = buildingName.trim();
    if (!trimmedBuilding) {
      setGlobalError("Building name is required.");
      return;
    }
    if (floors.some((f) => !f.label.trim())) {
      setGlobalError("Every floor needs a label.");
      return;
    }
    if (floors.some((f) => !f.planImageDataUrl)) {
      setGlobalError("Every floor needs a plan image uploaded.");
      return;
    }

    setIsSaving(true);

    const projectId = newUserPlanId();
    const plan: BuildingPlan = {
      projectId,
      buildingName: trimmedBuilding,
      isUserCreated: true,
      createdAt: new Date().toISOString(),
      floors: floors.map((f) => draftToFloor(f)),
    };

    const ok = saveUserPlan(plan);
    if (!ok) {
      setIsSaving(false);
      setGlobalError(
        "Could not save — browser storage is full. Delete an existing user-uploaded plan and try again."
      );
      return;
    }

    reset();
    onClose();
    router.push(`/floorplan/${projectId}`);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm">
      <div
        role="dialog"
        aria-label="Create project from floor plan"
        className="relative w-full max-w-2xl max-h-[92vh] bg-white border border-[#e2e8f0] rounded-2xl shadow-2xl overflow-hidden text-[#0f172a] flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="shrink-0 flex items-center justify-between px-6 py-4 border-b border-[#e2e8f0] bg-[#f8fafc]">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-blue-50 border border-blue-200 flex items-center justify-center text-[#2563eb]">
              <UploadCloud className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-[#0f172a]">
                Create Project from Floor Plan
              </h2>
              <p className="text-xs text-[#64748b]">
                Upload a blueprint or CAD export as the base layer
              </p>
            </div>
          </div>
          <button
            onClick={handleClose}
            disabled={isSaving}
            className="p-1.5 rounded-lg text-[#64748b] hover:text-[#0f172a] hover:bg-slate-100 disabled:opacity-40 disabled:cursor-not-allowed"
            aria-label="Close"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Scrollable body */}
        <div className="flex-1 min-h-0 overflow-y-auto p-6 space-y-5">
          {/* Storage disclaimer */}
          <div className="p-3 rounded-xl bg-amber-50 border border-amber-200 flex items-start gap-2.5 text-[11px]">
            <Info className="w-4 h-4 text-[#d97706] shrink-0 mt-0.5" />
            <div className="text-[#92400e] leading-snug">
              <span className="font-bold">POC storage:</span> uploads live in
              this browser&apos;s local storage only, capped at 5 MB per plan
              image and PNG / JPG / SVG. They won&apos;t sync to other devices.
            </div>
          </div>

          {/* Building name */}
          <div className="space-y-1.5">
            <label className="text-[11px] font-bold text-[#0f172a] uppercase tracking-wider">
              Building name
            </label>
            <input
              type="text"
              value={buildingName}
              onChange={(e) => setBuildingName(e.target.value)}
              placeholder="e.g. Riverside Tower, Sector 9 MEP Wing"
              className="w-full px-3.5 py-2 rounded-xl border border-[#e2e8f0] bg-white text-sm text-[#0f172a] placeholder-[#94a3b8] focus:outline-none focus:border-[#2563eb] focus:ring-2 focus:ring-blue-100 transition-all"
            />
          </div>

          {/* Floors */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <label className="text-[11px] font-bold text-[#0f172a] uppercase tracking-wider">
                Floors ({floors.length})
              </label>
              <button
                type="button"
                onClick={addFloor}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-[#e2e8f0] bg-white text-[11px] font-bold text-[#2563eb] hover:bg-blue-50 hover:border-blue-200 cursor-pointer transition-colors"
              >
                <Plus className="w-3.5 h-3.5" />
                Add floor
              </button>
            </div>

            {floors.map((floor, index) => (
              <FloorEditor
                key={floor.id}
                floor={floor}
                index={index}
                canRemove={floors.length > 1}
                onChange={(patch) => patchFloor(floor.id, patch)}
                onRemove={() => removeFloor(floor.id)}
                onFilePicked={(file) => handleFilePicked(floor.id, file)}
              />
            ))}
          </div>
        </div>

        {/* Footer */}
        <div className="shrink-0 px-6 py-3 border-t border-[#e2e8f0] bg-[#f8fafc] flex items-center justify-between gap-3">
          {globalError ? (
            <div className="flex items-center gap-1.5 text-[11px] text-[#dc2626] font-bold">
              <AlertTriangle className="w-3.5 h-3.5 shrink-0" />
              <span>{globalError}</span>
            </div>
          ) : (
            <span className="text-[10px] text-[#94a3b8]">
              You&apos;ll be able to place clickable room nodes on the plan
              after saving.
            </span>
          )}

          <div className="flex items-center gap-2">
            <button
              onClick={handleClose}
              disabled={isSaving}
              className="px-3.5 py-1.5 rounded-xl bg-white border border-[#e2e8f0] text-xs font-bold text-[#0f172a] hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              disabled={isSaving}
              className="inline-flex items-center gap-1.5 px-4 py-1.5 rounded-xl bg-[#2563eb] hover:bg-[#1d4ed8] disabled:bg-[#94a3b8] disabled:cursor-wait text-white text-xs font-bold shadow-sm cursor-pointer"
            >
              {isSaving ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  Saving…
                </>
              ) : (
                <>
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  Create project
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

/* --------------------------- FloorEditor row --------------------------- */

interface FloorEditorProps {
  floor: DraftFloor;
  index: number;
  canRemove: boolean;
  onChange: (patch: Partial<DraftFloor>) => void;
  onRemove: () => void;
  onFilePicked: (file: File | null) => void;
}

const FloorEditor: React.FC<FloorEditorProps> = ({
  floor,
  index,
  canRemove,
  onChange,
  onRemove,
  onFilePicked,
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);

  return (
    <div className="p-4 rounded-2xl border border-[#e2e8f0] bg-white space-y-3">
      <div className="flex items-center justify-between">
        <span className="text-[10px] font-bold uppercase tracking-wider text-[#94a3b8]">
          Floor {index + 1}
        </span>
        {canRemove && (
          <button
            type="button"
            onClick={onRemove}
            className="p-1 rounded-md text-[#94a3b8] hover:text-[#dc2626] hover:bg-red-50 cursor-pointer transition-colors"
            aria-label={`Remove floor ${index + 1}`}
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
        <TextField
          label="Label"
          value={floor.label}
          onChange={(v) => onChange({ label: v })}
          placeholder="Floor 5"
        />
        <TextField
          label="Discipline"
          value={floor.discipline}
          onChange={(v) => onChange({ discipline: v })}
          placeholder="Mechanical"
        />
        <TextField
          label="Total area"
          value={floor.totalArea}
          onChange={(v) => onChange({ totalArea: v })}
          placeholder="1,240 m²"
        />
      </div>

      <div className="space-y-1.5">
        <label className="text-[10px] font-bold uppercase tracking-wider text-[#94a3b8]">
          Plan image
        </label>

        {floor.planImageDataUrl ? (
          <div className="flex items-center gap-3 p-2.5 rounded-xl bg-slate-50 border border-[#e2e8f0]">
            <div className="relative w-16 h-12 rounded-lg overflow-hidden bg-white border border-[#e2e8f0] shrink-0">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={floor.planImageDataUrl}
                alt={`${floor.label} preview`}
                className="w-full h-full object-contain"
              />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-[12px] font-bold text-[#0f172a] truncate font-mono">
                {floor.fileName ?? "plan image"}
              </p>
              <p className="text-[10px] text-[#64748b]">
                {floor.planImageWidth} × {floor.planImageHeight} px
              </p>
            </div>
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              className="px-2.5 py-1 rounded-lg text-[10px] font-bold text-[#2563eb] hover:bg-blue-50 cursor-pointer"
            >
              Replace
            </button>
          </div>
        ) : (
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            className="w-full flex items-center justify-center gap-2 p-4 rounded-xl border-2 border-dashed border-[#cbd5e1] hover:border-[#2563eb] hover:bg-blue-50/40 cursor-pointer transition-colors text-[#64748b] hover:text-[#2563eb]"
          >
            <FileImage className="w-4 h-4" />
            <span className="text-[11px] font-bold">
              Choose PNG / JPG / SVG (up to 5 MB)
            </span>
          </button>
        )}

        {floor.error && (
          <p className="text-[10px] text-[#dc2626] font-bold flex items-center gap-1">
            <AlertTriangle className="w-3 h-3" />
            {floor.error}
          </p>
        )}

        <input
          ref={fileInputRef}
          type="file"
          accept={ACCEPT}
          onChange={(e) => {
            onFilePicked(e.target.files?.[0] ?? null);
            // Reset so re-picking the same file re-fires onChange
            if (fileInputRef.current) fileInputRef.current.value = "";
          }}
          className="hidden"
        />
      </div>
    </div>
  );
};

const TextField: React.FC<{
  label: string;
  value: string;
  onChange: (v: string) => void;
  placeholder?: string;
}> = ({ label, value, onChange, placeholder }) => (
  <div className="space-y-1">
    <label className="text-[10px] font-bold uppercase tracking-wider text-[#94a3b8]">
      {label}
    </label>
    <input
      type="text"
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
      className="w-full px-2.5 py-1.5 rounded-lg border border-[#e2e8f0] bg-white text-[12px] text-[#0f172a] placeholder-[#94a3b8] focus:outline-none focus:border-[#2563eb] focus:ring-2 focus:ring-blue-100 transition-all"
    />
  </div>
);

/* --------------------------- helpers --------------------------- */

const readImage = (
  file: File
): Promise<{ dataUrl: string; width: number; height: number }> =>
  new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      const dataUrl = reader.result as string;
      if (!dataUrl) {
        reject(new Error("Could not read the image."));
        return;
      }
      // SVGs don't always report dimensions reliably via `Image`. Fall back to
      // the 1000×620 canvas viewBox if the browser can't extract them.
      const isSvg = file.type === "image/svg+xml";
      const img = new window.Image();
      img.onload = () =>
        resolve({
          dataUrl,
          width: img.naturalWidth || (isSvg ? 1000 : 0),
          height: img.naturalHeight || (isSvg ? 620 : 0),
        });
      img.onerror = () => {
        if (isSvg) {
          resolve({ dataUrl, width: 1000, height: 620 });
        } else {
          reject(new Error("The browser couldn't read this image."));
        }
      };
      img.src = dataUrl;
    };
    reader.onerror = () => reject(new Error("Could not read the file."));
    reader.readAsDataURL(file);
  });

const draftToFloor = (draft: DraftFloor): BuildingFloor => {
  // Drop a single starter room in the middle of the plan so the new floor
  // isn't clickable-less. Step 4 (room editor) is where the user places real
  // ones; this is just a "hello, click me" seed.
  const seedRoom: FloorPlanRoom = {
    id: `${draft.id}-seed`,
    name: "Untitled Room",
    kind: "office",
    status: "ready",
    scanCount: 0,
    x: 440,
    y: 260,
    w: 120,
    h: 100,
  };
  return {
    id: draft.id,
    label: draft.label.trim(),
    discipline: draft.discipline.trim() || "General",
    totalArea: draft.totalArea.trim() || "—",
    rooms: [seedRoom],
    doors: [],
    planImageDataUrl: draft.planImageDataUrl,
    planImageWidth: draft.planImageWidth,
    planImageHeight: draft.planImageHeight,
  };
};

