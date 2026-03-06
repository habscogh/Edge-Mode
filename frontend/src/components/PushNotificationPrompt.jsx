import React, { useState, useEffect } from 'react';
import { Bell, X } from 'lucide-react';
import { Button } from './ui/button';

export const PushNotificationPrompt = ({ onClose, onEnable }) => {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    // Animate in
    setTimeout(() => setIsVisible(true), 100);
  }, []);

  const handleClose = () => {
    setIsVisible(false);
    setTimeout(onClose, 300);
  };

  const handleEnable = () => {
    setIsVisible(false);
    setTimeout(() => {
      onEnable();
      onClose();
    }, 300);
  };

  return (
    <>
      {/* Backdrop */}
      <div 
        className={`fixed inset-0 bg-black/60 z-50 transition-opacity duration-300 ${
          isVisible ? 'opacity-100' : 'opacity-0'
        }`}
        onClick={handleClose}
      />
      
      {/* Modal */}
      <div className={`fixed bottom-0 left-0 right-0 z-50 p-4 transition-transform duration-300 ${
        isVisible ? 'translate-y-0' : 'translate-y-full'
      }`}>
        <div className="max-w-md mx-auto bg-zinc-900 border border-zinc-700 rounded-xl p-6 shadow-2xl">
          {/* Close button */}
          <button
            onClick={handleClose}
            className="absolute top-4 right-4 text-zinc-500 hover:text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>

          {/* Icon */}
          <div className="w-16 h-16 bg-primary/20 rounded-full flex items-center justify-center mx-auto mb-4">
            <Bell className="w-8 h-8 text-primary" />
          </div>

          {/* Content */}
          <h3 className="text-xl font-heading font-bold text-white text-center mb-2">
            Stay On Track! 🔥
          </h3>
          <p className="text-zinc-400 text-center font-body text-sm mb-6">
            Get friendly reminders to log your sessions and keep your streak alive. 
            We'll only notify you when it matters.
          </p>

          {/* Buttons */}
          <div className="flex gap-3">
            <Button
              onClick={handleClose}
              variant="ghost"
              className="flex-1 text-zinc-400 hover:text-white"
            >
              Maybe Later
            </Button>
            <Button
              onClick={handleEnable}
              className="flex-1 bg-primary text-primary-foreground hover:bg-primary/90 font-bold"
            >
              Enable Notifications
            </Button>
          </div>
        </div>
      </div>
    </>
  );
};
