import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { User, LogOut, CreditCard, Trophy, Settings, Mail, Lock, Trash2, Bell, Shield, UserPlus, ChevronRight, HelpCircle, Target, Swords, Users, Sun, Moon, School } from 'lucide-react';
import { format } from 'date-fns';
import axios from 'axios';
import { toast } from 'sonner';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { BadgeSummary } from '../components/BadgeSummary';
import PushNotificationSettings from '../components/PushNotificationSettings';
import { InstallAppSettings } from '../components/InstallPrompt';
import { SyncStatusCard } from '../components/OfflineIndicator';
import { SchoolSelector } from '../components/SchoolSelector';
import { AmbassadorCard, AmbassadorBadge } from '../components/AmbassadorBadge';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ADMIN_EMAILS = ['admin@edgemodeapp.com'];

export const ProfileScreen = () => {
  const { user, logout, fetchUser } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [selectedPlan, setSelectedPlan] = useState('monthly');
  const [showAccountSettings, setShowAccountSettings] = useState(false);
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [newEmail, setNewEmail] = useState('');
  const [deletePassword, setDeletePassword] = useState('');
  const [linkedStudents, setLinkedStudents] = useState([]);
  const [notificationSettings, setNotificationSettings] = useState({
    streak_reminders: true,
    weekly_summary: true
  });

  const isAdmin = user && ADMIN_EMAILS.includes(user.email);
  const isParent = user?.is_parent || linkedStudents.length > 0;

  useEffect(() => {
    fetchNotificationSettings();
    fetchLinkedStudents();
  }, []);

  const fetchLinkedStudents = async () => {
    try {
      const response = await axios.get(`${API}/parent/linked-students`);
      setLinkedStudents(response.data.students || []);
    } catch (error) {
      // Not a parent or no linked students - that's fine
    }
  };

  const fetchNotificationSettings = async () => {
    try {
      const response = await axios.get(`${API}/notifications/settings`);
      setNotificationSettings(response.data);
    } catch (error) {
      console.error('Failed to fetch notification settings:', error);
    }
  };

  const handleNotificationToggle = async (setting) => {
    const newSettings = {
      ...notificationSettings,
      [setting]: !notificationSettings[setting]
    };
    
    try {
      await axios.put(`${API}/notifications/settings`, newSettings);
      setNotificationSettings(newSettings);
      toast.success('Notification settings updated');
    } catch (error) {
      console.error('Failed to update notifications:', error);
      toast.error('Failed to update settings');
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const handleSubscribe = async () => {
    setLoading(true);
    try {
      const originUrl = window.location.origin;
      const response = await axios.post(`${API}/payments/create-checkout`, {
        origin_url: originUrl,
        plan: selectedPlan
      });
      
      if (response.data.url) {
        window.location.href = response.data.url;
      }
    } catch (error) {
      console.error('Failed to create checkout:', error);
      toast.error('Failed to start subscription process');
      setLoading(false);
    }
  };

  const handleChangePassword = async () => {
    if (!currentPassword || !newPassword) {
      toast.error('Please fill all fields');
      return;
    }
    try {
      await axios.post(`${API}/users/change-password`, {
        current_password: currentPassword,
        new_password: newPassword
      });
      toast.success('Password changed successfully');
      setCurrentPassword('');
      setNewPassword('');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to change password');
    }
  };

  const handleChangeEmail = async () => {
    if (!newEmail || !currentPassword) {
      toast.error('Please fill all fields');
      return;
    }
    try {
      await axios.post(`${API}/users/change-email`, {
        new_email: newEmail,
        password: currentPassword
      });
      toast.success('Email changed successfully');
      setNewEmail('');
      setCurrentPassword('');
      await fetchUser();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to change email');
    }
  };

  const handleDeleteAccount = async () => {
    if (!deletePassword) {
      toast.error('Please enter your password');
      return;
    }
    if (!window.confirm('Are you sure? This action cannot be undone.')) {
      return;
    }
    try {
      await axios.delete(`${API}/users/account`);
      toast.success('Account deleted');
      logout();
      navigate('/');
    } catch (error) {
      toast.error('Failed to delete account');
    }
  };

  if (!user) return null;

  const isTrialActive = user.is_trial && user.trial_ends_at && new Date(user.trial_ends_at) > new Date();
  const trialDaysLeft = isTrialActive ? Math.ceil((new Date(user.trial_ends_at) - new Date()) / (1000 * 60 * 60 * 24)) : 0;

  return (
    <div className="min-h-screen bg-[#09090b] p-4 pb-24">
      <div className="max-w-2xl mx-auto pt-6">
        <h1 className="text-3xl font-heading font-bold uppercase tracking-tight text-white mb-6">
          Profile
        </h1>

        {/* Admin Dashboard Link */}
        {isAdmin && (
          <div 
            onClick={() => navigate('/admin')}
            className="bg-purple-500/10 border border-purple-500/30 rounded-md p-4 mb-4 cursor-pointer hover:bg-purple-500/20 transition-colors"
          >
            <div className="flex items-center gap-3">
              <Shield className="w-5 h-5 text-purple-400" />
              <div>
                <div className="text-purple-400 font-body font-bold">Admin Dashboard</div>
                <div className="text-purple-400/70 text-sm font-body">View user stats and activity</div>
              </div>
            </div>
          </div>
        )}

        <div className="bg-zinc-950 border border-zinc-800 rounded-md p-6 mb-4">
          <div className="flex items-center gap-4 mb-6">
            <div className="w-16 h-16 rounded-full bg-primary/20 flex items-center justify-center">
              <User className="w-8 h-8 text-primary" />
            </div>
            <div>
              <h2 className="text-2xl font-heading font-bold uppercase text-white">{user.username}</h2>
              <p className="text-zinc-400 font-body text-sm">{user.email}</p>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4 mb-4">
            <div className="bg-zinc-900 border border-zinc-800 rounded-md p-4">
              <div className="text-zinc-400 text-xs font-body uppercase tracking-wide mb-1">Age</div>
              <div className="text-xl font-mono font-bold text-white">{user.age}</div>
            </div>
            <div className="bg-zinc-900 border border-zinc-800 rounded-md p-4">
              <div className="text-zinc-400 text-xs font-body uppercase tracking-wide mb-1">Joined</div>
              <div className="text-xl font-mono font-bold text-white">
                {format(new Date(user.join_date), 'MMM yyyy')}
              </div>
            </div>
          </div>

          <div className="bg-zinc-900 border border-zinc-800 rounded-md p-4">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <Trophy className="w-4 h-4 text-primary" />
                <span className="text-white font-body">Streaks</span>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-2 text-center">
              <div>
                <div className="text-2xl font-mono font-bold text-primary">{user.current_streak}</div>
                <div className="text-zinc-500 text-xs font-body">Current Streak</div>
              </div>
              <div>
                <div className="text-2xl font-mono font-bold text-white">{user.longest_streak}</div>
                <div className="text-zinc-500 text-xs font-body">Longest Streak</div>
              </div>
            </div>
          </div>
        </div>

        {/* Badge Summary - links to full achievements page */}
        <div className="mb-4">
          <BadgeSummary />
        </div>

        {/* Founding Ambassador Section */}
        <div className="mb-4">
          <AmbassadorCard 
            user={user} 
            onActivate={() => fetchUser && fetchUser()}
          />
        </div>

        {/* Parent Dashboard Button (only for parents) */}
        {isParent && (
          <div 
            className="bg-zinc-950 border border-blue-500/30 rounded-lg p-4 mb-4 cursor-pointer hover:border-blue-500/50 transition-colors"
            onClick={() => navigate('/parent-dashboard')}
            data-testid="parent-dashboard-btn"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-blue-500/20 rounded-full flex items-center justify-center">
                  <Users className="w-5 h-5 text-blue-500" />
                </div>
                <div>
                  <div className="text-white font-body font-medium">Parent Dashboard</div>
                  <div className="text-zinc-500 text-sm font-body">View your linked students' progress</div>
                </div>
              </div>
              <ChevronRight className="w-5 h-5 text-blue-500" />
            </div>
          </div>
        )}

        {/* Manage Pillars Button */}
        <div 
          className="bg-zinc-950 border border-zinc-800 rounded-lg p-4 mb-4 cursor-pointer hover:border-zinc-700 transition-colors"
          onClick={() => navigate('/pillars')}
          data-testid="manage-pillars-btn"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-orange-500/20 rounded-full flex items-center justify-center">
                <Target className="w-5 h-5 text-orange-500" />
              </div>
              <div>
                <div className="text-white font-body font-medium">Manage Pillars</div>
                <div className="text-zinc-500 text-sm font-body">Add, remove, or adjust your pillars</div>
              </div>
            </div>
            <ChevronRight className="w-5 h-5 text-zinc-500" />
          </div>
        </div>

        {/* Challenges Button */}
        <div 
          className="bg-zinc-950 border border-zinc-800 rounded-lg p-4 mb-4 cursor-pointer hover:border-zinc-700 transition-colors"
          onClick={() => navigate('/challenges')}
          data-testid="challenges-btn"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-amber-500/20 rounded-full flex items-center justify-center">
                <Swords className="w-5 h-5 text-amber-500" />
              </div>
              <div>
                <div className="text-white font-body font-medium">Challenges</div>
                <div className="text-zinc-500 text-sm font-body">Compete in weekly & monthly challenges</div>
              </div>
            </div>
            <ChevronRight className="w-5 h-5 text-zinc-500" />
          </div>
        </div>

        {/* School Selection */}
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-heading uppercase tracking-wide text-zinc-500">Your School (Optional)</span>
            <button 
              onClick={() => navigate('/school-leaderboard')}
              className="text-primary text-xs font-body hover:underline flex items-center gap-1"
            >
              View School Leaderboard <ChevronRight className="w-3 h-3" />
            </button>
          </div>
          <SchoolSelector 
            currentSchool={user?.school_name}
            onSchoolChange={(schoolName) => {
              if (fetchUser) fetchUser();
            }}
          />
        </div>

        {/* Family Access Button */}
        <div 
          className="bg-zinc-950 border border-zinc-800 rounded-lg p-4 mb-4 cursor-pointer hover:border-zinc-700 transition-colors"
          onClick={() => navigate('/family')}
          data-testid="family-btn"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-blue-500/20 rounded-full flex items-center justify-center">
                <Users className="w-5 h-5 text-blue-500" />
              </div>
              <div>
                <div className="text-white font-body font-medium">Family Access</div>
                <div className="text-zinc-500 text-sm font-body">Let parents track your progress</div>
              </div>
            </div>
            <ChevronRight className="w-5 h-5 text-zinc-500" />
          </div>
        </div>

        {/* Invite Friends Button */}
        <div 
          className="bg-zinc-950 border border-zinc-800 rounded-lg p-4 mb-4 cursor-pointer hover:border-zinc-700 transition-colors"
          onClick={() => navigate('/invite')}
          data-testid="invite-friends-btn"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-primary/20 rounded-full flex items-center justify-center">
                <UserPlus className="w-5 h-5 text-primary" />
              </div>
              <div>
                <div className="text-white font-body font-medium">Invite Friends</div>
                <div className="text-zinc-500 text-sm font-body">Share Edge Mode with friends</div>
              </div>
            </div>
            <ChevronRight className="w-5 h-5 text-zinc-500" />
          </div>
        </div>

        {/* Help & FAQ Button */}
        <div 
          className="bg-zinc-950 border border-zinc-800 rounded-lg p-4 mb-4 cursor-pointer hover:border-zinc-700 transition-colors"
          onClick={() => navigate('/faq')}
          data-testid="faq-btn"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-zinc-800 rounded-full flex items-center justify-center">
                <HelpCircle className="w-5 h-5 text-zinc-400" />
              </div>
              <div>
                <div className="text-white font-body font-medium">Help & FAQ</div>
                <div className="text-zinc-500 text-sm font-body">Find answers to common questions</div>
              </div>
            </div>
            <ChevronRight className="w-5 h-5 text-zinc-500" />
          </div>
        </div>

        {/* Theme Toggle */}
        <div 
          className="bg-zinc-950 border border-zinc-800 rounded-lg p-4 mb-4 cursor-pointer hover:border-zinc-700 transition-colors"
          onClick={toggleTheme}
          data-testid="theme-toggle-btn"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                theme === 'dark' ? 'bg-indigo-500/20' : 'bg-yellow-500/20'
              }`}>
                {theme === 'dark' ? (
                  <Moon className="w-5 h-5 text-indigo-400" />
                ) : (
                  <Sun className="w-5 h-5 text-yellow-500" />
                )}
              </div>
              <div>
                <div className="text-white font-body font-medium">Theme</div>
                <div className="text-zinc-500 text-sm font-body">
                  {theme === 'dark' ? 'Dark mode active' : 'Light mode active'}
                </div>
              </div>
            </div>
            <div className={`px-3 py-1 rounded-full text-xs font-mono font-bold ${
              theme === 'dark' ? 'bg-indigo-500/20 text-indigo-400' : 'bg-yellow-500/20 text-yellow-600'
            }`}>
              {theme === 'dark' ? 'DARK' : 'LIGHT'}
            </div>
          </div>
        </div>

        <div className="bg-zinc-950 border border-zinc-800 rounded-md p-6 mb-4">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <CreditCard className="w-5 h-5 text-primary" />
              <div>
                <div className="text-white font-body">Subscription</div>
                <div className="text-zinc-400 text-sm font-body">
                  {isTrialActive ? `${trialDaysLeft} days left in trial` : 
                   user.subscription_active ? 'Premium Member' : 'Choose your plan'}
                </div>
              </div>
            </div>
            <div className={`px-3 py-1 rounded-full text-xs font-mono font-bold ${
              user.subscription_active || isTrialActive
                ? 'bg-primary/20 text-primary'
                : 'bg-zinc-800 text-zinc-400'
            }`}>
              {isTrialActive ? 'TRIAL' : user.subscription_active ? 'ACTIVE' : 'INACTIVE'}
            </div>
          </div>
          
          {!user.subscription_active && !isTrialActive && (
            <>
              <div className="grid grid-cols-2 gap-3 mb-4">
                <button
                  onClick={() => setSelectedPlan('monthly')}
                  className={`p-4 border rounded-md transition-all duration-200 ${
                    selectedPlan === 'monthly'
                      ? 'bg-primary/10 border-primary'
                      : 'bg-zinc-900 border-zinc-800 hover:border-zinc-600'
                  }`}
                >
                  <div className="text-white font-body font-bold mb-1">Monthly</div>
                  <div className="text-2xl font-mono font-bold text-primary">$4.99</div>
                  <div className="text-zinc-500 text-xs font-body">per month</div>
                </button>
                
                <button
                  onClick={() => setSelectedPlan('yearly')}
                  className={`p-4 border rounded-md transition-all duration-200 ${
                    selectedPlan === 'yearly'
                      ? 'bg-primary/10 border-primary'
                      : 'bg-zinc-900 border-zinc-800 hover:border-zinc-600'
                  }`}
                >
                  <div className="text-white font-body font-bold mb-1">Yearly</div>
                  <div className="text-2xl font-mono font-bold text-primary">$49.99</div>
                  <div className="text-zinc-500 text-xs font-body">per year</div>
                  <div className="text-xs font-mono text-primary mt-1">Save 17%</div>
                </button>
              </div>
              
              <Button
                data-testid="subscribe-btn"
                onClick={handleSubscribe}
                disabled={loading}
                className="w-full bg-primary text-primary-foreground hover:bg-primary/90 font-heading uppercase tracking-wide"
              >
                {loading ? 'Processing...' : `Subscribe ${selectedPlan === 'monthly' ? 'Monthly' : 'Yearly'}`}
              </Button>
            </>
          )}
          
          {(user.subscription_active || isTrialActive) && (
            <p className="text-zinc-500 text-sm font-body text-center">
              {isTrialActive ? 'Enjoying your trial? Subscribe to continue after trial ends.' : 'Thank you for being an Edge Mode Premium member!'}
            </p>
          )}
        </div>

        {/* Notification Settings */}
        <div className="bg-zinc-950 border border-zinc-800 rounded-md p-6 mb-4">
          <div className="flex items-center gap-3 mb-4">
            <Bell className="w-5 h-5 text-zinc-400" />
            <span className="text-white font-body font-bold">Notifications</span>
          </div>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-white font-body">Streak Reminders</div>
                <div className="text-zinc-500 text-xs font-body">Get reminded to keep your streak alive</div>
              </div>
              <button
                data-testid="toggle-streak-reminders"
                onClick={() => handleNotificationToggle('streak_reminders')}
                className={`w-12 h-6 rounded-full transition-colors relative ${
                  notificationSettings.streak_reminders ? 'bg-primary' : 'bg-zinc-700'
                }`}
              >
                <div className={`w-5 h-5 bg-white rounded-full absolute top-0.5 transition-transform ${
                  notificationSettings.streak_reminders ? 'translate-x-6' : 'translate-x-0.5'
                }`} />
              </button>
            </div>
            
            <div className="flex items-center justify-between">
              <div>
                <div className="text-white font-body">Weekly Summary</div>
                <div className="text-zinc-500 text-xs font-body">Receive your progress report every week</div>
              </div>
              <button
                data-testid="toggle-weekly-summary"
                onClick={() => handleNotificationToggle('weekly_summary')}
                className={`w-12 h-6 rounded-full transition-colors relative ${
                  notificationSettings.weekly_summary ? 'bg-primary' : 'bg-zinc-700'
                }`}
              >
                <div className={`w-5 h-5 bg-white rounded-full absolute top-0.5 transition-transform ${
                  notificationSettings.weekly_summary ? 'translate-x-6' : 'translate-x-0.5'
                }`} />
              </button>
            </div>
          </div>
          
          {/* Push Notifications */}
          <div className="mt-4 pt-4 border-t border-zinc-800">
            <PushNotificationSettings />
          </div>
          
          {/* Install App */}
          <div className="mt-4 pt-4 border-t border-zinc-800">
            <InstallAppSettings />
          </div>
          
          {/* Sync Status */}
          <div className="mt-4 pt-4 border-t border-zinc-800">
            <SyncStatusCard />
          </div>
        </div>

        <div className="bg-zinc-950 border border-zinc-800 rounded-md p-6 mb-4">
          <button
            onClick={() => setShowAccountSettings(!showAccountSettings)}
            className="flex items-center gap-3 w-full"
          >
            <Settings className="w-5 h-5 text-zinc-400" />
            <span className="text-white font-body">Account Settings</span>
          </button>

          {showAccountSettings && (
            <div className="mt-6 space-y-6">
              <div>
                <h3 className="text-white font-body font-bold mb-3 flex items-center gap-2">
                  <Lock className="w-4 h-4" />
                  Change Password
                </h3>
                <div className="space-y-2">
                  <Input
                    type="password"
                    placeholder="Current password"
                    value={currentPassword}
                    onChange={(e) => setCurrentPassword(e.target.value)}
                    className="bg-zinc-900 border-zinc-800 text-white"
                  />
                  <Input
                    type="password"
                    placeholder="New password"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    className="bg-zinc-900 border-zinc-800 text-white"
                  />
                  <Button
                    onClick={handleChangePassword}
                    className="w-full bg-zinc-800 hover:bg-zinc-700"
                  >
                    Update Password
                  </Button>
                </div>
              </div>

              <div>
                <h3 className="text-white font-body font-bold mb-3 flex items-center gap-2">
                  <Mail className="w-4 h-4" />
                  Change Email
                </h3>
                <div className="space-y-2">
                  <Input
                    type="email"
                    placeholder="New email"
                    value={newEmail}
                    onChange={(e) => setNewEmail(e.target.value)}
                    className="bg-zinc-900 border-zinc-800 text-white"
                  />
                  <Input
                    type="password"
                    placeholder="Current password"
                    value={currentPassword}
                    onChange={(e) => setCurrentPassword(e.target.value)}
                    className="bg-zinc-900 border-zinc-800 text-white"
                  />
                  <Button
                    onClick={handleChangeEmail}
                    className="w-full bg-zinc-800 hover:bg-zinc-700"
                  >
                    Update Email
                  </Button>
                </div>
              </div>

              <div>
                <h3 className="text-red-500 font-body font-bold mb-3 flex items-center gap-2">
                  <Trash2 className="w-4 h-4" />
                  Delete Account
                </h3>
                <p className="text-zinc-500 text-sm mb-3">This action cannot be undone.</p>
                <div className="space-y-2">
                  <Input
                    type="password"
                    placeholder="Enter password to confirm"
                    value={deletePassword}
                    onChange={(e) => setDeletePassword(e.target.value)}
                    className="bg-zinc-900 border-zinc-800 text-white"
                  />
                  <Button
                    onClick={handleDeleteAccount}
                    className="w-full bg-red-500 hover:bg-red-600"
                  >
                    Delete My Account
                  </Button>
                </div>
              </div>
            </div>
          )}
        </div>

        <Button
          data-testid="logout-btn"
          onClick={handleLogout}
          variant="ghost"
          className="w-full text-red-500 hover:text-red-400 hover:bg-red-500/10 font-heading uppercase tracking-wide"
        >
          <LogOut className="w-5 h-5 mr-2" />
          Logout
        </Button>
      </div>
    </div>
  );
};