import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import offlineStorage from '../utils/offlineStorage';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export function useOfflineSync() {
  const { token } = useAuth();
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [pendingCount, setPendingCount] = useState(0);
  const [isSyncing, setIsSyncing] = useState(false);
  const [lastSyncResult, setLastSyncResult] = useState(null);

  // Initialize and listen for changes
  useEffect(() => {
    const initStorage = async () => {
      await offlineStorage.init();
      const count = await offlineStorage.getPendingCount();
      setPendingCount(count);
    };

    initStorage();

    // Listen for storage events
    const unsubscribe = offlineStorage.addListener((event) => {
      switch (event.type) {
        case 'online':
          setIsOnline(true);
          break;
        case 'offline':
          setIsOnline(false);
          break;
        case 'sessionSaved':
          setPendingCount(prev => prev + 1);
          break;
        case 'syncStart':
          setIsSyncing(true);
          break;
        case 'syncComplete':
          setIsSyncing(false);
          setPendingCount(event.pending);
          setLastSyncResult({
            synced: event.synced,
            failed: event.failed,
            timestamp: new Date().toISOString()
          });
          break;
        case 'sessionSynced':
          setPendingCount(prev => Math.max(0, prev - 1));
          break;
        default:
          break;
      }
    });

    return unsubscribe;
  }, []);

  // Auto-sync when online and authenticated
  useEffect(() => {
    if (isOnline && token && pendingCount > 0) {
      syncNow();
    }
  }, [isOnline, token]); // eslint-disable-line react-hooks/exhaustive-deps

  // Manual sync function
  const syncNow = useCallback(async () => {
    if (!token || !isOnline || isSyncing) return null;
    
    const result = await offlineStorage.syncPendingSessions(token, API_URL);
    return result;
  }, [token, isOnline, isSyncing]);

  // Save session offline
  const saveOffline = useCallback(async (sessionData) => {
    return await offlineStorage.saveOfflineSession(sessionData);
  }, []);

  // Get pending sessions
  const getPendingSessions = useCallback(async () => {
    return await offlineStorage.getPendingSessions();
  }, []);

  return {
    isOnline,
    pendingCount,
    isSyncing,
    lastSyncResult,
    syncNow,
    saveOffline,
    getPendingSessions
  };
}
