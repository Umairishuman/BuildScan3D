/**
 * Labelled scan bundle written by the processing pipeline (src/arcore3dgs/export_web.py):
 * <scanUrl>/scan.json + one .spz per semantic group + mesh.glb. Coordinates are metric (metres, +Y up).
 */
export interface ScanGroup {
  /** floor | ceiling | walls | openings | electrical | other */
  key: string;
  /** File name of the group's splats, relative to the scan folder. */
  url: string;
  splats: number;
  /** Class colour used when the viewer tints splats by class. */
  color: string;
  classes: string[];
}

export interface ScanWall {
  id: number;
  length: number;
  height: number;
  gross_area: number;
  openings_area: number;
  net_area: number;
  openings: string[];
  fixtures: string[];
}

export interface ScanFixture {
  id: string;
  /** Detected class, e.g. "door", "light switch", "power socket", "ceiling light". */
  cls: string;
  position: [number, number, number];
  /** Height of the fixture's centre above the floor (m). */
  height_above_floor: number;
  /** Heights of its lowest / highest point above the floor (m); in bundles exported since 2026-11-12. */
  bottom?: number;
  top?: number;
  wall: number | null;
  along_wall: number | null;
  width: number;
  height: number;
  /** Number of video frames the detection was confirmed in (0 for openings found from wall gaps). */
  views: number;
  /** "wall gap (layout)" for doorways / window openings found from gaps in the wall (#9). */
  source?: string;
}

export interface ScanInfo {
  floor_area: number | null;
  ceiling_height: number | null;
  walls: ScanWall[];
  fixtures: ScanFixture[];
  groups: ScanGroup[];
  /** File name of the surface mesh (.glb), or null. */
  mesh: string | null;
  /** No roof: open to the sky (bundles since 2026-11-19, #8). */
  open_top?: boolean;
  /** The layout found a closed outline (a corner between every pair of neighbouring walls); null / absent = unknown. */
  room_closed?: boolean | null;
  /** Layout warnings in plain words (e.g. "only 1 wall(s) found: not a closed room ..."). */
  warnings?: string[];
}

/** Marker / list colour per fixture class. */
export const FIXTURE_COLORS: Record<string, string> = {
  door: "#285aff",
  window: "#00c8ff",
  "light switch": "#ff00c8",
  "power socket": "#ff7800",
  "ceiling light": "#f5c400",
  "tube light": "#f5c400",
  lamp: "#ffb84d",
  "air conditioner": "#00dc78",
  "ceiling fan": "#a050ff",
  // openings without a leaf / frame, found from gaps in the wall (layout.py, #9)
  doorway: "#285aff",
  "window opening": "#00c8ff",
};
