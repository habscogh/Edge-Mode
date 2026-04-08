import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { ArrowLeft, Lock, Check, Sparkles } from 'lucide-react';
import { toast } from 'sonner';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const CompanionsScreen = () => {
  const navigate = useNavigate();
  const [companions, setCompanions] = useState([]);
  const [activeCompanion, setActiveCompanion] = useState(null);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({ unlocked: 0, total: 0 });

  useEffect(() => {
    fetchCompanions();
  }, []);

  const fetchCompanions = async () => {
    try {
      const response = await axios.get(`${API}/pets/companions`);
      setCompanions(response.data.companions);
      setActiveCompanion(response.data.active_companion);
      setStats({
        unlocked: response.data.unlocked_count,
        total: response.data.total_count
      });
      
      if (response.data.newly_unlocked?.length > 0) {
        toast.success(`New companions unlocked: ${response.data.newly_unlocked.join(', ')}!`);
      }
    } catch (error) {
      toast.error('Failed to load companions');
    } finally {
      setLoading(false);
    }
  };

  const activateCompanion = async (companionId) => {
    try {
      const response = await axios.post(`${API}/pets/companions/${companionId}/activate`);
      setActiveCompanion(companionId);
      toast.success(response.data.message);
    } catch (error) {
      toast.error('Failed to activate companion');
    }
  };

  const deactivateCompanion = async () => {
    try {
      await axios.post(`${API}/pets/companions/deactivate`);
      setActiveCompanion(null);
      toast.success('Companion deactivated');
    } catch (error) {
      toast.error('Failed to deactivate companion');
    }
  };

  const getRarityStyle = (rarity) => {
    const styles = {
      legendary: { bg: 'from-yellow-500/20 to-amber-500/20', border: 'border-yellow-500/50', text: 'text-yellow-400' },
      epic: { bg: 'from-purple-500/20 to-violet-500/20', border: 'border-purple-500/50', text: 'text-purple-400' },
      rare: { bg: 'from-blue-500/20 to-cyan-500/20', border: 'border-blue-500/50', text: 'text-blue-400' },
      uncommon: { bg: 'from-green-500/20 to-emerald-500/20', border: 'border-green-500/50', text: 'text-green-400' },
      common: { bg: 'from-zinc-700/20 to-zinc-600/20', border: 'border-zinc-600/50', text: 'text-zinc-400' },
    };
    return styles[rarity] || styles.common;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black text-white pb-20">
      {/* Header */}
      <div className="bg-gradient-to-b from-zinc-900 to-black p-4 sticky top-0 z-10">
        <div className="flex items-center gap-3 mb-4">
          <button onClick={() => navigate(-1)} className="p-2 hover:bg-zinc-800 rounded-lg">
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h1 className="text-xl font-heading font-bold uppercase flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-yellow-400" />
              Companions
            </h1>
            <p className="text-zinc-400 text-sm">Tiny pets that follow you</p>
          </div>
        </div>

        {/* Stats */}
        <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-3 flex items-center justify-between">
          <div>
            <p className="text-zinc-400 text-xs">Collected</p>
            <p className="text-white font-bold">{stats.unlocked} / {stats.total}</p>
          </div>
          <div className="text-right">
            <p className="text-zinc-400 text-xs">Progress</p>
            <p className="text-primary font-bold">{Math.round((stats.unlocked / stats.total) * 100)}%</p>
          </div>
        </div>
      </div>

      {/* Companions List */}
      <div className="p-4 space-y-3">
        {companions.map(companion => {
          const style = getRarityStyle(companion.rarity);
          const isActive = activeCompanion === companion.id;
          
          return (
            <div
              key={companion.id}
              className={`rounded-xl border p-4 transition-all ${
                companion.is_unlocked
                  ? `bg-gradient-to-r ${style.bg} ${style.border} ${isActive ? 'ring-2 ring-primary' : ''}`
                  : 'bg-zinc-900/50 border-zinc-800 opacity-70'
              }`}
            >
              <div className="flex items-center gap-4">
                {/* Icon */}
                <div className={`w-14 h-14 rounded-full flex items-center justify-center text-3xl ${
                  companion.is_unlocked 
                    ? 'bg-black/30' 
                    : 'bg-zinc-800'
                }`}>
                  {companion.is_unlocked ? companion.icon : '❓'}
                </div>

                {/* Info */}
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <h3 className={`font-bold ${companion.is_unlocked ? 'text-white' : 'text-zinc-500'}`}>
                      {companion.is_unlocked ? companion.name : '???'}
                    </h3>
                    <span className={`text-xs px-2 py-0.5 rounded-full capitalize ${style.bg} ${style.text}`}>
                      {companion.rarity}
                    </span>
                  </div>
                  <p className={`text-xs mt-1 ${companion.is_unlocked ? 'text-zinc-400' : 'text-zinc-600'}`}>
                    {companion.is_unlocked ? companion.description : `Unlock progress: ${companion.progress}/${companion.threshold}`}
                  </p>
                  
                  {/* Bonus */}
                  {companion.is_unlocked && companion.bonus && (
                    <div className="mt-2 flex gap-2 flex-wrap">
                      {companion.bonus.xp_multiplier && (
                        <span className="text-xs bg-green-500/20 text-green-400 px-2 py-0.5 rounded-full">
                          +{Math.round((companion.bonus.xp_multiplier - 1) * 100)}% XP
                        </span>
                      )}
                      {companion.bonus.coin_bonus && (
                        <span className="text-xs bg-yellow-500/20 text-yellow-400 px-2 py-0.5 rounded-full">
                          +{companion.bonus.coin_bonus} coins/session
                        </span>
                      )}
                    </div>
                  )}

                  {/* Progress bar for locked */}
                  {!companion.is_unlocked && companion.threshold > 0 && (
                    <div className="mt-2">
                      <div className="h-1.5 bg-zinc-800 rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-zinc-600 transition-all"
                          style={{ width: `${companion.progress_percent}%` }}
                        />
                      </div>
                    </div>
                  )}
                </div>

                {/* Action */}
                {companion.is_unlocked ? (
                  <button
                    onClick={() => isActive ? deactivateCompanion() : activateCompanion(companion.id)}
                    className={`px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                      isActive
                        ? 'bg-primary text-black'
                        : 'bg-zinc-800 text-white hover:bg-zinc-700'
                    }`}
                  >
                    {isActive ? <Check className="w-4 h-4" /> : 'Use'}
                  </button>
                ) : (
                  <Lock className="w-5 h-5 text-zinc-600" />
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default CompanionsScreen;
