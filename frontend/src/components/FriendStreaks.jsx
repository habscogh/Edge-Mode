import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Flame, Users, TrendingUp } from 'lucide-react';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const FriendStreakCard = ({ streak }) => {
  const getStreakColor = (days) => {
    if (days >= 14) return 'text-orange-400 bg-orange-500/20';
    if (days >= 7) return 'text-amber-400 bg-amber-500/20';
    if (days >= 3) return 'text-yellow-400 bg-yellow-500/20';
    return 'text-zinc-400 bg-zinc-700/30';
  };

  const colorClass = getStreakColor(streak.mutual_streak);

  return (
    <div 
      className="flex items-center justify-between p-3 bg-zinc-950 rounded-lg border border-zinc-800 hover:border-zinc-700 transition-colors"
      data-testid={`friend-streak-${streak.friend_id}`}
    >
      <div className="flex items-center gap-3">
        <div className={`w-10 h-10 rounded-full flex items-center justify-center ${colorClass}`}>
          <Flame className="w-5 h-5" />
        </div>
        <div>
          <p className="text-white font-medium text-sm">@{streak.friend_username}</p>
          <p className="text-zinc-500 text-xs">{streak.total_mutual_days} days together</p>
        </div>
      </div>
      <div className={`px-3 py-1 rounded-full text-sm font-bold ${colorClass}`}>
        {streak.mutual_streak} 🔥
      </div>
    </div>
  );
};

const FriendStreaks = ({ compact = false }) => {
  const [streaks, setStreaks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetchStreaks();
  }, []);

  const fetchStreaks = async () => {
    try {
      const response = await axios.get(`${API}/engagement/friend-streaks`);
      setStreaks(response.data.friend_streaks || []);
      setMessage(response.data.message || '');
    } catch (error) {
      console.error('Failed to fetch friend streaks:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-4 animate-pulse">
        <div className="h-4 bg-zinc-800 rounded w-1/3 mb-3"></div>
        <div className="h-12 bg-zinc-800 rounded"></div>
      </div>
    );
  }

  if (streaks.length === 0) {
    if (compact) return null;
    
    return (
      <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-4">
        <div className="flex items-center gap-2 mb-3">
          <Users className="w-4 h-4 text-primary" />
          <h3 className="text-white font-bold text-sm">Friend Streaks</h3>
        </div>
        <div className="text-center py-4">
          <Users className="w-10 h-10 mx-auto mb-2 text-zinc-600" />
          <p className="text-zinc-500 text-sm">
            {message || 'Join a team or challenge friends to see mutual streaks!'}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-4" data-testid="friend-streaks-section">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Flame className="w-4 h-4 text-orange-400" />
          <h3 className="text-white font-bold text-sm">Friend Streaks</h3>
          <span className="text-xs bg-orange-500/20 text-orange-400 px-2 py-0.5 rounded-full">
            Mutual
          </span>
        </div>
        <div className="flex items-center gap-1 text-zinc-500 text-xs">
          <TrendingUp className="w-3 h-3" />
          <span>{streaks.length} active</span>
        </div>
      </div>

      <div className={`space-y-2 ${compact ? 'max-h-32 overflow-y-auto' : ''}`}>
        {streaks.slice(0, compact ? 3 : 10).map((streak) => (
          <FriendStreakCard key={streak.friend_id} streak={streak} />
        ))}
      </div>

      {compact && streaks.length > 3 && (
        <p className="text-center text-zinc-500 text-xs mt-2">
          +{streaks.length - 3} more streaks
        </p>
      )}
    </div>
  );
};

export default FriendStreaks;
