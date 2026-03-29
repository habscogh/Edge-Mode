import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { TrendingUp, TrendingDown, Flame, CheckCircle2, Trophy, Sparkles, Minus } from 'lucide-react';
import { getLocalDateString } from '../utils/dateUtils';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export const ProgressInsights = () => {
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchInsights();
  }, []);

  const fetchInsights = async () => {
    try {
      const localDate = getLocalDateString();
      const response = await axios.get(`${API}/stats/progress-insights?local_date=${localDate}`);
      setInsights(response.data);
    } catch (error) {
      console.error('Failed to fetch progress insights:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading || !insights) return null;

  const { this_week, last_week, changes, insights: insightMessages, personal_bests } = insights;

  // Don't show if no activity
  if (this_week.sessions === 0 && last_week.sessions === 0) return null;

  const getIcon = (iconType) => {
    switch (iconType) {
      case 'trending_up': return <TrendingUp className="w-4 h-4" />;
      case 'trending_down': return <TrendingDown className="w-4 h-4" />;
      case 'fire': return <Flame className="w-4 h-4" />;
      case 'check_circle': return <CheckCircle2 className="w-4 h-4" />;
      case 'trophy': return <Trophy className="w-4 h-4" />;
      default: return <Sparkles className="w-4 h-4" />;
    }
  };

  return (
    <div className="space-y-3" data-testid="progress-insights">
      {/* Personal Bests Alert */}
      {personal_bests && personal_bests.length > 0 && (
        <div className="bg-gradient-to-r from-amber-500/20 to-yellow-500/20 border border-amber-500/30 rounded-lg p-4">
          <div className="flex items-center gap-2 text-amber-400 font-bold mb-1">
            <Trophy className="w-5 h-5" />
            New Personal Best!
          </div>
          {personal_bests.map((pb, idx) => (
            <p key={idx} className="text-amber-200 text-sm">{pb.message}</p>
          ))}
        </div>
      )}

      {/* Weekly Comparison Card */}
      {(changes.minutes_pct !== 0 || changes.sessions_pct !== 0) && (
        <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-4">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs text-zinc-500 uppercase tracking-wide font-medium">This Week vs Last Week</span>
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            {/* Minutes Comparison */}
            <div className="text-center">
              <div className={`flex items-center justify-center gap-1 text-lg font-bold ${
                changes.minutes_pct > 0 ? 'text-primary' : changes.minutes_pct < 0 ? 'text-red-400' : 'text-zinc-400'
              }`}>
                {changes.minutes_pct > 0 ? (
                  <TrendingUp className="w-5 h-5" />
                ) : changes.minutes_pct < 0 ? (
                  <TrendingDown className="w-5 h-5" />
                ) : (
                  <Minus className="w-5 h-5" />
                )}
                {changes.minutes_pct > 0 ? '+' : ''}{changes.minutes_pct}%
              </div>
              <div className="text-xs text-zinc-500">Time Logged</div>
              <div className="text-sm text-zinc-300 mt-1">
                {this_week.minutes}m vs {last_week.minutes}m
              </div>
            </div>

            {/* Sessions Comparison */}
            <div className="text-center">
              <div className={`flex items-center justify-center gap-1 text-lg font-bold ${
                changes.sessions_pct > 0 ? 'text-primary' : changes.sessions_pct < 0 ? 'text-red-400' : 'text-zinc-400'
              }`}>
                {changes.sessions_pct > 0 ? (
                  <TrendingUp className="w-5 h-5" />
                ) : changes.sessions_pct < 0 ? (
                  <TrendingDown className="w-5 h-5" />
                ) : (
                  <Minus className="w-5 h-5" />
                )}
                {changes.sessions_pct > 0 ? '+' : ''}{changes.sessions_pct}%
              </div>
              <div className="text-xs text-zinc-500">Sessions</div>
              <div className="text-sm text-zinc-300 mt-1">
                {this_week.sessions} vs {last_week.sessions}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Insight Messages */}
      {insightMessages && insightMessages.length > 0 && (
        <div className="space-y-2">
          {insightMessages.slice(0, 2).map((insight, idx) => (
            <div
              key={idx}
              className={`flex items-center gap-3 p-3 rounded-lg ${
                insight.type === 'positive' 
                  ? 'bg-primary/10 border border-primary/20' 
                  : 'bg-zinc-900 border border-zinc-800'
              }`}
            >
              <div className={`${insight.type === 'positive' ? 'text-primary' : 'text-zinc-400'}`}>
                {getIcon(insight.icon)}
              </div>
              <span className={`text-sm font-medium ${
                insight.type === 'positive' ? 'text-primary' : 'text-zinc-300'
              }`}>
                {insight.message}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ProgressInsights;
