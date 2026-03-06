import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { Trophy, Lock, CheckCircle, TrendingUp, Clock, Flame, Target, Star, Share2, ArrowLeft } from 'lucide-react';
import { format, parseISO } from 'date-fns';
import { ShareButton, ShareIcons } from '../components/ShareButton';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const BADGE_ICONS = {
  '🏆': Trophy,
  '🔥': Flame,
  '💯': CheckCircle,
  '⏱️': Clock,
  '✨': Star,
  '🎯': Target
};

const BadgeCard = ({ badge, progress, onShare }) => {
  const isEarned = badge.earned;
  const IconComponent = BADGE_ICONS[badge.icon] || Trophy;
  const progressData = progress?.find(p => p.badge_id === badge.id);
  
  return (
    <div 
      className={`relative p-4 rounded-lg border transition-all ${
        isEarned 
          ? 'bg-zinc-900 border-primary/50 shadow-lg shadow-primary/10' 
          : 'bg-zinc-950 border-zinc-800 opacity-60'
      }`}
      data-testid={`badge-card-${badge.id}`}
    >
      {/* Earned indicator */}
      {isEarned && (
        <div className="absolute -top-2 -right-2 bg-primary rounded-full p-1">
          <CheckCircle className="w-4 h-4 text-primary-foreground" />
        </div>
      )}
      
      {/* Badge icon */}
      <div className={`w-14 h-14 rounded-full flex items-center justify-center mx-auto mb-3 ${
        isEarned ? 'bg-primary/20' : 'bg-zinc-800'
      }`}>
        {isEarned ? (
          <span className="text-3xl">{badge.icon}</span>
        ) : (
          <Lock className="w-6 h-6 text-zinc-600" />
        )}
      </div>
      
      {/* Badge info */}
      <h3 className={`text-center font-heading font-bold text-sm uppercase tracking-wide mb-1 ${
        isEarned ? 'text-white' : 'text-zinc-500'
      }`}>
        {badge.name}
      </h3>
      <p className={`text-center text-xs font-body ${
        isEarned ? 'text-zinc-400' : 'text-zinc-600'
      }`}>
        {badge.description}
      </p>
      
      {/* Earned date or progress */}
      {isEarned && badge.earned_at && (
        <div className="flex items-center justify-center gap-2 mt-2">
          <p className="text-xs text-primary font-mono">
            {format(parseISO(badge.earned_at), 'MMM d, yyyy')}
          </p>
          <button
            onClick={(e) => {
              e.stopPropagation();
              onShare && onShare(badge);
            }}
            className="p-1 rounded-full hover:bg-zinc-800 transition-colors"
            title="Share this badge"
            data-testid={`share-badge-${badge.id}`}
          >
            <Share2 className="w-3.5 h-3.5 text-zinc-500 hover:text-primary" />
          </button>
        </div>
      )}
      
      {/* Progress bar for unearned badges */}
      {!isEarned && progressData && (
        <div className="mt-3">
          <div className="flex justify-between text-xs text-zinc-500 mb-1">
            <span>{progressData.current}</span>
            <span>{progressData.target}</span>
          </div>
          <div className="h-1.5 bg-zinc-800 rounded-full overflow-hidden">
            <div 
              className="h-full bg-zinc-600 rounded-full transition-all"
              style={{ width: `${progressData.percent}%` }}
            />
          </div>
        </div>
      )}
    </div>
  );
};

export const AchievementsScreen = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [badges, setBadges] = useState(null);
  const [progress, setProgress] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all'); // all, earned, locked
  const [shareMenuBadge, setShareMenuBadge] = useState(null);

  useEffect(() => {
    fetchBadges();
  }, []);

  const fetchBadges = async () => {
    try {
      const [badgesRes, progressRes] = await Promise.all([
        axios.get(`${API}/badges/user`),
        axios.get(`${API}/badges/progress`)
      ]);
      setBadges(badgesRes.data);
      setProgress(progressRes.data);
    } catch (error) {
      console.error('Failed to fetch badges:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleShareBadge = (badge) => {
    setShareMenuBadge(badge);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-[#09090b]">
        <div className="text-zinc-400 font-mono">Loading...</div>
      </div>
    );
  }

  const filteredBadges = badges?.all_badges?.filter(badge => {
    if (filter === 'earned') return badge.earned;
    if (filter === 'locked') return !badge.earned;
    return true;
  }) || [];

  // Group badges by category
  const categories = {
    milestone: { name: 'Milestones', badges: [] },
    streak: { name: 'Streaks', badges: [] },
    consistency: { name: 'Consistency', badges: [] },
    mastery: { name: 'Mastery', badges: [] }
  };

  filteredBadges.forEach(badge => {
    if (categories[badge.category]) {
      categories[badge.category].badges.push(badge);
    }
  });

  return (
    <div className="min-h-screen bg-[#09090b] pb-24" data-testid="achievements-screen">
      <div className="p-6">
        {/* Header */}
        <div className="mb-6">
          <button
            onClick={() => navigate(-1)}
            className="flex items-center gap-2 text-zinc-400 hover:text-white transition-colors mb-4"
            data-testid="achievements-back-btn"
          >
            <ArrowLeft className="w-5 h-5" />
            <span className="text-sm font-body">Back</span>
          </button>
          <h1 className="text-2xl font-heading font-bold uppercase tracking-tight text-white mb-2">
            Achievements
          </h1>
          <p className="text-zinc-400 font-body text-sm">
            Earn badges by reaching milestones in your journey
          </p>
        </div>

        {/* Stats Summary */}
        <div className="bg-zinc-950 border border-zinc-800 rounded-lg p-4 mb-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-primary/20 rounded-full flex items-center justify-center">
                <Trophy className="w-6 h-6 text-primary" />
              </div>
              <div>
                <div className="text-2xl font-mono font-bold text-white">
                  {badges?.total_earned || 0}
                  <span className="text-zinc-500 text-lg">/{badges?.total_available || 0}</span>
                </div>
                <div className="text-zinc-500 text-xs font-body">Badges Earned</div>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-right">
                <div className="text-lg font-mono font-bold text-primary">
                  {badges?.total_available ? Math.round((badges.total_earned / badges.total_available) * 100) : 0}%
                </div>
                <div className="text-zinc-500 text-xs font-body">Complete</div>
              </div>
              {badges?.total_earned > 0 && (
                <ShareButton 
                  type="badge_summary" 
                  data={{ earned: badges.total_earned, total: badges.total_available }}
                  variant="outline"
                  size="sm"
                  className="border-zinc-700 text-zinc-300 hover:bg-zinc-800"
                />
              )}
            </div>
          </div>
        </div>

        {/* Filter Tabs */}
        <div className="flex gap-2 mb-6">
          {['all', 'earned', 'locked'].map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-4 py-2 rounded-md text-sm font-heading uppercase tracking-wide transition-colors ${
                filter === f
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-zinc-900 text-zinc-400 hover:text-white'
              }`}
              data-testid={`filter-${f}`}
            >
              {f}
            </button>
          ))}
        </div>

        {/* Share Modal for individual badge */}
        {shareMenuBadge && (
          <>
            <div 
              className="fixed inset-0 bg-black/60 z-40"
              onClick={() => setShareMenuBadge(null)}
            />
            <div className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-50 bg-zinc-900 border border-zinc-700 rounded-lg p-6 w-[90%] max-w-sm">
              <div className="text-center mb-4">
                <div className="w-16 h-16 bg-primary/20 rounded-full flex items-center justify-center mx-auto mb-3">
                  <span className="text-4xl">{shareMenuBadge.icon}</span>
                </div>
                <h3 className="text-white font-heading font-bold uppercase">{shareMenuBadge.name}</h3>
                <p className="text-zinc-400 text-sm">{shareMenuBadge.description}</p>
              </div>
              <p className="text-zinc-500 text-xs text-center mb-4">Share your achievement</p>
              <ShareIcons 
                type="badge" 
                data={shareMenuBadge} 
                className="justify-center"
              />
              <button
                onClick={() => setShareMenuBadge(null)}
                className="w-full mt-4 py-2 text-zinc-400 text-sm hover:text-white transition-colors"
              >
                Close
              </button>
            </div>
          </>
        )}

        {/* Badge Categories */}
        {Object.entries(categories).map(([key, category]) => (
          category.badges.length > 0 && (
            <div key={key} className="mb-8">
              <h2 className="text-sm font-heading uppercase tracking-wide text-zinc-500 mb-4">
                {category.name}
              </h2>
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
                {category.badges.map((badge) => (
                  <BadgeCard 
                    key={badge.id} 
                    badge={badge} 
                    progress={progress}
                    onShare={handleShareBadge}
                  />
                ))}
              </div>
            </div>
          )
        ))}

        {filteredBadges.length === 0 && (
          <div className="text-center py-12">
            <Trophy className="w-12 h-12 text-zinc-700 mx-auto mb-4" />
            <p className="text-zinc-500 font-body">
              {filter === 'earned' 
                ? "You haven't earned any badges yet. Keep going!" 
                : "No badges to show"}
            </p>
          </div>
        )}
      </div>
    </div>
  );
};
