// Service Worker for Offline Availability across devices (CleanUrls + Chromium Redirect-Safe v2)
const CACHE_NAME = 'mikel-cv-v2';
const PRECACHE_URLS = [
  '/',
  '/cv',
  '/portfolio',
  '/bot',
  '/cockpit',
  '/equipo',
  '/salita',
  '/aura-nav-interactive.js',
  '/aura-nav-interactive.css',
  '/cv_mikel_irastorza.pdf',
  '/qr-cv.png',
  '/apple-touch-icon.png',
  '/manifest.json'
];

// Reconstructs redirected responses so Chromium never throws ERR_FAILED on navigate requests
async function cleanRedirectedResponse(response) {
  if (!response || !response.redirected) {
    return response;
  }
  const body = await response.blob();
  return new Response(body, {
    status: response.status,
    statusText: response.statusText,
    headers: response.headers
  });
}

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(async (cache) => {
      await Promise.all(
        PRECACHE_URLS.map(async (url) => {
          try {
            const raw = await fetch(url, { redirect: 'follow' });
            if (raw && raw.ok) {
              const clean = await cleanRedirectedResponse(raw);
              await cache.put(url, clean);
            }
          } catch (_) {
            // Ignore transient offline errors during precache
          }
        })
      );
    }).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return;

  // Normalize .html navigation requests to clean URLs when on same origin
  const reqUrl = new URL(event.request.url);
  const isSameOrigin = reqUrl.origin === self.location.origin;

  event.respondWith(
    (async () => {
      const cachedResponse = await caches.match(event.request);
      if (cachedResponse && !cachedResponse.redirected) {
        // Refresh cache in background
        fetch(event.request.url, { redirect: 'follow' })
          .then(cleanRedirectedResponse)
          .then((netRes) => {
            if (netRes && netRes.status === 200) {
              caches.open(CACHE_NAME).then((cache) => cache.put(event.request, netRes));
            }
          })
          .catch(() => {});
        return cachedResponse;
      }

      try {
        const fetchTarget = isSameOrigin ? event.request.url : event.request;
        const networkResponse = await fetch(fetchTarget, { redirect: 'follow' });
        const safeResponse = await cleanRedirectedResponse(networkResponse);
        if (safeResponse && safeResponse.status === 200 && isSameOrigin) {
          const cache = await caches.open(CACHE_NAME);
          cache.put(event.request, safeResponse.clone()).catch(() => {});
        }
        return safeResponse;
      } catch (_) {
        if (event.request.headers.get('accept')?.includes('text/html')) {
          const fallback = await caches.match('/cv');
          if (fallback) return cleanRedirectedResponse(fallback);
        }
        return new Response('Sin conexion temporal', {
          status: 503,
          headers: { 'Content-Type': 'text/plain; charset=utf-8' }
        });
      }
    })()
  );
});
