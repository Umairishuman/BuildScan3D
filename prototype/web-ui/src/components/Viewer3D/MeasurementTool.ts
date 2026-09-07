import * as THREE from "three";

export interface MeasurementRecord {
  id: string;
  name: string;
  distanceMeters: number;
  startPoint: THREE.Vector3;
  endPoint: THREE.Vector3;
  color: string;
}

export class MeasurementManager {
  private scene: THREE.Scene;
  private camera: THREE.Camera;
  private container: HTMLElement;
  public measurements: MeasurementRecord[] = [];
  public currentStartPoint: THREE.Vector3 | null = null;
  public isMeasureModeActive: boolean = false;

  private activeMarkersGroup: THREE.Group;
  private previewLine: THREE.Line | null = null;
  private previewMarker: THREE.Mesh | null = null;

  constructor(scene: THREE.Scene, camera: THREE.Camera, container: HTMLElement) {
    this.scene = scene;
    this.camera = camera;
    this.container = container;

    this.activeMarkersGroup = new THREE.Group();
    this.scene.add(this.activeMarkersGroup);

    // Initial default measurements to show immediately for defense demonstration
    this.addDefaultMeasurement(
      new THREE.Vector3(-0.71, 3.4, 0.8),
      new THREE.Vector3(0.71, 3.4, 0.8),
      "Main HVAC Duct Width",
      1.42
    );

    this.addDefaultMeasurement(
      new THREE.Vector3(0, 0, -2.5),
      new THREE.Vector3(0, 2.85, -2.5),
      "Chilled Water Pipe Header Clear Height",
      2.85
    );
  }

  private addDefaultMeasurement(
    p1: THREE.Vector3,
    p2: THREE.Vector3,
    name: string,
    overrideDistance?: number
  ) {
    const dist = overrideDistance ?? p1.distanceTo(p2);
    const id = `meas_${Date.now()}_${Math.random().toString(36).substr(2, 4)}`;

    const record: MeasurementRecord = {
      id,
      name,
      distanceMeters: +dist.toFixed(2),
      startPoint: p1,
      endPoint: p2,
      color: "#38bdf8",
    };

    this.measurements.push(record);
    this.renderMeasurementVisuals(record);
  }

  public handlePointClick(point: THREE.Vector3): MeasurementRecord | null {
    if (!this.isMeasureModeActive) return null;

    if (!this.currentStartPoint) {
      // First point selected
      this.currentStartPoint = point.clone();
      this.createMarker(point, 0x38bdf8);
      return null;
    } else {
      // Second point selected: complete measurement
      const p1 = this.currentStartPoint;
      const p2 = point.clone();
      const dist = p1.distanceTo(p2);

      const count = this.measurements.length + 1;
      const record: MeasurementRecord = {
        id: `meas_${Date.now()}`,
        name: `Dimension #${count}`,
        distanceMeters: +dist.toFixed(2),
        startPoint: p1,
        endPoint: p2,
        color: "#38bdf8",
      };

      this.measurements.push(record);
      this.renderMeasurementVisuals(record);
      this.currentStartPoint = null;

      return record;
    }
  }

  private createMarker(pos: THREE.Vector3, color: number): THREE.Mesh {
    const geo = new THREE.SphereGeometry(0.045, 16, 16);
    const mat = new THREE.MeshBasicMaterial({ color, depthTest: false });
    const mesh = new THREE.Mesh(geo, mat);
    mesh.position.copy(pos);
    mesh.renderOrder = 999;
    this.activeMarkersGroup.add(mesh);
    return mesh;
  }

  private renderMeasurementVisuals(record: MeasurementRecord) {
    this.createMarker(record.startPoint, 0x38bdf8);
    this.createMarker(record.endPoint, 0x38bdf8);

    // Laser Line between points
    const points = [record.startPoint, record.endPoint];
    const lineGeo = new THREE.BufferGeometry().setFromPoints(points);
    const lineMat = new THREE.LineDashedMaterial({
      color: 0x38bdf8,
      dashSize: 0.1,
      gapSize: 0.05,
      linewidth: 3,
      depthTest: false,
    });

    const line = new THREE.Line(lineGeo, lineMat);
    line.computeLineDistances();
    line.renderOrder = 998;
    this.activeMarkersGroup.add(line);
  }

  public clearAll() {
    this.measurements = [];
    this.currentStartPoint = null;
    while (this.activeMarkersGroup.children.length > 0) {
      const obj = this.activeMarkersGroup.children[0];
      this.activeMarkersGroup.remove(obj);
    }
  }

  public deleteMeasurement(id: string) {
    this.measurements = this.measurements.filter((m) => m.id !== id);
    // Re-render
    while (this.activeMarkersGroup.children.length > 0) {
      const obj = this.activeMarkersGroup.children[0];
      this.activeMarkersGroup.remove(obj);
    }
    this.measurements.forEach((m) => this.renderMeasurementVisuals(m));
  }
}
