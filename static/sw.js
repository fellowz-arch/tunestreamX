self.addEventListener("install", event => {
  console.log("TuneStreamX Service Worker installed");
});

self.addEventListener("fetch", event => {
  event.respondWith(fetch(event.request));
});