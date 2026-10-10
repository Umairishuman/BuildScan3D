"use client";

import React from "react";

/**
 * Decorative construction-themed backdrop for the /projects page. Sits behind
 * the content (`aria-hidden`), non-interactive. Draws an isometric building
 * silhouette with a tower crane, dimension lines, and dashed blueprint arcs
 * over the shared CAD grid AppShell already lays down.
 */
export const ProjectsBackdrop: React.FC = () => (
  <div
    aria-hidden
    className="pointer-events-none absolute inset-0 -z-0 overflow-hidden"
  >
    {/* Soft radial tint bloom in top-right */}
    <div
      className="absolute -top-20 -right-20 w-[520px] h-[520px] rounded-full opacity-40"
      style={{
        background:
          "radial-gradient(closest-side, rgba(37, 99, 235, 0.16), transparent 70%)",
      }}
    />

    {/* Isometric building + crane, upper-right */}
    <svg
      viewBox="0 0 900 620"
      className="absolute top-8 right-0 h-[560px] w-auto opacity-[0.10]"
      preserveAspectRatio="xMidYMid meet"
      role="presentation"
    >
      <defs>
        <linearGradient id="pb-face" x1="0" x2="0" y1="0" y2="1">
          <stop offset="0" stopColor="#2563eb" stopOpacity="0.6" />
          <stop offset="1" stopColor="#2563eb" stopOpacity="0.9" />
        </linearGradient>
        <pattern id="pb-window" x="0" y="0" width="24" height="30" patternUnits="userSpaceOnUse">
          <rect width="24" height="30" fill="transparent" />
          <rect x="6" y="6" width="12" height="14" fill="#2563eb" opacity="0.55" />
        </pattern>
      </defs>

      {/* Ground line */}
      <line x1="60" y1="560" x2="860" y2="560" stroke="#0f172a" strokeWidth="1.5" />
      {/* Ground ticks */}
      {Array.from({ length: 22 }).map((_, i) => (
        <line
          key={i}
          x1={60 + i * 36}
          y1={560}
          x2={70 + i * 36}
          y2={572}
          stroke="#0f172a"
          strokeWidth="0.8"
        />
      ))}

      {/* Isometric building shell — left face */}
      <polygon
        points="180,560 180,240 380,180 380,500"
        fill="url(#pb-window)"
        stroke="#0f172a"
        strokeWidth="1.5"
      />
      {/* Building right face */}
      <polygon
        points="380,180 620,220 620,540 380,500"
        fill="url(#pb-face)"
        stroke="#0f172a"
        strokeWidth="1.5"
      />
      {/* Building roof */}
      <polygon
        points="180,240 380,180 620,220 420,280"
        fill="#0f172a"
        opacity="0.55"
        stroke="#0f172a"
        strokeWidth="1.2"
      />
      {/* Second smaller tower */}
      <polygon
        points="620,540 620,320 720,340 720,560"
        fill="#2563eb"
        opacity="0.75"
        stroke="#0f172a"
        strokeWidth="1.2"
      />
      <polygon
        points="620,320 720,340 760,330 660,310"
        fill="#0f172a"
        opacity="0.55"
      />

      {/* Tower crane */}
      <g stroke="#0f172a" strokeWidth="1.6" fill="none">
        {/* Mast */}
        <line x1="470" y1="560" x2="470" y2="80" />
        <line x1="480" y1="560" x2="480" y2="80" />
        {/* Mast lattice */}
        {Array.from({ length: 14 }).map((_, i) => (
          <line
            key={i}
            x1="470"
            y1={100 + i * 32}
            x2="480"
            y2={132 + i * 32}
          />
        ))}
        {/* Cabin */}
        <rect x="460" y="70" width="30" height="18" fill="#facc15" opacity="0.85" />
        {/* Jib (working arm) */}
        <line x1="475" y1="72" x2="770" y2="72" />
        <line x1="475" y1="66" x2="770" y2="90" strokeDasharray="6 3" />
        {/* Counter-jib */}
        <line x1="475" y1="72" x2="360" y2="72" />
        <line x1="475" y1="66" x2="360" y2="82" strokeDasharray="4 3" />
        {/* Hook + cable */}
        <line x1="700" y1="72" x2="700" y2="360" strokeDasharray="3 3" />
        <polygon points="694,360 706,360 704,372 696,372" fill="#0f172a" opacity="0.85" />
      </g>

      {/* Dimension arrow beneath the building */}
      <g stroke="#0f172a" strokeWidth="1" opacity="0.75">
        <line x1="180" y1="590" x2="720" y2="590" />
        <line x1="180" y1="584" x2="180" y2="596" />
        <line x1="720" y1="584" x2="720" y2="596" />
        <polygon points="180,590 190,586 190,594" fill="#0f172a" />
        <polygon points="720,590 710,586 710,594" fill="#0f172a" />
      </g>
      <text
        x="450"
        y="608"
        fontSize="12"
        fontWeight="700"
        fill="#0f172a"
        textAnchor="middle"
      >
        54.00 m
      </text>
    </svg>

    {/* Blueprint drafting arc + coordinates, lower-left */}
    <svg
      viewBox="0 0 600 500"
      className="absolute bottom-4 left-0 h-[420px] w-auto opacity-[0.09]"
      preserveAspectRatio="xMidYMid meet"
      role="presentation"
    >
      <g stroke="#0f172a" strokeWidth="1.2" fill="none">
        {/* Compass arc */}
        <path d="M 80 400 A 220 220 0 0 1 520 400" strokeDasharray="6 4" />
        <path d="M 130 400 A 170 170 0 0 1 470 400" />
        {/* Centreline */}
        <line x1="300" y1="400" x2="300" y2="150" />
        {/* Radial ticks */}
        {Array.from({ length: 9 }).map((_, i) => {
          const a = (i / 8) * Math.PI;
          const x1 = 300 + Math.cos(Math.PI - a) * 170;
          const y1 = 400 - Math.sin(a) * 170;
          const x2 = 300 + Math.cos(Math.PI - a) * 190;
          const y2 = 400 - Math.sin(a) * 190;
          return (
            <line key={i} x1={x1} y1={y1} x2={x2} y2={y2} strokeWidth="1" />
          );
        })}
        <line x1="80" y1="400" x2="520" y2="400" />
      </g>
      <text x="290" y="392" fontSize="10" fontWeight="700" fill="#0f172a">
        A1
      </text>
      <text x="300" y="150" fontSize="10" fontWeight="700" fill="#0f172a" textAnchor="middle">
        N
      </text>
    </svg>

    {/* Fade-to-content overlay so content stays readable */}
    <div
      className="absolute inset-0"
      style={{
        background:
          "linear-gradient(180deg, rgba(248,250,252,0) 40%, rgba(248,250,252,0.9) 100%)",
      }}
    />
  </div>
);
