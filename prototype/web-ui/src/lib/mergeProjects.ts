import type { Project } from "./mockData";

/**
 * Hand-written projects + listed bundles, without duplicates (used by useAllProjects). A hand-written project
 * whose bundle is not on this server (e.g. scan-008 on Vercel) opens the published copy of the same folder
 * instead, if there is one (D-076); a bundle on this server always wins. Real scans first (hand-written real ones
 * keep their place at the top), then the listed bundles, then the mock portfolio. With `hideUnavailable` (the list
 * has arrived), a hand-written scan whose folder is neither listed on this server nor published is left out, so the
 * deployed site shows only published scans (Umair, 2026-11-19); mock projects without a bundle always stay.
 */
export function mergeProjects(handWritten: Project[], bundles: Project[], hideUnavailable = false): Project[] {
  const localUrls = new Set(bundles.map((b) => b.scanUrl).filter((u): u is string => !!u && u.startsWith("/")));
  const replaced = new Set<string>();
  const mocks = handWritten.map((p) => {
    const m = p.scanUrl ? /^\/scans\/([^/]+)\/$/.exec(p.scanUrl) : null;
    if (!m || localUrls.has(p.scanUrl!)) return p;
    const copy = bundles.find((b) => !!b.scanUrl && /^https?:/.test(b.scanUrl) && b.scanUrl.endsWith(`/${m[1]}/`));
    if (!copy) return hideUnavailable ? null : p;
    replaced.add(copy.id);
    return { ...p, scanUrl: copy.scanUrl };
  }).filter((p): p is Project => p !== null);
  const shown = new Set(mocks.map((p) => p.scanUrl).filter(Boolean));
  const extra = bundles.filter((b) => !shown.has(b.scanUrl) && !replaced.has(b.id));
  const realMock = mocks.filter((p) => p.scanUrl || p.splatUrl);
  const otherMock = mocks.filter((p) => !(p.scanUrl || p.splatUrl));
  return [...realMock, ...extra, ...otherMock];
}
