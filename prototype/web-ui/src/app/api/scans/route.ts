import { NextResponse } from "next/server";
import { listBundleProjects, sortProjects } from "@/lib/scanBundles";
import { listPublishedProjects } from "@/lib/remoteBundles";

// Route handlers are not cached by default: public/scans/ (and the published indexes, D-076) are read on every
// request, so a bundle that a run just wrote or someone just published shows up without a rebuild.
export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  const local = listBundleProjects(); // this machine's public/scans/ (on Vercel only the git-tracked newroom/)
  const published = await listPublishedProjects(); // R2 bucket, only when SCANS_BASE_URL is set
  return NextResponse.json(sortProjects([...local, ...published]));
}
