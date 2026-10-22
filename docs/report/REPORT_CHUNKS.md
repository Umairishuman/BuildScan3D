# Report prose chunks

- **Chunks:** 105
- **Total words:** 10930
- **Date:** 2026-10-22
- **Taken from commit:** `f532caf` (`F26_FYP1_Mid_Report_LaTeX_Complete/chapters/`)
- **Chunk size:** 13–197 words (cap 200). Every chunk ends at the end of a paragraph or list item, so at a sentence end; no paragraph had to be split.
- **No `.tex` file was modified** by this extraction pass.

Notes for the apply pass (Prompt B):

- Chunks break at every `\chapter`, `\section` and `\subsection`, and at every table, figure and TikZ environment, so many sections give one short chunk. `\paragraph{}` lead-ins do not start a new chunk; their titles are not in `original:`, but their markup lies inside the `lines:` span and must be kept.
- `[ref: label]` and `[cite: key]` stand for `\ref{label}` and `\cite{key}`; the word before them (Table, Figure, Section, Chapter) is the report's own.
- Maths is rendered as plain symbols (`>=`, `→`, `~`, `×`, `≈`, `k_1`); list items appear one per line in source order.
- A `lines:` span may also contain `\begin{itemize}` / `\end{itemize}` lines and blank lines between the prose it covers. It never contains a heading line (other than a `\paragraph{}` lead-in), a table or a figure.

## 04_abstract.tex

### CHUNK 001
- **file:** chapters/04_abstract.tex
- **section:** Abstract
- **lines:** 5-7
- **words:** 170

original:

Existing 3D scanning solutions for indoor environments require expensive LiDAR hardware or multi-step manual workflows inaccessible to construction site teams, facility managers, and small architectural firms. This project, BuildScan 3D, addresses the gap by providing an end-to-end pipeline that converts a recording from a commodity Android smartphone (a realme phone, with no LiDAR or special hardware) into a metric-scale, photorealistic 3D Gaussian Splatting (3DGS) model suitable for real-world measurements.

The system comprises five stages: (1) a custom ARCore-based Android application that captures 30 FPS video alongside camera poses, depth maps, and live image-quality feedback; (2) a pose-prior module that aligns ARCore's OpenGL coordinates to the COLMAP/Nerfstudio convention; (3) a cloud-GPU reconstruction pipeline that performs COLMAP Structure-from-Motion with Sim3 alignment to ARCore's metric frame, followed by Nerfstudio splatfacto 3D Gaussian Splatting training; (4) a structural layer that extracts wall planes, corners, wall lengths and doors from the model as the basis for floor plans and 1:1 measurement (prototype built); and (5) a planned web-based viewer for metric measurement and model inspection.

rewrite:


---

### CHUNK 002
- **file:** chapters/04_abstract.tex
- **section:** Abstract
- **lines:** 9-9
- **words:** 127

original:

At mid-evaluation, Iteration 1 stands at core pipeline complete, refinement ongoing: the Android capture app records all required sensor data with live quality and coverage guidance; the FastAPI processing server accepts uploads and dispatches jobs to on-demand RunPod GPU pods; and the current best reconstruction (v6) scores 26.52 dB PSNR / 0.8886 SSIM on 42 held-out frames, and tape-measure checks show a mean measurement error of 4.8 mm (0.19%), worst case 0.29%, against a 5% accuracy target. Key technical challenges solved include IMU-bridged tracking-gap recovery, lens self-calibration via COLMAP, and diagnosis and correction of degenerate Gaussian splat geometry. The open items are 3DGS refinement, 3D mesh creation, completion of the structural layer, and the web workspace (including floor plans and 1:1 measurement), followed by end-to-end field validation.

rewrite:


---

## 06_executive_summary.tex

### CHUNK 003
- **file:** chapters/06_executive_summary.tex
- **section:** Executive Summary; Executive Summary — Problem; Executive Summary — Research; Executive Summary — Solution
- **lines:** 5-11
- **words:** 194

original:

BuildScan 3D is a mobile-to-cloud system that converts a short smartphone video of an indoor space into a photorealistic, metric-scale 3D model suitable for measurements, facility documentation, and construction progress tracking.

Professional 3D scanning of indoor spaces requires expensive LiDAR equipment ($10,000+) or photogrammetry workflows that demand expert knowledge and hours of manual processing. Small construction firms, facility managers, and architectural students lack access to affordable, automated tools that produce models accurate enough for real-world measurements.

We reviewed the 3D Gaussian Splatting literature [cite: kerbl3dgs], on-device reconstruction (PocketGS [cite: pocketgs]), and visual-inertial SLAM approaches (VIGS-SLAM [cite: vigsslam]). The key gap we identified is that no existing system combines smartphone ARCore capture with cloud-GPU 3DGS processing to deliver metric-scale models with sub-centimetre measurement accuracy in a fully automated pipeline.

Our five-stage pipeline: (1) an Android app captures video, ARCore poses, depth and IMU data at 30 FPS with live quality guidance; (2) pose conversion and coordinate alignment; (3) cloud GPU processing via COLMAP SfM and Nerfstudio splatfacto 3DGS; (4) a structural layer (wall planes, corners, wall lengths, door detection) for floor plans and 1:1 measurement, prototype built; (5) planned Three.js web viewer with metric measurements.

rewrite:


---

### CHUNK 004
- **file:** chapters/06_executive_summary.tex
- **section:** Executive Summary — Current status (Iteration 1: core pipeline complete, refinement ongoing)
- **lines:** 13-13
- **words:** 162

original:

The Android capture app records all required sensor data with live image-quality assessment and coverage guidance (red/yellow/green dot overlay). The FastAPI processing server accepts uploads and dispatches jobs to on-demand RunPod GPU pods (NVIDIA RTX 4090 by default, selectable at runtime), with automatic pod termination on completion or failure. End-to-end processing has been measured at about 75 minutes on the development RTX 3070; no cloud-GPU timing has been measured yet, and the under-35-minute RTX 4090 figure is an FYP-2 projection. The current best reconstruction (v6) scores 26.52 dB PSNR / 0.8886 SSIM on 42 held-out frames that no model was trained on. Tape-measure checks show a mean error of 4.8 mm (0.19%) and a worst case of 0.29% (8 mm over a 2.8 m wall), far inside the 5% accuracy target. CI/CD via GitHub Actions validates Python code, Android builds, and web UI on every push. Open items: 3DGS refinement, 3D mesh creation, completion of the structural layer, and the web workspace.

rewrite:


---

### CHUNK 005
- **file:** chapters/06_executive_summary.tex
- **section:** Executive Summary — Risks; Executive Summary — FYP-2 plan
- **lines:** 15-17
- **words:** 95

original:

Cloud GPU availability and per-job cost (not yet measured); structural-layer robustness across rooms (ceiling-height detection is not yet reliable); measurement accuracy validation across diverse room geometries; the unmeasured RTX 4090 processing time. The full risk register has twelve entries with likelihood, impact, mitigation and owner.

Complete the structural layer and automatic floor plans (Stage 4), build the web measurement workspace (Stage 5), conduct field trials on more rooms, and validate measurement accuracy against tape-measure ground truth across multiple rooms. 3D mesh creation is also in scope as planned work; it has not yet been scheduled.

rewrite:


---

## chapter1_introduction.tex

### CHUNK 006
- **file:** chapters/chapter1_introduction.tex
- **section:** Project Overview
- **lines:** 4-6
- **words:** 70

original:

BuildScan 3D is an end-to-end system that enables non-expert users to create photorealistic, metric-scale 3D models of indoor spaces using only a commodity Android smartphone. The user records a short walk-through video; the system automatically uploads the captured data to a cloud GPU, reconstructs a 3D Gaussian Splatting model, and returns a viewable, measurable digital twin of the scanned space.

It targets construction site documentation, facility management and architectural surveying.

rewrite:


---

### CHUNK 007
- **file:** chapters/chapter1_introduction.tex
- **section:** Problem Statement
- **lines:** 9-9
- **words:** 81

original:

Capturing accurate, metric-scale 3D models of indoor environments currently requires either (a) LiDAR hardware costing $10,000 or more, (b) photogrammetry workflows requiring expert knowledge and hours of manual post-processing, or (c) consumer-grade scanning apps (e.g. Polycam, Luma AI) that produce visually plausible but metrically inaccurate models unsuitable for measurement. There is no affordable, fully automated pipeline that turns a smartphone video into a metrically accurate 3D model with sufficient quality for professional use. Section [ref: sec:gaps] examines these gaps in detail.

rewrite:


---

### CHUNK 008
- **file:** chapters/chapter1_introduction.tex
- **section:** Problem Context and Motivation
- **lines:** 12-14
- **words:** 111

original:

Construction and facility management lose time and money to rework caused by inaccurate or outdated spatial documentation. Small firms and site teams need quick, accurate as-built captures for routine inspections. Modern smartphones carry high-resolution cameras, IMUs, and AR-capable processors (via Google ARCore), making them potential 3D capture devices—if the software pipeline can bridge the accuracy gap between consumer AR and professional surveying.

Recent advances in 3D Gaussian Splatting [cite: kerbl3dgs] enable photorealistic novel-view synthesis at real-time frame rates from posed images, while ARCore provides metric-scale camera poses and depth sensing on Android devices. Combining these technologies with cloud GPU processing creates an opportunity for a fully automated, affordable indoor scanning solution.

rewrite:


---

### CHUNK 009
- **file:** chapters/chapter1_introduction.tex
- **section:** Project Vision
- **lines:** 17-17
- **words:** 75

original:

BuildScan 3D aims to democratize indoor 3D scanning by making it as simple as recording a video on a phone. The system will: (1) guide the user during capture to ensure sufficient coverage and quality; (2) automatically process the recording on a cloud GPU; (3) return a metric-scale 3D model with measurement tools; and (4) extract the room's structure—wall planes, corners, wall lengths and doors—as the basis for automatic floor plans and 1:1 metric measurement.

rewrite:


---

### CHUNK 010
- **file:** chapters/chapter1_introduction.tex
- **section:** Project Objectives
- **lines:** 21-26
- **words:** 123

original:

Develop an Android capture application that records video, ARCore poses, depth maps, and IMU data with live image-quality feedback.

Build an automated cloud-GPU processing pipeline that converts a phone recording into a 3D Gaussian Splatting model, targeting under 35 minutes end-to-end on a cloud RTX 4090 (a projection; the measured time today is 75 minutes on the development RTX 3070).

Achieve metric-scale accuracy within 5% of tape-measure ground truth for distances measured in the model.

Achieve held-out PSNR >= 25 dB for photometric reconstruction quality.

Build a structural layer that extracts wall planes, corners, wall lengths and doors from the reconstructed model, as the basis for automatic floor plans and 1:1 metric measurement.

Build a web-based 3D viewer with point-to-point metric measurement tools.

rewrite:


---

### CHUNK 011
- **file:** chapters/chapter1_introduction.tex
- **section:** Project Scope — In scope; Project Scope — Out of scope
- **lines:** 33-43
- **words:** 100

original:

Android capture application with ARCore integration, live IQA, and coverage guidance.

Automated reconstruction pipeline: keyframe extraction, COLMAP SfM, Sim3 metric alignment, splatfacto 3DGS training.

FastAPI processing server with local and cloud GPU (RunPod) execution modes.

Metric measurement capability in the 3D model.

Structural layer: automatic wall planes, corners, wall lengths, door detection and floor plans (prototype built in FYP-1; completion in FYP-2).

Three.js/WebGPU web viewer for model inspection and measurement (FYP-2).

3D mesh creation from the reconstructed model (planned; not yet scheduled).

CI/CD pipeline via GitHub Actions.

outdoor environments and building-wide scans, iOS (ARKit), real-time on-device reconstruction, and BIM export.

rewrite:


---

### CHUNK 012
- **file:** chapters/chapter1_introduction.tex
- **section:** Project Modules
- **lines:** 47-52
- **words:** 136

original:

Mobile Capture Module: Android app using ARCore for video recording, camera pose tracking, depth sensing, IMU telemetry, and live quality/coverage guidance.

Pose Prior Module: Coordinate alignment from ARCore's OpenGL convention to COLMAP/Nerfstudio, quaternion-to-rotation-matrix conversion, and Sim3 metric alignment.

Reconstruction Pipeline Module: COLMAP SfM (feature extraction, matching, mapping, undistortion), lens self-calibration, and Nerfstudio splatfacto 3DGS training.

Processing Server Module: FastAPI backend for dataset upload, job management, progress tracking, and cloud GPU dispatch via RunPod API.

Structural Layer Module: Rebuilds the room shell next to the splat model (structure.py): floor and wall planes, corners, wall lengths, doors and other openings, and the floor polygon used for floor plans and 1:1 measurement. Prototype built; completion in FYP-2.

Web Viewer Module (FYP-2): Three.js/WebGPU-based viewer with splat rendering, point-to-point 1:1 measurement that can snap to structural-layer walls, and a floor-plan view.

rewrite:


---

### CHUNK 013
- **file:** chapters/chapter1_introduction.tex
- **section:** Stakeholders and User Classes
- **lines:** 56-56
- **words:** 53

original:

The primary users are construction site managers, facility maintenance teams and architectural survey teams who need quick as-built documentation. Secondary users are architecture and civil engineering students, and real estate professionals documenting properties. Administrators operate the cloud GPU resources and monitor processing jobs. The supervisor, Mr. Furqan Nasir, provides academic evaluation and guidance.

rewrite:


---

### CHUNK 014
- **file:** chapters/chapter1_introduction.tex
- **section:** Success Criteria
- **lines:** 61-65
- **words:** 104

original:

Metric accuracy: distances measured in the model within 5% of tape-measure ground truth (measured so far: mean 0.19%, worst case 0.29%).

Reconstruction quality: held-out PSNR >= 25 dB, SSIM >= 0.85.

Processing time: under 35 minutes end-to-end from upload to viewable model on an NVIDIA RTX 4090 cloud GPU (FYP-2 target, projected and not yet measured; currently 75 minutes on the development RTX 3070).

Capture guidance: live IQA reduces user-caused quality failures by >=50% compared to unguided capture.

Structural layer: wall planes, wall lengths and doors extracted automatically, with wall lengths within the 5% accuracy target (FYP-2; not yet verified against a tape measure).

rewrite:


---

### CHUNK 015
- **file:** chapters/chapter1_introduction.tex
- **section:** Constraints and Assumptions
- **lines:** 69-69
- **words:** 76

original:

The phone must support ARCore (Google's AR compatibility list); all results in this report come from a commodity Android phone (realme) with no LiDAR or other special hardware. Cloud processing needs internet connectivity and a RunPod account. The scanned space must be a single room or a connected set of rooms (not a full building), lit well enough for ARCore to keep tracking, and the current pipeline targets rooms up to about 10 × 10 m.

rewrite:


---

### CHUNK 016
- **file:** chapters/chapter1_introduction.tex
- **section:** Ethical, Legal and DEI Considerations
- **lines:** 73-76
- **words:** 123

original:

Privacy: The captured video may include personally identifiable spaces. All data is processed on the user's own cloud account; no data is shared with third parties. The system does not store or transmit video beyond what is needed for processing.

Accessibility: The capture app provides visual quality feedback (colour-coded overlay) and haptic feedback (vibration on quality degradation) to assist users with varying levels of technical expertise.

Environmental: Cloud GPU pods are terminated immediately after processing to minimize unnecessary compute resource usage and associated energy consumption.

Tool disclosure: GenAI tools (Claude Code, GitHub Copilot, ChatGPT) were used for code generation assistance, debugging, documentation and report drafting, including the correction pass on this report. Full disclosure is provided in Chapter [ref: ch:evidence], Table [ref: tab:aitools].

rewrite:


---

## chapter2_research.tex

### CHUNK 017
- **file:** chapters/chapter2_research.tex
- **section:** Research Method / Approach
- **lines:** 4-4
- **words:** 62

original:

Our research followed a structured literature review combined with empirical experimentation. We surveyed recent publications (2023–2025) in 3D Gaussian Splatting, on-device 3D reconstruction, and visual-inertial SLAM, focusing on methods that operate on monocular or smartphone-captured video. We then implemented and benchmarked candidate approaches on our own ARCore-captured datasets to validate claims and identify practical limitations. Key papers are archived in docs/Research Papers/.

rewrite:


---

### CHUNK 018
- **file:** chapters/chapter2_research.tex
- **section:** Existing Solutions / Products — Commercial products; Existing Solutions / Products — Research systems
- **lines:** 10-21
- **words:** 186

original:

Matterport Pro3: Professional LiDAR scanner ($6,000+). Produces accurate metric models but requires dedicated hardware and per-scan cloud processing fees.

Polycam: Smartphone app using LiDAR (iPhone Pro) or photogrammetry. Fast capture but limited metric accuracy on non-LiDAR devices; no automated cloud processing pipeline.

Luma AI: Consumer 3DGS from video. Visually impressive but provides no metric scale and no measurement tools.

RealityCapture: Professional photogrammetry software. High-quality output but requires expert operation, manual photo capture, and desktop GPU processing.

3D Gaussian Splatting [cite: kerbl3dgs]: Kerbl et al. (2023) introduced real-time radiance field rendering using anisotropic 3D Gaussians, achieving state-of-the-art novel-view synthesis quality. Requires pre-computed SfM poses; no built-in capture guidance or metric scale.

PocketGS [cite: pocketgs]: On-device 3DGS training on a smartphone. Demonstrates that dense multi-view stereo initialization produces better geometry than sparse SfM points alone. Limited to short sequences and small scenes.

VIGS-SLAM [cite: vigsslam]: Visual-inertial Gaussian splatting SLAM. Real-time tracking and mapping but requires custom hardware integration and is not available as a turnkey system.

PGSR [cite: pgsr]: Planar-based Gaussian Splatting for surface reconstruction. Improves geometric flatness of walls/floors but sacrifices reflective surface quality (glossy floors, mirrors).

rewrite:


---

### CHUNK 019
- **file:** chapters/chapter2_research.tex
- **section:** Limitations and Gaps
- **lines:** 48-54
- **words:** 137

original:

The key limitations of existing solutions that motivate our work are:

Cost barrier: Professional solutions (Matterport, RealityCapture) require expensive hardware or software licenses.

No metric scale from video: Consumer apps (Luma AI) and research methods (3DGS, PocketGS) produce visually plausible models but without metric scale, making measurements impossible.

No capture guidance: No existing system provides real-time feedback on image quality, tracking state, and spatial coverage during capture, leading to frequent quality failures.

Manual pipeline: Research pipelines require manual steps (photo selection, COLMAP setup, training configuration) that non-experts cannot perform.

No structure from a plain video: Consumer 3DGS apps and research methods produce a radiance field but no explicit room structure (wall planes, wall lengths, doors) from which a floor plan or reliable measurement can be taken; where floor plans exist, they depend on LiDAR or dedicated hardware.

rewrite:


---

### CHUNK 020
- **file:** chapters/chapter2_research.tex
- **section:** Proposed Solution
- **lines:** 58-64
- **words:** 126

original:

BuildScan 3D bridges these gaps by combining:

ARCore for metric scale: The phone's visual-inertial odometry provides metric-scale poses that are refined via COLMAP SfM and aligned through a Sim3 transform, giving the 3D model real-world dimensions.

Live capture guidance: Real-time image quality assessment (blur, exposure, motion speed) and spatial coverage visualization (voxel-based direction-aware coverage map) reduce capture failures.

Fully automated cloud pipeline: A FastAPI server handles upload, dispatches processing to a RunPod GPU pod, monitors progress, and delivers the finished model—no manual steps.

State-of-the-art rendering: Nerfstudio splatfacto 3DGS produces photorealistic models that render at real-time frame rates.

Structural layer: wall planes, corners, wall lengths and doors extracted automatically from the splat model (structure.py, prototype), as the basis for floor plans and 1:1 measurement; completion in FYP-2.

rewrite:


---

### CHUNK 021
- **file:** chapters/chapter2_research.tex
- **section:** Complex Computing Problem
- **lines:** 68-75
- **words:** 106

original:

The core complex computing problem is: How can a sequence of monocular smartphone video frames, with noisy ARCore poses and sparse depth measurements, be automatically converted into a geometrically accurate, metrically scaled 3D Gaussian Splatting model that supports reliable real-world measurements?

This involves:

Robust Structure-from-Motion on casually captured, motion-blurred video with tracking gaps and silent ARCore re-anchoring events.

Metric alignment between COLMAP's arbitrary-scale coordinate system and ARCore's metric frame via a Sim3 similarity transform with outlier rejection.

Correct initialization of 3D Gaussians from multi-view stereo points to avoid degenerate geometry (zero-thickness splats, opacity collapse).

Per-step GPU resource management with timeout watchdogs to prevent unbounded cloud billing.

rewrite:


---

### CHUNK 022
- **file:** chapters/chapter2_research.tex
- **section:** Technical Challenges
- **lines:** 80-86
- **words:** 177

original:

ARCore silent re-anchoring: ARCore silently corrects its world frame during SLAM loop closures, causing pose discontinuities of up to 1 m / 28°. On our first room every pose before 60 s was off by about 1 m and 28°, so part of the room appeared twice. Solved by taking training poses from image-based COLMAP SfM, which does not depend on ARCore's world frame; the app now also logs ARCore anchors so that re-anchors are directly detectable. Genuine tracking losses are bridged with the IMU (fallback.py).

Lens distortion: ARCore's reported camera intrinsics lack lens distortion coefficients. COLMAP's self-calibration recovers radial distortion (k_1 ≈ 0.09, k_2 ≈ -0.22), which is essential for sub-pixel SfM accuracy.

Degenerate Gaussian splats: Our initial training recipe produced zero-thickness, half-transparent splats (“cotton texture”) due to a flattening regularizer interacting pathologically with Adam's gradient normalization. Root-cause analysis (documented in Training_Analysis.md) led to adopting Nerfstudio splatfacto with measured-point initialization.

Plain/textureless surfaces: Rooms with plain white walls and ceilings cause tracking losses and produce inconsistent depth estimates. Solved via texture-aware IQA warnings and ceiling/floor capture guidance.

rewrite:


---

### CHUNK 023
- **file:** chapters/chapter2_research.tex
- **section:** Technical Challenges
- **lines:** 88-88
- **words:** 41

original:

GPU memory constraints: The RTX 3070 (8 GB VRAM) limits splat count to approximately 3 million at full resolution. Addressed by training on a 24 GB cloud GPU (RTX 4090 via RunPod) and optimizing memory usage (images in pinned CPU RAM).

rewrite:


---

### CHUNK 024
- **file:** chapters/chapter2_research.tex
- **section:** Research Findings and Design Decisions
- **lines:** 92-97
- **words:** 168

original:

Key research findings that shaped our design:

SfM poses outperform ARCore poses for 3DGS: Raw ARCore poses have a 2.32 px median reprojection error; bundle adjustment reduces it to 0.62 px (626k observations), but cannot remove ARCore's silent 1 m / 28° re-anchor or its missing lens model. Switching to image-based COLMAP poses with lens self-calibration raised the training-view fit from 21.9 dB (12–30 px misaligned) to 28 dB (2–3 px), raised held-out SSIM from 0.78 to 0.86 (0.91 on a second room), and cut badly placed surfaces from 7–23% to 3% (1% on the second room). For reference, the best model trained on the earlier poses was our own trainer with COLMAP depth (gs_colmap_nc, 22.67 dB / 0.782 held-out). Decision: Use COLMAP SfM for training poses; ARCore provides metric scale via Sim3 alignment.

Dense initialization is critical: PocketGS [cite: pocketgs] demonstrated that dense multi-view stereo points (vs. sparse SfM points) significantly improve reconstruction quality (SSIM 0.834 vs. 0.791). Decision: Initialize from MVS-measured points voxel-downsampled at 1 cm.

rewrite:


---

### CHUNK 025
- **file:** chapters/chapter2_research.tex
- **section:** Research Findings and Design Decisions
- **lines:** 99-101
- **words:** 110

original:

Regularization can be harmful: Our flattening loss, depth loss, and pose refinement each degraded quality when applied together. The plain splatfacto recipe (photometric loss only, fixed poses) outperformed every combination. In a separate comparison on a different scene (roomAttemptSadness2), splatfacto on our preprocessed inputs reached 27.81 dB held-out (28.08 dB on training views), against 24.70 dB held-out for our own trainer with the corrected recipe. Decision: Use standard splatfacto; keep custom preprocessing.

Gyro-aware frame selection improves sharpness: Selecting frames by predicted motion blur (from IMU angular velocity and exposure time) instead of texture content improved PSNR by 0.26 dB. Decision: Implemented select_sharp.py using per-frame exposure metadata logged by the app.

rewrite:


---

### CHUNK 026
- **file:** chapters/chapter2_research.tex
- **section:** Techniques Explored and Parked
- **lines:** 106-106
- **words:** 68

original:

Before the switch to image-based poses, the team tried a series of techniques to fix blurry, “cotton-like” models with floating splats. None of them fixed the underlying problem (ARCore's silent re-anchor and missing lens model; finding 1 above); the best model of that period reached only 22.67 dB / 0.782 on held-out frames. They are recorded here so that every technique attempted is visible. Numbers are from docs/progress/.

rewrite:


---

## chapter3_iteration_plan.tex

### CHUNK 027
- **file:** chapters/chapter3_iteration_plan.tex
- **section:** Proposal Feedback Summary
- **lines:** 4-4
- **words:** 63

original:

At the proposal defense the panel asked the team to distinguish BuildScan 3D from consumer scanning apps (Polycam, Luma AI), to demonstrate metric accuracy against ground-truth measurements, to define clear acceptance criteria for reconstruction quality, and to focus on measurement accuracy and the automated pipeline rather than a feature-rich UI. Each point and the action taken is recorded in the action register below.

rewrite:


---

### CHUNK 028
- **file:** chapters/chapter3_iteration_plan.tex
- **section:** Proposal Action Register
- **lines:** 8-8
- **words:** 18

original:

Table [ref: tab:actionregister] records the feedback received at the proposal defense and the action taken on each point.

rewrite:


---

### CHUNK 029
- **file:** chapters/chapter3_iteration_plan.tex
- **section:** Iteration Strategy
- **lines:** 31-35
- **words:** 83

original:

We follow a two-iteration strategy aligned with FYP-1 and FYP-2:

Iteration 1 (FYP-1, Weeks 1–8): Core model implementation—capture app, reconstruction pipeline, processing server, cloud GPU integration, validated on real recordings. Status at mid-evaluation: core pipeline complete, refinement ongoing. Deliverables: working Android APK, FastAPI server, RunPod integration, metric-accurate 3D reconstruction.

Iteration 2 (FYP-2, Weeks 9–16): Optimization, performance tuning, and feature enrichment. Deliverables: reduced processing time, pipeline robustness improvements, Three.js web viewer with measurement tools, structural layer and floor plans, field validation on multiple rooms.

rewrite:


---

### CHUNK 030
- **file:** chapters/chapter3_iteration_plan.tex
- **section:** Iteration 1 Plan
- **lines:** 40-43
- **words:** 65

original:

Objective: Build the end-to-end pipeline from phone capture to 3D model.

Features: ARCore capture with IQA + coverage overlay; COLMAP SfM + splatfacto training; FastAPI server with RunPod dispatch; upload UI in the Android app.

Deliverables: Working Android APK, processing server, cloud GPU integration, reconstruction quality validation on two rooms.

Evidence: Live demo of phone capture → upload → cloud processing → 3D model viewing.

rewrite:


---

### CHUNK 031
- **file:** chapters/chapter3_iteration_plan.tex
- **section:** Iteration 2 Plan
- **lines:** 48-51
- **words:** 88

original:

Objective: Optimize processing time, improve pipeline robustness, complete the structural layer and add measurement tools.

Features: pipeline optimization (target <35 min on RTX 4090, projected, from 75 min measured on RTX 3070), edge-case robustness, the web viewer with wall-snapping measurement, and structural layer completion; modules and schedule in Chapter [ref: ch:plan].

Deliverables: Optimized pipeline with reduced processing time, web viewer with measurement tools, structural layer with floor-plan export, field validation report across >=5 rooms.

Evidence: Processing time benchmarks; measurement accuracy comparison with tape-measure ground truth across >=5 rooms.

rewrite:


---

### CHUNK 032
- **file:** chapters/chapter3_iteration_plan.tex
- **section:** Progress Against Plan
- **lines:** 83-89
- **words:** 89

original:

The core-pipeline milestones of Iteration 1 have been met; refinement is ongoing:

Week 1–2: ARCore capture app with basic recording → Completed.

Week 3–4: COLMAP SfM pipeline with ARCore Sim3 alignment → Completed. Also resolved root causes of poor reconstruction quality (tracking gaps, lens distortion, degenerate splats).

Week 5–6: Live IQA, coverage overlay, quality improvements (gyro-aware frame selection, MVS initialization) → Completed.

Week 7–8: Processing server, RunPod integration, upload UI, CI/CD → Completed.

Open items: 3DGS refinement, 3D mesh creation, completion of the structural layer, and the web workspace.

rewrite:


---

### CHUNK 033
- **file:** chapters/chapter3_iteration_plan.tex
- **section:** Delays, Deviations and Recovery Plan
- **lines:** 94-95
- **words:** 109

original:

Deviation: We initially built a custom training script (train.py) with depth supervision, flattening regularization, and pose refinement. After extensive analysis (documented in Training_Analysis.md), we found this produced worse results than standard splatfacto. We pivoted to using splatfacto for training and keeping our custom preprocessing. This analysis consumed approximately 2 weeks but resulted in a better-informed design decision.

Recovery: The core pipeline is in place, but Iteration 1 is not finished: the open items listed above remain. FYP-2 therefore starts with the one-command v6 pipeline and the processing-time reduction, and schedules the structural layer and web workspace in Iterations 2a–2b. 3D mesh creation is in scope but not yet scheduled.

rewrite:


---

## chapter4_requirements.tex

### CHUNK 034
- **file:** chapters/chapter4_requirements.tex
- **section:** User Interactions / Use Cases
- **lines:** 4-8
- **words:** 66

original:

The system supports three primary user interactions:

Capture: The user opens the Android app, starts recording, walks through the room while receiving live quality feedback, stops recording, and taps “Upload & Process.”

Monitor: The user watches the processing progress screen showing current step, percentage, elapsed time, and log output.

View/Measure: The user opens the finished 3D model in the web viewer and takes point-to-point measurements (FYP-2).

rewrite:


---

### CHUNK 035
- **file:** chapters/chapter4_requirements.tex
- **section:** Use Case Diagram
- **lines:** 12-12
- **words:** 94

original:

The system involves three actors (Figure [ref: fig:usecase]): the End User (captures and views), the Processing Server (manages jobs), and the Cloud GPU (runs reconstruction). The use cases are Record Scan, Upload Dataset, Monitor Progress, View Model, Take Measurement, and Configure Server. Each maps to code: Record Scan to HelloArActivity and CaptureLogger; Upload Dataset and Monitor Progress to ProcessingActivity and the /upload and /status endpoints of server/main.py; Configure Server to the app's settings menu (server URL) and /config; View Model and Take Measurement to the desktop viewer today and the web workspace in FYP-2.

rewrite:


---

### CHUNK 036
- **file:** chapters/chapter4_requirements.tex
- **section:** Detailed Use Cases — UC-1: Record Indoor Scan; Detailed Use Cases — UC-2: Upload and Process
- **lines:** 55-67
- **words:** 122

original:

Actor: End User

Precondition: App installed on ARCore-compatible Android device

Main flow: User opens app → taps Record → walks through room → receives live IQA feedback (blur, speed, darkness, texture warnings) and coverage overlay (red/yellow/green dots) → taps Stop → sees quality summary

Postcondition: Dataset saved locally (video, poses, depth, quality, meta)

Actor: End User

Precondition: Recording completed; server URL configured

Main flow: User taps “Upload & Process” → app zips depth folder, uploads all files → server creates job, dispatches to GPU → app polls progress every 3 s showing step, percentage, logs → completion or failure reported

Postcondition: 3D model (splat.ply) available for download

Exception: Upload fails → retry button; pipeline step fails → error message with step name

rewrite:


---

### CHUNK 037
- **file:** chapters/chapter4_requirements.tex
- **section:** Functional Requirements
- **lines:** 71-71
- **words:** 36

original:

Table [ref: tab:fr] lists the functional requirements by module. Each has a priority, a status, a verifiable acceptance check, and its trace to the implementing file and the test case (Chapter [ref: ch:testing]) that checks it.

rewrite:


---

### CHUNK 038
- **file:** chapters/chapter4_requirements.tex
- **section:** Non-Functional Requirements
- **lines:** 113-113
- **words:** 27

original:

Table [ref: tab:nfr] lists the non-functional requirements with their measurement method and current status. Several are not yet measured; they are marked as such rather than assumed.

rewrite:


---

### CHUNK 039
- **file:** chapters/chapter4_requirements.tex
- **section:** Acceptance Criteria
- **lines:** 141-141
- **words:** 56

original:

The acceptance check of every requirement is in Tables [ref: tab:fr] and [ref: tab:nfr]. The project-level acceptance thresholds are: held-out PSNR >= 25 dB and SSIM >= 0.85 (FR-P4; met by v6), distances within 5% of tape measure (FR-P3; met, worst case 0.29%), and processing under 35 min on an RTX 4090 (NFR-P1; not yet measured).

rewrite:


---

## chapter5_design.tex

### CHUNK 040
- **file:** chapters/chapter5_design.tex
- **section:** System Architecture
- **lines:** 4-12
- **words:** 119

original:

BuildScan 3D uses a three-tier client-server architecture:

Client tier: Android application (ARCore capture, upload, progress display).

Server tier: FastAPI backend (job management, pipeline orchestration, RunPod dispatch).

Compute tier: GPU processing (local or RunPod on-demand pod running COLMAP + Nerfstudio).

The data flow is strictly sequential: Capture → Upload → Process → Download. The server acts as an orchestrator that manages the GPU lifecycle and provides progress updates to the client via polling. Figure [ref: fig:architecture] shows the components of each tier and how they talk to each other. The server runs in one of four processing modes set through /config: dry_run (the default: uploads are saved, nothing is processed), local, runpod and remote (a fixed GPU host over SSH).

rewrite:


---

### CHUNK 041
- **file:** chapters/chapter5_design.tex
- **section:** Architectural Components — Android App (googleARCore/samples/hello_ar_java/)
- **lines:** 70-78
- **words:** 76

original:

HelloArActivity: Main AR camera activity with recording controls, settings menu, and quality overlay.

CaptureLogger: Background I/O thread writing poses, tracking, points, quality, depth, and metadata files.

QualityMonitor: Analyzes camera frames for blur, brightness, motion speed, and texture.

CoverageMap: Voxel-based (10 cm) coverage tracker with 8-azimuth × 2-elevation direction awareness.

CoverageOverlayView: Renders red/yellow/green dots over the camera view.

ProcessingActivity: Upload + progress UI with OkHttp multipart client.

Figure [ref: fig:androidarch] shows how these classes and screens connect.

rewrite:


---

### CHUNK 042
- **file:** chapters/chapter5_design.tex
- **section:** Architectural Components — Processing Server (server/); Architectural Components — Reconstruction Pipeline (src/arcore3dgs/)
- **lines:** 116-129
- **words:** 130

original:

main.py: FastAPI endpoints—/upload, /status/job_id, /jobs, /logs/job_id, /retry/job_id, /jobs/job_id/cancel, /download/job_id, /config, /gpus, /datasets, /reprocess, /run-on-pod, /health.

pipeline.py: Local pipeline runner with Job dataclass, StepConfig per-step timeouts, and subprocess execution with streaming stdout.

runpod_client.py: RunPod API client (GraphQL pod creation, SSH/SCP helpers, remote pipeline execution, pod watchdog, pod termination in finally blocks).

fallback.py: IMU-bridged tracking-gap recovery.

prepare.py: Keyframe extraction from video (sharpest frame by Laplacian variance in each window of 8 frames).

select_sharp.py: Gyro-aware keyframe selection (least predicted motion blur per 0.2 s window). Used for the v4–v6 models; not yet part of the one-command pipeline.

sfm_colmap.py: COLMAP SIFT matching + global mapper + lens self-calibration + Sim3 alignment to ARCore metric frame.

export_nerfstudio.py: Convert COLMAP output to Nerfstudio data format.

Nerfstudio ns-train splatfacto: 3DGS training (30k iterations).

Nerfstudio ns-export: Export splat.ply.

rewrite:


---

### CHUNK 043
- **file:** chapters/chapter5_design.tex
- **section:** Interfaces and Dependencies — External dependencies
- **lines:** 153-153
- **words:** 29

original:

Google ARCore SDK (Android), COLMAP 4.2 (SfM/MVS), Nerfstudio 1.1.5 (3DGS training), OkHttp 4.12.0 (Android HTTP client), FastAPI + Uvicorn (Python web framework) and the RunPod API (cloud GPU provisioning).

rewrite:


---

### CHUNK 044
- **file:** chapters/chapter5_design.tex
- **section:** Architecture Decisions and Rationale
- **lines:** 158-162
- **words:** 191

original:

COLMAP SfM over ARCore poses for training: Raw ARCore poses have a 2.32 px median reprojection error (slow drift); bundle adjustment reduces this to 0.62 px, but ARCore also re-anchors silently (every pose before 60 s was off by 1 m and 28°) and reports no lens distortion. COLMAP's SfM with self-calibrated lens distortion (k_1 ≈ 0.09, k_2 ≈ -0.22) removes both. On the same recording, training-view fit rose from 21.9 dB to 28 dB, held-out SSIM from 0.78 to 0.86, and badly placed surfaces fell from 7–23% to 3%.

Splatfacto over custom trainer: After extensive analysis showing our custom training recipe produced degenerate splats, we adopted Nerfstudio's battle-tested splatfacto implementation. On a separate scene (roomAttemptSadness2), splatfacto reached 27.81 dB held-out against 24.70 dB for our corrected custom trainer on the same inputs. Our value-add is in the preprocessing (ARCore integration, metric alignment, IMU fallback, quality guidance).

RunPod on-demand over serverless: On-demand pods allow full SSH control of the pipeline, suit long-running jobs (about 75 min end-to-end measured on an RTX 3070), and support arbitrary software installation. Serverless endpoints have cold-start latency and timeout limits that conflict with COLMAP's variable runtime.

rewrite:


---

### CHUNK 045
- **file:** chapters/chapter5_design.tex
- **section:** Architecture Decisions and Rationale
- **lines:** 164-164
- **words:** 21

original:

HTTP polling over WebSockets: Simpler implementation, works across firewalls/proxies, and 3-second polling interval is sufficient for a pipeline that takes minutes.

rewrite:


---

### CHUNK 046
- **file:** chapters/chapter5_design.tex
- **section:** Design Evolution
- **lines:** 169-173
- **words:** 123

original:

Proposal → Mid: Added live IQA and coverage guidance (not in original proposal). Changed from ARCore-pose-based training to COLMAP SfM-based training after discovering ARCore's pose accuracy limitations. On the way, the team's own GPU bundle adjustment, Metric3D depth, own stereo matcher, depth supervision, floater pruning, median filtering and post-hoc flat-forcing were tried and parked (Section [ref: sec:parked]).

Custom trainer → splatfacto: After two weeks of analysis documenting six root causes of degenerate splat geometry, we switched training to Nerfstudio splatfacto. The custom preprocessing pipeline was retained and validated.

Local-only → local + cloud: Added RunPod cloud GPU support to enable processing on machines without a GPU, and to support faster GPUs (RTX 4090 by default) than the development machine (RTX 3070, 8 GB).

rewrite:


---

### CHUNK 047
- **file:** chapters/chapter5_design.tex
- **section:** Domain Model
- **lines:** 177-183
- **words:** 69

original:

The core domain entities are:

Scan: A recording session producing a dataset (video + sensor files).

Dataset: The collection of files from one scan (video, poses, depth, quality, meta).

Job: A processing task with status (queued, processing, completed, failed), progress, and output path. Its life cycle is shown in Figure [ref: fig:jobstate].

Model: The output 3D Gaussian Splatting model (splat.ply).

Measurement: A point-to-point distance in the metric model (FYP-2).

rewrite:


---

### CHUNK 048
- **file:** chapters/chapter5_design.tex
- **section:** Data Design — Capture data (per scan); Data Design — Pipeline intermediate data
- **lines:** 214-232
- **words:** 141

original:

dataset.mp4: H.264 video, 1920×1080, 30 FPS.

poses.csv: timestamp, tx, ty, tz, qx, qy, qz, qw, fx, fy, cx, cy (per frame).

tracking.csv: timestamp, tracking_state, failure_reason (per frame).

points.csv: timestamp, point_id, x, y, z, confidence (ARCore feature points).

quality.csv: timestamp, sharpness, brightness, motion_speed, texture_level (per analyzed frame).

depth/: uint16 depth maps (mm) + uint8 confidence maps at 5 Hz.

meta.json: device model, camera config, resolution, ARCore version.

poses_fused.csv, fallback_report.json: poses with tracking gaps bridged by the IMU.

work/images/, work/frames.json: extracted keyframes (JPEG) and their ARCore poses.

work_sfm/: COLMAP database, sparse model, undistorted images, Sim3-aligned frames.json, init_points.ply.

work_sfm/transforms.json: Nerfstudio-format camera transforms.

work_sfm/gs_sfm/splat.ply: Final 3DGS model.

Figure [ref: fig:dataflow] traces the capture files through the six pipeline steps. quality.csv, meta.json and depth/ are uploaded and stored with the dataset, but the current six steps do not read them (keyframe extraction runs with –depth 0).

rewrite:


---

### CHUNK 049
- **file:** chapters/chapter5_design.tex
- **section:** Process / Behavior Design
- **lines:** 283-294
- **words:** 150

original:

The end-to-end pipeline follows a sequential six-step process:

Fallback (2 min timeout): Read the gyroscope and accelerometer samples stored in dataset.mp4, find tracking gaps in tracking.csv, and bridge them with IMU integration anchored at both ends of each gap.

Prepare (5 min timeout): Decode video, keep the sharpest frame (Laplacian variance) in each window of 8 frames, extract to JPEG (prepare.py). The gyro-aware selection of select_sharp.py that produced v6 is not yet in this step.

SfM (40 min timeout): COLMAP feature extraction (SIFT), exhaustive matching, global mapper, lens self-calibration, image undistortion, Sim3 alignment to ARCore metric frame.

Export (2 min timeout): Convert COLMAP output to Nerfstudio transforms.json format.

Train (60 min timeout): Nerfstudio splatfacto training (30k iterations) with bilateral grid exposure compensation, scale regularization, and fixed poses.

Export Model (5 min timeout): Export trained model to splat.ply.

Figure [ref: fig:pipelinesteps] shows the steps with their timeouts and the measured times.

rewrite:


---

### CHUNK 050
- **file:** chapters/chapter5_design.tex
- **section:** Process / Behavior Design
- **lines:** 327-327
- **words:** 76

original:

Each step is executed as a subprocess with streaming stdout captured for progress reporting. If a step exceeds its timeout, the process is killed and the job is marked failed. In RunPod mode, whenever a pod has been created it is terminated in a finally block regardless of success or failure, and a watchdog thread terminates it after MAX_POD_LIFETIME (default 7200 s). Figure [ref: fig:sequence] shows the upload → process → download interaction in RunPod mode.

rewrite:


---

## chapter6_iteration1.tex

### CHUNK 051
- **file:** chapters/chapter6_iteration1.tex
- **section:** Iteration Objectives
- **lines:** 4-4
- **words:** 28

original:

Build the complete end-to-end pipeline: phone capture → automated upload → cloud GPU reconstruction → metric-scale 3D model. Validate reconstruction quality and metric accuracy on real indoor scans.

rewrite:


---

### CHUNK 052
- **file:** chapters/chapter6_iteration1.tex
- **section:** Selected Use Cases / Features
- **lines:** 7-7
- **words:** 34

original:

UC-1 Record Indoor Scan (with live IQA and coverage guidance), UC-2 Upload and Process (with progress tracking), and UC-3 View the finished model (in the local viewer; the web viewer is deferred to FYP-2).

rewrite:


---

### CHUNK 053
- **file:** chapters/chapter6_iteration1.tex
- **section:** Design
- **lines:** 10-14
- **words:** 66

original:

The Iteration 1 design focused on three subsystems:

Capture subsystem: ARCore session → CaptureLogger (background I/O) → QualityMonitor (frame analysis at 6 FPS) → CoverageMap (depth → voxels → overlay).

Upload subsystem: OkHttp multipart POST → FastAPI /upload → Job creation → Pipeline dispatch (local or RunPod).

Pipeline subsystem: six sequential steps, each with a timeout watchdog, detailed in Section [ref: sec:process] and Figure [ref: fig:pipelinesteps].

rewrite:


---

### CHUNK 054
- **file:** chapters/chapter6_iteration1.tex
- **section:** Implementation
- **lines:** 18-24
- **words:** 100

original:

Implementation was carried out in Java (Android app) and Python (server and pipeline). Key implementation milestones:

Weeks 1–2: Extended the ARCore hello_ar_java sample with CaptureLogger for sensor data recording, verified pose-to-video synchronization (r = 0.76–0.79 at 0.00 s offset).

Weeks 3–4: Built the COLMAP SfM pipeline (sfm_colmap.py), resolved coordinate alignment issues (OpenGL → OpenCV), implemented Sim3 metric alignment, debugged lens distortion.

Weeks 5–6: Diagnosed and fixed degenerate splat geometry (6 root causes documented in Training_Analysis.md), added gyro-aware frame selection, live IQA, and coverage overlay.

Weeks 7–8: Built the FastAPI server, RunPod cloud GPU integration, Android upload UI (ProcessingActivity), CI/CD pipeline.

rewrite:


---

### CHUNK 055
- **file:** chapters/chapter6_iteration1.tex
- **section:** Completed Features / Module — Android Capture App (implemented); Completed Features / Module — Processing Server (implemented)
- **lines:** 30-32
- **words:** 149

original:

30 FPS video recording with per-frame pose, tracking state, feature points, depth, quality metrics and device metadata; per-frame exposure time, rolling-shutter readout and anchor-correction logging. Live IQA shows a colour-coded banner (tracking lost in red, moving too fast in orange; blurry, too dark or low texture in yellow) with a vibration alert, and the coverage overlay draws red (1 direction), yellow (2–3) and green (4+) dots at 2 Hz. Recording ends with a quality summary dialog and an Upload & Process button that opens ProcessingActivity. The server URL is set in the settings menu (persisted in SharedPreferences), and the recording fast-path skips all demo rendering.

The FastAPI endpoints and processing modes of Section [ref: sec:components], switchable at runtime; per-step timeout watchdogs (Figure [ref: fig:pipelinesteps]); RunPod integration with pod creation, SSH readiness polling, dependency installation, SCP upload/download and pod termination; API key loaded from the environment or a .env file.

rewrite:


---

### CHUNK 056
- **file:** chapters/chapter6_iteration1.tex
- **section:** Completed Features / Module — Reconstruction Pipeline (core complete, refinement ongoing); Completed Features / Module — CI/CD (implemented)
- **lines:** 34-36
- **words:** 99

original:

All six steps of Section [ref: sec:process] run end to end: IMU gap bridging, keyframe extraction, COLMAP SfM with lens self-calibration and Sim3 alignment (tape-measure error: mean 0.19%, worst case 0.29%), splatfacto training with bilateral-grid exposure compensation, and export to splat.ply. Gyro-aware frame selection (select_sharp.py, using per-frame exposure metadata) is validated for v4–v6 but not yet in the one-command pipeline, which still uses prepare.py's sharpest frame per window.

GitHub Actions CI (lint, tests on three Python versions, web and APK builds, repository hygiene), CD to build artefacts and releases, and a pull request template; details in Chapter [ref: ch:evidence].

rewrite:


---

### CHUNK 057
- **file:** chapters/chapter6_iteration1.tex
- **section:** Technical Implementation Details — Pose-to-video synchronization (CaptureLogger.java); Technical Implementation Details — Sim3 metric alignment (sfm_colmap.py)
- **lines:** 40-42
- **words:** 141

original:

ARCore's recording API writes video and poses from the same frames, but poses are only logged during TRACKING state, creating gaps. The pipeline interpolates poses at each frame's PTS (linear position, slerp rotation) and skips frames inside tracking gaps > 0.12 s.

COLMAP's global mapper produces an arbitrary-scale coordinate system. We compute a 7-DOF similarity transform (rotation + translation + scale) from matched COLMAP and ARCore camera positions using RANSAC (2,000 four-point samples, 10 cm inlier threshold) followed by a Umeyama refit on the inliers; the inlier median residual is about 2.5 cm. Because ARCore re-anchors silently, only its largest self-consistent segment ends up as inliers. Frames that jump more than 30 cm from their temporal neighbours are dropped as SfM mis-registrations. The resulting metric scale is validated against a tape measure (Table [ref: tab:tape]). Figure [ref: fig:sim3] shows the steps.

rewrite:


---

### CHUNK 058
- **file:** chapters/chapter6_iteration1.tex
- **section:** Technical Implementation Details — Recording fast-path (HelloArActivity.java); Technical Implementation Details — Featureless-tracking fallback (imu.py, fallback.py, relocalize_pnp.py)
- **lines:** 64-66
- **words:** 145

original:

During recording, the onDrawFrame() method exits early after camera feed rendering and quality overlay (at 2 Hz). All plane detection rendering, virtual object placement, PBR lighting, cubemap filtering, and tap handling are skipped, reducing GL thread load significantly.

On plain walls ARCore loses tracking, and after re-tracking it sometimes continues in a shifted or rotated world frame. The fallback reads the gyroscope and accelerometer (201 Hz) stored in ARCore's own recording, self-calibrates the IMU-to-camera rotation and the sensor biases, and bridges each gap: rotation by gyro integration, position by accelerometer integration with a minimal cubic correction that matches position and velocity at both ends. A heading mismatch at re-tracking reveals a new map frame, and the post-gap segment is re-aligned to the map by matching its keyframes against it (PnP). This is the team's main novelty claim. Validation on gaps cut out of tracked data:

rewrite:


---

### CHUNK 059
- **file:** chapters/chapter6_iteration1.tex
- **section:** Technical Implementation Details — Featureless-tracking fallback (imu.py, fallback.py, relocalize_pnp.py); Technical Implementation Details — Structural layer (structure.py, prototype)
- **lines:** 83-85
- **words:** 187

original:

On a real recording, all three heading jumps were detected, and re-alignment cut the error of post-gap frames against earlier frames from 49.7 px to 8.2 px. Limits: IMU-only position is reliable only when both ends of a gap are anchored, and re-alignment needs the user to return to an already mapped area (the app now says so during tracking loss).

The photoreal splat model is not modified. Instead the room shell is rebuilt next to it: the floor plane from the distribution of splat heights; the outermost wall on each side of the two dominant wall directions, each refined individually; corners as intersections of neighbouring walls, giving the floor polygon; per-wall textures as the median over the best views, which removes moving reflections; and openings where the cameras consistently see through a wall plane, classified as doors by their size and position. On the first room it found wall planes of 6.65–6.68 × 4.45–4.48 m and detected 5 doors automatically. Output is structure.json (planes, corners, dimensions, openings), the basis for automatic floor plans and 1:1 measurement. Ceiling-height detection is not yet reliable and is FYP-2 work.

rewrite:


---

### CHUNK 060
- **file:** chapters/chapter6_iteration1.tex
- **section:** Technical Implementation Details — RunPod lifecycle (runpod_client.py)
- **lines:** 87-87
- **words:** 49

original:

The run_pipeline_on_runpod() function wraps the entire pod lifecycle in a try/finally block. Whenever a pod was created, the finally clause calls terminate_pod(), and a watchdog thread enforces a hard time limit, so that that even exceptions, timeouts, or SSH failures do not leave a pod running and accumulating charges.

rewrite:


---

### CHUNK 061
- **file:** chapters/chapter6_iteration1.tex
- **section:** Algorithms and Technical Decisions
- **lines:** 92-99
- **words:** 142

original:

Gyro-aware frame selection: For each 0.2 s window, compute predicted motion blur as blur_px = ω × t_exp × f, where ω is IMU angular velocity (rad/s), t_exp is exposure time, and f is focal length in pixels. Select the frame with minimum predicted blur. This outperforms Laplacian-based sharpness (r = 0.20 correlation with true blur).

Coverage map: Discretize 3D space into 10 cm voxels. For each voxel, track from how many of 16 directions (8 azimuth × 2 elevation) it has been observed. Display as dots: red (1 direction), yellow (2–3), green (4+). Cap processing at 5,000 voxels and 2,000 drawn dots for performance.

Degenerate splat diagnosis: Computed per-model statistics (thickness/width median, opacity histogram, splat count) and compared against reference implementations. Identified flattening regularizer × Adam interaction as the primary cause of zero-thickness splats.

Figure [ref: fig:coverage] illustrates the coverage map.

rewrite:


---

### CHUNK 062
- **file:** chapters/chapter6_iteration1.tex
- **section:** Demonstration Evidence
- **lines:** 170-177
- **words:** 79

original:

The following can be demonstrated live:

Android app: Record a room scan with live IQA feedback and coverage overlay.

Upload flow: Tap “Upload & Process,” watch progress screen update.

Server: Start server with scripts/start_server.bat, show API docs at /docs.

3D model: View the reconstructed splat.ply in the local viewer (scripts/view_splat.bat).

Metric accuracy: Measure the table and a wall in the model and compare with the tape-measure values in Table [ref: tab:tape].

CI/CD: Show GitHub Actions passing on the repository.

rewrite:


---

### CHUNK 063
- **file:** chapters/chapter6_iteration1.tex
- **section:** Contributions and Novelty
- **lines:** 182-188
- **words:** 161

original:

The contributions so far, each backed by measured evidence in this report:

Measured evidence of why commodity ARCore poses fail for 3DGS—a silent 1 m / 28° re-anchor and a missing lens model (k_1 ≈ 0.09, k_2 ≈ -0.22)—and a working fix: image-based poses with ARCore kept for scale and gravity (Table [ref: tab:posefix]).

A featureless-tracking IMU fallback, validated on simulated gaps: 3.8 cm error against 30.6 cm for interpolation over 9 s, and post-gap re-alignment from 49.7 px to 8.2 px (Table [ref: tab:imufallback]).

Live capture-quality guidance and a coverage overlay in the app: warnings for blur, fast motion, darkness and plain surfaces, a vibration alert, and a live overlay of unmapped areas.

Gyro-aware frame selection that measurably improves quality: +0.26 dB / +0.009 SSIM, the largest single gain on the way to v6 (Table [ref: tab:quality]).

Millimetre-level metric accuracy from a phone video, without LiDAR: mean 4.8 mm (0.19%), worst case 0.29% against a tape measure (Table [ref: tab:tape]).

rewrite:


---

### CHUNK 064
- **file:** chapters/chapter6_iteration1.tex
- **section:** Iteration Outcome
- **lines:** 192-206
- **words:** 188

original:

Iteration 1 status: core pipeline complete, refinement ongoing. Results so far:

Reconstruction quality clears the 25 dB PSNR acceptance bar: the current best model (v6) scores 26.52 dB PSNR / 0.8886 SSIM on 42 held-out frames that no model was trained on.

Metric accuracy: tape-measure mean error 4.8 mm (0.19%), worst case 0.29%, against a 5% target.

Processing time is approximately 75 minutes measured on the local RTX 3070 (matching 23, mapping 6, training 45 min). The FYP-2 target is under 35 minutes on an RTX 4090 (RunPod); this is a projection and has not yet been measured.

The app provides live quality guidance and coverage visualization.

The server supports both local and cloud GPU processing with automatic lifecycle management.

Open items (the FYP-2 schedule for all but mesh creation is in the Remaining FYP Plan chapter):

3DGS refinement: make the v6 recipe the one-command pipeline, validate it on the second room, and model the remaining motion blur.

3D mesh creation: in scope as planned work; not yet scheduled.

Structural layer completion: wall-to-wall dimensions, doors and openings, ceiling-height detection, floor-plan export.

Web workspace: browser viewer with 1:1 measurement.

rewrite:


---

## chapter8_testing.tex

### CHUNK 065
- **file:** chapters/chapter8_testing.tex
- **section:** Testing Strategy
- **lines:** 5-11
- **words:** 166

original:

Our testing strategy combines automated unit/integration tests (CI-enforced) with manual system-level validation on real indoor scans. The rationale is that unit tests verify algorithmic correctness (coordinate transforms, file parsing, API contracts), while end-to-end validation on real data verifies reconstruction quality and metric accuracy—properties that cannot be unit-tested.

Unit tests: Python pipeline modules tested with pytest on small synthetic capture folders (Python 3.10, 3.11, 3.12; no GPU, network or phone needed). Run by GitHub Actions CI on pushes to non-master branches, on pull requests, and from the CD workflow.

Lint: ruff in CI; real errors fail the run, unused-code findings are informational only.

Integration tests: Server endpoint tests through the FastAPI test client with the job starters replaced by recorders (upload, status, download, config), and RunPod client tests with the network faked. No test runs against a live RunPod pod.

Android: There are no Android (Java) unit tests. The capture app is checked by using it on a phone, and its packaging by the APK/manifest checker tests.

rewrite:


---

### CHUNK 066
- **file:** chapters/chapter8_testing.tex
- **section:** Testing Strategy
- **lines:** 12-13
- **words:** 77

original:

System tests: Manual runs of the reconstruction pipeline on real recordings, followed by held-out evaluation and tape-measure comparison. The full app upload → server → RunPod → download path has not yet been run as a recorded test.

Regression tests: Each pipeline change is compared on the same two reference recordings (the first room, newRoomAttemptSadness, and a second room, roomAttemptSadness2) to detect quality regressions. This comparison is run by hand with the evaluation scripts, not in CI.

rewrite:


---

### CHUNK 067
- **file:** chapters/chapter8_testing.tex
- **section:** Test Cases; Test Cases — Where “Pass (CI)” comes from
- **lines:** 40-42
- **words:** 175

original:

The automated tests are the pytest suite in tests/: 12 test files plus a shared conftest.py that builds small synthetic ARCore capture folders (no GPU, no network, no phone). The suite tests the Python side of the project only. There are no Android (Java) unit tests; the capture app is checked on a phone and, for its packaging, by the APK/manifest checker tests.

The suite was re-run in full against the current master head (commit 0d78466, 22 October 2026): 194 passed, 1 skipped, with the blocking ruff lint clean. The single skip is the APK signing check, which needs keytool from a local Java installation. Earlier, GitHub Actions CI run #6 (12 October 2026, commit c3bfcc9 on branch ci/pipeline-updates) ran the same suite on Python 3.10, 3.11 and 3.12 and the “Unit tests” step succeeded on all three; the re-run above was on a single interpreter, so the cross-version evidence is still CI's. “Pass (manual)” means a recorded run with its numbers in docs/progress/. Anything else is marked “Not yet executed” or “Not yet automated”.

rewrite:


---

### CHUNK 068
- **file:** chapters/chapter8_testing.tex
- **section:** Test Cases — Faults found by that re-run
- **lines:** 44-46
- **words:** 102

original:

The re-run was not a formality: it found three defects introduced after CI run #6 by the RunPod GPU-selection work. server/main.py called time.time() in the job-cancel endpoint without importing time, so POST /jobs/job_id/cancel raised NameError at runtime; two test files had also gone stale against the widened /config payload and the new GPU-name resolution step. All three are fixed in commit 0d78466. This is itself evidence for the value of the automated suite and the blocking lint gate.

Table [ref: tab:testfiles] lists what each pytest file covers, and Table [ref: tab:testcases] gives every test case with its expected result, evidence and status.

rewrite:


---

### CHUNK 069
- **file:** chapters/chapter8_testing.tex
- **section:** Test Results — Automated tests (CI)
- **lines:** 113-113
- **words:** 119

original:

The pytest suite has 128 test functions in 12 files (one of them parametrised over every Python file, giving 195 collected tests); the full run takes under three seconds. Of the 20 test cases above, 12 are backed by these automated tests (TC-6 is also checked by tape measure), 2 by recorded manual runs (TC-5, TC-13), 2 are only partly executed (TC-11, TC-12), 3 Android cases have no automated test (TC-1 to TC-3), and TC-14 has not been executed. CI runs on every push to non-master branches, on pull requests, and from the CD workflow on master; the CI workflow itself has not yet run on the current master head, so the multi-version evidence remains that of run #6.

rewrite:


---

### CHUNK 070
- **file:** chapters/chapter8_testing.tex
- **section:** Test Results — System-level results; Test Results — Effect of the pose fix
- **lines:** 135-137
- **words:** 61

original:

The current best model, v6, clears both acceptance thresholds. Gyro-aware frame selection (1166 candidate frames, 1108 kept) contributed the largest single gain (+0.26 dB / +0.009 SSIM); dense MVS initialisation (1.15M fused points reduced to 460k at 1 cm) added +0.21 dB / +0.003 SSIM.

Table [ref: tab:posefix] compares the earlier ARCore-pose pipeline with the image-based pipeline on the same recording.

rewrite:


---

### CHUNK 071
- **file:** chapters/chapter8_testing.tex
- **section:** Test Results — Second room; Test Results — Splatfacto versus our own trainer (different scene)
- **lines:** 154-156
- **words:** 91

original:

The image-based pipeline was also run on a second room (roomAttemptSadness2), measured by Muhammad Tayyab: held-out SSIM 0.91 with 1% badly placed surfaces. A held-out PSNR for the second room has not yet been measured.

On roomAttemptSadness2, Nerfstudio splatfacto trained on our preprocessed inputs reached 27.81 dB on held-out views and 28.08 dB on training views, against 24.70 dB held-out for our own trainer with the corrected recipe. This comparison motivated the switch to splatfacto. It is a different scene and protocol from Table [ref: tab:quality] and is not v6's score.

rewrite:


---

### CHUNK 072
- **file:** chapters/chapter8_testing.tex
- **section:** Acceptance Testing / Validation
- **lines:** 159-165
- **words:** 173

original:

Acceptance testing validates the system against the success criteria defined in Section 1.9:

Metric accuracy: Four rigid-object distances measured in the model agree with a tape measure to a mean of 4.8 mm (0.19%) and a worst case of 0.29% (Table [ref: tab:tape]), against a 5% target.

Reconstruction quality: v6 scores 26.52 dB PSNR / 0.8886 SSIM on 42 held-out frames of the first room, clearing the 25 dB / 0.85 thresholds; the second room reaches held-out SSIM 0.91 (its PSNR is not yet measured). Views from the room centre, where no camera stood, are coherent, and the earlier ghosts and floating splats are gone.

Processing time: The measured end-to-end time is approximately 75 minutes on the development RTX 3070 (feature matching 23 min, mapping 6 min, training 45 min). The NFR-P1 target of under 35 minutes on an RTX 4090 is a projection for FYP-2 and has not yet been measured, so NFR-P1 is not yet verified.

Capture usability: Not yet formally evaluated. Usability testing with external users is planned for FYP-2.

rewrite:


---

### CHUNK 073
- **file:** chapters/chapter8_testing.tex
- **section:** Acceptance Testing / Validation — Tape-measure evidence
- **lines:** 169-169
- **words:** 47

original:

Table [ref: tab:tape] compares distances measured in the reconstructed model (first room, image-based pipeline) with a tape measure. Two further measurements on soft edges (a chair and a rug) are recorded in docs/progress/Problems_and_Solutions.md; they are excluded from the rigid-object mean because their endpoints are not well defined.

rewrite:


---

### CHUNK 074
- **file:** chapters/chapter8_testing.tex
- **section:** Acceptance Testing / Validation — Tape-measure evidence
- **lines:** 189-189
- **words:** 63

original:

The worst case is 0.29%, far inside the 5% accuracy target. The error does not grow with distance (-8 mm at both 2.8 m and 6.7 m), so the ARCore-derived scale is sound; the small, consistent negative offset most likely comes from where the endpoints are clicked in the viewer. These are four measurements in one room; more rooms are planned for FYP-2.

rewrite:


---

### CHUNK 075
- **file:** chapters/chapter8_testing.tex
- **section:** Edge and Failure Cases
- **lines:** 194-198
- **words:** 181

original:

Tracking loss during capture: ARCore loses tracking in featureless corridors or when the phone is moved too fast. The app displays a red “Tracking Lost” banner and pauses quality logging. The IMU fallback (fallback.py) bridges the gap; on simulated gaps of 9 s its position error is 3.8 cm against 30.6 cm for interpolation, and re-alignment after re-tracking cuts post-gap error from 49.7 px to 8.2 px (Table [ref: tab:imufallback]). In the image-based pipeline COLMAP also registers most gap frames (748 of 759 on the second room). Re-alignment fails if the user never returns to a mapped area; those segments are flagged unverified and kept out of training. Mitigation: Live IQA warns the user to slow down; coverage overlay shows unscanned areas.

Plain white walls: Rooms with large untextured surfaces produce sparse SfM point clouds in those regions. The model shows blurring or holes on plain walls. Mitigation: The IQA “low texture” warning prompts the user to capture textured objects nearby.

Mirrors and glass: Highly reflective surfaces cause incorrect depth estimates and SfM outliers. Status: Known limitation; documented for FYP-2 investigation.

rewrite:


---

### CHUNK 076
- **file:** chapters/chapter8_testing.tex
- **section:** Edge and Failure Cases
- **lines:** 200-202
- **words:** 112

original:

Network interruption during upload: If the HTTP connection drops mid-upload, the app (ProcessingActivity) displays an error with a retry button. On the server, an upload missing a required file or carrying a corrupt depth zip is rejected cleanly (TC-8). Status: Partly handled; an interrupted upload has not been tested end to end.

RunPod pod failure: If SSH never becomes ready (pod crash, GPU unavailable), wait_for_ready gives up after 300 s (polling every 10 s), the pod is terminated in the finally block, and the job is marked failed. Status: Implemented; the timeout is unit-tested with a faked API (TC-7), but the termination path has not yet been exercised on a live pod.

rewrite:


---

### CHUNK 077
- **file:** chapters/chapter8_testing.tex
- **section:** Current Validation Status
- **lines:** 222-232
- **words:** 189

original:

Status of the Iteration 1 acceptance criteria (core pipeline complete, refinement ongoing):

✓ Reconstruction quality: v6 scores 26.52 dB / 0.8886 on the first room (>=25 dB, >=0.85). Second room: SSIM 0.91; PSNR not yet measured.

✓ Metric accuracy: mean 0.19%, worst case 0.29% against the 5% target (Table [ref: tab:tape]).

Processing time: not yet verified. Measured 75 min on RTX 3070; the <35 min RTX 4090 target (NFR-P1) is projected and not yet measured.

Pod lifecycle: partly verified. terminate_pod() is called from finally blocks and the client calls are unit-tested with a faked API; a live-pod test is not yet executed.

✓ CI pipeline: suite re-run green on the current master head (194 passed, 1 skipped, ruff clean); CI run #6 covers Python 3.10–3.12.

Not yet automated or executed: Android unit tests (TC-1 to TC-3), processing timeout (TC-14), app-to-RunPod end-to-end run.

Remaining validation for FYP-2: measurement accuracy on >=3 additional rooms with varied geometry; structural-layer accuracy (wall lengths against tape measure, detected doors against a manual count); web viewer usability testing with external users; and stress testing with large rooms, long recordings (>10 minutes) and low-end Android devices.

rewrite:


---

## chapter9_development_evidence.tex

### CHUNK 078
- **file:** chapters/chapter9_development_evidence.tex
- **section:** Work Completed
- **lines:** 5-5
- **words:** 99

original:

The team has built the Android capture app (ARCore pose, depth and quality logging, live IQA, coverage overlay, upload UI); the reconstruction pipeline (IMU fallback, keyframe extraction, COLMAP SfM with Sim3 metric alignment, Nerfstudio splatfacto training, model export, with gyro-aware frame selection validated but not yet in the one-command pipeline); the FastAPI processing server with local and RunPod cloud GPU modes and pod termination in finally blocks; the CI/CD pipeline (lint, unit tests, APK and web builds, hygiene checks); the server launcher (start_server.bat) with .env support; and a root-cause analysis of degenerate splat geometry (six causes, documented in Training_Analysis.md).

rewrite:


---

### CHUNK 079
- **file:** chapters/chapter9_development_evidence.tex
- **section:** Work Remaining
- **lines:** 8-8
- **words:** 69

original:

Scheduled in Chapter [ref: ch:plan]: the Three.js/WebGPU splat viewer with orbit controls; point-to-point measurement; completing the structural layer (wall-to-wall dimensions, doors and openings, ceiling-height detection, floor-plan export) with wall snapping and a floor-plan view; 3DGS refinement (one-command v6 pipeline, second-room validation, IMU-driven motion-blur modelling); field validation on >=3 more rooms; and usability evaluation with external users. 3D mesh creation is in scope as planned work but not yet scheduled.

rewrite:


---

### CHUNK 080
- **file:** chapters/chapter9_development_evidence.tex
- **section:** Individual Responsibilities
- **lines:** 12-12
- **words:** 31

original:

The primary evidence of each member's contribution is the set of modules they own: the files whose commit history carries their name (git log – <file>). Table [ref: tab:responsibilities] lists them.

rewrite:


---

### CHUNK 081
- **file:** chapters/chapter9_development_evidence.tex
- **section:** Contribution of Each Team Member — Muhammad Umair (23I-0662); Contribution of Each Team Member — Zaid Fareed (23I-0829); Contribution of Each Team Member — Muhammad Tayyab (23I-0636)
- **lines:** 35-41
- **words:** 166

original:

Project lead. Built the processing server (FastAPI endpoints, job model with per-step timeouts, local pipeline runner) and the RunPod integration (pod creation, SSH readiness, remote pipeline, termination in finally blocks). Built the app's upload and progress screen and the scan gallery/detail screens, worked on the main AR activity and coverage overlay, built the web UI prototype, and wrote the proposal and report.

Built the CI/CD infrastructure (lint, test and build workflows on three Python versions, Android build and signing checks, repository hygiene, releases) and wrote the entire automated test suite that backs the “Pass (CI)” results in Chapter [ref: ch:testing]. Also contributed trainer fixes and the ARKitScenes trainer experiments.

Built the reconstruction pipeline: IMU fallback and re-alignment, keyframe and gyro-aware frame selection, bundle adjustment, the COLMAP SfM stage with Sim3 metric alignment, dense MVS initialisation, the structural layer, and the evaluation tools. Wrote the app's capture logging and live IQA, ran the training analysis, and produced the v6 model, the tape-measure validation and the second-room result.

rewrite:


---

### CHUNK 082
- **file:** chapters/chapter9_development_evidence.tex
- **section:** Contribution of Each Team Member — Commit counts
- **lines:** 44-44
- **words:** 97

original:

The repository has 133 commits: Muhammad Umair 85, Zaid Fareed 26, Muhammad Tayyab 20 (committing as “BlazingBeam”), and 2 automated commits by the GitHub Actions bot. These counts reflect differing commit granularity, not differing effort. Umair commits each small change separately; Tayyab works in large batches, so a single commit of his often carries a whole pipeline stage (for example, the commit that introduced image-based SfM poses and lens self-calibration, or the one that introduced gyro-aware frames, dense MVS initialisation and the structural layer). The owned modules above, not the commit counts, are the evidence of contribution.

rewrite:


---

### CHUNK 083
- **file:** chapters/chapter9_development_evidence.tex
- **section:** Repository and Version Control Evidence
- **lines:** 47-58
- **words:** 156

original:

The project repository is hosted on GitHub. Key statistics:

Repository: github.com/Umairishuman/FYP (private)

Branches: master (stable) and work branches such as ci/github-actions, ci/pipeline-updates and exp/trainer-arkitscenes

Commit history: 133 commits (85 / 26 / 20, plus 2 bot commits)

CI: GitHub Actions runs on work branches, pull requests and (through the CD workflow) master: ruff lint and pytest on Python 3.10, 3.11 and 3.12; a Node.js build of the web UI (a placeholder for FYP-2); a Gradle APK build with signing and manifest checks; and repository hygiene (file-size limits, a secrets check, workflow lint).

CD: on push to master, build artefacts; on a version tag, a GitHub Release with the APK and web bundle.

Code review: Pull request template with area checkboxes and a testing checklist

Task tracking: docs/progress/TODO.md is the dated task log, with status markers and links to commits and analysis documents.

Table [ref: tab:repo] maps the repository layout to the modules described in this report.

rewrite:


---

### CHUNK 084
- **file:** chapters/chapter9_development_evidence.tex
- **section:** Tools and Tool-Assisted Development
- **lines:** 118-120
- **words:** 20

original:

IMPORTANT: Generative AI Tool Disclosure

In compliance with university policy, we disclose the use of the following AI-assisted development tools:

rewrite:


---

### CHUNK 085
- **file:** chapters/chapter9_development_evidence.tex
- **section:** Tools and Tool-Assisted Development — Statement of originality; Tools and Tool-Assisted Development — Other development tools
- **lines:** 139-141
- **words:** 108

original:

All core algorithms (Sim3 alignment, gyro-aware frame selection, coverage map, IQA pipeline, RunPod lifecycle management) were designed by the team. AI tools were used as assistants for code generation, debugging, explanation and report drafting, as disclosed in Table [ref: tab:aitools]. The system architecture, experimental methodology, root-cause analysis, and design decisions are entirely our own work. All AI-generated code was reviewed, understood, tested, and adapted by team members before integration into the codebase.

Android Studio (Ladybug) with the Android Gradle Plugin, Visual Studio Code with Python and Java extensions, Git and GitHub, Postman for API testing, ADB for device-level debugging, and NVIDIA Nsight for GPU profiling during training experiments.

rewrite:


---

### CHUNK 086
- **file:** chapters/chapter9_development_evidence.tex
- **section:** External Components and Dependencies
- **lines:** 165-165
- **words:** 20

original:

All external components are used under permissive open-source licenses compatible with academic use. No proprietary or restrictively-licensed code is included.

rewrite:


---

### CHUNK 087
- **file:** chapters/chapter9_development_evidence.tex
- **section:** Risks and Mitigation
- **lines:** 169-169
- **words:** 46

original:

Table [ref: tab:risks] is the project's risk register. Likelihood and impact are rated Low, Medium or High by the team; each risk is handled by the member who owns the affected modules (Table [ref: tab:responsibilities]). The register is reviewed at the start of each FYP-2 iteration.

rewrite:


---

### CHUNK 088
- **file:** chapters/chapter9_development_evidence.tex
- **section:** Security and Privacy Considerations
- **lines:** 200-203
- **words:** 184

original:

API key management: The RunPod API key is loaded at runtime from environment variables or a .env file, never hardcoded in source. However, .env is not in .gitignore and was committed to the repository on 18 October 2026, so NFR-S2 is not met; the key must be rotated and the file removed from version control.

CI secrets scanning: The CI hygiene job fails if a .env, key or certificate file is tracked, and scans tracked files for private keys, AWS keys and GitHub tokens (it has no pattern for RunPod keys). CI last ran (run #6) before .env was committed; by the job's own rule, the next CI run on master will fail until the file is removed.

Data privacy: Captured scan data (video, depth, poses) is transmitted to the processing server over the local network. In production, HTTPS would be required. Scan data is stored only for the duration of processing and can be deleted via the API.

Cloud GPU security: RunPod pods are created on-demand, used for a single job, and terminated immediately after. No persistent data remains on the cloud GPU.

rewrite:


---

### CHUNK 089
- **file:** chapters/chapter9_development_evidence.tex
- **section:** Current Limitations
- **lines:** 208-213
- **words:** 163

original:

Mirrors and glass: Highly reflective and transparent surfaces cause SfM outliers and incorrect depth. The model shows artifacts in these regions. Planned FYP-2 investigation: detect and mask reflective regions.

Large rooms: Rooms exceeding approximately 8×8 m may exceed GPU memory during training on the RTX 3070 (8 GB). A 24 GB cloud GPU (RTX 4090, the RunPod default) is expected to handle larger scenes; this has not yet been measured.

Outdoor scenes: The system is designed for indoor environments. Outdoor scenes with sky, vegetation, and long-range views are out of scope.

Real-time processing: Processing takes approximately 75 minutes on the development RTX 3070; no cloud-GPU timing has been measured yet. Real-time reconstruction is not feasible with current 3DGS training times.

Single-floor only: The current coverage map and measurement tools assume a single-floor environment. Multi-floor buildings require manual segmentation.

No web viewer yet: The 3D model can currently only be viewed in a local desktop viewer. The web-based Three.js viewer is planned for FYP-2.

rewrite:


---

## chapter10_fyp2_plan.tex

### CHUNK 090
- **file:** chapters/chapter10_fyp2_plan.tex
- **section:** Remaining Scope
- **lines:** 5-5
- **words:** 70

original:

FYP-2 has three priorities: (1) finishing the refinement of the reconstruction pipeline and making it faster; (2) completing the structural layer (wall planes, corners, wall lengths, door detection and floor plans) that turns the photoreal model into something that can be measured reliably; and (3) building the web workspace with 1:1 metric measurement. The core capture → upload → reconstruct pipeline was built in FYP-1; FYP-2 completes and validates it.

rewrite:


---

### CHUNK 091
- **file:** chapters/chapter10_fyp2_plan.tex
- **section:** Remaining Modules and Features
- **lines:** 10-14
- **words:** 159

original:

Pipeline Optimization Module: Make the v6 recipe (gyro-selected frames, dense MVS initialisation, finer densification) the one-command pipeline and validate it on the second room. Reduce end-to-end processing time from the measured 75 min on the development RTX 3070 (matching 23 min, mapping 6 min, training 45 min) to under 35 min on an RTX 4090. The 35 min figure is a projected target, not a measurement. Techniques: ARCore-pose-guided or sequential matching pairs instead of exhaustive COLMAP matching, fewer training iterations, and fewer keyframes on slow walks.

Reconstruction Refinement: IMU-driven motion-blur and rolling-shutter modelling during training, using the per-frame exposure time and rolling-shutter readout the app now logs (the gyroscope shows the median training frame is blurred by 6–12 px). Also ARCore-started image-only alignment with re-anchor detection from the logged anchors, which could give COLMAP-quality poses faster.

Robustness Improvements: Better handling of mirrors and glass (detecting and masking reflective regions), textureless walls, large rooms (>8 m), and variable lighting conditions.

rewrite:


---

### CHUNK 092
- **file:** chapters/chapter10_fyp2_plan.tex
- **section:** Remaining Modules and Features
- **lines:** 16-20
- **words:** 171

original:

Structural Layer Module: Complete structure.py, which already rebuilds the room shell next to the splat model: floor and wall planes, corners from neighbouring wall intersections, wall lengths (prototype: 6.65–6.68 × 4.45–4.48 m on the first room) and openings, with 5 doors detected automatically. Remaining work: wall-to-wall dimensions, doors and other openings as first-class objects, fixing the ceiling-height detection, automatic floor-plan export, and measurement clicks that snap to walls. The photoreal splat model itself is not modified, because post-hoc flattening destroyed the glossy floor's reflections and crushed door frames.

Web Workspace Module: Three.js / WebGPU-based Gaussian splat viewer with orbit/pan/zoom controls, running in any modern browser. Loads the splat.ply model and the structural layer's structure.json, and shows a floor-plan view.

Measurement Module: Point-to-point 1:1 distance tool in the metric 3D model. The user clicks two points on the splat surface or on a structural-layer wall; the system computes the Euclidean distance in metres in the Sim3-aligned coordinate frame. Target accuracy: within 5% of tape measure (current evidence: mean 0.19%, worst case 0.29%).

rewrite:


---

### CHUNK 093
- **file:** chapters/chapter10_fyp2_plan.tex
- **section:** Remaining Modules and Features
- **lines:** 22-24
- **words:** 49

original:

3D Mesh Creation: Create a 3D mesh of the scanned room from the reconstruction, alongside the splat model. This is in scope as planned work; it has not yet been assigned to an iteration.

Dashboard Module: Web-based project dashboard showing scan history, processing status, model thumbnails, and measurement records.

rewrite:


---

### CHUNK 094
- **file:** chapters/chapter10_fyp2_plan.tex
- **section:** Remaining Iterations
- **lines:** 30-32
- **words:** 86

original:

Iteration 2a (Weeks 1–4): Pipeline optimization and web viewer. Deliverable: one-command v6 pipeline; processing time <35 min on RTX 4090 (projected, not yet measured); browser-based splat viewer with point-to-point measurements validated on >=3 rooms.

Iteration 2b (Weeks 5–8): Robustness, reconstruction refinement and the structural layer. Deliverable: improved edge-case handling; structural layer with wall lengths, doors and floor-plan export; measurement snapping to walls in the viewer.

Iteration 2c (Weeks 9–12): Dashboard, field validation, and final polish. Deliverable: complete web workspace, user testing on 5+ rooms, final report.

rewrite:


---

### CHUNK 095
- **file:** chapters/chapter10_fyp2_plan.tex
- **section:** Implementation Plan — Iteration 2a: Optimization + Web Viewer (Weeks 1–4); Implementation Plan — Iteration 2b: Robustness + Structural Layer (Weeks 5–8); Implementation Plan — Iteration 2c: Dashboard + Final Validation (Weeks 9–12)
- **lines:** 39-60
- **words:** 195

original:

Put the v6 recipe into the one-command pipeline; replace exhaustive matching with ARCore-pose-guided or sequential pairs (week 1).

Reduce splatfacto iterations and keyframes on slow walks; benchmark every change on the two reference rooms (week 1–2).

Set up a Three.js project with a Gaussian splat renderer and camera controls (week 2).

Build the measurement tool: ray-cast click → nearest splat → 3D coordinate → distance display (week 3).

Validate measurement accuracy against tape-measure ground truth on 3 rooms (week 3–4).

Integrate the viewer with the FastAPI backend for model loading (week 4).

Implement reflective-surface detection and masking for mirrors and glass (week 5).

Try IMU-driven motion-blur and rolling-shutter modelling on recordings that carry per-frame exposure metadata (week 5–6).

Structural layer: fix ceiling-height detection; make doors and openings first-class objects with their dimensions (week 6).

Structural layer: wall-to-wall dimensions and automatic floor-plan export from the floor polygon (week 7).

Load structure.json in the web viewer; snap measurement clicks to walls; add a floor-plan view (week 8).

Build the web dashboard: scan list, processing status, model thumbnails (week 9–10).

User testing with 5+ external users; collect usability feedback (week 10–11).

Fix usability issues, write documentation (week 11–12).

rewrite:


---

### CHUNK 096
- **file:** chapters/chapter10_fyp2_plan.tex
- **section:** Implementation Plan — Iteration 2c: Dashboard + Final Validation (Weeks 9–12)
- **lines:** 61-61
- **words:** 13

original:

Final validation: measurement accuracy, structural-layer accuracy, processing time on 5+ rooms (week 12).

rewrite:


---

### CHUNK 097
- **file:** chapters/chapter10_fyp2_plan.tex
- **section:** Testing and Validation Plan
- **lines:** 66-71
- **words:** 126

original:

Measurement accuracy: Compare point-to-point measurements in the web viewer against tape-measure ground truth on >=5 rooms of varying size and geometry. Target: error within 5% of tape measure, extending the current four-measurement evidence (mean 0.19%) to more rooms.

Structural layer: For each test room, compare extracted wall lengths against tape measure (target: within 5%) and the detected doors against a manual count.

Web viewer performance: Maintain >=30 FPS on a mid-range laptop (integrated GPU) for models up to 2 million splats.

Usability testing: Task completion rate >=90% for first-time users performing capture, viewing, and measurement tasks.

Processing time: End-to-end pipeline <35 min on RTX 4090 (projected target; currently 75 min measured on RTX 3070). Benchmark each optimization individually.

Cross-browser: Verify viewer on Chrome, Firefox, and Edge.

rewrite:


---

### CHUNK 098
- **file:** chapters/chapter10_fyp2_plan.tex
- **section:** Deployment Plan
- **lines:** 76-79
- **words:** 65

original:

Server: Deploy the FastAPI backend and web viewer on a VPS with HTTPS (Let's Encrypt). Static assets served via CDN.

GPU processing: Continue using RunPod on-demand pods. Evaluate RunPod serverless endpoints if job volume increases.

Android app: Distribute the APK via GitHub Releases. Google Play Store submission if time permits.

CI/CD: Extend the existing GitHub Actions to deploy the web frontend on push to master.

rewrite:


---

### CHUNK 099
- **file:** chapters/chapter10_fyp2_plan.tex
- **section:** Expected Final Deliverables
- **lines:** 105-112
- **words:** 87

original:

Android APK: Capture app with live IQA, coverage overlay, and upload.

Web workspace: Gaussian splat viewer with 1:1 measurement tools and a floor-plan view.

Processing server: FastAPI backend with local and cloud GPU support.

Structural layer: Per-room structure.json (planes, corners, wall lengths, doors and openings) and floor-plan export.

Validation report: Measurement accuracy on >=5 rooms, structural-layer accuracy, processing-time benchmarks, usability test results.

Documentation: User guide, API documentation, deployment guide.

Source code: Complete repository with CI/CD, tests, and documentation.

Final report: FYP-2 report with complete results and analysis.

rewrite:


---

## conclusion.tex

### CHUNK 100
- **file:** chapters/conclusion.tex
- **section:** Conclusion; Conclusion — What we found; Conclusion — What we built and measured
- **lines:** 3-7
- **words:** 197

original:

BuildScan 3D turns a casual video from a commodity Android phone into a metric-scale 3D Gaussian Splatting model of a room. At mid-evaluation, Iteration 1 stands at core pipeline complete, refinement ongoing.

Four findings shaped the design: (1) image-based COLMAP poses replace ARCore poses for training: once ARCore's silent re-anchor and missing lens model were removed, training-view fit rose from 21.9 dB to 28 dB and held-out SSIM from 0.78 to 0.86; (2) dense MVS initialisation is critical for splat geometry; (3) aggressive regularisation degrades quality when combined with Adam; (4) gyro-aware frame selection outperforms texture-based sharpness metrics.

A three-tier system—Android capture app with live IQA and coverage overlay, FastAPI processing server with RunPod dispatch, and a COLMAP + splatfacto pipeline with Sim3 metric alignment—with CI/CD via GitHub Actions. The current best model (v6) scores 26.52 dB PSNR (>=25 dB target) and 0.8886 SSIM (>=0.85 target) on 42 held-out frames. Tape-measure checks give a mean error of 4.8 mm (0.19%) on rigid objects and a worst case of 0.29%, substantially better than the 5% accuracy target. Processing currently takes about 75 minutes on an RTX 3070; the under-35-minute RTX 4090 target is projected and not yet measured.

rewrite:


---

### CHUNK 101
- **file:** chapters/conclusion.tex
- **section:** Conclusion — Risks and next steps
- **lines:** 9-9
- **words:** 93

original:

The risk register (Table [ref: tab:risks]) tracks twelve risks; the highest are cloud GPU cost (cost per scan not yet measured), the unmeasured RTX 4090 processing time, tracking loss on featureless surfaces, and delivering the remaining FYP-2 scope. Mirrors and glass remain a known limitation. FYP-2 completes 3DGS refinement, the structural layer (wall planes, corners, wall lengths, door detection) with automatic floor plans, and the web workspace with point-to-point 1:1 measurement, and validates them on more rooms. 3D mesh creation is also in scope as planned work and has not yet been scheduled.

rewrite:


---

## appendix_meetings.tex

### CHUNK 102
- **file:** chapters/appendix_meetings.tex
- **section:** Supervisor Meetings
- **lines:** 5-5
- **words:** 52

original:

The team held two meetings with the supervisor, Mr. Furqan Nasir, before the mid-evaluation. Their dates were not recorded at the time, so they are listed in order rather than by date. No formal minutes were taken, and no decision in this report is presented as having been approved by the supervisor.

rewrite:


---

### CHUNK 103
- **file:** chapters/appendix_meetings.tex
- **section:** Supervisor Meetings
- **lines:** 18-18
- **words:** 19

original:

The dated record of the work itself is the progress log below and the commit history (Chapter [ref: ch:evidence]).

rewrite:


---

### CHUNK 104
- **file:** chapters/appendix_meetings.tex
- **section:** Progress Log
- **lines:** 22-31
- **words:** 143

original:

Detailed development progress is maintained in docs/progress/TODO.md. Key milestones:

ARCore capture app: Basic recording → pose sync validation → IQA → coverage overlay → upload UI. Incremental feature additions documented with timestamps.

Reconstruction pipeline: Best custom-trainer model on ARCore-derived poses (gs_colmap_nc, 22.67 dB / 0.782 held-out) → image-based COLMAP poses (training-view fit 21.9 → 28 dB; held-out SSIM 0.78 → 0.86) → v3 (26.04 dB / 0.8756 on the 42-frame held-out set) → gyro-aware frame selection (+0.26 dB / +0.009 SSIM) → dense MVS initialisation (+0.21 dB / +0.003 SSIM) → v6 (26.52 dB / 0.8886). Each improvement documented with before/after metrics.

Quality debugging: Two-week root-cause analysis documented in Training_Analysis.md covering 6 identified causes of degenerate splats, with per-cause experiments and metrics.

Server and cloud: FastAPI server → local pipeline runner → RunPod integration → guaranteed pod lifecycle. Problem-solution pairs documented in Problems_and_Solutions.md.

rewrite:


---

### CHUNK 105
- **file:** chapters/appendix_meetings.tex
- **section:** Problems and Solutions Summary
- **lines:** 36-44
- **words:** 100

original:

25 problems encountered during development are documented in docs/progress/Problems_and_Solutions.md. The most significant:

ARCore silent re-anchoring causing pose discontinuities (solved: anchor logging + IMU fallback)

COLMAP lens distortion not matching ARCore intrinsics (solved: self-calibration)

Degenerate splat geometry from custom training recipe (solved: adopted splatfacto)

30 FPS input overwhelming COLMAP matching (solved: keyframe selection, one sharp frame per window)

Motion blur in training frames, 6–12 px median (solved for v4–v6: gyro-aware frame selection, +0.26 dB / +0.009 SSIM)

GPU memory overflow on the 8 GB RTX 3070 with >1000 full-resolution frames (solved: skip page-locked image caching above 4 GB; default densification thresholds)

rewrite:


---
