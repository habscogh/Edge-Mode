import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  Users, Activity, CreditCard, Calendar, TrendingUp, 
  ArrowLeft, RefreshCw, UserPlus, Clock, Star, Mail, Send,
  ChevronDown, ChevronUp, Search, CheckCircle, XCircle, Trash2, Zap
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
  
  // Subscription management state
  const [showSubManager, setShowSubManager] = useState(false);
  const [subEmail, setSubEmail] = useState('');
  const [subPlan, setSubPlan] = useState('yearly');
  const [subDays, setSubDays] = useState(365);
  const [activatingSub, setActivatingSub] = useState(false);
  const [searchResults, setSearchResults] = useState([]);
  const [searching, setSearching] = useState(false);

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

  const fetchAmbassadors = async () => {
    try {
      const res = await axios.get(`${API}/admin/ambassadors`);
      setAmbassadors(res.data.ambassadors || []);
    } catch (err) {
      console.error('Failed to fetch ambassadors:', err);
      toast.error('Failed to load ambassadors');
    }
  };

  const fetchSubscribers = async () => {
    try {
      const res = await axios.get(`${API}/admin/subscribers`);
      setSubscribers(res.data);
    } catch (err) {
      console.error('Failed to fetch subscribers:', err);
      toast.error('Failed to load subscribers');
    }
  };

  const handleSendMessage = async (target) => {
    if (!messageSubject.trim() || !messageBody.trim()) {
      toast.error('Please fill in subject and message');
      return;
    }
    
    setSendingMessage(true);
    try {
      const endpoint = target === 'ambassadors' 
        ? `${API}/admin/messages/ambassadors`
        : `${API}/admin/messages/subscribers`;
      
      const res = await axios.post(endpoint, {
        subject: messageSubject,
        message: messageBody,
        send_email: true
      });
      
      toast.success(`Message sent to ${res.data.sent_to} ${target}!`);
      setMessageSubject('');
      setMessageBody('');
      setShowMessageForm(null);
    } catch (err) {
      console.error('Failed to send message:', err);
      toast.error('Failed to send message');
    } finally {
      setSendingMessage(false);
    }
  };

  const handleSearchUsers = async (query) => {
    if (query.length < 2) {
      setSearchResults([]);
      return;
    }
    
    setSearching(true);
    try {
      const res = await axios.get(`${API}/admin/users/search?q=${encodeURIComponent(query)}`);
      setSearchResults(res.data.users || []);
    } catch (err) {
      console.error('Search failed:', err);
    } finally {
      setSearching(false);
    }
  };

  const handleActivateSubscription = async () => {
    if (!subEmail.trim()) {
      toast.error('Please enter an email address');
      return;
    }
    
    setActivatingSub(true);
    try {
      const res = await axios.post(`${API}/admin/subscriptions/activate`, {
        email: subEmail,
        plan: subPlan,
        duration_days: parseInt(subDays)
      });
      
      toast.success(`Subscription activated for ${res.data.user.email}!`);
      setSubEmail('');
      setSearchResults([]);
      // Refresh subscribers list
      fetchSubscribers();
    } catch (err) {
      console.error('Failed to activate subscription:', err);
      toast.error(err.response?.data?.detail || 'Failed to activate subscription');
    } finally {
      setActivatingSub(false);
    }
  };

  const handleDeactivateSubscription = async (email) => {
    if (!confirm(`Deactivate subscription for ${email}?`)) return;
    
    try {
      await axios.post(`${API}/admin/subscriptions/deactivate?email=${encodeURIComponent(email)}`);
      toast.success(`Subscription deactivated for ${email}`);
      fetchSubscribers();
    } catch (err) {
      console.error('Failed to deactivate:', err);
      toast.error('Failed to deactivate subscription');
    }
  };

  const handleDeleteUser = async (email, username) => {
    if (!confirm(`⚠️ DELETE USER: ${username} (${email})?\n\nThis will permanently delete:\n- All sessions\n- All reflections\n- All badges\n- All data\n\nThis cannot be undone!`)) return;
    
    try {
      const res = await axios.delete(`${API}/admin/users/${encodeURIComponent(email)}`);
      toast.success(`User ${email} deleted successfully`);
      setSearchResults([]);
      setSubEmail('');
      // Refresh data
      fetchAdminData();
    } catch (err) {
      console.error('Failed to delete user:', err);
      toast.error(err.response?.data?.detail || 'Failed to delete user');
    }
  };

  const handleExpireTrial = async (email, username) => {
    if (!confirm(`Expire trial for ${username} (${email})?\n\nThis will set their trial to expired so they see the payment screen.`)) return;
    
    try {
      await axios.post(`${API}/admin/users/expire-trial?email=${encodeURIComponent(email)}`);
      toast.success(`Trial expired for ${email}`);
      setSearchResults([]);
    } catch (err) {
      console.error('Failed to expire trial:', err);
      toast.error(err.response?.data?.detail || 'Failed to expire trial');
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

        {/* Subscription Management */}
        <div className="bg-zinc-950 border border-zinc-800 rounded-md p-6 mb-6">
          <div 
            className="flex items-center justify-between cursor-pointer"
            onClick={() => setShowSubManager(!showSubManager)}
          >
            <h3 className="text-lg font-heading font-bold uppercase text-white flex items-center gap-2">
              <CreditCard className="w-5 h-5 text-emerald-400" />
              Subscription Management
            </h3>
            {showSubManager ? (
              <ChevronUp className="w-5 h-5 text-zinc-400" />
            ) : (
              <ChevronDown className="w-5 h-5 text-zinc-400" />
            )}
          </div>
          
          {showSubManager && (
            <div className="mt-4 space-y-4">
              <p className="text-zinc-400 text-sm">
                Manually activate subscriptions for users (when Stripe webhooks fail)
              </p>
              
              {/* Search/Enter Email */}
              <div className="space-y-2">
                <label className="text-zinc-400 text-sm">User Email</label>
                <div className="relative">
                  <Input
                    type="email"
                    placeholder="Enter email address..."
                    value={subEmail}
                    onChange={(e) => {
                      setSubEmail(e.target.value);
                      handleSearchUsers(e.target.value);
                    }}
                    className="bg-zinc-800 border-zinc-700"
                  />
                  {searching && (
                    <div className="absolute right-3 top-1/2 -translate-y-1/2">
                      <Search className="w-4 h-4 text-zinc-500 animate-pulse" />
                    </div>
                  )}
                </div>
                
                {/* Search Results Dropdown */}
                {searchResults.length > 0 && (
                  <div className="bg-zinc-800 border border-zinc-700 rounded-md max-h-48 overflow-y-auto">
                    {searchResults.map((u, idx) => (
                      <div
                        key={idx}
                        className="px-3 py-2 hover:bg-zinc-700 flex justify-between items-center border-b border-zinc-700 last:border-0"
                      >
                        <div 
                          className="flex-1 cursor-pointer"
                          onClick={() => {
                            setSubEmail(u.email);
                            setSearchResults([]);
                          }}
                        >
                          <span className="text-white text-sm">{u.username}</span>
                          <span className="text-zinc-400 text-xs ml-2">{u.email}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          {u.subscription_active ? (
                            <span className="text-xs text-green-400 flex items-center gap-1">
                              <CheckCircle className="w-3 h-3" /> Active
                            </span>
                          ) : (
                            <span className="text-xs text-zinc-500">No sub</span>
                          )}
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              handleExpireTrial(u.email, u.username);
                            }}
                            className="text-orange-400 hover:text-orange-300 hover:bg-orange-500/20 p-1 rounded"
                            title="Expire trial (for testing)"
                          >
                            <Clock className="w-4 h-4" />
                          </button>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              handleDeleteUser(u.email, u.username);
                            }}
                            className="text-red-400 hover:text-red-300 hover:bg-red-500/20 p-1 rounded"
                            title="Delete user"
                          >
                            <XCircle className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
              
              {/* Plan Selection */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-zinc-400 text-sm block mb-1">Plan</label>
                  <select
                    value={subPlan}
                    onChange={(e) => {
                      setSubPlan(e.target.value);
                      setSubDays(e.target.value === 'yearly' ? 365 : 30);
                    }}
                    className="w-full bg-zinc-800 border border-zinc-700 rounded-md px-3 py-2 text-white text-sm"
                  >
                    <option value="monthly">Monthly</option>
                    <option value="yearly">Yearly</option>
                  </select>
                </div>
                <div>
                  <label className="text-zinc-400 text-sm block mb-1">Duration (days)</label>
                  <Input
                    type="number"
                    value={subDays}
                    onChange={(e) => setSubDays(e.target.value)}
                    className="bg-zinc-800 border-zinc-700"
                  />
                </div>
              </div>
              
              {/* Activate Button */}
              <Button
                onClick={handleActivateSubscription}
                disabled={activatingSub || !subEmail.trim()}
                className="w-full bg-emerald-600 hover:bg-emerald-500 text-white"
              >
                <CheckCircle className="w-4 h-4 mr-2" />
                {activatingSub ? 'Activating...' : 'Activate Subscription'}
              </Button>
            </div>
          )}
        </div>

        {/* Ambassadors Section */}
        <div className="bg-zinc-950 border border-zinc-800 rounded-md p-6 mb-6">
          <div 
            className="flex items-center justify-between cursor-pointer"
            onClick={() => {
              setShowAmbassadors(!showAmbassadors);
              if (!showAmbassadors && ambassadors.length === 0) fetchAmbassadors();
            }}
          >
            <h3 className="text-lg font-heading font-bold uppercase text-white flex items-center gap-2">
              <Star className="w-5 h-5 text-yellow-400" />
              Founding Ambassadors
              <span className="text-sm font-mono text-yellow-400 ml-2">
                ({stats?.ambassadors?.total || 0})
              </span>
            </h3>
            {showAmbassadors ? (
              <ChevronUp className="w-5 h-5 text-zinc-400" />
            ) : (
              <ChevronDown className="w-5 h-5 text-zinc-400" />
            )}
          </div>
          
          {showAmbassadors && (
            <div className="mt-4">
              {/* Ambassador List */}
              {ambassadors.length > 0 ? (
                <div className="space-y-2 max-h-64 overflow-y-auto mb-4">
                  {ambassadors.map((amb, idx) => (
                    <div key={idx} className="flex justify-between items-center text-sm bg-zinc-900 p-3 rounded">
                      <div>
                        <span className="text-white font-body">{amb.username}</span>
                        <span className="text-zinc-500 font-body ml-2">({amb.email})</span>
                      </div>
                      <span className="text-yellow-400 font-mono text-xs">
                        {amb.ambassador_since ? format(parseISO(amb.ambassador_since), 'MMM d, yyyy') : 'N/A'}
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-zinc-500 font-body text-sm mb-4">No ambassadors yet</p>
              )}
              
              {/* Send Message Button */}
              <Button
                onClick={() => setShowMessageForm(showMessageForm === 'ambassadors' ? null : 'ambassadors')}
                className="bg-yellow-500/20 text-yellow-400 hover:bg-yellow-500/30 w-full"
              >
                <Mail className="w-4 h-4 mr-2" />
                Send Message to All Ambassadors
              </Button>
              
              {/* Message Form */}
              {showMessageForm === 'ambassadors' && (
                <div className="mt-4 p-4 bg-zinc-900 rounded-lg space-y-3">
                  <Input
                    placeholder="Subject"
                    value={messageSubject}
                    onChange={(e) => setMessageSubject(e.target.value)}
                    className="bg-zinc-800 border-zinc-700"
                  />
                  <textarea
                    placeholder="Message body..."
                    value={messageBody}
                    onChange={(e) => setMessageBody(e.target.value)}
                    className="w-full bg-zinc-800 border border-zinc-700 rounded-md p-3 text-white placeholder-zinc-500 h-32 resize-none"
                  />
                  <div className="flex gap-2">
                    <Button
                      variant="ghost"
                      onClick={() => setShowMessageForm(null)}
                      className="flex-1"
                    >
                      Cancel
                    </Button>
                    <Button
                      onClick={() => handleSendMessage('ambassadors')}
                      disabled={sendingMessage}
                      className="flex-1 bg-yellow-500 text-black hover:bg-yellow-400"
                    >
                      <Send className="w-4 h-4 mr-2" />
                      {sendingMessage ? 'Sending...' : 'Send'}
                    </Button>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Subscribers Section */}
        <div className="bg-zinc-950 border border-zinc-800 rounded-md p-6 mb-6">
          <div 
            className="flex items-center justify-between cursor-pointer"
            onClick={() => {
              setShowSubscribers(!showSubscribers);
              if (!showSubscribers && subscribers.paid_subscribers.length === 0) fetchSubscribers();
            }}
          >
            <h3 className="text-lg font-heading font-bold uppercase text-white flex items-center gap-2">
              <CreditCard className="w-5 h-5 text-green-400" />
              Active Subscribers
              <span className="text-sm font-mono text-green-400 ml-2">
                ({stats?.subscriptions?.paid || 0} paid, {stats?.subscriptions?.trial || 0} trial)
              </span>
            </h3>
            {showSubscribers ? (
              <ChevronUp className="w-5 h-5 text-zinc-400" />
            ) : (
              <ChevronDown className="w-5 h-5 text-zinc-400" />
            )}
          </div>
          
          {showSubscribers && (
            <div className="mt-4">
              {/* Paid Subscribers */}
              <h4 className="text-sm font-heading text-green-400 uppercase mb-2">
                Paid Subscribers ({subscribers.paid_count || 0})
              </h4>
              {subscribers.paid_subscribers?.length > 0 ? (
                <div className="space-y-2 max-h-48 overflow-y-auto mb-4">
                  {subscribers.paid_subscribers.map((sub, idx) => (
                    <div key={idx} className="flex justify-between items-center text-sm bg-zinc-900 p-3 rounded">
                      <div>
                        <span className="text-white font-body">{sub.username}</span>
                        <span className="text-zinc-500 font-body ml-2">({sub.email})</span>
                      </div>
                      <span className="text-green-400 font-mono text-xs">PAID</span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-zinc-500 font-body text-sm mb-4">No paid subscribers yet</p>
              )}
              
              {/* Trial Users */}
              <h4 className="text-sm font-heading text-blue-400 uppercase mb-2">
                Active Trials ({subscribers.trial_count || 0})
              </h4>
              {subscribers.trial_users?.length > 0 ? (
                <div className="space-y-2 max-h-48 overflow-y-auto mb-4">
                  {subscribers.trial_users.map((sub, idx) => (
                    <div key={idx} className="flex justify-between items-center text-sm bg-zinc-900 p-3 rounded">
                      <div>
                        <span className="text-white font-body">{sub.username}</span>
                        <span className="text-zinc-500 font-body ml-2">({sub.email})</span>
                      </div>
                      <span className="text-blue-400 font-mono text-xs">TRIAL</span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-zinc-500 font-body text-sm mb-4">No active trials</p>
              )}
              
              {/* Send Message Button */}
              <Button
                onClick={() => setShowMessageForm(showMessageForm === 'subscribers' ? null : 'subscribers')}
                className="bg-green-500/20 text-green-400 hover:bg-green-500/30 w-full"
              >
                <Mail className="w-4 h-4 mr-2" />
                Send Message to Paid Subscribers
              </Button>
              
              {/* Message Form */}
              {showMessageForm === 'subscribers' && (
                <div className="mt-4 p-4 bg-zinc-900 rounded-lg space-y-3">
                  <Input
                    placeholder="Subject"
                    value={messageSubject}
                    onChange={(e) => setMessageSubject(e.target.value)}
                    className="bg-zinc-800 border-zinc-700"
                  />
                  <textarea
                    placeholder="Message body..."
                    value={messageBody}
                    onChange={(e) => setMessageBody(e.target.value)}
                    className="w-full bg-zinc-800 border border-zinc-700 rounded-md p-3 text-white placeholder-zinc-500 h-32 resize-none"
                  />
                  <div className="flex gap-2">
                    <Button
                      variant="ghost"
                      onClick={() => setShowMessageForm(null)}
                      className="flex-1"
                    >
                      Cancel
                    </Button>
                    <Button
                      onClick={() => handleSendMessage('subscribers')}
                      disabled={sendingMessage}
                      className="flex-1 bg-green-500 text-black hover:bg-green-400"
                    >
                      <Send className="w-4 h-4 mr-2" />
                      {sendingMessage ? 'Sending...' : 'Send'}
                    </Button>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
