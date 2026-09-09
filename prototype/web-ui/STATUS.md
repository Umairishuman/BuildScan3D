# BuildScan 3D — Build Status & Handoff

**Single source of truth for what is built, what is next, and what has already been decided.**
Last updated: 2026-09-09 (Viewer restructure + real X-Ray) · Branch: `prototype`

---

## 0. How to use this file

**At the start of a session:** read this file before touching code. Sections 2 (Locked
Decisions) and 5 (Next Steps) are the important ones — Section 2 exists specifically to stop
you re-litigating choices the user has already made.

**At the end of every step:** update this file before you consider the step finished.
Specifically:

1. Move the completed step from §5 (Next Steps) to §4 (Completed).
2. Record the actual files created/modified, and the verification output you got.
3. Add anything new to §6 (Known Issues) or §2 (Locked Decisions) if the user made a call.
4. Bump "Last updated" at the top and add a line to §8 (Changelog).

**Working agreement with the user (standing):**

- Build **strictly one component at a time**. Do not batch screens.
- **Never invent missing files or assets.** If something referenced does not exist, stop and
  ask. This has already caught a missing floor-plan asset once.
- Review existing code first and **match and elevate** the established design system rather
  than introducing a parallel one.
- Verify before reporting done: typecheck, build, and lint must all pass.

---

## 1. Project coordinates

| Item | Value |
|---|---|
| App root | `d:\FYP\prototype\web-ui` |
| Spec | `d:\FYP\prototype\POC_requirements.md` (screen map + per-screen prompts) |
| Reference design | `d:\FYP\UI designs\Web Designs-Light Themed.png` |
| Design/brand rules | `prototype/web-ui/AGENTS.md` (imported by `CLAUDE.md`) |
| Framework | Next.js 16.3.4 (App Router, Turbopack), React 19.2.8 |
| Styling | Tailwind **v4**, CSS-first — `@import "tailwindcss"` in `globals.css`. **There is no `tailwind.config`.** |
| Icons | `lucide-react` v1.41 (exports the `LucideIcon` type) |
| 3D | `three` v0.185 + `@types/three`, hand-rolled camera controls (no OrbitControls dependency) |
| Fonts | Geist + Geist Mono via `next/font/google` — **kept deliberately, see §2** |

### Verification commands

Run all three before declaring a step done:

```bash
cd d:/FYP/prototype/web-ui
npx tsc --noEmit                  # must be silent
npx next build                    # must compile + prerender
npx eslint src --max-warnings=0   # must be 0 ERRORS (4 known warnings, see §6)
```

Smoke-test routes against a running dev server (`npm run dev`, port 3000):

```bash
for p in / /dashboard /viewer/sector-4-mep /viewer/does-not-exist; do
  printf "%-28s %s\n" "$p" "$(curl -s -o /dev/null -w '%{http_code}' http://localhost:3000$p)"
done
# expected: 200 200 200 404
```

> Note: Next refuses to start a second dev server for the same directory. If one is already
> running on :3000, test against it instead of starting your own.

---

## 2. Locked decisions — do not re-litigate

These were decided by the user. Several **contradict the spec and the reference PNG on
purpose.** Do not "fix" them back.

| # | Decision | Why it matters |
|---|---|---|
| D1 | **Navigation is a hamburger-triggered floating overlay**, not a persistent left rail. | The reference PNG and `POC_requirements.md` §1 both say "persistent app shell ~220px sidebar". The user overrode this. The PNG/spec are authoritative on *visual language* (colour, cards, pills, typography) but **not** on shell chrome. |
| D2 | **The 3D workspace is a light Project Detail Shell.** The old dark fullscreen HUD is retired. | `ViewerHUD.tsx` is now dead code (see §6). |
| D3 | **The 3D canvas itself is light** (`#eef3f9`), matching the reference PNG. | Required re-toning all architectural materials and the lighting rig — they were authored for a dark scene. |
| D4 | **Semantic AI layers live as a 4th tab ("Layers") in the right 320px dock**, alongside Saved/Current/Tools. | The spec never mentions where they go, but they are the Stage-4 YOLOv8 differentiator and must stay reachable. |
| D5 | **"2D" view mode is a true orthographic top-down plan**, distinct from "Top" (which stays perspective). | |
| D6 | **Keep Geist + Geist Mono.** Do **not** switch to Inter / JetBrains Mono. | The spec §1 asks for Inter + JetBrains Mono. The user explicitly declined. |
| D7 | **Floor-plan artwork is hand-authored inline SVG.** Do not scrape or download a blueprint image. | Licensing risk on an FYP submission, and SVG lets status nodes anchor to real room geometry. |
| D8 | **`/dashboard` is an Operations Overview**, not a project-workspace hero and not a project list. It shows portfolio KPIs, a featured active scan, quick actions, recent projects, an activity feed, and worker status. The full project grid lives at `/projects` (Projects nav item). | The initial "workspace hero" redesign duplicated the flow already covered by `/projects → /viewer/[id]`, leaving the landing page without genuine dashboard value. Keeps the bespoke top bar (search + four status pills) built in the previous iteration. Hamburger still opens the drawer `Sidebar` so nav is preserved. |
| D9 | **The featured project card on `/dashboard` uses the static hero PNG** (`/images/dashboard background.png`) as its render, small. | The reference render is a marketing-grade isometric that the WebGL scene can't match yet; the real 3D viewer stays at `/viewer/[id]`. |

---

## 3. Architecture conventions established

Follow these when adding screens.

### `AppShell` is the layout for every authenticated screen
`src/components/AppShell.tsx`. Composes Navbar + overlay Sidebar + CAD grid background +
breadcrumb strip.

```tsx
<AppShell
  variant="contained"        // "contained" = scrolling max-w-7xl page (lists/dashboards)
                             // "fluid"     = h-screen, no padding (3D canvas, floor plan)
  activeNav="projects"       // NavId — which menu entry highlights
  onSelectNav={fn}           // optional; omit and AppShell routes by href instead
  breadcrumbs={[{ label: "All Projects", href: "/dashboard" }, { label: project.name }]}
  searchQuery={q} onSearchChange={setQ}   // omit both -> search renders read-only
  onOpenRecentSite={fn}      // optional; defaults to /viewer/<id>
>
```

### Navigation config is centralised
`src/lib/navigation.ts` owns `NavId`, `NAV_ITEMS`, `RECENT_SITES`, `STATUS_DOT`.

**`NAV_ITEMS[].href` is `string | null`.** `null` means "screen not built yet" and AppShell
will not navigate, so no menu item can 404. **When you finish a screen, flip its `href` to the
real path.** Currently only `/dashboard` has a href.

### Shared pieces
- `src/components/StatusPill.tsx` — status dot + tinted pill. Use for every status badge.
- `src/lib/mockData.ts` — all fixtures. Add new fixtures here, do not inline them in components.

### 3D viewer contracts
- `SceneBuilder` owns geometry, materials and **visibility resolution**. Layer toggles and
  render mode both funnel through the private `applyState()` — this is deliberate, because both
  controls address the point cloud and split handling let them overwrite each other.
- `Canvas3D` is a `forwardRef` exposing `Canvas3DHandle` = `{ zoomIn, zoomOut, resetView, fitToScreen }`.
- Props that pointer handlers need are mirrored into refs, synced in a **`useEffect` with no dep
  array**. React 19's `react-hooks/refs` rule forbids writing refs during render — do not move
  these assignments back into the render body.

---

## 4. Completed

### Step 0 — S1 Sign In ✅ (pre-existing)
`src/app/page.tsx`. Split hero, brand lockup, email/password with show-hide, security badges.
Any credentials navigate to `/dashboard`. Matches the reference PNG.

### Step 0b — S2 All Projects dashboard ✅ (pre-existing, refactored in Step 1)
`src/app/dashboard/page.tsx` + `ProjectCard.tsx`. Card grid, status filter pills, date-range
button, New Capture modal, job-status modal. See §6 for the unfinished list-view toggle.

### Step 1 — `AppShell` shared layout ✅
**Created:** `src/components/AppShell.tsx`, `src/lib/navigation.ts`
**Modified:** `Sidebar.tsx` (reads shared config, `role="dialog"`, body scroll lock),
`Navbar.tsx` (removed dead `onOpenNewCapture` prop, search props now optional),
`dashboard/page.tsx` (consumes AppShell).
**Fixed:** clicking a Ready/Complete site in Recent Sites previously did nothing.
**Verified:** tsc clean · build ok · eslint 0 errors.

### Viewer restructure + real X-Ray (user asks) ✅
- **3D shell:** `SceneBuilder.buildBaseRoom()` now closes the room off with a **front
  wall** and a **ceiling** at y=4. Shell materials (floor / all 4 walls / ceiling) are
  tracked in a new `shellMaterials[]` via a `registerShell()` helper. Removed the branch
  pipe I added to `buildPipes` last round — it was reading as "a pipe in the middle of the
  room."
- **Real X-Ray:** new `SceneBuilder.setXrayMode(enabled)` dials `opacity: 0.18`,
  `transparent: true`, and `depthWrite: false` on every shell material only. Interior
  systems (pipes / ducts / conduits / wires / sprinklers) are drawn either way, so the
  toggle actually *reveals* the plenum instead of hiding it. Wired through as a new
  `xrayMode` prop on `Canvas3D` with its own `useEffect`. The bottom-bar toggle relabelled
  from `Systems On/Off` to `X-Ray` / `X-Ray On`.
- **Viewer layout:** left `DetailSidebar` (260px) and right `RightDock` (320px) both
  gone. Content moves to a new **horizontal `ProjectDetailTopBar`** with identity + status
  pill + tabs + capture-provenance chips. `RightDock.tsx` deleted (fully replaced).
  Layers and Measurements now live in a new **`FloatingSidePanel`** popover (320px, top-
  right of the viewport, `max-h-[calc(100vh-9rem)]`), toggled from two new pill buttons
  next to `Export`. The Measurements top-bar tab and the "New Measurement" toggle both
  auto-open the panel to the right sub-tab. The whole viewport is now edge-to-edge for the
  3D canvas.

**Verified:** `npx tsc --noEmit` silent · `npx next build` compiles 6 routes · `npx eslint
src` 0 errors + 1 known warning.

### Wiring + Systems X-Ray toggle ✅ (superseded — see above)
- **Wiring:** `SceneBuilder.buildConduits()` now draws five colored wire bundles (red /
  black / blue / yellow / green) running through the cable tray using
  `THREE.CatmullRomCurve3` + `TubeGeometry` — each wire dips slightly at every drop
  point so the bundle reads as slack cable rather than a straight rod. Small dark
  bundle straps (torus rings) sit at ~2 m intervals. At each drop, two flexible wires
  (red + black) bend down through the elbow to the socket boxes on the floor.
- **X-Ray toggle:** new `Systems On` / `Systems Off` button in `ViewportBottomBar`
  (leftmost, before Splats), backed by a `handleToggleSystems` on the viewer page
  that flips `pipes`, `conduits`, `hvac`, `fire`, and `pointcloud` in one setState
  call. `areSystemsVisible` is derived — the button's state matches whether *any* of
  those layers is currently on. One click empties the room to the base shell; another
  restores every MEP layer.

**Verified:** `npx tsc --noEmit` silent · `npx next build` compiles 6 routes · `npx eslint
src` 0 errors + 1 known warning.

### Polish pass — nav fix, status labels, projects backdrop, 3D scene ✅
**User asks (four):** (1) clicking Dashboard from /projects didn't navigate; (2) status
pills read too generic; (3) /projects needed a construction-themed background; (4) the 3D
scene needed to look better.

**Fixes:**
- **Nav:** `app/projects/page.tsx` rewrote — removed the local `onSelectNav` handler that
  was swallowing menu clicks (it only mutated a local tab state), removed the in-page
  Floor Plan tab (already tech-debt in §6, superseded by `/floorplan/[id]`), and deleted
  `components/FloorPlanView.tsx`. Menu clicks now flow through `AppShell` → `router.push`.
  Cleared 3 of the 4 known lint warnings in the process.
- **Status labels:** `MOCK_PROJECTS.statusLabel` updated per project to something discipline-
  specific (e.g. `Training · RTX 4090`, `3DGS Ready · 1.45M splats`, `Signed Off · Handed to
  Coordinator`, `Draft · Awaiting Capture`, `Queued · 2 of 6 workers`). `ProjectCard.tsx` now
  renders `project.statusLabel` instead of hardcoded single words, with `truncate` on the
  text and shrink-safe dot markers. Filter pill labels on `/projects` also relabelled
  (Complete → "Signed Off").
- **Projects backdrop:** new `components/ProjectsBackdrop.tsx` — isometric building
  silhouette with a tower crane (lattice mast, cabin, jib, hook + cable), 54.00 m dimension
  arrow, drafting compass arc, radial gradient bloom, all at ~10% opacity so content stays
  readable. Sits `-z-0` behind the `/projects` content. Page header rewritten from
  "All Projects · Manage and view your construction sites and scans" (generic) to
  "Projects Portfolio · <n> sites captured · <ready> ready to review · <processing> in
  training · <complete> signed off" (real counts).
- **3D scene:** `Viewer3D/SceneBuilder.ts` substantially expanded — right wall + skirting
  boards; four corner columns with base plinths (was two); perpendicular tie beams;
  ceiling grid drafting lines; painted floor-tile scribe lines; wall-mounted control panel
  with three emissive indicator LEDs; door frame in the right wall; pipe elbows connecting
  risers to header; insulation sleeves on the supply header; hangers rodded to the ceiling;
  branch pipe running perpendicular to the header; HVAC flange bands, trapezoid transition,
  three louvered diffusers on the branch + a return grille; electrical cable tray with
  rails and rungs carrying the conduit runs; sprinkler heads rebuilt as brass bodies with
  deflector plates + fusible bulbs. `Canvas3D.tsx` switched to `PCFSoftShadowMap`, added
  soft-shadow bias config on the key light, exposure bumped to 1.05, and every major solid
  now casts / receives shadows.

**Verified:** `npx tsc --noEmit` silent · `npx next build` compiles 6 routes · `npx eslint
src` now reports 0 errors + **1** known warning (down from 4 — the FloorPlanView unused
imports are gone with the file).

### Step 7 — S7 & S8 Overview / Files / Report tabs ✅
**Created:** `ProjectDetail/OverviewTab.tsx` (4 stat cards + 3D preview card using the hero PNG
+ Layer Summary with per-layer progress bars + Recent Activity feed reusing
`MOCK_NOTIFICATIONS`), `ProjectDetail/FilesTab.tsx` (drag-drop upload zone accepting real
`onDrop` events + file list with per-kind tinted icons, monospace filename, size, upload date,
per-row hover-revealed Download / Delete actions), `ProjectDetail/ReportTab.tsx` (sticky
sub-toolbar with Generate/Export buttons + PDF-style A4-ish preview page with header, site
info stats row, 3D snapshot, executive summary paragraph, flagged-issues register table with
color-coded Change pills).
**Modified:** `lib/mockData.ts` (added `ProjectFile` type + `MOCK_PROJECT_FILES` — 7 seeded
rows spanning PLY, KSPLAT, OBJ, PDF, CSV, PNG, JSON), `ProjectDetail/DetailSidebar.tsx`
(flipped `overview`, `files`, `report` tabs to `ready: true`),
`app/viewer/[id]/page.tsx` (dispatches Overview/Files/Report in the centre pane and hides the
RightDock via a new `isFullWidthTab` flag covering History + these three).

Delivered:
- **Overview:** stats are real (`project.area`, `project.scansCount`, `project.dateCaptured`,
  flagged-issue count from `MOCK_CHANGE_LOG`); Layer Summary shows Plumbing/Electrical/HVAC/
  Fire/Structural with counts + proportional bars.
- **Files:** dropzone highlights on drag-over (`bg-blue-50/60` + solid blue border) and
  accepts native file drops — a dropped file infers its kind from the extension, formats bytes
  into KB/MB/GB, and prepends to the list. Delete removes rows locally. All 7 seeded rows are
  disciplined (real Nerfstudio artefacts + human-authored PDFs/CSVs).
- **Report:** Generate button spins for 900ms then updates the "Last generated" timestamp;
  Export as PDF is a stub button. The preview page is centered in a 820px card with a proper
  header (`Report #BS-2025-04-<id>`), site-info stats row, snapshot with caption, exec summary
  paragraph, and a flagged-issues register table showing all `MOCK_CHANGE_LOG` rows.

**Verified:** `npx tsc --noEmit` silent · `npx next build` compiles 6 routes · `npx eslint src`
0 errors + 4 known warnings.

### Dashboard → Operations Overview ✅ (out-of-order — user brief)
**Follow-up to the workspace-hero pivot.** The hero landing showed one project prettily but
duplicated `/projects → /viewer/[id]`, so `/dashboard` was rebuilt as a real portfolio landing
page. Kept the bespoke top bar (search + four status pills) from the previous iteration.

**Deleted:** `components/DashboardHome/HeroCanvas.tsx`, `ProjectSidebar.tsx`, `ScansStrip.tsx`
(the single-project-focused pieces from the earlier version).
**Created:** `components/DashboardHome/Overview.tsx` (page title bar + KPI row × 4 +
FeaturedActiveCard + QuickActionsCard + Recent Projects 3-mini-card strip) and
`ActivityColumn.tsx` (Recent Activity feed reusing `MOCK_NOTIFICATIONS` + WorkerStatusCard
reusing `MOCK_PIPELINE_STEPS` — worker identity, current-step progress bar, queue list).
**Rewrote:** `app/dashboard/page.tsx` — composes `DashboardOverview` in the left column and
`ActivityColumn` (360px) on the right; wires `NewCaptureModal`.

Everything is derived from real fixtures:
- KPIs count `MOCK_PROJECTS.length` (Total), `.filter(status==="processing")` (Active),
  ready+complete (Ready Models), and `MOCK_CHANGE_LOG.filter(flagged)` (Flagged Issues).
- Featured Active picks the first processing project, falls back to the first project.
- Recent Projects excludes the featured project and shows the next 3 — clicking a
  ready/complete card opens `/viewer/[id]`, others link back to `/projects`.
- Activity feed reuses the 5 most-recent notification fixtures.
- Worker Status reuses the pipeline steps: current in-progress step shows its progress bar +
  detail line; the queue list strikes through completed steps and pulses the active one.

**Verified:** `npx tsc --noEmit` silent · `npx next build` compiles 6 routes · `npx eslint src`
0 errors + 4 known warnings.

### Dashboard hero redesign ✅ (superseded — see above)
**Brief:** `public/images/dashbaord ultimate redesign.png` — a workspace-style dashboard
featuring one project (Sector 4 MEP Room) with a big hero render, floating tool overlays, a
right column of project stats, and a scans strip along the bottom. Uses
`public/images/dashboard background.png` as the render.

**Created:** `components/DashboardHome/TopBar.tsx` (bespoke top bar: hamburger + logo +
search-with-⌘K + 4 status pills + notifications + user block), `HeroCanvas.tsx` (background
image + project identity card + Orbit/Pan/Measure/Section/Compare tool pill + 2D/3D switch +
vertical icon rail + 3 measurement badges + compass rose + floor selector F5–B1 with mini
plan), `ProjectSidebar.tsx` (date button + Export + Project Overview card with 74% progress
bar + Total/Processed/Pending trio + Computer Vision Pipeline list with per-step status +
Quick Stats 2×2 grid), `ScansStrip.tsx` (Scans/Floor Plans/Reports tab strip + 6-thumb grid).
**Created:** `app/projects/page.tsx` — the previous project-grid dashboard, moved verbatim
except for `activeNav="projects"` and a new title component-of-record.
**Rewrote:** `app/dashboard/page.tsx` — composes the new hero layout, keeps the drawer
`Sidebar` for hamburger nav.
**Modified:** `lib/navigation.ts` — `projects` `href` flipped from `null` to `/projects` so the
menu item works.

**Verified:** `npx tsc --noEmit` silent · `npx next build` compiles 6 routes (adds
`○ /projects`) · `npx eslint src` reports 0 errors + 4 known warnings · dev-server smoke:
`/dashboard`, `/projects`, `/viewer/*`, `/floorplan/*` all 200, bad id → 404.

### Step 6 — S4b Comparison View ✅
**Created:** `src/components/ProjectDetail/ComparisonView.tsx` — full-width workspace shown
when the History tab is active. Sub-header with back button + Overlay/Split segmented toggle,
legend row with two dated scan chips, canvas with hand-authored dual-tinted SVG scenes, change-
log table below.
**Modified:** `lib/mockData.ts` (added `ComparisonScan` / `ComparisonPair` /
`MOCK_COMPARISON_PAIR` + `ChangeType` / `ChangeLogEntry` / `MOCK_CHANGE_LOG` — 5 seeded rows),
`ProjectDetail/DetailSidebar.tsx` (flipped `history` tab `ready: true`),
`app/viewer/[id]/page.tsx` (renders `<ComparisonView onBack={…} />` when `detailTab === "history"`
and hides the RightDock while it's active since the comparison is a full-width workspace).

Delivered:
- **Overlay mode:** older scan (blue) painted underneath; newer scan (green) drawn on top and
  clipped with `clip-path: inset(0 0 0 X%)`. Draggable wipe handle with a 36px pill and ↔ arrow
  icon, keyboard-accessible (`role="slider"`, arrow keys nudge 2%), clamped 2–98%.
- **Split mode:** two panes side-by-side, divider between, each labelled with scan name + date.
- Both scans share an isometric MEP schematic. Real differences reveal at the wipe: HVAC duct
  shifted up 12px in the newer scan (the +0.24 m delta), a chilled-water pipe drawn thicker in
  the newer scan (+12 mm OD), a conduit run present in the older scan only (Removed), and a
  sprinkler head + support bracket present in the newer scan only (Added).
- Legend chip stays pinned bottom-left; Fullscreen button bottom-right; top-left/right labels
  in each scan's tint.
- **Change-log table:** Element / Change Type (Added/Removed/Modified with icon + tinted pill) /
  Layer / Delta (monospace) / Flagged (toggleable button, seeded initial state from fixtures).

**Verified:** `npx tsc --noEmit` silent · `npx next build` compiles 5 routes · `npx eslint src`
reports 0 errors + 4 known warnings.

### Step 5 — S6 Notifications panel ✅
**Created:** `src/components/NotificationsPanel.tsx` (380px dropdown, tab bar
All/Scans/Projects/System, list of typed rows with tinted circular icons, footer link).
**Modified:** `lib/mockData.ts` (added `NotificationItem` type + `MOCK_NOTIFICATIONS` — 6
seeded rows spanning scan_processing, scan_completed, measurement_added, comment,
project_archived, scan_failed), `components/Navbar.tsx` (bell button now toggles the panel;
badge count derives from unread items instead of a hardcoded `3`; escape key + click-outside
dismiss).

Delivered:
- Panel opens anchored to the bell (`absolute top-full right-0 mt-2`), max-height capped to
  fit the viewport, tab bar reusing the segmented pill style.
- Rows: tinted circular icon (amber clock / green check / blue ruler / grey message / grey
  archive / red warning), bold title, two-line description, right-aligned relative timestamp
  (e.g. `12m ago`), blue unread dot on the right edge.
- Empty-state message when a bucket has no items.
- `Mark all read` action zeroes the badge and clears the unread dots.
- Bell icon flips to `bg-blue-50 text-[#2563eb]` while the panel is open; a
  `data-notifications-toggle` attribute lets the panel's outside-click listener ignore the
  bell so it doesn't race the toggle.

**Verified:** `npx tsc --noEmit` silent · `npx next build` compiles 5 routes · `npx eslint src`
reports 0 errors + 4 known warnings.

### Step 4 — S2.5 Floor Plan route ✅
**Created:** `src/app/floorplan/[id]/page.tsx` (AppShell fluid, breadcrumb, header strip with
building title + floor tabs + disabled `+ New Capture`, floating legend), plus
`components/FloorPlan/FloorPlanCanvas.tsx` (hand-authored inline SVG blueprint) and
`components/FloorPlan/FloorTabStrip.tsx` (segmented control matching `ViewportOverlays`).
**Modified:** `lib/mockData.ts` (added `BuildingPlan`/`BuildingFloor`/`FloorPlanRoom` types
plus `MOCK_BUILDING_PLANS` — Tower A with 4 floors × 6-7 rooms each, real x/y/w/h geometry in
a 1000×620 viewBox), `lib/navigation.ts` (flipped `floorplan` href to
`/floorplan/tower-a-floors-5-8`), `components/ProjectCard.tsx` (Ready/Complete cards route via
`hasBuildingPlan(id)`: multi-floor → `/floorplan/[id]`, single-room → `/viewer/[id]`).

Delivered:
- Hand-authored SVG plan per floor: outer wall, dashed corridor outlines, per-room fills keyed
  to discipline (MEP / office / conference / utility / lobby / corridor), door swing arcs,
  metric dimension ruler, north-arrow compass, room labels + scan counts.
- Status nodes anchored to each room's centre — green (Ready), teal (Complete), amber
  (Processing with a pulsing SVG ring animation). Hover → white tooltip card with status pill
  + scan count + call-to-action; only Ready/Complete rooms are clickable, Processing rooms show
  a `not-allowed` cursor.
- Every clickable room routes to the parent project's own `/viewer/[id]` — one 3D model stands
  in for all rooms this pass (POC scope).
- Floor tab strip shows floor label + discipline sub-label; active tab surfaces in white.
- Floating legend top-right counts Ready / Processing / Complete for the active floor and
  restates the click-to-open hint. `+ New Capture` is disabled with a mobile-app tooltip.

**Verified:** `npx tsc --noEmit` silent · `npx next build` compiles 5 routes (adds
`ƒ /floorplan/[id]`) · `npx eslint src` reports 0 errors + 4 known warnings · dev-server smoke
test: `/floorplan/tower-a-floors-5-8` → 200, `/floorplan/does-not-exist` → 404.

### Step 3 — S4a Measurements panel ✅
**Created:** `ProjectDetail/MeasurementsPanel.tsx` (Saved / Current / Tools sub-views + pinned
`+ New Measurement` primary button).
**Modified:** `lib/mockData.ts` (added `SavedMeasurement` type and `MOCK_SAVED_MEASUREMENTS`
fixture — 5 rows: length, height, pipe, width, beam), `Viewer3D/Canvas3D.tsx` (extended
`Canvas3DHandle` with `deleteMeasurement(id)` and `clearMeasurements()` — both re-emit
`onMeasurementsChange` so the panel stays in sync), `ProjectDetail/RightDock.tsx` (delegates
the three measurement tabs to `MeasurementsPanel`; the Layers branch is unchanged), and
`app/viewer/[id]/page.tsx` (lifted `isMeasureMode` out of a hardcoded `false` into React state;
toggling it auto-focuses the Current tab; delete/clear route through the canvas handle so 3D
markers and rows tear down together).

Delivered:
- **Saved tab:** search input + 5 seeded rows, each with a tinted type icon, monospace-bold
  value, label, right-aligned timestamp, and a hover-revealed overflow menu.
- **Current tab:** live rows from the canvas session; per-row `Trash2` (delete a single
  measurement) plus a `Clear all` header action.
- **Tools tab:** measure-mode toggle switch, five-type chip grid (only `length` wired — the
  rest are documented as Stage 5), and a session `Clear` button.
- Monospace font only on numeric values (`{value} m`), per acceptance criterion.

**Verified:** `npx tsc --noEmit` silent · `npx next build` compiles (5/5 static pages) ·
`npx eslint src --max-warnings=100` reports 0 errors + the 4 known warnings from §6.

### Step 2 — S3/S4 Project Detail Shell + 3D Viewer ✅
**Created:** `ProjectDetail/DetailSidebar.tsx` (260px, 6 tabs, capture provenance),
`ProjectDetail/ViewportOverlays.tsx` (view toggle, 6-icon tool rail, axis gizmo, bottom bar),
`ProjectDetail/RightDock.tsx` (320px, Saved/Current/Tools/Layers), `StatusPill.tsx`
**Rewrote:** `viewer/[id]/page.tsx`, `Viewer3D/Canvas3D.tsx`
**Modified:** `Viewer3D/SceneBuilder.ts` (light theme + `RenderMode` + `applyState()`)

Delivered: light viewport, dual camera with true orthographic 2D, render modes
(Textured / Mesh / Point Cloud), working zoom/reset/fit via imperative handle, orbit-tracking
XYZ gizmo, live metric coordinate readout, fullscreen, export modal, functional Layers tab.

**Fixed two real bugs:** `/viewer/<bad-id>` silently fell back to `MOCK_PROJECTS[0]` (now
`notFound()`); click-vs-drag compared against the last mousemove instead of the drag origin, so
slow drags registered as measurement clicks.

**Verified:** tsc clean · build ok · eslint 0 errors · routes `200/200/200/404` · SSR output
contains real project name, detail nav and layer panel.

---

## 5. Next steps

Ordered per `POC_requirements.md` §4. **Do one per session/turn.**

### Step 8 — S9: Empty & error states ◀ NEXT
Empty search results, empty measurements, failed-scan state, offline. Lowest priority.

---

## 6. Known issues & tech debt

| Issue | Location | Notes |
|---|---|---|
| **Orphaned dead code** | `Viewer3D/ViewerHUD.tsx` | The retired dark HUD. Nothing imports it. User declined deletion once — **ask before removing.** |
| **List view does nothing** | `dashboard/page.tsx` | `viewMode` state drives only button styling; the grid is always 3-col. Either implement the list layout or remove the toggle. |
| **`globals.css` conflicts** | `src/app/globals.css` | Duplicate `--background` declaration, plus a `prefers-color-scheme: dark` block setting `#0a0a0a`. Currently inert because `layout.tsx` hardcodes `bg-[#f8fafc]` on `<body>` — but it is a live trap. |
| 1 pre-existing lint warning | `ExportModal.tsx:29` | Unused `filename` param. Harmless; clean up when touching the file. (FloorPlanView deleted — its 3 warnings gone with it.) |
| Non-functional controls | dashboard date-range button, `View all activity →` footer link in the notifications panel, "Export as PDF" in `ReportTab.tsx` | Bell is now wired (Step 5); the rest stay stubs. `Generate Report` in ReportTab shows a spinner + updates the timestamp but doesn't produce a file. |
| Search is shallow | `dashboard/page.tsx` | Filters name/block/floor only. |
| Dashboard KPI deltas are static strings | `components/DashboardHome/Overview.tsx` | Each KPI card shows a helper caption ("+2 this month", "Training on RTX 4090", …). The number itself is real (derived from fixtures) but the caption is fixed text — swap in real trend data when there is any. |
| Every floor-plan room opens the same 3D model | `components/FloorPlan/FloorPlanCanvas.tsx` (`openRoom`) | POC scope — clicking any room routes to the parent project's own `/viewer/[id]` rather than a per-room scan. Wire per-room `targetProjectId` on `FloorPlanRoom` when real per-room captures land. |
| Non-length measurement types are inert | `ProjectDetail/MeasurementsPanel.tsx` (Tools tab) | The five-chip grid shows length/height/pipe/width/beam but only `length` maps to a canvas mode — the others render for demo completeness and ship in Stage 5. |
| Saved-measurement overflow menu is inert | `ProjectDetail/MeasurementsPanel.tsx` (Saved tab) | The `…` button on saved rows is present but not wired (no rename/export/delete actions yet). |
| Nav items are inert | `lib/navigation.ts` | Projects/Scans/Reports/Team/Settings have `href: null` by design until built. |

---

## 7. Screen map status

| # | Screen | Status |
|---|---|---|
| S1 | Sign In | ✅ Done |
| S2 | All Projects dashboard | ✅ Done — **moved to `/projects`**. `/dashboard` is now the redesigned hero (see D8). |
| S2.5 | Floor Plan | ✅ Done (POC: all rooms route to the parent project's viewer) |
| S3/S4 | Project Detail Shell + 3D Viewer | ✅ Done |
| S4a | Measurements panel | ✅ Done |
| S4b | Comparison View | ✅ Done |
| S6 | Notifications | ✅ Done |
| S7 | Overview tab | ✅ Done |
| S8 | Files / Report tabs | ✅ Done |
| S9 | Empty / error states | ⬜ Step 8 |

---

## 8. Changelog

- **2026-09-09** — Viewer restructure (user brief): closed the 3D room off with a front
  wall + ceiling; removed the mis-placed branch pipe; rewrote the X-Ray toggle so it now
  dials only the *shell* to translucent (`opacity 0.18`, `depthWrite: false`) via a new
  `SceneBuilder.setXrayMode` and a matching `xrayMode` prop on `Canvas3D`, keeping every
  MEP system drawn either way. Rebuilt the viewer layout: dropped the left `DetailSidebar`
  and right `RightDock` in favour of a horizontal `ProjectDetailTopBar` (identity + tabs +
  capture provenance) and two floating popovers (`FloatingSidePanel` for Layers and
  Measurements) triggered from pills next to Export. Bottom-bar toggle relabelled to
  `X-Ray`. `RightDock.tsx` deleted.
- **2026-09-09** — Added electrical wiring to the 3D scene (5 colored wire bundles in the
  cable tray as `TubeGeometry` along a Catmull-Rom curve with per-drop dips + 2-wire
  drops to socket boxes + torus straps) and a **Systems On/Off** X-Ray toggle in the
  viewport bottom bar that flips every MEP layer (pipes, conduits, HVAC, fire, point
  cloud) in a single click.
- **2026-09-09** — Polish pass (user asks): fixed Dashboard nav from /projects (removed the
  local `onSelectNav` that intercepted menu clicks; retired the in-page FloorPlan tab and
  deleted `FloorPlanView.tsx`); replaced generic one-word status labels with discipline-
  specific phrasing (`Training · RTX 4090`, `3DGS Ready · 1.45M splats`, etc.) and wired
  `ProjectCard` to render `project.statusLabel` instead of hardcoded text; added
  `ProjectsBackdrop` (isometric building silhouette + tower crane + drafting arc behind
  /projects); rewrote the /projects header to show real counts. Enriched the 3D scene
  substantially (right wall + skirtings, four corner columns with plinths, tie beams,
  ceiling grid, floor tile scribes, control panel with LEDs, door frame, pipe elbows +
  hangers + insulation sleeves, HVAC bands + transition + three louvered diffusers + return
  grille, electrical cable tray + drops + sockets, proper brass sprinkler heads with
  deflectors) and switched to `PCFSoftShadowMap` with a tuned shadow bias.
- **2026-09-09** — Step 7: S7 & S8 tabs — Overview (4 real-data stat cards + 3D preview +
  Layer Summary with proportional bars + Recent Activity feed), Files (native drag-drop that
  infers kind from extension + 7-row list with per-kind tinted icons and hover Download /
  Delete), Report (PDF-style preview card with header/stats/snapshot/summary/flagged-issues
  register + Generate Report spinner + Export as PDF stub). All three centre-pane tabs hide
  the RightDock via a new `isFullWidthTab` flag.
- **2026-09-09** — Project thumbnails swapped for real photos from Unsplash (free license, no
  attribution required). Six 1200-wide JPEGs downloaded to `public/thumbnails/` via the
  Unsplash download endpoint and referenced from `MOCK_PROJECTS` (paths flipped from `.png`
  to `.jpg`). Old placeholder PNGs deleted. Photo IDs recorded below (D7 is unchanged — that
  decision covers floor-plan blueprints, not project photos).
  - `card1_mep.jpg` — Unsplash photo `2nsQWyPU6tw` (Sector 4 MEP Room)
  - `card2_tower_a.jpg` — Unsplash photo `fNILto8puuU` (Tower A - Floors 5-8)
  - `card3_west_wing.jpg` — Unsplash photo `IB0VA6VdqBw` (West Wing)
  - `card4_parking.jpg` — Unsplash photo `HfSJz23_BOM` (Parking Garage)
  - `card5_north_tower.jpg` — Unsplash photo `NMrUtSA7094` (North Tower)
  - `card6_east_wing.jpg` — Unsplash photo `kK7uPfb2YWU` (East Wing)
- **2026-09-09** — Dashboard → Operations Overview: reverted the workspace-hero landing to a
  real portfolio dashboard (KPIs · Featured Active · Quick Actions · Recent Projects · Recent
  Activity · Worker Status), all derived from existing fixtures. Kept the bespoke top bar with
  search + four status pills. Decision D8 replaced.
- **2026-09-09** — Dashboard hero redesign (out-of-order, user brief): `/dashboard` becomes a
  project-workspace hero for Sector 4 MEP Room built from
  `public/images/dashboard background.png`, with tool pill, 2D/3D toggle, icon rail,
  measurement callouts, compass, floor selector, right column of project stats + pipeline +
  quick stats, and bottom Scans/Plans/Reports strip. Old project-grid moves to `/projects`;
  Projects nav item finally has a real href. Decisions D8 + D9 recorded.
- **2026-09-09** — Step 6: S4b Comparison View — Overlay wipe + Split View toggle, draggable
  keyboard-accessible wipe handle, hand-drawn isometric MEP scenes tinted per scan showing real
  differences (shifted duct, thicker pipe, removed conduit, added sprinkler/bracket), change-log
  table with Added/Removed/Modified pills and per-row Flag toggle. Reached from the History
  tab; hides the RightDock while active.
- **2026-09-09** — Step 5: S6 Notifications panel — 380px dropdown from the bell with
  All/Scans/Projects/System tabs, 6 typed seeded items, unread badge derived from fixtures,
  `Mark all read`, click-outside/Escape dismissal. Bell no longer hardcodes `3`.
- **2026-09-09** — Step 4: S2.5 Floor Plan route (`/floorplan/[id]`) with hand-authored SVG
  blueprint (walls, doors, dimensions, north arrow), 4-floor Tower A fixture, floor tab strip,
  clickable status nodes with hover tooltips, floating legend, disabled New Capture. All rooms
  currently open the parent project's own viewer (POC scope). `hasBuildingPlan` decides whether
  a project card routes to the plan or straight to the 3D viewer.
- **2026-09-09** — Step 3: S4a Measurements panel wired into RightDock — Saved (5 seeded rows),
  Current (live session rows w/ per-row delete + Clear all), Tools (measure-mode toggle, type
  chips, session clear). Lifted `isMeasureMode` into state; extended `Canvas3DHandle` with
  `deleteMeasurement`/`clearMeasurements`.
- **2026-09-09** — Step 2: S3/S4 Project Detail Shell + light 3D viewer; orthographic 2D; render
  modes; axis gizmo; fixed bad-id fallback and drag-as-click bugs. Decisions D2–D7 recorded.
- **2026-09-09** — Step 1: `AppShell` + centralised navigation config; Sidebar/Navbar refactor;
  fixed dead Recent Sites clicks. Decision D1 recorded.
