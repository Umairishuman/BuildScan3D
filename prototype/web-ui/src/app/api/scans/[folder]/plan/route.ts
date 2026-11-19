import fs from "node:fs";
import { NextResponse } from "next/server";
import { listBundleRefs, planImagePath } from "@/lib/scanBundles";

export const runtime = "nodejs";

/** The layout plan (plan.png) of a listed bundle's run, used as its card thumbnail. */
export async function GET(_req: Request, { params }: { params: Promise<{ folder: string }> }) {
  const { folder } = await params;
  // Only folders that are listed bundles: the name is never used to build a path directly.
  const ref = listBundleRefs().find((r) => r.folder === folder);
  const file = ref ? planImagePath(ref) : null;
  if (!file) return new NextResponse("No plan image", { status: 404 });
  return new NextResponse(new Uint8Array(fs.readFileSync(file)), {
    headers: { "Content-Type": "image/png", "Cache-Control": "no-cache" },
  });
}
