import * as THREE from "three";

export interface SemanticLayersState {
  base: boolean;
  pipes: boolean;
  conduits: boolean;
  hvac: boolean;
  fire: boolean;
  pointcloud: boolean;
}

/**
 * How the reconstruction is drawn.
 * - `textured`  solid shaded surfaces (default)
 * - `mesh`      BIM wireframe over the same geometry
 * - `pointcloud` raw Gaussian splats only, solids hidden
 */
export type RenderMode = "textured" | "mesh" | "pointcloud";

/** Viewport background, matched to the light app canvas. */
export const SCENE_BACKGROUND = 0xeef3f9;

export class SceneBuilder {
  public scene: THREE.Scene;
  public baseGroup: THREE.Group;
  public pipesGroup: THREE.Group;
  public conduitsGroup: THREE.Group;
  public hvacGroup: THREE.Group;
  public fireGroup: THREE.Group;
  public pointCloudGroup: THREE.Group;
  public interactiveMeshes: THREE.Object3D[] = [];

  /** Every solid material, so wireframe can be toggled without a scene walk. */
  private solidMaterials: THREE.MeshStandardMaterial[] = [];

  private layers: SemanticLayersState = {
    base: true,
    pipes: true,
    conduits: true,
    hvac: true,
    fire: true,
    pointcloud: true,
  };
  private renderMode: RenderMode = "textured";

  constructor() {
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(SCENE_BACKGROUND);
    // Light haze only — a dense fog on a light ground flattens the MEP colours.
    this.scene.fog = new THREE.FogExp2(SCENE_BACKGROUND, 0.018);

    this.baseGroup = new THREE.Group();
    this.pipesGroup = new THREE.Group();
    this.conduitsGroup = new THREE.Group();
    this.hvacGroup = new THREE.Group();
    this.fireGroup = new THREE.Group();
    this.pointCloudGroup = new THREE.Group();

    this.scene.add(this.baseGroup);
    this.scene.add(this.pipesGroup);
    this.scene.add(this.conduitsGroup);
    this.scene.add(this.hvacGroup);
    this.scene.add(this.fireGroup);
    this.scene.add(this.pointCloudGroup);

    this.setupLighting();
    this.buildBaseRoom();
    this.buildPipes();
    this.buildConduits();
    this.buildHVAC();
    this.buildFireSprinklers();
    this.buildGaussianPointCloud();
  }

  /** Track a material so render-mode switches can reach it later. */
  private register<T extends THREE.MeshStandardMaterial>(material: T): T {
    this.solidMaterials.push(material);
    return material;
  }

  private setupLighting() {
    // Sky/ground bounce does most of the work on a light ground plane and keeps
    // the architectural surfaces from going flat grey.
    const hemiLight = new THREE.HemisphereLight(0xffffff, 0xc8d4e3, 1.05);
    this.scene.add(hemiLight);

    const ambientLight = new THREE.AmbientLight(0xffffff, 0.35);
    this.scene.add(ambientLight);

    const keyLight = new THREE.DirectionalLight(0xffffff, 1.35);
    keyLight.position.set(6, 12, 8);
    this.scene.add(keyLight);

    // Cool fill from the opposite side to keep shadowed pipe undersides legible.
    const fillLight = new THREE.DirectionalLight(0xdbeafe, 0.5);
    fillLight.position.set(-7, 4, -6);
    this.scene.add(fillLight);
  }

  private buildBaseRoom() {
    // Floor Grid — blueprint lines, echoing the app's CAD grid background
    const gridHelper = new THREE.GridHelper(12, 24, 0x94a3b8, 0xd3dde9);
    gridHelper.position.y = 0;
    this.baseGroup.add(gridHelper);

    // Floor slab
    const floorGeo = new THREE.PlaneGeometry(12, 12);
    const floorMat = this.register(
      new THREE.MeshStandardMaterial({
        color: 0xe2e8f0,
        roughness: 0.95,
        metalness: 0.02,
      })
    );
    const floor = new THREE.Mesh(floorGeo, floorMat);
    floor.rotation.x = -Math.PI / 2;
    floor.position.y = -0.01;
    this.baseGroup.add(floor);
    this.interactiveMeshes.push(floor);

    // Back Wall
    const wallGeo = new THREE.PlaneGeometry(12, 4);
    const wallMat = this.register(
      new THREE.MeshStandardMaterial({
        color: 0xeef2f7,
        roughness: 0.95,
        metalness: 0.0,
        side: THREE.DoubleSide,
      })
    );
    const backWall = new THREE.Mesh(wallGeo, wallMat);
    backWall.position.set(0, 2, -6);
    this.baseGroup.add(backWall);
    this.interactiveMeshes.push(backWall);

    // Side Wall (Left)
    const sideWall = new THREE.Mesh(wallGeo, wallMat);
    sideWall.rotation.y = Math.PI / 2;
    sideWall.position.set(-6, 2, 0);
    this.baseGroup.add(sideWall);
    this.interactiveMeshes.push(sideWall);

    // Concrete Ceiling Beams (I-Beams)
    const beamGeo = new THREE.BoxGeometry(12, 0.3, 0.3);
    const beamMat = this.register(
      new THREE.MeshStandardMaterial({
        color: 0xaab7c7,
        metalness: 0.35,
        roughness: 0.55,
      })
    );

    for (let z = -4; z <= 4; z += 2.5) {
      const beam = new THREE.Mesh(beamGeo, beamMat);
      beam.position.set(0, 3.8, z);
      this.baseGroup.add(beam);
      this.interactiveMeshes.push(beam);
    }

    // Concrete Columns
    const colGeo = new THREE.CylinderGeometry(0.25, 0.25, 4, 16);
    const colMat = this.register(
      new THREE.MeshStandardMaterial({
        color: 0xc2ccd9,
        roughness: 0.9,
      })
    );

    const col1 = new THREE.Mesh(colGeo, colMat);
    col1.position.set(-4, 2, -3);
    this.baseGroup.add(col1);
    this.interactiveMeshes.push(col1);

    const col2 = new THREE.Mesh(colGeo, colMat);
    col2.position.set(4, 2, -3);
    this.baseGroup.add(col2);
    this.interactiveMeshes.push(col2);
  }

  private buildPipes() {
    const pipeMat = this.register(
      new THREE.MeshStandardMaterial({
        color: 0x0369a1, // Deep Blue (Hydronic / Chilled Water)
        roughness: 0.35,
        metalness: 0.65,
      })
    );

    const valveMat = this.register(
      new THREE.MeshStandardMaterial({
        color: 0xbe123c, // Red Valve handles
        roughness: 0.4,
        metalness: 0.5,
      })
    );

    // Main horizontal pipe header
    const mainPipeGeo = new THREE.CylinderGeometry(0.12, 0.12, 10, 24);
    const mainPipe = new THREE.Mesh(mainPipeGeo, pipeMat);
    mainPipe.rotation.z = Math.PI / 2;
    mainPipe.position.set(0, 2.85, -2.5);
    this.pipesGroup.add(mainPipe);
    this.interactiveMeshes.push(mainPipe);

    // Return Pipe header (lower)
    const returnPipe = new THREE.Mesh(mainPipeGeo, pipeMat);
    returnPipe.rotation.z = Math.PI / 2;
    returnPipe.position.set(0, 2.4, -2.5);
    this.pipesGroup.add(returnPipe);
    this.interactiveMeshes.push(returnPipe);

    // Vertical riser drops
    const riserGeo = new THREE.CylinderGeometry(0.08, 0.08, 2.4, 16);
    const riser1 = new THREE.Mesh(riserGeo, pipeMat);
    riser1.position.set(-2.5, 1.2, -2.5);
    this.pipesGroup.add(riser1);
    this.interactiveMeshes.push(riser1);

    const riser2 = new THREE.Mesh(riserGeo, pipeMat);
    riser2.position.set(2.5, 1.2, -2.5);
    this.pipesGroup.add(riser2);
    this.interactiveMeshes.push(riser2);

    // Valve wheels
    const valveGeo = new THREE.TorusGeometry(0.12, 0.025, 8, 24);
    const v1 = new THREE.Mesh(valveGeo, valveMat);
    v1.position.set(-2.5, 1.8, -2.35);
    this.pipesGroup.add(v1);
    this.interactiveMeshes.push(v1);

    const v2 = new THREE.Mesh(valveGeo, valveMat);
    v2.position.set(2.5, 1.8, -2.35);
    this.pipesGroup.add(v2);
    this.interactiveMeshes.push(v2);
  }

  private buildConduits() {
    const conduitMat = this.register(
      new THREE.MeshStandardMaterial({
        color: 0xd97706, // Amber (Electrical)
        roughness: 0.4,
        metalness: 0.6,
      })
    );

    const boxMat = this.register(
      new THREE.MeshStandardMaterial({
        color: 0x92400e,
        roughness: 0.5,
        metalness: 0.5,
      })
    );

    // Multi-run electrical conduit pipes along back wall
    for (let i = 0; i < 4; i++) {
      const yPos = 3.2 + i * 0.08;
      const conduitGeo = new THREE.CylinderGeometry(0.025, 0.025, 11, 12);
      const conduit = new THREE.Mesh(conduitGeo, conduitMat);
      conduit.rotation.z = Math.PI / 2;
      conduit.position.set(0, yPos, -5.85);
      this.conduitsGroup.add(conduit);
      this.interactiveMeshes.push(conduit);
    }

    // Junction Box
    const jBoxGeo = new THREE.BoxGeometry(0.35, 0.45, 0.15);
    const jBox = new THREE.Mesh(jBoxGeo, boxMat);
    jBox.position.set(1.5, 3.3, -5.8);
    this.conduitsGroup.add(jBox);
    this.interactiveMeshes.push(jBox);

    // Conduit vertical drop
    const dropGeo = new THREE.CylinderGeometry(0.025, 0.025, 2.5, 12);
    const drop = new THREE.Mesh(dropGeo, conduitMat);
    drop.position.set(1.5, 2.0, -5.85);
    this.conduitsGroup.add(drop);
    this.interactiveMeshes.push(drop);
  }

  private buildHVAC() {
    const hvacMat = this.register(
      new THREE.MeshStandardMaterial({
        color: 0x059669, // Emerald Metallic (HVAC Ductwork)
        roughness: 0.35,
        metalness: 0.7,
      })
    );

    // Primary Rectangular Supply Duct
    const ductGeo = new THREE.BoxGeometry(10, 0.65, 1.42); // 1.42m width!
    const duct = new THREE.Mesh(ductGeo, hvacMat);
    duct.position.set(0, 3.4, 0.8);
    this.hvacGroup.add(duct);
    this.interactiveMeshes.push(duct);

    // Branch takeoff duct
    const branchGeo = new THREE.BoxGeometry(0.5, 0.45, 3);
    const branch = new THREE.Mesh(branchGeo, hvacMat);
    branch.position.set(2, 3.4, 2.5);
    this.hvacGroup.add(branch);
    this.interactiveMeshes.push(branch);

    // Supply Diffuser / Vent
    const ventGeo = new THREE.BoxGeometry(0.6, 0.05, 0.6);
    const ventMat = this.register(
      new THREE.MeshStandardMaterial({
        color: 0x065f46,
        metalness: 0.5,
      })
    );
    const vent = new THREE.Mesh(ventGeo, ventMat);
    vent.position.set(2, 3.15, 3.8);
    this.hvacGroup.add(vent);
    this.interactiveMeshes.push(vent);
  }

  private buildFireSprinklers() {
    const fireMat = this.register(
      new THREE.MeshStandardMaterial({
        color: 0xdc2626, // Red
        roughness: 0.3,
        metalness: 0.6,
      })
    );

    // Main line
    const fireGeo = new THREE.CylinderGeometry(0.04, 0.04, 10, 16);
    const firePipe = new THREE.Mesh(fireGeo, fireMat);
    firePipe.rotation.x = Math.PI / 2;
    firePipe.position.set(-3.5, 3.65, 0);
    this.fireGroup.add(firePipe);
    this.interactiveMeshes.push(firePipe);

    // Sprinkler drop heads
    const headGeo = new THREE.ConeGeometry(0.04, 0.08, 8);
    for (let z = -4; z <= 4; z += 2) {
      const head = new THREE.Mesh(headGeo, fireMat);
      head.rotation.x = Math.PI;
      head.position.set(-3.5, 3.55, z);
      this.fireGroup.add(head);
      this.interactiveMeshes.push(head);
    }
  }

  private buildGaussianPointCloud() {
    // Generate 12,000 synthetic 3D point cloud particles representing the raw Gaussian Splatting / Lidar reconstruction
    const count = 12000;
    const positions = new Float32Array(count * 3);
    const colors = new Float32Array(count * 3);

    // Deepened against the light viewport so splats stay legible on #eef3f9.
    const c1 = new THREE.Color(0x0284c7); // Sky blue
    const c2 = new THREE.Color(0x059669); // Emerald
    const c3 = new THREE.Color(0xd97706); // Amber
    const c4 = new THREE.Color(0x64748b); // Concrete gray

    for (let i = 0; i < count; i++) {
      // Cluster points around MEP elements
      const mode = Math.random();
      let x = 0, y = 0, z = 0;
      let col = c4;

      if (mode < 0.3) {
        // Pipe cluster
        x = (Math.random() - 0.5) * 8;
        y = 2.4 + (Math.random() - 0.5) * 0.6;
        z = -2.5 + (Math.random() - 0.5) * 0.3;
        col = c1;
      } else if (mode < 0.6) {
        // HVAC duct cluster
        x = (Math.random() - 0.5) * 9;
        y = 3.4 + (Math.random() - 0.5) * 0.7;
        z = 0.8 + (Math.random() - 0.5) * 1.5;
        col = c2;
      } else if (mode < 0.8) {
        // Electrical conduit cluster
        x = (Math.random() - 0.5) * 10;
        y = 3.2 + (Math.random() - 0.5) * 0.4;
        z = -5.8 + (Math.random() - 0.5) * 0.2;
        col = c3;
      } else {
        // Room floor and walls
        x = (Math.random() - 0.5) * 10;
        y = Math.random() * 3.8;
        z = (Math.random() - 0.5) * 10;
        col = c4;
      }

      positions[i * 3] = x;
      positions[i * 3 + 1] = y;
      positions[i * 3 + 2] = z;

      colors[i * 3] = col.r;
      colors[i * 3 + 1] = col.g;
      colors[i * 3 + 2] = col.b;
    }

    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute("color", new THREE.BufferAttribute(colors, 3));

    const material = new THREE.PointsMaterial({
      size: 0.035,
      vertexColors: true,
      transparent: true,
      opacity: 0.9,
      // Splats are the raw reconstruction — never hide them behind the fog.
      fog: false,
    });

    const pointCloud = new THREE.Points(geometry, material);
    this.pointCloudGroup.add(pointCloud);
  }

  public updateSemanticLayers(layers: SemanticLayersState) {
    this.layers = layers;
    this.applyState();
  }

  public setRenderMode(mode: RenderMode) {
    this.renderMode = mode;
    this.applyState();
  }

  /**
   * Single place where layer toggles and render mode resolve into visibility.
   * Keeping them combined stops the two controls fighting over the same groups
   * (notably the point cloud, which both can address).
   */
  private applyState() {
    const solidsVisible = this.renderMode !== "pointcloud";

    this.baseGroup.visible = this.layers.base && solidsVisible;
    this.pipesGroup.visible = this.layers.pipes && solidsVisible;
    this.conduitsGroup.visible = this.layers.conduits && solidsVisible;
    this.hvacGroup.visible = this.layers.hvac && solidsVisible;
    this.fireGroup.visible = this.layers.fire && solidsVisible;
    this.pointCloudGroup.visible = this.layers.pointcloud;

    const wireframe = this.renderMode === "mesh";
    this.solidMaterials.forEach((material) => {
      material.wireframe = wireframe;
    });
  }
}

