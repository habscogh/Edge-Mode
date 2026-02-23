import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import { Flame, TrendingUp, Calendar, Zap, Clock, ArrowUp, ArrowDown, Minus } from 'lucide-react';
import { Button } from '../components/ui/button';
import { useNavigate } from 'react-router-dom';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { format, parseISO } from 'date-fns';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export const Dashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [comparison, setComparison] = useState(null);
  const [history, setHistory] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAllData();
  }, []);

  const fetchAllData = async () => {
    try {
      const [statsRes, comparisonRes, historyRes] = await Promise.all([
        axios.get(`${API}/stats/weekly`),
        axios.get(`${API}/stats/comparison`),
        axios.get(`${API}/stats/history?days=30`)
      ]);
      setStats(statsRes.data);
      setComparison(comparisonRes.data);
      setHistory(historyRes.data);
    } catch (error) {
      console.error('Failed to fetch data:', error);
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

  const chartData = history ? history.dates.map((date, idx) => ({
    date: format(parseISO(date), 'MMM d'),
    score: history.scores[idx]
  })) : [];

  const getComparisonIcon = () => {
    if (comparison.improvement_pct > 0) return <ArrowUp className="w-4 h-4 text-primary" />;
    if (comparison.improvement_pct < 0) return <ArrowDown className="w-4 h-4 text-red-500" />;
    return <Minus className="w-4 h-4 text-zinc-500" />;
  };

  const getComparisonColor = () => {
    if (comparison.improvement_pct > 0) return 'text-primary';
    if (comparison.improvement_pct < 0) return 'text-red-500';
    return 'text-zinc-500';
  };

  return (
    <div className="min-h-screen bg-[#09090b] pb-24">
      <div className="p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-heading font-bold uppercase tracking-tight text-white mb-1">
              {user?.username}
            </h1>
            <p className="text-zinc-400 text-sm font-body">Log your effort daily. Review your performance weekly</p>
          </div>
          <Flame className="w-8 h-8 text-primary" />
        </div>

        <div className="grid grid-cols-3 gap-3 mb-6">
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

          <div data-testid="total-sessions-card" className="bg-zinc-950 border border-zinc-800 rounded-md p-4">
            <div className="flex items-center gap-2 mb-2">
              <Zap className="w-4 h-4 text-yellow-500" />
              <span className="text-zinc-400 text-xs font-body uppercase tracking-wide">Total</span>
            </div>
            <div className="text-3xl font-mono font-bold text-white">{user?.total_sessions_completed || 0}</div>
            <div className="text-zinc-500 text-xs font-body mt-1">sessions</div>
          </div>
        </div>

        {comparison && (
          <div data-testid="yesterday-vs-today-card" className="bg-zinc-950 border border-zinc-800 rounded-md p-4 mb-6">
            <h3 className="text-sm font-heading uppercase tracking-wide text-white mb-3">Yesterday vs Today</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <div className="text-zinc-500 text-xs font-body mb-1">Yesterday</div>
                <div className="text-xl font-mono text-zinc-400">{comparison.yesterday_sessions} sessions</div>
                <div className="text-xs text-zinc-600 font-body">{comparison.yesterday_minutes} min</div>
              </div>
              <div>
                <div className="text-zinc-500 text-xs font-body mb-1">Today</div>
                <div className="text-xl font-mono text-white">{comparison.today_sessions} sessions</div>
                <div className="text-xs text-zinc-500 font-body">{comparison.today_minutes} min</div>
              </div>
            </div>
            <div className={`flex items-center gap-2 mt-3 ${getComparisonColor()}`}>
              {getComparisonIcon()}
              <span className="text-sm font-mono font-bold">
                {comparison.improvement_pct > 0 ? '+' : ''}{comparison.improvement_pct}%
              </span>
            </div>
          </div>
        )}

        <div data-testid="performance-graph-card" className="bg-zinc-950 border border-zinc-800 rounded-md p-4 mb-6">
          <h3 className="text-sm font-heading uppercase tracking-wide text-white mb-4">30-Day Performance</h3>
          <ResponsiveContainer width="100%" height={150}>
            <LineChart data={chartData}>
              <XAxis 
                dataKey="date" 
                stroke="#52525b" 
                style={{ fontSize: '10px' }}
                tickLine={false}
              />
              <YAxis 
                stroke="#52525b" 
                style={{ fontSize: '10px' }}
                tickLine={false}
                domain={[0, 100]}
              />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#18181b', 
                  border: '1px solid #27272a',
                  borderRadius: '6px',
                  color: '#fafafa'
                }}
              />
              <Line 
                type="monotone" 
                dataKey="score" 
                stroke="#22c55e" 
                strokeWidth={2}
                dot={{ fill: '#22c55e', r: 3 }}
              />
            </LineChart>
          </ResponsiveContainer>
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

          <div className="grid grid-cols-2 gap-3 mb-4">
            <div className="bg-zinc-900/50 border border-zinc-800 rounded p-3">
              <div className="text-zinc-400 text-xs font-body uppercase mb-1">Sessions</div>
              <div className="text-xl font-mono font-bold text-white">{stats?.total_sessions || 0}</div>
            </div>
            <div className="bg-zinc-900/50 border border-zinc-800 rounded p-3">
              <div className="text-zinc-400 text-xs font-body uppercase mb-1">Time Invested</div>
              <div className="text-xl font-mono font-bold text-white">{Math.floor((stats?.total_minutes || 0) / 60)}h {(stats?.total_minutes || 0) % 60}m</div>
            </div>
          </div>

          <div className="space-y-2">
            {stats?.pillars_data?.map((pillar, idx) => (
              <div key={idx} className="bg-zinc-900/50 border border-zinc-800 rounded p-3">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-white text-sm font-body">{pillar.pillar_name}</span>
                  <span className="text-zinc-400 text-xs font-mono">
                    {pillar.sessions_completed}/{pillar.target_sessions} sessions
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
          Log Session
        </Button>
      </div>
    </div>
  );
};