"use client";

import React, { useCallback, useEffect, useRef, useState, use } from "react";
import { notFound } from "next/navigation";
import { Download, Layers as LayersIcon, Ruler as RulerIcon } from "lucide-react";
import { AppShell } from "@/components/AppShell";
import {
  DetailTab,
  DETAIL_TABS,
} from "@/components/ProjectDetail/DetailSidebar";
import { ProjectDetailTopBar } from "@/components/ProjectDetail/ProjectDetailTopBar";
import {
  ViewModeToggle,
  ViewportToolRail,
  AxisGizmo,
  ViewportBottomBar,
} from "@/components/ProjectDetail/ViewportOverlays";
import { FloatingSidePanel } from "@/components/ProjectDetail/FloatingSidePanel";
import { MeasurementsPanel } from "@/components/ProjectDetail/MeasurementsPanel";
import { ComparisonView } from "@/components/ProjectDetail/ComparisonView";
import { OverviewTab } from "@/components/ProjectDetail/OverviewTab";
import { FilesTab } from "@/components/ProjectDetail/FilesTab";
import { ReportTab } from "@/components/ProjectDetail/ReportTab";
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
import { Eye, EyeOff } from "lucide-react";

interface ViewerPageProps {
  params: Promise<{ id: string }>;
}

type PanelKey = "layers" | "measurements" | null;

export default function ViewerPage({ params }: ViewerPageProps) {
  const { id: projectId } = use(params);
  const project = MOCK_PROJECTS.find((p) => p.id === projectId);
  if (!project) notFound();
  return <ViewerWorkspace project={project} />;
}

/* --------------------------- Semantic Layers config --------------------------- */

interface LayerMeta {
  key: keyof SemanticLayersState;
  label: string;
  dot: string;
  count: string;
}

const LAYERS: LayerMeta[] = [
  { key: "pipes", label: "Pipes & Plumbing", dot: "bg-[#0369a1]", count: "12 Segments" },
  { key: "conduits", label: "Electrical Conduits", dot: "bg-[#d97706]", count: "18 Runs" },
  { key: "hvac", label: "HVAC Ductwork", dot: "bg-[#059669]", count: "4 Units" },
  { key: "fire", label: "Fire Protection", dot: "bg-[#dc2626]", count: "8 Sprinklers" },
  { key: "base", label: "Structural Base & Walls", dot: "bg-[#94a3b8]", count: "Architecture" },
  { key: "pointcloud", label: "Gaussian Splats (Raw)", dot: "bg-[#6366f1]", count: "1.24M Points" },
];

/* --------------------------- Workspace --------------------------- */

export function ViewerWorkspace({ project }: { project: (typeof MOCK_PROJECTS)[number] }) {
  const canvasRef = useRef<Canvas3DHandle>(null);
  const viewportRef = useRef<HTMLDivElement>(null);

  const [detailTab, setDetailTab] = useState<DetailTab>("viewer");
  const [openPanel, setOpenPanel] = useState<PanelKey>(null);
  const [measurementsSubTab, setMeasurementsSubTab] =
    useState<"saved" | "current" | "tools">("saved");

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
  const [isMeasureMode, setIsMeasureMode] = useState(false);
  const [xrayMode, setXrayMode] = useState(false);
  const [hoveredCoordinate, setHoveredCoordinate] = useState<string | null>(null);
  const [orbit, setOrbit] = useState({ theta: Math.PI / 4, phi: Math.PI / 3 });
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isExportModalOpen, setIsExportModalOpen] = useState(false);
  const [isChromeVisible, setIsChromeVisible] = useState(true);
  const chromeTimeoutRef = useRef<number | null>(null);

  const handleToggleLayer = (layer: keyof SemanticLayersState) => {
    setSemanticLayers((prev) => ({ ...prev, [layer]: !prev[layer] }));
  };

  const handleOrbitChange = useCallback((theta: number, phi: number) => {
    setOrbit((prev) =>
      Math.abs(prev.theta - theta) < 0.02 && Math.abs(prev.phi - phi) < 0.02
        ? prev
        : { theta, phi }
    );
  }, []);

  const handleToggleFullscreen = () => {
    if (document.fullscreenElement) document.exitFullscreen();
    else viewportRef.current?.requestFullscreen?.();
  };

  useEffect(() => {
    const onChange = () => setIsFullscreen(Boolean(document.fullscreenElement));
    document.addEventListener("fullscreenchange", onChange);
    return () => document.removeEventListener("fullscreenchange", onChange);
  }, []);

  // Auto-hide the top strip after 2.5s of no cursor movement while the 3D
  // viewer is open. Any mousemove (or leaving the viewport) restores it. Other
  // tabs always show the strip regardless of `isChromeVisible`.
  const bumpChrome = useCallback(() => {
    setIsChromeVisible(true);
    if (chromeTimeoutRef.current !== null) {
      window.clearTimeout(chromeTimeoutRef.current);
    }
    chromeTimeoutRef.current = window.setTimeout(() => {
      setIsChromeVisible(false);
    }, 2500);
  }, []);

  // Cancel any pending hide when the tab changes; the derived visibility below
  // handles making non-viewer tabs always show the strip.
  useEffect(() => {
    if (detailTab === "viewer") return;
    if (chromeTimeoutRef.current !== null) {
      window.clearTimeout(chromeTimeoutRef.current);
      chromeTimeoutRef.current = null;
    }
  }, [detailTab]);

  const isTopBarVisible = detailTab !== "viewer" || isChromeVisible;

  // "Measurements" tab in the top bar now opens the floating measurements
  // panel over the 3D viewport rather than swapping the centre content.
  const handleSelectDetailTab = (tab: DetailTab) => {
    if (tab === "measurements") {
      setDetailTab("viewer");
      setOpenPanel("measurements");
      setMeasurementsSubTab("saved");
      return;
    }
    setDetailTab(tab);
    setOpenPanel(null);
  };

  const handleToggleMeasureMode = () => {
    setIsMeasureMode((prev) => {
      const next = !prev;
      if (next) {
        setOpenPanel("measurements");
        setMeasurementsSubTab("current");
      }
      return next;
    });
  };

  const handleDeleteMeasurement = (id: string) =>
    canvasRef.current?.deleteMeasurement(id);
  const handleClearMeasurements = () => canvasRef.current?.clearMeasurements();

  const isPlanView = viewMode === "2d";
  const activeDetailTab = DETAIL_TABS.find((t) => t.id === detailTab);

  return (
    <AppShell
      variant="fluid"
      activeNav="projects"
      breadcrumbs={[
        { label: "All Projects", href: "/projects" },
        { label: project.name },
      ]}
    >
      <div className="flex-1 min-h-0 flex flex-col">
        {/* Top strip — collapses to zero height when the mouse is idle in the
            3D viewer so the canvas grows to fill the reclaimed space. Uses
            `max-height` instead of absolute positioning so it never covers the
            floating viewport overlays. */}
        <div
          className={`shrink-0 overflow-hidden transition-[max-height,opacity] duration-300 ease-out ${
            isTopBarVisible
              ? "max-h-16 opacity-100"
              : "max-h-0 opacity-0 pointer-events-none"
          }`}
        >
          <ProjectDetailTopBar
            project={project}
            activeTab={detailTab}
            onSelectTab={handleSelectDetailTab}
          />
        </div>

        <section
          className="flex-1 min-h-0 flex flex-col bg-[#eef3f9]"
          onMouseMove={detailTab === "viewer" ? bumpChrome : undefined}
          onMouseLeave={
            detailTab === "viewer" ? () => setIsChromeVisible(true) : undefined
          }
        >
          {detailTab === "history" ? (
            <ComparisonView onBack={() => setDetailTab("viewer")} />
          ) : detailTab === "overview" ? (
            <OverviewTab project={project} />
          ) : detailTab === "files" ? (
            <FilesTab />
          ) : detailTab === "report" ? (
            <ReportTab project={project} />
          ) : detailTab === "viewer" ? (
            <div ref={viewportRef} className="relative flex-1 min-h-0 bg-[#eef3f9]">
              <Canvas3D
                ref={canvasRef}
                semanticLayers={semanticLayers}
                renderMode={renderMode}
                viewMode={viewMode}
                interactionMode={interactionMode}
                isMeasureMode={isMeasureMode}
                xrayMode={xrayMode}
                onMeasurementsChange={setMeasurements}
                onHoverCoordinate={setHoveredCoordinate}
                onOrbitChange={handleOrbitChange}
              />

              {/* Top-left: view mode */}
              <div className="absolute top-4 left-4 z-20">
                <ViewModeToggle value={viewMode} onChange={setViewMode} />
              </div>

              {/* Top-right cluster: panel toggles + Export */}
              <div className="absolute top-4 right-4 z-20 flex items-center gap-2">
                <PanelToggleButton
                  Icon={LayersIcon}
                  label="Layers"
                  isActive={openPanel === "layers"}
                  onClick={() =>
                    setOpenPanel((p) => (p === "layers" ? null : "layers"))
                  }
                />
                <PanelToggleButton
                  Icon={RulerIcon}
                  label="Measurements"
                  isActive={openPanel === "measurements"}
                  count={measurements.length}
                  onClick={() =>
                    setOpenPanel((p) => (p === "measurements" ? null : "measurements"))
                  }
                />
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
                  systemsVisible={xrayMode}
                  onToggleSystems={() => setXrayMode((v) => !v)}
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
                  <span className="text-[10px] text-[#64748b] font-medium">1:1 metric</span>
                </div>
              </div>

              {/* Floating panels dock in the top-right column below the toolbar */}
              {openPanel && (
                <div className="absolute top-16 right-4 z-30">
                  {openPanel === "layers" ? (
                    <FloatingSidePanel
                      title="Semantic Layers"
                      Icon={LayersIcon}
                      badge={
                        <span className="text-[10px] px-2 py-0.5 rounded-full bg-blue-50 text-[#2563eb] font-bold border border-blue-100">
                          YOLOv8-Seg
                        </span>
                      }
                      onClose={() => setOpenPanel(null)}
                    >
                      <div className="space-y-2 pt-2">
                        {LAYERS.map((layer) => {
                          const isVisible = semanticLayers[layer.key];
                          return (
                            <button
                              key={layer.key}
                              onClick={() => handleToggleLayer(layer.key)}
                              aria-pressed={isVisible}
                              className={`w-full flex items-center justify-between p-2.5 rounded-xl border text-xs font-semibold transition-all cursor-pointer ${
                                isVisible
                                  ? "bg-white border-[#e2e8f0] shadow-sm text-[#0f172a]"
                                  : "bg-slate-50 border-transparent text-[#94a3b8]"
                              }`}
                            >
                              <div className="flex items-center gap-2.5 min-w-0">
                                <span
                                  className={`w-2.5 h-2.5 rounded-full shrink-0 ${layer.dot} ${
                                    isVisible ? "" : "opacity-40"
                                  }`}
                                />
                                <span className="truncate">{layer.label}</span>
                              </div>
                              <div className="flex items-center gap-2 shrink-0 pl-2">
                                <span className="text-[10px] text-[#64748b]">
                                  {layer.count}
                                </span>
                                {isVisible ? (
                                  <Eye className="w-3.5 h-3.5 text-[#2563eb]" />
                                ) : (
                                  <EyeOff className="w-3.5 h-3.5 text-[#cbd5e1]" />
                                )}
                              </div>
                            </button>
                          );
                        })}
                      </div>
                    </FloatingSidePanel>
                  ) : (
                    <FloatingSidePanel
                      title="Measurements"
                      Icon={RulerIcon}
                      badge={
                        <span className="text-[10px] px-2 py-0.5 rounded-full bg-blue-50 text-[#2563eb] font-bold border border-blue-100">
                          {measurements.length} live
                        </span>
                      }
                      onClose={() => setOpenPanel(null)}
                      header={
                        <div
                          role="tablist"
                          aria-label="Measurements section"
                          className="flex items-center gap-0.5 p-1 rounded-xl bg-[#f1f5f9]"
                        >
                          {(["saved", "current", "tools"] as const).map((tab) => {
                            const isActive = measurementsSubTab === tab;
                            return (
                              <button
                                key={tab}
                                role="tab"
                                aria-selected={isActive}
                                onClick={() => setMeasurementsSubTab(tab)}
                                className={`flex-1 px-2 py-1.5 rounded-lg text-[11px] font-bold capitalize transition-all cursor-pointer ${
                                  isActive
                                    ? "bg-white text-[#2563eb] shadow-sm"
                                    : "text-[#64748b] hover:text-[#0f172a]"
                                }`}
                              >
                                {tab}
                              </button>
                            );
                          })}
                        </div>
                      }
                    >
                      <MeasurementsPanel
                        subTab={measurementsSubTab}
                        measurements={measurements}
                        isMeasureMode={isMeasureMode}
                        onToggleMeasureMode={handleToggleMeasureMode}
                        onDeleteMeasurement={handleDeleteMeasurement}
                        onClearAll={handleClearMeasurements}
                      />
                    </FloatingSidePanel>
                  )}
                </div>
              )}
            </div>
          ) : (
            <div className="flex-1 min-h-0 flex items-center justify-center p-8">
              <div className="max-w-sm text-center space-y-3 p-8 rounded-2xl bg-white border border-dashed border-[#e2e8f0] shadow-sm">
                <h2 className="text-sm font-bold text-[#0f172a]">
                  {activeDetailTab?.label} tab
                </h2>
                <p className="text-xs text-[#64748b] leading-relaxed">
                  This section is built in a later step. Switch back to the 3D
                  Viewer to keep exploring the scan.
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

/* ---------------------------- Panel toggle button ---------------------------- */

const PanelToggleButton: React.FC<{
  Icon: React.ComponentType<{ className?: string }>;
  label: string;
  isActive: boolean;
  count?: number;
  onClick: () => void;
}> = ({ Icon, label, isActive, count, onClick }) => (
  <button
    onClick={onClick}
    aria-pressed={isActive}
    className={`flex items-center gap-1.5 pl-2.5 pr-3 py-2 rounded-xl text-[11px] font-bold transition-all cursor-pointer shadow-md ${
      isActive
        ? "bg-[#2563eb] text-white"
        : "bg-white/95 backdrop-blur-md border border-[#e2e8f0] text-[#0f172a] hover:bg-white"
    }`}
  >
    <Icon className="w-3.5 h-3.5" />
    <span>{label}</span>
    {typeof count === "number" && (
      <span
        className={`text-[10px] font-mono font-bold px-1.5 py-0.5 rounded-full ${
          isActive ? "bg-white/25 text-white" : "bg-blue-50 text-[#2563eb]"
        }`}
      >
        {count}
      </span>
    )}
  </button>
);
