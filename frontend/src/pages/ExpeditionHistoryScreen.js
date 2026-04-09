import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { ArrowLeft, Map, Coins, Zap, Trophy, Clock, Sparkles, Share2 } from 'lucide-react';
import { toast } from 'sonner';
import ShareableStoryCard from '../components/ShareableStoryCard';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const rarityStyles = {
  legendary: {
    bg: 'bg-gradient-to-br from-yellow-900/30 to-amber-900/30',
    border: 'border-yellow-500/50',
    text: 'text-yellow-400',
    badge: 'bg-yellow-500/20 text-yellow-400'
  },
  rare: {
    bg: 'bg-gradient-to-br from-blue-900/30 to-cyan-900/30',
    border: 'border-blue-500/50',
    text: 'text-blue-400',
    badge: 'bg-blue-500/20 text-blue-400'
  },
  uncommon: {
    bg: 'bg-gradient-to-br from-green-900/30 to-emerald-900/30',
    border: 'border-green-500/50',
    text: 'text-green-400',
    badge: 'bg-green-500/20 text-green-400'
  },
  common: {
    bg: 'bg-zinc-800/50',
    border: 'border-zinc-600/50',
    text: 'text-zinc-400',
    badge: 'bg-zinc-700 text-zinc-400'
  }
};

const ExpeditionHistoryScreen = () => {
  const navigate = useNavigate();
  const [expeditions, setExpeditions] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [selectedExpedition, setSelectedExpedition] = useState(null);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const response = await axios.get(`${API}/pets/expedition-history`);
      setExpeditions(response.data.expeditions || []);
      setStats(response.data.stats || null);
    } catch (error) {
      toast.error('Failed to load expedition history');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  const filteredExpeditions = filter === 'all'
    ? expeditions
    : expeditions.filter(e => e.rarity === filter);

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
              <Map className="w-5 h-5 text-amber-400" />
              Adventure Log
            </h1>
            <p className="text-zinc-400 text-sm">Your pet's expedition history</p>
          </div>
        </div>

        {/* Stats Overview */}
        {stats && expeditions.length > 0 && (
          <div className="grid grid-cols-4 gap-2 mb-4">
            <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-3 text-center">
              <div className="text-xl font-bold text-white">{stats.total_coins_earned}</div>
              <div className="text-xs text-zinc-500 flex items-center justify-center gap-1">
                <Coins className="w-3 h-3 text-yellow-400" /> Coins
              </div>
            </div>
            <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-3 text-center">
              <div className="text-xl font-bold text-white">{stats.total_xp_earned}</div>
              <div className="text-xs text-zinc-500 flex items-center justify-center gap-1">
                <Zap className="w-3 h-3 text-purple-400" /> XP
              </div>
            </div>
            <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-3 text-center">
              <div className="text-xl font-bold text-white">{stats.items_found}</div>
              <div className="text-xs text-zinc-500 flex items-center justify-center gap-1">
                <Trophy className="w-3 h-3 text-amber-400" /> Items
              </div>
            </div>
            <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-3 text-center">
              <div className="text-xl font-bold text-white">{expeditions.length}</div>
              <div className="text-xs text-zinc-500 flex items-center justify-center gap-1">
                <Map className="w-3 h-3 text-emerald-400" /> Trips
              </div>
            </div>
          </div>
        )}

        {/* Rarity Filter */}
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
              {f !== 'all' && stats?.by_rarity?.[f] > 0 && (
                <span className="ml-1 opacity-60">({stats.by_rarity[f]})</span>
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      <div className="p-4">
        {filteredExpeditions.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">🗺️</div>
            <h3 className="text-xl font-bold text-white mb-2">No Adventures Yet</h3>
            <p className="text-zinc-400 text-sm">
              Log sessions of 59+ minutes to send your pet on expeditions!
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {/* Timeline */}
            {filteredExpeditions.map((expedition, index) => {
              const style = rarityStyles[expedition.rarity] || rarityStyles.common;
              
              return (
                <div
                  key={expedition.id}
                  className={`relative rounded-xl border ${style.bg} ${style.border} p-4 transition-all`}
                  data-testid={`expedition-${expedition.id}`}
                >
                  {/* Timeline connector */}
                  {index < filteredExpeditions.length - 1 && (
                    <div className="absolute left-7 top-full w-0.5 h-4 bg-zinc-700" />
                  )}

                  {/* Header */}
                  <div className="flex items-start gap-3 mb-3">
                    {/* Pet Icon */}
                    <div className="w-12 h-12 rounded-full bg-black/30 flex items-center justify-center text-2xl flex-shrink-0">
                      {expedition.pet_icon || '🐾'}
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <h3 className="font-bold text-white">{expedition.expedition_name}</h3>
                        <span className={`text-xs px-2 py-0.5 rounded-full capitalize ${style.badge}`}>
                          {expedition.rarity}
                        </span>
                      </div>
                      <div className="flex items-center gap-2 text-xs text-zinc-500 mt-1">
                        <Clock className="w-3 h-3" />
                        <span>{formatDate(expedition.completed_at)}</span>
                        <span>•</span>
                        <span>{expedition.duration_minutes} min</span>
                        <span>•</span>
                        <span>{expedition.pillar}</span>
                      </div>
                    </div>
                  </div>

                  {/* Story */}
                  <div className="bg-black/20 rounded-lg p-3 mb-3">
                    <p className="text-sm text-zinc-300 italic">"{expedition.story}"</p>
                  </div>

                  {/* Rewards */}
                  <div className="flex items-center gap-3 flex-wrap">
                    <div className="flex items-center gap-1.5 bg-yellow-500/10 text-yellow-400 px-2.5 py-1 rounded-full text-sm">
                      <Coins className="w-4 h-4" />
                      <span>+{expedition.rewards?.coins || 0}</span>
                    </div>
                    <div className="flex items-center gap-1.5 bg-purple-500/10 text-purple-400 px-2.5 py-1 rounded-full text-sm">
                      <Zap className="w-4 h-4" />
                      <span>+{expedition.rewards?.xp || 0}</span>
                    </div>
                    {expedition.rewards?.item && (
                      <div className="flex items-center gap-1.5 bg-amber-500/10 text-amber-400 px-2.5 py-1 rounded-full text-sm">
                        <span className="text-lg">{expedition.rewards.item.icon}</span>
                        <span>{expedition.rewards.item.name}</span>
                      </div>
                    )}
                    {/* Share button */}
                    <button
                      onClick={() => setSelectedExpedition(expedition)}
                      className="ml-auto flex items-center gap-1.5 bg-pink-500/10 text-pink-400 px-2.5 py-1 rounded-full text-sm hover:bg-pink-500/20 transition-colors"
                      data-testid={`share-expedition-${expedition.id}`}
                    >
                      <Share2 className="w-4 h-4" />
                      <span>Share</span>
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
      
      {/* Shareable Story Card Modal */}
      {selectedExpedition && (
        <ShareableStoryCard
          expedition={selectedExpedition}
          onClose={() => setSelectedExpedition(null)}
        />
      )}
    </div>
  );
};

export default ExpeditionHistoryScreen;
