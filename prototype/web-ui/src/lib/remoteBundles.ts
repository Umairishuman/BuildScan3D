/**
 * Server-side only: lists the scan bundles published to the R2 bucket (D-076, issue #28), so the deployed site
 * shows scans that live on no web server's disk.
 *
 * Bucket layout, written by scripts/publish_scan.py:
 *   <SCANS_BASE_URL>owners.json                         {"version": 1, "owners": [{"id": "umair", "name": "Umair"}]}
 *   <SCANS_BASE_URL>scans/<owner>/index.json            {"version": 1, "owner": "umair", "bundles": [PublishedBundle]}
 *   <SCANS_BASE_URL>scans/<owner>/<capture>_<tag>/      scan.json, *.spz, mesh.glb, plan.png
 * One index per person, because scan numbers and run IDs are per machine (OD-12) and two people publishing at the
 * same time must not overwrite each other's list. Unset SCANS_BASE_URL = nothing published is listed (this PC).
 */
import type { Project } from "./mockData";
import type { ScanInfo } from "@/components/Viewer3D/scanTypes";
import { BUNDLE_ID_PREFIX, bundleToProject } from "./scanBundles";

/** One published bundle as publish_scan.py writes it into scans/<owner>/index.json. */
export interface PublishedBundle {
  folder: string;
  capture: string;
  tag: string;
  scan_number: number | null;
  run_id: string | null;
  /** YYYY-MM-DD of the run (TRAINING.md), else the day it was published. */
  date: string;
  room: string | null;
  /** File name of the plan thumbnail inside the folder, or null. */
  plan: string | null;
  /** The bundle's scan.json (2–3 KB), so listing needs one request per person, not one per scan. */
  scan: ScanInfo;
}

interface OwnerEntry {
  id: string;
  name: string;
}

const SAFE_OWNER = /^[a-z0-9][a-z0-9-]{0,31}$/;
const SAFE_FOLDER = /^[A-Za-z0-9][A-Za-z0-9_.-]*$/;
const SAFE_FILE = /^[A-Za-z0-9][A-Za-z0-9_.-]*$/;
const DATE = /^\d{4}-\d{2}-\d{2}$/;

/** The bucket's public base URL with a trailing "/", or null when this deployment lists nothing remote. */
export function scansBaseUrl(): string | null {
  const raw = process.env.SCANS_BASE_URL?.trim();
  if (!raw) return null;
  try {
    const u = new URL(raw);
    if (u.protocol !== "https:" && u.protocol !== "http:") return null;
    return u.href.endsWith("/") ? u.href : `${u.href}/`;
  } catch {
    return null;
  }
}

async function getJson<T>(url: string, tries = 2): Promise<T> {
  // no-store: a scan published a minute ago shows up without a redeploy
  try {
    const r = await fetch(url, { cache: "no-store", signal: AbortSignal.timeout(8000) });
    if (!r.ok) throw new Error(`HTTP ${r.status} for ${url}`);
    return (await r.json()) as T;
  } catch (e) {
    // one retry: the r2.dev URL is rate-limited and a single request can fail (seen 2026-11-19: "fetch failed")
    if (tries > 1) return getJson<T>(url, tries - 1);
    throw e;
  }
}

/** Project id of a published bundle; includes the owner so two people's folders can never clash. */
export function publishedId(owner: string, folder: string): string {
  return `${BUNDLE_ID_PREFIX}${owner}-${folder}`;
}

function toProject(base: string, owner: OwnerEntry, b: PublishedBundle): Project | null {
  if (!b || !SAFE_FOLDER.test(b.folder ?? "") || !b.scan || typeof b.scan !== "object") return null;
  const folderUrl = `${base}scans/${owner.id}/${b.folder}/`;
  const plan = b.plan && SAFE_FILE.test(b.plan) ? `${folderUrl}${b.plan}` : null;
  return bundleToProject(
    { folder: b.folder, capture: b.capture || b.folder, tag: b.tag || "", scanNumber: b.scan_number ?? null },
    b.scan,
    {
      id: publishedId(owner.id, b.folder),
      scanUrl: folderUrl,
      thumbnail: plan,
      processed: new Date(`${DATE.test(b.date) ? b.date : "1970-01-01"}T12:00:00`),
      runId: b.run_id ?? undefined,
      ownerName: owner.name,
      roomName: b.room ?? undefined,
      origin: `Published by ${owner.name} (scans/${owner.id}/${b.folder}/).`,
    },
  );
}

/** Every published bundle of every owner as a Project. A broken or missing index skips that owner only. */
export async function listPublishedProjects(): Promise<Project[]> {
  const base = scansBaseUrl();
  if (!base) return [];
  let owners: OwnerEntry[] = [];
  try {
    const doc = await getJson<{ owners?: OwnerEntry[] }>(`${base}owners.json`);
    owners = (doc.owners ?? []).filter((o) => o && SAFE_OWNER.test(o.id ?? ""));
  } catch (e) {
    console.warn(`[scans] no owners.json: ${e instanceof Error ? e.message : e}`);
    return [];
  }
  const lists = await Promise.all(
    owners.map(async (o) => {
      const owner = { id: o.id, name: (o.name || o.id).slice(0, 40) };
      try {
        const idx = await getJson<{ bundles?: PublishedBundle[] }>(`${base}scans/${owner.id}/index.json`);
        return (idx.bundles ?? []).map((b) => toProject(base, owner, b)).filter((p): p is Project => p !== null);
      } catch (e) {
        console.warn(`[scans] index of ${owner.id} skipped: ${e instanceof Error ? e.message : e}`);
        return [];
      }
    }),
  );
  return lists.flat();
}
