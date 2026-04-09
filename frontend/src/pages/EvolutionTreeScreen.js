import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { ArrowLeft, Sparkles, GitBranch, Lock, Check, Star } from 'lucide-react';
import { toast } from 'sonner';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

// Evolution paths based on dominant habit focus
const EVOLUTION_PATHS = {
  scholar: {
    name: 'Scholar Path',
    color: 'text-blue-400',
    bgColor: 'bg-blue-500/20',
    borderColor: 'border-blue-500/50',
    description: 'Focused on Study & Academics',
    requirements: '60%+ sessions in Study/Academics'
  },
  athlete: {
    name: 'Athlete Path',
    color: 'text-green-400',
    bgColor: 'bg-green-500/20',
    borderColor: 'border-green-500/50',
    description: 'Focused on Fitness & Training',
    requirements: '60%+ sessions in Fitness/Training'
  },
  artist: {
    name: 'Artist Path',
    color: 'text-purple-400',
    bgColor: 'bg-purple-500/20',
    borderColor: 'border-purple-500/50',
    description: 'Focused on Creative pursuits',
    requirements: '60%+ sessions in Creative activities'
  },
  balanced: {
    name: 'Balanced Path',
    color: 'text-amber-400',
    bgColor: 'bg-amber-500/20',
    borderColor: 'border-amber-500/50',
    description: 'Well-rounded across all habits',
    requirements: 'No single habit > 50%'
  }
};

const EvolutionTreeScreen = () => {
  const navigate = useNavigate();
  const [petData, setPetData] = useState(null);
  const [habitStats, setHabitStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [currentPath, setCurrentPath] = useState('balanced');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [petRes, statsRes] = await Promise.all([
        axios.get(`${API}/pets/my-pet`),
        axios.get(`${API}/stats/habit-breakdown`).catch(() => ({ data: null }))
      ]);
      
      setPetData(petRes.data);
      
      // Calculate dominant path from habit stats
      if (statsRes.data?.breakdown) {
        setHabitStats(statsRes.data.breakdown);
        const dominant = calculateDominantPath(statsRes.data.breakdown);
        setCurrentPath(dominant);
      }
    } catch (error) {
      toast.error('Failed to load evolution data');
    } finally {
      setLoading(false);
    }
  };

  const calculateDominantPath = (breakdown) => {
    if (!breakdown || breakdown.length === 0) return 'balanced';
    
    const total = breakdown.reduce((sum, h) => sum + h.sessions, 0);
    if (total === 0) return 'balanced';
    
    const sorted = [...breakdown].sort((a, b) => b.sessions - a.sessions);
    const topPercent = (sorted[0].sessions / total) * 100;
    
    if (topPercent < 50) return 'balanced';
    
    const topPillar = sorted[0].pillar.toLowerCase();
    if (topPillar.includes('study') || topPillar.includes('academic')) return 'scholar';
    if (topPillar.includes('fitness') || topPillar.includes('training') || topPillar.includes('sport')) return 'athlete';
    if (topPillar.includes('creative') || topPillar.includes('art') || topPillar.includes('music')) return 'artist';
    
    return 'balanced';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
      </div>
    );
  }

  const pet = petData?.pet;
  const stages = petData?.stages || {};
  const currentStage = pet?.evolution_stage || 1;
  const pathInfo = EVOLUTION_PATHS[currentPath];

  return (
    <div className="min-h-screen bg-black text-white pb-20">
      {/* Header */}
      <div className="bg-gradient-to-b from-zinc-900 to-black p-4 sticky top-0 z-10">
        <div className="flex items-center gap-3">
          <button onClick={() => navigate(-1)} className="p-2 hover:bg-zinc-800 rounded-lg">
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h1 className="text-xl font-heading font-bold uppercase flex items-center gap-2">
              <GitBranch className="w-5 h-5 text-purple-400" />
              Evolution Tree
            </h1>
            <p className="text-zinc-400 text-sm">Your pet's growth journey</p>
          </div>
        </div>
      </div>

      <div className="p-4">
        {/* Current Path Banner */}
        <div className={`${pathInfo.bgColor} border ${pathInfo.borderColor} rounded-xl p-4 mb-6`}>
          <div className="flex items-center gap-3">
            <div className={`w-12 h-12 rounded-full ${pathInfo.bgColor} flex items-center justify-center`}>
              <Star className={`w-6 h-6 ${pathInfo.color}`} />
            </div>
            <div>
              <h2 className={`font-bold ${pathInfo.color}`}>{pathInfo.name}</h2>
              <p className="text-zinc-400 text-sm">{pathInfo.description}</p>
            </div>
          </div>
        </div>

        {/* Evolution Tree Visual */}
        <div className="relative">
          {/* Vertical line */}
          <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-gradient-to-b from-purple-500 via-amber-500 to-green-500 opacity-30" />
          
          {/* Stages */}
          <div className="space-y-6">
            {[1, 2, 3, 4, 5, 6].map((stage) => {
              const stageData = stages[stage];
              const isUnlocked = stage <= currentStage;
              const isCurrent = stage === currentStage;
              
              return (
                <div key={stage} className="relative flex items-center gap-4">
                  {/* Stage indicator */}
                  <div className={`relative z-10 w-16 h-16 rounded-full flex items-center justify-center text-3xl ${
                    isCurrent 
                      ? 'bg-gradient-to-br from-purple-600 to-pink-600 ring-4 ring-purple-500/50 animate-pulse' 
                      : isUnlocked 
                        ? 'bg-zinc-800 ring-2 ring-green-500/50' 
                        : 'bg-zinc-900 ring-2 ring-zinc-700'
                  }`}>
                    {isUnlocked ? (
                      stageData?.icon || '🥚'
                    ) : (
                      <Lock className="w-6 h-6 text-zinc-600" />
                    )}
                  </div>
                  
                  {/* Stage info */}
                  <div className={`flex-1 p-4 rounded-xl border ${
                    isCurrent 
                      ? 'bg-purple-900/20 border-purple-500/50' 
                      : isUnlocked 
                        ? 'bg-zinc-900/50 border-zinc-700' 
                        : 'bg-zinc-900/30 border-zinc-800'
                  }`}>
                    <div className="flex items-center justify-between mb-1">
                      <h3 className={`font-bold ${isUnlocked ? 'text-white' : 'text-zinc-500'}`}>
                        Stage {stage}: {isUnlocked ? (stageData?.name || 'Unlocked') : 'Locked'}
                      </h3>
                      {isUnlocked && (
                        <Check className="w-5 h-5 text-green-400" />
                      )}
                    </div>
                    <p className="text-sm text-zinc-400">
                      {stage === 1 && 'Starting form'}
                      {stage === 2 && 'Unlocks at 7-day streak'}
                      {stage === 3 && 'Unlocks at 30-day streak'}
                      {stage === 4 && 'Unlocks at 60-day streak'}
                      {stage === 5 && 'Unlocks at 90-day streak'}
                      {stage === 6 && 'Unlocks at 100-day streak (Legendary!)'}
                    </p>
                    
                    {/* Branching paths for later stages */}
                    {stage >= 4 && !isUnlocked && (
                      <div className="mt-3 pt-3 border-t border-zinc-700">
                        <p className="text-xs text-zinc-500 mb-2">Potential evolution paths:</p>
                        <div className="flex flex-wrap gap-2">
                          {Object.entries(EVOLUTION_PATHS).map(([key, path]) => (
                            <span 
                              key={key}
                              className={`text-xs px-2 py-1 rounded-full ${path.bgColor} ${path.color}`}
                            >
                              {path.name.replace(' Path', '')}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Habit Breakdown */}
        {habitStats && habitStats.length > 0 && (
          <div className="mt-8">
            <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-amber-400" />
              Your Habit Focus
            </h3>
            <div className="space-y-3">
              {habitStats.map((habit, idx) => {
                const total = habitStats.reduce((sum, h) => sum + h.sessions, 0);
                const percent = total > 0 ? Math.round((habit.sessions / total) * 100) : 0;
                
                return (
                  <div key={idx} className="bg-zinc-900 rounded-lg p-3">
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm text-zinc-300">{habit.pillar}</span>
                      <span className="text-sm text-zinc-400">{percent}%</span>
                    </div>
                    <div className="h-2 bg-zinc-800 rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-gradient-to-r from-purple-500 to-pink-500 rounded-full transition-all duration-500"
                        style={{ width: `${percent}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Info box */}
        <div className="mt-8 bg-zinc-900/50 border border-zinc-800 rounded-xl p-4">
          <h4 className="font-bold text-white mb-2">How Evolution Works</h4>
          <ul className="text-sm text-zinc-400 space-y-2">
            <li>• Your pet evolves as your streak grows</li>
            <li>• Different habit focuses can unlock unique evolution paths</li>
            <li>• At Stage 4+, your dominant habit affects your pet's final form</li>
            <li>• Balanced habits unlock the rare Balanced evolution</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default EvolutionTreeScreen;
