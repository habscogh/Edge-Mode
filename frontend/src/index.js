import React from "react";
import ReactDOM from "react-dom/client";
import "@/index.css";
import App from "@/App";
import { ThemeProvider } from "@/context/ThemeContext";

// Register Service Worker for PWA features
if (typeof window !== 'undefined' && 'serviceWorker' in navigator) {
  window.addEventListener('load', async () => {
    try {
      const registration = await navigator.serviceWorker.register('/sw.js', {
        scope: '/',
        updateViaCache: 'none'
      });
      
      console.log('[App] Service Worker registered:', registration.scope);
      
      // Check for updates periodically
      registration.addEventListener('updatefound', () => {
        const newWorker = registration.installing;
        console.log('[App] New Service Worker installing...');
        
        newWorker.addEventListener('statechange', () => {
          if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
            console.log('[App] New content available, refresh to update');
          }
        });
      });

      // Request periodic sync permission (for background updates)
      if ('periodicSync' in registration) {
        try {
          await registration.periodicSync.register('update-content', {
            minInterval: 24 * 60 * 60 * 1000 // 24 hours
          });
          console.log('[App] Periodic sync registered');
        } catch (e) {
          console.log('[App] Periodic sync not supported');
        }
      }

    } catch (error) {
      console.error('[App] Service Worker registration failed:', error);
    }
  });
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <ThemeProvider>
      <App />
    </ThemeProvider>
  </React.StrictMode>,
);
