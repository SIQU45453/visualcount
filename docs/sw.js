// VisualCount offline helper:
// 1) keeps the app and the AI model on the phone so it works without internet,
// 2) adds the two security headers that let the AI use several CPU cores (faster counting).
const APP = "vc-app-v1", MODEL = "vc-model-v1";
const SHELL = ["./", "index.html", "manifest.webmanifest", "icon-192.png", "icon-512.png",
  "vendor/ort.wasm.min.js", "vendor/ort-wasm-simd-threaded.mjs", "vendor/ort-wasm-simd-threaded.wasm", "vendor/xlsx.full.min.js"];

self.addEventListener("install", e => { e.waitUntil(caches.open(APP).then(c => c.addAll(SHELL)).then(() => self.skipWaiting())); });
self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== APP && k !== MODEL).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});

function isolate(r) {
  if (!r || r.status === 0 || r.type === "opaque") return r;
  const h = new Headers(r.headers);
  h.set("Cross-Origin-Embedder-Policy", "require-corp");
  h.set("Cross-Origin-Opener-Policy", "same-origin");
  return new Response(r.body, { status: r.status, statusText: r.statusText, headers: h });
}

self.addEventListener("fetch", e => {
  const req = e.request, url = new URL(req.url);
  if (req.method !== "GET" || url.origin !== location.origin) return;
  const isModel = url.pathname.endsWith(".onnx");
  const isPage = req.mode === "navigate" || url.pathname.endsWith("/") || url.pathname.endsWith("index.html");
  e.respondWith((async () => {
    if (isPage) { // newest page when online, saved page when offline
      try { const r = await fetch(req); if (r.ok) (await caches.open(APP)).put(req, r.clone()); return isolate(r); }
      catch (err) { return isolate(await caches.match(req) || await caches.match("index.html")); }
    }
    const hit = await caches.match(req);
    if (hit) return isolate(hit);
    const r = await fetch(req);
    if (r.ok) (await caches.open(isModel ? MODEL : APP)).put(req, r.clone());
    return isolate(r);
  })());
});
