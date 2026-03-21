// Edge Mode Service Worker v2 - Full PWA Support
// Features: Offline, Push Notifications, Background Sync, Periodic Sync

const CACHE_NAME = 'edge-mode-v2';
const OFFLINE_URL = '/offline.html';

// Assets to cache immediately on install
const PRECACHE_ASSETS = [
  '/',
  '/index.html',
  '/manifest.json',
  '/icon-48.png',
  '/icon-96.png',
  '/icon-192.png',
  '/icon-512.png'
];

// ============================================
// INSTALL EVENT - Cache core assets
// ============================================
self.addEventListener('install', (event) => {
  console.log('[SW] Installing Service Worker v2...');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('[SW] Caching core assets');
        return cache.addAll(PRECACHE_ASSETS);
      })
      .then(() => self.skipWaiting())
  );
});

// ============================================
// ACTIVATE EVENT - Clean up old caches
// ============================================
self.addEventListener('activate', (event) => {
  console.log('[SW] Activating Service Worker v2...');
  event.waitUntil(
    Promise.all([
      // Clean old caches
      caches.keys().then((cacheNames) => {
        return Promise.all(
          cacheNames
            .filter((name) => name !== CACHE_NAME)
            .map((name) => {
              console.log('[SW] Deleting old cache:', name);
              return caches.delete(name);
            })
        );
      }),
      // Take control of all clients immediately
      self.clients.claim()
    ])
  );
});

// ============================================
// FETCH EVENT - Network-first with cache fallback
// ============================================
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET requests
  if (request.method !== 'GET') return;

  // Skip API requests - always go to network
  if (url.pathname.startsWith('/api/')) return;

  // Skip external requests
  if (url.origin !== self.location.origin) return;

  // For navigation requests (page loads)
  if (request.mode === 'navigate') {
    event.respondWith(
      fetch(request)
        .then((response) => {
          // Cache successful navigation responses
          if (response.ok) {
            const clone = response.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(request, clone));
          }
          return response;
        })
        .catch(() => {
          // Offline fallback - return cached index.html for SPA
          return caches.match('/index.html');
        })
    );
    return;
  }

  // For static assets - cache-first strategy
  if (url.pathname.match(/\.(js|css|png|jpg|jpeg|svg|ico|woff|woff2)$/)) {
    event.respondWith(
      caches.match(request).then((cachedResponse) => {
        if (cachedResponse) {
          // Return cached version and update in background
          fetch(request).then((response) => {
            if (response.ok) {
              caches.open(CACHE_NAME).then((cache) => cache.put(request, response));
            }
          });
          return cachedResponse;
        }
        // Not cached - fetch and cache
        return fetch(request).then((response) => {
          if (response.ok) {
            const clone = response.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(request, clone));
          }
          return response;
        });
      })
    );
    return;
  }

  // Default - network first with cache fallback
  event.respondWith(
    fetch(request)
      .then((response) => {
        if (response.ok) {
          const clone = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(request, clone));
        }
        return response;
      })
      .catch(() => caches.match(request))
  );
});

// ============================================
// PUSH NOTIFICATIONS
// ============================================
self.addEventListener('push', (event) => {
  console.log('[SW] Push notification received');

  let data = {
    title: 'Edge Mode',
    body: 'You have a new notification',
    icon: '/icon-192.png',
    badge: '/icon-96.png',
    url: '/dashboard'
  };

  if (event.data) {
    try {
      data = { ...data, ...event.data.json() };
    } catch (e) {
      console.error('[SW] Error parsing push data:', e);
      data.body = event.data.text();
    }
  }

  const options = {
    body: data.body,
    icon: data.icon || '/icon-192.png',
    badge: data.badge || '/icon-96.png',
    vibrate: [100, 50, 100],
    data: {
      url: data.url || '/dashboard',
      timestamp: Date.now()
    },
    tag: data.tag || 'edge-mode-notification',
    renotify: true,
    requireInteraction: false,
    actions: [
      { action: 'open', title: 'Open App' },
      { action: 'dismiss', title: 'Dismiss' }
    ]
  };

  event.waitUntil(
    self.registration.showNotification(data.title, options)
  );
});

// ============================================
// NOTIFICATION CLICK
// ============================================
self.addEventListener('notificationclick', (event) => {
  console.log('[SW] Notification clicked:', event.action);
  event.notification.close();

  if (event.action === 'dismiss') return;

  const urlToOpen = event.notification.data?.url || '/dashboard';

  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true })
      .then((clientList) => {
        // Focus existing window if available
        for (const client of clientList) {
          if (client.url.includes(self.location.origin) && 'focus' in client) {
            client.navigate(urlToOpen);
            return client.focus();
          }
        }
        // Open new window
        return clients.openWindow(urlToOpen);
      })
  );
});

// ============================================
// BACKGROUND SYNC - Retry failed requests
// ============================================
self.addEventListener('sync', (event) => {
  console.log('[SW] Background sync:', event.tag);

  if (event.tag === 'sync-sessions') {
    event.waitUntil(syncSessions());
  }
  if (event.tag === 'sync-logs') {
    event.waitUntil(syncLogs());
  }
});

async function syncSessions() {
  try {
    const cache = await caches.open('pending-requests');
    const requests = await cache.keys();
    
    for (const request of requests) {
      if (request.url.includes('/api/sessions')) {
        const cachedResponse = await cache.match(request);
        const data = await cachedResponse.json();
        
        await fetch(request, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data)
        });
        
        await cache.delete(request);
        console.log('[SW] Synced session');
      }
    }
  } catch (error) {
    console.error('[SW] Sync failed:', error);
  }
}

async function syncLogs() {
  // Similar logic for syncing logs
  console.log('[SW] Syncing logs...');
}

// ============================================
// PERIODIC BACKGROUND SYNC - Check for updates
// ============================================
self.addEventListener('periodicsync', (event) => {
  console.log('[SW] Periodic sync:', event.tag);

  if (event.tag === 'check-streaks') {
    event.waitUntil(checkStreaks());
  }
  if (event.tag === 'update-content') {
    event.waitUntil(updateContent());
  }
});

async function checkStreaks() {
  try {
    // Fetch latest streak data in background
    console.log('[SW] Checking streaks in background...');
  } catch (error) {
    console.error('[SW] Periodic sync error:', error);
  }
}

async function updateContent() {
  try {
    // Update cached content
    const cache = await caches.open(CACHE_NAME);
    await cache.add('/');
    console.log('[SW] Content updated');
  } catch (error) {
    console.error('[SW] Content update failed:', error);
  }
}

// ============================================
// MESSAGE HANDLER - Communicate with app
// ============================================
self.addEventListener('message', (event) => {
  console.log('[SW] Message received:', event.data);

  if (event.data?.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }

  if (event.data?.type === 'CACHE_URLS') {
    const urls = event.data.payload || [];
    caches.open(CACHE_NAME).then((cache) => {
      cache.addAll(urls);
    });
  }

  if (event.data?.type === 'CLEAR_CACHE') {
    caches.delete(CACHE_NAME).then(() => {
      console.log('[SW] Cache cleared');
    });
  }
});

// ============================================
// SHARE TARGET HANDLER
// ============================================
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);
  
  if (url.pathname === '/share-target' && event.request.method === 'GET') {
    event.respondWith(
      (async () => {
        const params = url.searchParams;
        const title = params.get('title') || '';
        const text = params.get('text') || '';
        const sharedUrl = params.get('url') || '';
        
        // Redirect to dashboard with shared content
        const redirectUrl = `/dashboard?shared=true&title=${encodeURIComponent(title)}&text=${encodeURIComponent(text)}&url=${encodeURIComponent(sharedUrl)}`;
        
        return Response.redirect(redirectUrl, 303);
      })()
    );
  }
});

console.log('[SW] Service Worker loaded - Edge Mode v2');
