import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'sonner';
import { Button } from '../components/ui/button';
import { BulkInviteSection } from '../components/BulkInviteSection';
import { 
  ArrowLeft, 
  Users, 
  TrendingUp, 
  Calendar,
  Flame,
  Target,
  ChevronRight,
  Clock,
  Award
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const PlayerCard = ({ player, onViewDetails }) => {
  const getStreakColor = (streak) => {
    if (streak >= 14) return 'text-amber-400';
    if (streak >= 7) return 'text-primary';
    return 'text-zinc-400';
  };

  return (
    <div 
      className="bg-zinc-950 border border-zinc-800 rounded-lg p-4 cursor-pointer hover:border-zinc-700 transition-colors"
      onClick={() => onViewDetails(player.id)}
      data-testid={`player-card-${player.id}`}
    >
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-primary/20 rounded-full flex items-center justify-center">
            <span className="text-primary font-bold">{player.username?.charAt(0).toUpperCase()}</span>
          </div>
          <div>
            <h3 className="text-white font-medium">{player.username}</h3>
            <span className="text-zinc-500 text-sm">Age {player.age}</span>
          </div>
        </div>
        <ChevronRight className="w-5 h-5 text-zinc-500" />
      </div>

      <div className="grid grid-cols-3 gap-3 mb-3">
        <div className="text-center">
          <div className={`font-mono font-bold ${getStreakColor(player.current_streak)}`}>
            {player.current_streak}
          </div>
          <div className="text-zinc-500 text-xs">Streak</div>
        </div>
        <div className="text-center">
          <div className="font-mono font-bold text-primary">{player.consistency_pct}%</div>
          <div className="text-zinc-500 text-xs">Consistency</div>
        </div>
        <div className="text-center">
          <div className="font-mono font-bold text-white">{player.sessions_this_week}</div>
          <div className="text-zinc-500 text-xs">Sessions</div>
        </div>
      </div>

      {player.pillar_breakdown && player.pillar_breakdown.length > 0 && (
        <div className="border-t border-zinc-800 pt-3">
          <div className="flex flex-wrap gap-2">
            {player.pillar_breakdown.slice(0, 3).map((pillar, idx) => (
              <span 
                key={idx}
                className="text-xs bg-zinc-900 px-2 py-1 rounded text-zinc-400"
              >
                {pillar.pillar_name.split('/')[0]}: {pillar.sessions}/{pillar.target}
              </span>
            ))}
          </div>
        </div>
      )}

      {player.last_active && (
        <div className="text-xs text-zinc-500 mt-2">
          Last active: {player.last_active}
        </div>
      )}
    </div>
  );
};

const PlayerDetailsModal = ({ player, onClose }) => {
  if (!player) return null;

  return (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
      <div className="bg-zinc-950 border border-zinc-800 rounded-lg w-full max-w-md max-h-[80vh] overflow-hidden">
        <div className="p-4 border-b border-zinc-800 flex items-center justify-between">
          <div>
            <h2 className="text-white font-bold">{player.player?.username}</h2>
            <p className="text-zinc-500 text-sm">Age {player.player?.age}</p>
          </div>
          <button onClick={onClose} className="text-zinc-400 hover:text-white text-2xl">&times;</button>
        </div>

        <div className="p-4 overflow-y-auto max-h-[60vh]">
          {/* Streaks */}
          <div className="bg-zinc-900 rounded-lg p-4 mb-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Flame className="w-5 h-5 text-amber-500" />
                <span className="text-white">Current Streak</span>
              </div>
              <span className="font-mono font-bold text-amber-500">{player.player?.current_streak} days</span>
            </div>
            <div className="flex items-center justify-between mt-2">
              <span className="text-zinc-400 text-sm">Longest Streak</span>
              <span className="font-mono text-zinc-300">{player.player?.longest_streak} days</span>
            </div>
          </div>

          {/* Weekly Stats */}
          <div className="bg-zinc-900 rounded-lg p-4 mb-4">
            <h3 className="text-white font-medium mb-3">This Week</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <div className="text-2xl font-mono font-bold text-primary">{player.weekly_stats?.sessions}</div>
                <div className="text-zinc-500 text-sm">Sessions</div>
              </div>
              <div>
                <div className="text-2xl font-mono font-bold text-white">{player.weekly_stats?.consistency_pct}%</div>
                <div className="text-zinc-500 text-sm">Consistency</div>
              </div>
              <div>
                <div className="text-2xl font-mono font-bold text-zinc-300">{player.weekly_stats?.unique_days}</div>
                <div className="text-zinc-500 text-sm">Days Active</div>
              </div>
              <div>
                <div className="text-2xl font-mono font-bold text-zinc-300">{player.weekly_stats?.minutes}</div>
                <div className="text-zinc-500 text-sm">Minutes</div>
              </div>
            </div>
          </div>

          {/* Pillars */}
          {player.pillars && player.pillars.length > 0 && (
            <div className="bg-zinc-900 rounded-lg p-4 mb-4">
              <h3 className="text-white font-medium mb-3">Pillars</h3>
              <div className="space-y-2">
                {player.pillars.map((pillar, idx) => (
                  <div key={idx} className="flex items-center justify-between">
                    <span className="text-zinc-400">{pillar.pillar_name}</span>
                    <span className="text-white font-mono">{pillar.weekly_target_sessions}/week</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Badges */}
          <div className="flex items-center gap-2 text-zinc-400">
            <Award className="w-4 h-4" />
            <span>{player.badges_earned} badges earned</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export const CoachDashboard = () => {
  const { groupId } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [dashboard, setDashboard] = useState(null);
  const [selectedPlayer, setSelectedPlayer] = useState(null);
  const [playerDetails, setPlayerDetails] = useState(null);

  useEffect(() => {
    fetchDashboard();
  }, [groupId]);

  const fetchDashboard = async () => {
    try {
      const response = await axios.get(`${API}/groups/${groupId}/coach/dashboard`);
      setDashboard(response.data);
    } catch (error) {
      console.error('Failed to fetch coach dashboard:', error);
      if (error.response?.status === 403) {
        toast.error('Only the coach can access this dashboard');
        navigate(-1);
      } else {
        toast.error('Failed to load dashboard');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleViewPlayerDetails = async (playerId) => {
    try {
      const response = await axios.get(`${API}/groups/${groupId}/coach/player/${playerId}`);
      setPlayerDetails(response.data);
      setSelectedPlayer(playerId);
    } catch (error) {
      console.error('Failed to fetch player details:', error);
      toast.error('Failed to load player details');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-[#09090b]">
        <div className="text-zinc-400 font-mono">Loading dashboard...</div>
      </div>
    );
  }

  if (!dashboard) {
    return (
      <div className="min-h-screen bg-[#09090b] p-4">
        <Button onClick={() => navigate(-1)} variant="ghost" className="text-zinc-400">
          <ArrowLeft className="w-5 h-5 mr-2" /> Back
        </Button>
        <div className="text-center py-12 text-zinc-500">Dashboard not available</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#09090b] pb-24">
      {/* Header */}
      <div className="bg-zinc-950 border-b border-zinc-800 p-4">
        <div className="flex items-center gap-3 mb-4">
          <button onClick={() => navigate(-1)} className="text-zinc-400 hover:text-white">
            <ArrowLeft className="w-6 h-6" />
          </button>
          <div>
            <h1 className="text-xl font-bold text-white">{dashboard.group?.name}</h1>
            <p className="text-zinc-500 text-sm">Coach Dashboard</p>
          </div>
        </div>

        {/* Team Stats */}
        <div className="grid grid-cols-4 gap-2">
          <div className="bg-zinc-900 rounded-lg p-3 text-center">
            <div className="flex items-center justify-center mb-1">
              <Users className="w-4 h-4 text-primary" />
            </div>
            <div className="text-xl font-mono font-bold text-white">{dashboard.team_stats?.total_players}</div>
            <div className="text-zinc-500 text-xs">Players</div>
          </div>
          <div className="bg-zinc-900 rounded-lg p-3 text-center">
            <div className="flex items-center justify-center mb-1">
              <Target className="w-4 h-4 text-primary" />
            </div>
            <div className="text-xl font-mono font-bold text-primary">{dashboard.team_stats?.avg_consistency}%</div>
            <div className="text-zinc-500 text-xs">Avg Consistency</div>
          </div>
          <div className="bg-zinc-900 rounded-lg p-3 text-center">
            <div className="flex items-center justify-center mb-1">
              <TrendingUp className="w-4 h-4 text-primary" />
            </div>
            <div className="text-xl font-mono font-bold text-white">{dashboard.team_stats?.avg_performance}</div>
            <div className="text-zinc-500 text-xs">Avg Performance</div>
          </div>
          <div className="bg-zinc-900 rounded-lg p-3 text-center">
            <div className="flex items-center justify-center mb-1">
              <Calendar className="w-4 h-4 text-primary" />
            </div>
            <div className="text-xl font-mono font-bold text-white">{dashboard.team_stats?.total_sessions_this_week}</div>
            <div className="text-zinc-500 text-xs">Sessions</div>
          </div>
        </div>
      </div>

      {/* Players List */}
      <div className="p-4">
        <h2 className="text-white font-medium mb-3">Players ({dashboard.players?.length || 0})</h2>
        
        {dashboard.players?.length === 0 ? (
          <div className="text-center py-12">
            <Users className="w-12 h-12 text-zinc-700 mx-auto mb-4" />
            <h3 className="text-zinc-400 font-medium mb-2">No players yet</h3>
            <p className="text-zinc-500 text-sm">Share your group invite code to add players</p>
            <div className="mt-4 bg-zinc-900 rounded-lg p-4 inline-block">
              <div className="text-zinc-400 text-sm mb-1">Invite Code</div>
              <div className="text-primary font-mono font-bold text-lg">{dashboard.group?.invite_code}</div>
            </div>
          </div>
        ) : (
          <div className="space-y-3">
            {dashboard.players.map(player => (
              <PlayerCard 
                key={player.id} 
                player={player} 
                onViewDetails={handleViewPlayerDetails}
              />
            ))}
          </div>
        )}
      </div>

      {/* Player Details Modal */}
      {selectedPlayer && playerDetails && (
        <PlayerDetailsModal 
          player={playerDetails}
          onClose={() => {
            setSelectedPlayer(null);
            setPlayerDetails(null);
          }}
        />
      )}
    </div>
  );
};

export default CoachDashboard;
