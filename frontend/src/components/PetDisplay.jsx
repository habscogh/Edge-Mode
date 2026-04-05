import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'sonner';
import { Button } from './ui/button';
import { 
  Heart, 
  Sparkles, 
  ChevronRight,
  Star,
  Zap,
  Cookie,
  Gamepad2,
  GraduationCap,
  Moon,
  Music
} from 'lucide-react';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

// Rarity colors
const rarityColors = {
  common: 'text-zinc-400 border-zinc-600',
  uncommon: 'text-green-400 border-green-500/50',
  rare: 'text-blue-400 border-blue-500/50',
  epic: 'text-purple-400 border-purple-500/50',
  legendary: 'text-yellow-400 border-yellow-500/50'
};

// Interaction button configs
const interactionButtons = [
  { type: 'pet', icon: Heart, label: 'Pet', color: 'text-pink-400 hover:bg-pink-500/20' },
  { type: 'feed', icon: Cookie, label: 'Feed', color: 'text-orange-400 hover:bg-orange-500/20' },
  { type: 'play', icon: Gamepad2, label: 'Play', color: 'text-green-400 hover:bg-green-500/20' },
  { type: 'train', icon: GraduationCap, label: 'Train', color: 'text-blue-400 hover:bg-blue-500/20' },
  { type: 'dance', icon: Music, label: 'Dance', color: 'text-purple-400 hover:bg-purple-500/20' },
  { type: 'sleep', icon: Moon, label: 'Sleep', color: 'text-indigo-400 hover:bg-indigo-500/20' },
];

// Animation classes mapped to CSS
const animationClasses = {
  bounce: 'pet-bounce',
  hearts: 'pet-hearts',
  wiggle: 'pet-wiggle',
  spin: 'pet-spin',
  eat: 'pet-eat',
  satisfied: 'pet-hearts',
  jump: 'pet-jump',
  run: 'pet-run',
  focus: 'pet-sparkle',
  levelup: 'pet-sparkle',
  sparkle: 'pet-sparkle',
  sleep: 'pet-sleep',
  zzz: 'pet-sleep',
  dream: 'pet-sleep',
  dance: 'pet-dance',
};

const PetDisplay = ({ onSelectPet, compact = false }) => {
  const navigate = useNavigate();
  const [petData, setPetData] = useState(null);
  const [interactions, setInteractions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentAnimation, setCurrentAnimation] = useState(null);
  const [showEmoji, setShowEmoji] = useState(null);

  useEffect(() => {
    fetchPetData();
  }, []);

  const fetchPetData = async () => {
    try {
      const [petRes, intRes] = await Promise.all([
        axios.get(`${API}/pets/my-pet`),
        axios.get(`${API}/pets/interactions`).catch(() => ({ data: { interactions: [] } }))
      ]);
      setPetData(petRes.data);
      setInteractions(intRes.data.interactions || []);
    } catch (error) {
      console.error('Failed to fetch pet:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleInteract = async (interactionType) => {
    if (currentAnimation || !petData?.has_pet) return;
    
    try {
      const response = await axios.post(`${API}/pets/interact`, {
        interaction_type: interactionType
      });
      
      // Show animation
      setCurrentAnimation(response.data.animation);
      
      // Show emoji based on interaction
      const emojis = {
        pet: '💕',
        feed: '🍖',
        play: '⚡',
        train: '📚',
        dance: '🎵',
        sleep: '💤'
      };
      setShowEmoji(emojis[interactionType] || '✨');
      
      toast.success(response.data.message);
      
      // Clear animation after delay
      setTimeout(() => {
        setCurrentAnimation(null);
        setShowEmoji(null);
        fetchPetData(); // Refresh data
      }, 1500);
      
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Interaction failed');
    }
  };

  const getInteractionStatus = (type) => {
    const interaction = interactions.find(i => i.type === type);
    return interaction || { available: true, remaining_seconds: 0 };
  };

  const formatCooldown = (seconds) => {
    if (seconds < 60) return `${seconds}s`;
    const mins = Math.floor(seconds / 60);
    if (mins < 60) return `${mins}m`;
    const hours = Math.floor(mins / 60);
    return `${hours}h`;
  };

  if (loading) {
    return (
      <div className="bg-zinc-900/50 rounded-xl p-4 border border-zinc-800 animate-pulse">
        <div className="h-24 bg-zinc-800 rounded-lg"></div>
      </div>
    );
  }

  // No pet yet - show selection prompt
  if (!petData?.has_pet) {
    return (
      <div 
        className="bg-gradient-to-br from-purple-900/30 to-pink-900/30 rounded-xl p-4 border border-purple-500/30 cursor-pointer hover:border-purple-500/50 transition-all"
        onClick={onSelectPet}
        data-testid="pet-selection-prompt"
      >
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 bg-purple-500/20 rounded-full flex items-center justify-center text-3xl animate-bounce">
            🐾
          </div>
          <div className="flex-1">
            <h3 className="text-white font-bold text-sm">Get Your Companion!</h3>
            <p className="text-zinc-400 text-xs">Choose a virtual pet to grow with you</p>
          </div>
          <ChevronRight className="w-5 h-5 text-purple-400" />
        </div>
      </div>
    );
  }

  const { pet, current_streak, next_evolution, days_until_evolution } = petData;

  return (
    <div 
      className={`relative bg-gradient-to-br from-zinc-900 to-zinc-800 rounded-xl p-4 border ${rarityColors[pet.rarity] || 'border-zinc-700'} overflow-hidden`}
      data-testid="pet-display"
    >
      {/* Background sparkles for legendary */}
      {pet.rarity === 'legendary' && (
        <div className="absolute inset-0 opacity-20">
          <div className="absolute top-2 left-4 text-yellow-400 animate-pulse">✨</div>
          <div className="absolute bottom-4 right-6 text-yellow-400 animate-pulse delay-300">✨</div>
        </div>
      )}

      <div className="flex items-center gap-4">
        {/* Pet Icon - Tappable */}
        <div 
          className={`relative w-16 h-16 bg-zinc-800 rounded-full flex items-center justify-center text-4xl cursor-pointer transition-transform hover:scale-110 ${currentAnimation ? animationClasses[currentAnimation] || 'animate-bounce' : ''}`}
          onClick={() => handleInteract('pet')}
          data-testid="pet-tap-area"
        >
          {pet.icon}
          
          {/* Floating emoji animation */}
          {showEmoji && (
            <div className="absolute -top-4 left-1/2 transform -translate-x-1/2 text-2xl pet-float-up">
              {showEmoji}
            </div>
          )}
        </div>

        {/* Pet Info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h3 className="text-white font-bold text-sm truncate">{pet.name}</h3>
            <span className={`text-xs px-1.5 py-0.5 rounded-full bg-zinc-800 ${rarityColors[pet.rarity]?.split(' ')[0]}`}>
              {pet.rarity}
            </span>
          </div>
          <p className="text-zinc-400 text-xs">{pet.appearance_name}</p>
          
          {/* Evolution progress */}
          {next_evolution && (
            <div className="mt-2">
              <div className="flex justify-between text-xs text-zinc-500 mb-1">
                <span>Stage {pet.evolution_stage} → {next_evolution.stage}</span>
                <span>{days_until_evolution} days</span>
              </div>
              <div className="h-1.5 bg-zinc-700 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-purple-500 to-pink-500 transition-all"
                  style={{ 
                    width: `${Math.min(100, (current_streak / next_evolution.streak_required) * 100)}%` 
                  }}
                />
              </div>
            </div>
          )}
          
          {/* Max evolution badge */}
          {!next_evolution && (
            <div className="flex items-center gap-1 mt-1 text-yellow-400 text-xs">
              <Star className="w-3 h-3" />
              <span>Max Evolution!</span>
            </div>
          )}
        </div>

        {/* Bonuses */}
        {(pet.xp_bonus > 0 || pet.coin_bonus > 0) && (
          <div className="text-right">
            {pet.xp_bonus > 0 && (
              <div className="flex items-center gap-1 text-purple-400 text-xs">
                <Zap className="w-3 h-3" />
                <span>+{Math.round(pet.xp_bonus * 100)}% XP</span>
              </div>
            )}
            {pet.coin_bonus > 0 && (
              <div className="flex items-center gap-1 text-yellow-400 text-xs">
                <span>+{pet.coin_bonus}</span>
                <span>🪙</span>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Interaction Buttons */}
      {!compact && (
        <div className="mt-4 flex flex-wrap gap-2 justify-center">
          {interactionButtons.map(({ type, icon: Icon, label, color }) => {
            const status = getInteractionStatus(type);
            const isAvailable = status.available;
            
            return (
              <button
                key={type}
                onClick={() => handleInteract(type)}
                disabled={!isAvailable || currentAnimation}
                className={`flex flex-col items-center justify-center p-2 rounded-lg transition-all ${
                  isAvailable 
                    ? `bg-zinc-800/50 ${color} cursor-pointer` 
                    : 'bg-zinc-900/50 text-zinc-600 cursor-not-allowed'
                }`}
                title={isAvailable ? label : `Cooldown: ${formatCooldown(status.remaining_seconds)}`}
                data-testid={`pet-action-${type}`}
              >
                <Icon className="w-5 h-5" />
                <span className="text-[10px] mt-1">
                  {isAvailable ? label : formatCooldown(status.remaining_seconds)}
                </span>
              </button>
            );
          })}
        </div>
      )}

      {/* Tap hint for compact mode */}
      {compact && (
        <p className="text-center text-zinc-600 text-xs mt-2">
          Tap your pet to interact! 💕
        </p>
      )}
    </div>
  );
};

export default PetDisplay;
