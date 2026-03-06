import React, { useState, useEffect } from 'react';
import { Wifi, WifiOff, RefreshCw, Check, AlertCircle, Cloud, CloudOff } from 'lucide-react';
import { useOfflineSync } from '../hooks/useOfflineSync';

// Floating status indicator (shows in corner of screen)
export function OfflineIndicator() {
  const { isOnline, pendingCount, isSyncing } = useOfflineSync();
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState('');
  const [wasOffline, setWasOffline] = useState(false);

  useEffect(() => {
    if (!isOnline) {
      setWasOffline(true);
      setToastMessage("You're offline. Sessions will be saved locally.");
      setShowToast(true);
    } else if (wasOffline && isOnline) {
      setToastMessage("Back online! Syncing your sessions...");
      setShowToast(true);
      setWasOffline(false);
    }

    if (showToast) {
      const timer = setTimeout(() => setShowToast(false), 4000);
      return () => clearTimeout(timer);
    }
  }, [isOnline, wasOffline, showToast]);

  // Don't show anything if online and no pending
  if (isOnline && pendingCount === 0 && !showToast) {
    return null;
  }

  return (
    <>
      {/* Floating indicator */}
      {(!isOnline || pendingCount > 0) && (
        <div className="fixed top-4 right-4 z-50 flex items-center gap-2">
          {!isOnline && (
            <div className="flex items-center gap-2 px-3 py-2 bg-amber-500/20 border border-amber-500/50 rounded-full text-amber-400 text-sm">
              <WifiOff className="w-4 h-4" />
              <span>Offline</span>
            </div>
          )}
          
          {pendingCount > 0 && (
            <div className={`flex items-center gap-2 px-3 py-2 rounded-full text-sm ${
              isSyncing 
                ? 'bg-blue-500/20 border border-blue-500/50 text-blue-400' 
                : 'bg-zinc-800 border border-zinc-700 text-zinc-300'
            }`}>
              {isSyncing ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Syncing...</span>
                </>
              ) : (
                <>
                  <CloudOff className="w-4 h-4" />
                  <span>{pendingCount} pending</span>
                </>
              )}
            </div>
          )}
        </div>
      )}

      {/* Toast notification */}
      {showToast && (
        <div className="fixed top-16 right-4 z-50 animate-slide-in">
          <div className={`flex items-center gap-3 px-4 py-3 rounded-xl shadow-lg ${
            isOnline 
              ? 'bg-emerald-500/20 border border-emerald-500/50 text-emerald-400' 
              : 'bg-amber-500/20 border border-amber-500/50 text-amber-400'
          }`}>
            {isOnline ? (
              <Wifi className="w-5 h-5" />
            ) : (
              <WifiOff className="w-5 h-5" />
            )}
            <span className="text-sm">{toastMessage}</span>
          </div>
        </div>
      )}
    </>
  );
}

// Sync status card (for profile/settings page)
export function SyncStatusCard() {
  const { isOnline, pendingCount, isSyncing, lastSyncResult, syncNow } = useOfflineSync();
  const [showDetails, setShowDetails] = useState(false);

  return (
    <div className="bg-zinc-800/50 rounded-xl p-4 border border-zinc-700/50">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
            isOnline ? 'bg-emerald-500/20' : 'bg-amber-500/20'
          }`}>
            {isOnline ? (
              <Cloud className="w-5 h-5 text-emerald-400" />
            ) : (
              <CloudOff className="w-5 h-5 text-amber-400" />
            )}
          </div>
          <div>
            <h3 className="font-medium text-white">Sync Status</h3>
            <p className="text-sm text-zinc-400">
              {isOnline ? 'Connected' : 'Offline mode'}
              {pendingCount > 0 && ` • ${pendingCount} pending`}
            </p>
          </div>
        </div>

        {pendingCount > 0 && isOnline && (
          <button
            onClick={syncNow}
            disabled={isSyncing}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors text-sm font-medium ${
              isSyncing 
                ? 'bg-zinc-700 text-zinc-400' 
                : 'bg-emerald-500 hover:bg-emerald-600 text-white'
            }`}
          >
            <RefreshCw className={`w-4 h-4 ${isSyncing ? 'animate-spin' : ''}`} />
            {isSyncing ? 'Syncing...' : 'Sync Now'}
          </button>
        )}
      </div>

      {/* Status details */}
      {(pendingCount > 0 || lastSyncResult) && (
        <div className="mt-4 pt-4 border-t border-zinc-700/50">
          {pendingCount > 0 && (
            <div className="flex items-center gap-2 text-sm text-amber-400 mb-2">
              <AlertCircle className="w-4 h-4" />
              <span>{pendingCount} session{pendingCount !== 1 ? 's' : ''} waiting to sync</span>
            </div>
          )}

          {lastSyncResult && (
            <div className="flex items-center gap-2 text-sm text-zinc-400">
              <Check className="w-4 h-4 text-emerald-400" />
              <span>
                Last sync: {lastSyncResult.synced} synced
                {lastSyncResult.failed > 0 && `, ${lastSyncResult.failed} failed`}
              </span>
            </div>
          )}
        </div>
      )}

      {/* Info about offline mode */}
      <div className="mt-4 pt-4 border-t border-zinc-700/50">
        <div className="flex items-start gap-2 text-sm text-zinc-500">
          <CloudOff className="w-4 h-4 flex-shrink-0 mt-0.5" />
          <p>Sessions logged while offline are saved locally and automatically synced when you're back online.</p>
        </div>
      </div>
    </div>
  );
}

export default OfflineIndicator;
