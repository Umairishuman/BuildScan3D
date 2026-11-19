import { NextResponse } from "next/server";
import { listBundleProjects } from "@/lib/scanBundles";

// Route handlers are not cached by default: public/scans/ is read on every request, so a bundle that a run
// just wrote shows up without a rebuild.
export const runtime = "nodejs";

export function GET() {
  return NextResponse.json(listBundleProjects());
}
