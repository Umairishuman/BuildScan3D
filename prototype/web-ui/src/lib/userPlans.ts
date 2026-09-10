/**
 * User-created floor plans (browser-only, POC scope).
 *
 * The Create Project modal writes plans here, the Floor Plan route reads them
 * back merged with `MOCK_BUILDING_PLANS`. Everything lives under a single
 * localStorage key as JSON — no backend, no server dependency, but also no
 * cross-browser or cross-device sync. The 5 MB `planImageDataUrl` limit
 * enforced by the modal keeps this well under the ~10 MB origin quota.
 *
 * Every helper is guarded for SSR (`typeof window === "undefined"`) so nothing
 * blows up when Next renders the initial HTML on the server. The merged
 * lookups will only see mock plans during SSR; the client re-renders after
 * hydration and picks up the user plans naturally.
 */

import { BuildingPlan, MOCK_BUILDING_PLANS } from "@/lib/mockData";

const STORAGE_KEY = "buildscan.userPlans.v1";

/** Version tag so we can invalidate old shapes on schema changes. */
interface StoredEnvelope {
  version: 1;
  plans: BuildingPlan[];
}

const isBrowser = () => typeof window !== "undefined";

const safeParse = (raw: string | null): BuildingPlan[] => {
  if (!raw) return [];
  try {
    const parsed = JSON.parse(raw) as StoredEnvelope;
    if (!parsed || parsed.version !== 1 || !Array.isArray(parsed.plans)) return [];
    return parsed.plans;
  } catch {
    return [];
  }
};

export const loadUserPlans = (): BuildingPlan[] => {
  if (!isBrowser()) return [];
  try {
    return safeParse(window.localStorage.getItem(STORAGE_KEY));
  } catch {
    return [];
  }
};

const writePlans = (plans: BuildingPlan[]): boolean => {
  if (!isBrowser()) return false;
  const envelope: StoredEnvelope = { version: 1, plans };
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(envelope));
    return true;
  } catch {
    // Most commonly a QuotaExceededError; caller should surface an error.
    return false;
  }
};

/** Insert or replace a plan (matched by `projectId`). Returns success flag. */
export const saveUserPlan = (plan: BuildingPlan): boolean => {
  const stamped: BuildingPlan = {
    ...plan,
    isUserCreated: true,
    createdAt: plan.createdAt ?? new Date().toISOString(),
  };
  const existing = loadUserPlans();
  const idx = existing.findIndex((p) => p.projectId === stamped.projectId);
  const next =
    idx === -1
      ? [...existing, stamped]
      : existing.map((p, i) => (i === idx ? stamped : p));
  return writePlans(next);
};

export const deleteUserPlan = (projectId: string): boolean => {
  const next = loadUserPlans().filter((p) => p.projectId !== projectId);
  return writePlans(next);
};

/**
 * Every building plan visible to the app — mock plans first (so Tower A stays
 * in a stable position), then any user-created plans appended.
 */
export const getAllBuildingPlans = (): BuildingPlan[] => [
  ...MOCK_BUILDING_PLANS,
  ...loadUserPlans(),
];

export const findAnyBuildingPlan = (projectId: string): BuildingPlan | undefined =>
  getAllBuildingPlans().find((plan) => plan.projectId === projectId);

export const hasAnyBuildingPlan = (projectId: string): boolean =>
  getAllBuildingPlans().some((plan) => plan.projectId === projectId);

/**
 * ID generator for new user plans. Prefixed so we can spot them in the URL
 * (`/floorplan/user-…`) and route decisions can distinguish quickly.
 */
export const newUserPlanId = (): string => {
  const ts = Date.now().toString(36);
  const rand = Math.random().toString(36).slice(2, 8);
  return `user-${ts}-${rand}`;
};
