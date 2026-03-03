const CACHE_NAME = 'tunestreamx-v1';

self.addEventListener('install', event => {
  console.log('TuneStreamX Service Worker installed');
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  console.log('TuneStreamX Service Worker activated');
  event.waitUntil(clients.claim());
});

self.addEventListener('fetch', event => {
  event.respondWith(fetch(event.request));
});