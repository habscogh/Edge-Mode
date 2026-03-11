import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { Trophy, Users, Clock, ChevronRight, Flame, Zap, Target, Loader2 } from 'lucide-react';
import { Button } from './ui/button';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const METRIC_ICONS = {
  total_sessions: Zap,
  total_minutes: Clock,
  consistency: Target,
  pillar_sessions: Flame,
  pillar_minutes: Clock
};

export const FeaturedChallenges = () => {
  const navigate = useNavigate();
  const [challenges, setChallenges] = useState([]);
  const [loading, setLoading] = useState(true);
  const [joining, setJoining] = useState(null);

  useEffect(() => {
    fetchFeatured();
  }, []);

  const fetchFeatured = async () => {
    try {
      const response = await axios.get(`${API}/challenges/featured`);
      setChallenges(response.data || []);
    } catch (error) {
      console.error('Failed to fetch featured challenges:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleJoin = async (challengeId, e) => {
    e.stopPropagation();
    setJoining(challengeId);
    try {
      await axios.post(`${API}/challenges/join`, { challenge_id: challengeId });
      toast.success('Joined challenge!');
      fetchFeatured();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to join');
    } finally {
      setJoining(null);
    }
  };

  const getDaysLeft = (endDate) => {
    const end = new Date(endDate);
    const now = new Date();
    const diff = Math.ceil((end - now) / (1000 * 60 * 60 * 24));
    return diff > 0 ? diff : 0;
  };

  if (loading) {
    return (
      <div className="bg-zinc-950 border border-zinc-800 rounded-lg p-4 mb-6">
        <div className="flex items-center justify-center py-4">
          <Loader2 className="w-5 h-5 text-primary animate-spin" />
        </div>
      </div>
    );
  }

  if (challenges.length === 0) {
    return null;
  }

  return (
    <div className="mb-6">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-heading uppercase tracking-wide text-white flex items-center gap-2">
          <Trophy className="w-4 h-4 text-yellow-400" />
          Active Challenges
        </h3>
        <button 
          onClick={() => navigate('/challenges')}
          className="text-xs text-primary hover:text-primary/80 flex items-center gap-1"
        >
          View All <ChevronRight className="w-3 h-3" />
        </button>
      </div>

      <div className="space-y-3">
        {challenges.map(challenge => {
          const MetricIcon = METRIC_ICONS[challenge.metric_type] || Zap;
          const daysLeft = getDaysLeft(challenge.end_date);
          
          return (
            <div 
              key={challenge.id}
              onClick={() => navigate('/challenges')}
              className="bg-gradient-to-r from-zinc-900 to-zinc-950 border border-zinc-800 rounded-lg p-4 cursor-pointer hover:border-zinc-700 transition-all group"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <Trophy className="w-4 h-4 text-yellow-400" />
                    <span className="font-heading font-bold text-white text-sm uppercase">
                      {challenge.name}
                    </span>
                    {challenge.featured && (
                      <span className="text-[10px] px-1.5 py-0.5 bg-yellow-500/20 text-yellow-400 rounded-full border border-yellow-500/30">
                        Featured
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-zinc-500 line-clamp-1">{challenge.description}</p>
                </div>
                
                {!challenge.is_participating ? (
                  <Button
                    onClick={(e) => handleJoin(challenge.id, e)}
                    disabled={joining === challenge.id}
                    size="sm"
                    className="bg-primary/20 text-primary hover:bg-primary/30 text-xs ml-2"
                  >
                    {joining === challenge.id ? (
                      <Loader2 className="w-3 h-3 animate-spin" />
                    ) : (
                      'Join'
                    )}
                  </Button>
                ) : (
                  <div className="text-xs text-primary bg-primary/10 px-2 py-1 rounded border border-primary/30">
                    #{challenge.user_rank || '—'}
                  </div>
                )}
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3 text-xs text-zinc-500">
                  <span className="flex items-center gap-1">
                    <MetricIcon className="w-3 h-3" />
                    {challenge.metric_type.replace('_', ' ')}
                  </span>
                  <span className="flex items-center gap-1">
                    <Users className="w-3 h-3" />
                    {challenge.participant_count || 0}
                  </span>
                  <span className="flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    {daysLeft}d left
                  </span>
                </div>

                {/* Mini leaderboard preview */}
                {challenge.top_participants?.length > 0 && (
                  <div className="flex items-center -space-x-1">
                    {challenge.top_participants.slice(0, 3).map((p, i) => (
                      <div
                        key={p.user_id}
                        className={`w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold border-2 border-zinc-950 ${
                          i === 0 ? 'bg-yellow-500 text-black' :
                          i === 1 ? 'bg-zinc-400 text-black' :
                          'bg-amber-700 text-white'
                        }`}
                        title={`${p.username}: ${p.current_score?.toFixed(0) || 0}`}
                      >
                        {p.username?.charAt(0).toUpperCase() || '?'}
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Progress bar for participating users */}
              {challenge.is_participating && challenge.user_score > 0 && (
                <div className="mt-3 pt-3 border-t border-zinc-800">
                  <div className="flex items-center justify-between text-xs mb-1">
                    <span className="text-zinc-500">Your Score</span>
                    <span className="text-primary font-mono">{challenge.user_score?.toFixed(1) || 0}</span>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
