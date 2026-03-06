import React, { useEffect, useState } from 'react';
import confetti from 'canvas-confetti';

// Confetti celebration for milestones
export const triggerConfetti = (type = 'default') => {
  const defaults = {
    origin: { y: 0.7 },
    zIndex: 9999,
  };

  switch (type) {
    case 'streak':
      // Fire burst for streaks
      confetti({
        ...defaults,
        particleCount: 100,
        spread: 70,
        colors: ['#22c55e', '#f97316', '#eab308'],
      });
      break;
    
    case 'badge':
      // Star burst for badges
      const end = Date.now() + 500;
      const colors = ['#22c55e', '#3b82f6', '#f97316'];
      
      (function frame() {
        confetti({
          particleCount: 3,
          angle: 60,
          spread: 55,
          origin: { x: 0 },
          colors: colors,
          zIndex: 9999,
        });
        confetti({
          particleCount: 3,
          angle: 120,
          spread: 55,
          origin: { x: 1 },
          colors: colors,
          zIndex: 9999,
        });

        if (Date.now() < end) {
          requestAnimationFrame(frame);
        }
      }());
      break;
    
    case 'milestone':
      // Big celebration for major milestones
      const duration = 1000;
      const animationEnd = Date.now() + duration;
      
      const interval = setInterval(() => {
        const timeLeft = animationEnd - Date.now();
        
        if (timeLeft <= 0) {
          return clearInterval(interval);
        }
        
        confetti({
          particleCount: 50,
          startVelocity: 30,
          spread: 360,
          origin: {
            x: Math.random(),
            y: Math.random() - 0.2
          },
          colors: ['#22c55e', '#f97316', '#eab308', '#3b82f6', '#ec4899'],
          zIndex: 9999,
        });
      }, 150);
      break;
    
    default:
      confetti({
        ...defaults,
        particleCount: 50,
        spread: 60,
      });
  }
};

// Celebration overlay component for big moments
export const CelebrationOverlay = ({ type, message, subMessage, onClose }) => {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    // Trigger confetti
    triggerConfetti(type);
    
    // Animate in
    setTimeout(() => setIsVisible(true), 50);
    
    // Auto close after 3 seconds
    const timer = setTimeout(() => {
      setIsVisible(false);
      setTimeout(onClose, 300);
    }, 3000);
    
    return () => clearTimeout(timer);
  }, [type, onClose]);

  const getEmoji = () => {
    switch (type) {
      case 'streak': return '🔥';
      case 'badge': return '🏆';
      case 'milestone': return '⭐';
      default: return '🎉';
    }
  };

  return (
    <div 
      className={`fixed inset-0 z-[100] flex items-center justify-center p-4 transition-opacity duration-300 ${
        isVisible ? 'opacity-100' : 'opacity-0'
      }`}
      onClick={() => {
        setIsVisible(false);
        setTimeout(onClose, 300);
      }}
    >
      {/* Semi-transparent backdrop */}
      <div className="absolute inset-0 bg-black/40" />
      
      {/* Celebration card */}
      <div className={`relative bg-zinc-900 border border-zinc-700 rounded-2xl p-8 max-w-sm w-full text-center shadow-2xl transform transition-all duration-300 ${
        isVisible ? 'scale-100 translate-y-0' : 'scale-90 translate-y-4'
      }`}>
        <div className="text-6xl mb-4 animate-bounce">
          {getEmoji()}
        </div>
        <h2 className="text-2xl font-heading font-bold text-white mb-2">
          {message}
        </h2>
        {subMessage && (
          <p className="text-zinc-400 font-body">
            {subMessage}
          </p>
        )}
        <p className="text-zinc-500 text-xs mt-4 font-body">
          Tap anywhere to continue
        </p>
      </div>
    </div>
  );
};
