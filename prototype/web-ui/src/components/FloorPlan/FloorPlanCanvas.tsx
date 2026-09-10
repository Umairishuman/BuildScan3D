"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import {
  BuildingFloor,
  FloorPlanDoor,
  FloorPlanRoom,
  FloorPlanRoomKind,
  FloorPlanRoomStatus,
} from "@/lib/mockData";

const VIEW_W = 1000;
const VIEW_H = 620;
const MARGIN = 40;

/** Room fills — brand-neutral pastels keyed to discipline. */
const KIND_FILL: Record<FloorPlanRoomKind, string> = {
  mep: "#eff6ff",
  office: "#fefce8",
  conference: "#f3e8ff",
  utility: "#f1f5f9",
  lobby: "#ecfeff",
  corridor: "#f8fafc",
};

const STATUS_STROKE: Record<FloorPlanRoomStatus, string> = {
  ready: "#10b981",
  processing: "#f59e0b",
  complete: "#14b8a6",
};

const STATUS_FILL: Record<FloorPlanRoomStatus, string> = {
  ready: "#ffffff",
  processing: "#fffbeb",
  complete: "#ffffff",
};

const STATUS_LABEL: Record<FloorPlanRoomStatus, string> = {
  ready: "Ready",
  processing: "Processing",
  complete: "Complete",
};

interface FloorPlanCanvasProps {
  floor: BuildingFloor;
  buildingName: string;
  /** Where every clickable room should navigate. */
  targetProjectId: string;
}

export const FloorPlanCanvas: React.FC<FloorPlanCanvasProps> = ({
  floor,
  buildingName,
  targetProjectId,
}) => {
  const router = useRouter();
  const [hovered, setHovered] = useState<FloorPlanRoom | null>(null);

  const isImageMode = Boolean(floor.planImageDataUrl);

  // Rooms opt in to a specific viewer via `room.targetProjectId`; unset rooms
  // fall back to the plan-level default supplied by the caller.
  const openRoom = (room: FloorPlanRoom) => {
    router.push(`/viewer/${room.targetProjectId ?? targetProjectId}`);
  };

  return (
    <div className="relative w-full h-full">
      {/* Blueprint background: CAD grid + soft vignette. Kept inside the canvas so
          the surrounding shell keeps the app's plain slate ground. */}
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
          viewBox={`0 0 ${VIEW_W} ${VIEW_H}`}
          preserveAspectRatio="xMidYMid meet"
          className="w-full h-full block"
          role="img"
          aria-label={`${buildingName} — ${floor.label} floor plan`}
        >
          {isImageMode ? (
            <>
              {/* Uploaded plan as the base layer. Stretched to fill the viewBox
                  so room coords (0-1000 × 0-620) map 1:1 to image pixels. */}
              <image
                href={floor.planImageDataUrl}
                x={0}
                y={0}
                width={VIEW_W}
                height={VIEW_H}
                preserveAspectRatio="none"
              />

              {/* Invisible hover / click hit-boxes so the whole room area,
                  not just the small node dot, responds to the pointer. */}
              {floor.rooms.map((room) => (
                <rect
                  key={`hit-${room.id}`}
                  x={room.x}
                  y={room.y}
                  width={room.w}
                  height={room.h}
                  fill="transparent"
                  onMouseEnter={() => setHovered(room)}
                  onMouseLeave={() => setHovered(null)}
                  onClick={
                    room.status === "processing" ? undefined : () => openRoom(room)
                  }
                  style={{
                    cursor:
                      room.status === "processing" ? "not-allowed" : "pointer",
                  }}
                />
              ))}
            </>
          ) : (
            <>
              {/* Outer wall */}
              <rect
                x={MARGIN}
                y={MARGIN}
                width={VIEW_W - MARGIN * 2}
                height={VIEW_H - MARGIN * 2}
                fill="none"
                stroke="#0f172a"
                strokeWidth={4}
                rx={4}
              />

              {/* Dimension ticks along the top edge */}
              <DimensionRuler />

              {/* Compass rose (top-right, inside the plan) */}
              <CompassRose x={VIEW_W - MARGIN - 60} y={MARGIN + 60} />

              {/* Rooms */}
              {floor.rooms.map((room) => (
                <RoomShape
                  key={room.id}
                  room={room}
                  isHovered={hovered?.id === room.id}
                  onEnter={() => setHovered(room)}
                  onLeave={() => setHovered(null)}
                  onOpen={() => openRoom(room)}
                />
              ))}

              {/* Doors — small quarter-circle swings */}
              {floor.doors.map((door, i) => (
                <DoorSwing key={i} door={door} />
              ))}
            </>
          )}

          {/* Status nodes anchored to room centres (shared across both modes) */}
          {floor.rooms.map((room) => (
            <StatusNode
              key={`node-${room.id}`}
              room={room}
              isHovered={hovered?.id === room.id}
              onEnter={() => setHovered(room)}
              onLeave={() => setHovered(null)}
              onOpen={() => openRoom(room)}
              stroked={isImageMode}
            />
          ))}
        </svg>

        {/* Hover tooltip (HTML, positioned in room-coord space via CSS %) */}
        {hovered && <RoomTooltip room={hovered} />}
      </div>
    </div>
  );
};

/* ------------------------------------------------------------------ */
/* SVG sub-components                                                  */
/* ------------------------------------------------------------------ */

interface RoomShapeProps {
  room: FloorPlanRoom;
  isHovered: boolean;
  onEnter: () => void;
  onLeave: () => void;
  onOpen: () => void;
}

const RoomShape: React.FC<RoomShapeProps> = ({
  room,
  isHovered,
  onEnter,
  onLeave,
  onOpen,
}) => {
  const canOpen = room.status !== "processing";
  const cx = room.x + room.w / 2;
  const cy = room.y + room.h / 2;

  return (
    <g
      onMouseEnter={onEnter}
      onMouseLeave={onLeave}
      onClick={canOpen ? onOpen : undefined}
      style={{ cursor: canOpen ? "pointer" : "not-allowed" }}
    >
      <rect
        x={room.x}
        y={room.y}
        width={room.w}
        height={room.h}
        fill={KIND_FILL[room.kind]}
        stroke={isHovered ? "#2563eb" : "#94a3b8"}
        strokeWidth={isHovered ? 2 : 1.25}
        strokeDasharray={room.kind === "corridor" ? "4 4" : undefined}
      />
      <text
        x={cx}
        y={cy - 6}
        textAnchor="middle"
        fontSize={16}
        fontWeight={700}
        fill="#0f172a"
        style={{ pointerEvents: "none" }}
      >
        {room.name}
      </text>
      <text
        x={cx}
        y={cy + 14}
        textAnchor="middle"
        fontSize={11}
        fontWeight={500}
        fill="#64748b"
        style={{ pointerEvents: "none" }}
      >
        {room.scanCount} scan{room.scanCount === 1 ? "" : "s"} · {STATUS_LABEL[room.status]}
      </text>
    </g>
  );
};

const DoorSwing: React.FC<{ door: FloorPlanDoor }> = ({ door }) => {
  const { cx, cy, radius, quadrant } = door;
  // Build a quarter-arc: start point → arc endpoint by quadrant.
  const points: Record<typeof quadrant, { sx: number; sy: number; ex: number; ey: number }> = {
    tr: { sx: cx + radius, sy: cy, ex: cx, ey: cy - radius },
    tl: { sx: cx, sy: cy - radius, ex: cx - radius, ey: cy },
    br: { sx: cx, sy: cy + radius, ex: cx + radius, ey: cy },
    bl: { sx: cx - radius, sy: cy, ex: cx, ey: cy + radius },
  };
  const p = points[quadrant];
  const sweep = quadrant === "tr" || quadrant === "bl" ? 0 : 1;
  return (
    <g stroke="#0f172a" fill="none" strokeWidth={1.25} opacity={0.55}>
      <path d={`M ${p.sx} ${p.sy} A ${radius} ${radius} 0 0 ${sweep} ${p.ex} ${p.ey}`} />
      <line x1={cx} y1={cy} x2={p.sx} y2={p.sy} />
    </g>
  );
};

interface StatusNodeProps {
  room: FloorPlanRoom;
  isHovered: boolean;
  onEnter: () => void;
  onLeave: () => void;
  onOpen: () => void;
  /** True when the base layer is a photograph — add a white halo for contrast. */
  stroked?: boolean;
}

const StatusNode: React.FC<StatusNodeProps> = ({
  room,
  isHovered,
  onEnter,
  onLeave,
  onOpen,
  stroked = false,
}) => {
  const canOpen = room.status !== "processing";
  const cx = room.x + room.w / 2;
  const cy = room.y + 24;
  const stroke = STATUS_STROKE[room.status];
  const fill = STATUS_FILL[room.status];

  return (
    <g
      onMouseEnter={onEnter}
      onMouseLeave={onLeave}
      onClick={canOpen ? onOpen : undefined}
      style={{ cursor: canOpen ? "pointer" : "not-allowed" }}
    >
      {/* Processing pulse ring */}
      {room.status === "processing" && (
        <circle
          cx={cx}
          cy={cy}
          r={16}
          fill="none"
          stroke={stroke}
          strokeWidth={2}
          opacity={0.5}
        >
          <animate
            attributeName="r"
            values="10;22;10"
            dur="1.8s"
            repeatCount="indefinite"
          />
          <animate
            attributeName="opacity"
            values="0.55;0;0.55"
            dur="1.8s"
            repeatCount="indefinite"
          />
        </circle>
      )}
      {/* Contrast halo when the node sits on an uploaded photograph */}
      {stroked && (
        <circle
          cx={cx}
          cy={cy}
          r={isHovered ? 14 : 12}
          fill="white"
          opacity={0.9}
        />
      )}
      <circle
        cx={cx}
        cy={cy}
        r={isHovered ? 12 : 10}
        fill={fill}
        stroke={stroke}
        strokeWidth={2.5}
      />
      <circle cx={cx} cy={cy} r={4} fill={stroke} />
    </g>
  );
};

const DimensionRuler: React.FC = () => {
  const ticks: number[] = [];
  const step = 100;
  for (let x = MARGIN; x <= VIEW_W - MARGIN; x += step) ticks.push(x);

  return (
    <g stroke="#cbd5e1" strokeWidth={0.75}>
      <line x1={MARGIN} y1={26} x2={VIEW_W - MARGIN} y2={26} />
      {ticks.map((x) => (
        <g key={x}>
          <line x1={x} y1={22} x2={x} y2={30} />
          <text
            x={x}
            y={18}
            fontSize={8}
            fontWeight={600}
            fill="#94a3b8"
            textAnchor="middle"
          >
            {((x - MARGIN) / 10).toFixed(0)}m
          </text>
        </g>
      ))}
    </g>
  );
};

const CompassRose: React.FC<{ x: number; y: number }> = ({ x, y }) => (
  <g transform={`translate(${x} ${y})`}>
    <circle r={22} fill="white" stroke="#e2e8f0" strokeWidth={1} />
    <polygon
      points="0,-16 6,4 0,-2 -6,4"
      fill="#2563eb"
      stroke="#1d4ed8"
      strokeWidth={0.75}
    />
    <text
      y={-18}
      textAnchor="middle"
      fontSize={9}
      fontWeight={700}
      fill="#0f172a"
    >
      N
    </text>
  </g>
);

/* ------------------------------------------------------------------ */
/* HTML tooltip                                                         */
/* ------------------------------------------------------------------ */

const RoomTooltip: React.FC<{ room: FloorPlanRoom }> = ({ room }) => {
  // Position the tooltip as a % over the SVG viewport so it tracks the room
  // even when the plan is scaled to the containing box.
  const leftPct = ((room.x + room.w / 2) / VIEW_W) * 100;
  const topPct = ((room.y - 12) / VIEW_H) * 100;

  return (
    <div
      className="pointer-events-none absolute z-10 -translate-x-1/2 -translate-y-full px-3 py-2 rounded-xl bg-white border border-[#e2e8f0] shadow-lg min-w-[180px]"
      style={{ left: `${leftPct}%`, top: `${topPct}%` }}
      role="tooltip"
    >
      <div className="flex items-center gap-2 mb-1">
        <span
          className="w-2 h-2 rounded-full"
          style={{ backgroundColor: STATUS_STROKE[room.status] }}
        />
        <span
          className="text-[10px] font-bold uppercase tracking-wider"
          style={{ color: STATUS_STROKE[room.status] }}
        >
          {STATUS_LABEL[room.status]}
        </span>
      </div>
      <p className="text-[12px] font-bold text-[#0f172a] leading-snug">
        {room.name}
      </p>
      <p className="text-[11px] text-[#64748b] mt-0.5">
        {room.scanCount} scan{room.scanCount === 1 ? "" : "s"} captured
      </p>
      {room.status !== "processing" && (
        <p className="text-[10px] font-bold text-[#2563eb] mt-1.5">
          Click to open 3D viewer →
        </p>
      )}
    </div>
  );
};
