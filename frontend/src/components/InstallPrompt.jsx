import React, { useState } from 'react';
import { Download, X, Share, Smartphone, Check, Plus } from 'lucide-react';
import { useInstallPrompt } from '../hooks/useInstallPrompt';

// Floating Install Button (for dashboard/app pages)
export function InstallButton({ className = '' }) {
  const { isInstallable, isInstalled, isIOS, promptInstall } = useInstallPrompt();
  const [showIOSGuide, setShowIOSGuide] = useState(false);

  if (isInstalled) return null;

  if (isIOS) {
    return (
      <>
        <button
          onClick={() => setShowIOSGuide(true)}
          className={`flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-emerald-500 to-emerald-600 text-white rounded-full shadow-lg hover:shadow-emerald-500/25 transition-all ${className}`}
          data-testid="install-app-btn"
        >
          <Download className="w-4 h-4" />
          <span className="text-sm font-medium">Install App</span>
        </button>
        
        {showIOSGuide && (
          <IOSInstallGuide onClose={() => setShowIOSGuide(false)} />
        )}
      </>
    );
  }

  if (!isInstallable) return null;

  return (
    <button
      onClick={promptInstall}
      className={`flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-emerald-500 to-emerald-600 text-white rounded-full shadow-lg hover:shadow-emerald-500/25 transition-all ${className}`}
      data-testid="install-app-btn"
    >
      <Download className="w-4 h-4" />
      <span className="text-sm font-medium">Install App</span>
    </button>
  );
}

// iOS Install Guide Modal
function IOSInstallGuide({ onClose }) {
  return (
    <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-black/80 backdrop-blur-sm">
      <div className="w-full max-w-md bg-zinc-900 rounded-t-2xl sm:rounded-2xl p-6 animate-slide-up">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-bold text-white">Install Edge Mode</h3>
          <button
            onClick={onClose}
            className="p-2 hover:bg-zinc-800 rounded-full transition-colors"
          >
            <X className="w-5 h-5 text-zinc-400" />
          </button>
        </div>
        
        <p className="text-zinc-400 text-sm mb-6">
          Add Edge Mode to your home screen for the best experience!
        </p>
        
        <div className="space-y-4">
          <div className="flex items-start gap-4 p-3 bg-zinc-800/50 rounded-lg">
            <div className="w-8 h-8 bg-blue-500/20 rounded-full flex items-center justify-center flex-shrink-0">
              <span className="text-blue-400 font-bold">1</span>
            </div>
            <div>
              <p className="text-white font-medium">Tap the Share button</p>
              <p className="text-zinc-500 text-sm">Look for <Share className="w-4 h-4 inline text-blue-400" /> at the bottom of Safari</p>
            </div>
          </div>
          
          <div className="flex items-start gap-4 p-3 bg-zinc-800/50 rounded-lg">
            <div className="w-8 h-8 bg-blue-500/20 rounded-full flex items-center justify-center flex-shrink-0">
              <span className="text-blue-400 font-bold">2</span>
            </div>
            <div>
              <p className="text-white font-medium">Scroll and tap "Add to Home Screen"</p>
              <p className="text-zinc-500 text-sm">Look for <Plus className="w-4 h-4 inline text-zinc-400" /> Add to Home Screen</p>
            </div>
          </div>
          
          <div className="flex items-start gap-4 p-3 bg-zinc-800/50 rounded-lg">
            <div className="w-8 h-8 bg-emerald-500/20 rounded-full flex items-center justify-center flex-shrink-0">
              <span className="text-emerald-400 font-bold">3</span>
            </div>
            <div>
              <p className="text-white font-medium">Tap "Add" to install</p>
              <p className="text-zinc-500 text-sm">Edge Mode will appear on your home screen!</p>
            </div>
          </div>
        </div>
        
        <button
          onClick={onClose}
          className="w-full mt-6 py-3 bg-zinc-800 hover:bg-zinc-700 text-white rounded-lg transition-colors font-medium"
        >
          Got it!
        </button>
      </div>
    </div>
  );
}

// Banner Component (for landing page or first-time users)
export function InstallBanner({ onDismiss }) {
  const { isInstallable, isInstalled, isIOS, promptInstall } = useInstallPrompt();
  const [showIOSGuide, setShowIOSGuide] = useState(false);
  const [dismissed, setDismissed] = useState(() => {
    return localStorage.getItem('installBannerDismissed') === 'true';
  });

  const handleDismiss = () => {
    setDismissed(true);
    localStorage.setItem('installBannerDismissed', 'true');
    onDismiss?.();
  };

  if (isInstalled || dismissed) return null;
  if (!isInstallable && !isIOS) return null;

  const handleInstall = async () => {
    if (isIOS) {
      setShowIOSGuide(true);
    } else {
      const installed = await promptInstall();
      if (installed) {
        handleDismiss();
      }
    }
  };

  return (
    <>
      <div className="fixed bottom-4 left-4 right-4 z-40 animate-slide-up" data-testid="install-banner">
        <div className="max-w-md mx-auto bg-gradient-to-r from-zinc-900 to-zinc-800 border border-zinc-700 rounded-2xl p-4 shadow-2xl">
          <div className="flex items-start gap-3">
            <div className="w-12 h-12 bg-emerald-500/20 rounded-xl flex items-center justify-center flex-shrink-0">
              <Smartphone className="w-6 h-6 text-emerald-400" />
            </div>
            <div className="flex-1 min-w-0">
              <h4 className="text-white font-bold text-sm">Install Edge Mode</h4>
              <p className="text-zinc-400 text-xs mt-0.5">
                Add to home screen for quick access & push notifications
              </p>
            </div>
            <button
              onClick={handleDismiss}
              className="p-1.5 hover:bg-zinc-700 rounded-full transition-colors flex-shrink-0"
            >
              <X className="w-4 h-4 text-zinc-500" />
            </button>
          </div>
          
          <div className="flex gap-2 mt-3">
            <button
              onClick={handleInstall}
              className="flex-1 flex items-center justify-center gap-2 py-2.5 bg-emerald-500 hover:bg-emerald-600 text-white rounded-xl transition-colors font-medium text-sm"
            >
              <Download className="w-4 h-4" />
              Install Now
            </button>
            <button
              onClick={handleDismiss}
              className="px-4 py-2.5 bg-zinc-700 hover:bg-zinc-600 text-zinc-300 rounded-xl transition-colors text-sm"
            >
              Later
            </button>
          </div>
        </div>
      </div>
      
      {showIOSGuide && (
        <IOSInstallGuide onClose={() => setShowIOSGuide(false)} />
      )}
    </>
  );
}

// Settings Component (for profile page)
export function InstallAppSettings() {
  const { isInstallable, isInstalled, isIOS, promptInstall } = useInstallPrompt();
  const [showIOSGuide, setShowIOSGuide] = useState(false);

  if (isInstalled) {
    return (
      <div className="bg-zinc-800/50 rounded-xl p-4 border border-zinc-700/50">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-emerald-500/20 flex items-center justify-center">
            <Check className="w-5 h-5 text-emerald-400" />
          </div>
          <div>
            <h3 className="font-medium text-white">App Installed</h3>
            <p className="text-sm text-zinc-400">Edge Mode is installed on this device</p>
          </div>
        </div>
      </div>
    );
  }

  const handleInstall = async () => {
    if (isIOS) {
      setShowIOSGuide(true);
    } else {
      await promptInstall();
    }
  };

  return (
    <>
      <div className="bg-zinc-800/50 rounded-xl p-4 border border-zinc-700/50">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-blue-500/20 flex items-center justify-center">
              <Smartphone className="w-5 h-5 text-blue-400" />
            </div>
            <div>
              <h3 className="font-medium text-white">Install App</h3>
              <p className="text-sm text-zinc-400">
                {isIOS ? 'Add to your home screen' : isInstallable ? 'Quick access from home screen' : 'Open in Safari to install'}
              </p>
            </div>
          </div>
          
          {(isInstallable || isIOS) && (
            <button
              onClick={handleInstall}
              className="flex items-center gap-2 px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors text-sm font-medium"
              data-testid="install-app-settings-btn"
            >
              <Download className="w-4 h-4" />
              Install
            </button>
          )}
        </div>
        
        {/* Benefits */}
        <div className="mt-4 pt-4 border-t border-zinc-700/50 grid grid-cols-2 gap-2">
          {[
            'Quick access',
            'Push notifications',
            'Full screen mode',
            'Works offline'
          ].map((benefit) => (
            <div key={benefit} className="flex items-center gap-2 text-sm text-zinc-400">
              <Check className="w-4 h-4 text-emerald-400" />
              {benefit}
            </div>
          ))}
        </div>
      </div>
      
      {showIOSGuide && (
        <IOSInstallGuide onClose={() => setShowIOSGuide(false)} />
      )}
    </>
  );
}

export default InstallButton;
