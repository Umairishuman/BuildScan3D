"use client";

import React, { useState, use } from "react";
import { Canvas3D } from "@/components/Viewer3D/Canvas3D";
import { ViewerHUD } from "@/components/Viewer3D/ViewerHUD";
import { SemanticLayersState } from "@/components/Viewer3D/SceneBuilder";
import { MeasurementRecord } from "@/components/Viewer3D/MeasurementTool";
import { ExportModal } from "@/components/ExportModal";
import { MOCK_PROJECTS } from "@/lib/mockData";

interface ViewerPageProps {
  params: Promise<{ id: string }>;
}

export default function ViewerPage({ params }: ViewerPageProps) {
  const resolvedParams = use(params);
  const projectId = resolvedParams.id;

  const project =
    MOCK_PROJECTS.find((p) => p.id === projectId) || MOCK_PROJECTS[0];

  const [semanticLayers, setSemanticLayers] = useState<SemanticLayersState>({
    base: true,
    pipes: true,
    conduits: true,
    hvac: true,
    fire: true,
    pointcloud: true,
  });

  const [isMeasureMode, setIsMeasureMode] = useState(false);
  const [measurements, setMeasurements] = useState<MeasurementRecord[]>([]);
  const [activePresetView, setActivePresetView] = useState<
    "perspective" | "top" | "front" | "side"
  >("perspective");
  const [wireframeMode, setWireframeMode] = useState(false);
  const [isExportModalOpen, setIsExportModalOpen] = useState(false);

  const handleToggleLayer = (layer: keyof SemanticLayersState) => {
    setSemanticLayers((prev) => ({
      ...prev,
      [layer]: !prev[layer],
    }));
  };

  const handleDeleteMeasurement = (id: string) => {
    setMeasurements((prev) => prev.filter((m) => m.id !== id));
  };

  const handleClearMeasurements = () => {
    setMeasurements([]);
  };

  return (
    <div className="relative w-screen h-screen overflow-hidden bg-slate-950 select-none">
      {/* 3D WebGL / Three.js Viewport */}
      <Canvas3D
        semanticLayers={semanticLayers}
        isMeasureMode={isMeasureMode}
        onMeasurementsChange={setMeasurements}
        activePresetView={activePresetView}
        wireframeMode={wireframeMode}
      />

      {/* Floating HUD & Toolbars */}
      <ViewerHUD
        projectName={project.name}
        location={project.location}
        semanticLayers={semanticLayers}
        onToggleLayer={handleToggleLayer}
        isMeasureMode={isMeasureMode}
        onToggleMeasureMode={() => setIsMeasureMode(!isMeasureMode)}
        measurements={measurements}
        onDeleteMeasurement={handleDeleteMeasurement}
        onClearMeasurements={handleClearMeasurements}
        activePresetView={activePresetView}
        onSelectPresetView={setActivePresetView}
        wireframeMode={wireframeMode}
        onToggleWireframe={() => setWireframeMode(!wireframeMode)}
        onOpenExportModal={() => setIsExportModalOpen(true)}
      />

      {/* Export BIM / CSV Modal */}
      <ExportModal
        isOpen={isExportModalOpen}
        onClose={() => setIsExportModalOpen(false)}
        projectName={project.name}
        measurementsCount={measurements.length}
      />
    </div>
  );
}
