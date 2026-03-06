// Edge Mode Service Worker for Push Notifications
const CACHE_NAME = 'edge-mode-v1';

// Handle push events
self.addEventListener('push', function(event) {
  console.log('[SW] Push received:', event);
  
  let data = {
    title: 'Edge Mode',
    body: 'You have a new notification',
    icon: '/logo192.png',
    badge: '/badge.png',
    url: '/dashboard'
  };
  
  if (event.data) {
    try {
      data = { ...data, ...event.data.json() };
    } catch (e) {
      console.error('[SW] Error parsing push data:', e);
    }
  }
  
  const options = {
    body: data.body,
    icon: data.icon || '/logo192.png',
    badge: data.badge || '/badge.png',
    vibrate: [100, 50, 100],
    data: {
      url: data.url || '/dashboard',
      timestamp: data.timestamp || new Date().toISOString()
    },
    tag: data.tag || 'default',
    renotify: true,
    requireInteraction: false,
    actions: [
      { action: 'open', title: 'Open' },
      { action: 'dismiss', title: 'Dismiss' }
    ]
  };
  
  event.waitUntil(
    self.registration.showNotification(data.title, options)
  );
});

// Handle notification clicks
self.addEventListener('notificationclick', function(event) {
  console.log('[SW] Notification click:', event.action);
  
  event.notification.close();
  
  if (event.action === 'dismiss') {
    return;
  }
  
  const urlToOpen = event.notification.data?.url || '/dashboard';
  
  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true })
      .then(function(clientList) {
        // Check if there's already a window open
        for (let client of clientList) {
          if (client.url.includes(self.location.origin) && 'focus' in client) {
            client.navigate(urlToOpen);
            return client.focus();
          }
        }
        // Open a new window
        if (clients.openWindow) {
          return clients.openWindow(urlToOpen);
        }
      })
  );
});

// Handle notification close
self.addEventListener('notificationclose', function(event) {
  console.log('[SW] Notification closed');
});

// Service worker activation
self.addEventListener('activate', function(event) {
  console.log('[SW] Activated');
  event.waitUntil(self.clients.claim());
});

// Service worker installation
self.addEventListener('install', function(event) {
  console.log('[SW] Installed');
  self.skipWaiting();
});
