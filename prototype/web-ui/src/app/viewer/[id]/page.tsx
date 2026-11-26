"use client";

import React, { useCallback, useEffect, useRef, useState, use } from "react";
import { notFound } from "next/navigation";
import { Download, Layers as LayersIcon, Maximize2, Minimize2, Ruler as RulerIcon } from "lucide-react";
import { useRouter } from "next/navigation";
import { Sidebar } from "@/components/Sidebar";
import type { NavItem } from "@/lib/navigation";
import {
  ChromeIconButton,
  CoordinateReadout,
  ViewerInfoCard,
  ViewerTitleChip,
  ViewerToolbar,
} from "@/components/ProjectDetail/ViewerChrome";
import { AppShell } from "@/components/AppShell";
import {
  DetailTab,
  DETAIL_TABS,
} from "@/components/ProjectDetail/DetailSidebar";
import { ProjectDetailTopBar } from "@/components/ProjectDetail/ProjectDetailTopBar";
import { AxisGizmo } from "@/components/ProjectDetail/ViewportOverlays";
import { FloatingSidePanel } from "@/components/ProjectDetail/FloatingSidePanel";
import { ScanLayersPanel } from "@/components/ProjectDetail/ScanLayersPanel";
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
import { SplatCanvas } from "@/components/Viewer3D/SplatCanvas";
import type { ScanInfo } from "@/components/Viewer3D/scanTypes";
import { SemanticLayersState, RenderMode } from "@/components/Viewer3D/SceneBuilder";
import { MeasurementRecord } from "@/components/Viewer3D/MeasurementTool";
import { ExportModal } from "@/components/ExportModal";
import { MOCK_PROJECTS } from "@/lib/mockData";
import { useAllProjects } from "@/lib/useAllProjects";
import { Eye, EyeOff } from "lucide-react";

interface ViewerPageProps {
  params: Promise<{ id: string }>;
}

type PanelKey = "layers" | "measurements" | null;

/** Ids of scan bundles listed automatically from public/scans/ or the R2 bucket (src/lib/scanBundles.ts BUNDLE_ID_PREFIX). */
const BUNDLE_ID_PREFIX = "run-";

export default function ViewerPage({ params }: ViewerPageProps) {
  const { id: projectId } = use(params);
  const project = MOCK_PROJECTS.find((p) => p.id === projectId);
  // Mock projects without a scan bundle open straight away. Hand-written projects with a bundle go through the
  // listed projects too, so on a server without their local folder they open the published copy (D-076).
  if (project && !project.scanUrl) return <ViewerWorkspace project={project} />;
  // Not hand-written: only an auto-listed bundle can still match; anything else is a 404 straight away.
  if (!project && !projectId.startsWith(BUNDLE_ID_PREFIX)) notFound();
  return <BundleViewer projectId={projectId} />;
}

function BundleViewer({ projectId }: { projectId: string }) {
  const { projects, loading, error } = useAllProjects();
  const project = projects.find((p) => p.id === projectId);
  // wait for the list even for a hand-written project: its scanUrl may still change to the published copy
  if (project && !loading) return <ViewerWorkspace project={project} />;
  if (loading) {
    return (
      <AppShell variant="contained" activeNav="projects">
        <p className="py-16 text-center text-sm text-[#64748b]">Loading scan…</p>
      </AppShell>
    );
  }
  if (error) {
    return (
      <AppShell variant="contained" activeNav="projects">
        <p className="py-16 text-center text-sm text-[#64748b]">
          Could not list the processed scans ({error}).
        </p>
      </AppShell>
    );
  }
  notFound();
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
  // Orbit / pan switch removed with the old tool rail (2026-11-25): dragging orbits; it was never wired for splat scans.
  const interactionMode: InteractionMode = "orbit";
  const [renderMode, setRenderMode] = useState<RenderMode>("textured");
  const [measurements, setMeasurements] = useState<MeasurementRecord[]>([]);
  const [isMeasureMode, setIsMeasureMode] = useState(false);
  const [xrayMode, setXrayMode] = useState(false);
  const [hoveredCoordinate, setHoveredCoordinate] = useState<string | null>(null);
  const [orbit, setOrbit] = useState({ theta: Math.PI / 4, phi: Math.PI / 3 });
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isExportModalOpen, setIsExportModalOpen] = useState(false);
  const [isChromeVisible, setIsChromeVisible] = useState(true);
  // Labelled real scans (project.scanUrl): what the Scan Layers panel switches
  const [scanInfo, setScanInfo] = useState<ScanInfo | null>(null);
  const [hiddenGroups, setHiddenGroups] = useState<string[]>([]);
  const [tintByClass, setTintByClass] = useState(false);
  const [showFixtures, setShowFixtures] = useState(true);
  const [selectedFixture, setSelectedFixture] = useState<string | null>(null);
  const isRealScan = Boolean(project.splatUrl || project.scanUrl);
  const chromeTimeoutRef = useRef<number | null>(null);
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isInfoOpen, setIsInfoOpen] = useState(false);
  const router = useRouter();

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

  const activeDetailTab = DETAIL_TABS.find((t) => t.id === detailTab);

  if (detailTab === "viewer") {
    // Full-window viewer (2026-11-25, web STATUS D10): no navbar / breadcrumb / project bar above the model; small
    // floating controls, and only the ones that work for this project.
    return (
      <div
        ref={viewportRef}
        className="relative h-screen w-screen overflow-hidden bg-[#eef3f9] text-[#0f172a]"
        onMouseMove={bumpChrome}
      >
        {isRealScan ? (
          <SplatCanvas
            ref={canvasRef}
            splatUrl={project.scanUrl ? undefined : project.splatUrl}
            scanUrl={project.scanUrl}
            initialPosition={project.splatStart?.position ?? [0, 0, 0]}
            initialTarget={project.splatStart?.target ?? [0, 0, -1]}
            viewMode={viewMode}
            interactionMode={interactionMode}
            isMeasureMode={isMeasureMode}
            hiddenGroups={hiddenGroups}
            tintByClass={tintByClass}
            showMesh={renderMode === "mesh"}
            showFixtures={showFixtures}
            onScanLoaded={setScanInfo}
            onFixtureClick={(id) => {
              setSelectedFixture(id);
              setOpenPanel("layers");
            }}
            onMeasurementsChange={setMeasurements}
            onHoverCoordinate={setHoveredCoordinate}
            onOrbitChange={handleOrbitChange}
          />
        ) : (
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
        )}

        <Sidebar
          isOpen={isMenuOpen}
          onClose={() => setIsMenuOpen(false)}
          activeNav="projects"
          onSelectNav={(item: NavItem) => {
            if (item.href) router.push(item.href);
          }}
          onOpenRecentSite={(id: string) => router.push(`/viewer/${id}`)}
        />

        {/* top left: menu, back, identity, details */}
        <div className="absolute top-3 left-3 z-30 flex flex-col items-start gap-2">
          <ViewerTitleChip
            project={project}
            backHref="/projects"
            onOpenMenu={() => setIsMenuOpen(true)}
            infoOpen={isInfoOpen}
            onToggleInfo={() => setIsInfoOpen((v) => !v)}
            moreItems={
              isRealScan
                ? undefined
                : (["overview", "history", "files", "report"] as const).map((id) => ({
                    label: DETAIL_TABS.find((t) => t.id === id)?.label ?? id,
                    onSelect: () => handleSelectDetailTab(id),
                  }))
            }
          />
          {isInfoOpen && <ViewerInfoCard project={project} onClose={() => setIsInfoOpen(false)} />}
        </div>

        {/* top right: tools; panels open underneath */}
        <div className="absolute top-3 right-3 z-30 flex flex-col items-end gap-2">
          <div className="flex items-center gap-1.5">
            <ChromeIconButton
              Icon={LayersIcon}
              label="Semantic layers"
              active={openPanel === "layers"}
              onClick={() => setOpenPanel((p) => (p === "layers" ? null : "layers"))}
              disabledReason={
                isRealScan && !project.scanUrl
                  ? "this scan has no semantic labels (walls, floor, doors, fixtures); labelled scans come from the semantics stage"
                  : undefined
              }
            />
            <ChromeIconButton
              Icon={RulerIcon}
              label={isMeasureMode ? "Measuring: click two points on the model (click here to stop)" : "Measure"}
              active={isMeasureMode || openPanel === "measurements"}
              badge={measurements.length}
              onClick={() => {
                if (isRealScan) {
                  setMeasurementsSubTab("current");
                  setIsMeasureMode((m) => !m);
                  setOpenPanel("measurements");
                } else {
                  setOpenPanel((p) => (p === "measurements" ? null : "measurements"));
                }
              }}
            />
            {project.splatUrl && !project.scanUrl ? (
              <ChromeIconButton Icon={Download} label="Download the model (.spz)" href={project.splatUrl} download />
            ) : !isRealScan ? (
              <ChromeIconButton Icon={Download} label="Export (demo)" onClick={() => setIsExportModalOpen(true)} />
            ) : (
              <ChromeIconButton
                Icon={Download}
                label="Download"
                disabledReason="this scan is several files (one per label group, plus a mesh); no single-file download yet"
              />
            )}
            <ChromeIconButton
              Icon={isFullscreen ? Minimize2 : Maximize2}
              label={isFullscreen ? "Exit full screen" : "Full screen"}
              onClick={handleToggleFullscreen}
            />
          </div>

          {openPanel === "layers" && project.scanUrl && (
            <FloatingSidePanel title="Scan Layers" Icon={LayersIcon} onClose={() => setOpenPanel(null)}>
              <ScanLayersPanel
                scan={scanInfo}
                hiddenGroups={hiddenGroups}
                onToggleGroup={(key) =>
                  setHiddenGroups((h) => (h.includes(key) ? h.filter((k) => k !== key) : [...h, key]))
                }
                tintByClass={tintByClass}
                onToggleTint={() => setTintByClass((v) => !v)}
                showFixtures={showFixtures}
                onToggleFixtures={() => setShowFixtures((v) => !v)}
                onFlyTo={(point) => canvasRef.current?.flyTo?.(point)}
                selectedFixtureId={selectedFixture}
                onSelectFixture={setSelectedFixture}
              />
            </FloatingSidePanel>
          )}
          {openPanel === "layers" && !isRealScan && (
            <FloatingSidePanel title="Semantic Layers (demo)" Icon={LayersIcon} onClose={() => setOpenPanel(null)}>
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
                        <span className={`w-2.5 h-2.5 rounded-full shrink-0 ${layer.dot} ${isVisible ? "" : "opacity-40"}`} />
                        <span className="truncate">{layer.label}</span>
                      </div>
                      {isVisible ? (
                        <Eye className="w-3.5 h-3.5 text-[#2563eb]" />
                      ) : (
                        <EyeOff className="w-3.5 h-3.5 text-[#cbd5e1]" />
                      )}
                    </button>
                  );
                })}
              </div>
            </FloatingSidePanel>
          )}
          {openPanel === "measurements" && (
            <FloatingSidePanel
              title="Measurements"
              Icon={RulerIcon}
              onClose={() => {
                setOpenPanel(null);
                setIsMeasureMode(false);
              }}
              header={
                isRealScan ? undefined : (
                  <div role="tablist" aria-label="Measurements section" className="flex items-center gap-0.5 p-1 rounded-xl bg-[#f1f5f9]">
                    {(["saved", "current", "tools"] as const).map((tab) => (
                      <button
                        key={tab}
                        role="tab"
                        aria-selected={measurementsSubTab === tab}
                        onClick={() => setMeasurementsSubTab(tab)}
                        className={`flex-1 px-2 py-1.5 rounded-lg text-[11px] font-bold capitalize cursor-pointer ${
                          measurementsSubTab === tab
                            ? "bg-white text-[#2563eb] shadow-sm"
                            : "text-[#64748b] hover:text-[#0f172a]"
                        }`}
                      >
                        {tab}
                      </button>
                    ))}
                  </div>
                )
              }
            >
              <MeasurementsPanel
                subTab={isRealScan ? "current" : measurementsSubTab}
                measurements={measurements}
                isMeasureMode={isMeasureMode}
                onToggleMeasureMode={handleToggleMeasureMode}
                onDeleteMeasurement={handleDeleteMeasurement}
                onClearAll={handleClearMeasurements}
              />
            </FloatingSidePanel>
          )}
        </div>

        {/* bottom right: coordinates while hovering + orientation */}
        <div className="absolute bottom-3 right-3 z-20 flex items-end gap-2 pointer-events-none">
          <CoordinateReadout value={hoveredCoordinate} />
          <AxisGizmo theta={orbit.theta} phi={orbit.phi} />
        </div>

        {/* bottom centre: one slim toolbar, dimmed while the mouse is idle */}
        <div className="absolute bottom-3 left-1/2 -translate-x-1/2 z-20">
          <ViewerToolbar
            viewModes={isRealScan ? ["3d", "top"] : ["3d", "top", "2d", "side", "front"]}
            viewMode={viewMode}
            onViewMode={setViewMode}
            onZoomIn={() => canvasRef.current?.zoomIn()}
            onZoomOut={() => canvasRef.current?.zoomOut()}
            onReset={() => canvasRef.current?.resetView()}
            renderOptions={
              isRealScan
                ? [
                    { mode: "textured" },
                    {
                      mode: "mesh",
                      unavailable: project.scanUrl
                        ? undefined
                        : "No mesh for this scan: only labelled scan bundles include one",
                    },
                  ]
                : [{ mode: "textured" }, { mode: "mesh" }, { mode: "pointcloud" }]
            }
            renderMode={renderMode}
            onRenderMode={setRenderMode}
            dimmed={!isChromeVisible}
            toggles={isRealScan ? undefined : [{ label: "X-Ray", active: xrayMode, onClick: () => setXrayMode((v) => !v) }]}
          />
        </div>

        {!isRealScan && (
          <ExportModal
            isOpen={isExportModalOpen}
            onClose={() => setIsExportModalOpen(false)}
            projectName={project.name}
            measurementsCount={measurements.length}
          />
        )}
      </div>
    );
  }

  // The other sections (demo projects only; real scans show just the viewer): the earlier shell with its tab bar.
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
        <ProjectDetailTopBar project={project} activeTab={detailTab} onSelectTab={handleSelectDetailTab} />
        <section className="flex-1 min-h-0 flex flex-col bg-[#eef3f9]">
          {detailTab === "history" ? (
            <ComparisonView onBack={() => setDetailTab("viewer")} />
          ) : detailTab === "overview" ? (
            <OverviewTab project={project} />
          ) : detailTab === "files" ? (
            <FilesTab />
          ) : detailTab === "report" ? (
            <ReportTab project={project} />
          ) : (
            <div className="flex-1 min-h-0 flex items-center justify-center p-8">
              <div className="max-w-sm text-center space-y-3 p-8 rounded-2xl bg-white border border-dashed border-[#e2e8f0] shadow-sm">
                <h2 className="text-sm font-bold text-[#0f172a]">{activeDetailTab?.label} tab</h2>
                <p className="text-xs text-[#64748b] leading-relaxed">
                  This section is not built. Switch back to the 3D Viewer to keep exploring the scan.
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
    </AppShell>
  );
}

