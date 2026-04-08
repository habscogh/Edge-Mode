import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { User, LogOut, CreditCard, Trophy, Settings, Mail, Lock, Trash2, Bell, Shield, UserPlus, ChevronRight, HelpCircle, Target, Swords, Users, Sun, Moon, School, PawPrint, Medal } from 'lucide-react';
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
import { ReferralSection } from '../components/Referrals';

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
    weekly_summary: true,
    morning_reminders: false
  });
  const [myPet, setMyPet] = useState(null);
  const [displayBadge, setDisplayBadge] = useState(null);
  const [availableBadges, setAvailableBadges] = useState([]);
  const [showBadgeSelector, setShowBadgeSelector] = useState(false);
  
  // Profile customization state
  const [profileCustomization, setProfileCustomization] = useState({
    theme: null,
    frame: null,
    effect: null
  });
  const [availableThemes, setAvailableThemes] = useState([]);
  const [availableFrames, setAvailableFrames] = useState([]);
  const [availableEffects, setAvailableEffects] = useState([]);
  const [showCustomizationPanel, setShowCustomizationPanel] = useState(false);
  const [customizationTab, setCustomizationTab] = useState('themes');

  const isAdmin = user && ADMIN_EMAILS.includes(user.email);
  const isParent = user?.is_parent || linkedStudents.length > 0;

  useEffect(() => {
    fetchNotificationSettings();
    fetchLinkedStudents();
    fetchMyPet();
    fetchDisplayBadge();
    fetchProfileCustomization();
  }, []);

  const fetchProfileCustomization = async () => {
    try {
      const [customRes, themesRes, framesRes, effectsRes] = await Promise.all([
        axios.get(`${API}/shop/profile-customization`),
        axios.get(`${API}/shop/available-customizations/themes`),
        axios.get(`${API}/shop/available-customizations/avatars`),
        axios.get(`${API}/shop/available-customizations/effects`)
      ]);
      setProfileCustomization(customRes.data);
      setAvailableThemes(themesRes.data.items || []);
      setAvailableFrames(framesRes.data.items || []);
      setAvailableEffects(effectsRes.data.items || []);
    } catch (error) {
      // No customizations or error - that's fine
    }
  };

  const handleSetTheme = async (inventoryId) => {
    try {
      const response = await axios.post(`${API}/shop/set-theme`, { inventory_id: inventoryId });
      setProfileCustomization(prev => ({ ...prev, theme: response.data.theme }));
      toast.success(response.data.message);
    } catch (error) {
      toast.error('Failed to set theme');
    }
  };

  const handleSetFrame = async (inventoryId) => {
    try {
      const response = await axios.post(`${API}/shop/set-frame`, { inventory_id: inventoryId });
      setProfileCustomization(prev => ({ ...prev, frame: response.data.frame }));
      toast.success(response.data.message);
    } catch (error) {
      toast.error('Failed to set frame');
    }
  };

  const handleSetEffect = async (inventoryId) => {
    try {
      const response = await axios.post(`${API}/shop/set-effect`, { inventory_id: inventoryId });
      setProfileCustomization(prev => ({ ...prev, effect: response.data.effect }));
      toast.success(response.data.message);
    } catch (error) {
      toast.error('Failed to set effect');
    }
  };

  const fetchDisplayBadge = async () => {
    try {
      const [badgeRes, availableRes] = await Promise.all([
        axios.get(`${API}/shop/display-badge`),
        axios.get(`${API}/shop/available-display-badges`)
      ]);
      setDisplayBadge(badgeRes.data.badge);
      setAvailableBadges(availableRes.data.badges || []);
    } catch (error) {
      // No display badge or error - that's fine
    }
  };

  const handleSetDisplayBadge = async (badgeId) => {
    try {
      const response = await axios.post(`${API}/shop/set-display-badge`, {
        badge_id: badgeId
      });
      setDisplayBadge(response.data.badge);
      setShowBadgeSelector(false);
      toast.success(response.data.message);
    } catch (error) {
      toast.error('Failed to set display badge');
    }
  };

  const fetchMyPet = async () => {
    try {
      const response = await axios.get(`${API}/pets/my-pet`);
      setMyPet(response.data);
    } catch (error) {
      // No pet or error - that's fine
    }
  };

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

        {/* Profile Card with Theme */}
        <div 
          className="rounded-md p-6 mb-4 relative overflow-hidden"
          style={{
            background: profileCustomization.theme?.theme_data?.gradient || '#09090b',
            borderWidth: '1px',
            borderStyle: 'solid',
            borderColor: profileCustomization.theme?.theme_data?.border_color || '#27272a',
            boxShadow: profileCustomization.theme ? `0 0 30px ${profileCustomization.theme.theme_data?.glow_color || 'transparent'}` : 'none'
          }}
        >
          {/* Effect overlay */}
          {profileCustomization.effect && (
            <div className={`absolute inset-0 pointer-events-none ${profileCustomization.effect.effect_data?.animation_class || ''}`} />
          )}
          
          <div className="flex items-center gap-4 mb-6 relative z-10">
            {/* Avatar with Frame */}
            <div 
              className={`w-16 h-16 rounded-full flex items-center justify-center relative ${
                profileCustomization.effect?.effect_data?.animation_class || ''
              }`}
              style={{
                background: profileCustomization.theme?.theme_data?.accent_color 
                  ? `${profileCustomization.theme.theme_data.accent_color}33` 
                  : 'rgba(16, 185, 129, 0.2)',
                borderWidth: profileCustomization.frame?.frame_data?.border_width || '0',
                borderStyle: profileCustomization.frame?.frame_data?.border_style || 'none',
                borderColor: profileCustomization.frame?.frame_data?.border_color || 'transparent',
                boxShadow: profileCustomization.frame?.frame_data?.box_shadow || 'none',
                animation: profileCustomization.frame?.frame_data?.animation !== 'none' 
                  ? `${profileCustomization.frame?.frame_data?.animation} 1.5s ease-in-out infinite` 
                  : 'none'
              }}
            >
              <User className="w-8 h-8" style={{ 
                color: profileCustomization.theme?.theme_data?.accent_color || '#10b981' 
              }} />
            </div>
            <div>
              <div className="flex items-center gap-2 flex-wrap">
                <h2 className="text-2xl font-heading font-bold uppercase text-white drop-shadow-lg">{user.username}</h2>
                {displayBadge && (
                  <span className="text-xl" title={displayBadge.name}>{displayBadge.icon}</span>
                )}
                {user.is_ambassador && <AmbassadorBadge size="small" />}
              </div>
              <p className="text-zinc-300/80 font-body text-sm">{user.email}</p>
            </div>
          </div>

          {/* Customize Profile Button */}
          <button
            onClick={() => setShowCustomizationPanel(!showCustomizationPanel)}
            className="w-full py-2 px-4 rounded-lg text-sm font-body transition-all mb-4"
            style={{
              background: profileCustomization.theme?.theme_data?.accent_color 
                ? `${profileCustomization.theme.theme_data.accent_color}22` 
                : 'rgba(39, 39, 42, 1)',
              borderWidth: '1px',
              borderStyle: 'solid',
              borderColor: profileCustomization.theme?.theme_data?.border_color || '#3f3f46',
              color: profileCustomization.theme?.theme_data?.accent_color || '#a1a1aa'
            }}
            data-testid="customize-profile-btn"
          >
            {showCustomizationPanel ? '✕ Close Customization' : '✨ Customize Profile'}
          </button>

          {/* Profile Customization Panel */}
          {showCustomizationPanel && (
            <div className="bg-black/30 backdrop-blur-sm rounded-lg p-4 mb-4 border border-white/10">
              <h3 className="text-white font-heading font-bold mb-3">Profile Customization</h3>
              
              {/* Tabs */}
              <div className="flex gap-2 mb-4">
                {['themes', 'frames', 'effects'].map(tab => (
                  <button
                    key={tab}
                    onClick={() => setCustomizationTab(tab)}
                    className={`px-3 py-1.5 rounded-lg text-sm font-body capitalize transition-all ${
                      customizationTab === tab 
                        ? 'bg-white/20 text-white' 
                        : 'bg-white/5 text-zinc-400 hover:bg-white/10'
                    }`}
                  >
                    {tab === 'themes' ? '🎨' : tab === 'frames' ? '👤' : '✨'} {tab}
                  </button>
                ))}
              </div>

              {/* Theme Options */}
              {customizationTab === 'themes' && (
                <div className="space-y-2">
                  {availableThemes.length > 0 ? (
                    <>
                      <button
                        onClick={() => handleSetTheme(null)}
                        className={`w-full p-3 rounded-lg text-left transition-all ${
                          !profileCustomization.theme 
                            ? 'bg-white/20 border border-white/30' 
                            : 'bg-white/5 hover:bg-white/10 border border-transparent'
                        }`}
                      >
                        <span className="text-white font-body">Default Theme</span>
                      </button>
                      {availableThemes.map(theme => (
                        <button
                          key={theme.inventory_id}
                          onClick={() => handleSetTheme(theme.inventory_id)}
                          className={`w-full p-3 rounded-lg text-left transition-all flex items-center gap-3 ${
                            profileCustomization.theme?.inventory_id === theme.inventory_id
                              ? 'border border-white/30' 
                              : 'border border-transparent hover:bg-white/10'
                          }`}
                          style={{
                            background: theme.theme_data?.gradient || 'rgba(255,255,255,0.05)'
                          }}
                        >
                          <span className="text-xl">{theme.icon}</span>
                          <span className="text-white font-body">{theme.name}</span>
                        </button>
                      ))}
                    </>
                  ) : (
                    <p className="text-zinc-500 text-sm font-body">Purchase themes from the shop</p>
                  )}
                </div>
              )}

              {/* Frame Options */}
              {customizationTab === 'frames' && (
                <div className="space-y-2">
                  {availableFrames.length > 0 ? (
                    <>
                      <button
                        onClick={() => handleSetFrame(null)}
                        className={`w-full p-3 rounded-lg text-left transition-all flex items-center gap-3 ${
                          !profileCustomization.frame 
                            ? 'bg-white/20 border border-white/30' 
                            : 'bg-white/5 hover:bg-white/10 border border-transparent'
                        }`}
                      >
                        <div className="w-8 h-8 rounded-full bg-zinc-700 flex items-center justify-center">
                          <User className="w-4 h-4 text-zinc-400" />
                        </div>
                        <span className="text-white font-body">No Frame</span>
                      </button>
                      {availableFrames.map(frame => (
                        <button
                          key={frame.inventory_id}
                          onClick={() => handleSetFrame(frame.inventory_id)}
                          className={`w-full p-3 rounded-lg text-left transition-all flex items-center gap-3 ${
                            profileCustomization.frame?.inventory_id === frame.inventory_id
                              ? 'bg-white/20 border border-white/30' 
                              : 'bg-white/5 hover:bg-white/10 border border-transparent'
                          }`}
                        >
                          <div 
                            className="w-8 h-8 rounded-full bg-zinc-800 flex items-center justify-center"
                            style={{
                              borderWidth: frame.frame_data?.border_width,
                              borderStyle: frame.frame_data?.border_style,
                              borderColor: frame.frame_data?.border_color,
                              boxShadow: frame.frame_data?.box_shadow
                            }}
                          >
                            <User className="w-4 h-4 text-zinc-400" />
                          </div>
                          <div>
                            <span className="text-white font-body">{frame.name}</span>
                            <span className="text-xl ml-2">{frame.icon}</span>
                          </div>
                        </button>
                      ))}
                    </>
                  ) : (
                    <p className="text-zinc-500 text-sm font-body">Purchase avatar frames from the shop</p>
                  )}
                </div>
              )}

              {/* Effect Options */}
              {customizationTab === 'effects' && (
                <div className="space-y-2">
                  {availableEffects.length > 0 ? (
                    <>
                      <button
                        onClick={() => handleSetEffect(null)}
                        className={`w-full p-3 rounded-lg text-left transition-all ${
                          !profileCustomization.effect 
                            ? 'bg-white/20 border border-white/30' 
                            : 'bg-white/5 hover:bg-white/10 border border-transparent'
                        }`}
                      >
                        <span className="text-white font-body">No Effect</span>
                      </button>
                      {availableEffects.map(effect => (
                        <button
                          key={effect.inventory_id}
                          onClick={() => handleSetEffect(effect.inventory_id)}
                          className={`w-full p-3 rounded-lg text-left transition-all flex items-center gap-3 ${
                            profileCustomization.effect?.inventory_id === effect.inventory_id
                              ? 'bg-white/20 border border-white/30' 
                              : 'bg-white/5 hover:bg-white/10 border border-transparent'
                          }`}
                        >
                          <span className="text-2xl">{effect.icon}</span>
                          <div>
                            <span className="text-white font-body">{effect.name}</span>
                            <p className="text-zinc-500 text-xs">{effect.description}</p>
                          </div>
                        </button>
                      ))}
                    </>
                  ) : (
                    <p className="text-zinc-500 text-sm font-body">Purchase special effects from the shop</p>
                  )}
                </div>
              )}
            </div>
          )}

          {/* Display Badge Selector */}
          <div className="bg-black/20 backdrop-blur-sm border border-white/10 rounded-md p-4 mb-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Medal className="w-4 h-4 text-yellow-400" />
                <span className="text-white font-body">Display Badge</span>
              </div>
              <button
                onClick={() => setShowBadgeSelector(!showBadgeSelector)}
                className="text-sm hover:opacity-80 transition-colors"
                style={{ color: profileCustomization.theme?.theme_data?.accent_color || '#10b981' }}
                data-testid="change-display-badge-btn"
              >
                {displayBadge ? 'Change' : 'Set Badge'}
              </button>
            </div>
            {displayBadge ? (
              <div className="flex items-center gap-2 mt-2">
                <span className="text-2xl">{displayBadge.icon}</span>
                <span className="text-zinc-300 font-body">{displayBadge.name}</span>
              </div>
            ) : (
              <p className="text-zinc-400 text-sm mt-2 font-body">
                {availableBadges.length > 0 
                  ? 'Select a badge to display next to your name!'
                  : 'Purchase badges from the shop to display here'
                }
              </p>
            )}
            
            {/* Badge Selector Dropdown */}
            {showBadgeSelector && availableBadges.length > 0 && (
              <div className="mt-3 pt-3 border-t border-zinc-700">
                <p className="text-zinc-400 text-xs mb-2 font-body">Choose a badge:</p>
                <div className="flex flex-wrap gap-2">
                  {displayBadge && (
                    <button
                      onClick={() => handleSetDisplayBadge(null)}
                      className="px-3 py-2 bg-zinc-800 hover:bg-zinc-700 rounded-lg text-sm text-zinc-300 transition-colors"
                      data-testid="clear-display-badge"
                    >
                      None
                    </button>
                  )}
                  {availableBadges.map((badge) => (
                    <button
                      key={badge.inventory_id}
                      onClick={() => handleSetDisplayBadge(badge.inventory_id)}
                      className={`px-3 py-2 rounded-lg text-sm transition-colors flex items-center gap-2 ${
                        displayBadge?.inventory_id === badge.inventory_id
                          ? 'bg-primary/20 border border-primary text-white'
                          : 'bg-zinc-800 hover:bg-zinc-700 text-zinc-300'
                      }`}
                      data-testid={`select-badge-${badge.item_id}`}
                    >
                      <span className="text-lg">{badge.icon}</span>
                      <span>{badge.name}</span>
                    </button>
                  ))}
                </div>
                {availableBadges.length === 0 && (
                  <button
                    onClick={() => navigate('/shop')}
                    className="text-primary text-sm hover:underline"
                  >
                    Browse badges in shop →
                  </button>
                )}
              </div>
            )}
          </div>

          <div className="grid grid-cols-2 gap-4 mb-4">
            <div 
              className="rounded-md p-4"
              style={{
                background: profileCustomization.theme ? 'rgba(0,0,0,0.3)' : '#18181b',
                borderWidth: '1px',
                borderStyle: 'solid',
                borderColor: profileCustomization.theme?.theme_data?.border_color ? `${profileCustomization.theme.theme_data.border_color}40` : '#27272a'
              }}
            >
              <div className="text-zinc-400 text-xs font-body uppercase tracking-wide mb-1">Age</div>
              <div className="text-xl font-mono font-bold text-white">{user.age}</div>
            </div>
            <div 
              className="rounded-md p-4"
              style={{
                background: profileCustomization.theme ? 'rgba(0,0,0,0.3)' : '#18181b',
                borderWidth: '1px',
                borderStyle: 'solid',
                borderColor: profileCustomization.theme?.theme_data?.border_color ? `${profileCustomization.theme.theme_data.border_color}40` : '#27272a'
              }}
            >
              <div className="text-zinc-400 text-xs font-body uppercase tracking-wide mb-1">Joined</div>
              <div className="text-xl font-mono font-bold text-white">
                {format(new Date(user.join_date), 'MMM yyyy')}
              </div>
            </div>
          </div>

          <div 
            className="rounded-md p-4"
            style={{
              background: profileCustomization.theme ? 'rgba(0,0,0,0.3)' : '#18181b',
              borderWidth: '1px',
              borderStyle: 'solid',
              borderColor: profileCustomization.theme?.theme_data?.border_color ? `${profileCustomization.theme.theme_data.border_color}40` : '#27272a'
            }}
          >
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <Trophy className="w-4 h-4" style={{ color: profileCustomization.theme?.theme_data?.accent_color || '#10b981' }} />
                <span className="text-white font-body">Streaks</span>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-2 text-center">
              <div>
                <div className="text-2xl font-mono font-bold" style={{ color: profileCustomization.theme?.theme_data?.accent_color || '#10b981' }}>{user.current_streak}</div>
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

        {/* My Pet Section */}
        <div 
          className="bg-zinc-950 border border-purple-500/30 rounded-lg p-4 mb-4 cursor-pointer hover:border-purple-500/50 transition-colors"
          onClick={() => navigate('/pets')}
          data-testid="my-pet-btn"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              {myPet?.has_pet ? (
                <>
                  <div className="w-12 h-12 bg-purple-500/20 rounded-full flex items-center justify-center text-2xl">
                    {myPet.pet.icon}
                  </div>
                  <div>
                    <div className="text-white font-body font-medium flex items-center gap-2">
                      {myPet.pet.name}
                      <span className="text-xs px-2 py-0.5 rounded-full bg-purple-500/20 text-purple-400">
                        {myPet.pet.stage_name}
                      </span>
                    </div>
                    <div className="text-zinc-500 text-sm font-body">
                      {myPet.next_evolution 
                        ? `${myPet.days_until_evolution} days until evolution`
                        : 'Max Evolution!'
                      }
                    </div>
                  </div>
                </>
              ) : (
                <>
                  <div className="w-12 h-12 bg-purple-500/20 rounded-full flex items-center justify-center">
                    <PawPrint className="w-6 h-6 text-purple-400" />
                  </div>
                  <div>
                    <div className="text-white font-body font-medium">Get a Pet!</div>
                    <div className="text-zinc-500 text-sm font-body">Choose your companion</div>
                  </div>
                </>
              )}
            </div>
            <ChevronRight className="w-5 h-5 text-purple-400" />
          </div>
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
                <div className="text-white font-body">Streak & Inactivity Reminders</div>
                <div className="text-zinc-500 text-xs font-body">Get "We Miss You" emails when inactive</div>
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
            
            <div className="flex items-center justify-between">
              <div>
                <div className="text-white font-body flex items-center gap-2">
                  Morning Motivation
                  <span className="text-xs bg-primary/20 text-primary px-2 py-0.5 rounded-full">New</span>
                </div>
                <div className="text-zinc-500 text-xs font-body">Daily motivational email at 8 AM</div>
              </div>
              <button
                data-testid="toggle-morning-reminders"
                onClick={() => handleNotificationToggle('morning_reminders')}
                className={`w-12 h-6 rounded-full transition-colors relative ${
                  notificationSettings.morning_reminders ? 'bg-primary' : 'bg-zinc-700'
                }`}
              >
                <div className={`w-5 h-5 bg-white rounded-full absolute top-0.5 transition-transform ${
                  notificationSettings.morning_reminders ? 'translate-x-6' : 'translate-x-0.5'
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