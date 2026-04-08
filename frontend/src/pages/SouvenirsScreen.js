import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { ArrowLeft, Trophy, Sparkles, Map } from 'lucide-react';
import { toast } from 'sonner';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const rarityStyles = {
  legendary: 'bg-gradient-to-br from-yellow-900/30 to-amber-900/30 border-yellow-500/50 text-yellow-400',
  rare: 'bg-gradient-to-br from-blue-900/30 to-cyan-900/30 border-blue-500/50 text-blue-400',
  uncommon: 'bg-gradient-to-br from-green-900/30 to-emerald-900/30 border-green-500/50 text-green-400',
  common: 'bg-zinc-800/50 border-zinc-600/50 text-zinc-400',
};

const SouvenirsScreen = () => {
  const navigate = useNavigate();
  const [souvenirs, setSouvenirs] = useState([]);
  const [stats, setStats] = useState({ total: 0, by_rarity: {} });
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    fetchSouvenirs();
  }, []);

  const fetchSouvenirs = async () => {
    try {
      const response = await axios.get(`${API}/pets/souvenirs`);
      setSouvenirs(response.data.souvenirs || []);
      setStats({
        total: response.data.total || 0,
        by_rarity: response.data.by_rarity || {}
      });
    } catch (error) {
      toast.error('Failed to load souvenirs');
    } finally {
      setLoading(false);
    }
  };

  const filteredSouvenirs = filter === 'all' 
    ? souvenirs 
    : souvenirs.filter(s => s.rarity === filter);

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
              <Trophy className="w-5 h-5 text-amber-400" />
              Souvenirs
            </h1>
            <p className="text-zinc-400 text-sm">Treasures from your pet's expeditions</p>
          </div>
        </div>

        {/* Stats */}
        <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-4 mb-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Map className="w-5 h-5 text-purple-400" />
              <span className="text-zinc-400">Total Collected</span>
            </div>
            <span className="text-2xl font-bold text-white">{stats.total}</span>
          </div>
          
          {/* Rarity breakdown */}
          <div className="mt-3 flex gap-2 flex-wrap">
            {Object.entries(stats.by_rarity).map(([rarity, items]) => (
              <span 
                key={rarity}
                className={`text-xs px-2 py-1 rounded-full capitalize border ${rarityStyles[rarity]}`}
              >
                {rarity}: {items.length}
              </span>
            ))}
          </div>
        </div>

        {/* Filter */}
        <div className="flex gap-2 overflow-x-auto pb-2">
          {['all', 'legendary', 'rare', 'uncommon', 'common'].map(f => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-all ${
                filter === f
                  ? 'bg-primary text-black'
                  : 'bg-zinc-800 text-zinc-400 hover:bg-zinc-700'
              }`}
            >
              {f.charAt(0).toUpperCase() + f.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      <div className="p-4">
        {filteredSouvenirs.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">🗺️</div>
            <h3 className="text-xl font-bold text-white mb-2">No Souvenirs Yet</h3>
            <p className="text-zinc-400 text-sm">
              Log sessions of 59+ minutes to send your pet on expeditions!
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-2 gap-3">
            {filteredSouvenirs.map(souvenir => (
              <div
                key={souvenir.id}
                className={`rounded-xl p-4 border ${rarityStyles[souvenir.rarity]}`}
                data-testid={`souvenir-${souvenir.id}`}
              >
                <div className="text-4xl mb-2 text-center">{souvenir.icon}</div>
                <h3 className="font-bold text-white text-center text-sm">{souvenir.name}</h3>
                <p className="text-xs text-zinc-400 text-center mt-1">{souvenir.description}</p>
                <div className="flex items-center justify-center gap-2 mt-2">
                  <span className={`text-xs px-2 py-0.5 rounded-full capitalize border ${rarityStyles[souvenir.rarity]}`}>
                    {souvenir.rarity}
                  </span>
                </div>
                {souvenir.from_pillar && (
                  <p className="text-xs text-zinc-500 text-center mt-2">
                    From: {souvenir.from_pillar}
                  </p>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default SouvenirsScreen;
