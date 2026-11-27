// Viewer load and frame-time test through the Chrome DevTools protocol (GPU rendering, headless Chrome, ANGLE D3D11).
// node scripts/viewer_perf.mjs <url> <label> [loadTimeoutS]   (a viewer server must be running; screenshots to $PERF_OUT, else next to this file)
// Phases: load (until the "Loading Gaussian splat scan" pill is gone), idle 4 s, drag-look 6 s, hover 4 s.
// Reports frame intervals (median / p95 / max ms), frames > 50 ms, long tasks, WebGL renderer, context losses.
import { spawn } from "node:child_process";
import { mkdtempSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const [url, label = "run", loadTimeout = "180"] = process.argv.slice(2);
const CHROME = "C:/Program Files/Google/Chrome/Application/chrome.exe";
const port = 9300 + Math.floor(Math.random() * 500);
const prof = mkdtempSync(join(tmpdir(), "vperf-"));
const chrome = spawn(CHROME, [`--remote-debugging-port=${port}`, `--user-data-dir=${prof}`, "--headless=new",
  "--window-size=1600,900", "--use-angle=d3d11", "--enable-gpu", "--ignore-gpu-blocklist", "--no-first-run",
  "--disable-background-timer-throttling", "--disable-renderer-backgrounding", "about:blank"], { stdio: "ignore" });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let ws, id = 0; const pending = new Map(); const events = [];
async function connect() {
  for (let i = 0; i < 50; i++) {
    try { const l = await (await fetch(`http://127.0.0.1:${port}/json`)).json(); const p = l.find((t) => t.type === "page"); if (p) return p.webSocketDebuggerUrl; } catch {}
    await sleep(200);
  }
  throw new Error("no chrome");
}
const send = (method, params = {}) => new Promise((res, rej) => { const i = ++id; pending.set(i, { res, rej }); ws.send(JSON.stringify({ id: i, method, params })); });
const evalJs = async (expr) => { const r = await send("Runtime.evaluate", { expression: expr, awaitPromise: true, returnByValue: true }); return r.result?.value; };
try {
  ws = new WebSocket(await connect());
  await new Promise((r) => (ws.onopen = r));
  ws.onmessage = (m) => { const d = JSON.parse(m.data); if (d.id && pending.has(d.id)) { const p = pending.get(d.id); pending.delete(d.id); d.error ? p.rej(new Error(d.error.message)) : p.res(d.result); } else if (d.method) events.push(d); };
  await send("Page.enable"); await send("Runtime.enable");
  await send("Page.addScriptToEvaluateOnNewDocument", { source: `
    window.__perf = { frames: [], long: [], lost: 0 };
    (function loop(){ requestAnimationFrame((t)=>{ window.__perf.frames.push(t); loop(); }); })();
    try { new PerformanceObserver((l)=>{ for (const e of l.getEntries()) window.__perf.long.push([e.startTime, e.duration]); }).observe({ entryTypes: ["longtask"] }); } catch {}
    document.addEventListener("webglcontextlost", ()=>window.__perf.lost++, true);
  ` });
  const t0 = Date.now();
  await send("Page.navigate", { url });
  let loaded = false;
  while ((Date.now() - t0) / 1000 < +loadTimeout) {
    await sleep(500);
    const st = await evalJs(`(() => { const b = document.body?.innerText || ""; return { loading: /Loading Gaussian splat scan|Loading scan…/.test(b), err: /Could not load/.test(b), canvas: !!document.querySelector("canvas") }; })()`);
    if (st?.err) { console.log(label, "load error"); break; }
    if (st && st.canvas && !st.loading) { loaded = true; break; }
  }
  const loadS = (Date.now() - t0) / 1000;
  const gl = await evalJs(`(() => { const c = document.createElement("canvas").getContext("webgl2"); const e = c && c.getExtension("WEBGL_debug_renderer_info"); return e ? c.getParameter(e.UNMASKED_RENDERER_WEBGL) : "?"; })()`);
  const stats = async (name, ms, action) => {
    await evalJs(`(window.__perf.frames = [], window.__perf.long = [], 0)`);
    const end = Date.now() + ms;
    if (action) await action(end); else await sleep(ms);
    const r = await evalJs(`(() => { const f = window.__perf.frames; const d = []; for (let i = 1; i < f.length; i++) d.push(f[i] - f[i-1]); d.sort((a,b)=>a-b);
      const q = (p) => d.length ? d[Math.min(d.length-1, Math.floor(p*d.length))] : 0;
      return { n: d.length, med: q(0.5), p95: q(0.95), max: d[d.length-1] || 0, over50: d.filter(x=>x>50).length, longN: window.__perf.long.length, longMs: Math.round(window.__perf.long.reduce((s,e)=>s+e[1],0)), lost: window.__perf.lost }; })()`);
    console.log(`${label.padEnd(18)} ${name.padEnd(6)} frames ${String(r.n).padStart(4)}  median ${r.med.toFixed(1)} ms  p95 ${r.p95.toFixed(1)}  max ${r.max.toFixed(0)}  >50ms ${r.over50}  long tasks ${r.longN} (${r.longMs} ms)  ctx lost ${r.lost}`);
    return r;
  };
  console.log(`${label}: loaded=${loaded} in ${loadS.toFixed(1)} s, GPU: ${gl}`);
  if (loaded) {
    await sleep(3000);
    await stats("idle", 4000);
    await stats("drag", 6000, async (end) => {
      let x = 600, dir = 1;
      await send("Input.dispatchMouseEvent", { type: "mouseMoved", x, y: 450 });
      await send("Input.dispatchMouseEvent", { type: "mousePressed", x, y: 450, button: "left", buttons: 1, clickCount: 1 });
      while (Date.now() < end) { x += 12 * dir; if (x > 1100 || x < 500) dir = -dir; await send("Input.dispatchMouseEvent", { type: "mouseMoved", x, y: 450, button: "left", buttons: 1 }); await sleep(16); }
      await send("Input.dispatchMouseEvent", { type: "mouseReleased", x, y: 450, button: "left", buttons: 0, clickCount: 1 });
    });
    await stats("hover", 4000, async (end) => {
      let x = 500; while (Date.now() < end) { x = 500 + ((x - 500 + 9) % 600); await send("Input.dispatchMouseEvent", { type: "mouseMoved", x, y: 420, buttons: 0 }); await sleep(16); }
    });
    const shot = await send("Page.captureScreenshot", { format: "jpeg", quality: 70 });
    writeFileSync(join(process.env.PERF_OUT || join(process.argv[1], ".."), `perf_${label}.jpg`), Buffer.from(shot.data, "base64"));
  }
} catch (e) { console.log(label, "ERROR", e.message); }
finally { try { ws?.close(); } catch {} chrome.kill(); }
