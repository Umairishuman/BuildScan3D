# BuildScan 3D — Agent Instructions & Design Guidelines

## 1. Brand Assets & Logo Rules
- **Official Logo**: Always use `/images/logo-new-removebg-preview.png` (transparent background) or `/images/logo-new.png` for all branding, login screens, headers, navbars, and exported reports.
- **Do NOT** replace the official logo with generic icons, raw SVG cubes, or placeholder text. Always render the brand asset from `/images/logo-new-removebg-preview.png`.
- **Hero Image (Login)**: Always use `/images/login-left-panel-new.png` for the left full-bleed architectural 3D blueprint panel on the login screen.

## 2. UI Theme & Design System
- **Theme**: Light Enterprise SaaS theme (`#f8fafc` background, crisp white cards `#ffffff`, subtle slate borders `#e2e8f0`, primary blue accents `#2563eb`).
- **Typography**: Clean modern sans-serif with high-contrast text (`#0f172a` headings, `#64748b` secondary text).

## 3. FYP Defense Architecture
- **Stage 1 (Mobile)**: CameraX / ARCore (Android) & ARKit (iOS) capturing 30 FPS video + 120Hz IMU telemetry (`poses.csv` and `points.csv`).
- **Stage 2 (Pose Prior)**: `build_transforms.py` quaternion to $3 \times 3$ SO(3) matrix conversion + OpenGL to OpenCV/Nerfstudio coordinate alignment (`transforms.json` and `points3D.ply`).
- **Stage 3 (3DGS)**: Nerfstudio `splatfacto` 3D Gaussian Splatting trained in < 5 minutes on Cloud GPU (NVIDIA RTX 4090).
- **Stage 4 (Semantic AI)**: YOLOv8-Seg 2D segmentation masks projected to 3D point cloud for MEP systems (Pipes, Conduits, HVAC).
- **Stage 5 (Web Workspace)**: Three.js / WebGPU rendering with 1:1 metric measurements and semantic system toggles.

## 4. Git & Commit Conventions
- **No AI attribution in commits.** Do NOT add `Co-Authored-By: Claude ...`, `Generated with Claude Code`, or any similar AI attribution trailer to commit messages or pull request descriptions. Commits are authored by the student team only.
- This applies to every commit and PR in this repository, with no exceptions.
