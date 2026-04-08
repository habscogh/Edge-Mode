import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { ArrowLeft, BookOpen, Trophy, Sparkles, Lock } from 'lucide-react';
import { toast } from 'sonner';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const PetCodexScreen = () => {
  const navigate = useNavigate();
  const [codex, setCodex] = useState(null);
  const [activeTab, setActiveTab] = useState('pets');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCodex();
  }, []);

  const fetchCodex = async () => {
    try {
      const response = await axios.get(`${API}/pets/codex`);
      setCodex(response.data);
    } catch (error) {
      toast.error('Failed to load codex');
    } finally {
      setLoading(false);
    }
  };

  const getRarityStyle = (rarity) => {
    const styles = {
      legendary: 'bg-gradient-to-r from-yellow-500/20 to-amber-500/20 border-yellow-500/50 text-yellow-400',
      epic: 'bg-gradient-to-r from-purple-500/20 to-violet-500/20 border-purple-500/50 text-purple-400',
      rare: 'bg-gradient-to-r from-blue-500/20 to-cyan-500/20 border-blue-500/50 text-blue-400',
      uncommon: 'bg-gradient-to-r from-green-500/20 to-emerald-500/20 border-green-500/50 text-green-400',
      common: 'bg-zinc-800/50 border-zinc-600/50 text-zinc-400',
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
            <h1 className="text-xl font-heading font-bold uppercase">Pet Codex</h1>
            <p className="text-zinc-400 text-sm">Your collection progress</p>
          </div>
        </div>

        {/* Completion Progress */}
        {codex && (
          <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-4 mb-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-zinc-400 text-sm">Overall Completion</span>
              <span className="text-primary font-bold">{codex.completion.percent}%</span>
            </div>
            <div className="h-3 bg-zinc-800 rounded-full overflow-hidden">
              <div 
                className="h-full bg-gradient-to-r from-primary to-emerald-400 transition-all duration-500"
                style={{ width: `${codex.completion.percent}%` }}
              />
            </div>
            <div className="flex justify-between mt-2 text-xs text-zinc-500">
              <span>{codex.completion.owned} collected</span>
              <span>{codex.completion.total} total</span>
            </div>
          </div>
        )}

        {/* Tabs */}
        <div className="flex gap-2">
          {[
            { id: 'pets', label: 'Pets', icon: '🐾', count: codex?.pets },
            { id: 'companions', label: 'Companions', icon: '✨', count: codex?.companions },
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex-1 py-2 px-3 rounded-lg text-sm font-medium transition-all ${
                activeTab === tab.id
                  ? 'bg-primary/20 text-primary border border-primary/30'
                  : 'bg-zinc-900 text-zinc-400 border border-zinc-800 hover:border-zinc-700'
              }`}
            >
              <span className="mr-1">{tab.icon}</span>
              {tab.label}
              {tab.count && (
                <span className="ml-1 text-xs opacity-60">
                  ({tab.count.owned}/{tab.count.total})
                </span>
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      <div className="p-4">
        {/* Pets Grid */}
        {activeTab === 'pets' && codex?.pets?.items && (
          <div className="grid grid-cols-2 gap-3">
            {codex.pets.items.map(pet => (
              <div
                key={pet.id}
                className={`rounded-xl p-4 border transition-all ${
                  pet.owned
                    ? getRarityStyle(pet.rarity)
                    : 'bg-zinc-900/50 border-zinc-800 opacity-60'
                }`}
              >
                <div className="flex justify-between items-start mb-2">
                  <span className="text-3xl">{pet.owned ? pet.icon : '❓'}</span>
                  {!pet.owned && <Lock className="w-4 h-4 text-zinc-600" />}
                </div>
                <h3 className={`font-bold text-sm ${pet.owned ? 'text-white' : 'text-zinc-500'}`}>
                  {pet.owned ? pet.name : '???'}
                </h3>
                <p className={`text-xs capitalize ${pet.owned ? '' : 'text-zinc-600'}`}>
                  {pet.rarity}
                </p>
                {pet.owned && (
                  <div className="mt-2 text-xs text-zinc-400">
                    {pet.icon} → {pet.max_icon}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {/* Companions Grid */}
        {activeTab === 'companions' && codex?.companions?.items && (
          <div className="space-y-3">
            {codex.companions.items.map(comp => (
              <div
                key={comp.id}
                className={`rounded-xl p-4 border flex items-center gap-4 ${
                  comp.owned
                    ? getRarityStyle(comp.rarity)
                    : 'bg-zinc-900/50 border-zinc-800 opacity-60'
                }`}
              >
                <div className="text-3xl">
                  {comp.owned ? comp.icon : '❓'}
                </div>
                <div className="flex-1">
                  <h3 className={`font-bold ${comp.owned ? 'text-white' : 'text-zinc-500'}`}>
                    {comp.owned ? comp.name : '???'}
                  </h3>
                  <p className={`text-xs ${comp.owned ? 'text-zinc-400' : 'text-zinc-600'}`}>
                    {comp.owned ? comp.description : `Unlock via ${comp.unlock_type}`}
                  </p>
                  <span className={`text-xs capitalize mt-1 inline-block px-2 py-0.5 rounded-full ${
                    comp.owned ? getRarityStyle(comp.rarity) : 'bg-zinc-800 text-zinc-500'
                  }`}>
                    {comp.rarity}
                  </span>
                </div>
                {!comp.owned && <Lock className="w-5 h-5 text-zinc-600" />}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default PetCodexScreen;
