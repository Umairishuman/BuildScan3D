/**
 * Server-side only: lists every processed scan bundle in public/scans/ as a Project, so each run of
 * scripts/run_full.sh shows up in the Projects tab without editing mockData.ts (COMPLETION_PLAN 5.3).
 *
 * A bundle is a folder public/scans/<capture>_<tag>/ with scan.json (written by export_web.py). The card's
 * numbers come from scan.json; the scan number from dataset/.scan_numbers.tsv (D-065); the run ID and date
 * from the matching TRAINING.md heading ("... (tag `<tag>`)") when there is one. Bundles are gitignored
 * (D-061), so this lists what exists on the machine that serves the web UI.
 */
import fs from "node:fs";
import path from "node:path";
import type { Project } from "./mockData";
import type { ScanInfo } from "@/components/Viewer3D/scanTypes";

const WEB_ROOT = process.cwd(); // prototype/web-ui when started with `next dev` / `next start`
const SCANS_DIR = path.join(WEB_ROOT, "public", "scans");
const REPO_ROOT = path.resolve(WEB_ROOT, "..", "..");
const DATASET_DIR = path.join(REPO_ROOT, "dataset");

/** Project ids of auto-listed bundles start with this, so they never clash with hand-written ones. */
export const BUNDLE_ID_PREFIX = "run-";

const SAFE_FOLDER = /^[A-Za-z0-9][A-Za-z0-9_.-]*$/;

export interface BundleRef {
  folder: string;
  capture: string;
  tag: string;
  scanNumber: number | null;
}

function readScanNumbers(): Map<string, number> {
  const map = new Map<string, number>();
  try {
    for (const line of fs.readFileSync(path.join(DATASET_DIR, ".scan_numbers.tsv"), "utf8").split("\n")) {
      const [num, name] = line.trim().split("\t");
      if (num && name && /^\d+$/.test(num)) map.set(name, Number(num));
    }
  } catch {
    // no register on this machine: cards fall back to the folder name
  }
  return map;
}

interface RunInfo {
  runId: string;
  date: string;
}

/** tag -> run ID + date, from TRAINING.md headings such as "### R-039 · 2026-11-16 · ... (tag `r1116w9`)". */
function readRuns(): Map<string, RunInfo> {
  const map = new Map<string, RunInfo>();
  try {
    const text = fs.readFileSync(path.join(REPO_ROOT, "docs", "progress", "TRAINING.md"), "utf8");
    // Headings name the tag as "(tag `r1116w9`)" or just "(`r1112lev`)": an explicit "tag `x`" wins, otherwise
    // every back-ticked word of the heading counts (file names there never match a bundle's tag). First run wins.
    for (const m of text.matchAll(/^### (R-\d+) · (\d{4}-\d{2}-\d{2}) · (.*)$/gm)) {
      const info = { runId: m[1], date: m[2] };
      const explicit = /tag `([^`]+)`/.exec(m[3]);
      const tags = explicit ? [explicit[1]] : [...m[3].matchAll(/`([^`]+)`/g)].map((t) => t[1]);
      for (const t of tags) if (!map.has(t)) map.set(t, info);
    }
  } catch {
    // records not next to the web UI (e.g. a copied build): no run IDs on the cards
  }
  return map;
}

/** Splits "<capture>_<tag>" using the known capture names first, then the last underscore. */
function splitFolder(folder: string, numbers: Map<string, number>): BundleRef {
  let capture = "";
  for (const name of numbers.keys()) {
    if (folder.startsWith(`${name}_`) && name.length > capture.length) capture = name;
  }
  if (!capture) {
    const cut = folder.lastIndexOf("_");
    capture = cut > 0 ? folder.slice(0, cut) : folder;
  }
  const tag = folder.length > capture.length ? folder.slice(capture.length + 1) : "";
  return { folder, capture, tag, scanNumber: numbers.get(capture) ?? null };
}

export function listBundleRefs(): BundleRef[] {
  let entries: fs.Dirent[] = [];
  try {
    entries = fs.readdirSync(SCANS_DIR, { withFileTypes: true });
  } catch {
    return [];
  }
  const numbers = readScanNumbers();
  return entries
    .filter((e) => e.isDirectory() && SAFE_FOLDER.test(e.name))
    .filter((e) => fs.existsSync(path.join(SCANS_DIR, e.name, "scan.json")))
    .map((e) => splitFolder(e.name, numbers));
}

/** Layout plan image of a bundle's run (dataset/<capture>/work_<tag>_sfm/gs_<tag>/layout/plan.png), if on disk. */
export function planImagePath(ref: BundleRef): string | null {
  if (!ref.tag) return null;
  const p = path.join(DATASET_DIR, ref.capture, `work_${ref.tag}_sfm`, `gs_${ref.tag}`, "layout", "plan.png");
  return fs.existsSync(p) ? p : null;
}

const CLASS_PLURALS: Record<string, string> = {
  door: "doors",
  window: "windows",
  "light switch": "switches",
  "power socket": "sockets",
  "ceiling light": "ceiling lights",
  "tube light": "tube lights",
};

function fixtureSummary(scan: ScanInfo): string {
  const counts = new Map<string, number>();
  for (const f of scan.fixtures ?? []) counts.set(f.cls, (counts.get(f.cls) ?? 0) + 1);
  return [...counts.entries()]
    .sort((a, b) => b[1] - a[1])
    .map(([cls, n]) => `${n} ${n === 1 ? cls : CLASS_PLURALS[cls] ?? `${cls}s`}`)
    .join(", ");
}

function formatDate(d: Date): string {
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
}

/**
 * Camera start: 1.5 m above the floor at the middle of the detected fixtures, looking at the first door
 * (or fixture). Without fixtures: the coordinate origin, which is where ARCore tracking started (on the walk).
 */
function cameraStart(scan: ScanInfo): Project["splatStart"] {
  const fx = scan.fixtures ?? [];
  if (fx.length === 0) return undefined;
  const floorY = fx.reduce((s, f) => s + (f.position[1] - f.height_above_floor), 0) / fx.length;
  const cx = fx.reduce((s, f) => s + f.position[0], 0) / fx.length;
  const cz = fx.reduce((s, f) => s + f.position[2], 0) / fx.length;
  const look = fx.find((f) => f.cls === "door") ?? fx[0];
  const eye: [number, number, number] = [cx, floorY + 1.5, cz];
  let target: [number, number, number] = [look.position[0], floorY + 1.2, look.position[2]];
  if (Math.hypot(target[0] - eye[0], target[2] - eye[2]) < 0.3) target = [eye[0], eye[1], eye[2] - 1];
  return { position: eye, target };
}

function bundleToProject(ref: BundleRef, runs: Map<string, RunInfo>): Project | null {
  const file = path.join(SCANS_DIR, ref.folder, "scan.json");
  let scan: ScanInfo;
  try {
    scan = JSON.parse(fs.readFileSync(file, "utf8")) as ScanInfo;
  } catch {
    return null; // half-written or broken bundle: skip it rather than break the page
  }
  const run = runs.get(ref.tag);
  const processed = run ? new Date(`${run.date}T12:00:00`) : fs.statSync(file).mtime;
  const splats = (scan.groups ?? []).reduce((s, g) => s + (g.splats ?? 0), 0);
  const nFix = (scan.fixtures ?? []).length;
  const nWalls = (scan.walls ?? []).length;
  const area = scan.floor_area != null ? `≈ ${Math.round(scan.floor_area)} m²` : "area not measured";
  const title = ref.scanNumber != null ? `Scan #${ref.scanNumber}` : ref.capture;
  const runLabel = [run?.runId, ref.tag ? `tag ${ref.tag}` : ""].filter(Boolean).join(" · ");

  const facts = [
    `${nWalls} wall${nWalls === 1 ? "" : "s"}`,
    scan.open_top ? "no roof (open to the sky)" : null,
    scan.room_closed === false ? "not a closed room" : null,
    scan.floor_area != null ? `floor ${scan.floor_area.toFixed(1)} m²` : null,
    scan.ceiling_height != null ? `ceiling ${scan.ceiling_height.toFixed(2)} m` : null,
  ].filter(Boolean);

  return {
    id: `${BUNDLE_ID_PREFIX}${ref.folder}`,
    name: `${title} · ${ref.tag || "run"}`,
    floor: runLabel || "Processed run",
    block: ref.capture,
    area,
    location: [title, run?.runId ?? ref.tag, area].filter(Boolean).join(" • "),
    dateCaptured: formatDate(processed),
    status: "ready",
    statusLabel:
      `3DGS Ready · ${(splats / 1e6).toFixed(2)}M splats${nFix ? " · labelled" : ""}` +
      (scan.open_top ? " · no roof" : scan.room_closed === false ? " · open outline" : ""),
    thumbnail: planImagePath(ref)
      ? `/api/scans/${encodeURIComponent(ref.folder)}/plan`
      : "/images/logo-new.png", // no plan.png on this machine: the official logo, not a made-up image
    scansCount: 1,
    gaussianCount: splats.toLocaleString("en-US"),
    accuracy:
      scan.ceiling_height != null
        ? `Ceiling ${scan.ceiling_height.toFixed(2)} m auto-measured (no tape check)`
        : scan.open_top
          ? "No roof: wall height only (no tape check)"
          : "Not checked against tape",
    description:
      `Processed bundle public/scans/${ref.folder}/ (listed automatically). ` +
      `${facts.join(", ")}. ` +
      (nFix ? `Fixtures: ${fixtureSummary(scan)}.` : "No fixtures labelled.") +
      (scan.warnings?.length ? ` Layout warnings: ${scan.warnings.join("; ")}.` : ""),
    scanUrl: `/scans/${ref.folder}/`,
    splatStart: cameraStart(scan),
  };
}

/** Every bundle in public/scans/ as a Project, newest first. */
export function listBundleProjects(): Project[] {
  const runs = readRuns();
  return listBundleRefs()
    .map((ref) => bundleToProject(ref, runs))
    .filter((p): p is Project => p !== null)
    .sort((a, b) => Date.parse(b.dateCaptured) - Date.parse(a.dateCaptured) || b.id.localeCompare(a.id));
}
