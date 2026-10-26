"use client";

import React, {
  forwardRef,
  useEffect,
  useImperativeHandle,
  useRef,
  useState,
} from "react";
import * as THREE from "three";
import { MeasurementManager, MeasurementRecord } from "./MeasurementTool";
import type { Canvas3DHandle, InteractionMode, ViewMode } from "./Canvas3D";

/**
 * Real 3D Gaussian Splatting viewer for captured scans (Spark renderer, in-browser).
 *
 * Unlike the old Python viewer (server renders every frame and streams JPEGs), splats are uploaded to
 * the GPU once and sorted in a worker, so navigation runs at display frame rate. Exposes the same
 * Canvas3DHandle as the mock-scene Canvas3D, so the viewport toolbar and measurement panel work unchanged.
 * Navigation: drag to look / slide, scroll or W/A/S/D to move (Spark's SparkControls).
 * Measurement: click two points; the ray hits the splats (metric model, distances in metres).
 */
interface SplatCanvasProps {
  splatUrl: string;
  /** Camera start pose in model (metric) coordinates. */
  initialPosition: [number, number, number];
  initialTarget: [number, number, number];
  viewMode: ViewMode;
  interactionMode: InteractionMode;
  isMeasureMode: boolean;
  onMeasurementsChange: (measurements: MeasurementRecord[]) => void;
  onHoverCoordinate?: (coordinate: string | null) => void;
  onOrbitChange?: (theta: number, phi: number) => void;
}

type LoadState = { phase: "loading" | "ready" | "error"; message?: string };

export const SplatCanvas = forwardRef<Canvas3DHandle, SplatCanvasProps>(
  function SplatCanvas(
    {
      splatUrl,
      initialPosition,
      initialTarget,
      viewMode,
      isMeasureMode,
      onMeasurementsChange,
      onHoverCoordinate,
      onOrbitChange,
    },
    ref
  ) {
    const mountRef = useRef<HTMLDivElement>(null);
    const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
    const measurementRef = useRef<MeasurementManager | null>(null);
    const [load, setLoad] = useState<LoadState>({ phase: "loading" });

    // Props read by imperative handlers (synced after every render, never during it).
    const onMeasurementsChangeRef = useRef(onMeasurementsChange);
    const onHoverCoordinateRef = useRef(onHoverCoordinate);
    const onOrbitChangeRef = useRef(onOrbitChange);
    const initialRef = useRef({ initialPosition, initialTarget });
    useEffect(() => {
      onMeasurementsChangeRef.current = onMeasurementsChange;
      onHoverCoordinateRef.current = onHoverCoordinate;
      onOrbitChangeRef.current = onOrbitChange;
      initialRef.current = { initialPosition, initialTarget };
    });

    const placeCamera = (mode: ViewMode) => {
      const camera = cameraRef.current;
      if (!camera) return;
      const { initialPosition: p, initialTarget: t } = initialRef.current;
      if (mode === "top" || mode === "2d") {
        camera.position.set(p[0], p[1] + 3.5, p[2]);
        camera.up.set(0, 0, -1);
        camera.lookAt(p[0], p[1] - 1, p[2]);
        camera.up.set(0, 1, 0);
      } else {
        camera.position.set(p[0], p[1], p[2]);
        camera.lookAt(t[0], t[1], t[2]);
      }
    };

    const dolly = (metres: number) => {
      const camera = cameraRef.current;
      if (!camera) return;
      const dir = new THREE.Vector3();
      camera.getWorldDirection(dir);
      camera.position.addScaledVector(dir, metres);
    };

    useImperativeHandle(
      ref,
      () => ({
        zoomIn: () => dolly(0.5),
        zoomOut: () => dolly(-0.5),
        resetView: () => placeCamera("3d"),
        fitToScreen: () => placeCamera("3d"),
        deleteMeasurement: (id: string) => {
          const m = measurementRef.current;
          if (!m) return;
          m.deleteMeasurement(id);
          onMeasurementsChangeRef.current([...m.measurements]);
        },
        clearMeasurements: () => {
          const m = measurementRef.current;
          if (!m) return;
          m.clearAll();
          onMeasurementsChangeRef.current([...m.measurements]);
        },
      }),
      // Helpers only read refs, so the handle can stay stable.
      []
    );

    useEffect(() => {
      const container = mountRef.current;
      if (!container) return;
      let disposed = false;
      let frameId = 0;
      const cleanups: Array<() => void> = [];

      const scene = new THREE.Scene();
      scene.background = new THREE.Color(0xeef3f9);
      const camera = new THREE.PerspectiveCamera(60, container.clientWidth / container.clientHeight, 0.05, 200);
      cameraRef.current = camera;
      placeCamera("3d");

      // Spark recommends antialias off (splats are already smooth) and handles sorting itself.
      const renderer = new THREE.WebGLRenderer({ antialias: false });
      renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
      renderer.setSize(container.clientWidth, container.clientHeight);
      container.innerHTML = "";
      container.appendChild(renderer.domElement);
      cleanups.push(() => renderer.dispose());

      const measurement = new MeasurementManager(scene, camera, container);
      measurementRef.current = measurement;
      onMeasurementsChangeRef.current([...measurement.measurements]);

      (async () => {
        try {
          const { SparkRenderer, SplatMesh, SparkControls } = await import("@sparkjsdev/spark");
          if (disposed) return;
          const spark = new SparkRenderer({ renderer });
          scene.add(spark);
          const splat = new SplatMesh({ url: splatUrl, raycastable: true });
          scene.add(splat);
          const controls = new SparkControls({ canvas: renderer.domElement });

          const raycaster = new THREE.Raycaster();
          const ndc = new THREE.Vector2();
          const toNdc = (e: MouseEvent) => {
            const r = container.getBoundingClientRect();
            ndc.set(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1);
          };
          const hitPoint = (): THREE.Vector3 | null => {
            raycaster.setFromCamera(ndc, camera);
            const hits = raycaster.intersectObject(splat, false);
            return hits.length > 0 ? hits[0].point : null;
          };

          // Click (not drag) while measuring -> measurement point on the splat surface.
          let down = { x: 0, y: 0 };
          const onDown = (e: MouseEvent) => (down = { x: e.clientX, y: e.clientY });
          const onUp = (e: MouseEvent) => {
            if (!measurement.isMeasureModeActive || e.button !== 0) return;
            if (Math.abs(e.clientX - down.x) + Math.abs(e.clientY - down.y) > 5) return;
            toNdc(e);
            const p = hitPoint();
            if (p) {
              measurement.handlePointClick(p);
              onMeasurementsChangeRef.current([...measurement.measurements]);
            }
          };
          // Hover XYZ readout, throttled: a splat raycast is heavier than a mesh raycast.
          let lastHover = 0;
          const onMove = (e: MouseEvent) => {
            const now = performance.now();
            if (now - lastHover < 120) return;
            lastHover = now;
            toNdc(e);
            const p = hitPoint();
            onHoverCoordinateRef.current?.(
              p ? `X: ${p.x >= 0 ? "+" : ""}${p.x.toFixed(2)}m  Y: ${p.y.toFixed(2)}m  Z: ${p.z >= 0 ? "+" : ""}${p.z.toFixed(2)}m` : null
            );
          };
          const onLeave = () => onHoverCoordinateRef.current?.(null);
          container.addEventListener("mousedown", onDown);
          container.addEventListener("mouseup", onUp);
          container.addEventListener("mousemove", onMove);
          container.addEventListener("mouseleave", onLeave);
          cleanups.push(() => {
            container.removeEventListener("mousedown", onDown);
            container.removeEventListener("mouseup", onUp);
            container.removeEventListener("mousemove", onMove);
            container.removeEventListener("mouseleave", onLeave);
            scene.remove(splat);
            splat.dispose();
          });

          splat.initialized
            .then(() => !disposed && setLoad({ phase: "ready" }))
            .catch((err: unknown) => !disposed && setLoad({ phase: "error", message: String(err) }));

          const dir = new THREE.Vector3();
          const animate = () => {
            frameId = requestAnimationFrame(animate);
            controls.update(camera);
            camera.getWorldDirection(dir);
            onOrbitChangeRef.current?.(Math.atan2(dir.x, dir.z), Math.acos(THREE.MathUtils.clamp(-dir.y, -1, 1)));
            renderer.render(scene, camera);
          };
          animate();
        } catch (err) {
          if (!disposed) setLoad({ phase: "error", message: String(err) });
        }
      })();

      const resize = new ResizeObserver(() => {
        const w = container.clientWidth, h = container.clientHeight;
        if (w === 0 || h === 0) return;
        camera.aspect = w / h;
        camera.updateProjectionMatrix();
        renderer.setSize(w, h);
      });
      resize.observe(container);

      return () => {
        disposed = true;
        cancelAnimationFrame(frameId);
        resize.disconnect();
        cleanups.forEach((fn) => fn());
      };
      // Mount once per splat; camera placement helpers only read refs.
    }, [splatUrl]);

    useEffect(() => {
      if (measurementRef.current) measurementRef.current.isMeasureModeActive = isMeasureMode;
    }, [isMeasureMode]);

    useEffect(() => {
      placeCamera(viewMode);
    }, [viewMode]);

    return (
      <div className="relative w-full h-full select-none overflow-hidden bg-[#eef3f9]">
        <div ref={mountRef} className={`w-full h-full ${isMeasureMode ? "cursor-crosshair" : "cursor-grab active:cursor-grabbing"}`} />
        {load.phase !== "ready" && (
          <div className="absolute inset-0 z-10 flex items-center justify-center pointer-events-none">
            <div className="px-4 py-2 rounded-full bg-white border border-[#e2e8f0] shadow text-[12px] font-semibold text-[#0f172a]">
              {load.phase === "loading" ? "Loading Gaussian splat scan…" : `Could not load the scan: ${load.message}`}
            </div>
          </div>
        )}
        {isMeasureMode && (
          <div className="absolute top-4 left-1/2 -translate-x-1/2 z-20 px-4 py-2 rounded-full bg-[#2563eb] text-white shadow-lg text-[11px] font-bold pointer-events-none">
            Click two points on the scan to measure metric distance
          </div>
        )}
        <div className="absolute bottom-3 left-1/2 -translate-x-1/2 z-10 px-3 py-1 rounded-full bg-white/80 border border-[#e2e8f0] text-[10px] text-[#64748b] pointer-events-none">
          Drag to look · Scroll or W/A/S/D to move · E/Q up/down
        </div>
      </div>
    );
  }
);
