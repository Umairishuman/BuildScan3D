"use client";

import React, {
  forwardRef,
  useEffect,
  useImperativeHandle,
  useRef,
} from "react";
import * as THREE from "three";
import { SceneBuilder, SemanticLayersState, RenderMode } from "./SceneBuilder";
import { MeasurementManager, MeasurementRecord } from "./MeasurementTool";

export type ViewMode = "3d" | "2d" | "top" | "side" | "front";
export type InteractionMode = "orbit" | "pan";

/** Imperative controls driven by the floating viewport toolbar. */
export interface Canvas3DHandle {
  zoomIn: () => void;
  zoomOut: () => void;
  resetView: () => void;
  fitToScreen: () => void;
  deleteMeasurement: (id: string) => void;
  clearMeasurements: () => void;
}

interface Canvas3DProps {
  semanticLayers: SemanticLayersState;
  renderMode: RenderMode;
  viewMode: ViewMode;
  interactionMode: InteractionMode;
  isMeasureMode: boolean;
  onMeasurementsChange: (measurements: MeasurementRecord[]) => void;
  /** Live XYZ readout under the cursor, surfaced so the shell can place it. */
  onHoverCoordinate?: (coordinate: string | null) => void;
  /** Camera azimuth/elevation in radians, for the axis gizmo. */
  onOrbitChange?: (theta: number, phi: number) => void;
}

interface SphericalState {
  radius: number;
  theta: number;
  phi: number;
}

/** Camera framing per view mode. `2d` is orthographic and handled separately. */
const VIEW_PRESETS: Record<
  Exclude<ViewMode, "2d">,
  { spherical: SphericalState; target: THREE.Vector3 }
> = {
  "3d": {
    spherical: { radius: 9, theta: Math.PI / 4, phi: Math.PI / 3 },
    target: new THREE.Vector3(0, 2, 0),
  },
  top: {
    spherical: { radius: 10, theta: 0, phi: 0.05 },
    target: new THREE.Vector3(0, 1, 0),
  },
  front: {
    spherical: { radius: 9, theta: 0, phi: Math.PI / 2 },
    target: new THREE.Vector3(0, 2, -1),
  },
  side: {
    spherical: { radius: 9, theta: Math.PI / 2, phi: Math.PI / 2 },
    target: new THREE.Vector3(0, 2, -1),
  },
};

const ORTHO_DEFAULT_HALF_HEIGHT = 7;
const MIN_RADIUS = 1.5;
const MAX_RADIUS = 25;
const MIN_HALF_HEIGHT = 1.5;
const MAX_HALF_HEIGHT = 18;

const clamp = (value: number, min: number, max: number) =>
  Math.max(min, Math.min(max, value));

export const Canvas3D = forwardRef<Canvas3DHandle, Canvas3DProps>(
  function Canvas3D(
    {
      semanticLayers,
      renderMode,
      viewMode,
      interactionMode,
      isMeasureMode,
      onMeasurementsChange,
      onHoverCoordinate,
      onOrbitChange,
    },
    ref
  ) {
    const mountRef = useRef<HTMLDivElement>(null);
    const sceneBuilderRef = useRef<SceneBuilder | null>(null);
    const measurementManagerRef = useRef<MeasurementManager | null>(null);
    const perspectiveCameraRef = useRef<THREE.PerspectiveCamera | null>(null);
    const orthographicCameraRef = useRef<THREE.OrthographicCamera | null>(null);
    const rendererRef = useRef<THREE.WebGLRenderer | null>(null);

    // Props the imperative event handlers read. Kept in refs so the mount
    // effect can stay a genuine run-once and never tear down the WebGL context.
    const viewModeRef = useRef(viewMode);
    const interactionModeRef = useRef(interactionMode);
    const onMeasurementsChangeRef = useRef(onMeasurementsChange);
    const onHoverCoordinateRef = useRef(onHoverCoordinate);
    const onOrbitChangeRef = useRef(onOrbitChange);

    // Each ref is seeded with its initial value by useRef above, so the mount
    // effect below always reads something valid; this keeps them current after
    // later renders. Writing refs during render is not allowed in React 19.
    useEffect(() => {
      viewModeRef.current = viewMode;
      interactionModeRef.current = interactionMode;
      onMeasurementsChangeRef.current = onMeasurementsChange;
      onHoverCoordinateRef.current = onHoverCoordinate;
      onOrbitChangeRef.current = onOrbitChange;
    });

    // Orbit / pan state
    const isDraggingRef = useRef(false);
    const isRightClickRef = useRef(false);
    const previousMousePositionRef = useRef({ x: 0, y: 0 });
    const dragStartRef = useRef({ x: 0, y: 0 });
    const cameraTargetRef = useRef(new THREE.Vector3(0, 2, 0));
    const sphericalRef = useRef<SphericalState>({ ...VIEW_PRESETS["3d"].spherical });

    // Orthographic (2D plan) state — half-height in world metres plus XZ centre.
    const orthoRef = useRef({ halfHeight: ORTHO_DEFAULT_HALF_HEIGHT, x: 0, z: 0 });

    const isOrtho = () => viewModeRef.current === "2d";

    const activeCamera = (): THREE.Camera | null =>
      isOrtho() ? orthographicCameraRef.current : perspectiveCameraRef.current;

    const updatePerspectiveCamera = () => {
      const camera = perspectiveCameraRef.current;
      if (!camera) return;

      const { radius, theta, phi } = sphericalRef.current;
      const target = cameraTargetRef.current;

      camera.position.set(
        target.x + radius * Math.sin(phi) * Math.sin(theta),
        target.y + radius * Math.cos(phi),
        target.z + radius * Math.sin(phi) * Math.cos(theta)
      );
      camera.lookAt(target);
      onOrbitChangeRef.current?.(theta, phi);
    };

    const updateOrthographicCamera = () => {
      const camera = orthographicCameraRef.current;
      const container = mountRef.current;
      if (!camera || !container) return;

      const width = container.clientWidth || 1;
      const height = container.clientHeight || 1;
      const aspect = width / height;
      const { halfHeight, x, z } = orthoRef.current;

      camera.left = -halfHeight * aspect;
      camera.right = halfHeight * aspect;
      camera.top = halfHeight;
      camera.bottom = -halfHeight;
      camera.near = 0.1;
      camera.far = 200;
      camera.updateProjectionMatrix();

      // Straight down, with -Z toward the top of the screen so the plan reads
      // like an architectural drawing rather than a mirrored one.
      camera.position.set(x, 40, z);
      camera.up.set(0, 0, -1);
      camera.lookAt(x, 0, z);

      // A plan view has no azimuth; report a fixed heading for the gizmo.
      onOrbitChangeRef.current?.(0, 0);
    };

    const updateActiveCamera = () => {
      if (isOrtho()) updateOrthographicCamera();
      else updatePerspectiveCamera();
    };

    const applyViewPreset = (mode: ViewMode) => {
      if (mode === "2d") {
        orthoRef.current = { halfHeight: ORTHO_DEFAULT_HALF_HEIGHT, x: 0, z: 0 };
        updateOrthographicCamera();
        return;
      }
      const preset = VIEW_PRESETS[mode];
      sphericalRef.current = { ...preset.spherical };
      cameraTargetRef.current.copy(preset.target);
      updatePerspectiveCamera();
    };

    useImperativeHandle(
      ref,
      () => ({
        zoomIn: () => {
          if (isOrtho()) {
            orthoRef.current.halfHeight = clamp(
              orthoRef.current.halfHeight * 0.82,
              MIN_HALF_HEIGHT,
              MAX_HALF_HEIGHT
            );
          } else {
            sphericalRef.current.radius = clamp(
              sphericalRef.current.radius * 0.82,
              MIN_RADIUS,
              MAX_RADIUS
            );
          }
          updateActiveCamera();
        },
        zoomOut: () => {
          if (isOrtho()) {
            orthoRef.current.halfHeight = clamp(
              orthoRef.current.halfHeight / 0.82,
              MIN_HALF_HEIGHT,
              MAX_HALF_HEIGHT
            );
          } else {
            sphericalRef.current.radius = clamp(
              sphericalRef.current.radius / 0.82,
              MIN_RADIUS,
              MAX_RADIUS
            );
          }
          updateActiveCamera();
        },
        resetView: () => applyViewPreset(viewModeRef.current),
        deleteMeasurement: (id: string) => {
          const manager = measurementManagerRef.current;
          if (!manager) return;
          manager.deleteMeasurement(id);
          onMeasurementsChangeRef.current([...manager.measurements]);
        },
        clearMeasurements: () => {
          const manager = measurementManagerRef.current;
          if (!manager) return;
          manager.clearAll();
          onMeasurementsChangeRef.current([]);
        },
        fitToScreen: () => {
          const sceneBuilder = sceneBuilderRef.current;
          if (!sceneBuilder) return;

          // Frame whatever is currently visible, so hiding layers tightens the fit.
          const box = new THREE.Box3().setFromObject(sceneBuilder.scene);
          if (box.isEmpty()) return;

          const sphere = box.getBoundingSphere(new THREE.Sphere());
          const center = sphere.center;

          if (isOrtho()) {
            orthoRef.current.x = center.x;
            orthoRef.current.z = center.z;
            orthoRef.current.halfHeight = clamp(
              sphere.radius * 1.1,
              MIN_HALF_HEIGHT,
              MAX_HALF_HEIGHT
            );
            updateOrthographicCamera();
            return;
          }

          const camera = perspectiveCameraRef.current;
          if (!camera) return;
          const fitDistance =
            sphere.radius / Math.sin((camera.fov * Math.PI) / 180 / 2);
          cameraTargetRef.current.copy(center);
          sphericalRef.current.radius = clamp(
            fitDistance * 1.05,
            MIN_RADIUS,
            MAX_RADIUS
          );
          updatePerspectiveCamera();
        },
      }),
      // The helpers this closes over only ever read refs, so they behave
      // identically across renders and the handle can stay stable.
      // eslint-disable-next-line react-hooks/exhaustive-deps
      []
    );

    useEffect(() => {
      if (!mountRef.current) return;

      const container = mountRef.current;
      const width = container.clientWidth;
      const height = container.clientHeight;

      // 1. Scene
      const sceneBuilder = new SceneBuilder();
      sceneBuilderRef.current = sceneBuilder;

      // 2. Cameras — both live for the whole session; view mode picks one.
      const perspectiveCamera = new THREE.PerspectiveCamera(
        55,
        width / height,
        0.1,
        200
      );
      perspectiveCameraRef.current = perspectiveCamera;

      const orthographicCamera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0.1, 200);
      orthographicCameraRef.current = orthographicCamera;

      updatePerspectiveCamera();
      updateOrthographicCamera();

      // 3. Renderer
      const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
      renderer.setSize(width, height);
      renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
      renderer.shadowMap.enabled = true;
      renderer.shadowMap.type = THREE.PCFSoftShadowMap;
      renderer.toneMapping = THREE.ACESFilmicToneMapping;
      renderer.toneMappingExposure = 1.05;
      container.innerHTML = "";
      container.appendChild(renderer.domElement);
      rendererRef.current = renderer;

      // 4. Measurement Manager
      const measurementManager = new MeasurementManager(
        sceneBuilder.scene,
        perspectiveCamera,
        container
      );
      measurementManagerRef.current = measurementManager;
      onMeasurementsChangeRef.current([...measurementManager.measurements]);

      // 5. Pointer interaction
      const raycaster = new THREE.Raycaster();
      const mouse = new THREE.Vector2();

      const handlePointerDown = (e: MouseEvent) => {
        isDraggingRef.current = true;
        isRightClickRef.current = e.button === 2;
        previousMousePositionRef.current = { x: e.clientX, y: e.clientY };
        dragStartRef.current = { x: e.clientX, y: e.clientY };
      };

      const handlePointerMove = (e: MouseEvent) => {
        const camera = activeCamera();
        if (!camera) return;

        const rect = container.getBoundingClientRect();
        mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
        mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

        // Coordinate readout on hover
        raycaster.setFromCamera(mouse, camera);
        const hits = raycaster.intersectObjects(sceneBuilder.interactiveMeshes, true);
        if (hits.length > 0) {
          const p = hits[0].point;
          onHoverCoordinateRef.current?.(
            `X: ${p.x >= 0 ? "+" : ""}${p.x.toFixed(2)}m  Y: ${p.y.toFixed(
              2
            )}m  Z: ${p.z >= 0 ? "+" : ""}${p.z.toFixed(2)}m`
          );
        } else {
          onHoverCoordinateRef.current?.(null);
        }

        if (!isDraggingRef.current) return;

        const deltaX = e.clientX - previousMousePositionRef.current.x;
        const deltaY = e.clientY - previousMousePositionRef.current.y;
        previousMousePositionRef.current = { x: e.clientX, y: e.clientY };

        if (isOrtho()) {
          // Plan view: every drag pans across the floor.
          const container2 = mountRef.current;
          const h = container2?.clientHeight || 1;
          const worldPerPixel = (orthoRef.current.halfHeight * 2) / h;
          orthoRef.current.x -= deltaX * worldPerPixel;
          orthoRef.current.z -= deltaY * worldPerPixel;
          updateOrthographicCamera();
          return;
        }

        const shouldPan =
          isRightClickRef.current || interactionModeRef.current === "pan";

        if (shouldPan) {
          const perspectiveCam = perspectiveCameraRef.current;
          if (!perspectiveCam) return;
          const panSpeed = 0.008 * (sphericalRef.current.radius / 10);
          const forward = new THREE.Vector3();
          perspectiveCam.getWorldDirection(forward);
          const right = new THREE.Vector3()
            .crossVectors(forward, perspectiveCam.up)
            .normalize();
          const up = new THREE.Vector3().crossVectors(right, forward).normalize();

          cameraTargetRef.current.addScaledVector(right, -deltaX * panSpeed);
          cameraTargetRef.current.addScaledVector(up, deltaY * panSpeed);
        } else {
          sphericalRef.current.theta -= deltaX * 0.006;
          sphericalRef.current.phi = clamp(
            sphericalRef.current.phi - deltaY * 0.006,
            0.05,
            Math.PI / 2 + 0.1
          );
        }

        updatePerspectiveCamera();
      };

      const handlePointerUp = (e: MouseEvent) => {
        // Compare against where the drag began, not the last move event, so a
        // slow drag is never mistaken for a click.
        const deltaMove =
          Math.abs(e.clientX - dragStartRef.current.x) +
          Math.abs(e.clientY - dragStartRef.current.y);

        isDraggingRef.current = false;

        const camera = activeCamera();
        if (
          deltaMove < 5 &&
          e.button === 0 &&
          camera &&
          measurementManagerRef.current?.isMeasureModeActive
        ) {
          const rect = container.getBoundingClientRect();
          mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
          mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

          raycaster.setFromCamera(mouse, camera);
          const intersects = raycaster.intersectObjects(
            sceneBuilder.interactiveMeshes,
            true
          );

          if (intersects.length > 0) {
            measurementManagerRef.current.handlePointClick(intersects[0].point);
            onMeasurementsChangeRef.current([
              ...measurementManagerRef.current.measurements,
            ]);
          }
        }
      };

      const handleWheel = (e: WheelEvent) => {
        e.preventDefault();
        if (isOrtho()) {
          orthoRef.current.halfHeight = clamp(
            orthoRef.current.halfHeight + e.deltaY * 0.004,
            MIN_HALF_HEIGHT,
            MAX_HALF_HEIGHT
          );
          updateOrthographicCamera();
          return;
        }
        sphericalRef.current.radius = clamp(
          sphericalRef.current.radius + e.deltaY * 0.002,
          MIN_RADIUS,
          MAX_RADIUS
        );
        updatePerspectiveCamera();
      };

      const handleContextMenu = (e: MouseEvent) => e.preventDefault();
      const handlePointerLeave = () => onHoverCoordinateRef.current?.(null);

      container.addEventListener("mousedown", handlePointerDown);
      window.addEventListener("mousemove", handlePointerMove);
      window.addEventListener("mouseup", handlePointerUp);
      container.addEventListener("wheel", handleWheel, { passive: false });
      container.addEventListener("contextmenu", handleContextMenu);
      container.addEventListener("mouseleave", handlePointerLeave);

      // 6. Animation Loop
      let animationFrameId: number;
      const animate = () => {
        animationFrameId = requestAnimationFrame(animate);
        const camera = activeCamera();
        if (camera) renderer.render(sceneBuilder.scene, camera);
      };
      animate();

      // 7. Resize
      const resizeObserver = new ResizeObserver(() => {
        const w = container.clientWidth;
        const h = container.clientHeight;
        if (w === 0 || h === 0) return;

        perspectiveCamera.aspect = w / h;
        perspectiveCamera.updateProjectionMatrix();
        updateOrthographicCamera();
        renderer.setSize(w, h);
      });
      resizeObserver.observe(container);

      return () => {
        cancelAnimationFrame(animationFrameId);
        container.removeEventListener("mousedown", handlePointerDown);
        window.removeEventListener("mousemove", handlePointerMove);
        window.removeEventListener("mouseup", handlePointerUp);
        container.removeEventListener("wheel", handleWheel);
        container.removeEventListener("contextmenu", handleContextMenu);
        container.removeEventListener("mouseleave", handlePointerLeave);
        resizeObserver.disconnect();
        renderer.dispose();
      };
      // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    // Measure mode
    useEffect(() => {
      if (measurementManagerRef.current) {
        measurementManagerRef.current.isMeasureModeActive = isMeasureMode;
      }
    }, [isMeasureMode]);

    // Semantic layers
    useEffect(() => {
      sceneBuilderRef.current?.updateSemanticLayers(semanticLayers);
    }, [semanticLayers]);

    // Render mode (textured / wireframe mesh / raw point cloud)
    useEffect(() => {
      sceneBuilderRef.current?.setRenderMode(renderMode);
    }, [renderMode]);

    // View mode — reframes the camera and swaps projection for 2D
    useEffect(() => {
      applyViewPreset(viewMode);
      // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [viewMode]);

    return (
      <div className="relative w-full h-full select-none overflow-hidden bg-[#eef3f9]">
        <div
          ref={mountRef}
          className={`w-full h-full ${
            isMeasureMode
              ? "cursor-crosshair"
              : interactionMode === "pan"
              ? "cursor-move"
              : "cursor-grab active:cursor-grabbing"
          }`}
        />

        {/* Measurement Mode Helper Callout */}
        {isMeasureMode && (
          <div className="absolute top-4 left-1/2 -translate-x-1/2 z-20 px-4 py-2 rounded-full bg-[#2563eb] text-white shadow-lg text-[11px] font-bold flex items-center gap-2 pointer-events-none">
            <Ruler />
            <span>Click two points on the model to measure metric distance</span>
          </div>
        )}
      </div>
    );
  }
);

/** Small inline ruler glyph — avoids pulling an icon import into the canvas. */
function Ruler() {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className="w-3.5 h-3.5"
      aria-hidden
    >
      <path d="M21.3 8.7 8.7 21.3a1 1 0 0 1-1.4 0l-4.6-4.6a1 1 0 0 1 0-1.4L15.3 2.7a1 1 0 0 1 1.4 0l4.6 4.6a1 1 0 0 1 0 1.4Z" />
      <path d="m7.5 10.5 2 2M10.5 7.5l2 2M13.5 4.5l2 2M4.5 13.5l2 2" />
    </svg>
  );
}
