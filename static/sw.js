/* TZStudies Service Worker */

const CACHE_NAME = 'tzstudies-v1';

// Static assets to cache immediately when SW installs
const PRECACHE_URLS = [
  '/',
  '/static/css/styles.css',
  '/static/js/script.js',
  '/static/tutors/tzstudies.png',
  '/offline'
];

// Install — precache core assets
self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.open(CACHE_NAME).then(function(cache) {
      return cache.addAll(PRECACHE_URLS);
    }).then(function() {
      return self.skipWaiting();
    })
  );
});

// Activate — delete old caches
self.addEventListener('activate', function(event) {
  event.waitUntil(
    caches.keys().then(function(cacheNames) {
      return Promise.all(
        cacheNames
          .filter(function(name) { return name !== CACHE_NAME; })
          .map(function(name) { return caches.delete(name); })
      );
    }).then(function() {
      return self.clients.claim();
    })
  );
});

// Fetch — serve from cache when possible
self.addEventListener('fetch', function(event) {
  // Skip non-GET requests and browser extensions
  if (event.request.method !== 'GET') return;
  if (!event.request.url.startsWith(self.location.origin)) return;

  // Skip admin routes — always fetch fresh
  if (event.request.url.includes('/admin')) return;

  // Skip PDF downloads — don't cache large files
  if (event.request.url.includes('/download')) return;

  // For HTML pages: network first, fall back to cache, then offline page
  if (event.request.headers.get('accept') &&
      event.request.headers.get('accept').includes('text/html')) {
    event.respondWith(
      fetch(event.request)
        .then(function(response) {
          // Cache a copy of the page
          var copy = response.clone();
          caches.open(CACHE_NAME).then(function(cache) {
            cache.put(event.request, copy);
          });
          return response;
        })
        .catch(function() {
          return caches.match(event.request).then(function(cached) {
            return cached || caches.match('/offline');
          });
        })
    );
    return;
  }

  // For static assets: cache first, fall back to network
  event.respondWith(
    caches.match(event.request).then(function(cached) {
      return cached || fetch(event.request).then(function(response) {
        var copy = response.clone();
        caches.open(CACHE_NAME).then(function(cache) {
          cache.put(event.request, copy);
        });
        return response;
      });
    })
  );
});
