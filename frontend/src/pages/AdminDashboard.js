import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  Users, Activity, CreditCard, Calendar, TrendingUp, 
  ArrowLeft, RefreshCw, UserPlus, Clock, Star, Mail, Send,
  ChevronDown, ChevronUp
} from 'lucide-react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { format, parseISO } from 'date-fns';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export const AdminDashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [recentActivity, setRecentActivity] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // New state for ambassadors and subscribers
  const [ambassadors, setAmbassadors] = useState([]);
  const [subscribers, setSubscribers] = useState({ paid_subscribers: [], trial_users: [] });
  const [showAmbassadors, setShowAmbassadors] = useState(false);
  const [showSubscribers, setShowSubscribers] = useState(false);
  const [showMessageForm, setShowMessageForm] = useState(null); // 'ambassadors' or 'subscribers'
  const [messageSubject, setMessageSubject] = useState('');
  const [messageBody, setMessageBody] = useState('');
  const [sendingMessage, setSendingMessage] = useState(false);

  useEffect(() => {
    fetchAdminData();
  }, []);

  const fetchAdminData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [statsRes, activityRes] = await Promise.all([
        axios.get(`${API}/admin/stats`),
        axios.get(`${API}/admin/recent-activity`)
      ]);
      setStats(statsRes.data);
      setRecentActivity(activityRes.data);
    } catch (err) {
      console.error('Failed to fetch admin data:', err);
      if (err.response?.status === 403) {
        setError('Admin access required');
      } else {
        setError('Failed to load admin data');
      }
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-[#09090b]">
        <div className="text-zinc-400 font-mono">Loading admin data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-[#09090b] p-4 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-500 font-heading text-xl mb-4">{error}</div>
          <Button onClick={() => navigate('/dashboard')} variant="outline">
            Back to Dashboard
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#09090b] p-4 pb-24">
      <div className="max-w-4xl mx-auto pt-6">
        <div className="flex items-center justify-between mb-6">
          <button
            onClick={() => navigate('/dashboard')}
            className="flex items-center gap-2 text-zinc-400 hover:text-white transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
            <span className="font-body">Back</span>
          </button>
          <Button
            onClick={fetchAdminData}
            variant="outline"
            size="sm"
            className="border-zinc-700"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
        </div>

        <div className="flex items-center gap-3 mb-6">
          <TrendingUp className="w-8 h-8 text-primary" />
          <div>
            <h1 className="text-3xl font-heading font-bold uppercase tracking-tight text-white">
              Admin Dashboard
            </h1>
            <p className="text-zinc-400 font-body text-sm">
              Last updated: {stats?.generated_at ? format(parseISO(stats.generated_at), 'MMM d, h:mm a') : 'N/A'}
            </p>
          </div>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-zinc-950 border border-zinc-800 rounded-md p-4">
            <div className="flex items-center gap-2 mb-2">
              <Users className="w-4 h-4 text-blue-400" />
              <span className="text-zinc-400 text-xs font-body uppercase">Total Users</span>
            </div>
            <div className="text-2xl font-mono font-bold text-white">{stats?.users?.total || 0}</div>
          </div>

          <div className="bg-zinc-950 border border-zinc-800 rounded-md p-4">
            <div className="flex items-center gap-2 mb-2">
              <UserPlus className="w-4 h-4 text-green-400" />
              <span className="text-zinc-400 text-xs font-body uppercase">New This Week</span>
            </div>
            <div className="text-2xl font-mono font-bold text-white">{stats?.users?.this_week || 0}</div>
          </div>

          <div className="bg-zinc-950 border border-zinc-800 rounded-md p-4">
            <div className="flex items-center gap-2 mb-2">
              <Activity className="w-4 h-4 text-primary" />
              <span className="text-zinc-400 text-xs font-body uppercase">Active (7d)</span>
            </div>
            <div className="text-2xl font-mono font-bold text-white">{stats?.users?.active_last_7_days || 0}</div>
          </div>

          <div className="bg-zinc-950 border border-zinc-800 rounded-md p-4">
            <div className="flex items-center gap-2 mb-2">
              <CreditCard className="w-4 h-4 text-yellow-400" />
              <span className="text-zinc-400 text-xs font-body uppercase">Paid</span>
            </div>
            <div className="text-2xl font-mono font-bold text-white">{stats?.subscriptions?.paid || 0}</div>
          </div>
        </div>

        {/* Detailed Stats */}
        <div className="grid md:grid-cols-2 gap-6 mb-6">
          {/* User Stats */}
          <div className="bg-zinc-950 border border-zinc-800 rounded-md p-6">
            <h3 className="text-lg font-heading font-bold uppercase text-white mb-4 flex items-center gap-2">
              <Users className="w-5 h-5 text-blue-400" />
              User Stats
            </h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-zinc-400 font-body">Total Users</span>
                <span className="text-white font-mono">{stats?.users?.total || 0}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-zinc-400 font-body">New Today</span>
                <span className="text-green-400 font-mono">+{stats?.users?.today || 0}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-zinc-400 font-body">New This Week</span>
                <span className="text-green-400 font-mono">+{stats?.users?.this_week || 0}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-zinc-400 font-body">New This Month</span>
                <span className="text-green-400 font-mono">+{stats?.users?.this_month || 0}</span>
              </div>
              <div className="flex justify-between items-center border-t border-zinc-800 pt-3">
                <span className="text-zinc-400 font-body">Active (Last 7 days)</span>
                <span className="text-primary font-mono font-bold">{stats?.users?.active_last_7_days || 0}</span>
              </div>
            </div>
          </div>

          {/* Session & Subscription Stats */}
          <div className="bg-zinc-950 border border-zinc-800 rounded-md p-6">
            <h3 className="text-lg font-heading font-bold uppercase text-white mb-4 flex items-center gap-2">
              <Activity className="w-5 h-5 text-primary" />
              Activity Stats
            </h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-zinc-400 font-body">Total Sessions Logged</span>
                <span className="text-white font-mono">{stats?.sessions?.total || 0}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-zinc-400 font-body">Sessions Today</span>
                <span className="text-white font-mono">{stats?.sessions?.today || 0}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-zinc-400 font-body">Sessions This Week</span>
                <span className="text-white font-mono">{stats?.sessions?.this_week || 0}</span>
              </div>
              <div className="flex justify-between items-center border-t border-zinc-800 pt-3">
                <span className="text-zinc-400 font-body">Paid Subscribers</span>
                <span className="text-yellow-400 font-mono font-bold">{stats?.subscriptions?.paid || 0}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-zinc-400 font-body">Active Trials</span>
                <span className="text-blue-400 font-mono">{stats?.subscriptions?.trial || 0}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-zinc-400 font-body">Total Groups</span>
                <span className="text-white font-mono">{stats?.groups?.total || 0}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="grid md:grid-cols-2 gap-6">
          {/* Recent Signups */}
          <div className="bg-zinc-950 border border-zinc-800 rounded-md p-6">
            <h3 className="text-lg font-heading font-bold uppercase text-white mb-4 flex items-center gap-2">
              <UserPlus className="w-5 h-5 text-green-400" />
              Recent Signups
            </h3>
            {recentActivity?.recent_signups?.length > 0 ? (
              <div className="space-y-3 max-h-64 overflow-y-auto">
                {recentActivity.recent_signups.map((user, idx) => (
                  <div key={idx} className="flex justify-between items-center text-sm">
                    <div>
                      <span className="text-white font-body">{user.username}</span>
                      <span className="text-zinc-500 font-body ml-2">({user.email})</span>
                    </div>
                    <span className="text-zinc-400 font-mono text-xs">{user.join_date}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-zinc-500 font-body text-sm">No recent signups</p>
            )}
          </div>

          {/* Recent Sessions */}
          <div className="bg-zinc-950 border border-zinc-800 rounded-md p-6">
            <h3 className="text-lg font-heading font-bold uppercase text-white mb-4 flex items-center gap-2">
              <Clock className="w-5 h-5 text-primary" />
              Recent Sessions
            </h3>
            {recentActivity?.recent_sessions?.length > 0 ? (
              <div className="space-y-3 max-h-64 overflow-y-auto">
                {recentActivity.recent_sessions.map((session, idx) => (
                  <div key={idx} className="flex justify-between items-center text-sm">
                    <div>
                      <span className="text-white font-body">{session.username}</span>
                      <span className="text-zinc-500 font-body ml-2">- {session.pillar}</span>
                    </div>
                    <span className="text-zinc-400 font-mono text-xs">{session.minutes_spent}m</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-zinc-500 font-body text-sm">No recent sessions</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
