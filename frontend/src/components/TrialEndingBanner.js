import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { X, Clock, Flame, TrendingUp, CreditCard } from 'lucide-react';
import { Button } from './ui/button';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export const TrialEndingBanner = ({ onSubscribe }) => {
  const { user } = useAuth();
  const [dismissed, setDismissed] = useState(false);
  const [stats, setStats] = useState(null);
  const [daysLeft, setDaysLeft] = useState(null);

  useEffect(() => {
    if (user?.is_trial && user?.trial_ends_at) {
      const trialEnd = new Date(user.trial_ends_at);
      const now = new Date();
      const diffTime = trialEnd - now;
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
      
      // Only show banner if 3 days or less remaining (days 12-14)
      if (diffDays <= 3 && diffDays > 0) {
        setDaysLeft(diffDays);
        fetchStats();
      }
    }
  }, [user]);

  const fetchStats = async () => {
    try {
      const localDate = new Date().toISOString().split('T')[0];
      const response = await axios.get(`${API}/stats/weekly?local_date=${localDate}`);
      setStats(response.data);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
  };

  const handleDismiss = () => {
    setDismissed(true);
    // Store dismissal in sessionStorage so it shows again next session
    sessionStorage.setItem('trialBannerDismissed', 'true');
  };

  // Check if already dismissed this session
  useEffect(() => {
    if (sessionStorage.getItem('trialBannerDismissed')) {
      setDismissed(true);
    }
  }, []);

  // Don't show if not a trial user, already subscribed, or dismissed
  if (!user?.is_trial || !daysLeft || dismissed) {
    return null;
  }

  return (
    <div className="bg-gradient-to-r from-orange-950/80 to-red-950/80 border-b border-orange-800/50 px-4 py-3" data-testid="trial-ending-banner">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <Clock className="w-5 h-5 text-orange-400" />
              <h3 className="text-white font-heading font-bold text-sm uppercase tracking-wide">
                Your 14-day trial ends {daysLeft === 1 ? 'tomorrow' : `in ${daysLeft} days`}
              </h3>
            </div>
            
            <div className="flex flex-wrap items-center gap-4 text-sm mb-3">
              {user?.current_streak > 0 && (
                <div className="flex items-center gap-1.5">
                  <Flame className="w-4 h-4 text-orange-400" />
                  <span className="text-zinc-300">
                    You've built a <span className="text-orange-400 font-bold">{user.current_streak}-day streak</span>
                  </span>
                </div>
              )}
              {stats?.consistency_pct > 0 && (
                <div className="flex items-center gap-1.5">
                  <TrendingUp className="w-4 h-4 text-green-400" />
                  <span className="text-zinc-300">
                    Consistency score: <span className="text-green-400 font-bold">{Math.round(stats.consistency_pct)}%</span>
                  </span>
                </div>
              )}
            </div>
            
            <p className="text-orange-200/80 text-xs font-body">
              Don't lose your progress. Subscribe now to keep your momentum going.
            </p>
          </div>
          
          <div className="flex items-center gap-2">
            <Button
              onClick={onSubscribe}
              size="sm"
              className="bg-orange-500 hover:bg-orange-600 text-white font-heading uppercase text-xs tracking-wide"
              data-testid="trial-banner-subscribe-btn"
            >
              <CreditCard className="w-3.5 h-3.5 mr-1.5" />
              Subscribe
            </Button>
            <button
              onClick={handleDismiss}
              className="text-zinc-400 hover:text-white transition-colors p-1"
              aria-label="Dismiss"
              data-testid="trial-banner-dismiss-btn"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
