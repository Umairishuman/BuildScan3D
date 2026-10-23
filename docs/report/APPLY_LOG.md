# Apply log: chunk rewrites

Prompt B of `docs/report/CLOUD_PROMPT_SPLIT.md`, applied on 2026-10-22 to the chunks in `docs/report/REPORT_CHUNKS.md` (rewrites from `ebde511`). Not compiled.

## Summary

- **Applied:** 85 chunks, one commit per source file (12 files).
- **Identical to the original, left untouched:** 18 chunks (028, 037, 038, 042, 043, 045, 048, 051, 073, 080, 084, 086, 087, 096, 102, 103, 104, 105).
- **Skipped as empty:** 097.
- **Held back:** 098 (see below).
- **Corrections to the rewrites:** 195 across 75 chunks: 28 honesty markers and mandated wording restored, 17 citations or references restored, 137 factual or technical errors corrected, 13 typos or broken grammar fixed.
- **Spans that no longer matched:** none. Before each replacement the span was re-rendered and compared with its `original:` text; all matched. Edits ran bottom-up within each file, and line counts are unchanged.
- **Render-back check:** every rebuilt span renders back to exactly the corrected rewrite.
- **Static check after applying:** braces and environments balanced, 59 `\ref`s all resolve, 9 `\cite`s and 43 `\label`s unchanged, 9 figures present.
- **Protected figures:** every ground-truth number present before the pass is still present.

The correction approach (keep your wording, fix only factual and technical errors, restore dropped citations and references, enforce the number and honesty rules) was chosen by you before applying. Each correction is a literal `old → new` edit on your rewrite text, listed below so you can review or revert it.

## Chunk held back

- **098 (`chapter10_fyp2_plan.tex`, Deployment Plan).** The rewrite in this block is a version of the *Testing and Validation Plan*, which is chunk 097's text (measurement accuracy, structural layer, web viewer performance, usability, processing time). Chunk 097 was left empty. Applying 098 as filed would have replaced the deployment plan (server, GPU processing, APK distribution, CI/CD) with a second testing plan. Both sections keep their original text. If the 098 rewrite was meant for 097, move it to 097's `rewrite:` block (it drops 097's cross-browser item) and rerun Prompt B.

## Numbers

No invented measurement was accepted. Numbers in a rewrite that were not in its original:

| Chunk | Number | Outcome |
|---|---|---|
| 064, 101 | 490 ("RTX 490") | Typo for RTX 4090; corrected. |
| 070 | "460, 000" | The ground truth is ~460k; written as "about 460,000". |
| 018 | 6000 | The original's $6,000; kept. |
| 049 | 30,000 | The original's 30k iterations (code default 30000); kept. |
| 061 | 5000, 2000 | The original's 5,000 voxels / 2,000 dots; kept. |
| 005 | 12 | "twelve" risks written as a numeral; kept. |
| 039, 063, 098 | 6, 5, 2, 4090, ... | Already in the brief's ground-truth table or the original; kept (098 not applied). |

Factual statements that changed numbers' meaning were corrected: "more than 1 m and 28°" back to "up to" (022); poses "within" 1 m back to "off by" (022); worst case "less than 0.29%" back to "0.29%" (072); the r = 0.20 correlation re-attributed to the Laplacian measure (061).

## Honesty markers and mandated wording restored

Rule 2 of Prompt B: a rewrite may not weaken "not yet measured", "projected", "not yet scheduled" and similar, or the status wording the brief mandates ("core pipeline complete, refinement ongoing"; planned and prototype status).

| Chunk | Your text | Applied as | Why |
|---|---|---|---|
| 001 | to create floor plans and measure objects; | to create floor plans and measure objects (prototype built); | restored status: the structural layer is a prototype |
| 001 | (5) a web viewer for measurements | (5) a planned web viewer for measurements | restored status: the web viewer is planned, not built |
| 002 | At the mid-point evaluation, we can say that the first iteration has made progress in terms of the total completion of core pipeline and the refinement process: | At the mid-point evaluation, Iteration 1 stands at core pipeline complete, refinement ongoing: | restored the mandated status wording (brief decision 8); the rewrite's phrasing implied total completion |
| 004 | however, the cloud-GPU timings are yet to be measured. | however, the cloud-GPU timings are yet to be measured, and the under-35-minute RTX 4090 figure is an FYP-2 projection. | restored the projection label (brief decision 1) |
| 005 | The cloud GPU availability and per-work charge as per known data; | The cloud GPU availability and per-job cost (not yet measured); | honesty marker: 'as per known data' inverted 'not yet measured' |
| 010 | aiming for a total time of 35 minutes on a cloud RTX 4090 (the current processing time is 75 minutes on the development RTX 3070) | aiming for a total time under 35 minutes on a cloud RTX 4090 (a projection; the current measured processing time is 75 minutes on the development RTX 3070) | restored 'under' and the projection label (brief decision 1) |
| 011 | making of an architectural drawing (prototype was created in FYP-1) | making of floor plans (prototype was created in FYP-1; completion in FYP-2) | the output is floor plans; restored completion status |
| 012 | Web Viewer: Viewer created | Web Viewer Module (FYP-2): Viewer created | module name and status: planned for FYP-2 |
| 014 | (FYP-2 goal; aims achieved but yet not measured; the present result is 75 minutes on the working RTX 3070) | (FYP-2 goal; projected and not yet measured; the present result is 75 minutes on the development RTX 3070) | honesty marker: 'aims achieved' contradicted 'projected' |
| 020 | Structual part: the walls, their angles, and the doors are taken from the splat picture automatically through the use of (structure.py, prototype). | Structural layer: the wall planes, corners, wall lengths and doors are taken from the splat model automatically through the use of structure.py (prototype); co… | spelling; corners not angles; restored status |
| 029 | As of the mid-evaluation, the pipeline has been completed and improvement works are implemented. | As of the mid-evaluation, the core pipeline is complete and refinement is ongoing. | mandated status wording (brief decision 8) |
| 031 | (goal <35 minutes on RTX 4090; anticipated value compared to actual results of RTX 3070 being 75 minutes) | (goal <35 minutes on RTX 4090, projected; 75 minutes measured on RTX 3070) | honesty marker: the 35 min figure is a projection |
| 049 | The sharpness selective algorithm mentioned in the previous stage is not applied here. | The gyro-aware selection of select_sharp.py that produced v6 is not yet applied here. | honesty marker restored; the previous stage does not mention it |
| 059 | which can be used for automatic floor planning and measurement. | which can be used for automatic floor planning and measurement. Ceiling-height detection is not yet reliable and is FYP-2 work. | honesty marker restored |
| 064 | The Iteration 1 status is that the core pipeline has been successfully completed and further refinements are currently being carried out progressively. | The Iteration 1 status is core pipeline complete, refinement ongoing. | mandated status wording (brief decision 8) |
| 064 | The target for the FYP-2 project on RTX 490 is to get that under 35 minutes (the target is theoretical and has not yet been achieved). | The target for the FYP-2 project on RTX 4090 is to get that under 35 minutes (the target is a projection and has not yet been measured). | typo RTX 490; honesty marker: projection, not yet measured |
| 069 | The CI process itself has been performed only with respect to run number 6 so that the evidence is only available for that particular run. | The CI workflow itself has not yet run on the current master head, so the multi-version evidence remains that of run number 6. | garbled; restored the 'not yet run on master' marker |
| 072 | The target NFR-P1 being under 35 minutes is based on the RTX 4090 graphics card and should be evaluated during FYP-2. | The NFR-P1 target of under 35 minutes on the RTX 4090 graphics card is a projection for FYP-2 and has not yet been measured, so NFR-P1 is not yet verified. | honesty markers restored: projection, not yet measured, not yet verified |
| 072 | Capture usability: No release tests were conducted at this stage. If successful testing is present in the future the usability tests with customers/ testers wi… | Capture usability: Not yet formally evaluated. Usability testing with external users is planned for FYP-2. | garbled; restored the 'not yet' marker |
| 075 | lead to incorrect depth estimates and SfM outliers. | lead to incorrect depth estimates and SfM outliers. Status: Known limitation; documented for FYP-2 investigation. | restored the status line |
| 077 | while the target is less than 35 minutes on the RTX 4090 (NFR-P1). | while the target is less than 35 minutes on the RTX 4090 (NFR-P1), which is projected and not yet measured. | honesty markers restored |
| 077 | Pod lifecycle: the first checks were made. | Pod lifecycle: partly verified. | honesty marker restored |
| 079 | but the creation of the 3D mesh is still in the roster but not planned yet. | 3D mesh creation is in scope as planned work but not yet scheduled. | honesty marker: in scope, not yet scheduled |
| 094 | (calculation yet to be verified) | (projected, not yet measured) | honesty marker restored |
| 100 | At the moment, Iteration 1 is in the middle of its development plan, with the pipeline being complete and changes being made in how the input data is processed. | At mid-evaluation, Iteration 1 stands at core pipeline complete, refinement ongoing. | mandated status wording (brief decision 8) |
| 100 | while the expected result of below 35 minutes using RTX 4090 video card is not confirmed yet. | while the target of below 35 minutes using an RTX 4090 video card is projected and not yet measured. | honesty markers restored |
| 101 | of which the most prominent are cloud GPU costs that have not been fully established mechanics of the RTX 490 processing time, inability to keep track of chang… | of which the most prominent are cloud GPU costs (cost per scan not yet measured), the unmeasured RTX 4090 processing time, tracking loss on featureless surface… | garbled; typo RTX 490; the risk is tracking loss on featureless surfaces; restored 'not yet measured' |
| 101 | The FYP-2 implies working on 3DGS improvement. Moreover, creating 3D models is regarded as a planned task that has not been contracted yet. | The FYP-2 implies working on 3DGS improvement, the structural layer with automatic floor plans, and the web workspace with 1:1 measurement, validated on more r… | restored the FYP-2 scope (structural layer, web workspace); it is mesh creation, and it is not yet scheduled |

## Citations and references restored

The `\cite`/`\ref` was put back at the place the original had it, pointing at the same key or label.

| Chunk | Your text | Applied as | Why |
|---|---|---|---|
| 003 | application of Gaussian Splatting for 3D scanning , PocketGS, and visual-inertial SLAM | application of Gaussian Splatting for 3D scanning [cite: kerbl3dgs], PocketGS [cite: pocketgs], and visual-inertial SLAM (VIGS-SLAM [cite: vigsslam]) | restored the three citations the rewrite dropped |
| 004 | (the most preferred pod is NVIDIA RTX 4090, but it can be selected at run-time) | (the default pod is NVIDIA RTX 4090, but it can be selected at run-time) | RTX 4090 is the code default, not a preference |
| 008 | 3D Gaussian Splatting technology (see kerbl3dgs article) | 3D Gaussian Splatting technology [cite: kerbl3dgs] | restored the citation |
| 016 | including editing of the report. | including editing of the report. Full disclosure is provided in Chapter [ref: ch:evidence], Table [ref: tab:aitools]. | restored the pointer to the GenAI disclosure (Form 3 C8 gate) |
| 018 | PocketGS [Source: pocketgs] | PocketGS [cite: pocketgs] | restored citation |
| 018 | VIGS-SLAM [Source: vigsslam] | VIGS-SLAM [cite: vigsslam] | restored citation |
| 018 | PGSR [Source: pgsr] | PGSR [cite: pgsr] | restored citation |
| 031 | and the finale of the structure layer; Chapters [ref: ch:plan]; modules and timetable. | and completion of the structural layer; modules and timetable in Chapter [ref: ch:plan]. | component name; garbled reference |
| 050 | (default value is 7200 s) is reached. | (default value is 7200 s) is reached. Figure [ref: fig:sequence] shows the upload → process → download interaction in RunPod mode. | restored the figure reference the rewrite dropped |
| 057 | from its Fig. [ref: fig:sim3] temporal neighbours | from its temporal neighbours | misplaced figure reference |
| 057 | (see Table [ref: tab:tape]). | (see Table [ref: tab:tape]). Figure [ref: fig:sim3] shows the steps. | figure reference restored at the end |
| 062 | check against the dimensions of table in [ref: tab:tape]. | check against the tape-measure values in Table [ref: tab:tape]. | garbled reference |
| 063 | The present solution is to utilize ARCore for image-based spatial localization, while preserving gravity and scale in the process. | The present solution is to use image-based poses, keeping ARCore for scale and gravity (Table [ref: tab:posefix]). | inverted fact: poses come from images, ARCore keeps scale and gravity; restored table reference |
| 063 | and post-video alignment which improved from 49.7 px to 8.2 px. | and post-gap re-alignment which improved from 49.7 px to 8.2 px (Table [ref: tab:imufallback]). | it is post-gap re-alignment; restored table reference |
| 063 | (biggest achievement since version 6). | (the largest single gain on the way to v6; Table [ref: tab:quality]). | inverted: the gain led up to v6; restored table reference |
| 063 | Worst-case error = 0.29% as compared to tape measurement. | Worst-case error = 0.29% as compared to tape measurement (Table [ref: tab:tape]). | restored table reference |
| 085 | The AI applications were utilized for creating the initial program code, debugging, giving explanations, and making reports. | The AI applications were utilized for creating the initial program code, debugging, giving explanations, and making reports, as disclosed in Table [ref: tab:ai… | restored the pointer to the GenAI disclosure table (Form 3 C8 gate) |

## Factual and technical errors corrected

Errors the rewrites introduced that the number and marker rules do not catch.

| Chunk | Your text | Applied as | Why |
|---|---|---|---|
| 001 | which has no LiDAR unit of any particular equipment | which has no LiDAR unit or any special equipment | garbled clause |
| 001 | into a 3D Gaussian Splatting (3DGS) model | into a metric-scale 3D Gaussian Splatting (3DGS) model | restored 'metric-scale': the model's defining property |
| 001 | together with location, depth map | together with camera poses, depth maps | 'location' is wrong: the app records camera poses |
| 002 | out of forty-two held-out frames | on forty-two held-out frames | the score is measured on the frames, not 'out of' them |
| 002 | Some of the unexplored areas remaining include | The open items remaining include | these are open items, not unexplored areas |
| 003 | BuildScan 3D is an exemplary system | BuildScan 3D is a mobile-to-cloud system | removed unsupported self-praise; restored what the system is |
| 003 | (4) application of measurement and analysis techniques; (5) viewing the data with the use of a specialized viewer. | (4) a structural layer (wall planes, corners, wall lengths, door detection) for floor plans and 1:1 measurement, prototype built; (5) viewing the data in a pla… | stage 4 is the structural layer (brief decision 7) and stage 5 is planned, not built |
| 005 | (the height detection is still not reliable) | (the ceiling-height detection is still not reliable) | it is ceiling-height detection specifically |
| 005 | for various room layouts. | for various room layouts; the unmeasured RTX 4090 processing time. | restored the dropped 'unmeasured RTX 4090 time' risk |
| 005 | Finish up the structural layer and web-based measurement environment (Stage 4); | Finish up the structural layer and automatic floor plans (Stage 4) and the web-based measurement environment (Stage 5); | the web workspace is Stage 5, and floor plans were dropped |
| 006 | builds a 3D Gaussian Splatting, and produces a virtual image of the scanned area | builds a 3D Gaussian Splatting model, and produces a viewable, measurable digital twin of the scanned area | missing noun; 'virtual image' lost that the output is measurable |
| 006 | The solution is primarily aimed at taking photographs of construction sites, irrespective of the type of facility being managed or designed. | The solution is primarily aimed at construction site documentation, facility management and architectural surveying. | factual error: the system does not take photographs; restored the three target domains |
| 008 | artsy AR | consumer AR | wrong word: the gap is between consumer AR and surveying |
| 008 | create photorealistic views of one object in real-time | create photorealistic new views of a scene in real time | 3DGS renders novel views of a scene, not of one object |
| 008 | ARCore provides measurements and depth measurement capabilities for cameras on Android devices | ARCore provides metric-scale camera poses and depth measurement capabilities on Android devices | restored what ARCore provides: metric-scale camera poses |
| 010 | captures videos, ARCore positions, depth maps | captures videos, ARCore poses, depth maps | technical term: poses |
| 011 | Three.js web browser as model viewing application (FYP-2) | Three.js web viewer as model viewing and measurement application (FYP-2) | it is a web viewer, not a browser |
| 011 | based on the 3D data from the initiative | based on the reconstructed model | garbled source of the mesh |
| 012 | Mobile Capture Reference: | Mobile Capture Module: | module name |
| 012 | Pose pReference: | Pose Prior Module: | module name |
| 012 | Sim3 measurement alignment | Sim3 metric alignment | technical term |
| 012 | Capture Pipeline: COLMAP | Reconstruction Pipeline Module: COLMAP | this is the reconstruction module, not capture |
| 012 | Processing Server: FastAPI | Processing Server Module: FastAPI | module name |
| 012 | Structural Reference Layer: Recreation of the construction of the room leaving the splat model | Structural Layer Module: Recreation of the construction of the room next to the splat model | module name; the shell is rebuilt next to the splat model, not 'leaving' it |
| 013 | The leadership position is held by Mr. Furqan Nasir who carries out the semi-academic assessment and consulting. | The supervisor, Mr. Furqan Nasir, carries out the academic assessment and guidance. | Mr. Furqan Nasir is the supervisor, not a 'leadership position' |
| 014 | Reconstruction quality: held PSNR | Reconstruction quality: held-out PSNR | technical term: held-out |
| 014 | Structural element: walls | Structural layer: walls | name of the component |
| 018 | it does not work with non-LiDAR devices | it has limited metric accuracy on non-LiDAR devices | factual error: Polycam works without LiDAR, with limited accuracy |
| 018 | Kerbl and some other researcher from the paper published in 2023 | Kerbl et al. in the paper published in 2023 | correct attribution |
| 019 | No guidance for catching: | No guidance for capturing: | wrong word |
| 019 | coverage during catching, | coverage during capture, | wrong word |
| 020 | ARCore for metric frame: With help of visual-inertial odometry of the phone it is possible to obtain the metric frames. | ARCore for metric scale: With help of visual-inertial odometry of the phone it is possible to obtain metric-scale poses. | ARCore provides metric scale through its poses |
| 020 | Groundbreaking image creation: Nerfstudio splatfacto 3DGS builds the most realistic models | State-of-the-art rendering: Nerfstudio splatfacto 3DGS builds photorealistic models | removed unsupported superlatives |
| 021 | How can one set of mobile phone videos that are single-lensed and have questionable motion that has happened too quickly turned into a proper 3D Gaussian Splat… | How can a sequence of single-lens mobile phone video frames, with noisy ARCore poses and sparse depth measurements, be turned automatically into a metrically s… | the problem statement lost its inputs (noisy ARCore poses, sparse depth) and 'metrically scaled', and was ungrammatical |
| 021 | Strong Structure-from-Motion using casual videos, where spoilers of motion made it difficult to track and ARCore re-anchoring has not provided any information. | Strong Structure-from-Motion using casual, motion-blurred videos with tracking gaps and silent ARCore re-anchoring events. | garbled; the challenge is motion blur, tracking gaps and silent re-anchoring |
| 021 | The coordination of scales in COLMAP's units of measurement and ARCore's metrics using a certain transform Sim3 with outlier rejection to not leave out any inf… | The coordination of scales between COLMAP's arbitrary-scale coordinate system and ARCore's metric frame using a Sim3 transform with outlier rejection. | COLMAP's frame has arbitrary scale; outlier rejection discards data rather than keeping all of it |
| 021 | problems with construction of geometries that are not going anywhere (zero-thickness splats, opacity collapse) | problems with degenerate geometry (zero-thickness splats, opacity collapse) | garbled term |
| 021 | The correct setting of GPU resources for managing each loop with sleep modules to prevent the outflow of expenses for cloud resources. | The correct setting of GPU resources, managing each step with timeout watchdogs to prevent the outflow of expenses for cloud resources. | the mechanism is per-step timeout watchdogs, not sleep modules |
| 022 | resulting in significant pose shifts of more than 1 m and 28° | resulting in significant pose shifts of up to 1 m and 28° | the measured shift is about 1 m / 28°, not more |
| 022 | all poses taken in the first minute were within 1 m and 28° | all poses taken in the first minute were off by about 1 m and 28° | inverted fact: the poses were off by 1 m / 28° |
| 022 | The tracking software is now capable of logging ARCore placements for a more detailed observation of the re-anchoring process itself. | The app now logs ARCore anchors, so re-anchoring events are directly detectable. | it is the app that logs anchors |
| 022 | We achieved zero-thickness, semi-transparent splats | Our initial training recipe produced zero-thickness, semi-transparent splats | 'achieved' presented a defect as a goal |
| 024 | after performing co-calibration via the bundle method, the error was reduced to 0.62 px (after using 626k of observed values) | after bundle adjustment, the error was reduced to 0.62 px (626k observations) | technical term: bundle adjustment |
| 024 | In addition, the work with colloquial data caused the training view destroying errors identified despite that the error was prior to switching into landmark-ba… | Switching to image-based COLMAP poses with lens self-calibration raised the training-view fit from 21.9 dB (12–30 px misaligned) to 28 dB (2–3 px), raised held… | garbled passage ('C-POLMAP', '21.9 dB and 28 dB to 28 dB'); restored the SSIM 0.78 -> 0.86 result, the second-room figu… |
| 024 | Decided: continue using COLMAP and Sim3 alignment of ARCore for retrieving the most realistic metric scale in the images. | Decided: use COLMAP SfM for training poses, with ARCore providing metric scale through Sim3 alignment. | garbled decision |
| 024 | volume downsampling to 1 cm | voxel downsampling to 1 cm | technical term: voxel |
| 025 | The splatfacto baseline achieved an amazing score of 27.81 dB in a different scene (roomAttemptSadness2), compared to 24.70 dB achieved by our model with a rec… | The splatfacto baseline achieved 27.81 dB held-out in a different scene (roomAttemptSadness2), compared to 24.70 dB achieved by our own trainer with the correc… | removed hype; 27.81 is held-out on a different scene (brief decision 5); the comparison is with our own trainer |
| 025 | Decision: Write select_sharp.py using the recorded metadata. | Decision: Implemented select_sharp.py using the recorded per-frame exposure metadata. | select_sharp.py is already implemented |
| 026 | (ARCore's lack of re-anchoring/lens model; finding 1) | (ARCore's silent re-anchor and missing lens model; finding 1) | inverted fact: ARCore re-anchors silently; it does not lack re-anchoring |
| 026 | equal to only 22.67 / 0.782 dB | equal to only 22.67 dB / 0.782 | unit belongs to the PSNR, not the SSIM |
| 029 | We undertake a strategy that comprises not only two phases, represented by FYP-1 and FYP-2: | We undertake a strategy that comprises two iterations, represented by FYP-1 and FYP-2: | there are exactly two iterations |
| 029 | Phase 1 (FYP-1, Weeks 1–8): | Iteration 1 (FYP-1, Weeks 1–8): | the report calls these iterations throughout |
| 029 | Phase 2 (FYP-2, Weeks 9–16): | Iteration 2 (FYP-2, Weeks 9–16): | the report calls these iterations throughout |
| 029 | creation of the web-viewing page based on Three.js, which can also measure. | creation of the web-viewing page based on Three.js, which can also measure; the structural layer with floor plans; and field validation on multiple rooms. | restored the structural-layer and field-validation deliverables |
| 031 | Aim: Speed up processing time, enhance pipeline stability, finalize the structure layer | Aim: Speed up processing time, enhance pipeline stability, finalize the structural layer | component name |
| 031 | structure layer capable of floor plan export | structural layer capable of floor plan export | component name |
| 031 | Proof: Measuring time benchmarks | Proof: Processing time benchmarks | the benchmarks measure processing time |
| 032 | (selection of gyro-aware frames, initial MVS) | (selection of gyro-aware frames, MVS initialization) | technical term |
| 033 | than Splat Facto. Consequently, we switched to the Splat Facto technique | than splatfacto. Consequently, we switched to splatfacto | tool name is splatfacto |
| 033 | but the analysis allowed us to make the right decision about the design. Recovery: | but the analysis allowed us to make the right decision about the design.  Recovery: | split back into the two list items of the source |
| 034 | and switches the application off after this and taps | and stops recording after this and taps | the user stops recording; the app is not switched off |
| 034 | time wasted | time elapsed | wrong word: elapsed time |
| 035 | The various examples of use are | The use cases are | technical term: use cases |
| 036 | Postcondition: The information (splat.ply) is ready for downloading. | Postcondition: The 3D model (splat.ply) is ready for downloading. | the output is the 3D model |
| 039 | Project's acceptance limits are set as: PSNR >= 25 dB | Project's acceptance limits are set as: held-out PSNR >= 25 dB | the threshold is on held-out frames |
| 040 | which is capable of capturing images using Augmented Reality, uploading them to the server, and displaying the current progress of uploading the images. | which is capable of capturing video with ARCore, uploading it to the server, and displaying the current progress of processing. | the app captures video with ARCore and displays processing progress |
| 040 | handling job arrangements, orchestration of the upload process, and handling RunPod workloads | handling job arrangements, orchestration of the pipeline, and handling RunPod workloads | the server orchestrates the pipeline, not the upload |
| 041 | The HelloArActivity class is in charge of the AR camera, including screen and adjustment settings, as well as quality. | The HelloArActivity class is in charge of the AR camera, including the recording controls, the settings menu and the quality overlay. | restored what the activity contains |
| 041 | The CaptureLogger class is the background I/O executor which creates the I/O logs. | The CaptureLogger class is the background I/O executor which writes the poses, tracking, points, quality, depth and metadata files. | it writes the capture files, not I/O logs |
| 041 | maps directions with 8 times in the azimuth and 2 times in the elevation | maps directions with 8 azimuth × 2 elevation bins | garbled description of the direction bins |
| 041 | The ProcessingActivity class uploads with the help of OkHttp. | The ProcessingActivity class uploads and shows progress with the help of OkHttp. | restored the progress UI |
| 044 | Using COLMAP for SfM with ARCore poses: ARCore motion has a 2.32 px | Using COLMAP SfM over ARCore poses for training: Raw ARCore poses have a 2.32 px | inverted label: COLMAP replaces ARCore poses |
| 044 | There is no mention of lens distortion.   Compared to COLMAP's self-calibrated SfM with lens distortion (k1 ≈ 0.09 and k2 ≈ -0.22), ARCore's system has problem… | ARCore also reports no lens distortion. COLMAP's self-calibrated SfM with lens distortion (k1 ≈ 0.09 and k2 ≈ -0.22) removes both issues. On the same recording… | garbled: COLMAP removes both problems; merged back into the one list item of the source |
| 046 | The proposal now includes the guidelines for live IQA and coverage (absent from the original proposal). | Live IQA and coverage guidance were added (absent from the original proposal). | the features were added to the system, not to the proposal |
| 047 | (video, representative parameters, depth, quality and meta information) | (video, poses, depth, quality and meta information) | the dataset contains poses |
| 049 | The tracking gaps from tracking.csv will be identified and converted via the IMU integration at both ends. | The tracking gaps from tracking.csv will be identified and bridged with IMU integration anchored at both ends. | gaps are bridged, not converted |
| 049 | mapping, adjusting the lens, undistorting images | mapping, lens self-calibration, undistorting images | technical term |
| 049 | Train the Nerfstudio model by forming a splatfacto during 30,000 iterations with the use of bilateral grid compensation for the exposure and scaling along with… | Train the Nerfstudio splatfacto model for 30,000 iterations with bilateral-grid exposure compensation, scale regularization and fixed poses. | garbled training description |
| 050 | Additionally, this process is killed by the watchdog thread | Additionally, the pod is terminated by the watchdog thread | the watchdog terminates the pod |
| 054 | The use of gyroscope-based frame selection and performance analytics suggested a mechanism to deliver best quality output to user. | Gyroscope-based frame selection, live IQA and the coverage overlay were added. | garbled; restored what was added in weeks 5-6 |
| 054 | Weeks 7-8: FastAPI server, RunPod integration with cloud GPU and Android interface were all set up and implemented to complete the project as planned. | Weeks 7-8: FastAPI server, RunPod integration with cloud GPU, the Android upload interface (ProcessingActivity) and the CI/CD pipeline were all set up and impl… | the project is not complete (brief decision 8); restored the CI/CD milestone |
| 055 | Live IQA (Intra-Quality Assessment) | Live IQA (image quality assessment) | wrong expansion of IQA |
| 055 | tracking has issues moving quickly by having an orange hue | moving too fast is shown in orange | garbled |
| 055 | Finally, the process ends by closing the recording and having the processing activity started at the server URL described in preferences. | Recording ends with a quality summary dialog and an Upload & Process button that opens ProcessingActivity; the server URL is set in the settings menu and persi… | garbled description of how recording ends and where the URL is set |
| 056 | prepared by prepare.py it still selects frames in windows with sharpest perceptions from per-window exposures.  | the one-command pipeline still uses prepare.py's sharpest frame per window.   | garbled; split back into the two source paragraphs |
| 056 | as well as pull request creating. | as well as a pull request template. | it is a pull request template |
| 058 | an acceleration metering device for positioning | accelerometer integration for positioning | technical term |
| 058 | by solving the keyframe matching problem. | by matching its keyframes against the map (PnP). | restored the method |
| 061 | which is better than the Laplacian measure of sharpness since its performance correlates with the true motion blur according to the correlation r = 0.20. | which is better than the Laplacian measure of sharpness, whose correlation with the true motion blur is only r = 0.20. | inverted fact: r = 0.20 is the Laplacian measure's weak correlation |
| 061 | Coverage probability estimation: | Coverage map: | it is a coverage map, not a probability estimate |
| 061 | green is used in the case of more than four observations | green is used in the case of four or more directions | the green threshold is 4+ directions |
| 062 | Capture a scan of the room with IQA feedback in real time on the coverage. | Capture a scan of the room with live IQA feedback and the coverage overlay. | garbled |
| 064 | (mapping takes 6 minutes, while training takes 45 minutes) | (matching takes 23 minutes, mapping 6 minutes and training 45 minutes) | restored the matching time so the parts add up to 75 |
| 066 | (the first one being the first room, and the second one being newRoomAttemptSadness for the second room) | (the first room, newRoomAttemptSadness, and the second room, roomAttemptSadness2) | swapped recordings: newRoomAttemptSadness is the first room |
| 067 | Previously, on October 12, 2026, the CI of GitHub Actions completed | Previously, on October 12, 2026, GitHub Actions CI run #6 (commit c3bfcc9 on branch ci/pipeline-updates) completed | restored which CI run and commit the evidence comes from |
| 068 | introduced after CI #6 of the RunPod Work on GPU Selection | introduced after CI run #6 by the RunPod GPU-selection work | garbled attribution |
| 068 | This alone proves that any automated suite is worth having with the blocking lint gate. | This is itself evidence for the value of the automated suite and the blocking lint gate. | overclaim ('proves that any suite') |
| 068 | Table [ref: tab:testfiles] shows what all the files of pytest test and Table [ref: tab:testcases] describes number of the tests, expected results and status. | Table [ref: tab:testfiles] shows what each pytest file tests, and Table [ref: tab:testcases] describes every test case with its expected result, evidence and s… | garbled |
| 071 | than Table [ref: tab:quality] and therefore the score of v6. | than Table [ref: tab:quality] and is therefore not the score of v6. | inverted fact: 27.81 dB is not v6's score (brief decision 5) |
| 072 | The end-to-end distance measurements between four rigid objects in the software correspond to the tape measure, yielding a mean of 4.8 mm (0.19%) and a maximum… | Four rigid-object distances measured in the model correspond to the tape measure, yielding a mean error of 4.8 mm (0.19%) and a worst case of 0.29% (Table [ref… | the worst case is 0.29%, not 'less than'; garbled target |
| 072 | The results from the second room were not included this time, since the held-out frames yielded a score of 0.91 with PSNR not yet measured. Additionally, the i… | The second room reaches a held-out SSIM of 0.91; its PSNR is not yet measured. Additionally, views rendered from the centre of the room, where no camera stood,… | garbled: the second room is included; the views are rendered, not captured |
| 074 | Unlike other technologies, the ARCore derived scale does not grow with distance (-8 mm at both 2.8 m and 6.7m). | The error does not grow with distance (-8 mm at both 2.8 m and 6.7 m), so the ARCore-derived scale is sound. | it is the error that does not grow; 'unlike other technologies' is unsupported |
| 075 | The IMU fallback changes this. | The IMU fallback (fallback.py) bridges the gap. | garbled |
| 075 | The image-based pipeline also captures most frames in the gap | The image-based pipeline also registers most frames in the gap | COLMAP registers frames |
| 075 | suggests the user takes some other nearby textured objects. | suggests the user captures nearby textured objects. | garbled |
| 076 | (pod crash/software that uses GPU fails) | (pod crash, GPU unavailable) | garbled |
| 076 | which means the pod will eventually be terminated in inevitably (finally block). | after which the pod is terminated in the finally block and the job is marked failed. | garbled |
| 077 | version 6 generates average reconstruction quality of 26.52 dB / 0.8886 for the first room (the requirements are >25 dB, >0.85) | version 6 scores 26.52 dB / 0.8886 for the first room (the requirements are >= 25 dB, >= 0.85) | it is a score, not an average; thresholds are >= |
| 077 | Not executed yet: Android unit tests | Not yet automated or executed: Android unit tests | Android tests are not automated (brief decision 12) |
| 078 | model export (although no gyro-aware frame selection has been implemented yet), the processing server | model export, with gyro-aware frame selection validated but not yet in the one-command pipeline), the processing server | inverted fact: gyro-aware selection is implemented, just not in the pipeline; fixed unbalanced parenthesis |
| 078 | (containing several reasons in respective document) | (six causes, documented in Training_Analysis.md) | restored the count and the document |
| 079 | Found in Chapter [ref: ch:plan]: | Scheduled in Chapter [ref: ch:plan]: | these items are scheduled there |
| 079 | completion of the structure layer | completion of the structural layer | component name |
| 081 | SSH-ready for rituals | SSH readiness | garbled |
| 081 | and an initiative to develop a dense MVS and evaluate its structural layer and evaluation tools. | dense MVS initialisation, the structural layer, and the evaluation tools. | garbled list of owned modules |
| 081 | Captured app logging and in-line IQA, | Wrote the app's capture logging and live IQA, | he wrote the code; the feature is live IQA |
| 082 | Therefore, the contributions of each of the listed modules are more reliable evidence | Therefore, the owned modules listed above are more reliable evidence | points to the owned-modules table |
| 083 | CI – GitHub Actions is being implemented on work branches | CI – GitHub Actions runs on work branches | CI runs there; it is not being implemented |
| 083 | with the modules mentioned in this paper. | with the modules mentioned in this report. | it is a report |
| 088 | The RunPod API credential stays in memory via some environmentally loaded values or an environmental file and is never mentioned in the source code directly. N… | The RunPod API credential is loaded at runtime from environment variables or a .env file and is never mentioned in the source code directly. Nonetheless, the .… | garbled loading description; updated to the current state: .env was untracked and ignored in 562229d, and the key still… |
| 088 | also, it looks for any sensitive documents (except for RunPod keys ones) through the scanned material. The last time CI worked (job # 6) was prior to .env load… | also, it scans tracked files for private keys, AWS keys and GitHub tokens (it has no pattern for RunPod keys). The last time CI ran (run #6) was before .env wa… | garbled; updated now that .env is untracked |
| 090 | (2) creating the structural feature (wall planes, corners, walls, door identification and layout) | (2) completing the structural layer (wall planes, corners, wall lengths, door identification and floor plans) | the structural layer exists as a prototype and is being completed; restored wall lengths and floor plans |
| 091 | rolling shutter calibration using the per-frame exposure time | rolling shutter modelling using the per-frame exposure time | it is modelling, not calibration |
| 091 | In addition, there will be ARCore-aligned images with anchor detection based on the logged anchor information. | In addition, there will be ARCore-started image-only alignment with re-anchor detection based on the logged anchor information, which could give COLMAP-quality… | garbled description of the planned alignment method |
| 091 | textureless walls, large hallways, and different types of lighting conditions. | textureless walls, large rooms (>8 m), and different types of lighting conditions. | the limitation is large rooms, not hallways |
| 092 | and the system calculates the distance in m in a Sim3-aligned coordinate frame. | and the system calculates the distance in m in a Sim3-aligned coordinate frame. Target accuracy: within 5% of tape measure (current evidence: mean 0.19%, worst… | restored the measurable target (the rewrite dropped it) |
| 092 | The user clicks two points representing the shape on either splat or structural layer wall | The user clicks two points on either the splat surface or a structural-layer wall | garbled |
| 094 | allows for point-to-point measurements in a minimum of 3 rooms. | allows for point-to-point measurements, validated in a minimum of 3 rooms. | the 3 rooms are the validation set |
| 095 | ray-cast click – > nearby splat > 3D coordinates – > distance display | ray-cast click → nearest splat → 3D coordinates → distance display | broken arrows |
| 095 | Structural layer: measure dimensions, automate room layout exporting from the floor outline (week 7). | Structural layer: wall-to-wall dimensions, automate floor-plan exporting from the floor outline (week 7). | the output is a floor plan; restored wall-to-wall dimensions |
| 095 | Use structure.json in the browser; make measurements snap to walls; add floor view (week 8). | Use structure.json in the web viewer; make measurements snap to walls; add a floor-plan view (week 8). | it is the web viewer and a floor-plan view |
| 099 | Android APK: The product to measure the application’s performance through live IQA, coverage overlay, and uploading functionalities. | Android APK: The capture app with live IQA, coverage overlay, and uploading functionalities. | the APK is the capture app, not a performance-measuring product |
| 099 | Gaussian splatter viewer | Gaussian splat viewer | technical term |
| 100 | into a metric-precision 3D Gaussian Splatting model | into a metric-scale 3D Gaussian Splatting model | technical term |
| 100 | (1) in the place of ARCore poses for training, image-based COLMAP poses used for the training purposes; wasting ARCore's silent re-anchor and lens model has in… | (1) image-based COLMAP poses replace ARCore poses for training: once ARCore's silent re-anchor and missing lens model were removed, the training-view fit incre… | garbled: the re-anchor and missing lens model were removed, not 'wasted' |
| 100 | has reached 26.52 dB which means the original signal to noise ratio (PSNR) of > 25 dB and 0.8886 which means the original signal to noise ratio (SSIM) of > 0.8… | has reached 26.52 dB PSNR (target >= 25 dB) and 0.8886 SSIM (target >= 0.85) over 42 held-out frames | SSIM is not a signal-to-noise ratio; the thresholds are targets |
| 101 | Mirrors and glass are still considered as the limiting barrier. | Mirrors and glass remain a known limitation. | they are a known limitation, not the limiting barrier |

## Typos and broken grammar

Only where the sentence was broken or a name misspelt.

| Chunk | Your text | Applied as | Why |
|---|---|---|---|
| 001 | step-up procedures that are impractical for construct site personnel | step-up procedures that are impractical for construction site personnel | typo: 'construct site' |
| 004 | live-QA image quality processing | live IQA image quality processing | typo: the feature is IQA |
| 007 | requires either LiDAR devices costing over $10,000, (ii) | requires either (i) LiDAR devices costing over $10,000, (ii) | list numbering started at (ii) |
| 007 | Luma.AI | Luma AI | product name |
| 009 | length of the walls, and the door— | length of the walls, and the doors— | plural: several doors |
| 011 | COLMAP SFN, Sim3 for scaling and dataset creation | COLMAP SfM, Sim3 for metric scaling, and splatfacto 3DGS training | typo SFN; the last step is 3DGS training, not dataset creation |
| 032 | Weeks 7–8: been developed processing server, integrated with RunPod, upload interface has built, CI/CD has been finalized. | Weeks 7–8: the processing server has been developed and integrated with RunPod, the upload interface has been built, and CI/CD has been finalized. | broken grammar |
| 054 | (6 sources of failure are outlined in “Training Analysis” file) | (6 sources of failure are outlined in Training_Analysis.md) | file name |
| 060 | set in motion,, | set in motion, | typo |
| 064 | threshold of 25_dB | threshold of 25 dB | typo |
| 070 | bringing the amount of fused points from 1.15 million to 460, 000 points at the distance of 1 cm. | bringing the amount of fused points from 1.15 million to about 460,000 points at 1 cm voxel resolution. | typo; the figure is approximate (~460k); 1 cm is the voxel size |
| 076 | while the termination path is yet to be applied to a real pod. | while the termination path is yet to be exercised on a live pod. | wording |
| 083 | CD – on master branch’s push build artifacts; on tagged version do GitHub releases with the APK and web app bundle | CD – on a push to master, build artifacts; on a version tag, a GitHub release with the APK and web app bundle | broken grammar |

## Content the rewrites dropped (applied as written)

These omissions were kept, because they remove detail rather than state something false:

- 011: the "Out of scope" paragraph was missing from the rewrite. It is a required scope item, so the original paragraph was **kept** in place.
- 015: the 10 x 10 m room-size constraint and "not a full building".
- 040: the sentence on the four processing modes (`dry_run` default, local, runpod, remote).
- 055: the coverage-overlay, vibration, exposure/anchor logging and fast-path details of the Android app paragraph.
- 058: "This is the team's main novelty claim" and the lead-in to the IMU table.
- 064: the motion-blur item of the 3DGS-refinement open item.
- 092: the snap-to-wall clicks and the reason the splat model is not flattened.

## Outside the chunks

- `0f66703`: NFR-S2 in the requirements table and the `.env` row of the repository table still said `.env` was tracked. Your `562229d` untracked and ignored it, so both now say so, noting that the key committed on 18 October is still in the history and must be rotated. Chunk 088 was corrected the same way.
