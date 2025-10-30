const CACHE_NAME = 'ekam-cache-v5';  // Updated cache version
const OFFLINE_URL = '/static/offline.html';
const CACHEABLE_PATHS = [
  '/',
  '/static/css/style.css',
  '/static/js/main.js',
  '/static/manifest.json',
  '/static/browserconfig.xml',
  // Icons
  '/static/icons/favicon-16.png',
  '/static/icons/favicon-32.png',
  '/static/icons/apple-touch-icon.png',
  '/static/icons/icon-192.png',
  '/static/icons/icon-512.png',
  '/static/icons/icon-512-maskable.png',
  // Core pages
  '/login',
  '/register',
  '/properties',
  '/a-propos',
  '/licence',
  // Fallback images
  '/static/images/no-image.jpg',
  // API endpoints
  '/api/properties'
];

// Assets to precache
const PRECACHE_ASSETS = [
  '/',
  '/static/css/style.css',
  '/static/js/main.js',
  '/static/manifest.json',
  '/static/browserconfig.xml',
  OFFLINE_URL,
  // Icons
  '/static/icons/favicon-16.png',
  '/static/icons/favicon-32.png',
  '/static/icons/apple-touch-icon.png',
  '/static/icons/icon-192.png',
  '/static/icons/icon-512.png',
  '/static/icons/icon-512-maskable.png',
  // Core pages
  '/login',
  '/register',
  '/properties',
  '/a-propos',
  '/licence',
  // API endpoints
  '/api/properties',
  // Fallback images
  '/static/images/no-image.jpg'
];

self.addEventListener('install', (event) => {
  console.log('[Service Worker] Install');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('[Service Worker] Caching app shell and content');
        return cache.addAll(CACHEABLE_PATHS);
      })
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  console.log('[Service Worker] Activate');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cache) => {
          if (cache !== CACHE_NAME) {
            console.log('[Service Worker] Removing old cache', cache);
            return caches.delete(cache);
          }
        })
      );
    }).then(() => {
      console.log('[Service Worker] Claiming clients');
      return self.clients.claim();
    })
  );
});

// Network with cache fallback, and offline fallback for navigations
self.addEventListener('fetch', (event) => {
  const request = event.request;
  const url = new URL(request.url);
  
  // Skip non-GET requests and chrome-extension URLs
  if (request.method !== 'GET' || url.protocol === 'chrome-extension:') {
    return;
  }

  // Handle navigation requests
  if (request.mode === 'navigate') {
    event.respondWith(
      fetch(request)
        .then((response) => {
          // Don't cache error responses
          if (!response || response.status !== 200 || response.type !== 'basic') {
            return response;
          }
          
          // Clone the response and cache it
          const responseToCache = response.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(request, responseToCache);
          });
          
          return response;
        })
        .catch(async () => {
          // If fetch fails, try to serve from cache
          const cachedResponse = await caches.match(request);
          return cachedResponse || caches.match(OFFLINE_URL);
        })
    );
    return;
  }

  // For other requests: cache-first, then network
  event.respondWith(
    caches.match(request)
      .then((cachedResponse) => {
        // Return cached response if found
        if (cachedResponse) {
          console.log('[Service Worker] Returning cached response for:', request.url);
          return cachedResponse;
        }
        
        // Otherwise, fetch from network
        return fetch(request)
          .then((response) => {
            // Don't cache error responses or non-GET requests
            if (!response || response.status !== 200 || response.type !== 'basic') {
              return response;
            }
            
            // Clone the response and cache it
            const responseToCache = response.clone();
            caches.open(CACHE_NAME).then((cache) => {
              console.log('[Service Worker] Caching new response for:', request.url);
              cache.put(request, responseToCache);
            });
            
            return response;
          })
          .catch((error) => {
            console.error('[Service Worker] Fetch failed; returning offline page', error);
            if (request.headers.get('accept').includes('text/html')) {
              return caches.match(OFFLINE_URL);
            }
          });
      })
  );
});
