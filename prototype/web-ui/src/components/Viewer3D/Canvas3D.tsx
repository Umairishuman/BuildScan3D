"use client";

import React, { useEffect, useRef, useState } from "react";
import * as THREE from "three";
import { SceneBuilder, SemanticLayersState } from "./SceneBuilder";
import { MeasurementManager, MeasurementRecord } from "./MeasurementTool";

interface Canvas3DProps {
  semanticLayers: SemanticLayersState;
  isMeasureMode: boolean;
  onMeasurementsChange: (measurements: MeasurementRecord[]) => void;
  activePresetView: "perspective" | "top" | "front" | "side";
  wireframeMode: boolean;
}

export const Canvas3D: React.FC<Canvas3DProps> = ({
  semanticLayers,
  isMeasureMode,
  onMeasurementsChange,
  activePresetView,
  wireframeMode,
}) => {
  const mountRef = useRef<HTMLDivElement>(null);
  const sceneBuilderRef = useRef<SceneBuilder | null>(null);
  const measurementManagerRef = useRef<MeasurementManager | null>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);

  // Orbit state
  const isDraggingRef = useRef(false);
  const isRightClickRef = useRef(false);
  const previousMousePositionRef = useRef({ x: 0, y: 0 });
  const cameraTargetRef = useRef(new THREE.Vector3(0, 2, 0));
  const sphericalRef = useRef({ radius: 9, theta: Math.PI / 4, phi: Math.PI / 3 });

  const [hoveredCoordinate, setHoveredCoordinate] = useState<string | null>(null);

  useEffect(() => {
    if (!mountRef.current) return;

    const container = mountRef.current;
    const width = container.clientWidth;
    const height = container.clientHeight;

    // 1. Scene & Camera
    const sceneBuilder = new SceneBuilder();
    sceneBuilderRef.current = sceneBuilder;

    const camera = new THREE.PerspectiveCamera(55, width / height, 0.1, 100);
    cameraRef.current = camera;
    updateCameraPosition();

    // 2. Renderer
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.1;
    container.innerHTML = "";
    container.appendChild(renderer.domElement);
    rendererRef.current = renderer;

    // 3. Measurement Manager
    const measurementManager = new MeasurementManager(
      sceneBuilder.scene,
      camera,
      container
    );
    measurementManagerRef.current = measurementManager;
    onMeasurementsChange([...measurementManager.measurements]);

    // 4. Raycaster for clicking & measuring
    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();

    const handlePointerDown = (e: MouseEvent) => {
      isDraggingRef.current = true;
      isRightClickRef.current = e.button === 2;
      previousMousePositionRef.current = { x: e.clientX, y: e.clientY };
    };

    const handlePointerMove = (e: MouseEvent) => {
      const rect = container.getBoundingClientRect();
      mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

      // Coordinate HUD readout on hover
      raycaster.setFromCamera(mouse, camera);
      const hits = raycaster.intersectObjects(sceneBuilder.interactiveMeshes, true);
      if (hits.length > 0) {
        const p = hits[0].point;
        setHoveredCoordinate(
          `X: ${p.x >= 0 ? "+" : ""}${p.x.toFixed(2)}m  Y: ${p.y.toFixed(
            2
          )}m  Z: ${p.z >= 0 ? "+" : ""}${p.z.toFixed(2)}m`
        );
      }

      if (!isDraggingRef.current) return;

      const deltaX = e.clientX - previousMousePositionRef.current.x;
      const deltaY = e.clientY - previousMousePositionRef.current.y;
      previousMousePositionRef.current = { x: e.clientX, y: e.clientY };

      if (isRightClickRef.current) {
        // Pan
        const panSpeed = 0.008 * (sphericalRef.current.radius / 10);
        const forward = new THREE.Vector3();
        camera.getWorldDirection(forward);
        const right = new THREE.Vector3().crossVectors(forward, camera.up).normalize();
        const up = new THREE.Vector3().crossVectors(right, forward).normalize();

        cameraTargetRef.current.addScaledVector(right, -deltaX * panSpeed);
        cameraTargetRef.current.addScaledVector(up, deltaY * panSpeed);
      } else {
        // Orbit
        sphericalRef.current.theta -= deltaX * 0.006;
        sphericalRef.current.phi = Math.max(
          0.05,
          Math.min(Math.PI / 2 + 0.1, sphericalRef.current.phi - deltaY * 0.006)
        );
      }

      updateCameraPosition();
    };

    const handlePointerUp = (e: MouseEvent) => {
      const deltaMove =
        Math.abs(e.clientX - previousMousePositionRef.current.x) +
        Math.abs(e.clientY - previousMousePositionRef.current.y);

      isDraggingRef.current = false;

      // Treat as Click if minimal movement
      if (deltaMove < 5 && e.button === 0 && measurementManagerRef.current?.isMeasureModeActive) {
        const rect = container.getBoundingClientRect();
        mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
        mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

        raycaster.setFromCamera(mouse, camera);
        const intersects = raycaster.intersectObjects(
          sceneBuilder.interactiveMeshes,
          true
        );

        if (intersects.length > 0) {
          const clickedPoint = intersects[0].point;
          measurementManagerRef.current.handlePointClick(clickedPoint);
          onMeasurementsChange([...measurementManagerRef.current.measurements]);
        }
      }
    };

    const handleWheel = (e: WheelEvent) => {
      e.preventDefault();
      const zoomSpeed = 0.002;
      sphericalRef.current.radius = Math.max(
        1.5,
        Math.min(25, sphericalRef.current.radius + e.deltaY * zoomSpeed)
      );
      updateCameraPosition();
    };

    const handleContextMenu = (e: MouseEvent) => e.preventDefault();

    container.addEventListener("mousedown", handlePointerDown);
    window.addEventListener("mousemove", handlePointerMove);
    window.addEventListener("mouseup", handlePointerUp);
    container.addEventListener("wheel", handleWheel, { passive: false });
    container.addEventListener("contextmenu", handleContextMenu);

    // 5. Animation Loop
    let animationFrameId: number;
    const animate = () => {
      animationFrameId = requestAnimationFrame(animate);
      renderer.render(sceneBuilder.scene, camera);
    };
    animate();

    // 6. Resize Observer
    const resizeObserver = new ResizeObserver(() => {
      if (!container || !renderer || !camera) return;
      const w = container.clientWidth;
      const h = container.clientHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
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
      resizeObserver.disconnect();
      renderer.dispose();
    };
  }, []);

  function updateCameraPosition() {
    if (!cameraRef.current) return;
    const { radius, theta, phi } = sphericalRef.current;
    const target = cameraTargetRef.current;

    cameraRef.current.position.set(
      target.x + radius * Math.sin(phi) * Math.sin(theta),
      target.y + radius * Math.cos(phi),
      target.z + radius * Math.sin(phi) * Math.cos(theta)
    );
    cameraRef.current.lookAt(target);
  }

  // Update measurement mode active state
  useEffect(() => {
    if (measurementManagerRef.current) {
      measurementManagerRef.current.isMeasureModeActive = isMeasureMode;
    }
  }, [isMeasureMode]);

  // Update semantic layers
  useEffect(() => {
    if (sceneBuilderRef.current) {
      sceneBuilderRef.current.updateSemanticLayers(semanticLayers);
    }
  }, [semanticLayers]);

  // Handle Preset Views
  useEffect(() => {
    if (!cameraRef.current) return;

    if (activePresetView === "perspective") {
      sphericalRef.current = { radius: 9, theta: Math.PI / 4, phi: Math.PI / 3 };
      cameraTargetRef.current.set(0, 2, 0);
    } else if (activePresetView === "top") {
      sphericalRef.current = { radius: 10, theta: 0, phi: 0.05 };
      cameraTargetRef.current.set(0, 1, 0);
    } else if (activePresetView === "front") {
      sphericalRef.current = { radius: 9, theta: 0, phi: Math.PI / 2 };
      cameraTargetRef.current.set(0, 2, -1);
    } else if (activePresetView === "side") {
      sphericalRef.current = { radius: 9, theta: Math.PI / 2, phi: Math.PI / 2 };
      cameraTargetRef.current.set(0, 2, -1);
    }

    updateCameraPosition();
  }, [activePresetView]);

  // Wireframe toggle
  useEffect(() => {
    if (!sceneBuilderRef.current) return;
    sceneBuilderRef.current.scene.traverse((obj) => {
      if ((obj as THREE.Mesh).isMesh) {
        const mesh = obj as THREE.Mesh;
        if (Array.isArray(mesh.material)) {
          mesh.material.forEach((m) => (m.wireframe = wireframeMode));
        } else if (mesh.material) {
          mesh.material.wireframe = wireframeMode;
        }
      }
    });
  }, [wireframeMode]);

  return (
    <div className="relative w-full h-full select-none overflow-hidden bg-slate-950">
      <div ref={mountRef} className="w-full h-full cursor-grab active:cursor-grabbing" />

      {/* Real-time Hovered 3D Coordinate Ticker (AR Metric Anchor) */}
      {hoveredCoordinate && (
        <div className="absolute bottom-4 left-4 z-20 px-3 py-1.5 rounded-lg bg-slate-900/80 backdrop-blur border border-slate-800 text-[11px] font-mono text-cyan-300 pointer-events-none flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
          <span>{hoveredCoordinate}</span>
          <span className="text-slate-500 font-sans text-[10px]">
            [Metric SE(3) Scale 1:1]
          </span>
        </div>
      )}

      {/* Measurement Mode Helper Callout */}
      {isMeasureMode && (
        <div className="absolute top-4 left-1/2 -translate-x-1/2 z-20 px-4 py-2 rounded-xl bg-blue-600/90 backdrop-blur text-white shadow-xl shadow-blue-500/20 text-xs font-semibold flex items-center gap-2 animate-bounce">
          <span>📐 Click two points on the 3D model to measure metric distance</span>
        </div>
      )}
    </div>
  );
};
