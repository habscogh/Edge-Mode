import React, { useState, useEffect } from 'react';
import { X, Sparkles, Gift, Coins, Zap, Map, Trophy } from 'lucide-react';
import { Button } from './ui/button';

const rarityStyles = {
  common: {
    bg: 'bg-zinc-800',
    border: 'border-zinc-600',
    text: 'text-zinc-300',
    glow: ''
  },
  uncommon: {
    bg: 'bg-gradient-to-br from-green-900/50 to-emerald-900/50',
    border: 'border-green-500/50',
    text: 'text-green-400',
    glow: 'shadow-lg shadow-green-500/20'
  },
  rare: {
    bg: 'bg-gradient-to-br from-blue-900/50 to-cyan-900/50',
    border: 'border-blue-500/50',
    text: 'text-blue-400',
    glow: 'shadow-lg shadow-blue-500/20'
  },
  legendary: {
    bg: 'bg-gradient-to-br from-yellow-900/50 to-amber-900/50',
    border: 'border-yellow-500/50',
    text: 'text-yellow-400',
    glow: 'shadow-xl shadow-yellow-500/30'
  }
};

const ExpeditionModal = ({ isOpen, onClose, expeditionData }) => {
  const [showRewards, setShowRewards] = useState(false);
  const [animateItem, setAnimateItem] = useState(false);

  useEffect(() => {
    if (isOpen && expeditionData) {
      // Stagger animations
      setTimeout(() => setShowRewards(true), 800);
      setTimeout(() => setAnimateItem(true), 1500);
    } else {
      setShowRewards(false);
      setAnimateItem(false);
    }
  }, [isOpen, expeditionData]);

  if (!isOpen || !expeditionData) return null;

  const { expedition_name, story, rewards, rarity, pet_name } = expeditionData;
  const style = rarityStyles[rarity] || rarityStyles.common;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fade-in">
      <div 
        className={`relative w-full max-w-md rounded-2xl border-2 ${style.bg} ${style.border} ${style.glow} overflow-hidden`}
        data-testid="expedition-modal"
      >
        {/* Animated background particles */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          {[...Array(12)].map((_, i) => (
            <div
              key={i}
              className="absolute text-xl animate-float-random opacity-30"
              style={{
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
                animationDelay: `${Math.random() * 3}s`,
                animationDuration: `${3 + Math.random() * 2}s`
              }}
            >
              {['✨', '⭐', '🌟', '💫'][Math.floor(Math.random() * 4)]}
            </div>
          ))}
        </div>

        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 z-10 p-2 rounded-full bg-black/50 hover:bg-black/70 text-zinc-400 hover:text-white transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Header */}
        <div className="p-6 text-center">
          <div className="inline-flex items-center gap-2 bg-black/30 px-4 py-2 rounded-full mb-4">
            <Map className="w-4 h-4 text-amber-400" />
            <span className={`text-sm font-medium ${style.text}`}>{expedition_name}</span>
          </div>

          <h2 className="text-2xl font-heading font-bold text-white mb-2 uppercase">
            Expedition Complete!
          </h2>

          {/* Rarity badge */}
          <span className={`inline-block px-3 py-1 rounded-full text-xs font-bold uppercase ${style.text} bg-black/30`}>
            {rarity} Loot
          </span>
        </div>

        {/* Story */}
        <div className="px-6 pb-4">
          <div className="bg-black/30 rounded-xl p-4 border border-white/10">
            <p className="text-zinc-300 text-center leading-relaxed">
              {story}
            </p>
          </div>
        </div>

        {/* Rewards */}
        <div className={`px-6 pb-6 transition-all duration-500 ${showRewards ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
          <div className="flex items-center justify-center gap-2 mb-4">
            <Gift className="w-5 h-5 text-purple-400" />
            <h3 className="text-lg font-bold text-white">Rewards Found</h3>
          </div>

          <div className="grid grid-cols-2 gap-3">
            {/* Coins */}
            <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-xl p-4 text-center">
              <div className="flex items-center justify-center gap-2 mb-1">
                <Coins className="w-5 h-5 text-yellow-400" />
                <span className="text-2xl font-bold text-yellow-400">+{rewards.coins}</span>
              </div>
              <p className="text-xs text-zinc-400">Coins</p>
            </div>

            {/* XP */}
            <div className="bg-purple-500/10 border border-purple-500/30 rounded-xl p-4 text-center">
              <div className="flex items-center justify-center gap-2 mb-1">
                <Zap className="w-5 h-5 text-purple-400" />
                <span className="text-2xl font-bold text-purple-400">+{rewards.xp}</span>
              </div>
              <p className="text-xs text-zinc-400">XP</p>
            </div>
          </div>

          {/* Found Item */}
          {rewards.item && (
            <div 
              className={`mt-4 bg-gradient-to-r from-amber-900/30 to-orange-900/30 border border-amber-500/50 rounded-xl p-4 text-center transition-all duration-700 ${
                animateItem ? 'opacity-100 scale-100' : 'opacity-0 scale-90'
              }`}
            >
              <div className="flex items-center justify-center gap-2 mb-2">
                <Trophy className="w-5 h-5 text-amber-400" />
                <span className="text-sm font-medium text-amber-400">Souvenir Found!</span>
              </div>
              <div className="text-4xl mb-2 animate-bounce">{rewards.item.icon}</div>
              <h4 className="font-bold text-white">{rewards.item.name}</h4>
              <p className="text-xs text-zinc-400 mt-1">{rewards.item.description}</p>
            </div>
          )}
        </div>

        {/* Close button */}
        <div className="px-6 pb-6">
          <Button
            onClick={onClose}
            className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-bold py-3 rounded-xl"
            data-testid="expedition-close-btn"
          >
            <Sparkles className="w-4 h-4 mr-2" />
            Awesome!
          </Button>
        </div>
      </div>
    </div>
  );
};

export default ExpeditionModal;
