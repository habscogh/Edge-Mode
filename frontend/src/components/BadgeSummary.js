import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { Trophy, ChevronRight } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export const BadgeSummary = () => {
  const navigate = useNavigate();
  const [badges, setBadges] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchBadges();
  }, []);

  const fetchBadges = async () => {
    try {
      const response = await axios.get(`${API}/badges/user`);
      setBadges(response.data);
    } catch (error) {
      console.error('Failed to fetch badges:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-zinc-950 border border-zinc-800 rounded-lg p-4 animate-pulse">
        <div className="h-6 bg-zinc-800 rounded w-24 mb-3"></div>
        <div className="h-10 bg-zinc-800 rounded"></div>
      </div>
    );
  }

  const recentBadges = badges?.earned_badges?.slice(0, 3) || [];

  return (
    <div 
      className="bg-zinc-950 border border-zinc-800 rounded-lg p-4 cursor-pointer hover:border-zinc-700 transition-colors"
      onClick={() => navigate('/achievements')}
      data-testid="badge-summary"
    >
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Trophy className="w-4 h-4 text-primary" />
          <span className="text-sm font-heading uppercase tracking-wide text-zinc-400">
            Achievements
          </span>
        </div>
        <div className="flex items-center gap-1 text-zinc-500">
          <span className="text-xs font-mono">
            {badges?.total_earned || 0}/{badges?.total_available || 0}
          </span>
          <ChevronRight className="w-4 h-4" />
        </div>
      </div>

      {recentBadges.length > 0 ? (
        <div className="flex gap-2">
          {recentBadges.map((badge) => (
            <div 
              key={badge.id}
              className="w-10 h-10 bg-primary/20 rounded-full flex items-center justify-center"
              title={badge.name}
            >
              <span className="text-lg">{badge.icon}</span>
            </div>
          ))}
          {badges?.total_earned > 3 && (
            <div className="w-10 h-10 bg-zinc-800 rounded-full flex items-center justify-center">
              <span className="text-xs font-mono text-zinc-400">+{badges.total_earned - 3}</span>
            </div>
          )}
        </div>
      ) : (
        <p className="text-zinc-600 text-sm font-body">
          Start logging sessions to earn badges!
        </p>
      )}
    </div>
  );
};
