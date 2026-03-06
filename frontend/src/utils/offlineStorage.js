/**
 * Offline Storage Manager using IndexedDB
 * Handles storing and syncing sessions when offline
 */

const DB_NAME = 'EdgeModeOffline';
const DB_VERSION = 1;
const STORE_NAME = 'pendingSessions';

class OfflineStorage {
  constructor() {
    this.db = null;
    this.isOnline = navigator.onLine;
    this.syncInProgress = false;
    this.listeners = new Set();
    
    // Listen for online/offline events
    window.addEventListener('online', () => this.handleOnline());
    window.addEventListener('offline', () => this.handleOffline());
  }

  async init() {
    if (this.db) return this.db;

    return new Promise((resolve, reject) => {
      const request = indexedDB.open(DB_NAME, DB_VERSION);

      request.onerror = () => reject(request.error);
      request.onsuccess = () => {
        this.db = request.result;
        resolve(this.db);
      };

      request.onupgradeneeded = (event) => {
        const db = event.target.result;
        
        // Create store for pending sessions
        if (!db.objectStoreNames.contains(STORE_NAME)) {
          const store = db.createObjectStore(STORE_NAME, { keyPath: 'localId' });
          store.createIndex('timestamp', 'timestamp', { unique: false });
          store.createIndex('synced', 'synced', { unique: false });
        }
      };
    });
  }

  handleOnline() {
    this.isOnline = true;
    this.notifyListeners({ type: 'online' });
    // Auto-sync when coming back online
    this.syncPendingSessions();
  }

  handleOffline() {
    this.isOnline = false;
    this.notifyListeners({ type: 'offline' });
  }

  addListener(callback) {
    this.listeners.add(callback);
    return () => this.listeners.delete(callback);
  }

  notifyListeners(event) {
    this.listeners.forEach(callback => callback(event));
  }

  /**
   * Save a session for offline sync
   */
  async saveOfflineSession(sessionData) {
    await this.init();

    const offlineSession = {
      localId: `offline_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      ...sessionData,
      timestamp: new Date().toISOString(),
      synced: false,
      retryCount: 0
    };

    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([STORE_NAME], 'readwrite');
      const store = transaction.objectStore(STORE_NAME);
      const request = store.add(offlineSession);

      request.onsuccess = () => {
        this.notifyListeners({ type: 'sessionSaved', session: offlineSession });
        resolve(offlineSession);
      };
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Get all pending (unsynced) sessions
   */
  async getPendingSessions() {
    await this.init();

    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([STORE_NAME], 'readonly');
      const store = transaction.objectStore(STORE_NAME);
      const request = store.getAll();

      request.onsuccess = () => {
        // Filter for unsynced sessions (synced === false)
        const pendingSessions = request.result.filter(session => session.synced === false);
        resolve(pendingSessions);
      };
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Get count of pending sessions
   */
  async getPendingCount() {
    const sessions = await this.getPendingSessions();
    return sessions.length;
  }

  /**
   * Mark a session as synced
   */
  async markAsSynced(localId) {
    await this.init();

    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([STORE_NAME], 'readwrite');
      const store = transaction.objectStore(STORE_NAME);
      const getRequest = store.get(localId);

      getRequest.onsuccess = () => {
        const session = getRequest.result;
        if (session) {
          session.synced = true;
          session.syncedAt = new Date().toISOString();
          const updateRequest = store.put(session);
          updateRequest.onsuccess = () => resolve(session);
          updateRequest.onerror = () => reject(updateRequest.error);
        } else {
          resolve(null);
        }
      };
      getRequest.onerror = () => reject(getRequest.error);
    });
  }

  /**
   * Delete a synced session
   */
  async deleteSession(localId) {
    await this.init();

    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([STORE_NAME], 'readwrite');
      const store = transaction.objectStore(STORE_NAME);
      const request = store.delete(localId);

      request.onsuccess = () => resolve(true);
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Clear all synced sessions
   */
  async clearSyncedSessions() {
    await this.init();
    
    const transaction = this.db.transaction([STORE_NAME], 'readwrite');
    const store = transaction.objectStore(STORE_NAME);
    const index = store.index('synced');
    const request = index.openCursor(IDBKeyRange.only(true));

    return new Promise((resolve, reject) => {
      request.onsuccess = (event) => {
        const cursor = event.target.result;
        if (cursor) {
          cursor.delete();
          cursor.continue();
        } else {
          resolve(true);
        }
      };
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Sync all pending sessions to the server
   */
  async syncPendingSessions(token, apiUrl) {
    if (this.syncInProgress || !this.isOnline) {
      return { synced: 0, failed: 0, pending: await this.getPendingCount() };
    }

    this.syncInProgress = true;
    this.notifyListeners({ type: 'syncStart' });

    const pendingSessions = await this.getPendingSessions();
    let synced = 0;
    let failed = 0;

    for (const session of pendingSessions) {
      try {
        const response = await fetch(`${apiUrl}/api/sessions/complete`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({
            pillar: session.pillar,
            minutes_spent: session.minutes_spent,
            note: session.note,
            local_date: session.local_date
          })
        });

        if (response.ok) {
          await this.markAsSynced(session.localId);
          await this.deleteSession(session.localId);
          synced++;
          this.notifyListeners({ type: 'sessionSynced', session });
        } else {
          failed++;
          // Increment retry count
          session.retryCount = (session.retryCount || 0) + 1;
          const transaction = this.db.transaction([STORE_NAME], 'readwrite');
          transaction.objectStore(STORE_NAME).put(session);
        }
      } catch (error) {
        console.error('Failed to sync session:', error);
        failed++;
      }
    }

    this.syncInProgress = false;
    const pending = await this.getPendingCount();
    this.notifyListeners({ type: 'syncComplete', synced, failed, pending });

    // Clean up old synced sessions
    await this.clearSyncedSessions();

    return { synced, failed, pending };
  }
}

// Singleton instance
export const offlineStorage = new OfflineStorage();
export default offlineStorage;
