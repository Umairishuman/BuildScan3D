"use client";

import { useEffect, useState } from "react";
import { MOCK_PROJECTS, Project } from "./mockData";
import { mergeProjects } from "./mergeProjects";

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

  return { projects: mergeProjects(MOCK_PROJECTS, bundles), loading, error };
}
