// PLY splat -> compressed .spz with Spark's own encoder (~12x smaller, same rendering).
// Run from prototype/web-ui (uses its @sparkjsdev/spark): node ../../src/arcore3dgs/to_spz.mjs in.ply out.spz [maxSh] [opacityThreshold]
import { readFileSync, writeFileSync } from "node:fs";
import { pathToFileURL } from "node:url";
const spark = await import(pathToFileURL(process.cwd() + "/node_modules/@sparkjsdev/spark/dist/spark.module.js").href);
const [inp, out, maxSh = "3", thr = "0"] = process.argv.slice(2);
const t0 = Date.now();
const r = await spark.transcodeSpz({ inputs: [{ fileBytes: new Uint8Array(readFileSync(inp)), pathOrUrl: inp }], maxSh: +maxSh, opacityThreshold: +thr });
writeFileSync(out, r.fileBytes);
console.log(`${inp} -> ${out}: ${(r.fileBytes.length / 1e6).toFixed(1)} MB in ${((Date.now() - t0) / 1000).toFixed(1)} s`);
