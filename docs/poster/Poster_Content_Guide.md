# BuildScan 3D: Poster Content Guide

Material for the FYP poster, following *FYP Poster Submission Guidelines*. This is the content and the
layout plan, not the poster itself. Facts are as of 2026-11-11; check the numbers against
[docs/progress/STATUS.md](../progress/STATUS.md) before printing.

---

## 1. Hard requirements (from the guidelines)

| Requirement | Value |
|---|---|
| Size | **22.5 in × 34.5 in** (57.2 × 87.6 cm) |
| Orientation | **Portrait** |
| Readable from | 1 metre |
| Must include | Project name and logo · one-line objective · architecture or problem diagram · iterative project plan and deliverables · team and supervisor · tools and technologies · "FAST NUCES, Islamabad Campus" + logo · industry partner logo (if any) |
| Style | Little text, bullets, large fonts, visuals over words, spell-checked |

Suggested type sizes at this size (readable at 1 m):

| Element | Size |
|---|---|
| Project title | 110–140 pt |
| Section headings | 54–66 pt |
| Body bullets | 30–36 pt (never below 24 pt) |
| Figure captions, footer | 24–28 pt |

Set the canvas to 22.5 × 34.5 in at 300 dpi (6750 × 10350 px) in Canva / Figma / PowerPoint. Leave a margin of
at least 0.75 in.

---

## 2. Suggested layout

```
┌──────────────────────────────────────────────┐
│ [BuildScan logo]  BuildScan 3D   [FAST logo] │  header band
│  Phone video → measurable 3D model of a room │
├──────────────────────────────────────────────┤
│ OBJECTIVE (one line, large, highlighted box) │
├───────────────────────┬──────────────────────┤
│ THE PROBLEM           │ HERO IMAGE           │
│ 3–4 bullets + icons   │ labelled 3D room     │
├───────────────────────┴──────────────────────┤
│ SYSTEM ARCHITECTURE (5-stage flow, full width│
│ phone → upload → reconstruction → layout &   │
│ labels → web viewer)                         │
├───────────────────────┬──────────────────────┤
│ RESULTS               │ WHAT IT PRODUCES     │
│ 4 big-number tiles    │ plan + mesh + viewer │
├───────────────────────┴──────────────────────┤
│ PROJECT PLAN: iteration timeline (full width)│
├───────────────────────┬──────────────────────┤
│ TOOLS & TECHNOLOGIES  │ TEAM & SUPERVISOR    │
│ logo grid             │                      │
├───────────────────────┴──────────────────────┤
│ FAST NUCES, Islamabad Campus · Dept. of CS   │  footer band
└──────────────────────────────────────────────┘
```

Reading order runs top to bottom: what, why, how, how well, when, who.

---

## 3. Content per section

### 3.1 Header: name and logo
- **Name:** BuildScan 3D
- **Tagline (pick one):**
  - "From a phone video to a measurable 3D model of a room"
  - "Metric 3D room scanning with a commodity Android phone"
- **Logo:** use `prototype/web-ui/public/images/logo-new.png` (2496 × 1726 px, sharp up to ~8 in wide at 300 dpi).
  The transparent `logo-new-removebg-preview.png` is only 601 px wide, which prints blurry above ~3 in. If you need
  transparency at a larger size, remove the background from the large file instead. Don't redraw the logo.
- **University logo:** `F26_FYP1_Mid_Report_LaTeX_Complete/ThesisFigs/FASTLogo.jpg` is only 433 px, enough for ~1.5–2 in.
  Get a higher-resolution official FAST NUCES logo (or a vector file) from the department or the university website.
- **Industry partner:** none recorded in the repo. If you have one, add its logo; otherwise leave it out.

### 3.2 Objective (one line)
Recommended:
> **Turn a slow walk-through video from an ordinary Android phone into a metric, labelled 3D model of a room,
> with no LiDAR or special hardware.**

Shorter alternative:
> **Measurable, labelled 3D room models from a commodity phone video.**

### 3.3 The problem
- 3D scanning of rooms today needs **LiDAR scanners or LiDAR phones**: expensive and not what site staff carry.
- Photos and tape measures are slow, error-prone and leave **no 3D record** of the site.
- Phone-only 3D (photogrammetry, 3DGS) gives pretty models with **no real-world scale** and messy walls.
- **Target users:** construction-site supervisors, facility managers and small design firms, using the phone they already have.

Icon ideas: LiDAR scanner with a price tag, tape measure, phone with a question mark.

### 3.4 System architecture (the main diagram)
Draw as a left-to-right (or zig-zag) flow with an icon per box and 1–2 words under each:

1. **Capture (Android app):** ARCore video at 30 FPS + camera poses + IMU; live quality warnings (blur, darkness, speed) and a coverage overlay.
2. **Upload and processing server:** FastAPI server, local or cloud GPU (RunPod).
3. **Reconstruction:**
   - sharp-frame selection using the gyroscope;
   - COLMAP structure-from-motion, scaled to metres by aligning to ARCore;
   - Metric3D depth/normal priors;
   - 3D Gaussian Splatting training with flat-wall and motion-blur modelling.
4. **Understanding:**
   - room layout (walls, corners, dimensions);
   - semantic labels (walls, floor, ceiling, doors, windows, switches, sockets, lights);
   - surface mesh.
5. **Web workspace:** browser 3D viewer with layers, fixture list, measurements and mesh view.

Optional thin band under it: "Phone → ~1.5 h on one RTX 3070 → labelled metric model in the browser".

### 3.5 Results (big-number tiles)
Use 4 tiles, each a large number and a one-line caption. All are from the newRoomAttemptSadness capture:

| Tile | Number | Caption |
|---|---|---|
| Speed | **~4 h → 96 min** | End-to-end processing on one RTX 3070 |
| Scale | **6.60 m vs 6.70 m** | Room length vs tape measure (−1.5%) |
| Flat walls | **< 1 cm** | Median wall deviation of the mesh |
| Labels | **15 / 15** | Detected fixtures correct; 15 of 17 visible fixtures found |

Other numbers you can use instead:
- 605,481 Gaussians;
- floor 28.8 m², ceiling height 2.73 m;
- held-out image quality PSNR 25.2 dB / SSIM 0.83 on 79 frames the model never saw.

**Honesty notes (the panel may ask):**
- **One room.** All results come from one room, and the label rules were tuned on that room. Say "on our test room".
- **Two scale figures.** The mid report's 0.19% tape error was the older v6 model on 4 measurements. The current model's room length is −1.5% off. Don't put both on the poster without saying which model each is.
- **Two quality figures.** v6's 26.5 dB was on a different, easier test set from the 25.2 dB above, so the two numbers are not comparable.

### 3.6 What it produces (visual panel)
Pick 3–4 images. Visuals do most of the work on a poster.

| Visual | Where it is |
|---|---|
| **Hero:** 3D room in the web viewer with class tint and fixture markers | Screenshot of `/viewer/newroom-scan` with Layers on (`npm run dev` in `prototype/web-ui`) |
| Floor plan with labelled fixtures | `saved_models/2026-10-27_v9_semantic_pgsr/newRoomAttemptSadness/semantic_v10/plan_semantic.png` |
| Room layout with dimensions and corners | `.../layout/plan.png`, `.../layout/corners.jpg` |
| Labelled views (class colours) | `.../semantic_v10/views_semantic.jpg` |
| Mesh | `.../mesh/mesh_views.jpg`, or a viewer screenshot in Mesh mode |
| Real photo vs model render | `dataset/newRoomAttemptSadness/work_v9e2e_sfm/gs_v9e2e/eval/offpath_frames.jpg` |
| App during capture (quality banner, coverage dots) | `F26_FYP1_Mid_Report_LaTeX_Complete/ThesisFigs/app-capture.png` |
| Web UI design | `UI designs/Web Designs-Light Themed.png` |

Take the viewer screenshots at the largest window size you can (4K if possible), because they'll be printed about 10 in wide.

### 3.7 Project plan: iterative timeline
The guidelines want iterations that each produce a working outcome (not waterfall). Draw a horizontal timeline
with one box per iteration: name, outcome, and status (✔ done / ◐ in progress / ○ planned).

| Iteration | Outcome delivered | Status |
|---|---|---|
| **1: Capture to 3D** (FYP-1) | Android ARCore app with live quality checks and coverage overlay; FastAPI server + RunPod cloud GPU; first metric 3DGS models | ✔ |
| **2a: Better 3D, faster** | Gyro-based sharp frames, COLMAP self-calibration, depth/normal priors, flat-wall and motion-blur modelling; ~4 h → 96 min | ✔ |
| **2b: Understanding the room** | Room layout and dimensions, semantic labels (walls, floor, ceiling, doors, windows, switches, sockets, lights), mesh | ✔ (one room) |
| **2c: Web workspace** | Browser viewer with scan layers, fixtures, mesh mode and measurements; dashboard | ◐ |
| **2d: Validation and polish** | Tests on more rooms against tape measurements, faster processing, usability testing with users, final report | ○ |

Check this with your team and supervisor. The mid report's FYP-2 plan (Ch. 10: 2a pipeline + viewer, 2b robustness + structural layer,
2c dashboard + field testing) was written before the semantics work. Use whichever version the panel has seen, or show the updated one and say it changed.

### 3.8 Team
Order members by roll number. Write "Mr." for the supervisor, not "Sir".

| Roll no. | Name |
|---|---|
| 23I-0636 | Muhammad Tayyab |
| 23I-0662 | Muhammad Umair |
| 23I-0829 | Zaid Fareed |

**Supervisor:** Mr. Furqan Nasir
**Co-supervisor:** none recorded. Add one if you have one.

(Source: the mid report title page. Confirm the spellings and roll numbers.)

### 3.9 Tools and technologies
Show as a logo grid grouped into 4 rows rather than a text list:

| Group | Items |
|---|---|
| Mobile | Android (Java), Google ARCore |
| 3D reconstruction | COLMAP, Nerfstudio (splatfacto), gsplat, PyTorch + CUDA, Open3D |
| AI models | Metric3D v2 (depth), Grounding DINO + SAM (detection, masks), CLIP (verification) |
| Backend and cloud | Python, FastAPI, RunPod GPU, GitHub Actions |
| Web | Next.js, React, TypeScript, Three.js, Spark (Gaussian-splat renderer) |

### 3.10 Footer
- "FAST National University of Computer and Emerging Sciences, Islamabad Campus · Department of Computer Science"
- FAST logo; industry partner logo if any.
- Optional: a QR code to the demo or a video of the viewer (only if it is publicly reachable).

---

## 4. Design rationale (to meet the guideline's four principles)

| Principle | How to meet it |
|---|---|
| **Visibility** | White cards with thin slate borders on a light background; generous spacing between sections; the objective in a highlighted box near the top |
| **Consistency** | Use the project palette throughout: background `#f8fafc`, cards `#ffffff`, borders `#e2e8f0`, accent blue `#2563eb`, headings `#0f172a`, secondary text `#64748b`. One sans-serif font family (e.g. Inter), with headings all the same size and left-aligned |
| **Attention** | Blue only for what matters: the objective, the result numbers, the "done" ticks. Number the architecture stages 1–5 so the eye follows them. Make the hero image the largest element |
| **Perception** | One simple icon per architecture stage. Fixture colours match the viewer (door blue `#285aff`, window cyan `#00c8ff`, switch magenta `#ff00c8`, socket orange `#ff7800`, lights yellow `#f5c400`). Dark text on light backgrounds only; no text over busy 3D images |

---

## 5. Checklist before submitting

- [ ] Portrait, 22.5 × 34.5 in, images at ≥ 150 dpi at print size (300 ideal)
- [ ] All required parts present: name and logo, objective, architecture, iterative plan, team (by roll number) and supervisor (Mr.), tools, university name and logo
- [ ] Body text ≥ 30 pt; read a printed A4 copy from 1 m (A4 is about ⅓ scale, so check that headings are readable)
- [ ] Every number matches STATUS.md, and says which model and room it comes from
- [ ] Spell check, including the capitalised words (BuildScan, ARCore, COLMAP, Nerfstudio, Gaussian, FAST NUCES)
- [ ] Under ~250 words of body text in total
- [ ] Team names and roll numbers confirmed by all three members
