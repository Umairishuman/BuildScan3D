# BuildScan 3D — Build Status & Handoff

**Single source of truth for what is built, what is next, and what has already been decided.**
Last updated: 2026-09-09 (Dashboard → Operations Overview) · Branch: `prototype`

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

### Step 7 — S7 & S8: Overview / Files / Report tabs ◀ NEXT
**Spec:** Prompt 8.
Fills the remaining `DetailSidebar` placeholders. Overview = stat cards + 3D thumbnail +
recent-activity feed + Layer Summary. Files = drag-drop zone + file list. Report = Generate
Report button + PDF-style preview + Export as PDF.

### Step 8 — S9: Empty & error states
Empty search results, empty measurements, failed-scan state, offline. Lowest priority.

---

## 6. Known issues & tech debt

| Issue | Location | Notes |
|---|---|---|
| **Orphaned dead code** | `Viewer3D/ViewerHUD.tsx` | The retired dark HUD. Nothing imports it. User declined deletion once — **ask before removing.** |
| **List view does nothing** | `dashboard/page.tsx` | `viewMode` state drives only button styling; the grid is always 3-col. Either implement the list layout or remove the toggle. |
| **`globals.css` conflicts** | `src/app/globals.css` | Duplicate `--background` declaration, plus a `prefers-color-scheme: dark` block setting `#0a0a0a`. Currently inert because `layout.tsx` hardcodes `bg-[#f8fafc]` on `<body>` — but it is a live trap. |
| 4 pre-existing lint warnings | `ExportModal.tsx:29`, `FloorPlanView.tsx:6` | Unused `filename`, `Layers`, `Eye`, `Activity`. Harmless; clean up when touching those files. |
| Non-functional controls | dashboard date-range button, `View all activity →` footer link in the notifications panel | Bell is now wired (Step 5); date-range button and `View all` link stay stubs until later steps. |
| Search is shallow | `dashboard/page.tsx` | Filters name/block/floor only. |
| **Dashboard floor-plan tab still live** | `projects/page.tsx` + `components/FloorPlanView.tsx` | The old project-grid page (now at `/projects`) keeps its "Floor Plan" tab rendering abstract rectangles from `MOCK_FLOOR_PLAN_SECTORS`. Superseded by the new `/floorplan/[id]` route; retire the tab and delete `FloorPlanView.tsx` next time `/projects` is touched. |
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
| S7 | Overview tab | ⬜ Step 7 |
| S8 | Files / Report tabs | ⬜ Step 7 |
| S9 | Empty / error states | ⬜ Step 8 |

---

## 8. Changelog

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
