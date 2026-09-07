# BuildScan 3D — Project Overview

## What is BuildScan 3D?

BuildScan 3D is a construction-site scanning system that lets field workers capture a physical space with a mobile phone and delivers an interactive, metric-accurate 3D model to construction managers through a web dashboard. The pipeline fuses phone video with AR spatial data to reconstruct geometry, semantically labels building systems (pipes, wiring, HVAC) using AI, and serves the result as a WebGPU-rendered `.ksplat` model with on-demand measurement tools.

---

## Full Project Architecture (100% Scope)

The complete system runs across five sequential pipeline stages:

| # | Stage | What it does | Technologies |
|---|---|---|---|
| 1 | **Edge Capture (Mobile)** | Records 30 FPS video synced with 120 Hz spatial IMU telemetry from the phone's AR framework | React Native (UI), CameraX / ARCore (Android), AVFoundation / ARKit (iOS) |
| 2 | **Pose Prior Injection** | Converts mobile quaternion data into 3×3 rotation matrices and writes them into the reconstruction database | Python, `pycolmap`, `sqlite3`, Ubuntu |
| 3 | **Metric Reconstruction** | Fuses visual frames with AR telemetry to handle blank walls and enforce absolute physical scale | COLMAP (`pose_prior_mapper`), Nerfstudio (3DGS) |
| 4 | **AI Semantic Labeling** | Projects 2D segmentation masks into 3D space to auto-identify pipes, wiring, and HVAC components | PyTorch, YOLOv8-Seg, Cloud GPU |
| 5 | **Web Orchestration** | Manages background rendering jobs and serves the interactive 3D model to the browser | Next.js, Node.js, Prisma, Redis, WebGPU |

---

## Proof of Concept (PoC) Scope — Defense Build

The PoC strips out ARCore and the entire Python/COLMAP backend. The goal is a **clickable, high-fidelity functional prototype** that demonstrates the complete user journey visually — satisfying the FAST-NUCES committee requirement without requiring live AR hardware or a running ML pipeline.

### What's removed from the PoC
- Live camera capture and ARCore/ARKit integration
- Python pose-prior injection pipeline
- COLMAP reconstruction and Nerfstudio rendering
- YOLOv8 semantic labeling
- Redis job queue and real backend processing

### What the PoC delivers

#### 1. Mobile App Skeleton (React Native)

| Feature | Description |
|---|---|
| **Simulated Viewfinder** | Camera screen showing a static image or locally looped video in place of a live feed |
| **Mock Telemetry Overlay** | UI indicators displaying "Spatial Tracking: Stable" and a dummy coordinate ticker to simulate AR data collection |
| **Workflow Navigation** | A working "Record" button that transitions to a mock "Uploading to Cloud…" confirmation screen, proving the full field-worker journey |

#### 2. Web Dashboard Skeleton (Next.js + Three.js / WebGPU)

Six screens. Light theme. Desktop viewport (1440 × 900). No marketing pages — drops straight into the enterprise SaaS workflow.

| Screen | Name | Key UI Elements |
|---|---|---|
| **S1** | **Authentication** | Centered login card · email + password fields · "Sign In" → `/dashboard` (no real auth) · security badges (256-bit, SOC 2) |
| **S2** | **Project Dashboard** | Left sidebar nav · global search · project cards in grid (site name, floor, area, scan count, capture date) · status badges: Ready (green), Processing (amber), Draft (grey) · "New Capture" button (disabled, tooltip: "Initiate from BuildScan mobile app") |
| **S3** | **Active Job Status** | Right slide-over panel (480px) triggered by clicking a Processing card · circular progress ring (e.g. 67%) · vertical step-tracker: ✅ Video Ingested → ✅ ARCore Poses Aligned → ✅ COLMAP SfM → ⏳ 3DGS Training (live progress bar, ETA) → ⬜ Export → ⬜ Semantic Projection → ⬜ Ready · collapsible raw logs panel in monospace |
| **S4** | **3D Viewer Workspace** | Left layer panel (Raw Geometry, Electrical, Plumbing, HVAC, Structural, Drywall toggles + opacity slider + X-Ray Mode) · central Three.js canvas with orientation widget, scale bar, view-mode pill (Perspective / Orthographic) · floating tool palette (Select, Measure, Annotate, Section Cut, Fullscreen) · Measure tool: click two points → dashed line + floating `2.47 m` badge in monospace · right panel: saved measurements list + Annotations |
| **S5** | **Scan History / Timeline** | Horizontal film-strip scrubber of all scans for a site · split view: selected scan (mini 3D viewer, left) vs. diff from previous scan (amber = added, red = removed, right) · change log table below (Element, Change Type, Layer, Delta, Flagged) |
| **S6** | **Notifications Feed** | Right slide-over · chronological system + team events · color-coded left borders by type (green = ready, amber = processing, red = failed) · "Mark all read" |

---

## Tech Stack Summary

| Layer | PoC Technologies | Full Build Additions |
|---|---|---|
| Mobile | React Native | CameraX, ARCore, AVFoundation, ARKit |
| Reconstruction | — | Python, pycolmap, COLMAP, Nerfstudio |
| AI / ML | — | PyTorch, YOLOv8-Seg, Cloud GPU |
| Web Frontend | Next.js, Three.js, WebGPU | WebGPU (live model) |
| Backend / Infra | Next.js API routes | Node.js, Prisma, Redis, SQLite |

---

## Roadmap

```
Phase 1 — PoC (Current)
  ├── React Native mobile skeleton with mock telemetry
  └── Next.js web dashboard with static 3D viewer and fake pipeline status

Phase 2 — Live Capture
  ├── ARCore / ARKit integration (real video + IMU)
  └── Upload pipeline to cloud storage

Phase 3 — Reconstruction Backend
  ├── Python pose-prior injection (pycolmap + sqlite3)
  └── COLMAP metric reconstruction + Nerfstudio 3DGS export

Phase 4 — AI Labeling
  ├── YOLOv8-Seg segmentation on GPU
  └── 2D → 3D mask projection

Phase 5 — Full Production
  ├── Redis job queue for async rendering
  ├── Live .ksplat delivery via WebGPU
  └── Real measurement tool with computed distances
```

---

## Key Terms

- **IMU** — Inertial Measurement Unit; the phone's gyroscope + accelerometer combination used to track orientation and movement.
- **Quaternion** — A mathematical representation of 3D rotation used by AR frameworks; converted to 3×3 matrices for COLMAP.
- **COLMAP** — Open-source Structure-from-Motion and MVS pipeline used for 3D reconstruction from images.
- **3DGS (3D Gaussian Splatting)** — A real-time novel-view synthesis technique that represents a scene as a cloud of oriented Gaussians; exported as `.ksplat` files.
- **Nerfstudio** — A modular framework for training and exporting NeRF and 3DGS models.
- **YOLOv8-Seg** — Ultralytics' instance segmentation model used to identify and mask building components in 2D frames.
- **`.ksplat`** — A binary file format for streaming and rendering 3D Gaussian Splat scenes in the browser via WebGPU.
- **Pose Prior** — A known camera position/orientation injected into COLMAP to improve reconstruction accuracy in low-texture environments (blank walls).