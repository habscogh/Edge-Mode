import React, { useState, useEffect } from 'react';
import { Flame, X, Trophy } from 'lucide-react';
import { Button } from './ui/button';
import { ShareIcons } from './ShareButton';

const MILESTONES = [7, 14, 30, 50, 100];

const MILESTONE_DATA = {
  7: {
    title: "Week Warrior!",
    emoji: "🔥",
    message: "You've logged sessions for 7 days straight!",
    color: "from-orange-500 to-amber-500"
  },
  14: {
    title: "Fortnight Fighter!",
    emoji: "🔥🔥",
    message: "Two weeks of consistency! You're unstoppable!",
    color: "from-orange-600 to-red-500"
  },
  30: {
    title: "Monthly Master!",
    emoji: "🔥🔥🔥",
    message: "30 days! You've built a powerful habit!",
    color: "from-red-500 to-pink-500"
  },
  50: {
    title: "Fifty & Thriving!",
    emoji: "⚡",
    message: "50-day streak! You're in the top 1%!",
    color: "from-purple-500 to-indigo-500"
  },
  100: {
    title: "Century Legend!",
    emoji: "👑",
    message: "100 days! You're a true legend!",
    color: "from-yellow-400 to-amber-500"
  }
};

// Check if a streak milestone was just hit
export const checkMilestoneHit = (previousStreak, currentStreak) => {
  for (const milestone of MILESTONES) {
    if (previousStreak < milestone && currentStreak >= milestone) {
      return milestone;
    }
  }
  return null;
};

// Milestone Celebration Modal
export const MilestoneCelebration = ({ milestone, streak, onClose, onShare }) => {
  const [showConfetti, setShowConfetti] = useState(true);
  const data = MILESTONE_DATA[milestone] || MILESTONE_DATA[7];

  useEffect(() => {
    // Auto-hide confetti after animation
    const timer = setTimeout(() => setShowConfetti(false), 3000);
    return () => clearTimeout(timer);
  }, []);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/80 backdrop-blur-sm"
        onClick={onClose}
      />
      
      {/* Confetti Effect */}
      {showConfetti && (
        <div className="absolute inset-0 pointer-events-none overflow-hidden">
          {[...Array(30)].map((_, i) => (
            <div
              key={i}
              className="absolute animate-confetti"
              style={{
                left: `${Math.random() * 100}%`,
                animationDelay: `${Math.random() * 2}s`,
                animationDuration: `${2 + Math.random() * 2}s`
              }}
            >
              <span className="text-2xl">
                {['🔥', '⭐', '✨', '🎉', '💪'][Math.floor(Math.random() * 5)]}
              </span>
            </div>
          ))}
        </div>
      )}
      
      {/* Modal Content */}
      <div 
        className="relative bg-zinc-900 border border-zinc-700 rounded-2xl p-6 w-full max-w-sm animate-bounce-in"
        data-testid="milestone-celebration"
      >
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-3 right-3 text-zinc-500 hover:text-white transition-colors"
          data-testid="milestone-close"
        >
          <X className="w-5 h-5" />
        </button>
        
        {/* Icon with gradient background */}
        <div className={`w-20 h-20 mx-auto mb-4 rounded-full bg-gradient-to-br ${data.color} flex items-center justify-center shadow-lg`}>
          <span className="text-4xl">{data.emoji}</span>
        </div>
        
        {/* Title */}
        <h2 className="text-2xl font-heading font-bold text-center text-white mb-2 uppercase tracking-wide">
          {data.title}
        </h2>
        
        {/* Streak number */}
        <div className="flex items-center justify-center gap-2 mb-3">
          <Flame className="w-6 h-6 text-orange-500" />
          <span className="text-3xl font-mono font-bold text-orange-500">{streak}</span>
          <span className="text-zinc-400 font-body">day streak</span>
        </div>
        
        {/* Message */}
        <p className="text-center text-zinc-400 font-body text-sm mb-6">
          {data.message}
        </p>
        
        {/* Share section */}
        <div className="bg-zinc-800/50 rounded-lg p-4 mb-4">
          <p className="text-center text-zinc-500 text-xs uppercase tracking-wide mb-3">
            Share your achievement
          </p>
          <ShareIcons 
            type="streak" 
            data={{ streak }} 
            className="justify-center"
          />
        </div>
        
        {/* Continue button */}
        <Button
          onClick={onClose}
          className="w-full bg-primary hover:bg-primary/90"
          data-testid="milestone-continue"
        >
          Keep Going! 💪
        </Button>
      </div>
      
      {/* CSS for animations */}
      <style jsx global>{`
        @keyframes confetti {
          0% {
            transform: translateY(-100vh) rotate(0deg);
            opacity: 1;
          }
          100% {
            transform: translateY(100vh) rotate(720deg);
            opacity: 0;
          }
        }
        
        @keyframes bounce-in {
          0% {
            transform: scale(0.3);
            opacity: 0;
          }
          50% {
            transform: scale(1.05);
          }
          70% {
            transform: scale(0.9);
          }
          100% {
            transform: scale(1);
            opacity: 1;
          }
        }
        
        .animate-confetti {
          animation: confetti linear forwards;
        }
        
        .animate-bounce-in {
          animation: bounce-in 0.5s ease-out forwards;
        }
      `}</style>
    </div>
  );
};

export default MilestoneCelebration;
