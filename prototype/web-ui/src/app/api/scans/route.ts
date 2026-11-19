import { NextResponse } from "next/server";
import { listBundleProjects, sortProjects } from "@/lib/scanBundles";
import { listPublishedProjects } from "@/lib/remoteBundles";

// Route handlers are not cached by default: public/scans/ (and the published indexes, D-076) are read on every
// request, so a bundle that a run just wrote or someone just published shows up without a rebuild.
export const runtime = "nodejs";
export const dynamic = "force-dynamic";

/**
 * Local bundles (public/scans/) are listed on a PC that runs the pipeline, not on the deployed site: there only
 * published scans show (Umair, 2026-11-19). Vercel sets VERCEL=1 itself; SCANS_LOCAL=1 / 0 overrides it.
 */
function listLocal(): boolean {
  const o = process.env.SCANS_LOCAL?.trim();
  if (o === "0" || o === "1") return o === "1";
  return !process.env.VERCEL;
}

const folderOf = (url?: string) => /\/([^/]+)\/$/.exec(url ?? "")?.[1];

export async function GET() {
  const local = listLocal() ? listBundleProjects() : [];
  const published = await listPublishedProjects(); // R2 bucket, only when SCANS_BASE_URL is set
  // A local bundle that is also published shows once (the local copy, marked online); folder names hold the
  // recording's id, so the same folder is the same run.
  const online = new Set(published.map((p) => folderOf(p.scanUrl)));
  const localFolders = new Set(local.map((p) => folderOf(p.scanUrl)));
  const marked = local.map((p) => (online.has(folderOf(p.scanUrl)) ? { ...p, statusLabel: `${p.statusLabel} · online` } : p));
  const remoteOnly = published.filter((p) => !localFolders.has(folderOf(p.scanUrl)));
  return NextResponse.json(sortProjects([...marked, ...remoteOnly]));
}
