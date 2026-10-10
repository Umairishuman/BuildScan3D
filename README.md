# BuildScan 3D — Construction Spatial Intelligence Platform

> **Final Year Project (FYP)**  
> Real-Time Metric 3D Reconstruction, ARCore Visual-Inertial Odometry, Metric3D Depth Fusion, and 3D Gaussian Splatting for Construction Site Verification & As-Built BIM Analysis.

---

## Overview

**BuildScan 3D** is an end-to-end spatial intelligence system designed for the architecture, engineering, and construction (AEC) industry. It bridges mobile visual-inertial tracking with GPU-accelerated neural spatial reconstruction:

1. **Mobile Capture & Tracking (ARCore):** Synchronous recording of 60-120Hz camera pose trajectory ($T, Q$) and calibrated hardware intrinsics ($f_x, f_y, c_x, c_y$).
2. **Zero-Shot Metric Depth Estimation (Metric3D v2 ViT-Large):** Predicts metric-accurate depth maps directly from monocular RGB video without scale ambiguity.
3. **Point Cloud & 3DGS Dataset Generation:** Fuses multi-view RGB-D observations into dense registered metric point clouds (`dense_prior.ply`) and formats NeRF/3DGS datasets (`transforms.json`).
4. **Spatial Web Dashboard & Interactive 3D Viewer:** Next.js enterprise web application with WebGL/Three.js 3D Gaussian Splatting rendering, Semantic AI layer filters (YOLOv8-Seg for MEP/plumbing/HVAC), and 2D CAD architectural floor plan alignment.

---

## Repository Folder Structure

```
d:/FYP/
├── docs/                                    # Project documentation, proposals, and literature
│   ├── Proposal Slides/                     # Defense presentation slide decks (.pptx)
│   ├── Research Papers/                     # 3DGS, PGSR, Metric3D, and VIO research papers
│   ├── BuildScan3D_FYP_Proposal_v3.docx     # Comprehensive FYP project proposal
│   ├── POC Plans.docx                       # Proof-of-concept milestone plans
│   ├── Workflow of BuildScan.docx           # End-to-end data pipeline specifications
│   └── Guidelines.docx                      # Project guidelines & standards
│
├── googleARCore/                            # Google ARCore SDK, libraries, and native samples
│   ├── libraries/                           # Native C/C++ ARCore header files
│   ├── samples/                             # ARCore tracking, raw depth, & recording samples
│   │   ├── hello_ar_java/                   # Standard VIO tracking reference
│   │   ├── raw_depth_java/                  # Time-of-Flight / hardware depth integration
│   │   ├── recording_playback_java/         # ARCore session recording and playback pipeline
│   │   └── semantics_java/                  # On-device semantic segmentation sample
│   └── tools/                               # ARCore developer tools (e.g. arcoreimg)
│
├── prototype/                               # Application prototypes and UI frontend
│   ├── requirements.md                      # Functional & technical software requirements
│   ├── mobile-ui/                           # Mobile capture interface prototype assets
│   └── web-ui/                              # BuildScan 3D Next.js Enterprise Web Platform
│       ├── public/                          # Static assets, branding logos, and thumbnails
│       │   ├── images/                      # Official transparent logo & UI graphic assets
│       │   └── thumbnails/                  # Project card high-resolution scan thumbnails
│       ├── src/
│       │   ├── app/                         # Next.js App Router
│       │   │   ├── page.tsx                 # Enterprise split-panel Login authentication page
│       │   │   ├── dashboard/page.tsx       # Main Projects & Scans Dashboard
│       │   │   ├── viewer/[id]/page.tsx     # 3D Gaussian Splatting WebGL/Three.js Viewer page
│       │   │   └── floorplan/[id]/page.tsx  # Dedicated 2D CAD Floor Plan route
│       │   ├── components/                  # Reusable UI & 3D components
│       │   │   ├── Navbar.tsx               # Top navigation bar with 3-bar menu toggle & brand lockup
│       │   │   ├── Sidebar.tsx              # Floating collapsible navigation menu box
│       │   │   ├── ProjectCard.tsx          # Construction site scan cards with live status badges
│       │   │   ├── FloorPlanView.tsx        # Interactive 2D architectural CAD blueprint viewer
│       │   │   ├── JobStatusModal.tsx       # Live reconstruction job telemetry & processing modal
│       │   │   ├── NewCaptureModal.tsx      # Mobile sync / direct scan upload dialog
│       │   │   └── Viewer3D/                # 3D Viewport engine
│       │   │       ├── Canvas3D.tsx         # Three.js 3D WebGL render canvas
│       │   │       ├── ViewerHUD.tsx        # HUD overlay, metric measurements, & semantic AI toggles
│       │   │       ├── SceneBuilder.ts      # 3D scene construction & layer filters
│       │   │       └── MeasurementTool.ts   # Metric point-to-point distance measurement engine
│       │   └── lib/                         # Mock datasets, project schemas, & navigation helpers
│       ├── next.config.ts                   # Next.js build configuration
│       ├── package.json                     # Node.js dependencies & scripts
│       └── tsconfig.json                    # TypeScript compiler configuration
│
├── src/                                     # Core Python ML & 3D Reconstruction Pipeline
│   ├── process_dataset.py                   # Video frame extraction and pose synchronization
│   ├── visualize_trajectory.py              # 3D trajectory visualizer for ARCore camera poses
│   └── Metric3D_v2/                         # Metric3D v2 Zero-Shot Depth & 3DGS Export Pipeline
│       ├── fusion_pipeline.py               # Automated headless batch depth fusion to dense point cloud
│       └── interactive_viewer.py            # 2-pass interactive reviewer, depth heatmap GUI, & 3DGS exporter
│
├── UI designs/                              # High-fidelity Figma / UI design mockup references
│   ├── Web Designs-Light Themed.png         # Light enterprise dashboard design reference
│   └── Web designs.png                      # Dark theme & HUD reference layouts
│
├── .gitignore                               # Git ignored files (datasets, build caches, checkpoints)
├── requirements.txt                         # Python dependencies (PyTorch, Metric3D, Open3D, gsplat)
└── README.md                                # Repository documentation and setup guide
```

---

## Quick Start Guide

### 1. Python ML & Depth Fusion Pipeline Setup

#### Prerequisites:
- **Python 3.10 or 3.11**
- **NVIDIA GPU** with CUDA 11.8 or 12.1
- **Git** with Long Paths enabled (required on Windows)

```powershell
# 1. Enable long path support in Git (prevents MAX_PATH errors on Windows)
git config --global core.longpaths true

# 2. Create and activate a virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# 3. Install PyTorch with CUDA 12.1 support
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

# 4. Install remaining requirements
pip install -r requirements.txt
```

#### Running the Pipelines:

- **Interactive Reviewer & 3DGS Exporter:**
  ```powershell
  python src/Metric3D_v2/interactive_viewer.py
  ```
  - `[SPACE]`: Play / Pause video sequence.
  - `[A]` / `[D]`: Step backward / forward through keyframes.
  - `Left Click`: Inspect depth and pixel coordinates.
  - `[E]`: Fuse point cloud (`dense_prior.ply`) and export 3DGS dataset (`transforms.json` + `images/*.png`).

- **Automated Batch Fusion Pipeline:**
  ```powershell
  python src/Metric3D_v2/fusion_pipeline.py
  ```

---

### 2. Web UI Platform Setup (Next.js)

#### Prerequisites:
- **Node.js 18+ or 20+**
- **npm** or **pnpm**

```powershell
# Navigate to web application directory
cd prototype/web-ui

# Install dependencies
npm install

# Start local development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the application:
- **Login Screen:** `/`
- **Dashboard & Interactive CAD Floor Plan:** `/dashboard`
- **3D Gaussian Splatting & Semantic AI Viewer:** `/viewer/sector-4-mep`

---

## Key Features

- **Metric-Accurate Point Cloud Reconstruction:** Sub-centimeter spatial accuracy through ARCore metric scale initialization and Metric3D ViT-Large zero-shot depth priors.
- **3D Gaussian Splatting (3DGS) Export:** Automatically generates `transforms.json` with camera fields of view and $4 \times 4$ camera-to-world matrices ($c2w$) ready for real-time radiance field training.
- **Interactive 2D CAD Blueprint Integration:** Clickable room sectors allowing seamless navigation directly from 2D architectural drawings into high-fidelity 3D spatial models.
- **BIM Semantic Layer Segmentation:** Interactive layer isolation for MEP (Mechanical, Electrical, Plumbing), HVAC ductwork, fire protection, structural elements, and raw Gaussian splats.
