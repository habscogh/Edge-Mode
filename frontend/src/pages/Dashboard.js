import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import { Flame, TrendingUp, Zap, ArrowUp, ArrowDown, Minus, CheckCircle2, X } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { useNavigate } from 'react-router-dom';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { format, parseISO } from 'date-fns';
import { ConsistencyRatingBadge } from '../components/ConsistencyRating';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export const Dashboard = () => {
  const { user, fetchUser } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [comparison, setComparison] = useState(null);
  const [history, setHistory] = useState(null);
  const [loading, setLoading] = useState(true);
  const [quickLogPillar, setQuickLogPillar] = useState(null);
  const [quickLogMinutes, setQuickLogMinutes] = useState('30');
  const [quickLogLoading, setQuickLogLoading] = useState(false);

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

  const handleQuickLog = async () => {
    if (!quickLogPillar) return;
    
    setQuickLogLoading(true);
    try {
      await axios.post(`${API}/sessions/complete`, {
        pillar: quickLogPillar,
        minutes_spent: parseInt(quickLogMinutes) || 30
      });
      toast.success(`Logged ${quickLogMinutes} min of ${quickLogPillar}!`);
      setQuickLogPillar(null);
      setQuickLogMinutes('30');
      // Refresh data
      fetchAllData();
      if (fetchUser) fetchUser();
    } catch (error) {
      console.error('Failed to quick log:', error);
      toast.error('Failed to log session');
    } finally {
      setQuickLogLoading(false);
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
              <ConsistencyRatingBadge consistencyPct={stats?.consistency_pct || 0} />
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

        {/* Quick Log Section */}
        <div data-testid="quick-log-section" className="bg-zinc-950 border border-zinc-800 rounded-md p-4 mb-6">
          <h3 className="text-sm font-heading uppercase tracking-wide text-white mb-3">
            <Zap className="w-4 h-4 inline mr-2 text-yellow-500" />
            Quick Log
          </h3>
          <p className="text-zinc-500 text-xs font-body mb-3">Tap a pillar to log 30 min instantly</p>
          <div className="flex flex-wrap gap-2">
            {stats?.pillars_data?.map((pillar, idx) => (
              <button
                key={idx}
                data-testid={`quick-log-${pillar.pillar_name.toLowerCase().replace(/\//g, '-').replace(/\s+/g, '-')}`}
                onClick={() => setQuickLogPillar(pillar.pillar_name)}
                className="px-3 py-2 bg-zinc-900 border border-zinc-700 rounded-full text-sm font-body text-white hover:bg-primary/20 hover:border-primary transition-all duration-200"
              >
                {pillar.pillar_name.split('/')[0]}
              </button>
            ))}
          </div>
        </div>

        {/* Quick Log Modal */}
        {quickLogPillar && (
          <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
            <div className="bg-zinc-950 border border-zinc-800 rounded-lg w-full max-w-sm p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-heading font-bold uppercase text-white">Quick Log</h3>
                <button
                  data-testid="close-quick-log-modal"
                  onClick={() => setQuickLogPillar(null)}
                  className="text-zinc-400 hover:text-white"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
              
              <div className="bg-primary/10 border border-primary/30 rounded-md p-3 mb-4">
                <div className="text-primary font-body font-bold">{quickLogPillar}</div>
              </div>

              <div className="mb-4">
                <label className="block text-zinc-400 text-sm font-body mb-2">Minutes</label>
                <div className="flex gap-2">
                  {['15', '30', '45', '60'].map((mins) => (
                    <button
                      key={mins}
                      data-testid={`quick-log-${mins}-min`}
                      onClick={() => setQuickLogMinutes(mins)}
                      className={`flex-1 py-2 rounded-md font-mono text-sm transition-all ${
                        quickLogMinutes === mins
                          ? 'bg-primary text-primary-foreground'
                          : 'bg-zinc-900 border border-zinc-700 text-white hover:border-zinc-500'
                      }`}
                    >
                      {mins}
                    </button>
                  ))}
                </div>
                <div className="mt-2">
                  <Input
                    data-testid="quick-log-custom-minutes"
                    type="number"
                    placeholder="Custom minutes"
                    value={quickLogMinutes}
                    onChange={(e) => setQuickLogMinutes(e.target.value)}
                    min="1"
                    className="bg-zinc-900 border-zinc-700 text-white font-mono text-center"
                  />
                </div>
              </div>

              <Button
                data-testid="confirm-quick-log-btn"
                onClick={handleQuickLog}
                disabled={quickLogLoading}
                className="w-full bg-primary text-primary-foreground hover:bg-primary/90 font-heading uppercase"
              >
                {quickLogLoading ? (
                  'Logging...'
                ) : (
                  <>
                    <CheckCircle2 className="w-4 h-4 mr-2" />
                    Log {quickLogMinutes} min
                  </>
                )}
              </Button>
            </div>
          </div>
        )}

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