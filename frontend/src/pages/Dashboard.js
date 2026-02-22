import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import { Flame, TrendingUp, Calendar, Zap } from 'lucide-react';
import { Button } from '../components/ui/button';
import { useNavigate } from 'react-router-dom';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export const Dashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API}/stats/weekly`);
      setStats(response.data);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-[#09090b]">
        <div className="text-zinc-400 font-mono">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#09090b] pb-24">
      <div className="p-6">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-heading font-bold uppercase tracking-tight text-white mb-1">
              {user?.username}
            </h1>
            <p className="text-zinc-400 text-sm font-body">1% Better Every Day</p>
          </div>
          <Flame className="w-8 h-8 text-primary" />
        </div>

        <div className="grid grid-cols-2 gap-4 mb-6">
          <div data-testid="current-streak-card" className="bg-zinc-950 border border-zinc-800 rounded-md p-4">
            <div className="flex items-center gap-2 mb-2">
              <Flame className="w-4 h-4 text-primary" />
              <span className="text-zinc-400 text-xs font-body uppercase tracking-wide">Streak</span>
            </div>
            <div className="text-3xl font-mono font-bold text-white">{user?.current_streak || 0}</div>
            <div className="text-zinc-500 text-xs font-body mt-1">days</div>
          </div>

          <div data-testid="longest-streak-card" className="bg-zinc-950 border border-zinc-800 rounded-md p-4">
            <div className="flex items-center gap-2 mb-2">
              <TrendingUp className="w-4 h-4 text-blue-500" />
              <span className="text-zinc-400 text-xs font-body uppercase tracking-wide">Best</span>
            </div>
            <div className="text-3xl font-mono font-bold text-white">{user?.longest_streak || 0}</div>
            <div className="text-zinc-500 text-xs font-body mt-1">days</div>
          </div>
        </div>

        <div data-testid="weekly-performance-card" className="bg-zinc-950 border border-zinc-800 rounded-md p-6 mb-6">
          <h2 className="text-lg font-heading font-bold uppercase tracking-tight text-white mb-4">
            This Week
          </h2>
          
          <div className="grid grid-cols-3 gap-4 mb-4">
            <div>
              <div className="text-zinc-400 text-xs font-body uppercase tracking-wide mb-1">Performance</div>
              <div className="text-2xl font-mono font-bold text-primary">{stats?.performance_index || 0}%</div>
            </div>
            <div>
              <div className="text-zinc-400 text-xs font-body uppercase tracking-wide mb-1">Consistency</div>
              <div className="text-2xl font-mono font-bold text-white">{stats?.consistency_pct || 0}%</div>
            </div>
            <div>
              <div className="text-zinc-400 text-xs font-body uppercase tracking-wide mb-1">Days</div>
              <div className="text-2xl font-mono font-bold text-white">{stats?.days_logged || 0}/7</div>
            </div>
          </div>

          <div className="space-y-2">
            {stats?.pillars_data?.map((pillar, idx) => (
              <div key={idx} className="bg-zinc-900/50 border border-zinc-800 rounded p-3">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-white text-sm font-body">{pillar.pillar_name}</span>
                  <span className="text-zinc-400 text-xs font-mono">
                    {pillar.minutes_logged}/{pillar.target_minutes} min
                  </span>
                </div>
                <div className="w-full bg-zinc-800 rounded-full h-1.5">
                  <div
                    className="bg-primary h-1.5 rounded-full transition-all duration-300"
                    style={{ width: `${Math.min(pillar.completion_pct, 100)}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <Button
          data-testid="log-activity-btn"
          onClick={() => navigate('/log')}
          className="w-full bg-primary text-primary-foreground hover:bg-primary/90 font-heading uppercase tracking-wide font-bold text-lg py-6"
        >
          <Zap className="w-5 h-5 mr-2" />
          Log Activity
        </Button>
      </div>
    </div>
  );
};