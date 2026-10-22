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

Current 3D scanning solutions available for indoor locations either need costly LiDAR hardware or complicated step-up procedures that are impractical for construct site personnel, building administrators, and small design companies. The project BuildScan 3D is closing the gap by offering a total system capable of converting a footage captured by a usual Android smartphone (such as the realme phone, which has no LiDAR unit of any particular equipment) into a 3D Gaussian Splatting (3DGS) model, i.e. the one that can be taken for real-world measurements. 

The proposed system has five steps: (1) an individual Android app that uses ARCore to record video at the rate of 30 FPS together with location, depth map, and image quality feedback; (2) a pose-prior stage that relates ARCore OpenGL coordinates to COLMAP/Nerfstudio ones; (3) a cloud-GPU reconstruction stage for which COLMAP Structure-from-Motion with Sim3 alignment of ARCore coordinates has been applied, and training has been performed with the use of Nerfstudio; (4) a structural layer that makes it possible to extract walls, corners, and lengths of walls and doors to create floor plans and measure objects; (5) a web viewer for measurements and inspecting the model.

---

### CHUNK 002
- **file:** chapters/04_abstract.tex
- **section:** Abstract
- **lines:** 9-9
- **words:** 127

original:

At mid-evaluation, Iteration 1 stands at core pipeline complete, refinement ongoing: the Android capture app records all required sensor data with live quality and coverage guidance; the FastAPI processing server accepts uploads and dispatches jobs to on-demand RunPod GPU pods; and the current best reconstruction (v6) scores 26.52 dB PSNR / 0.8886 SSIM on 42 held-out frames, and tape-measure checks show a mean measurement error of 4.8 mm (0.19%), worst case 0.29%, against a 5% accuracy target. Key technical challenges solved include IMU-bridged tracking-gap recovery, lens self-calibration via COLMAP, and diagnosis and correction of degenerate Gaussian splat geometry. The open items are 3DGS refinement, 3D mesh creation, completion of the structural layer, and the web workspace (including floor plans and 1:1 measurement), followed by end-to-end field validation.

rewrite:

At the mid-point evaluation, we can say that the first iteration has made progress in terms of the total completion of core pipeline and the refinement process: the Android capture application processes all the necessary sensor data with live quality and coverage guidance, the FastAPI processing server receives uploads and sends work to RunPod GPU pods as needed, and the top reconstruction (version six) achieved 26.52 dB PSNR/0.8886 SSIM out of forty-two held-out frames; tape measure calculations show an average measurement error of 4.8 mm (0.19%) and a maximum error of 0.29% which is far better than the five percent accuracy requirement. The most important technical issues that have been solved already are bridging the tracking gap with IMU, lens self-calibration using COLMAP, and discovering and fixing the problems with irregular Gaussian splat geometry. Some of the unexplored areas remaining include refining the 3DGS, creating 3D mesh, completing the structural layer and creating a web workspace (including the floor maps and 1:1 measurements), which should be followed by full-scale field validation.

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
BuildScan 3D is an exemplary system that allows users to turn a short video of an indoor space captured with a smartphone into an accurate 3D model that can be used to measure. 

The 3D scanning of interiors is usually performed using costly methods that involve either using LiDAR devices which cost more than $10,000 and require multiple preconditions or using photogrammetry, which requires advanced experience in the sphere as well as much time to analyze the data. Many construction companies, facility managers, and students cannot afford to buy the necessary equipment and utilize modern technology to create highly accurate models. 

We analyzed the existing developments related to the application of Gaussian Splatting for 3D scanning , PocketGS, and visual-inertial SLAM and found a significant gap. Thus, no system has combined the use of smartphones equipped with ARCore and cloud computing, allowing receiving accurate 3D models in a fully automatic manner. 

Our pipeline includes five stages, which include: (1) capturing video at a rate of 30 fps, ARCore poses, depth and IMU data; (2) alignment of the captures; (3) processing with the use of COLMAP and Nerfstudio; (4) application of measurement and analysis techniques; (5) viewing the data with the use of a specialized viewer.

---

### CHUNK 004
- **file:** chapters/06_executive_summary.tex
- **section:** Executive Summary — Current status (Iteration 1: core pipeline complete, refinement ongoing)
- **lines:** 13-13
- **words:** 162

original:

The Android capture app records all required sensor data with live image-quality assessment and coverage guidance (red/yellow/green dot overlay). The FastAPI processing server accepts uploads and dispatches jobs to on-demand RunPod GPU pods (NVIDIA RTX 4090 by default, selectable at runtime), with automatic pod termination on completion or failure. End-to-end processing has been measured at about 75 minutes on the development RTX 3070; no cloud-GPU timing has been measured yet, and the under-35-minute RTX 4090 figure is an FYP-2 projection. The current best reconstruction (v6) scores 26.52 dB PSNR / 0.8886 SSIM on 42 held-out frames that no model was trained on. Tape-measure checks show a mean error of 4.8 mm (0.19%) and a worst case of 0.29% (8 mm over a 2.8 m wall), far inside the 5% accuracy target. CI/CD via GitHub Actions validates Python code, Android builds, and web UI on every push. Open items: 3DGS refinement, 3D mesh creation, completion of the structural layer, and the web workspace.

rewrite:
This Android capture app is capable of recording all necessary sensor data together with live-QA image quality processing and coverage guidance (using red/yellow/green dot overlay). FastAPI processing server receives the data and dispatches the jobs to RunPod GPU pods that are available as per request (the most preferred pod is NVIDIA RTX 4090, but it can be selected at run-time). The approximate time taken in end-to-end processing using the development RTX 3070 has been calculated at about 75 min; however, the cloud-GPU timings are yet to be measured. The current best reconstruction results in 26.52 dB PSNR / 0.8886 SSIM for 42 frames that have not been used for training any of the models so far. Tape-measure accuracy is showing the mean error to be at 4.8 mm (0.19%) with the maximum value of 0.29% (8 mm in the case of 2.8 m wall), which is well inside the target of 5% accuracy. Python code, Android builds, and web UI are all verified via CI/CD process via GitHub Actions. Open items include refinement of 3DGS, creation of 3D mesh, completion of the structural layer, and web workspace.

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
The cloud GPU availability and per-work charge as per known data; structural layer durability among various rooms (the height detection is still not reliable); the success of measurement verification for various room layouts. The complete risk register comprises 12 items with probability, effect, and mitigation involved.

Finish up the structural layer and web-based measurement environment (Stage 4); conduct field trials in further rooms and check correctness of measurement against ground data acquired by means of tape measure. 3D mesh building is also included in the plans yet not scheduled.

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
BuildScan 3D is a comprehensive solution that allows anyone to produce photorealistic metric-size 3D models of indoor spaces using just a regular Android phone. The user has to make a short video of walking through the indicated place, while BuildScan uploads the data to the cloud, builds a 3D Gaussian Splatting, and produces a virtual image of the scanned area.


The solution is primarily aimed at taking photographs of construction sites, irrespective of the type of facility being managed or designed.

---

### CHUNK 007
- **file:** chapters/chapter1_introduction.tex
- **section:** Problem Statement
- **lines:** 9-9
- **words:** 81

original:

Capturing accurate, metric-scale 3D models of indoor environments currently requires either (a) LiDAR hardware costing $10,000 or more, (b) photogrammetry workflows requiring expert knowledge and hours of manual post-processing, or (c) consumer-grade scanning apps (e.g. Polycam, Luma AI) that produce visually plausible but metrically inaccurate models unsuitable for measurement. There is no affordable, fully automated pipeline that turns a smartphone video into a metrically accurate 3D model with sufficient quality for professional use. Section [ref: sec:gaps] examines these gaps in detail.

rewrite:
At this moment, an accurate, metric-grade 3D representation of indoors requires either LiDAR devices costing over $10,000, (ii) photogrammetric methods using professional knowledge and multiple hours of manual post-processing, or (iii) applications for phones (such as Polycam or Luma.AI) that will produce models that are visually realistic yet cannot produce 3D models measured in actual units. At present, availability of a fully automated process that would allow for transforming smartphone-based video into a metric-grade 3D model is not at hand. Section [ref: sec:gaps] provides a detailed description of the existing gaps that should be filled.


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
Construction and facility management are at a loss for time and money due to rework from improper or outdated spatial documents. Small businesses and site crews are in need of rapid and accurate as-built captures for their routine inspections. Modern smartphones equipped with high resolution cameras, IMUs, and processors capable of Augmented Reality (AR), have become potential devices for capturing 3D images. However, software technology should fill the void between artsy AR and professional surveying.

The new development in the field of 3D Gaussian Splatting technology (see kerbl3dgs article) makes it possible to create photorealistic views of one object in real-time. At the same time, ARCore provides measurements and depth measurement capabilities for cameras on Android devices. The combination of this technology with the use of cloud GPU computing will allow for the complete automation of the indoor scanning process.

---

### CHUNK 009
- **file:** chapters/chapter1_introduction.tex
- **section:** Project Vision
- **lines:** 17-17
- **words:** 75

original:

BuildScan 3D aims to democratize indoor 3D scanning by making it as simple as recording a video on a phone. The system will: (1) guide the user during capture to ensure sufficient coverage and quality; (2) automatically process the recording on a cloud GPU; (3) return a metric-scale 3D model with measurement tools; and (4) extract the room's structure—wall planes, corners, wall lengths and doors—as the basis for automatic floor plans and 1:1 metric measurement.

rewrite:

BuildScan 3D's mission is to make indoor 3D scanning accessible to everyone by simplifying the process so that it is as easy as making a video on a mobile phone. The technology will: (1) assist the user during the scanning process, ensuring high-quality results; (2) process any recorded video in the cloud; (3) provide a 3D model in a metric scale along with measurement tools; and (4) determine the shape of the room—the wall planes and corners, length of the walls, and the door—for further automated production of the floor plan along with accurate dimensions on a 1:1 scale.

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
Create a capture application for Android that captures videos, ARCore positions, depth maps, and IMU information while also providing live feedback about image quality.

Create an automated cloud-GPU processing system to turn recording from the phone into a 3D Gaussian Splatting model, aiming for a total time of 35 minutes on a cloud RTX 4090 (the current processing time is 75 minutes on the development RTX 3070).

Meet accuracy requirements of metric scale with less than 5% difference from actual measurement against a tape measure for distance measurements done in the model.

Be able to have held-out PSNR of over or equal 25 dB for photometric quality of reconstruction.

Develop structural layer that extracts wall planes, corners, wall dimensions and doors from the model for automatic creation of floor plan and metric measuring of the space.

Develop 3D viewer that operates online with point to point measuring tools.

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
Android capturing tool that has integrated ARCore, real-time IQA, and coverage suggestion.

Automated reconstruction process which includes extraction of keyframes, COLMAP SFN, Sim3 for scaling and dataset creation.

Local and cloud-based GPU serving via FastAPI processing server.

3D model measurement.

Structural layer including construction of plane, corners, wall lengths, detection of doors, and making of an architectural drawing (prototype was created in FYP-1).

Three.js web browser as model viewing application (FYP-2).

3D mesh production based on the 3D data from the initiative (plan exists, not yet scheduled).

CI/CD pipeline leveraged through GitHub Actions.

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
Mobile Capture Reference: Android application utilizing ARCore technology to conduct video recording, executing camera posture tracking, depth sensing activities, providing IMU telemetry and giving real-time coverage along with quality guidance.

Pose pReference: Coordinate alignment from ARCore OpenGL coordination system to COLMAP or Nerfstudio reference using conversion of quaternion to rotation matrix and Sim3 measurement alignment.

Capture Pipeline: COLMAP extracting of features, matching, mapping, undistorting of images, lens self-calibration, and training of Nerfstudio splatfacto 3DGS.

Processing Server: FastAPI backend responsible for uploading datasets, managing jobs, tracking and dispatching of the cloud GPU using RunPod API.

Structural Reference Layer: Recreation of the construction of the room leaving the splat model (structure.py): the planes of the floors and walls, corners as well as the walls’ lengths, doors or any other opening (the floor polygon which is used for providing plans and measurements). Prototype created; finishing shall occur in FYP-2.

Web Viewer: Viewer created in Three.js and WebGPU containing a rendering of the splat and accommodating 1:1 measurements.




---

### CHUNK 013
- **file:** chapters/chapter1_introduction.tex
- **section:** Stakeholders and User Classes
- **lines:** 56-56
- **words:** 53

original:

The primary users are construction site managers, facility maintenance teams and architectural survey teams who need quick as-built documentation. Secondary users are architecture and civil engineering students, and real estate professionals documenting properties. Administrators operate the cloud GPU resources and monitor processing jobs. The supervisor, Mr. Furqan Nasir, provides academic evaluation and guidance.

rewrite:
Main users are construction site supervisors, facility maintenance teams, and architectural inspection teams requiring prompt as-built documentation. Other users can be students of architecture and civil engineering, and property managers in real estate. Administrators manage cloud GPU resources and watch over the processing tasks. The leadership position is held by Mr. Furqan Nasir who carries out the semi-academic assessment and consulting.

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
Metric precision: distances taken on the model are within 5% of the tape-measure actual distance (measured: average 0.19%, maximum 0.29%).

Reconstruction quality: held PSNR >= 25 dB, SSIM >= 0.85.

Processing duration: the total time taken from submitting the data to the visible model is under 35 minutes on the NVIDIA RTX 4090 cloud (FYP-2 goal; aims achieved but yet not measured; the present result is 75 minutes on the working RTX 3070).

Capture guidance: the real-time IQA helps users decrease the errors by at least 50% in the process compared to the case when no interactive process is suggested.

Structural element: walls, wall lengths, and doors are extracted automatically with the accuracy being within accepted 5% (FYP-2; not checked against the tape measure yet).

---

### CHUNK 015
- **file:** chapters/chapter1_introduction.tex
- **section:** Constraints and Assumptions
- **lines:** 69-69
- **words:** 76

original:

The phone must support ARCore (Google's AR compatibility list); all results in this report come from a commodity Android phone (realme) with no LiDAR or other special hardware. Cloud processing needs internet connectivity and a RunPod account. The scanned space must be a single room or a connected set of rooms (not a full building), lit well enough for ARCore to keep tracking, and the current pipeline targets rooms up to about 10 × 10 m.

rewrite:
The device should have ARCore compatibility (provided by Google) and that is achieved through a common Android phone such as the realme phone, which lacks any specialized hardware, including LiDAR. The processing relies on the internet, specifically a RunPod account. Make sure that the scanned area is limited to one room (or simple group of rooms)—it must be well lit in order to track the spatial movements.

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
Privacy: The recorded video may contain recognizable personal identification elements. The data remains on the cloud account of the user alone, without involving any third party. The system does not save or transmit any extra video information apart from what is necessary in the process.

Accessibility: The application has visual support represented as visual quality indication (a capacity of colour-related visual presentation) and haptic facility represented as vibration (reading of level of quality).

Environmental: The computing resource is minimized by terminating cloud GPU pods immediately after processing the data.

Tool disclosure: GenAI tools (Claude Code, GitHub Copilot, ChatGPT) were employed in code development, debugging, documentation and report preparation, including editing of the report.

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
The methodology involved conducting a systematic literature review together with empirical experimentation. Recent articles covering the years 2023–2025 regarding the themes of 3D Gaussian Splatting, on-device 3D reconstruction, and visual-inertial SLAM were reviewed, with the focus on papers that describe systems operating with monocular video or video data captured in smartphones. After that, the prime candidates were implemented and tested on the ARCore-based data. Significant publications are kept in the research papers repository (docs/Research Papers/).

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
Matterport Pro3: This professional LiDAR scanner is priced over $6000 and can generate metric models accurately but has the disadvantage of needing specific hardware and charging extra fees for each scan carried out in the cloud.

Polycam: A mobile application based on LiDAR (iPhone Pro) or based on photogrammetry. Although it enables quick data collection, it does not work with non-LiDAR devices and does not have an automatic process in the cloud either.

Luma AI: It uses videos to produce a 3DGS that looks fantastic visually but does not have an option to scale and is missing various measuring options.

RealityCapture: The professional software for photogrammetry processes visual data very impressively but requires skills for the operator to take the photos on their own and to use a GPU for processing pictures. 

3D Gaussian Splatting [cite: kerbl3dgs]: Kerbl and some other researcher from the paper published in 2023 noted that the rendering of the radiance field in real time could take place due to the application of 3D Gaussians. The only prerequisite for this process is that the SfM poses should be computed before doing anything else. 

PocketGS [Source: pocketgs]: Conducting training of 3DGS on devices such as smartphones. The advantage of using dense multi-view stereo initialization is that it provides superior geometry compared to sparse points from Structure from Motion (SfM). However, it has the limitation of being applicable only to short sequences in small scenes.

VIGS-SLAM [Source: vigsslam]: Visual inertial Gaussian splatting SLAM (simultaneous localization and mapping). It allows for real-time tracking and mapping; however, the obstacle here is the need for custom hardware integration, and hence this system cannot be called a turn-key solution.

PGSR [Source: pgsr]: Planar Gaussian splatting method for surface reconstruction. It allows you to achieve a higher level of flatness of walls/floors, but the quality of reflection of the surfaces (mirrors, glossy floors) gets worse as a result.

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
Here are the main drawbacks of the solutions available, which play an important role for us:

Price barrier: Commercial solutions (Matterport, RealityCapture) require costly requirements for hardware or software licenses.

No metric scale from video: User apps (Luma AI) and research methods (3DGS, PocketGS) produce visually plausible models but without the metric scale, hence no measurement is possible.

No guidance for catching: No system exists that provides real-time feedback on the quality of images, tracking status, and coverage during catching, which results in substantial quality failures.

Manual pipeline: Research methodologies provide manual workflow steps (choosing a photo, setting up COLMAP, configuring the training), which non-specialists are unable to perform.

No structure from plain video: 3DGS consumer applications and research have a radiance field but no explicit structure of the room (walls, wall length, doors), thus making it impossible to create floorplans or measure accurately; if floorplans exist, they are only based on LiDAR data or other specialized hardware.

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

BuildScan 3D fulfills the following functions:

ARCore for metric frame: With help of visual-inertial odometry of the phone it is possible to obtain the metric frames. The results are later fine-tuned with the use of COLMAP and corrected with Sim3.

Live capture assistance: Real-time assessment of the image, indicating its blurriness, exposure, and movement speed, along with the voxel-based assessment of coverage, facilitates the obtaining of images.

Cloud-based pipeline: FastAPI allows uploading files while RunPod GPU pod is used for processing, as it controls the process from start to finish without intervention from the user.

Groundbreaking image creation: Nerfstudio splatfacto 3DGS builds the most realistic models, which can be visualized in real-time.

Structual part: the walls, their angles, and the doors are taken from the splat picture automatically through the use of (structure.py, prototype).

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
The complicated problem in computing is: How can one set of mobile phone videos that are single-lensed and have questionable motion that has happened too quickly turned into a proper 3D Gaussian Splatting model that is good at giving precise measurements in the real world?

This means accomplishing the following:

Strong Structure-from-Motion using casual videos, where spoilers of motion made it difficult to track and ARCore re-anchoring has not provided any information.

The coordination of scales in COLMAP's units of measurement and ARCore's metrics using a certain transform Sim3 with outlier rejection to not leave out any information.

The good initialization of 3D Gaussians that were received from multi-view stereo points in order to avoid any problems with construction of geometries that are not going anywhere (zero-thickness splats, opacity collapse).

The correct setting of GPU resources for managing each loop with sleep modules to prevent the outflow of expenses for cloud resources.

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

ARCore's unnoticed re-anchoring: During the SLAM loop closure, ARCore continuously corrects the world frame, resulting in significant pose shifts of more than 1 m and 28°. In our first test room, all poses taken in the first minute were within 1 m and 28°, consequently, some parts of the room were captured double. But we eliminated this issue by introducing COLMAP poses into the team’s workflow, as it utilizes an entirely different non-ARCore frame. The tracking software is now capable of logging ARCore placements for a more detailed observation of the re-anchoring process itself. Lost tracking moments are compensated by the inertial sensors (fallback.py). 

Lens Distortion: The camera parameters provided by ARCore do not include the values accounting for lens distortions. Using COLMAP self-calibration, we computed radial distortions (k_1 ≈ 0.09, k_2 ≈ -0.22) critical for achieving sub-pixel accuracy.

Degenerative Gaussian splats: We achieved zero-thickness, semi-transparent splats ("cotton-like essence") as a result of a flattening regularizer with adverse effects on Adam's gradient normalization. A detailed root-cause analysis (described in Training_Analysis.md) allowed us to use Nerfstudio's splatfacto, along with measured-point initialization.


Plain or untextured surfaces: The presence of white walls and ceilings leads to losses in tracking and unreliable depth estimations. The solution is represented by the introduction of IQA warnings with texture awareness and capturing suggestions for the ceilings and the floors.

---

### CHUNK 023
- **file:** chapters/chapter2_research.tex
- **section:** Technical Challenges
- **lines:** 88-88
- **words:** 41

original:

GPU memory constraints: The RTX 3070 (8 GB VRAM) limits splat count to approximately 3 million at full resolution. Addressed by training on a 24 GB cloud GPU (RTX 4090 via RunPod) and optimizing memory usage (images in pinned CPU RAM).

rewrite:
Limitations of GPU memory: With the RTX 3070 (8 GB VRAM), the splat count can reach a maximum of roughly 3 million at full resolution. This was dealt with by training on a 24 GB cloud GPU based on the RTX 4090 through RunPod and optimizing memory utilization (images in pinned CPU RAM).


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
The main research conclusions that guided our development:


The poses of SfM were superior to those of ARCore for 3DGS. When examining ARCore poses, their error by median reprojection, in pixels, was equal to 2.32 px; after performing co-calibration via the bundle method, the error was reduced to 0.62 px (after using 626k of observed values), however, nonetheless, the error carried by re-anchoring in ARCore could not be corrected, nor can the lack of a lens model in ARCore be overcome. In addition, the work with colloquial data caused the training view destroying errors identified despite that the error was prior to switching into landmark-based modeling, in general, however, led to improvement in that regard; switching to C-POLMAP enabled us to increase the overall fit (in decibels) of the system level from 21.9 dB and 28 dB to 28 dB (2-3 px); the number of surfaces indicated with extremely high errors had dropped from the earlier records from 7% - 23% to 3% for the searched datasets. It is said that the most successful model trained with earlier poses took place at approximately 22.67 dB. Decided: continue using COLMAP and Sim3 alignment of ARCore for retrieving the most realistic metric scale in the images.

An important point about dense initialization is made by PocketGS [cite: pocketgs], which shows that dense multi-view stereo points bring better reconstruction quality (SSIM 0.834 versus 0.791) in comparison to those obtained through sparse SfM points. The decision made is to begin the process from MVS-measured points that have gone through volume downsampling to 1 cm.
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
Regularization may introduce adverse effects. Our various loss metrics namely the flattening loss, the depth loss, or the pose refinement, performed worse when used together. In terms of performance, the splatfacto baseline recipe produced best results. The splatfacto baseline achieved an amazing score of 27.81 dB in a different scene (roomAttemptSadness2), compared to 24.70 dB achieved by our model with a recipe we modified. Conclusion: The best results can be obtained with standard splatfacto. The custom preprocessing needs to be kept.

Gyro-based frame selection leads to improved image sharpness. The motion blur in the frame is determined based on IMU angular velocity data. It has been determined that the PSNR increased by 0.26 dB. Decision: Write select_sharp.py using the recorded metadata.


---

### CHUNK 026
- **file:** chapters/chapter2_research.tex
- **section:** Techniques Explored and Parked
- **lines:** 106-106
- **words:** 68

original:

Before the switch to image-based poses, the team tried a series of techniques to fix blurry, “cotton-like” models with floating splats. None of them fixed the underlying problem (ARCore's silent re-anchor and missing lens model; finding 1 above); the best model of that period reached only 22.67 dB / 0.782 on held-out frames. They are recorded here so that every technique attempted is visible. Numbers are from docs/progress/.

rewrite:

Prior to utilizing image-based poses, several methods were used by the team in an attempt to solve the issue of the blurred “cottony” models that appeared as floating blotches. None of the methods managed to resolve the root of the problem (ARCore's lack of re-anchoring/lens model; finding 1), and even the best model from this era showed results equal to only 22.67 / 0.782 dB on the validation data. These methods were noted here just for historical purposes. All numbers come from the docs/progress/.

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

During the proposal defense, the committee requested the group to explain the differences between BuildScan 3D and consumer scan applications (Polycam, Luma AI), show metric accuracy as compared to the real measurements, set precise acceptance criteria for the quality of reconstruction, and concentrate on the metrics and the automated process, not addressing the rich UI. All the details of the requests and actions taken are summarized in the action register.

---

### CHUNK 028
- **file:** chapters/chapter3_iteration_plan.tex
- **section:** Proposal Action Register
- **lines:** 8-8
- **words:** 18

original:

Table [ref: tab:actionregister] records the feedback received at the proposal defense and the action taken on each point.

rewrite:

Table [ref: tab:actionregister] records the feedback received at the proposal defense and the action taken on each point.


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

We undertake a strategy that comprises not only two phases, represented by FYP-1 and FYP-2:

Phase 1 (FYP-1, Weeks 1–8): Implementation of the key model; thus, we create the app, reconstruction pipeline and processing server, integrate cloud GPU, and test everything on the real data. As of the mid-evaluation, the pipeline has been completed and improvement works are implemented. The deliverables include a functioning android app, FastAPI server, Run Pod integration, and accurate 3D reconstruction.

Phase 2 (FYP-2, Weeks 9–16): Performance tuning and enrichment of the functions offered. The deliverables include the reduction of time necessary for processing and improvement of robustness of the pipeline; creation of the web-viewing page based on Three.js, which can also measure.

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
Objective: Create the complete system from mobile phone capture to 3D model.

Features: ARCore capture, including IQA & overlay capabilities; COLMAP SfM together with splatfacto training; FastAPI server with RunPod dispatch; upload interface inside the Android application.

Deliverables: Working Android APK, processing server, cloud GPU integration, verification of reconstruction quality in two rooms.

Evidence: Live demo of mobile phone capture → upload → cloud processing → 3D model display.


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
Aim: Speed up processing time, enhance pipeline stability, finalize the structure layer, and integrate measuring instruments.


Characteristics: pipeline performance enhancement (goal <35 minutes on RTX 4090; anticipated value compared to actual results of RTX 3070 being 75 minutes), edge case resilient, wall-snapping measurement using the web viewer, and the finale of the structure layer; Chapters [ref: ch:plan]; modules and timetable.


Expected results: Optimized pipeline with lower processing time; web viewer providing measurement tools; structure layer capable of floor plan export; report on field validation for >=5 rooms.


Proof: Measuring time benchmarks; measuring accuracy comparison with tape measure on at least 5 rooms.


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
The core-pipeline milestones for Iteration 1 have been accomplished; refining work is still going on:

Weeks 1–2: ARCore capture app with primitive recording feature has been achieved.

Weeks 3–4: COLMAP SfM pipeline with ARCore Sim3 alignment has been completed. The main issues leading to low quality of reconstruction (gaps in tracking, distortion of lens, and problems with splats) have been solved.

Weeks 5–6: Live IQA has been realized with coverage overlay and a number of improvements in quality (selection of gyro-aware frames, initial MVS).

Weeks 7–8: been developed processing server, integrated with RunPod, upload interface has built, CI/CD has been finalized.

Current issues to be addressed: 3DGS refinement, 3D mesh generation, finishing the structural layer and the web workspace.


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
Deviation: At first, we came up with our unique script for training (train.py) that included depth supervision, flattening regularization, and pose correction. But after carrying out a thorough analysis (detailed in Training_Analysis.md) we realized that it had proved less effective than Splat Facto. Consequently, we switched to the Splat Facto technique, and kept our unique preprocessing intact. The overall process took around two weeks, but the analysis allowed us to make the right decision about the design.
Recovery: The basic pipeline has been launched, but Iteration 1 is not complete yet: there are still some points left to resolve. Therefore, the FYP-2 project will make use of the one-command v6 pipeline and the processing time decrease, and will make plans for structural layer and web workspace in Iteration 2a-2b. Actual 3D mesh creation is in the scope of the project but is not included into the agenda so far.

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
The system operates with three main types of interaction of the user:

Capture: The user starts the application on Android, initiates recording operation, then walks around the room being shown feedback on the recording quality, and switches the application off after this and taps “Upload & Process.”

Monitor: The user monitors the processing progress showing the current phase, percentage completed, time wasted, and logs.

View/Measure: The user checks the resultant 3D model on the web viewer and can calculate certain distances (FYP-2).

---

### CHUNK 035
- **file:** chapters/chapter4_requirements.tex
- **section:** Use Case Diagram
- **lines:** 12-12
- **words:** 94

original:

The system involves three actors (Figure [ref: fig:usecase]): the End User (captures and views), the Processing Server (manages jobs), and the Cloud GPU (runs reconstruction). The use cases are Record Scan, Upload Dataset, Monitor Progress, View Model, Take Measurement, and Configure Server. Each maps to code: Record Scan to HelloArActivity and CaptureLogger; Upload Dataset and Monitor Progress to ProcessingActivity and the /upload and /status endpoints of server/main.py; Configure Server to the app's settings menu (server URL) and /config; View Model and Take Measurement to the desktop viewer today and the web workspace in FYP-2.

rewrite:
The implementation of the system consists of three actors (See Figure [ref: fig:usecase]): End User (perform captures and views), Processing Server (executes jobs), and the Cloud GPU (carries-out reconstruction). The various examples of use are Record Scan, Upload Dataset, Monitor Progress, View Model, Take Measurements and Configure Server. Each of them has the relevant code: Record Scan corresponds to HelloArActivity and CaptureLogger; Upload Dataset and Monitor Progress refer to ProcessingActivity and the /upload and /status endpoints of server/main.py; Configure Server links to the settings menu of the app (server URL) and /config; View Model and Take Measurements correspond to the desktop viewer today and web workspace in phase FYP-2.

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
Actor: User

Precondition: Application downloaded on Android device compatible with ARCore.

Flow of Events: The User starts the application → presses Record → moves around the space → gets live feedback regarding IQA (blurriness, speed, darkness, texture)→ stops the recording → app displays the summary of quality data.

Postcondition: The information is saved on the device (video, poses, depth, quality, meta).

Actor: User

Precondition: Recording is over; URL of the server is configured.

Flow of events: The User clicks on Upload and Process → the app compresses the files and uploads them onto the server → server creates a job and sends it to GPU → app checks progress every 3 seconds communicating step, percentage, logs.

Postcondition: The information (splat.ply) is ready for downloading.


Exception: The upload does not go through → button for retrying exists; failure of the process → error message shows the step name.

---

### CHUNK 037
- **file:** chapters/chapter4_requirements.tex
- **section:** Functional Requirements
- **lines:** 71-71
- **words:** 36

original:

Table [ref: tab:fr] lists the functional requirements by module. Each has a priority, a status, a verifiable acceptance check, and its trace to the implementing file and the test case (Chapter [ref: ch:testing]) that checks it.

rewrite:
Table [ref: tab:fr] lists the functional requirements by module. Each has a priority, a status, a verifiable acceptance check, and its trace to the implementing file and the test case (Chapter [ref: ch:testing]) that checks it.


---

### CHUNK 038
- **file:** chapters/chapter4_requirements.tex
- **section:** Non-Functional Requirements
- **lines:** 113-113
- **words:** 27

original:

Table [ref: tab:nfr] lists the non-functional requirements with their measurement method and current status. Several are not yet measured; they are marked as such rather than assumed.

rewrite:
Table [ref: tab:nfr] lists the non-functional requirements with their measurement method and current status. Several are not yet measured; they are marked as such rather than assumed.


---

### CHUNK 039
- **file:** chapters/chapter4_requirements.tex
- **section:** Acceptance Criteria
- **lines:** 141-141
- **words:** 56

original:

The acceptance check of every requirement is in Tables [ref: tab:fr] and [ref: tab:nfr]. The project-level acceptance thresholds are: held-out PSNR >= 25 dB and SSIM >= 0.85 (FR-P4; met by v6), distances within 5% of tape measure (FR-P3; met, worst case 0.29%), and processing under 35 min on an RTX 4090 (NFR-P1; not yet measured).

rewrite:
All acceptance criteria are specified in Tables [ref: tab:fr] and [ref: tab:nfr]. Project's acceptance limits are set as: PSNR >= 25 dB and SSIM >= 0.85 (FR-P4; achieved by version 6), difference no more than 5% vs actual measure (FR-P3; achieved with the greatest difference of 0.29%), and processing duration should not exceed 35 min on RTX 4090 (NFR-P1; not measured yet).


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
The BuildScan 3D application is constructed on a three-level client-server architecture.

The client level is represented by a mobile app for Android, which is capable of capturing images using Augmented Reality, uploading them to the server, and displaying the current progress of uploading the images.

The server layer contains a FastAPI backend handling job arrangements, orchestration of the upload process, and handling RunPod workloads.

At the last level of computing, the system performs GPU processing by either using the local computer having all the necessary programs installed or using a pod from RunPod service.

In this system, the data is transmitted in a strict sequence: Capture → Upload → Process → Download. The server is acting as a controller managing the GPU and passing the information to the client through regular polling of the server. Figure [ref: fig:architecture] visualizes how every level function and communicates.

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
The HelloArActivity class is in charge of the AR camera, including screen and adjustment settings, as well as quality.
The CaptureLogger class is the background I/O executor which creates the I/O logs.
The QualityMonitor class is responsible for the analysis of the camera frames in terms of blurry images, brightness, speed of motion, and texture.
The CoverageMap class keeps track of the coverage by using voxels with 10 cm cubes and maps directions with 8 times in the azimuth and 2 times in the elevation.
The CoverageOverlayView class is responsible for the creation of red/yellow/green dots on the camera images. 
The ProcessingActivity class uploads with the help of OkHttp.
Figure [ref: fig:androidarch] illustrates the connection between these classes and screens.

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


---

### CHUNK 043
- **file:** chapters/chapter5_design.tex
- **section:** Interfaces and Dependencies — External dependencies
- **lines:** 153-153
- **words:** 29

original:

Google ARCore SDK (Android), COLMAP 4.2 (SfM/MVS), Nerfstudio 1.1.5 (3DGS training), OkHttp 4.12.0 (Android HTTP client), FastAPI + Uvicorn (Python web framework) and the RunPod API (cloud GPU provisioning).

rewrite:
Google ARCore SDK (Android), COLMAP 4.2 (SfM/MVS), Nerfstudio 1.1.5 (3DGS training), OkHttp 4.12.0 (Android HTTP client), FastAPI + Uvicorn (Python web framework) and the RunPod API (cloud GPU provisioning).



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
Using COLMAP for SfM with ARCore poses: ARCore motion has a 2.32 px median reprojection error (with slow drift); however, using bundle adjustment, the error is reduced to 0.62 px. However, ARCore can re-anchor poses without notifying us (for example, poses before 60 seconds were drifting by 1 m and 28°). There is no mention of lens distortion. 

Compared to COLMAP's self-calibrated SfM with lens distortion (k1 ≈ 0.09 and k2 ≈ -0.22), ARCore's system has problems with both issues. Out of the total recordings, changing the data made our training approach vastly improve the fitting from 21.9 dB to 28 dB and increased the held-out value of SSIM from 0.78 to 0.86. 

Using Splatfacto over custom training: After it became evident that the custom training recipe produces degenerate splats, we opted for Nerfstudio's proven splatfacto implementation. In another room (roomAttemptSadness2), we achieved a score of 27.81 dB held-out using splatfacto compared to 24.70 dB of the corrected custom trainer. 

Using RunPod on-demand over serverless: Our on-demand pods enable fully controlled SSH pipeline, and are suited for long processing times (approximately 75 mins in total on RTX 3070).

---

### CHUNK 045
- **file:** chapters/chapter5_design.tex
- **section:** Architecture Decisions and Rationale
- **lines:** 164-164
- **words:** 21

original:

HTTP polling over WebSockets: Simpler implementation, works across firewalls/proxies, and 3-second polling interval is sufficient for a pipeline that takes minutes.

rewrite:
HTTP polling over WebSockets: Simpler implementation, works across firewalls/proxies, and 3-second polling interval is sufficient for a pipeline that takes minutes.


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
Proposal → Mid: The proposal now includes the guidelines for live IQA and coverage (absent from the original proposal). The training switched to COLMAP SfM after realization of ARCore pose accuracy issue. Meanwhile, the GPU bundle adjustment, Metric3D depth, stereo matcher, depth supervision, floater pruning, median filtering, and post-hoc flat-forcing were all tried but shelved by the team (Section [ref: sec:parked]).

Custom trainer → splatfacto: After two weeks of analysis resulting in identifying six root-cause issues of the splat degeneracy, training switched to Nerfstudio splatfacto. The custom preprocessing pipeline was preserved and verified.

Local-only → local + cloud: RunPod cloud GPU support was added allowing the usage of machines without GPU and achieving speed with GPUs more powerful than the development machine generally used (RTX 4090 as the default one vs RTX 3070, with 8 GB of memory).


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
The fundamental entities of the domain comprise the following:

Scan: The session of recording that generates a dataset (video and sensor files).

Dataset: A set of files from one recorded session (video, representative parameters, depth, quality and meta information).

Job: A process performed along with a status (queued, processing, completed and failed) and its current status in progress and output location. Evolution of the job is illustrated in Figure [ref: fig:jobstate].

Model:  The 3D Gaussian Splatting model (splat.ply). 

Measurement: A distance measured in the metric model (FYP-2).

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
The procedure for the end-to-end pipeline is as follows: 

Fallback (2-minute timeout): Use the readings from the gyroscope and accelerometer datasets taken from the dataset.mp4 file. The tracking gaps from tracking.csv will be identified and converted via the IMU integration at both ends.

Prepare (5-minute timeout): Process the given clip, storing the sharpest frame from total 8 frames in terms of the Laplacian variance appearing in the relevant window under script prepare.py file. The sharpness selective algorithm mentioned in the previous stage is not applied here.

SfM (40-minute timeout): COLMAP will be used to perform feature extraction (using the SIFT algorithm), matching of the features, mapping, adjusting the lens, undistorting images, and aligning to the ARCore.

Exporting (2-minute timeout): It is necessary to convert the result from COLMAP into Nerfstudio transforms.json format.

Train (60-minute timeout): Train the Nerfstudio model by forming a splatfacto during 30,000 iterations with the use of bilateral grid compensation for the exposure and scaling along with keeping the poses.

Exporting the model (5-minute timeout): It is the final stage to create splat.ply model. 

Figure [ref: fig:pipelinesteps] depicts the above mentioned steps with the various timeframes taken during each stage.


---

### CHUNK 050
- **file:** chapters/chapter5_design.tex
- **section:** Process / Behavior Design
- **lines:** 327-327
- **words:** 76

original:

Each step is executed as a subprocess with streaming stdout captured for progress reporting. If a step exceeds its timeout, the process is killed and the job is marked failed. In RunPod mode, whenever a pod has been created it is terminated in a finally block regardless of success or failure, and a watchdog thread terminates it after MAX_POD_LIFETIME (default 7200 s). Figure [ref: fig:sequence] shows the upload → process → download interaction in RunPod mode.

rewrite:
Every subprocess captures the streaming stdout of the executed step. In case of timeout lapse, the process dies and the job is marked as failed. In RunPod mode, whenever a pod was previously created, it is killed in a finally block irrespective of the success of the step. Additionally, this process is killed by the watchdog thread when MAX_POD_LIFETIME (default value is 7200 s) is reached.

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
Build the complete end-to-end pipeline: phone capture → automated upload → cloud GPU reconstruction → metric-scale 3D model. Validate reconstruction quality and metric accuracy on real indoor scans.


---

### CHUNK 052
- **file:** chapters/chapter6_iteration1.tex
- **section:** Selected Use Cases / Features
- **lines:** 7-7
- **words:** 34

original:

UC-1 Record Indoor Scan (with live IQA and coverage guidance), UC-2 Upload and Process (with progress tracking), and UC-3 View the finished model (in the local viewer; the web viewer is deferred to FYP-2).

rewrite:
UC-1 Indoor Scan Recording (with live IQA and coverage guidance), UC-2 Upload and Processing (with process monitoring), and UC-3 Viewing of the completed model (for local viewing; web view will be taken up in FYP-2).



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
The design of Iteration 1 covered three subsystems:

Capture subsystem: ARCore session → CaptureLogger (background I/O) → QualityMonitor (frame analysis at a rate of 6 FPS) → CoverageMap (depth → voxels → overlay).

Upload subsystem: OkHttp multipart POST → FastAPI /upload → Job creation → Pipeline dispatch (local or RunPod).

Pipeline subsystem: consists of six steps in a sequence, whereby each step has a timeout watchdog; all details are provided in Section [ref: sec:process] and Figure [ref: fig:pipelinesteps].

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
Java (for Android app) was used for the implementation as well as Python (for server and pipeline). The following are the important milestones of the project from realization perspective.


Week 1-2: The CaptureLogger was added to the hello_ar_java sample from ARCore to store the sensor data. The synchronization of pose with video was confirmed (r=0.76-0.79 at the zero offset).


Weeks 3-4: The COLMAP pipeline was developed (sfm_colmap.py) and the coordination aligned (OpenGL→OpenCV) and Sim3 metric alignment was performed as well. The issues related to lens distortion were identified and resolved.


Weeks 5-6: The degenerate splat geometry was found out and fixed (6 sources of failure are outlined in “Training Analysis” file). The use of gyroscope-based frame selection and performance analytics suggested a mechanism to deliver best quality output to user.


Weeks 7-8: FastAPI server, RunPod integration with cloud GPU and Android interface were all set up and implemented to complete the project as planned.

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
The feature allows for recording video at 30 FPS, allowing each frame to be precisely logged regarding its pose, tracking state, the presence of feature points, and the depth, and provides metrics for quality and metadata of devices used for the recording. Live IQA (Intra-Quality Assessment) can easily show when tracking is lost with the help of a banner that has a red colour, tracking has issues moving quickly by having an orange hue, and when video quality is unacceptable by shading the information in yellow. Finally, the process ends by closing the recording and having the processing activity started at the server URL described in preferences.

The endpoints and modes of operation of FastAPI in section [ref: sec:components] are switchable at runtime; the step-level watchdog timeout function (Figure [ref: fig:pipelinesteps]); integration with RunPod via pod creation, SSH readiness checking, dependency installation, file upload/download and ending the pod; the API key can be set in the environment or stored in a .env file.


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
The six steps listed in Section [ref: sec:process] are completed in one go: IMU gap bridging, keyframe extraction, COLMAP SfM utilizing lens self-calibration and Sim3 alignment (measured using tape with an error of 0.19% on average and 0.29% at maximum), splatfacto learning with exposure compensation using bilateral grids, and exports as splat.ply. Gyro-aware frame selection (select_sharp.py focusing on exposure metadata) is validated for v4-v6 but not applied in the one-command pipeline yet; prepared by prepare.py it still selects frames in windows with sharpest perceptions from per-window exposures.
GitHub Actions CI (linting, tests with three versions of Python, web and APK building, repository hygiene), CD has been used for creation of built artifacts and releases as well as pull request creating. Details in Chapter [ref: ch:evidence].

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
When ARCore records, it records video and poses of the same frames, but poses are captured only during the tracker's TRACKING state, meaning that the reported poses contain gaps. During the processing of the frames, we interpolate the poses for each frame's PTS (linear interpolation for position and spherical linear interpolation - slerp - for the rotation) and skip the frames within the gaps which lasted more than 0.12 s.

COLMAP's global mapper generates a coordinate system of arbitrary scale. The 7-DOF similarity transform (i.e., rotation + translation + scale) is computed from the matched camera positions of COLMAP against the camera positions of ARCore using RANSAC (2,000 four-point samples, 10-centimeter inlier threshold), followed by a Umeyama refit on inliers, which resulted in an inlier median residual of about 2.5 cm. Since ARCore does the re-anchoring silently, only the largest self-consistent segment ends up being considered an inlier. Any frame that jumps more than 30 cm away from its Fig. [ref: fig:sim3] temporal neighbours is treated as an SfM mis-registration. The resultant metric scale is compared against a tape measure (see Table [ref: tab:tape]).


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
During recording, the execution of the onDrawFrame() method is terminated early just after the rendering of the camera feed and quality overlay (at the rate of 2 Hz). As a result, rendering of all the plane detection, virtual object placement, PBR lighting, work with the cubemaps, and taps is skipped, thus significantly lessening the load on the GL thread.


If there are just flat walls, ARCore cannot track the position, gets lost, and at the moment of re-tracking can continue operating in terms of the new shifted world frame. However, the fallback processes the gyroscope and accelerometers (201 Hz) recorded by ARCore while recalibrating the IMU-to-camera rotation and sensor offsets. It closes the gaps by using the gyro for rotation and an acceleration metering device for positioning with minor cubic correction for both initial and final points of the gap. In case of heading discrepancies at re-tracking stage, the new frame of the map is revealed thus making it possible for the segment following the gap to be aligned with the map by solving the keyframe matching problem.

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
In an actual recording, all three heading jumps were successfully detected and re-alignment was able to reduce the error between specified post-gap frames and previous frames from 49.7 px to 8.2 px. Constraints: Position by IMU can be trusted only if both ends of the gap are anchored and in order to re-align, the user needs to go back into the mapped area (the app warns when tracking failure occurs).

The photorealistic splat model remains unaltered. The room shell is built around it instead: floor plane from splat height distribution; the outer wall in each direction selected separately; corners, which represent the intersections of walls, form a floor polygon; textures, with exclusions of the moving reflections; openings classified as doors. In the first room, wall planes of 6.65–6.68 m × 4.45–4.48 m are confirmed, and 5 doors are detected automatically. The output consists of structure.json (planes, corners, openings), which can be used for automatic floor planning and measurement.

---

### CHUNK 060
- **file:** chapters/chapter6_iteration1.tex
- **section:** Technical Implementation Details — RunPod lifecycle (runpod_client.py)
- **lines:** 87-87
- **words:** 49

original:

The run_pipeline_on_runpod() function wraps the entire pod lifecycle in a try/finally block. Whenever a pod was created, the finally clause calls terminate_pod(), and a watchdog thread enforces a hard time limit, so that that even exceptions, timeouts, or SSH failures do not leave a pod running and accumulating charges.

rewrite:
The function run_pipeline_on_runpod() encompasses the complete lifecycle of a pod within a try/finally clause. It does so through its finally clause, which directly invokes terminate_pod() whenever a pod is set in motion,, and through the enforcement of a hard time limit via a watchdog thread, which ensures that a pod doesn’t stay active, even in cases of exceptions, timeouts, or SSH failures.

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
Gyro-based selection of frames: For a window of length 0.2 s, we calculate the expected motion blur defined as blur_px = ω × t_exp × f, where ω indicates the angular velocity derived from an inertial measurement unit (IMU) in rad/s, t_exp describes the time of exposure and f refers to the focal length in pixels. The frame that possesses the minimum predicted motion blur shall be selected, which is better than the Laplacian measure of sharpness since its performance correlates with the true motion blur according to the correlation r = 0.20.


Coverage probability estimation: 3D space is introduced as being represented with the help of voxels 10 cm each side. Then, each voxel is evaluated according to how many from the 16 directions (from 8 azimuthal and 2 elevation angles) where its observation has taken place. The results are represented with dots: those are red in the case of only 1 direction observed or yellow if 2 or 3 directions were seen while green is used in the case of more than four observations. The maximum number of voxels to be processed is limited to 5000 and number of dots is restricted to 2000 to provide reasonable performance.

Finding splat degeneration: The statistics for each model were calculated (e.g. median values of thickness and width of splats, opacity) and these statistics were compared with respective statistics for the reference implementations of splats. It was found that the interaction of flattening regularizer with Adam method was the primary reason for the creation of zero-thickness splats.

The coverage map is presented in Figure [ref: fig:coverage].

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
It can be shown live:

Android app: Capture a scan of the room with IQA feedback in real time on the coverage.

Upload process: Click on “Upload & Process” and spot progress screen.

Server: Set up a server via scripts/start_server.bat and demo API docs at /docs.

3D model: Show reconstructed splat.ply file in local viewer (scripts/view_splat.bat).

Metric accuracy: Measure the dimensions of table and wall and check against the dimensions of table in [ref: tab:tape].

CI/CD: Show that GitHub Actions are passing in the repository.



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
Summary of all key works based on the available data in this report:

Demonstrated issues with commodity ARCore: a silent 1 m / 28° spatial re-localization and the absence of a lens model (k_1 ≈ 0.09, k_2 ≈ -0.22). The present solution is to utilize ARCore for image-based spatial localization, while preserving gravity and scale in the process.

Fallback IMU tracking with no features, verified through simulations: the error was 3.8 cm vs 30.6 cm interpolated for the period of 9 seconds, and post-video alignment which improved from 49.7 px to 8.2 px.

Guidance for the app capture quality in the process of live video capturing obtained: information on blurriness, speed, and darkness of the scene, as well as a vibration-based warning and the overlay of unaccounted areas in the image.

Gyro-based frame selection, bringing measurable results: improved quality by +0.26 dB /+0.009 SSIM (biggest achievement since version 6).

Millimetric accuracy of measurements obtained from the video taken with the phone, without LiDAR: the average deviation = 4.8 mm (0.19%). Worst-case error = 0.29% as compared to tape measurement.

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
The Iteration 1 status is that the core pipeline has been successfully completed and further refinements are currently being carried out progressively. The results obtained thus far are:


The quality of the reconstruction is well above the required PSNR threshold of 25_dB, with the best model (v6) achieving PSNR of 26.52 dB (0.8886 SSIM) on the 42 frames that were used for testing.


The tape-measure average error is 4.8 mm (0.19%), with the maximum being 0.29% against the target of 5%.


The process takes roughly 75 minutes on the local RTX 3070 (mapping takes 6 minutes, while training takes 45 minutes). The target for the FYP-2 project on RTX 490 is to get that under 35 minutes (the target is theoretical and has not yet been achieved).


The application provides real-time monitoring of quality and coverage.


The server is capable of running both local processing and cloud processing based on the requirements of the application.


The incomplete tasks include (for all tasks apart from mesh creation, please refer to the Remaining FYP Plan chapter):


3DGS refinement: the target is to use v6 recipe for the one-command pipeline and to verify it on the second room.


3D mesh creation: this work is planned but has not yet been scheduled.


Structural layer completion: wall-to-wall dimensions, doors and openings, ceiling-height detection, floor-plan export.

Web workspace: browser viewer with 1:1 measurement.
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
Our approach to testing involves utilizing automated unit/integration tests alongside manual validation of the system on real-life indoor scans. This is justified based on the fact that unit tests manage to test only algorithm correctness (coordinate transformations, file processing, API agreements), while complete validation on actual data checks for reconstruction quality and metrics accuracy, which cannot be tested through unit tests.

Unit testing: Python pipeline modules are verified through pytest using synthetic capture folders with no hardware like GPUs and smartphones. The test runs automatically via GitHub Actions CI whenever there are pushes to branches other than master and when making pull requests or through the CD pipeline.


Linting: There is the running of ruff in CI. Real bugs lead to failure of the run, while issues relating to unused code have no impact on running.


Integration testing: There is testing of the server endpoints using FastAPI test client even though the job starters are replaced by recorders and also the client of RunPod even when the network is faked. There are no executions with the real pod of RunPod.


Android: There are no unit tests for Android Java applications. The capture application is verified on the phone, and its packaging is verified via the APK tests.


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
System tests: Manual execution of the reconstruction pipeline using actual media recordings. Evaluation is conducted by applying the metrics discussed earlier and comparing the outputs of experiments using tape measures. So far, no captured runs of the entire upload → server → RunPod → download path have been made.

Regression tests: Each change in the pipeline is compared against two reference recordings (the first one being the first room, and the second one being newRoomAttemptSadness for the second room) to determine any regressions in quality. The comparison is done manually using the evaluation scripts, not in CI.


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
The pytest suite found in tests/ includes 12 test files along with a shared conftest.py responsible for generating the synthetic ARCore capture folders (without GPU, network, or device). The tests in this suite check only the Python part of the implementation. There are no Java unit tests as the app is tested on an actual device and via the APK/manifest checker test. 

The suite was rerun in its entirety on the latest commit (0d78466, October 22, 2026) with results equal to 194 passes and 1 skipped (and ruff lint being clean). The only skipped test is the APK signing test that depends on the local Java installation. Previously, on October 12, 2026, the CI of GitHub Actions completed the execution of the same suite on versions 3.10, 3.11, and 3.12 of Python with the “Unit tests” phase being completed successfully for all three of them. In case of current re-run, only one version of interpreter was used, therefore the evidence of cross-version testing stays within CI. The term “Pass (manual)” denotes a performed run and its data can be found in docs/progress/. Other tests are tagged as either “Not yet executed” or “Not yet automated”.


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
The retest was not a mere formality: it detected three flaws that were introduced after CI #6 of the RunPod Work on GPU Selection. In the method job-cancel, server/main.py invoked time.time() without importing the time library, which caused the error NameError in POST /jobs/job_id/cancel; the two test files were also out of date with respect to the extended /config payload and the new method dealing with GPU name resolution. All three problems were resolved with the help of commit 0d78466. This alone proves that any automated suite is worth having with the blocking lint gate.

Table [ref: tab:testfiles] shows what all the files of pytest test and Table [ref: tab:testcases] describes number of the tests, expected results and status.

---

### CHUNK 069
- **file:** chapters/chapter8_testing.tex
- **section:** Test Results — Automated tests (CI)
- **lines:** 113-113
- **words:** 119

original:

The pytest suite has 128 test functions in 12 files (one of them parametrised over every Python file, giving 195 collected tests); the full run takes under three seconds. Of the 20 test cases above, 12 are backed by these automated tests (TC-6 is also checked by tape measure), 2 by recorded manual runs (TC-5, TC-13), 2 are only partly executed (TC-11, TC-12), 3 Android cases have no automated test (TC-1 to TC-3), and TC-14 has not been executed. CI runs on every push to non-master branches, on pull requests, and from the CD workflow on master; the CI workflow itself has not yet run on the current master head, so the multi-version evidence remains that of run #6.

rewrite:
There exists the pytest suite comprising 128 testing functions across 12 files for which the entire process takes less than three seconds. Out of 20 test cases mentioned earlier in the report, automated tests support 12 (though TC-6 was also performed using the tape measure). In addition, we have two cases (TC-5 and TC-13) performed manually, while two of the cases were tested only partially (TC-11 and TC-12). The remaining three Android test cases did not have automated tests (TC-1 through TC-3), while TC-14 was not executed. Continuous integration is performed every time there is a new commit to the non-master branches, as well as during pull requests and from continuous deployment on the master branch. The CI process itself has been performed only with respect to run number 6 so that the evidence is only available for that particular run.

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
The model with the best results to date, v6, surpasses both benchmarks of acceptance. The factor that produced the biggest single improvement is gyro-aware frame selection (1166 candidate frames examined, 1108 retained), which resulted in a gain of +0.26 dB (increase of SSIM value by 0.009). In turn, dense MVS initialization caused the second step increment equal to +0.21 dB (SSIM improvement of 0.003), bringing the amount of fused points from 1.15 million to 460, 000 points at the distance of 1 cm.

Table [ref: tab:posefix] demonstrates the performance of the previously employed ARCore-pose pipeline when compared to the current image-based method.

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
The image-based pipeline was also applied to a different room (roomAttemptSadness2) and the provided result by Muhammad Tayyab showed a held-out SSIM of 0.91 and 1% of poorly positioned surfaces. Meanwhile, the held-out PSNR has not been calculated yet for this room.

For roomAttemptSadness2, Nerfstudio's splatfacto trained on our processed data has achieved results of 27.81 dB for held-out views and 28.08 dB for training views compared to 24.70 dB for our own trainer applying the adjusted recipe. This situation has led the developers to migrate to splatfacto. It represents a different scene that has a different protocol than Table [ref: tab:quality] and therefore the score of v6.


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

Acceptance tests compare the system with success criteria as described above:

Metric accuracy: The end-to-end distance measurements between four rigid objects in the software correspond to the tape measure, yielding a mean of 4.8 mm (0.19%) and a maximum margin of error of less than 0.29% (Table [ref: tab:tape]), with the objective magnitude targeting under 5%.

Reconstruction quality: V6 produces 26.52 dB of PSNR / 0.8886 of SSIM on the 42 held-out frames from the first room, surpassing the required thresholds of 25 dB / 0.85. The results from the second room were not included this time, since the held-out frames yielded a score of 0.91 with PSNR not yet measured. Additionally, the images from the room could be captured from the centre of the room where there were no cameras, with ghosts and floating spots removed.

Processing time: The total time measured is approximately 75 minutes on the development RTX 3070 graphics card (23 minutes for feature matching, 6 for mapping, 45 minutes for training). The target NFR-P1 being under 35 minutes is based on the RTX 4090 graphics card and should be evaluated during FYP-2.

Capture usability: No release tests were conducted at this stage. If successful testing is present in the future the usability tests with customers/ testers will be part of FYP-II

---

### CHUNK 073
- **file:** chapters/chapter8_testing.tex
- **section:** Acceptance Testing / Validation — Tape-measure evidence
- **lines:** 169-169
- **words:** 47

original:

Table [ref: tab:tape] compares distances measured in the reconstructed model (first room, image-based pipeline) with a tape measure. Two further measurements on soft edges (a chair and a rug) are recorded in docs/progress/Problems_and_Solutions.md; they are excluded from the rigid-object mean because their endpoints are not well defined.

rewrite:
Table [ref: tab:tape] compares distances measured in the reconstructed model (first room, image-based pipeline) with a tape measure. Two further measurements on soft edges (a chair and a rug) are recorded in docs/progress/Problems_and_Solutions.md; they are excluded from the rigid-object mean because their endpoints are not well defined.


---

### CHUNK 074
- **file:** chapters/chapter8_testing.tex
- **section:** Acceptance Testing / Validation — Tape-measure evidence
- **lines:** 189-189
- **words:** 63

original:

The worst case is 0.29%, far inside the 5% accuracy target. The error does not grow with distance (-8 mm at both 2.8 m and 6.7 m), so the ARCore-derived scale is sound; the small, consistent negative offset most likely comes from where the endpoints are clicked in the viewer. These are four measurements in one room; more rooms are planned for FYP-2.

rewrite:
In the worst case, the figure is 0.29%, well below the accuracy goal of 5%. Unlike other technologies, the ARCore derived scale does not grow with distance (-8 mm at both 2.8 m and 6.7m). It is likely due to where the points are clicked in the viewer that there is a small negative offset. Above are four measurements taken in the same room; more rooms are to come in FYP-2.

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
Loss of tracking while recording: ARCore gets confused in plain corridors or if it is moved quickly. Hence, the app shows a red notification “Tracking Lost,” and stops recording the quality data. The IMU fallback changes this. The positioning error was 3.8 cm for the IMU fallback as opposed to 30.6 cm for interpolation at 9s of simulated gap. The post-realignment error after relocalization is now down to only 8.2 px compared to the original 49.7 px (Table [ref: tab:imufallback]). The image-based pipeline also captures most frames in the gap according to COLMAP (748 of 759 in the second room). Relocalization would fail if the user never returns to the area that has previously been recorded. Those will be tagged as unverified and hence not used in training. Solution: There is a Live IQA warning that advises the user to slow down, and the coverage overlay shows unscanned areas.

White walls: Rooms where bare walls have a large area have very few points in the SfM point cloud in these regions. The model will show some blurring or empty spaces. Solution: The IQA “low texture” warning suggests the user takes some other nearby textured objects.

Mirrors and glass: Very reflective materials lead to incorrect depth estimates and SfM outliers.

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
Network Failure during upload: If the HTTP connection happens to be interrupted during the upload of the file, the ProcessingActivity displays an error stating that there has been a failure and provides a retry option. On the server, when an upload is missing a necessary file or has a faulty depth zip, the server cleanly rejects the upload (TC-8). Status: Done partially; there has been no end to end testing of the interrupted upload.

RunPod Pod Failure: If in case the SSH does not come to readiness (pod crash/software that uses GPU fails), the give-up time set in wait_for_ready is 300s while polling every 10s, which means the pod will eventually be terminated in inevitably (finally block). Status: Implemented; the timeout has been unit tested under faked API conditions (TC-7), while the termination path is yet to be applied to a real pod.


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
Status update on the implementation of acceptance criteria for Iteration 1 (core pipeline completed, refinement ongoing):

Reconstruction quality: version 6 generates average reconstruction quality of 26.52 dB / 0.8886 for the first room (the requirements are >25 dB, >0.85). For the second room, the SSIM results are 0.91; PSNR has not been measured yet.

Metric accuracy: the average is 0.19%, while in the worst case it is 0.29%, compared to the target of 5% (Table [ref: tab:tape]).

Processing time: the value is yet to be verified. Previous tests showed that it takes 75 minutes on an RTX 3070; while the target is less than 35 minutes on the RTX 4090 (NFR-P1).

Pod lifecycle: the first checks were made. The terminate_pod() function was called from finally blocks, and the client side of the solution was tested with faked API, but there were no live tests yet with the pods.

CI pipeline: all tests were re-run green on the latest versions of the master (total of 194 tests were passed and one skipped; all checks were successful); CI run #6 covered Python versions 3.10 to 3.12.

Not executed yet: Android unit tests (TC-1 to TC-3), processing timeout (TC-14), app-to-RunPod full run.

The remaining validation required for FYP-2 includes testing measurement accuracy in at least three additional rooms that feature different geometrical layouts, accuracy assessment of structural-layer measurements like wall lengths as per a tape measure, doors found versus doors counted manually, web viewer effectiveness test, and stress testing involving large-sized rooms, long duration recordings, and fairly simple Android devices.

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
The Android capturing application has been developed (including ARCore pose, depth and quality logging features, live IQA, coverage overlay and upload interface), the reconstruction mechanism has been implemented (including IMU fallback, key frame extraction, COLMAP SfM with Sim3 metric alignment and Nerfstudio splatfacto training mechanism, model export (although no gyro-aware frame selection has been implemented yet), the processing server (introducing FastAPI with local and RunPod cloud GPU options and with pod termination function), the CI/CD system (including lint, unit testing, apk and web build and hygiene testing functions), the server launcher (start_server.bat, which supports .env files), and root-cause investigation of degenerate splat geometry (containing several reasons in respective document).


---

### CHUNK 079
- **file:** chapters/chapter9_development_evidence.tex
- **section:** Work Remaining
- **lines:** 8-8
- **words:** 69

original:

Scheduled in Chapter [ref: ch:plan]: the Three.js/WebGPU splat viewer with orbit controls; point-to-point measurement; completing the structural layer (wall-to-wall dimensions, doors and openings, ceiling-height detection, floor-plan export) with wall snapping and a floor-plan view; 3DGS refinement (one-command v6 pipeline, second-room validation, IMU-driven motion-blur modelling); field validation on >=3 more rooms; and usability evaluation with external users. 3D mesh creation is in scope as planned work but not yet scheduled.

rewrite:
Found in Chapter [ref: ch:plan]: the Three.js/WebGPU Splat viewer with orbit controllers, point-to-point measurement, completion of the structure layer (wall-to-wall dimensions of the walls, doors and openings, ceiling height identification and floor plan export), wall snapping and floor-plan display, improvement of 3DGS (one-click pipeline of v6 version, verification of the second room, motion blur modeling based on IMU); validation in the field is to be done in 3 or more rooms, usability check will involve outside users; but the creation of the 3D mesh is still in the roster but not planned yet.

---

### CHUNK 080
- **file:** chapters/chapter9_development_evidence.tex
- **section:** Individual Responsibilities
- **lines:** 12-12
- **words:** 31

original:

The primary evidence of each member's contribution is the set of modules they own: the files whose commit history carries their name (git log – <file>). Table [ref: tab:responsibilities] lists them.

rewrite:
The primary evidence of each member's contribution is the set of modules they own: the files whose commit history carries their name (git log – <file>). Table [ref: tab:responsibilities] lists them.


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
Project lead. Developed the processing server (FastAPI endpoints, job model with per-step timeouts, local pipeline runner) and RunPod integration (pod creation, SSH-ready for rituals, remote pipeline, termination in finally blocks). Developed the application's upload and progress screen with the scan gallery/detail screens, executed the main AR activity and coverage overlay work, created the web UI prototype, and wrote the proposal and a report.


Developed the CI/CD infrastructure (lint, test and build workflows on three versions of Python, Android build and signing checks, repository hygiene, releases) and wrote the entire automated test suite that backs the “Pass (CI)” results in Chapter [ref: ch:testing]. Provided contributions pertaining to trainer fixes and ARKitScenes trainer experiments.


Constructed the reconstruction pipeline: IMU fallback and re-alignment, keyframe and gyro-aware frame selection, bundle adjustment, the COLMAP SfM stages with Sim3 metric alignment, and an initiative to develop a dense MVS and evaluate its structural layer and evaluation tools. Captured app logging and in-line IQA, performed training analysis, and produced the v6 model, the tape-measure validation, and the result of the second room.

---

### CHUNK 082
- **file:** chapters/chapter9_development_evidence.tex
- **section:** Contribution of Each Team Member — Commit counts
- **lines:** 44-44
- **words:** 97

original:

The repository has 133 commits: Muhammad Umair 85, Zaid Fareed 26, Muhammad Tayyab 20 (committing as “BlazingBeam”), and 2 automated commits by the GitHub Actions bot. These counts reflect differing commit granularity, not differing effort. Umair commits each small change separately; Tayyab works in large batches, so a single commit of his often carries a whole pipeline stage (for example, the commit that introduced image-based SfM poses and lens self-calibration, or the one that introduced gyro-aware frames, dense MVS initialisation and the structural layer). The owned modules above, not the commit counts, are the evidence of contribution.

rewrite:
In total, there are 133 commits divided among four contributors: 85 by Muhammad Umair, 26 by Zaid Fareed, 20 by Muhammad Tayyab (under the alias of “BlazingBeam”) and two automated commits from the GitHub Actions bot. These numbers are not an indicator of effort levels by the contributors; rather, they reflect the way each of them commits their changes. For example, Umair commits every little change separately, Tayyab aggregates many changes together, and thus a single commit of his typically represents a significant stage of development. Therefore, the contributions of each of the listed modules are more reliable evidence of participation in the project than the number of commits.


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
The GitHub is used to host a project repository that has the following statistics – 

Repository – github.com/Umairishuman/FYP (private)

Branches – master branch (stable) including work branches such as ci/github-actions, ci/pipeline-updates and exp/trainer-arkitscenes

Commits history – 133 commits (85/26/20, including 2 other bot commits)

CI – GitHub Actions is being implemented on work branches, pull requests and (through the CD process) on the master branch: ruff lint and pytest in Python versions 3.10, 3.11, and 3.12; Node.js build of the web UI (this is just a placeholder of FYP-2); Gradle APK build checking signing and the manifest; repository hygiene including limitation of files’ sizes, secrets checking, and workflow’s linting

CD – on master branch’s push build artifacts; on tagged version do GitHub releases with the APK and web app bundle

Code review – there is a pull request template with area checkboxes as well as testing checklist

Task monitoring – there is docs/progress/TODO.md, which is a dated task log of various statuses marked with links to commits and analysis documents

Table [ref: tab:repo] matches repository layout with the modules mentioned in this paper.

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
IMPORTANT: Generative AI Tool Disclosure

In compliance with university policy, we disclose the use of the following AI-assisted development tools:

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
The team developed all the algorithms involved in the project, which includes Sim3 alignment, application of the gyro-aware frame selection method, building coverage maps, IQA methods, and managing the entire RunPod lifecycle. The AI applications were utilized for creating the initial program code, debugging, giving explanations, and making reports. The rest of material including architecture development, experimental design and data interpretation, and the reasons behind making particular design decisions were produced by the team. The output of AI software was well-studied by the members of the team before being integrated into the main system code.

The software tools that were used by the team included Android Studio (Ladybug) with Android Gradle plug-in, Visual Studio Code with Python and Java plug-ins, Git and GitHub, Postman for testing API, ADB for debugging, and NVIDIA Nsight for profiling GPU during training experiments.

---

### CHUNK 086
- **file:** chapters/chapter9_development_evidence.tex
- **section:** External Components and Dependencies
- **lines:** 165-165
- **words:** 20

original:

All external components are used under permissive open-source licenses compatible with academic use. No proprietary or restrictively-licensed code is included.

rewrite:
All external components are used under permissive open-source licenses compatible with academic use. No proprietary or restrictively-licensed code is included.


---

### CHUNK 087
- **file:** chapters/chapter9_development_evidence.tex
- **section:** Risks and Mitigation
- **lines:** 169-169
- **words:** 46

original:

Table [ref: tab:risks] is the project's risk register. Likelihood and impact are rated Low, Medium or High by the team; each risk is handled by the member who owns the affected modules (Table [ref: tab:responsibilities]). The register is reviewed at the start of each FYP-2 iteration.

rewrite:
Table [ref: tab:risks] is the project's risk register. Likelihood and impact are rated Low, Medium or High by the team; each risk is handled by the member who owns the affected modules (Table [ref: tab:responsibilities]). The register is reviewed at the start of each FYP-2 iteration.


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
API credential management: The RunPod API credential stays in memory via some environmentally loaded values or an environmental file and is never mentioned in the source code directly. Nonetheless, this .env file was uploaded to the repository on the 18th of October, 2026, contrary to NFR-S2; thus, it should be removed and renewed.


CI secret scanning: The CI hygiene job cannot pass if it keeps a .env file or key or certificate documents; also, it looks for any sensitive documents (except for RunPod keys ones) through the scanned material. The last time CI worked (job # 6) was prior to .env loading. As per the job requirement, next CI process would not be possible to run in master before the file is eliminated.  


Data privacy: The gathered scanning data is sent to the processing server via a local network. When in production, an HTTPS mode will need to be applied. Collected data can be processed and deleted via the API. 


Cloud GPU security: the RunPod pods are formed when they are needed and can only be used in a single operation; no data can be kept on the cloud GPU after.

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
Mirrors and Glass: The presence of highly reflective surfaces results in SfM outliers with an inaccurate depth model found in those areas. The planned FYP-2 experiment will attempt to detect and mask reflective surfaces.

Large Rooms: Rooms that exceed roughly 8×8 meters may exceed the GPU capacity limit when training takes place on an RTX 3070 (8 GB). It is expected that a cloud GPU with 24 GB of memory can handle larger scenes. However, this fact has yet to be confirmed.

Outdoor Scenes: The system has been designed for indoor use; outdoor scenes with sky, vegetation, and long distances are beyond the system capabilities.

Real-Time Processing: Processing takes 75 minutes on the developing RTX 3070, whereas cloud-GPU timing has yet to be carried out. Real-time processing is not possible using existing 3DGS training times.

Single-Floor Only: The current coverage map and measurement tools rely on a single-floor environment. Multi-floor buildings require manual editing.

No Web Viewer Yet: At the moment, 3D models can be viewed only in a desktop program. A web-based viewer based on Three.js will be developed for FYP-2.

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
FYP-2 has three main objectives: (1) completing the enhancement of the reconstruction approach and accelerating it; (2) creating the structural feature (wall planes, corners, walls, door identification and layout) that enables the photorealistic model to be suitably measured; and (3) developing a web workspace with a 1:1 measurement. The basic capture → upload → reconstruct pipeline was created during FYP-1 whereas FYP-2 completes and verifies it.

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
Pipeline Optimization Module: This involves utilizing the v6 recipe comprising of gyro-selected frames, dense MVS initialization, and finer densification, as the one-command pipeline for validation in the second room. Also, it entails reducing the end-to-end processing time from 75 minutes on the development RTX 3070 to less than 35 minutes on the RTX 4090. The 35-minute benchmark is the projected target instead of a measurement. Techniques employed will include ARCore-pose-guided matching or sequential matching pairs in place of exhaustive COLMAP matching, fewer training iterations and fewer keyframes in slow walks.

Reconstruction Improvement: This includes IMU-prompted motion blur modeling of the training data and rolling shutter calibration using the per-frame exposure time and rolling shutter information logged by the application. This means that according to the gyroscope, the median training frame is reported as being blurred by between 6 and 12 pixels. In addition, there will be ARCore-aligned images with anchor detection based on the logged anchor information.

Robustness Improvements: Enhance the handling of mirrors and glass surfaces (by masking reflective areas), textureless walls, large hallways, and different types of lighting conditions.

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
Structural Layer Module: Finish the implementation of structure.py, which currently creates a room shell next to the splat model: the floor planes and walls, junctions of neighbouring walls (e.g., room dimensions: 6.65-6.68×4.45-4.48 m) and openings (i.e., 5 automatically detected doors). Tasks remaining include measuring wall-to-wall distances, treating doors and other openings as first-class entities, fixing the ceiling height measurement and developing an automatic floor plan generation process.

Web Workspace Module: A Three.js / WebGPU-based Gaussian splat viewer with orbit/pan/zoom controls. It works in any modern web browser. It can load splat.ply with structure.json file from structural layer and display the floor plan view.

Measurement Module: A point-to-point measurement tool capable of measuring distance in metric units within a 3D model. The user clicks two points representing the shape on either splat or structural layer wall, and the system calculates the distance in m in a Sim3-aligned coordinate frame.


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
Development of 3D Mesh: Generate a 3D mesh of the room scanned during the reconstruction process in parallel with the creation of the splat model. This task is on the agenda as it was planned, but it is yet to be allocated into an iteration.

Module for Dashboard: Dashboard accessible via web showing scan history, status of processing, miniature size of models created, and records of measurements.

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
Iteration 2a (Weeks 1-4): Optimizing the pipeline and developing the web viewer. The result is a v6 pipeline that requires just one command; processing takes less than 35 minutes on the RTX 4090 (calculation yet to be verified); and a browser viewer that allows for point-to-point measurements in a minimum of 3 rooms.

Iteration 2b (Weeks 5-8): Robustness, improving the reconstruction process and structural component. The result is a better handling of edge cases, as well as adding a structural layer containing the wall lengths, location of the doors, and the floor plan; on the visualization website, it will be possible to snap the measurements to the walls. 

Iteration 2c (Weeks 9-12): A dashboard, field testing, and fine-tuning the software. The deliverable is a complete workspace on the web alongside the user testing of the application on at least 5 rooms and the final report.

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
Take the v6 recipe and fit it into the one-command pipeline; substitute exhaustive matching with ARCore-pose-guided or sequential pairs (week 1).


Decrease the number of iterations with splatfacto and keyframes for slow walks; test every adjustment in both reference rooms (week 1-2).


Create a project in Three.js equipped with a Gaussian splat renderer and camera controls (week 2).


Create a measuring device: ray-cast click – > nearby splat > 3D coordinates – > distance display (week 3).


Test measurement accuracy compared to a tape-measure on 3 rooms (week 3-4).


Connect the viewer to the FastAPI backend for model loading (week 4).


Add mirror/glass reflective-surface detection and masking features (week 5).


Experiment with IMU-based motion-blur and rolling-shutter modeling on recordings that support per-frame exposure metadata (week 5-6).


Structural layer: fix ceiling height detection; create doors and openings as separate objects with their dimensions (week 6).


Structural layer: measure dimensions, automate room layout exporting from the floor outline (week 7).


Use structure.json in the browser; make measurements snap to walls; add floor view (week 8).


Create the web dashboard: list of scans, processing statuses, model thumbnails (week 9-10).


Conduct usability tests with 5+ external users; obtain usability feedback (week 10-11).


Resolve usability problems; prepare documentation (week 11-12).

---

### CHUNK 096
- **file:** chapters/chapter10_fyp2_plan.tex
- **section:** Implementation Plan — Iteration 2c: Dashboard + Final Validation (Weeks 9–12)
- **lines:** 61-61
- **words:** 13

original:

Final validation: measurement accuracy, structural-layer accuracy, processing time on 5+ rooms (week 12).

rewrite:
Final validation: measurement accuracy, structural-layer accuracy, processing time on 5+ rooms (week 12).


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
Measurement accuracy: Compare point-to-point measurements in the web viewer against tape-measure ground truth on >=5 rooms of varying size and geometry. Target: error within 5% of tape measure, extending the current four-measurement evidence (mean 0.19%) to more rooms.

Structural layer: For each test room, compare extracted wall lengths against tape measure (target: within 5%) and the detected doors against a manual count.

Web viewer performance: Maintain >=30 FPS on a mid-range laptop (integrated GPU) for models up to 2 million splats.

Usability testing: Task completion rate >=90% for first-time users performing capture, viewing, and measurement tasks.

Processing time: End-to-end pipeline <35 min on RTX 4090 (projected target; currently 75 min measured on RTX 3070). Benchmark each optimization individually.

Cross-browser: Verify viewer on Chrome, Firefox, and Edge.


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
Accuracy of the measurement: Compare distances in web viewer to distance on the tape measure for at least 5 rooms with different sizes and designs. Required accuracy: no more than 5% off the tape measure readings, which in turn allows us to broaden our evidence that includes just four measurements with the mean of 0.19%.

Structure level: For each room, wall lengths formed should be compared to the tape measure (required accuracy: no more than 5%) and the closed doors should be compared to a manual count.

Web viewer efficacy: At least 30 FPS must be achieved on a medium computer (with integrated GPU) for models up to 2 million splats.

Usability testing: The completion rate for tasks should be at least 90% for new users performing capture, viewing, and measuring tasks.

Processing time: The entire process should take no more than 35 minutes on RTX 4090 (the current time is 75 minutes on RTX 3070).

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
Android APK: The product to measure the application’s performance through live IQA, coverage overlay, and uploading functionalities.


Web app: Gaussian splatter viewer with 1:1 measurement tools and floor plan view.


Processing server: FastAPI with local and cloud GPU compatibility.


Structural component: per-room structure.json (planes, corners, walls length, doors and openings) and floor plan export.


Validation report: accuracy of measurements taken in at least 5 rooms, structural component accuracy and time measurement statistics.


Documentation: user manual, API documentation, deployment manual.


Codebase: complete repository with CI/CD process, tests and documentation.


Final report: FYP-2 document with complete results and analysis.

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
BuildScan 3D takes a simple video recorded with a common Android phone and converts it into a metric-precision 3D Gaussian Splatting model of the room. At the moment, Iteration 1 is in the middle of its development plan, with the pipeline being complete and changes being made in how the input data is processed.

The design was determined by four major findings: (1) in the place of ARCore poses for training, image-based COLMAP poses used for the training purposes; wasting ARCore's silent re-anchor and lens model has increased the image fit from 21.9 dB to 28 dB and has improved the held-out SSIM from 0.78 to 0.86; (2) dense MVS initialization contributes to the geometry of splats; (3) excessive regularization brings the quality down when used along with Adam; (4) the choice of frames based on gyrosensor data performs better than the selection based on metrics of sharpness.

There is a three-tier system that consists of Android capture application with live IQA and coverage overlay, processing server with FastAPI and RunPod dispatch, and COLMAP + splatfacto pipeline with Sim3 metric alignment system working with CI/CD via GitHub Actions. The best current model (v6) has reached 26.52 dB which means the original signal to noise ratio (PSNR) of > 25 dB and 0.8886 which means the original signal to noise ratio (SSIM) of > 0.85 over 42 held-out frames. Tape measure checks give a 4.8 mm average error which is equal to 0.19% over rigid objects with the worst case scenario being 0.29% which is much better than the expected 5% accuracy. Processing takes approximately 75 minutes on RTX 3070 video card while the expected result of below 35 minutes using RTX 4090 video card is not confirmed yet.

---

### CHUNK 101
- **file:** chapters/conclusion.tex
- **section:** Conclusion — Risks and next steps
- **lines:** 9-9
- **words:** 93

original:

The risk register (Table [ref: tab:risks]) tracks twelve risks; the highest are cloud GPU cost (cost per scan not yet measured), the unmeasured RTX 4090 processing time, tracking loss on featureless surfaces, and delivering the remaining FYP-2 scope. Mirrors and glass remain a known limitation. FYP-2 completes 3DGS refinement, the structural layer (wall planes, corners, wall lengths, door detection) with automatic floor plans, and the web workspace with point-to-point 1:1 measurement, and validates them on more rooms. 3D mesh creation is also in scope as planned work and has not yet been scheduled.

rewrite:
Twelve risks have been identified and tracked in the risk register (Table [ref: tab:risks]), of which the most prominent are cloud GPU costs that have not been fully established mechanics of the RTX 490 processing time, inability to keep track of changes on plane surfaces, and providing the remaining project scope of the FYP-2. Mirrors and glass are still considered as the limiting barrier. The FYP-2 implies working on 3DGS improvement. Moreover, creating 3D models is regarded as a planned task that has not been contracted yet.

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
The team held two meetings with the supervisor, Mr. Furqan Nasir, before the mid-evaluation. Their dates were not recorded at the time, so they are listed in order rather than by date. No formal minutes were taken, and no decision in this report is presented as having been approved by the supervisor.


---

### CHUNK 103
- **file:** chapters/appendix_meetings.tex
- **section:** Supervisor Meetings
- **lines:** 18-18
- **words:** 19

original:

The dated record of the work itself is the progress log below and the commit history (Chapter [ref: ch:evidence]).

rewrite:

The dated record of the work itself is the progress log below and the commit history (Chapter [ref: ch:evidence]).

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
Detailed development progress is maintained in docs/progress/TODO.md. Key milestones:

ARCore capture app: Basic recording → pose sync validation → IQA → coverage overlay → upload UI. Incremental feature additions documented with timestamps.

Reconstruction pipeline: Best custom-trainer model on ARCore-derived poses (gs_colmap_nc, 22.67 dB / 0.782 held-out) → image-based COLMAP poses (training-view fit 21.9 → 28 dB; held-out SSIM 0.78 → 0.86) → v3 (26.04 dB / 0.8756 on the 42-frame held-out set) → gyro-aware frame selection (+0.26 dB / +0.009 SSIM) → dense MVS initialisation (+0.21 dB / +0.003 SSIM) → v6 (26.52 dB / 0.8886). Each improvement documented with before/after metrics.

Quality debugging: Two-week root-cause analysis documented in Training_Analysis.md covering 6 identified causes of degenerate splats, with per-cause experiments and metrics.

Server and cloud: FastAPI server → local pipeline runner → RunPod integration → guaranteed pod lifecycle. Problem-solution pairs documented in Problems_and_Solutions.md.


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

25 problems encountered during development are documented in docs/progress/Problems_and_Solutions.md. The most significant:

ARCore silent re-anchoring causing pose discontinuities (solved: anchor logging + IMU fallback)

COLMAP lens distortion not matching ARCore intrinsics (solved: self-calibration)

Degenerate splat geometry from custom training recipe (solved: adopted splatfacto)

30 FPS input overwhelming COLMAP matching (solved: keyframe selection, one sharp frame per window)

Motion blur in training frames, 6–12 px median (solved for v4–v6: gyro-aware frame selection, +0.26 dB / +0.009 SSIM)

GPU memory overflow on the 8 GB RTX 3070 with >1000 full-resolution frames (solved: skip page-locked image caching above 4 GB; default densification thresholds)

---
