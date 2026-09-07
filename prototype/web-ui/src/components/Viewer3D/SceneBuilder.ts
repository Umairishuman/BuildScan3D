import * as THREE from "three";

export interface SemanticLayersState {
  base: boolean;
  pipes: boolean;
  conduits: boolean;
  hvac: boolean;
  fire: boolean;
  pointcloud: boolean;
}

export class SceneBuilder {
  public scene: THREE.Scene;
  public baseGroup: THREE.Group;
  public pipesGroup: THREE.Group;
  public conduitsGroup: THREE.Group;
  public hvacGroup: THREE.Group;
  public fireGroup: THREE.Group;
  public pointCloudGroup: THREE.Group;
  public interactiveMeshes: THREE.Object3D[] = [];

  constructor() {
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0x0a0d14);
    this.scene.fog = new THREE.FogExp2(0x0a0d14, 0.04);

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

  private setupLighting() {
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.85);
    this.scene.add(ambientLight);

    const dirLight1 = new THREE.DirectionalLight(0xffffff, 1.2);
    dirLight1.position.set(5, 10, 7);
    this.scene.add(dirLight1);

    const dirLight2 = new THREE.DirectionalLight(0x60a5fa, 0.6);
    dirLight2.position.set(-5, -2, -5);
    this.scene.add(dirLight2);

    const pointLight = new THREE.PointLight(0x38bdf8, 1.5, 15);
    pointLight.position.set(0, 2.5, 0);
    this.scene.add(pointLight);
  }

  private buildBaseRoom() {
    // Floor Grid
    const gridHelper = new THREE.GridHelper(12, 24, 0x0284c7, 0x1e293b);
    gridHelper.position.y = 0;
    this.baseGroup.add(gridHelper);

    // Floor slab
    const floorGeo = new THREE.PlaneGeometry(12, 12);
    const floorMat = new THREE.MeshStandardMaterial({
      color: 0x111827,
      roughness: 0.8,
      metalness: 0.2,
    });
    const floor = new THREE.Mesh(floorGeo, floorMat);
    floor.rotation.x = -Math.PI / 2;
    floor.position.y = -0.01;
    this.baseGroup.add(floor);
    this.interactiveMeshes.push(floor);

    // Back Wall
    const wallGeo = new THREE.PlaneGeometry(12, 4);
    const wallMat = new THREE.MeshStandardMaterial({
      color: 0x1e293b,
      roughness: 0.9,
      side: THREE.DoubleSide,
    });
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
    const beamMat = new THREE.MeshStandardMaterial({
      color: 0x334155,
      metalness: 0.6,
      roughness: 0.4,
    });

    for (let z = -4; z <= 4; z += 2.5) {
      const beam = new THREE.Mesh(beamGeo, beamMat);
      beam.position.set(0, 3.8, z);
      this.baseGroup.add(beam);
      this.interactiveMeshes.push(beam);
    }

    // Concrete Columns
    const colGeo = new THREE.CylinderGeometry(0.25, 0.25, 4, 16);
    const colMat = new THREE.MeshStandardMaterial({
      color: 0x475569,
      roughness: 0.9,
    });

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
    const pipeMat = new THREE.MeshStandardMaterial({
      color: 0x0284c7, // Vibrant Blue (Hydronic / Chilled Water)
      roughness: 0.3,
      metalness: 0.7,
    });

    const valveMat = new THREE.MeshStandardMaterial({
      color: 0xe11d48, // Red Valve handles
      roughness: 0.4,
      metalness: 0.5,
    });

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
    const conduitMat = new THREE.MeshStandardMaterial({
      color: 0xf59e0b, // Amber / Yellow (Electrical)
      roughness: 0.4,
      metalness: 0.6,
    });

    const boxMat = new THREE.MeshStandardMaterial({
      color: 0x78350f,
      roughness: 0.5,
      metalness: 0.5,
    });

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
    const hvacMat = new THREE.MeshStandardMaterial({
      color: 0x10b981, // Emerald Metallic (HVAC Ductwork)
      roughness: 0.35,
      metalness: 0.8,
    });

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
    const ventMat = new THREE.MeshStandardMaterial({
      color: 0x064e3b,
      metalness: 0.5,
    });
    const vent = new THREE.Mesh(ventGeo, ventMat);
    vent.position.set(2, 3.15, 3.8);
    this.hvacGroup.add(vent);
    this.interactiveMeshes.push(vent);
  }

  private buildFireSprinklers() {
    const fireMat = new THREE.MeshStandardMaterial({
      color: 0xef4444, // Red
      roughness: 0.3,
      metalness: 0.7,
    });

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

    const c1 = new THREE.Color(0x38bdf8); // Sky blue
    const c2 = new THREE.Color(0x10b981); // Emerald
    const c3 = new THREE.Color(0xf59e0b); // Amber
    const c4 = new THREE.Color(0x94a3b8); // Concrete gray

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
      opacity: 0.85,
    });

    const pointCloud = new THREE.Points(geometry, material);
    this.pointCloudGroup.add(pointCloud);
  }

  public updateSemanticLayers(layers: SemanticLayersState) {
    this.baseGroup.visible = layers.base;
    this.pipesGroup.visible = layers.pipes;
    this.conduitsGroup.visible = layers.conduits;
    this.hvacGroup.visible = layers.hvac;
    this.fireGroup.visible = layers.fire;
    this.pointCloudGroup.visible = layers.pointcloud;
  }
}
