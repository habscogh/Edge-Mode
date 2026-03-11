import React, { useState, useEffect } from 'react';
import { Flame, X, Trophy, Zap } from 'lucide-react';
import { Button } from './ui/button';
import { ShareIcons } from './ShareButton';
import confetti from 'canvas-confetti';

const STREAK_MILESTONES = [7, 14, 30, 50, 100];
const SESSION_MILESTONES = [10, 25, 50, 100, 250, 500, 1000];

const MILESTONE_DATA = {
  // Streak milestones
  streak_7: {
    type: 'streak',
    title: "Week Warrior!",
    emoji: "🔥",
    message: "You've logged sessions for 7 days straight!",
    color: "from-orange-500 to-amber-500"
  },
  streak_14: {
    type: 'streak',
    title: "Fortnight Fighter!",
    emoji: "🔥🔥",
    message: "Two weeks of consistency! You're unstoppable!",
    color: "from-orange-600 to-red-500"
  },
  streak_30: {
    type: 'streak',
    title: "Monthly Master!",
    emoji: "🔥🔥🔥",
    message: "30 days! You've built a powerful habit!",
    color: "from-red-500 to-pink-500"
  },
  streak_50: {
    type: 'streak',
    title: "Fifty & Thriving!",
    emoji: "⚡",
    message: "50-day streak! You're in the top 1%!",
    color: "from-purple-500 to-indigo-500"
  },
  streak_100: {
    type: 'streak',
    title: "Century Legend!",
    emoji: "👑",
    message: "100 days! You're a true legend!",
    color: "from-yellow-400 to-amber-500"
  },
  // Session milestones
  session_10: {
    type: 'session',
    title: "Getting Started!",
    emoji: "⭐",
    message: "10 sessions logged! You're building momentum!",
    color: "from-blue-500 to-cyan-500"
  },
  session_25: {
    type: 'session',
    title: "Quarter Century!",
    emoji: "🌟",
    message: "25 sessions! You're making real progress!",
    color: "from-cyan-500 to-teal-500"
  },
  session_50: {
    type: 'session',
    title: "Halfway Hero!",
    emoji: "💪",
    message: "50 sessions! Half way to the century club!",
    color: "from-teal-500 to-green-500"
  },
  session_100: {
    type: 'session',
    title: "Century Club!",
    emoji: "🏆",
    message: "100 sessions! You've joined the elite!",
    color: "from-green-500 to-emerald-500"
  },
  session_250: {
    type: 'session',
    title: "Dedicated Grinder!",
    emoji: "💎",
    message: "250 sessions! True dedication pays off!",
    color: "from-emerald-500 to-blue-500"
  },
  session_500: {
    type: 'session',
    title: "Half Thousand!",
    emoji: "🚀",
    message: "500 sessions! You're absolutely crushing it!",
    color: "from-violet-500 to-purple-500"
  },
  session_1000: {
    type: 'session',
    title: "Thousand Club!",
    emoji: "👑",
    message: "1000 sessions! You're a true legend!",
    color: "from-yellow-500 to-orange-500"
  }
};

// Trigger real confetti
const triggerConfetti = (intensity = 'normal') => {
  const colors = ['#22c55e', '#f97316', '#eab308', '#3b82f6', '#ec4899'];
  
  if (intensity === 'epic') {
    // Epic confetti for big milestones (30+)
    const duration = 2000;
    const end = Date.now() + duration;
    
    const frame = () => {
      confetti({
        particleCount: 4,
        angle: 60,
        spread: 55,
        origin: { x: 0 },
        colors: colors,
        zIndex: 9999,
      });
      confetti({
        particleCount: 4,
        angle: 120,
        spread: 55,
        origin: { x: 1 },
        colors: colors,
        zIndex: 9999,
      });

      if (Date.now() < end) {
        requestAnimationFrame(frame);
      }
    };
    frame();
  } else {
    // Normal burst
    confetti({
      particleCount: 100,
      spread: 70,
      origin: { y: 0.6 },
      colors: colors,
      zIndex: 9999,
    });
  }
};

// Check if a streak milestone was just hit
export const checkMilestoneHit = (previousStreak, currentStreak) => {
  for (const milestone of STREAK_MILESTONES) {
    if (previousStreak < milestone && currentStreak >= milestone) {
      return { type: 'streak', value: milestone };
    }
  }
  return null;
};

// Check if a session milestone was just hit
export const checkSessionMilestoneHit = (previousSessions, currentSessions) => {
  for (const milestone of SESSION_MILESTONES) {
    if (previousSessions < milestone && currentSessions >= milestone) {
      return { type: 'session', value: milestone };
    }
  }
  return null;
};

// Milestone Celebration Modal
export const MilestoneCelebration = ({ milestone, streak, sessions, milestoneType = 'streak', onClose, onShare }) => {
  const [showConfetti, setShowConfetti] = useState(true);
  
  // Get the right data key based on type
  const dataKey = milestoneType === 'session' ? `session_${milestone}` : `streak_${milestone}`;
  const data = MILESTONE_DATA[dataKey] || MILESTONE_DATA['streak_7'];
  const displayValue = milestoneType === 'session' ? sessions : streak;

  useEffect(() => {
    // Trigger real canvas confetti
    const intensity = milestone >= 30 ? 'epic' : 'normal';
    triggerConfetti(intensity);
    
    // Auto-hide confetti after animation
    const timer = setTimeout(() => setShowConfetti(false), 3000);
    return () => clearTimeout(timer);
  }, [milestone]);

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
          {milestoneType === 'session' ? (
            <Zap className="w-6 h-6 text-yellow-500" />
          ) : (
            <Flame className="w-6 h-6 text-orange-500" />
          )}
          <span className={`text-3xl font-mono font-bold ${milestoneType === 'session' ? 'text-yellow-500' : 'text-orange-500'}`}>
            {displayValue}
          </span>
          <span className="text-zinc-400 font-body">
            {milestoneType === 'session' ? 'sessions' : 'day streak'}
          </span>
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
