# BuildScan 3D — Design-System-Matched PoC Spec & Detailed Build Prompts (v2)

This replaces the generic design tokens in v1 with the **actual system shown in your reference designs** (login, All Projects dashboard, 3D Workspace, Measurements panel, Comparison View, Notifications). Every prompt below is written to match that exact visual language, then goes deeper than what's currently mocked up.

---

## 1. Design System (extracted from your reference)

```
Brand: hexagon logo mark (blue gradient) + wordmark "BuildScan" (black, bold) "3D" (blue, bold).

Color palette:
- Primary blue: #2563EB (buttons, active nav, links, primary icons)
- Background: #F8FAFC (app canvas)
- Surface: #FFFFFF cards, 12–16px border radius, 1px #E5E7EB border, soft low-opacity shadow
- Status colors (pill = colored dot + colored text on tinted background):
  - Ready / Complete → green (#16A34A) on #ECFDF5
  - Processing → amber (#D97706) on #FFFBEB
  - Draft → gray (#6B7280) on #F3F4F6
  - Failed → red (#DC2626) on #FEF2F2
  - Archived → slate (#64748B) on #F1F5F9
Typography: Inter or similar geometric sans. Headings bold/semibold, body regular,
  metadata/timestamps small + gray (#6B7280). Monospace (JetBrains Mono) ONLY for
  measurement values (e.g. "12.48 m") and coordinate/log data.
Iconography: Lucide-style outline icons throughout (sidebar nav, tool palette,
  notification type icons, panel headers).

Persistent app shell (used on every authenticated screen):
- Top bar: logo (left) · "All Projects" dropdown selector · global search bar
  (center-left, placeholder "Search projects, scans, or sites...") · notification
  bell with unread-count badge · stacked team avatar group · user profile block
  (avatar + name + role "Project Manager") with dropdown chevron.
- Left sidebar (persistent, ~220px): nav items with icon + label — Dashboard,
  Projects, Scans, Reports, Team, Settings. Active item = light blue background,
  blue text/icon, rounded. Below nav: "Recent Sites" list — colored status dot +
  site name + status label per row, no icons.

Buttons: primary = solid blue, rounded-lg, white text. Secondary = white bg,
  gray border, dark text. Icon-only buttons = ghost, rounded, gray-600 icon.
Segmented controls (view toggles, tabs): pill-shaped container, active segment =
  white bg + shadow inside a light-gray track (e.g. Saved/Current/Tools,
  Overlay/Split View, 3D/2D/Top/Side/Front).
Filter pills (status filters row): rounded-full outline pills, colored dot +
  label, active = filled light-blue background.
```

Use this block verbatim at the top of every prompt you run — it's what makes every screen you generate after this look like it belongs to the same product.

---

## 2. Screen Map (reference screens + gaps filled in)

| # | Screen | In your reference? | Notes |
|---|---|---|---|
| S1 | Sign In | ✅ Shown | Split-hero layout, not a plain centered card |
| S2 | All Projects (Dashboard) | ✅ Shown | Card grid, filters, search, view toggle |
| **S2.5** | **Floor Plan View** | New | Bridges "click a project" → "click a room" per your original ask, styled to match S2/S4 |
| S3 | Project Detail Shell | ✅ Shown (as 3D Workspace) | Left detail nav: Overview, 3D Viewer, Measurements, History, Files, Report |
| S4 | 3D Viewer (within shell) | ✅ Shown | Central canvas, view-mode toggle, floating tool palette |
| S4a | Measurements Panel | ✅ Shown | Tabbed (Saved/Current/Tools), list + New Measurement |
| S4b | Comparison View | ✅ Shown | Maps to your original "S5 Timeline", but as Overlay/Split compare |
| S6 | Notifications | ✅ Shown | Tabbed (All/Scans/Projects/System) slide-over or panel |
| **S7** | **Overview tab** | New | The left-nav "Overview" item is shown but its content isn't — fill this in |
| **S8** | **Files / Report tabs** | New | Same — nav items shown, content not shown |
| **S9** | **Empty / Error states** | New | Still recommended, see v1 §3 |

**On the floor-plan question specifically:** your reference dashboard is a project *card grid*, not a floor plan. Rather than replace it, I'd keep the card grid as the main "All Projects" view (it's already well designed and matches enterprise SaaS conventions) and add the floor plan as **S2.5**, reached one of two ways — recommend testing both in your demo script:
- Clicking a multi-room project card (e.g. "Tower A — Floors 5-8") opens the Floor Plan view instead of jumping straight to one 3D model, since a whole tower has many scannable rooms.
- Clicking a single-room project card (e.g. "Sector 4 MEP Room") skips the floor plan and opens the 3D Workspace directly, since there's only one thing to show.

This gives you the floor-plan-click-to-3D moment *and* keeps the dashboard exactly as designed.

---

## 3. Detailed Build Prompts

Paste the Design System block (§1) once at the start of your session/tool, then run these one at a time.

### Prompt 1 — S1: Sign In
```
Build a sign-in screen for BuildScan 3D matching this design system: [paste §1].
Layout: two-panel split screen, no scroll.
Left panel (~55% width): light blue-gray gradient background, a large stylized
wireframe/blueprint illustration of a building under construction (line-art,
blue accent), tagline top-left "Real sites. 3D truth." / "Verify. Measure.
Build better." in gray, and small caption bottom-left "Powered by spatial data.
Built for construction."
Right panel (~45% width): white background, vertically centered content —
hexagon logo + "BuildScan 3D" wordmark, subtitle "Construction Spatial
Intelligence Platform", email input (envelope icon), password input (lock icon,
show/hide eye toggle), primary "Sign In" button (full width, blue), "Forgot
password?" link centered below, and two small outline pill badges at the
bottom: "🔒 256-bit encrypted" and "🛡 SOC 2 compliant".
Functionality: any input + Sign In click navigates to /dashboard (no real auth).
```

### Prompt 2 — S2: All Projects (Dashboard)
```
Build the "All Projects" dashboard for BuildScan 3D matching this design system:
[paste §1]. Include the persistent app shell (top bar + left sidebar as
specified). Sidebar "Dashboard" item active. Below the sidebar nav, a "Recent
Sites" section listing 4 sites with colored status dots and status labels.
Main content: page header "All Projects" (bold) + subtitle "Manage and view
your construction sites and scans." Below header, a row containing: status
filter pills (All / Ready / Processing / Draft / Archived, each with a colored
dot, "All" active by default), grid/list view toggle icons (right-aligned), a
date-range picker button (e.g. "Apr 1, 2025 – Apr 30, 2025"), and a primary
"+ New Capture" button with a tooltip on hover reading "Initiate from BuildScan
mobile app".
Below that: a 3-column grid of project cards. Each card: site/room photo
thumbnail with a status badge overlaid top-left on the image, title (bold),
metadata line (Floor · Block · Area in m²), a footer row with capture date
(calendar icon) and scan count (camera icon), and a "..." overflow menu icon
top-right of the card.
Seed 6 cards with varied statuses (2 Processing, 2 Ready, 1 Draft, 1 Complete),
mixing single-room projects (e.g. "Sector 4 MEP Room") and multi-floor
projects (e.g. "Tower A - Floors 5-8") — the distinction matters for later
navigation logic.
Clicking a single-room card should visually indicate navigation to the 3D
Workspace; clicking a multi-floor card should indicate navigation to a Floor
Plan view.
```

### Prompt 3 — S2.5: Floor Plan View (new, bridges dashboard → 3D model)
```
Build a "Floor Plan View" screen for BuildScan 3D matching this design system:
[paste §1], reached by clicking a multi-floor project card.
Include the persistent app shell. Breadcrumb below the top bar: "All Projects
> Tower A - Floors 5-8" with a home/back icon.
Below the breadcrumb, a horizontal floor tab strip (Floor 5, Floor 6 [active],
Floor 7, Floor 8) styled as the segmented-control pattern from the design system.
Main content: a large 2D architectural floor plan (line-art/blueprint style,
consistent with the S1 hero illustration) filling most of the screen, with
circular status-colored interaction nodes placed on individual rooms. A small
legend card floats top-right explaining node colors. A "+ New Capture" button
(disabled, same tooltip as S2) sits top-right of the content area.
Interactions to depict: hovering a node shows a tooltip card with room name +
scan count; an amber "Processing" node has a subtle pulse/glow; clicking a
green "Ready" node should visually indicate navigation into the Project Detail
Shell / 3D Workspace for that room.
```

### Prompt 4 — S3/S4: Project Detail Shell + 3D Viewer
```
Build the "Project Detail" screen for BuildScan 3D matching this design system:
[paste §1] — this is the main workspace shown when opening a single scan.
Include the persistent app shell. Breadcrumb: "All Projects > Sector 4 MEP Room".
Left detail panel (~260px, inside the main content area, separate from the
outer app sidebar): project title (bold), status pill ("Ready", green),
metadata line (Floor 3 · Block B · 847 m² · 6 scans), then a secondary nav
list with icons: Overview, 3D Viewer [active], Measurements, History, Files,
Report — active item styled the same as the outer sidebar's active state.
Center: large 3D canvas area (Three.js/WebGPU placeholder) rendering a sample
point-cloud/mesh room. Top-left of the canvas: a segmented view-mode toggle
(3D [active] / 2D / Top / Side / Front). Floating vertical icon toolbar on the
right edge of the canvas (rotate, pan, zoom in, zoom out, reset view, fit-to-
screen — 6 icons in a rounded white pill container). Bottom-left: a small XYZ
axis gizmo. Bottom-center: a small toolbar with a diamond/points icon,
fullscreen icon, and a "Point Cloud" dropdown (for switching render mode,
e.g. Point Cloud / Mesh / Textured).
Right side of the canvas: leave a 320px area reserved/blank — this will hold
the Measurements panel from Prompt 5.
```

### Prompt 5 — S4a: Measurements Panel
```
Build the "Measurements" side panel for BuildScan 3D matching this design
system: [paste §1], docked to the right of the 3D Viewer canvas (320px wide).
Header row: "Measurements" title + small grid/layout icon button top-right.
Below: a segmented tab control — Saved [active] / Current / Tools.
Below tabs: a search input with a search icon, placeholder "Search
measurements...".
Below search: a scrollable list of measurement items, each row containing a
small type icon (ruler, height, pipe, width, beam — vary per item), a bold
value in monospace font (e.g. "12.48 m"), a label below it (e.g. "Duct
Length"), a timestamp on the right ("Apr 28, 10:42 AM"), and a "..." overflow
menu. Seed 5 rows with varied measurement types.
Bottom of panel: a full-width primary "+ New Measurement" button (blue).
```

### Prompt 6 — S4b: Comparison View
```
Build a "Comparison View" screen for BuildScan 3D matching this design system:
[paste §1], reached from the "History" tab in the Project Detail left panel.
Include the app shell + breadcrumb + left detail panel (History tab active).
Header: back arrow + "Comparison View" title.
Below header: a segmented toggle — Overlay [active] / Split View.
Below that: a legend row with two colored dot + label + date pairs — e.g.
"● Scan A — Apr 12, 2025" (blue) and "● Scan B — Apr 28, 2025" (green).
Main area: a large 3D render showing both scans overlaid with color-coded
diff — blue for one scan's geometry, green for the newer/changed elements,
a draggable vertical slider handle in the center for wipe-compare, and a
small expand/fullscreen icon bottom-right. A small legend chip bottom-left
repeats "Scan A (older)" / "Scan B (newer)".
For Split View mode (describe as a secondary state): side-by-side panes
instead of the overlay, each labeled with its scan date.
Below the visual (if space allows, or as a scroll continuation): a change-log
table — columns Element, Change Type (Added/Removed/Modified, color-coded
text), Layer, Delta, Flagged (checkbox). Seed 5 rows.
```

### Prompt 7 — S6: Notifications
```
Build a "Notifications" panel for BuildScan 3D matching this design system:
[paste §1], opened from the bell icon in the top bar (render as a right-aligned
slide-over or dropdown panel, ~380px wide).
Header: bell icon + "Notifications" title.
Below header: a segmented tab row — All [active] / Scans / Projects / System.
Below tabs: a scrollable list of notification items. Each item has a small
circular icon-background on the left (color matches the event type: amber
clock = processing, green check = completed, blue ruler = measurement added,
gray avatar = comment, gray building = archived, red warning = failed), a
bold title line, a gray description line below it (including project/site
name where relevant), and a right-aligned relative timestamp ("12m ago", "1h
ago", "5h ago").
Seed 6 items covering: scan still processing, scan completed, new measurement
added, a team comment, a project archived, and a failed scan (red).
Footer: a centered "View all activity →" link below the list.
```

### Prompt 8 — S7 & S8: Overview / Files / Report tabs (fill in the remaining left-nav items)
```
Build three additional tab contents for the Project Detail Shell in BuildScan
3D, matching this design system: [paste §1]. Reuse the same app shell,
breadcrumb, and left detail panel from Prompt 4 for all three; only the main
content area changes.

1. Overview tab: a summary dashboard for this single scan — key stats as small
   cards (Total Area, Scan Count, Last Updated, Flagged Issues), a small
   embedded static 3D thumbnail/preview, a "Recent Activity" mini-feed (reuse
   notification row styling, filtered to this project), and a "Layer Summary"
   card listing each semantic layer (Plumbing, Electrical, HVAC, Structural,
   Drywall) with an element count each.

2. Files tab: a simple file-manager list — rows with file-type icon, filename,
   file size, upload date, and download/delete icon buttons. Include a
   drag-and-drop upload zone at the top (dashed border, upload icon, "Drag
   files here or click to upload").

3. Report tab: a document-style preview — a "Generate Report" primary button
   top-right, and below it a preview card resembling a PDF page: site info
   header, an embedded static 3D snapshot image, a summary paragraph
   placeholder, and a table of flagged issues. Include an "Export as PDF"
   secondary button.
```

---

## 4. Build Order (updated)

1. Design system tokens (§1) — do this first, reuse everywhere
2. S1 (Sign In) + S2 (All Projects) — establishes shell + card patterns
3. S3/S4 (Project Detail Shell + 3D Viewer) + S4a (Measurements) — your highest-value screen, most demo time will live here
4. S2.5 (Floor Plan) — adds the multi-room drill-down you wanted
5. S6 (Notifications) — quick, reuses list-row pattern from Measurements
6. S4b (Comparison View) — reuses the Project Detail shell
7. S7/S8 (Overview, Files, Report) — fill remaining nav items last, lowest priority if time-constrained

Minimum viable demo path if time is tight: **S1 → S2 → S3/S4 → S4a**. Everything else layers on top of that same shell.