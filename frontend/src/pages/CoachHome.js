import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'sonner';
import { Button } from '../components/ui/button';
import { 
  Users, 
  Trophy,
  TrendingUp,
  Calendar,
  Copy,
  Check,
  Share2,
  Settings,
  LogOut,
  ClipboardList,
  Sparkles
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export const CoachHome = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [loading, setLoading] = useState(true);
  const [dashboard, setDashboard] = useState(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    fetchDashboard();
  }, []);

  const fetchDashboard = async () => {
    try {
      const response = await axios.get(`${API}/coach/dashboard`);
      setDashboard(response.data);
    } catch (error) {
      console.error('Failed to fetch coach dashboard:', error);
      if (error.response?.status === 403) {
        toast.error('Coach access required');
        navigate('/dashboard');
      }
    } finally {
      setLoading(false);
    }
  };

  const copyInviteLink = () => {
    const fullLink = `${window.location.origin}/join/${dashboard.team.invite_code}`;
    navigator.clipboard.writeText(fullLink);
    setCopied(true);
    toast.success('Invite link copied!');
    setTimeout(() => setCopied(false), 2000);
  };

  const shareInviteLink = async () => {
    const fullLink = `${window.location.origin}/join/${dashboard.team.invite_code}`;
    
    if (navigator.share) {
      try {
        await navigator.share({
          title: `Join ${dashboard.team.name} on Edge Mode`,
          text: `Your coach has invited you to join ${dashboard.team.name}. Track your progress and compete with teammates!`,
          url: fullLink
        });
      } catch (error) {
        // User cancelled or share failed, fall back to copy
        copyInviteLink();
      }
    } else {
      copyInviteLink();
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#09090b] flex items-center justify-center">
        <div className="text-zinc-400 font-mono">Loading dashboard...</div>
      </div>
    );
  }

  if (!dashboard) {
    return (
      <div className="min-h-screen bg-[#09090b] flex items-center justify-center p-4">
        <div className="text-center">
          <h1 className="text-xl font-bold text-white mb-2">Dashboard Not Available</h1>
          <p className="text-zinc-500 mb-4">Unable to load coach dashboard</p>
          <Button onClick={() => navigate('/')} className="bg-primary text-black">
            Go Home
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#09090b] pb-8">
      {/* Header */}
      <div className="bg-zinc-950 border-b border-zinc-800 p-4">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-primary/20 rounded-full flex items-center justify-center">
              <Trophy className="w-5 h-5 text-primary" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-white">{dashboard.team.name}</h1>
              <p className="text-zinc-500 text-sm">Coach: {dashboard.coach.name}</p>
            </div>
          </div>
          <button 
            onClick={handleLogout}
            className="text-zinc-500 hover:text-white"
            data-testid="logout-btn"
          >
            <LogOut className="w-5 h-5" />
          </button>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-3 gap-3">
          <div className="bg-zinc-900 rounded-lg p-3 text-center">
            <div className="flex items-center justify-center mb-1">
              <Users className="w-4 h-4 text-primary" />
            </div>
            <div className="text-2xl font-mono font-bold text-white">{dashboard.stats.total_players}</div>
            <div className="text-zinc-500 text-xs">Players</div>
          </div>
          <div className="bg-zinc-900 rounded-lg p-3 text-center">
            <div className="flex items-center justify-center mb-1">
              <TrendingUp className="w-4 h-4 text-primary" />
            </div>
            <div className="text-2xl font-mono font-bold text-primary">{dashboard.stats.active_players_this_week}</div>
            <div className="text-zinc-500 text-xs">Active</div>
          </div>
          <div className="bg-zinc-900 rounded-lg p-3 text-center">
            <div className="flex items-center justify-center mb-1">
              <Calendar className="w-4 h-4 text-primary" />
            </div>
            <div className="text-2xl font-mono font-bold text-white">{dashboard.stats.total_sessions_this_week}</div>
            <div className="text-zinc-500 text-xs">Sessions</div>
          </div>
        </div>
      </div>

      <div className="p-4 space-y-4">
        {/* Invite Link Card */}
        <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-4">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-white font-medium">Invite Players</h2>
            {dashboard.team.has_extended_trial && (
              <span className="flex items-center gap-1 text-xs text-amber-500">
                <Sparkles className="w-3 h-3" />
                30-day trial
              </span>
            )}
          </div>
          
          <div className="bg-zinc-950 border border-zinc-700 rounded-lg p-3 mb-3">
            <div className="text-zinc-500 text-xs mb-1">Share this link with your players</div>
            <div className="flex items-center gap-2">
              <code className="flex-1 text-primary text-sm truncate">
                {window.location.origin}/join/{dashboard.team.invite_code}
              </code>
            </div>
          </div>

          <div className="flex gap-2">
            <Button
              onClick={copyInviteLink}
              variant="outline"
              className="flex-1 border-zinc-700 text-zinc-300"
              data-testid="copy-invite-btn"
            >
              {copied ? <Check className="w-4 h-4 mr-2" /> : <Copy className="w-4 h-4 mr-2" />}
              {copied ? 'Copied!' : 'Copy Link'}
            </Button>
            <Button
              onClick={shareInviteLink}
              className="flex-1 bg-primary hover:bg-primary/90 text-black"
              data-testid="share-invite-btn"
            >
              <Share2 className="w-4 h-4 mr-2" />
              Share
            </Button>
          </div>
        </div>

        {/* View Team Dashboard Button */}
        {dashboard.stats.total_players > 0 && (
          <Button
            onClick={() => navigate(`/coach/${dashboard.team.id}`)}
            className="w-full bg-zinc-900 border border-zinc-800 hover:bg-zinc-800 text-white"
            data-testid="view-team-btn"
          >
            <ClipboardList className="w-4 h-4 mr-2" />
            View Team Dashboard
          </Button>
        )}

        {/* Empty State */}
        {dashboard.stats.total_players === 0 && (
          <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-8 text-center">
            <Users className="w-12 h-12 text-zinc-700 mx-auto mb-4" />
            <h3 className="text-white font-medium mb-2">No Players Yet</h3>
            <p className="text-zinc-500 text-sm mb-4">
              Share your invite link with your team to get started
            </p>
          </div>
        )}

        {/* Trial Info */}
        <div className="text-center text-zinc-600 text-sm">
          <p>
            {dashboard.team.has_extended_trial ? (
              <>✨ Your players get a <span className="text-amber-500">30-day extended trial</span></>
            ) : (
              <>Your players get a 14-day free trial</>
            )}
          </p>
          <p className="mt-1">Coach account is always free</p>
        </div>
      </div>
    </div>
  );
};

export default CoachHome;
