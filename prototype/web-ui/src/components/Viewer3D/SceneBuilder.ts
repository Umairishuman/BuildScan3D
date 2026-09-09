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
    const hemiLight = new THREE.HemisphereLight(0xffffff, 0xc8d4e3, 1.0);
    this.scene.add(hemiLight);

    const ambientLight = new THREE.AmbientLight(0xffffff, 0.32);
    this.scene.add(ambientLight);

    const keyLight = new THREE.DirectionalLight(0xffffff, 1.35);
    keyLight.position.set(6, 12, 8);
    keyLight.castShadow = true;
    keyLight.shadow.mapSize.set(2048, 2048);
    keyLight.shadow.camera.near = 0.5;
    keyLight.shadow.camera.far = 40;
    keyLight.shadow.camera.left = -10;
    keyLight.shadow.camera.right = 10;
    keyLight.shadow.camera.top = 10;
    keyLight.shadow.camera.bottom = -10;
    keyLight.shadow.bias = -0.0004;
    keyLight.shadow.normalBias = 0.02;
    this.scene.add(keyLight);

    // Cool fill from the opposite side to keep shadowed pipe undersides legible.
    const fillLight = new THREE.DirectionalLight(0xdbeafe, 0.55);
    fillLight.position.set(-7, 4, -6);
    this.scene.add(fillLight);

    // Warm rim from the floor lifts the pipe undersides.
    const rimLight = new THREE.DirectionalLight(0xfff1d6, 0.22);
    rimLight.position.set(0, -4, 5);
    this.scene.add(rimLight);
  }

  private buildBaseRoom() {
    // Floor Grid — blueprint lines, echoing the app's CAD grid background
    const gridHelper = new THREE.GridHelper(12, 24, 0x94a3b8, 0xd3dde9);
    gridHelper.position.y = 0.001;
    this.baseGroup.add(gridHelper);

    // Floor slab (receives shadows for the pipe/duct under-shadow story)
    const floorGeo = new THREE.PlaneGeometry(12, 12);
    const floorMat = this.register(
      new THREE.MeshStandardMaterial({
        color: 0xe6ecf3,
        roughness: 0.95,
        metalness: 0.02,
      })
    );
    const floor = new THREE.Mesh(floorGeo, floorMat);
    floor.rotation.x = -Math.PI / 2;
    floor.position.y = -0.01;
    floor.receiveShadow = true;
    this.baseGroup.add(floor);
    this.interactiveMeshes.push(floor);

    // Floor tile scribe lines (2m grid painted into the slab)
    const tileMat = new THREE.LineBasicMaterial({
      color: 0xb6c1cf,
      transparent: true,
      opacity: 0.5,
    });
    for (let i = -6; i <= 6; i += 2) {
      const g1 = new THREE.BufferGeometry().setFromPoints([
        new THREE.Vector3(-6, 0.002, i),
        new THREE.Vector3(6, 0.002, i),
      ]);
      const g2 = new THREE.BufferGeometry().setFromPoints([
        new THREE.Vector3(i, 0.002, -6),
        new THREE.Vector3(i, 0.002, 6),
      ]);
      this.baseGroup.add(new THREE.Line(g1, tileMat));
      this.baseGroup.add(new THREE.Line(g2, tileMat));
    }

    // Wall material
    const wallMat = this.register(
      new THREE.MeshStandardMaterial({
        color: 0xeef2f7,
        roughness: 0.95,
        metalness: 0.0,
        side: THREE.DoubleSide,
      })
    );

    // Back Wall
    const backWall = new THREE.Mesh(new THREE.PlaneGeometry(12, 4), wallMat);
    backWall.position.set(0, 2, -6);
    backWall.receiveShadow = true;
    this.baseGroup.add(backWall);
    this.interactiveMeshes.push(backWall);

    // Side Wall (Left)
    const leftWall = new THREE.Mesh(new THREE.PlaneGeometry(12, 4), wallMat);
    leftWall.rotation.y = Math.PI / 2;
    leftWall.position.set(-6, 2, 0);
    leftWall.receiveShadow = true;
    this.baseGroup.add(leftWall);
    this.interactiveMeshes.push(leftWall);

    // Side Wall (Right) — a symmetrical enclosure reads more like a real room.
    const rightWall = new THREE.Mesh(new THREE.PlaneGeometry(12, 4), wallMat);
    rightWall.rotation.y = -Math.PI / 2;
    rightWall.position.set(6, 2, 0);
    rightWall.receiveShadow = true;
    this.baseGroup.add(rightWall);
    this.interactiveMeshes.push(rightWall);

    // Skirting on all three walls
    const skirtingMat = this.register(
      new THREE.MeshStandardMaterial({
        color: 0x94a3b8,
        roughness: 0.85,
      })
    );
    const backSkirt = new THREE.Mesh(new THREE.BoxGeometry(12, 0.12, 0.06), skirtingMat);
    backSkirt.position.set(0, 0.06, -5.97);
    this.baseGroup.add(backSkirt);
    const leftSkirt = new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.12, 12), skirtingMat);
    leftSkirt.position.set(-5.97, 0.06, 0);
    this.baseGroup.add(leftSkirt);
    const rightSkirt = new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.12, 12), skirtingMat);
    rightSkirt.position.set(5.97, 0.06, 0);
    this.baseGroup.add(rightSkirt);

    // Concrete Ceiling Beams
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
      beam.castShadow = true;
      beam.receiveShadow = true;
      this.baseGroup.add(beam);
      this.interactiveMeshes.push(beam);
    }

    // Perpendicular tie beams
    const tieGeo = new THREE.BoxGeometry(0.22, 0.22, 12);
    for (const x of [-3.5, 3.5]) {
      const tie = new THREE.Mesh(tieGeo, beamMat);
      tie.position.set(x, 3.95, 0);
      tie.castShadow = true;
      this.baseGroup.add(tie);
      this.interactiveMeshes.push(tie);
    }

    // Concrete Columns — four corners, not two.
    const colGeo = new THREE.CylinderGeometry(0.25, 0.25, 4, 20);
    const colMat = this.register(
      new THREE.MeshStandardMaterial({
        color: 0xc2ccd9,
        roughness: 0.9,
      })
    );

    for (const [x, z] of [
      [-4, -3],
      [4, -3],
      [-4, 3],
      [4, 3],
    ] as [number, number][]) {
      const col = new THREE.Mesh(colGeo, colMat);
      col.position.set(x, 2, z);
      col.castShadow = true;
      col.receiveShadow = true;
      this.baseGroup.add(col);
      this.interactiveMeshes.push(col);

      // Column base plinth
      const plinth = new THREE.Mesh(
        new THREE.BoxGeometry(0.7, 0.14, 0.7),
        colMat
      );
      plinth.position.set(x, 0.07, z);
      plinth.receiveShadow = true;
      this.baseGroup.add(plinth);
    }

    // Ceiling grid — hairline drafting lines painted at ceiling height
    const ceilingLineMat = new THREE.LineBasicMaterial({
      color: 0x94a3b8,
      transparent: true,
      opacity: 0.35,
    });
    for (let i = -6; i <= 6; i += 1) {
      const gx = new THREE.BufferGeometry().setFromPoints([
        new THREE.Vector3(-6, 3.98, i),
        new THREE.Vector3(6, 3.98, i),
      ]);
      const gz = new THREE.BufferGeometry().setFromPoints([
        new THREE.Vector3(i, 3.98, -6),
        new THREE.Vector3(i, 3.98, 6),
      ]);
      this.baseGroup.add(new THREE.Line(gx, ceilingLineMat));
      this.baseGroup.add(new THREE.Line(gz, ceilingLineMat));
    }

    // Wall-mounted control panel — visual anchor on the back wall
    const panelMat = this.register(
      new THREE.MeshStandardMaterial({
        color: 0x1e293b,
        roughness: 0.55,
        metalness: 0.35,
      })
    );
    const panel = new THREE.Mesh(new THREE.BoxGeometry(0.9, 1.1, 0.08), panelMat);
    panel.position.set(-4.4, 1.7, -5.94);
    panel.castShadow = true;
    this.baseGroup.add(panel);
    this.interactiveMeshes.push(panel);

    // Indicator LEDs
    const ledColors = [0x22c55e, 0xf59e0b, 0xdc2626];
    ledColors.forEach((c, i) => {
      const led = new THREE.Mesh(
        new THREE.SphereGeometry(0.035, 12, 12),
        new THREE.MeshStandardMaterial({
          color: c,
          emissive: c,
          emissiveIntensity: 0.6,
        })
      );
      led.position.set(-4.4 + (i - 1) * 0.2, 2.1, -5.9);
      this.baseGroup.add(led);
    });

    // Door frame in the right wall — reads as an entry
    const frameMat = this.register(
      new THREE.MeshStandardMaterial({
        color: 0x475569,
        roughness: 0.7,
      })
    );
    const doorTop = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.08, 1.4), frameMat);
    doorTop.position.set(5.96, 2.1, 3);
    this.baseGroup.add(doorTop);
    const doorLeft = new THREE.Mesh(new THREE.BoxGeometry(0.08, 2.1, 0.08), frameMat);
    doorLeft.position.set(5.96, 1.05, 3.7);
    this.baseGroup.add(doorLeft);
    const doorRight = new THREE.Mesh(new THREE.BoxGeometry(0.08, 2.1, 0.08), frameMat);
    doorRight.position.set(5.96, 1.05, 2.3);
    this.baseGroup.add(doorRight);
  }

  private buildPipes() {
    const pipeMat = this.register(
      new THREE.MeshStandardMaterial({
        color: 0x0369a1, // Deep Blue (Hydronic / Chilled Water)
        roughness: 0.35,
        metalness: 0.65,
      })
    );

    const insulationMat = this.register(
      new THREE.MeshStandardMaterial({
        color: 0xbfdbfe, // Pale blue pipe insulation sleeves
        roughness: 0.85,
        metalness: 0.05,
      })
    );

    const valveMat = this.register(
      new THREE.MeshStandardMaterial({
        color: 0xbe123c, // Red Valve handles
        roughness: 0.4,
        metalness: 0.5,
      })
    );

    const flangeMat = this.register(
      new THREE.MeshStandardMaterial({
        color: 0x475569,
        roughness: 0.5,
        metalness: 0.7,
      })
    );

    // Main horizontal pipe header (supply)
    const mainPipeGeo = new THREE.CylinderGeometry(0.12, 0.12, 10, 24);
    const mainPipe = new THREE.Mesh(mainPipeGeo, pipeMat);
    mainPipe.rotation.z = Math.PI / 2;
    mainPipe.position.set(0, 2.85, -2.5);
    mainPipe.castShadow = true;
    this.pipesGroup.add(mainPipe);
    this.interactiveMeshes.push(mainPipe);

    // Return pipe header (lower)
    const returnPipe = new THREE.Mesh(mainPipeGeo, pipeMat);
    returnPipe.rotation.z = Math.PI / 2;
    returnPipe.position.set(0, 2.4, -2.5);
    returnPipe.castShadow = true;
    this.pipesGroup.add(returnPipe);
    this.interactiveMeshes.push(returnPipe);

    // Insulation sleeves at intervals along the supply header
    for (const x of [-3.2, -1.4, 1.4, 3.2]) {
      const sleeve = new THREE.Mesh(
        new THREE.CylinderGeometry(0.16, 0.16, 0.6, 20),
        insulationMat
      );
      sleeve.rotation.z = Math.PI / 2;
      sleeve.position.set(x, 2.85, -2.5);
      sleeve.castShadow = true;
      this.pipesGroup.add(sleeve);
      this.interactiveMeshes.push(sleeve);
    }

    // Flanges where risers meet the header (paired collars for a real fitting look)
    for (const x of [-2.5, 2.5]) {
      const flange = new THREE.Mesh(
        new THREE.CylinderGeometry(0.16, 0.16, 0.05, 20),
        flangeMat
      );
      flange.position.set(x, 2.72, -2.5);
      this.pipesGroup.add(flange);
    }

    // Vertical riser drops with elbow bends into the header
    const riserGeo = new THREE.CylinderGeometry(0.08, 0.08, 2.4, 18);
    const elbowGeo = new THREE.TorusGeometry(0.14, 0.08, 12, 20, Math.PI / 2);
    for (const x of [-2.5, 2.5]) {
      const riser = new THREE.Mesh(riserGeo, pipeMat);
      riser.position.set(x, 1.2, -2.5);
      riser.castShadow = true;
      this.pipesGroup.add(riser);
      this.interactiveMeshes.push(riser);

      // Elbow bending the vertical riser into the horizontal header
      const elbow = new THREE.Mesh(elbowGeo, pipeMat);
      elbow.position.set(x + (x < 0 ? 0.14 : -0.14), 2.4, -2.5);
      elbow.rotation.z = x < 0 ? Math.PI / 2 : 0;
      elbow.castShadow = true;
      this.pipesGroup.add(elbow);
      this.interactiveMeshes.push(elbow);
    }

    // Valve wheels on the risers
    const valveGeo = new THREE.TorusGeometry(0.12, 0.025, 8, 24);
    for (const x of [-2.5, 2.5]) {
      const wheel = new THREE.Mesh(valveGeo, valveMat);
      wheel.position.set(x, 1.8, -2.35);
      wheel.castShadow = true;
      this.pipesGroup.add(wheel);
      this.interactiveMeshes.push(wheel);

      // Valve stem
      const stem = new THREE.Mesh(
        new THREE.CylinderGeometry(0.02, 0.02, 0.15, 12),
        valveMat
      );
      stem.rotation.x = Math.PI / 2;
      stem.position.set(x, 1.8, -2.42);
      this.pipesGroup.add(stem);
    }

    // Pipe hangers strapping the header to the ceiling beam above
    const hangerMat = this.register(
      new THREE.MeshStandardMaterial({
        color: 0x64748b,
        metalness: 0.7,
        roughness: 0.35,
      })
    );
    for (const x of [-4, -1.2, 1.2, 4]) {
      const rod = new THREE.Mesh(
        new THREE.CylinderGeometry(0.015, 0.015, 1.05, 8),
        hangerMat
      );
      rod.position.set(x, 3.35, -2.5);
      this.pipesGroup.add(rod);

      const clamp = new THREE.Mesh(
        new THREE.TorusGeometry(0.135, 0.02, 8, 20),
        hangerMat
      );
      clamp.rotation.x = Math.PI / 2;
      clamp.rotation.z = Math.PI / 2;
      clamp.position.set(x, 2.85, -2.5);
      this.pipesGroup.add(clamp);
    }

    // A branch pipe taking off toward the door side
    const branch = new THREE.Mesh(
      new THREE.CylinderGeometry(0.06, 0.06, 4.5, 16),
      pipeMat
    );
    branch.rotation.x = Math.PI / 2;
    branch.position.set(3.6, 2.85, 0);
    branch.castShadow = true;
    this.pipesGroup.add(branch);
    this.interactiveMeshes.push(branch);

    const branchElbow = new THREE.Mesh(elbowGeo, pipeMat);
    branchElbow.position.set(3.6, 2.85, -2.36);
    branchElbow.rotation.x = -Math.PI / 2;
    this.pipesGroup.add(branchElbow);
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

    const trayMat = this.register(
      new THREE.MeshStandardMaterial({
        color: 0x334155,
        roughness: 0.7,
        metalness: 0.45,
      })
    );

    // Cable tray channel running along the back wall — the conduits sit inside it
    const tray = new THREE.Mesh(
      new THREE.BoxGeometry(11, 0.05, 0.4),
      trayMat
    );
    tray.position.set(0, 3.16, -5.7);
    tray.castShadow = true;
    this.conduitsGroup.add(tray);
    this.interactiveMeshes.push(tray);

    // Tray side rails
    for (const zOff of [-0.18, 0.18]) {
      const rail = new THREE.Mesh(
        new THREE.BoxGeometry(11, 0.14, 0.03),
        trayMat
      );
      rail.position.set(0, 3.23, -5.7 + zOff);
      this.conduitsGroup.add(rail);
    }

    // Tray rung ladders
    for (let i = -5; i <= 5; i += 0.5) {
      const rung = new THREE.Mesh(
        new THREE.BoxGeometry(0.03, 0.02, 0.34),
        trayMat
      );
      rung.position.set(i, 3.19, -5.7);
      this.conduitsGroup.add(rung);
    }

    // Multi-run electrical conduit pipes riding on top of the cable tray
    for (let i = 0; i < 4; i++) {
      const yPos = 3.28 + i * 0.06;
      const conduit = new THREE.Mesh(
        new THREE.CylinderGeometry(0.025, 0.025, 11, 12),
        conduitMat
      );
      conduit.rotation.z = Math.PI / 2;
      conduit.position.set(0, yPos, -5.7);
      conduit.castShadow = true;
      this.conduitsGroup.add(conduit);
      this.interactiveMeshes.push(conduit);
    }

    // Junction Box on the wall
    const jBox = new THREE.Mesh(
      new THREE.BoxGeometry(0.35, 0.45, 0.15),
      boxMat
    );
    jBox.position.set(1.5, 3.3, -5.87);
    jBox.castShadow = true;
    this.conduitsGroup.add(jBox);
    this.interactiveMeshes.push(jBox);

    // Vertical conduit drops from the tray down to sockets on the floor
    for (const x of [-3, 1.5, 3.5]) {
      const drop = new THREE.Mesh(
        new THREE.CylinderGeometry(0.025, 0.025, 2.5, 12),
        conduitMat
      );
      drop.position.set(x, 2.0, -5.85);
      drop.castShadow = true;
      this.conduitsGroup.add(drop);
      this.interactiveMeshes.push(drop);

      // Elbow at the top of each drop
      const elbow = new THREE.Mesh(
        new THREE.TorusGeometry(0.08, 0.025, 8, 16, Math.PI / 2),
        conduitMat
      );
      elbow.position.set(x, 3.25, -5.79);
      elbow.rotation.z = Math.PI / 2;
      elbow.rotation.y = Math.PI / 2;
      this.conduitsGroup.add(elbow);

      // Socket box at the bottom of each drop
      const socket = new THREE.Mesh(
        new THREE.BoxGeometry(0.14, 0.18, 0.08),
        boxMat
      );
      socket.position.set(x, 0.75, -5.87);
      this.conduitsGroup.add(socket);
    }
  }

  private buildHVAC() {
    const hvacMat = this.register(
      new THREE.MeshStandardMaterial({
        color: 0x059669, // Emerald Metallic (HVAC Ductwork)
        roughness: 0.35,
        metalness: 0.7,
      })
    );
    const ventMat = this.register(
      new THREE.MeshStandardMaterial({
        color: 0x065f46,
        metalness: 0.5,
        roughness: 0.55,
      })
    );
    const bandMat = this.register(
      new THREE.MeshStandardMaterial({
        color: 0x0f766e,
        metalness: 0.55,
        roughness: 0.5,
      })
    );

    // Primary Rectangular Supply Duct (1.42 m wide — matches the measurement fixtures)
    const duct = new THREE.Mesh(
      new THREE.BoxGeometry(10, 0.65, 1.42),
      hvacMat
    );
    duct.position.set(0, 3.4, 0.8);
    duct.castShadow = true;
    this.hvacGroup.add(duct);
    this.interactiveMeshes.push(duct);

    // Flange bands at ~2 m intervals along the main duct
    for (const x of [-4, -2, 0, 2, 4]) {
      const band = new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.72, 1.5), bandMat);
      band.position.set(x, 3.4, 0.8);
      this.hvacGroup.add(band);
    }

    // Trapezoid transition piece stepping down to the branch
    const transition = new THREE.Mesh(
      new THREE.BoxGeometry(0.6, 0.55, 1.0),
      hvacMat
    );
    transition.position.set(2, 3.4, 1.9);
    transition.castShadow = true;
    this.hvacGroup.add(transition);

    // Branch takeoff duct
    const branch = new THREE.Mesh(
      new THREE.BoxGeometry(0.55, 0.5, 3),
      hvacMat
    );
    branch.position.set(2, 3.4, 3.5);
    branch.castShadow = true;
    this.hvacGroup.add(branch);
    this.interactiveMeshes.push(branch);

    // Three diffusers along the branch — proper diffuser plates + collars
    for (const z of [2.5, 3.5, 4.5]) {
      const collar = new THREE.Mesh(
        new THREE.CylinderGeometry(0.15, 0.15, 0.12, 20),
        hvacMat
      );
      collar.position.set(2, 3.12, z);
      collar.castShadow = true;
      this.hvacGroup.add(collar);

      const plate = new THREE.Mesh(
        new THREE.BoxGeometry(0.55, 0.04, 0.55),
        ventMat
      );
      plate.position.set(2, 3.03, z);
      plate.castShadow = true;
      this.hvacGroup.add(plate);
      this.interactiveMeshes.push(plate);

      // Louvered fins on the diffuser plate
      for (let i = -2; i <= 2; i++) {
        const fin = new THREE.Mesh(
          new THREE.BoxGeometry(0.5, 0.008, 0.04),
          bandMat
        );
        fin.position.set(2, 3.03, z + i * 0.09);
        this.hvacGroup.add(fin);
      }
    }

    // Return grille on the left of the main duct
    const returnGrille = new THREE.Mesh(
      new THREE.BoxGeometry(0.8, 0.04, 0.8),
      ventMat
    );
    returnGrille.position.set(-3.5, 3.05, 0.8);
    this.hvacGroup.add(returnGrille);
    for (let i = -3; i <= 3; i++) {
      const fin = new THREE.Mesh(
        new THREE.BoxGeometry(0.72, 0.008, 0.05),
        bandMat
      );
      fin.position.set(-3.5, 3.05, 0.8 + i * 0.11);
      this.hvacGroup.add(fin);
    }
  }

  private buildFireSprinklers() {
    const fireMat = this.register(
      new THREE.MeshStandardMaterial({
        color: 0xdc2626, // Red
        roughness: 0.3,
        metalness: 0.6,
      })
    );

    const brassMat = this.register(
      new THREE.MeshStandardMaterial({
        color: 0xf59e0b,
        roughness: 0.35,
        metalness: 0.8,
      })
    );

    // Main line
    const firePipe = new THREE.Mesh(
      new THREE.CylinderGeometry(0.05, 0.05, 10, 20),
      fireMat
    );
    firePipe.rotation.x = Math.PI / 2;
    firePipe.position.set(-3.5, 3.65, 0);
    firePipe.castShadow = true;
    this.fireGroup.add(firePipe);
    this.interactiveMeshes.push(firePipe);

    // Support brackets clamping the line up to a tie beam
    for (const z of [-3.5, -0.5, 2.5]) {
      const rod = new THREE.Mesh(
        new THREE.CylinderGeometry(0.012, 0.012, 0.25, 8),
        new THREE.MeshStandardMaterial({ color: 0x475569, metalness: 0.6 })
      );
      rod.position.set(-3.5, 3.85, z);
      this.fireGroup.add(rod);
    }

    // Sprinkler drop-heads — cylinder body + deflector plate
    for (let z = -4; z <= 4; z += 1.6) {
      // Threaded body drops from the main line
      const body = new THREE.Mesh(
        new THREE.CylinderGeometry(0.03, 0.028, 0.14, 12),
        brassMat
      );
      body.position.set(-3.5, 3.53, z);
      body.castShadow = true;
      this.fireGroup.add(body);
      this.interactiveMeshes.push(body);

      // Deflector plate (the little red disc under the head)
      const deflector = new THREE.Mesh(
        new THREE.CylinderGeometry(0.06, 0.06, 0.008, 16),
        fireMat
      );
      deflector.position.set(-3.5, 3.45, z);
      this.fireGroup.add(deflector);

      // Fusible link nub
      const bulb = new THREE.Mesh(
        new THREE.SphereGeometry(0.018, 10, 10),
        fireMat
      );
      bulb.position.set(-3.5, 3.47, z);
      this.fireGroup.add(bulb);
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

