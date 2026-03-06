import React, { useState } from 'react';
import { Bell, BellOff, Check, AlertCircle, Smartphone, Send } from 'lucide-react';
import { usePushNotifications } from '../hooks/usePushNotifications';

export default function PushNotificationSettings() {
  const {
    isSupported,
    isSubscribed,
    permission,
    loading,
    error,
    subscribe,
    unsubscribe,
    sendTest
  } = usePushNotifications();
  
  const [testSent, setTestSent] = useState(false);
  const [testLoading, setTestLoading] = useState(false);

  const handleToggle = async () => {
    if (isSubscribed) {
      await unsubscribe();
    } else {
      await subscribe();
    }
  };

  const handleSendTest = async () => {
    setTestLoading(true);
    const success = await sendTest();
    setTestSent(success);
    setTestLoading(false);
    
    if (success) {
      setTimeout(() => setTestSent(false), 3000);
    }
  };

  if (!isSupported) {
    return (
      <div className="bg-zinc-800/50 rounded-xl p-4 border border-zinc-700/50">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-zinc-700/50 flex items-center justify-center">
            <BellOff className="w-5 h-5 text-zinc-500" />
          </div>
          <div className="flex-1">
            <h3 className="font-medium text-zinc-300">Push Notifications</h3>
            <p className="text-sm text-zinc-500">Not supported on this device/browser</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-zinc-800/50 rounded-xl p-4 border border-zinc-700/50 space-y-4">
      {/* Main Toggle */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
            isSubscribed ? 'bg-emerald-500/20' : 'bg-zinc-700/50'
          }`}>
            {isSubscribed ? (
              <Bell className="w-5 h-5 text-emerald-400" />
            ) : (
              <BellOff className="w-5 h-5 text-zinc-500" />
            )}
          </div>
          <div>
            <h3 className="font-medium text-white">Push Notifications</h3>
            <p className="text-sm text-zinc-400">
              {isSubscribed ? 'Enabled on this device' : 'Get instant updates'}
            </p>
          </div>
        </div>
        
        <button
          onClick={handleToggle}
          disabled={loading}
          className={`relative w-14 h-7 rounded-full transition-colors ${
            isSubscribed ? 'bg-emerald-500' : 'bg-zinc-600'
          } ${loading ? 'opacity-50' : ''}`}
        >
          <div className={`absolute top-1 w-5 h-5 rounded-full bg-white transition-transform ${
            isSubscribed ? 'left-8' : 'left-1'
          }`} />
        </button>
      </div>

      {/* Permission Warning */}
      {permission === 'denied' && (
        <div className="flex items-start gap-2 p-3 bg-red-500/10 border border-red-500/30 rounded-lg">
          <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
          <div className="text-sm">
            <p className="text-red-400 font-medium">Notifications Blocked</p>
            <p className="text-red-400/80">
              Please enable notifications in your browser settings to receive push updates.
            </p>
          </div>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="flex items-center gap-2 p-3 bg-amber-500/10 border border-amber-500/30 rounded-lg">
          <AlertCircle className="w-5 h-5 text-amber-400" />
          <p className="text-sm text-amber-400">{error}</p>
        </div>
      )}

      {/* Features List */}
      {isSubscribed && (
        <div className="space-y-2 pt-2 border-t border-zinc-700/50">
          <p className="text-xs text-zinc-500 uppercase tracking-wider">You'll be notified about:</p>
          <div className="grid grid-cols-2 gap-2">
            {[
              'Streak reminders',
              'New badges earned',
              'Challenge updates',
              'Inactivity alerts'
            ].map((item) => (
              <div key={item} className="flex items-center gap-2 text-sm text-zinc-400">
                <Check className="w-4 h-4 text-emerald-400" />
                {item}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Test Notification Button */}
      {isSubscribed && (
        <div className="pt-2 border-t border-zinc-700/50">
          <button
            onClick={handleSendTest}
            disabled={testLoading || testSent}
            className={`w-full flex items-center justify-center gap-2 py-2.5 rounded-lg transition-colors ${
              testSent 
                ? 'bg-emerald-500/20 text-emerald-400' 
                : 'bg-zinc-700/50 hover:bg-zinc-700 text-zinc-300'
            }`}
          >
            {testLoading ? (
              <>
                <div className="w-4 h-4 border-2 border-zinc-500 border-t-transparent rounded-full animate-spin" />
                Sending...
              </>
            ) : testSent ? (
              <>
                <Check className="w-4 h-4" />
                Test Sent!
              </>
            ) : (
              <>
                <Send className="w-4 h-4" />
                Send Test Notification
              </>
            )}
          </button>
        </div>
      )}

      {/* Mobile Tip */}
      {!isSubscribed && (
        <div className="flex items-start gap-2 p-3 bg-blue-500/10 border border-blue-500/30 rounded-lg">
          <Smartphone className="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" />
          <div className="text-sm">
            <p className="text-blue-400 font-medium">Pro Tip</p>
            <p className="text-blue-400/80">
              Add Edge Mode to your home screen for the best notification experience!
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
