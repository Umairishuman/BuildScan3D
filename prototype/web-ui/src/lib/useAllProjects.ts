"use client";

import { useEffect, useState } from "react";
import { MOCK_PROJECTS, Project } from "./mockData";

/**
 * Hand-written projects (mockData.ts) plus every processed scan bundle in public/scans/ and every published one
 * in the R2 bucket (D-076), listed by the /api/scans route (src/lib/scanBundles.ts, src/lib/remoteBundles.ts). A bundle that a hand-written project already shows (same
 * scanUrl, e.g. newroom-scan, scan-008) is not listed twice. `loading` is true until the list has arrived;
 * if the route fails, only the hand-written projects are returned and `error` says why.
 */
export function useAllProjects(): { projects: Project[]; loading: boolean; error: string | null } {
  const [bundles, setBundles] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetch("/api/scans")
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(`HTTP ${r.status}`))))
      .then((list: Project[]) => {
        if (!cancelled) setBundles(list);
      })
      .catch((e: unknown) => {
        if (!cancelled) setError(e instanceof Error ? e.message : String(e));
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  // A hand-written project whose bundle is not on this server (e.g. scan-008 on Vercel) opens the published copy
  // of the same folder instead, if there is one (D-076); a bundle on this server always wins.
  const localUrls = new Set(bundles.map((b) => b.scanUrl).filter((u) => u?.startsWith("/")));
  const replaced = new Set<string>();
  const mocks = MOCK_PROJECTS.map((p) => {
    const m = p.scanUrl ? /^\/scans\/([^/]+)\/$/.exec(p.scanUrl) : null;
    if (!m || localUrls.has(p.scanUrl!)) return p;
    const copy = bundles.find((b) => b.scanUrl && /^https?:/.test(b.scanUrl) && b.scanUrl.endsWith(`/${m[1]}/`));
    if (!copy) return p;
    replaced.add(copy.id);
    return { ...p, scanUrl: copy.scanUrl };
  });
  const shown = new Set(mocks.map((p) => p.scanUrl).filter(Boolean));
  const extra = bundles.filter((b) => !shown.has(b.scanUrl) && !replaced.has(b.id));
  // Real scans first (hand-written real ones keep their place at the top), then the mock portfolio.
  const realMock = mocks.filter((p) => p.scanUrl || p.splatUrl);
  const otherMock = mocks.filter((p) => !(p.scanUrl || p.splatUrl));
  return { projects: [...realMock, ...extra, ...otherMock], loading, error };
}
