"use client";

import React, { useCallback, useEffect, useRef, useState, use } from "react";
import { notFound } from "next/navigation";
import { Download, Construction } from "lucide-react";
import { AppShell } from "@/components/AppShell";
import {
  DetailSidebar,
  DetailTab,
  DETAIL_TABS,
} from "@/components/ProjectDetail/DetailSidebar";
import {
  ViewModeToggle,
  ViewportToolRail,
  AxisGizmo,
  ViewportBottomBar,
} from "@/components/ProjectDetail/ViewportOverlays";
import { RightDock, DockTab } from "@/components/ProjectDetail/RightDock";
import {
  Canvas3D,
  Canvas3DHandle,
  ViewMode,
  InteractionMode,
} from "@/components/Viewer3D/Canvas3D";
import { SemanticLayersState, RenderMode } from "@/components/Viewer3D/SceneBuilder";
import { MeasurementRecord } from "@/components/Viewer3D/MeasurementTool";
import { ExportModal } from "@/components/ExportModal";
import { MOCK_PROJECTS } from "@/lib/mockData";

interface ViewerPageProps {
  params: Promise<{ id: string }>;
}

export default function ViewerPage({ params }: ViewerPageProps) {
  const { id: projectId } = use(params);
  const project = MOCK_PROJECTS.find((p) => p.id === projectId);

  // Previously this silently fell back to the first project, so a bad URL
  // showed the wrong room's data under the wrong name.
  if (!project) notFound();

  return <ViewerWorkspace project={project} />;
}

function ViewerWorkspace({ project }: { project: (typeof MOCK_PROJECTS)[number] }) {
  const canvasRef = useRef<Canvas3DHandle>(null);
  const viewportRef = useRef<HTMLDivElement>(null);

  const [detailTab, setDetailTab] = useState<DetailTab>("viewer");
  const [dockTab, setDockTab] = useState<DockTab>("layers");

  const [semanticLayers, setSemanticLayers] = useState<SemanticLayersState>({
    base: true,
    pipes: true,
    conduits: true,
    hvac: true,
    fire: true,
    pointcloud: true,
  });

  const [viewMode, setViewMode] = useState<ViewMode>("3d");
  const [interactionMode, setInteractionMode] = useState<InteractionMode>("orbit");
  const [renderMode, setRenderMode] = useState<RenderMode>("textured");
  const [measurements, setMeasurements] = useState<MeasurementRecord[]>([]);
  const [hoveredCoordinate, setHoveredCoordinate] = useState<string | null>(null);
  const [orbit, setOrbit] = useState({ theta: Math.PI / 4, phi: Math.PI / 3 });
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isExportModalOpen, setIsExportModalOpen] = useState(false);

  const handleToggleLayer = (layer: keyof SemanticLayersState) => {
    setSemanticLayers((prev) => ({ ...prev, [layer]: !prev[layer] }));
  };

  // The canvas reports orbit on every pointer move; only re-render the gizmo
  // once the camera has actually moved a visible amount.
  const handleOrbitChange = useCallback((theta: number, phi: number) => {
    setOrbit((prev) =>
      Math.abs(prev.theta - theta) < 0.02 && Math.abs(prev.phi - phi) < 0.02
        ? prev
        : { theta, phi }
    );
  }, []);

  const handleToggleFullscreen = () => {
    if (document.fullscreenElement) {
      document.exitFullscreen();
    } else {
      viewportRef.current?.requestFullscreen?.();
    }
  };

  useEffect(() => {
    const onChange = () => setIsFullscreen(Boolean(document.fullscreenElement));
    document.addEventListener("fullscreenchange", onChange);
    return () => document.removeEventListener("fullscreenchange", onChange);
  }, []);

  // "Measurements" in the left nav points at the same workspace — it just
  // focuses the dock, rather than hiding the model it measures.
  const handleSelectDetailTab = (tab: DetailTab) => {
    if (tab === "measurements") {
      setDetailTab("viewer");
      setDockTab("saved");
      return;
    }
    setDetailTab(tab);
  };

  const isPlanView = viewMode === "2d";
  const activeDetailTab = DETAIL_TABS.find((t) => t.id === detailTab);

  return (
    <AppShell
      variant="fluid"
      activeNav="projects"
      breadcrumbs={[
        { label: "All Projects", href: "/dashboard" },
        { label: project.name },
      ]}
    >
      <div className="flex-1 min-h-0 flex">
        <DetailSidebar
          project={project}
          activeTab={detailTab}
          onSelectTab={handleSelectDetailTab}
        />

        {/* Centre viewport */}
        <section className="flex-1 min-w-0 flex flex-col bg-[#eef3f9]">
          {detailTab === "viewer" ? (
            <div ref={viewportRef} className="relative flex-1 min-h-0 bg-[#eef3f9]">
              <Canvas3D
                ref={canvasRef}
                semanticLayers={semanticLayers}
                renderMode={renderMode}
                viewMode={viewMode}
                interactionMode={interactionMode}
                isMeasureMode={false}
                onMeasurementsChange={setMeasurements}
                onHoverCoordinate={setHoveredCoordinate}
                onOrbitChange={handleOrbitChange}
              />

              {/* Top-left: view mode */}
              <div className="absolute top-4 left-4 z-20">
                <ViewModeToggle value={viewMode} onChange={setViewMode} />
              </div>

              {/* Top-right: export */}
              <div className="absolute top-4 right-4 z-20">
                <button
                  onClick={() => setIsExportModalOpen(true)}
                  className="px-3.5 py-2 rounded-xl bg-[#2563eb] hover:bg-[#1d4ed8] text-white text-[11px] font-bold shadow-md transition-colors flex items-center gap-1.5 cursor-pointer"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>Export</span>
                </button>
              </div>

              {/* Right edge: tool rail */}
              <div className="absolute top-1/2 -translate-y-1/2 right-4 z-20">
                <ViewportToolRail
                  interactionMode={interactionMode}
                  onSetInteractionMode={setInteractionMode}
                  onZoomIn={() => canvasRef.current?.zoomIn()}
                  onZoomOut={() => canvasRef.current?.zoomOut()}
                  onResetView={() => canvasRef.current?.resetView()}
                  onFitToScreen={() => canvasRef.current?.fitToScreen()}
                  disableOrbit={isPlanView}
                />
              </div>

              {/* Bottom-left: axis gizmo */}
              <div className="absolute bottom-4 left-4 z-20">
                <AxisGizmo theta={orbit.theta} phi={orbit.phi} />
              </div>

              {/* Bottom-centre: render controls */}
              <div className="absolute bottom-4 left-1/2 -translate-x-1/2 z-20">
                <ViewportBottomBar
                  renderMode={renderMode}
                  onChangeRenderMode={setRenderMode}
                  splatsVisible={semanticLayers.pointcloud}
                  onToggleSplats={() => handleToggleLayer("pointcloud")}
                  onToggleFullscreen={handleToggleFullscreen}
                  isFullscreen={isFullscreen}
                />
              </div>

              {/* Bottom-right: live metric readout */}
              <div className="absolute bottom-4 right-4 z-20 pointer-events-none">
                <div className="px-3 py-2 rounded-xl bg-white/95 backdrop-blur-md border border-[#e2e8f0] shadow-sm flex items-center gap-2.5">
                  <span
                    className={`w-1.5 h-1.5 rounded-full ${
                      hoveredCoordinate ? "bg-[#2563eb] animate-pulse" : "bg-[#cbd5e1]"
                    }`}
                  />
                  <span className="text-[11px] font-mono font-bold text-[#0f172a]">
                    {hoveredCoordinate ?? "Hover the model for coordinates"}
                  </span>
                  <span className="text-[10px] text-[#64748b] font-medium">
                    1:1 metric
                  </span>
                </div>
              </div>
            </div>
          ) : (
            /* Overview / History / Files / Report arrive in spec Prompt 8. */
            <div className="flex-1 min-h-0 flex items-center justify-center p-8">
              <div className="max-w-sm text-center space-y-3 p-8 rounded-2xl bg-white border border-dashed border-[#e2e8f0] shadow-sm">
                <div className="w-11 h-11 mx-auto rounded-xl bg-blue-50 flex items-center justify-center">
                  <Construction className="w-5 h-5 text-[#2563eb]" />
                </div>
                <h2 className="text-sm font-bold text-[#0f172a]">
                  {activeDetailTab?.label} tab
                </h2>
                <p className="text-xs text-[#64748b] leading-relaxed">
                  This section is built in a later step. The 3D Viewer tab is
                  live — switch back to keep exploring the scan.
                </p>
                <button
                  onClick={() => setDetailTab("viewer")}
                  className="text-xs font-bold text-[#2563eb] hover:underline cursor-pointer"
                >
                  Back to 3D Viewer
                </button>
              </div>
            </div>
          )}
        </section>

        <RightDock
          activeTab={dockTab}
          onSelectTab={setDockTab}
          semanticLayers={semanticLayers}
          onToggleLayer={handleToggleLayer}
          measurementCount={measurements.length}
        />
      </div>

      <ExportModal
        isOpen={isExportModalOpen}
        onClose={() => setIsExportModalOpen(false)}
        projectName={project.name}
        measurementsCount={measurements.length}
      />
    </AppShell>
  );
}
