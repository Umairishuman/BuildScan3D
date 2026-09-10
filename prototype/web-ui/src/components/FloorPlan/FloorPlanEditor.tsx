"use client";

import React, { useCallback, useRef, useState } from "react";
import {
  ArrowLeft,
  MousePointerClick,
  Save,
  Trash2,
  X,
} from "lucide-react";
import {
  BuildingFloor,
  FloorPlanRoom,
  FloorPlanRoomKind,
  FloorPlanRoomStatus,
  MOCK_PROJECTS,
} from "@/lib/mockData";

const VIEW_W = 1000;
const VIEW_H = 620;
const DEFAULT_W = 140;
const DEFAULT_H = 110;
const CLICK_DRAG_THRESHOLD = 4; // px

interface FloorPlanEditorProps {
  floor: BuildingFloor;
  buildingName: string;
  onSave: (updatedFloor: BuildingFloor) => void;
  onCancel: () => void;
}

interface DragState {
  roomId: string;
  pointerId: number;
  startClientX: number;
  startClientY: number;
  startRoomX: number;
  startRoomY: number;
  moved: boolean;
}

const KINDS: FloorPlanRoomKind[] = [
  "mep",
  "office",
  "conference",
  "utility",
  "lobby",
  "corridor",
];

const STATUSES: FloorPlanRoomStatus[] = ["ready", "processing", "complete"];

const STATUS_STYLE: Record<
  FloorPlanRoomStatus,
  { stroke: string; fill: string; label: string }
> = {
  ready: { stroke: "#10b981", fill: "rgba(16, 185, 129, 0.15)", label: "Ready" },
  processing: {
    stroke: "#f59e0b",
    fill: "rgba(245, 158, 11, 0.15)",
    label: "Processing",
  },
  complete: {
    stroke: "#14b8a6",
    fill: "rgba(20, 184, 166, 0.15)",
    label: "Complete",
  },
};

const newRoomId = () =>
  `room-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 6)}`;

export const FloorPlanEditor: React.FC<FloorPlanEditorProps> = ({
  floor,
  buildingName,
  onSave,
  onCancel,
}) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const [rooms, setRooms] = useState<FloorPlanRoom[]>(() =>
    floor.rooms.map((r) => ({ ...r }))
  );
  const [selectedId, setSelectedId] = useState<string | null>(
    floor.rooms[0]?.id ?? null
  );
  const dragRef = useRef<DragState | null>(null);

  const isImageMode = Boolean(floor.planImageDataUrl);

  /** Convert a client (screen) coord to viewBox coord using the SVG's own CTM. */
  const toViewBox = useCallback(
    (clientX: number, clientY: number): { x: number; y: number } | null => {
      const svg = svgRef.current;
      if (!svg) return null;
      const ctm = svg.getScreenCTM();
      if (!ctm) return null;
      const pt = svg.createSVGPoint();
      pt.x = clientX;
      pt.y = clientY;
      const p = pt.matrixTransform(ctm.inverse());
      return { x: p.x, y: p.y };
    },
    []
  );

  const clamp = (v: number, min: number, max: number) =>
    Math.min(max, Math.max(min, v));

  const patchRoom = (id: string, patch: Partial<FloorPlanRoom>) => {
    setRooms((prev) => prev.map((r) => (r.id === id ? { ...r, ...patch } : r)));
  };

  const deleteRoom = (id: string) => {
    setRooms((prev) => prev.filter((r) => r.id !== id));
    setSelectedId((sel) => (sel === id ? null : sel));
  };

  const addRoomAt = (x: number, y: number) => {
    const room: FloorPlanRoom = {
      id: newRoomId(),
      name: `Room ${rooms.length + 1}`,
      kind: "office",
      status: "ready",
      scanCount: 0,
      x: clamp(x - DEFAULT_W / 2, 0, VIEW_W - DEFAULT_W),
      y: clamp(y - DEFAULT_H / 2, 0, VIEW_H - DEFAULT_H),
      w: DEFAULT_W,
      h: DEFAULT_H,
    };
    setRooms((prev) => [...prev, room]);
    setSelectedId(room.id);
  };

  /* --------------------------- Drag handlers --------------------------- */

  const beginDrag = (event: React.PointerEvent<SVGRectElement>, room: FloorPlanRoom) => {
    // Don't hijack right-clicks or auxiliary buttons.
    if (event.button !== 0) return;
    event.stopPropagation(); // don't let the SVG's add-on-click fire
    (event.target as SVGRectElement).setPointerCapture(event.pointerId);
    dragRef.current = {
      roomId: room.id,
      pointerId: event.pointerId,
      startClientX: event.clientX,
      startClientY: event.clientY,
      startRoomX: room.x,
      startRoomY: room.y,
      moved: false,
    };
    setSelectedId(room.id);
  };

  const continueDrag = (event: React.PointerEvent<SVGRectElement>) => {
    const drag = dragRef.current;
    if (!drag || drag.pointerId !== event.pointerId) return;

    const dx = event.clientX - drag.startClientX;
    const dy = event.clientY - drag.startClientY;
    if (
      !drag.moved &&
      Math.abs(dx) < CLICK_DRAG_THRESHOLD &&
      Math.abs(dy) < CLICK_DRAG_THRESHOLD
    ) {
      return; // treat as a click, don't move
    }

    // Convert delta from client px to viewBox units via the CTM.
    const svg = svgRef.current;
    if (!svg) return;
    const ctm = svg.getScreenCTM();
    if (!ctm) return;
    // Scale factors — one client pixel corresponds to 1/ctm.a and 1/ctm.d viewBox units.
    const scaleX = 1 / ctm.a;
    const scaleY = 1 / ctm.d;

    const room = rooms.find((r) => r.id === drag.roomId);
    if (!room) return;
    const newX = clamp(drag.startRoomX + dx * scaleX, 0, VIEW_W - room.w);
    const newY = clamp(drag.startRoomY + dy * scaleY, 0, VIEW_H - room.h);
    drag.moved = true;
    patchRoom(drag.roomId, { x: newX, y: newY });
  };

  const endDrag = (event: React.PointerEvent<SVGRectElement>) => {
    const drag = dragRef.current;
    if (!drag || drag.pointerId !== event.pointerId) return;
    dragRef.current = null;
  };

  /** Click on empty SVG area → add a new room at that point. */
  const handleSvgClick = (event: React.MouseEvent<SVGSVGElement>) => {
    // If a drag just happened, the room-level stopPropagation catches most,
    // but guard here too in case pointercancel left dragRef set.
    if (dragRef.current) return;
    const pt = toViewBox(event.clientX, event.clientY);
    if (!pt) return;
    addRoomAt(pt.x, pt.y);
  };

  const handleSave = () => {
    onSave({ ...floor, rooms });
  };

  const selected = rooms.find((r) => r.id === selectedId) ?? null;

  return (
    <div className="relative w-full h-full">
      {/* Blueprint background — same treatment as FloorPlanCanvas */}
      <div
        aria-hidden
        className="absolute inset-6 rounded-2xl border border-[#e2e8f0] bg-white shadow-sm overflow-hidden"
        style={{
          backgroundImage:
            "linear-gradient(to right, #e2e8f0 1px, transparent 1px), linear-gradient(to bottom, #e2e8f0 1px, transparent 1px)",
          backgroundSize: "40px 40px",
        }}
      />

      <div className="absolute inset-6 rounded-2xl overflow-hidden">
        <svg
          ref={svgRef}
          viewBox={`0 0 ${VIEW_W} ${VIEW_H}`}
          preserveAspectRatio={isImageMode ? "none" : "xMidYMid meet"}
          className="w-full h-full block cursor-crosshair"
          role="img"
          aria-label={`${buildingName} — ${floor.label} floor plan editor`}
          onClick={handleSvgClick}
        >
          {isImageMode ? (
            <image
              href={floor.planImageDataUrl}
              x={0}
              y={0}
              width={VIEW_W}
              height={VIEW_H}
              preserveAspectRatio="none"
            />
          ) : (
            <>
              <rect
                x={40}
                y={40}
                width={VIEW_W - 80}
                height={VIEW_H - 80}
                fill="#f8fafc"
                stroke="#94a3b8"
                strokeWidth={2}
                rx={4}
              />
            </>
          )}

          {rooms.map((room) => (
            <EditableRoom
              key={room.id}
              room={room}
              isSelected={room.id === selectedId}
              onPointerDown={(e) => beginDrag(e, room)}
              onPointerMove={continueDrag}
              onPointerUp={endDrag}
              onPointerCancel={endDrag}
              onDelete={() => deleteRoom(room.id)}
            />
          ))}
        </svg>
      </div>

      {/* Floating help tip, top-left */}
      <div className="absolute top-10 left-10 z-10 flex items-center gap-2 px-3 py-1.5 rounded-xl bg-white/95 backdrop-blur-md border border-[#e2e8f0] shadow-sm text-[11px] font-bold text-[#0f172a]">
        <MousePointerClick className="w-3.5 h-3.5 text-[#2563eb]" />
        Click empty space to add a room · drag a room to reposition
      </div>

      {/* Save / Cancel toolbar, top-right */}
      <div className="absolute top-10 right-10 z-10 flex items-center gap-2">
        <button
          onClick={onCancel}
          className="inline-flex items-center gap-1.5 px-3 py-2 rounded-xl bg-white border border-[#e2e8f0] text-[11px] font-bold text-[#0f172a] hover:bg-slate-50 shadow-sm cursor-pointer"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          Cancel
        </button>
        <button
          onClick={handleSave}
          className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-[#2563eb] hover:bg-[#1d4ed8] text-white text-[11px] font-bold shadow-md cursor-pointer"
        >
          <Save className="w-3.5 h-3.5" />
          Save Layout
        </button>
      </div>

      {/* Room-details editor panel, bottom-right */}
      {selected && (
        <div className="absolute bottom-10 right-10 z-10 w-72">
          <RoomDetailsPanel
            room={selected}
            onChange={(patch) => patchRoom(selected.id, patch)}
            onDelete={() => deleteRoom(selected.id)}
            onClose={() => setSelectedId(null)}
          />
        </div>
      )}
    </div>
  );
};

/* --------------------------- EditableRoom --------------------------- */

interface EditableRoomProps {
  room: FloorPlanRoom;
  isSelected: boolean;
  onPointerDown: (event: React.PointerEvent<SVGRectElement>) => void;
  onPointerMove: (event: React.PointerEvent<SVGRectElement>) => void;
  onPointerUp: (event: React.PointerEvent<SVGRectElement>) => void;
  onPointerCancel: (event: React.PointerEvent<SVGRectElement>) => void;
  onDelete: () => void;
}

const EditableRoom: React.FC<EditableRoomProps> = ({
  room,
  isSelected,
  onPointerDown,
  onPointerMove,
  onPointerUp,
  onPointerCancel,
  onDelete,
}) => {
  const style = STATUS_STYLE[room.status];
  const cx = room.x + room.w / 2;
  const cy = room.y + room.h / 2;
  return (
    <g style={{ cursor: "grab" }}>
      <rect
        x={room.x}
        y={room.y}
        width={room.w}
        height={room.h}
        fill={style.fill}
        stroke={isSelected ? "#2563eb" : style.stroke}
        strokeWidth={isSelected ? 3 : 2}
        strokeDasharray={isSelected ? undefined : "5 3"}
        rx={4}
        onPointerDown={onPointerDown}
        onPointerMove={onPointerMove}
        onPointerUp={onPointerUp}
        onPointerCancel={onPointerCancel}
      />
      <text
        x={cx}
        y={cy - 6}
        textAnchor="middle"
        fontSize={15}
        fontWeight={700}
        fill="#0f172a"
        style={{ pointerEvents: "none", userSelect: "none" }}
      >
        {room.name}
      </text>
      <text
        x={cx}
        y={cy + 12}
        textAnchor="middle"
        fontSize={11}
        fontWeight={500}
        fill="#475569"
        style={{ pointerEvents: "none", userSelect: "none" }}
      >
        {style.label} · {room.scanCount} scan{room.scanCount === 1 ? "" : "s"}
      </text>

      {/* Delete handle in the corner when selected */}
      {isSelected && (
        <g
          transform={`translate(${room.x + room.w - 14} ${room.y + 14})`}
          onClick={(e) => {
            e.stopPropagation();
            onDelete();
          }}
          style={{ cursor: "pointer" }}
        >
          <circle r={10} fill="#dc2626" />
          <path
            d="M -4 -4 L 4 4 M 4 -4 L -4 4"
            stroke="white"
            strokeWidth={2}
            strokeLinecap="round"
          />
        </g>
      )}
    </g>
  );
};

/* --------------------------- Details panel --------------------------- */

interface RoomDetailsPanelProps {
  room: FloorPlanRoom;
  onChange: (patch: Partial<FloorPlanRoom>) => void;
  onDelete: () => void;
  onClose: () => void;
}

const RoomDetailsPanel: React.FC<RoomDetailsPanelProps> = ({
  room,
  onChange,
  onDelete,
  onClose,
}) => (
  <div className="rounded-2xl bg-white/95 backdrop-blur-md border border-[#e2e8f0] shadow-2xl overflow-hidden">
    <div className="px-4 py-2.5 border-b border-[#f1f5f9] flex items-center justify-between">
      <div className="flex items-center gap-2 min-w-0">
        <span
          className="w-2.5 h-2.5 rounded-full shrink-0"
          style={{ backgroundColor: STATUS_STYLE[room.status].stroke }}
        />
        <h3 className="text-[11px] font-bold text-[#0f172a] truncate">
          Editing room
        </h3>
      </div>
      <button
        onClick={onClose}
        aria-label="Close panel"
        className="p-1 rounded-md text-[#94a3b8] hover:text-[#0f172a] hover:bg-slate-100 cursor-pointer"
      >
        <X className="w-3.5 h-3.5" />
      </button>
    </div>

    <div className="p-3 space-y-3">
      <Field label="Name">
        <input
          type="text"
          value={room.name}
          onChange={(e) => onChange({ name: e.target.value })}
          className="w-full px-2.5 py-1.5 rounded-lg border border-[#e2e8f0] text-[12px] text-[#0f172a] focus:outline-none focus:border-[#2563eb] focus:ring-2 focus:ring-blue-100"
        />
      </Field>

      <div className="grid grid-cols-2 gap-2">
        <Field label="Status">
          <select
            value={room.status}
            onChange={(e) =>
              onChange({ status: e.target.value as FloorPlanRoomStatus })
            }
            className="w-full px-2 py-1.5 rounded-lg border border-[#e2e8f0] text-[12px] text-[#0f172a] bg-white focus:outline-none focus:border-[#2563eb] focus:ring-2 focus:ring-blue-100"
          >
            {STATUSES.map((s) => (
              <option key={s} value={s}>
                {s[0].toUpperCase() + s.slice(1)}
              </option>
            ))}
          </select>
        </Field>
        <Field label="Discipline">
          <select
            value={room.kind}
            onChange={(e) =>
              onChange({ kind: e.target.value as FloorPlanRoomKind })
            }
            className="w-full px-2 py-1.5 rounded-lg border border-[#e2e8f0] text-[12px] text-[#0f172a] bg-white focus:outline-none focus:border-[#2563eb] focus:ring-2 focus:ring-blue-100"
          >
            {KINDS.map((k) => (
              <option key={k} value={k}>
                {k[0].toUpperCase() + k.slice(1)}
              </option>
            ))}
          </select>
        </Field>
      </div>

      <Field label="Scan count">
        <input
          type="number"
          min={0}
          value={room.scanCount}
          onChange={(e) =>
            onChange({ scanCount: Math.max(0, parseInt(e.target.value) || 0) })
          }
          className="w-full px-2.5 py-1.5 rounded-lg border border-[#e2e8f0] text-[12px] text-[#0f172a] focus:outline-none focus:border-[#2563eb] focus:ring-2 focus:ring-blue-100"
        />
      </Field>

      <Field label="Opens viewer for">
        <select
          value={room.targetProjectId ?? ""}
          onChange={(e) =>
            onChange({
              targetProjectId: e.target.value || undefined,
            })
          }
          className="w-full px-2 py-1.5 rounded-lg border border-[#e2e8f0] text-[12px] text-[#0f172a] bg-white focus:outline-none focus:border-[#2563eb] focus:ring-2 focus:ring-blue-100"
        >
          <option value="">— Plan default —</option>
          {MOCK_PROJECTS.map((p) => (
            <option key={p.id} value={p.id}>
              {p.name}
            </option>
          ))}
        </select>
      </Field>

      <button
        onClick={onDelete}
        className="w-full inline-flex items-center justify-center gap-1.5 py-1.5 rounded-lg border border-red-200 bg-red-50 text-[#dc2626] text-[11px] font-bold hover:bg-red-100 cursor-pointer transition-colors"
      >
        <Trash2 className="w-3.5 h-3.5" />
        Delete room
      </button>
    </div>
  </div>
);

const Field: React.FC<{ label: string; children: React.ReactNode }> = ({
  label,
  children,
}) => (
  <div className="space-y-1">
    <label className="text-[10px] font-bold uppercase tracking-wider text-[#94a3b8]">
      {label}
    </label>
    {children}
  </div>
);

