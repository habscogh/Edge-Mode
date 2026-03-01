import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Clock, TrendingUp, Flame, Target, CreditCard, CheckCircle, AlertTriangle, XCircle } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export const TrialExpiredScreen = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [pillars, setPillars] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedPlan, setSelectedPlan] = useState('monthly');

  useEffect(() => {
    fetchTrialStats();
  }, []);

  const fetchTrialStats = async () => {
    try {
      // Get user's accomplishments during trial
      const [sessionsRes, statsRes, pillarsRes] = await Promise.all([
        axios.get(`${API}/sessions/history?days=30`).catch(() => ({ data: [] })),
        axios.get(`${API}/stats/weekly`).catch(() => ({ data: {} })),
        axios.get(`${API}/users/pillars`).catch(() => ({ data: [] }))
      ]);
      
      const sessions = sessionsRes.data || [];
      const totalMinutes = sessions.reduce((sum, s) => sum + (s.minutes_spent || 0), 0);
      const totalSessions = sessions.length;
      const pillarsWorked = [...new Set(sessions.map(s => s.pillar))];
      
      // Get pillar progress
      const pillarProgress = pillarsRes.data?.map(p => {
        const pillarSessions = sessions.filter(s => s.pillar === p.pillar_name);
        return {
          name: p.pillar_name,
          sessions: pillarSessions.length,
          target: p.weekly_target_sessions
        };
      }) || [];
      
      setPillars(pillarProgress);
      setStats({
        totalSessions,
        totalMinutes,
        pillarsWorked: pillarsWorked.length,
        pillarNames: pillarsWorked,
        longestStreak: user?.longest_streak || 0,
        currentStreak: user?.current_streak || 0
      });
    } catch (error) {
      console.error('Failed to fetch stats:', error);
      setStats({ totalSessions: 0, totalMinutes: 0, pillarsWorked: 0, pillarNames: [], longestStreak: 0, currentStreak: 0 });
    }
  };

  const handleSubscribe = async (plan) => {
    setLoading(true);
    try {
      const response = await axios.post(`${API}/payments/create-checkout`, {
        plan: plan,
        success_url: `${window.location.origin}/subscription-success`,
        cancel_url: `${window.location.origin}/trial-expired`
      });
      
      if (response.data.checkout_url) {
        window.location.href = response.data.checkout_url;
      }
    } catch (error) {
      console.error('Failed to create checkout:', error);
      alert('Failed to start checkout. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#09090b] p-4 flex items-center justify-center">
      <div className="max-w-md w-full">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-primary/20 rounded-full flex items-center justify-center mx-auto mb-4">
            <Clock className="w-8 h-8 text-primary" />
          </div>
          <h1 className="text-3xl font-heading font-bold uppercase tracking-tight text-white mb-2">
            Trial Complete
          </h1>
          <p className="text-zinc-400 font-body">
            Your 14-day free trial has ended. Subscribe to keep your momentum going!
          </p>
        </div>

        {/* Trial Accomplishments */}
        {stats && (stats.totalSessions > 0 || stats.longestStreak > 0) && (
          <div className="bg-zinc-950 border border-zinc-800 rounded-md p-6 mb-4">
            <h3 className="text-sm font-heading uppercase tracking-wide text-zinc-400 mb-4">
              What You Accomplished
            </h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="text-center">
                <div className="text-2xl font-mono font-bold text-primary">{stats.totalSessions}</div>
                <div className="text-zinc-500 text-xs font-body">Sessions Logged</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-mono font-bold text-white">{Math.round(stats.totalMinutes / 60)}h</div>
                <div className="text-zinc-500 text-xs font-body">Total Time</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-mono font-bold text-white">{stats.pillarsWorked}</div>
                <div className="text-zinc-500 text-xs font-body">Pillars Worked</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-mono font-bold text-orange-400">{stats.longestStreak}</div>
                <div className="text-zinc-500 text-xs font-body">Longest Streak</div>
              </div>
            </div>
          </div>
        )}

        {/* What You'll Lose - Only show if user has meaningful progress */}
        {stats && (stats.totalSessions > 0 || stats.currentStreak > 0 || pillars.length > 0) && (
          <div className="bg-red-950/30 border border-red-900/50 rounded-md p-4 mb-6">
            <div className="flex items-center gap-2 mb-3">
              <AlertTriangle className="w-4 h-4 text-red-400" />
              <h3 className="text-sm font-heading uppercase tracking-wide text-red-400">
                What You'll Lose
              </h3>
            </div>
            <div className="space-y-2">
              {stats.currentStreak > 0 && (
                <div className="flex items-center gap-2 text-sm">
                  <XCircle className="w-4 h-4 text-red-400/70" />
                  <span className="text-zinc-300 font-body">
                    Your <span className="text-red-400 font-bold">{stats.currentStreak}-day streak</span> will be lost
                  </span>
                </div>
              )}
              {stats.totalMinutes > 0 && (
                <div className="flex items-center gap-2 text-sm">
                  <XCircle className="w-4 h-4 text-red-400/70" />
                  <span className="text-zinc-300 font-body">
                    <span className="text-red-400 font-bold">{Math.round(stats.totalMinutes / 60)}+ hours</span> of tracked progress
                  </span>
                </div>
              )}
              {pillars.length > 0 && (
                <div className="flex items-center gap-2 text-sm">
                  <XCircle className="w-4 h-4 text-red-400/70" />
                  <span className="text-zinc-300 font-body">
                    Your progress in <span className="text-red-400 font-bold">{pillars.map(p => p.name).slice(0, 2).join(', ')}</span>
                    {pillars.length > 2 && ` +${pillars.length - 2} more`}
                  </span>
                </div>
              )}
              {stats.longestStreak >= 7 && (
                <div className="flex items-center gap-2 text-sm">
                  <XCircle className="w-4 h-4 text-red-400/70" />
                  <span className="text-zinc-300 font-body">
                    Your <span className="text-red-400 font-bold">{stats.longestStreak}-day record</span> streak achievement
                  </span>
                </div>
              )}
            </div>
            <p className="text-red-400/80 text-xs font-body mt-3 text-center">
              Don't let your hard work disappear
            </p>
          </div>
        )}

        {/* Subscription Options */}
        <div className="space-y-3 mb-6">
          <div
            onClick={() => setSelectedPlan('monthly')}
            className={`p-4 rounded-md border cursor-pointer transition-all ${
              selectedPlan === 'monthly'
                ? 'bg-primary/10 border-primary'
                : 'bg-zinc-950 border-zinc-800 hover:border-zinc-600'
            }`}
          >
            <div className="flex justify-between items-center">
              <div>
                <div className="text-white font-body font-bold">Monthly</div>
                <div className="text-zinc-400 text-sm font-body">Flexible, cancel anytime</div>
              </div>
              <div className="text-right">
                <div className="text-white font-mono font-bold">$5.99</div>
                <div className="text-zinc-500 text-xs font-body">/month</div>
              </div>
            </div>
          </div>

          <div
            onClick={() => setSelectedPlan('yearly')}
            className={`p-4 rounded-md border cursor-pointer transition-all relative ${
              selectedPlan === 'yearly'
                ? 'bg-primary/10 border-primary'
                : 'bg-zinc-950 border-zinc-800 hover:border-zinc-600'
            }`}
          >
            <div className="absolute -top-2 right-4 bg-green-500 text-white text-xs font-bold px-2 py-0.5 rounded">
              SAVE 17%
            </div>
            <div className="flex justify-between items-center">
              <div>
                <div className="text-white font-body font-bold">Yearly</div>
                <div className="text-zinc-400 text-sm font-body">Best value for committed users</div>
              </div>
              <div className="text-right">
                <div className="text-white font-mono font-bold">$59.99</div>
                <div className="text-zinc-500 text-xs font-body">/year</div>
              </div>
            </div>
          </div>
        </div>

        {/* Subscribe Button */}
        <Button
          onClick={() => handleSubscribe(selectedPlan)}
          disabled={loading}
          className="w-full bg-primary text-primary-foreground hover:bg-primary/90 font-heading uppercase tracking-wide font-bold text-lg py-6 mb-4"
        >
          {loading ? 'Loading...' : (
            <>
              <CreditCard className="w-5 h-5 mr-2" />
              Subscribe Now
            </>
          )}
        </Button>

        {/* Benefits */}
        <div className="bg-zinc-950 border border-zinc-800 rounded-md p-4 mb-6">
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-sm">
              <CheckCircle className="w-4 h-4 text-green-500" />
              <span className="text-zinc-300 font-body">Unlimited session tracking</span>
            </div>
            <div className="flex items-center gap-2 text-sm">
              <CheckCircle className="w-4 h-4 text-green-500" />
              <span className="text-zinc-300 font-body">Performance analytics & insights</span>
            </div>
            <div className="flex items-center gap-2 text-sm">
              <CheckCircle className="w-4 h-4 text-green-500" />
              <span className="text-zinc-300 font-body">Groups & leaderboards</span>
            </div>
            <div className="flex items-center gap-2 text-sm">
              <CheckCircle className="w-4 h-4 text-green-500" />
              <span className="text-zinc-300 font-body">Email reminders & weekly summaries</span>
            </div>
          </div>
        </div>

        {/* Logout Option */}
        <button
          onClick={logout}
          className="w-full text-center text-zinc-500 text-sm font-body hover:text-zinc-300 transition-colors"
        >
          Log out
        </button>
      </div>
    </div>
  );
};
