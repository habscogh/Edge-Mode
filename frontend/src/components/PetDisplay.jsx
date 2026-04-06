import React, { useState, useEffect, useCallback } from 'react';
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
  Music,
  Hand,
  Megaphone,
  Compass
} from 'lucide-react';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

// Rarity colors with glow effects
const rarityColors = {
  common: 'text-zinc-400 border-zinc-600',
  uncommon: 'text-green-400 border-green-500/50',
  rare: 'text-blue-400 border-blue-500/50',
  epic: 'text-purple-400 border-purple-500/50',
  legendary: 'text-yellow-400 border-yellow-500/50 shadow-lg shadow-yellow-500/20'
};

// Enhanced interaction button configs with new actions
const interactionButtons = [
  { type: 'pet', icon: Heart, label: 'Pet', color: 'text-pink-400 hover:bg-pink-500/20', emoji: '💕' },
  { type: 'feed', icon: Cookie, label: 'Feed', color: 'text-orange-400 hover:bg-orange-500/20', emoji: '🍖' },
  { type: 'play', icon: Gamepad2, label: 'Play', color: 'text-green-400 hover:bg-green-500/20', emoji: '⚽' },
  { type: 'train', icon: GraduationCap, label: 'Train', color: 'text-blue-400 hover:bg-blue-500/20', emoji: '💪' },
  { type: 'dance', icon: Music, label: 'Dance', color: 'text-purple-400 hover:bg-purple-500/20', emoji: '🎵' },
  { type: 'highfive', icon: Hand, label: 'Hi-5', color: 'text-yellow-400 hover:bg-yellow-500/20', emoji: '✋' },
  { type: 'cheer', icon: Megaphone, label: 'Cheer', color: 'text-cyan-400 hover:bg-cyan-500/20', emoji: '📣' },
  { type: 'sleep', icon: Moon, label: 'Sleep', color: 'text-indigo-400 hover:bg-indigo-500/20', emoji: '💤' },
  { type: 'adventure', icon: Compass, label: 'Quest', color: 'text-amber-400 hover:bg-amber-500/20', emoji: '🗺️' },
];

// Animation classes mapped to CSS keyframes - NEW enhanced animations
const animationClasses = {
  // Petting animations
  petting_purr: 'pet-purr-vibrate',
  heart_particles: 'pet-hearts-rise',
  lean_nuzzle: 'pet-nuzzle',
  happy_wiggle: 'pet-wiggle-happy',
  // Feeding animations
  treat_munch: 'pet-munch',
  belly_glow: 'pet-belly-glow',
  happy_dance: 'pet-happy-dance',
  satisfied_wiggle: 'pet-satisfied',
  // Play animations
  ball_chase: 'pet-chase-ball',
  pounce_catch: 'pet-pounce',
  proud_return: 'pet-proud-return',
  wagging_tail: 'pet-wag',
  // Training animations  
  power_stretch: 'pet-stretch',
  energy_burst: 'pet-energy-burst',
  power_pose: 'pet-power-pose',
  level_glow: 'pet-level-up',
  // Sleep animations
  curl_up: 'pet-curl',
  soft_snore: 'pet-snore',
  dream_bubbles: 'pet-dream',
  peaceful_rest: 'pet-rest',
  // Dance animations
  jump_spin_360: 'pet-spin-360',
  air_guitar: 'pet-air-guitar',
  disco_lights: 'pet-disco',
  victory_dance: 'pet-victory',
  // High-five animations
  reach_out: 'pet-reach',
  bump_flash: 'pet-bump-flash',
  star_impact: 'pet-star-burst',
  confetti_burst: 'pet-confetti',
  // Cheer animations
  hold_sign: 'pet-hold-sign',
  fist_pump: 'pet-fist-pump',
  sparkle_glow: 'pet-sparkle-glow',
  motivate_pose: 'pet-motivate',
  // Adventure animations
  explorer_gear: 'pet-gear-up',
  walk_offscreen: 'pet-walk-off',
  return_trophy: 'pet-return-trophy',
  excited_spin: 'pet-excited-spin',
  // Legacy fallbacks
  bounce: 'pet-bounce',
  hearts: 'pet-hearts-rise',
  wiggle: 'pet-wiggle-happy',
  spin: 'pet-spin-360',
  eat: 'pet-munch',
  satisfied: 'pet-satisfied',
  jump: 'pet-pounce',
  run: 'pet-chase-ball',
  focus: 'pet-energy-burst',
  levelup: 'pet-level-up',
  sparkle: 'pet-sparkle-glow',
  sleep: 'pet-rest',
  zzz: 'pet-snore',
  dream: 'pet-dream',
  dance: 'pet-disco',
};

// Particle effects based on interaction type
const particleEmojis = {
  hearts_rising: ['💕', '💗', '💖', '💝', '❤️'],
  treat_particles: ['🍖', '🦴', '🍪', '✨', '⭐'],
  ball_bounce: ['⚽', '🏀', '⚡', '💨', '✨'],
  aura_pulse: ['💪', '⚡', '🔥', '✨', '💫'],
  zzz_floating: ['💤', '😴', '🌙', '⭐', '✨'],
  music_notes: ['🎵', '🎶', '🎤', '🎸', '✨'],
  star_burst: ['⭐', '🌟', '✨', '💫', '🎉'],
  sparkle_aura: ['✨', '💫', '⭐', '🌟', '💖'],
  trophy_sparkle: ['🏆', '🎖️', '🏅', '✨', '🎉'],
};

const PetDisplay = ({ onSelectPet, compact = false }) => {
  const navigate = useNavigate();
  const [petData, setPetData] = useState(null);
  const [interactions, setInteractions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentAnimation, setCurrentAnimation] = useState(null);
  const [currentEffect, setCurrentEffect] = useState(null);
  const [particles, setParticles] = useState([]);
  const [showMessage, setShowMessage] = useState(null);

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

  // Generate floating particles
  const spawnParticles = useCallback((effectType) => {
    const emojis = particleEmojis[effectType] || particleEmojis.sparkle_aura;
    const newParticles = [];
    
    for (let i = 0; i < 8; i++) {
      newParticles.push({
        id: Date.now() + i,
        emoji: emojis[Math.floor(Math.random() * emojis.length)],
        x: Math.random() * 80 + 10, // 10-90% horizontal
        delay: Math.random() * 0.5,
        duration: 1.5 + Math.random() * 1,
        scale: 0.8 + Math.random() * 0.6,
      });
    }
    
    setParticles(newParticles);
    
    // Clear particles after animation
    setTimeout(() => setParticles([]), 3000);
  }, []);

  const handleInteract = async (interactionType) => {
    if (currentAnimation || !petData?.has_pet) return;
    
    try {
      const response = await axios.post(`${API}/pets/interact`, {
        interaction_type: interactionType
      });
      
      // Show animation
      const animClass = animationClasses[response.data.animation] || 'pet-bounce';
      setCurrentAnimation(animClass);
      setCurrentEffect(response.data.effect);
      
      // Spawn particle effects
      spawnParticles(response.data.effect);
      
      // Show message popup
      setShowMessage(response.data.message);
      
      toast.success(response.data.message, {
        icon: interactionButtons.find(b => b.type === interactionType)?.emoji || '✨'
      });
      
      // Clear animation after delay
      setTimeout(() => {
        setCurrentAnimation(null);
        setCurrentEffect(null);
        setShowMessage(null);
        fetchPetData();
      }, 3000);
      
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
        className="bg-gradient-to-br from-purple-900/30 to-pink-900/30 rounded-xl p-4 border border-purple-500/30 cursor-pointer hover:border-purple-500/50 transition-all group"
        onClick={onSelectPet}
        data-testid="pet-selection-prompt"
      >
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 bg-purple-500/20 rounded-full flex items-center justify-center text-3xl animate-bounce group-hover:scale-110 transition-transform">
            🐾
          </div>
          <div className="flex-1">
            <h3 className="text-white font-bold text-sm">Get Your Companion!</h3>
            <p className="text-zinc-400 text-xs">Choose a virtual pet to grow with you</p>
          </div>
          <ChevronRight className="w-5 h-5 text-purple-400 group-hover:translate-x-1 transition-transform" />
        </div>
      </div>
    );
  }

  const { pet, current_streak, next_evolution, days_until_evolution } = petData;

  return (
    <div 
      className={`relative bg-gradient-to-br from-zinc-900 to-zinc-800 rounded-xl p-4 border-2 ${rarityColors[pet.rarity] || 'border-zinc-700'} overflow-hidden`}
      data-testid="pet-display"
    >
      {/* Background effects for legendary pets */}
      {pet.rarity === 'legendary' && (
        <div className="absolute inset-0 opacity-30 pointer-events-none">
          <div className="absolute top-2 left-4 text-yellow-400 animate-pulse text-lg">✨</div>
          <div className="absolute top-6 right-8 text-yellow-400 animate-pulse delay-200 text-sm">⭐</div>
          <div className="absolute bottom-8 left-8 text-yellow-400 animate-pulse delay-500 text-xs">💫</div>
          <div className="absolute bottom-4 right-4 text-yellow-400 animate-pulse delay-700 text-lg">✨</div>
        </div>
      )}
      
      {/* Epic glow effect */}
      {pet.rarity === 'epic' && (
        <div className="absolute inset-0 bg-gradient-to-r from-purple-500/10 to-pink-500/10 animate-pulse pointer-events-none" />
      )}

      {/* Floating particles */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        {particles.map((p) => (
          <div
            key={p.id}
            className="absolute particle-float-up"
            style={{
              left: `${p.x}%`,
              bottom: '20%',
              animationDelay: `${p.delay}s`,
              animationDuration: `${p.duration}s`,
              fontSize: `${p.scale * 1.5}rem`,
            }}
          >
            {p.emoji}
          </div>
        ))}
      </div>

      {/* Message popup */}
      {showMessage && (
        <div className="absolute top-0 left-0 right-0 z-20 p-2 bg-black/80 rounded-t-xl text-center animate-fade-in">
          <p className="text-sm text-white font-medium">{showMessage}</p>
        </div>
      )}

      <div className="flex items-center gap-4">
        {/* Pet Icon - Enhanced interactive area */}
        <div 
          className={`relative w-20 h-20 bg-gradient-to-br from-zinc-800 to-zinc-900 rounded-full flex items-center justify-center text-5xl cursor-pointer transition-all hover:scale-110 border-2 border-zinc-700 ${currentAnimation || ''}`}
          onClick={() => handleInteract('pet')}
          data-testid="pet-tap-area"
        >
          {/* Glow ring during animation */}
          {currentAnimation && (
            <div className="absolute inset-0 rounded-full border-4 border-yellow-400/50 animate-ping" />
          )}
          
          {pet.icon}
        </div>

        {/* Pet Info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h3 className="text-white font-bold text-sm truncate">{pet.name}</h3>
            <span className={`text-xs px-2 py-0.5 rounded-full bg-zinc-800 capitalize ${rarityColors[pet.rarity]?.split(' ')[0]}`}>
              {pet.rarity}
            </span>
          </div>
          <p className="text-zinc-400 text-xs">{pet.appearance_name}</p>
          
          {/* Happiness bar */}
          <div className="mt-1 flex items-center gap-2">
            <Heart className="w-3 h-3 text-pink-400" />
            <div className="flex-1 h-1.5 bg-zinc-700 rounded-full overflow-hidden">
              <div 
                className="h-full bg-gradient-to-r from-pink-500 to-red-500 transition-all"
                style={{ width: `${pet.happiness || 100}%` }}
              />
            </div>
            <span className="text-xs text-zinc-500">{pet.happiness}%</span>
          </div>
          
          {/* Evolution progress */}
          {next_evolution && (
            <div className="mt-2">
              <div className="flex justify-between text-xs text-zinc-500 mb-1">
                <span className="flex items-center gap-1">
                  <Sparkles className="w-3 h-3 text-purple-400" />
                  Stage {pet.evolution_stage} → {next_evolution.stage}
                </span>
                <span>{days_until_evolution} days</span>
              </div>
              <div className="h-1.5 bg-zinc-700 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-purple-500 via-pink-500 to-purple-500 bg-size-200 animate-gradient-x transition-all"
                  style={{ 
                    width: `${Math.min(100, (current_streak / next_evolution.streak_required) * 100)}%` 
                  }}
                />
              </div>
            </div>
          )}
          
          {/* Max evolution badge */}
          {!next_evolution && (
            <div className="flex items-center gap-1 mt-2 text-yellow-400 text-xs">
              <Star className="w-3 h-3 fill-yellow-400" />
              <span className="font-bold">MAX EVOLUTION!</span>
              <Star className="w-3 h-3 fill-yellow-400" />
            </div>
          )}
        </div>

        {/* Bonuses */}
        {(pet.xp_bonus > 0 || pet.coin_bonus > 0) && (
          <div className="text-right space-y-1">
            {pet.xp_bonus > 0 && (
              <div className="flex items-center gap-1 text-purple-400 text-xs bg-purple-500/10 px-2 py-1 rounded-full">
                <Zap className="w-3 h-3" />
                <span>+{Math.round(pet.xp_bonus * 100)}% XP</span>
              </div>
            )}
            {pet.coin_bonus > 0 && (
              <div className="flex items-center gap-1 text-yellow-400 text-xs bg-yellow-500/10 px-2 py-1 rounded-full">
                <span>🪙</span>
                <span>+{pet.coin_bonus}</span>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Interaction Buttons - Enhanced grid layout */}
      {!compact && (
        <div className="mt-4 grid grid-cols-5 gap-2">
          {interactionButtons.slice(0, 5).map(({ type, icon: Icon, label, color, emoji }) => {
            const status = getInteractionStatus(type);
            const isAvailable = status.available;
            
            return (
              <button
                key={type}
                onClick={() => handleInteract(type)}
                disabled={!isAvailable || currentAnimation}
                className={`flex flex-col items-center justify-center p-2 rounded-xl transition-all ${
                  isAvailable 
                    ? `bg-zinc-800/50 ${color} cursor-pointer active:scale-95` 
                    : 'bg-zinc-900/50 text-zinc-600 cursor-not-allowed opacity-50'
                }`}
                title={isAvailable ? label : `Cooldown: ${formatCooldown(status.remaining_seconds)}`}
                data-testid={`pet-action-${type}`}
              >
                <span className="text-lg">{emoji}</span>
                <span className="text-[9px] mt-0.5 font-medium">
                  {isAvailable ? label : formatCooldown(status.remaining_seconds)}
                </span>
              </button>
            );
          })}
        </div>
      )}
      
      {/* Second row of interactions */}
      {!compact && (
        <div className="mt-2 grid grid-cols-4 gap-2">
          {interactionButtons.slice(5).map(({ type, icon: Icon, label, color, emoji }) => {
            const status = getInteractionStatus(type);
            const isAvailable = status.available;
            
            return (
              <button
                key={type}
                onClick={() => handleInteract(type)}
                disabled={!isAvailable || currentAnimation}
                className={`flex flex-col items-center justify-center p-2 rounded-xl transition-all ${
                  isAvailable 
                    ? `bg-zinc-800/50 ${color} cursor-pointer active:scale-95` 
                    : 'bg-zinc-900/50 text-zinc-600 cursor-not-allowed opacity-50'
                }`}
                title={isAvailable ? label : `Cooldown: ${formatCooldown(status.remaining_seconds)}`}
                data-testid={`pet-action-${type}`}
              >
                <span className="text-lg">{emoji}</span>
                <span className="text-[9px] mt-0.5 font-medium">
                  {isAvailable ? label : formatCooldown(status.remaining_seconds)}
                </span>
              </button>
            );
          })}
        </div>
      )}

      {/* Tap hint for compact mode */}
      {compact && (
        <p className="text-center text-zinc-500 text-xs mt-2 flex items-center justify-center gap-1">
          <Heart className="w-3 h-3 text-pink-400" />
          Tap your pet to interact!
        </p>
      )}
    </div>
  );
};

export default PetDisplay;
