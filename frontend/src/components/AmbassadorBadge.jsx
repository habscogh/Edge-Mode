import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Award, Users, Calendar, TrendingUp, ChevronRight, Sparkles, Copy, Check } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { toast } from 'sonner';
import { format, parseISO } from 'date-fns';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Ambassador Badge - shown on profile and leaderboards
export const AmbassadorBadge = ({ size = 'default', showLabel = true }) => {
  const sizeClasses = {
    small: 'px-2 py-0.5 text-xs gap-1',
    default: 'px-3 py-1 text-sm gap-1.5',
    large: 'px-4 py-2 text-base gap-2'
  };
  
  const iconSize = {
    small: 'w-3 h-3',
    default: 'w-4 h-4',
    large: 'w-5 h-5'
  };

  return (
    <div 
      className={`inline-flex items-center bg-gradient-to-r from-amber-500 to-orange-500 text-white rounded-full font-bold ${sizeClasses[size]}`}
      data-testid="ambassador-badge"
    >
      <Award className={iconSize[size]} />
      {showLabel && <span>Founding Ambassador</span>}
    </div>
  );
};

// Ambassador Card for Profile - shows stats and activation
export const AmbassadorCard = ({ user, onActivate }) => {
  const [code, setCode] = useState('');
  const [activating, setActivating] = useState(false);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);
  const [isAmbassador, setIsAmbassador] = useState(user?.is_ambassador || false);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API}/ambassador/stats`);
      setStats(response.data);
      setIsAmbassador(response.data.is_ambassador || false);
    } catch (error) {
      console.error('Failed to fetch ambassador stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleActivate = async (e) => {
    e.preventDefault();
    if (!code.trim()) return;

    setActivating(true);
    try {
      const response = await axios.post(`${API}/ambassador/activate`, { code: code.trim() });
      if (response.data.success) {
        toast.success(response.data.message);
        if (onActivate) onActivate();
      } else {
        toast.error(response.data.message);
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Invalid ambassador code');
    } finally {
      setActivating(false);
      setCode('');
    }
  };

  const copyReferralLink = async () => {
    if (!stats?.referral_code) return;
    try {
      await navigator.clipboard.writeText(`https://edgemodeapp.com/auth?ref=${stats.referral_code}`);
      setCopied(true);
      toast.success('Referral link copied!');
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      toast.error('Failed to copy');
    }
  };

  if (loading) {
    return (
      <div className="bg-card border border-border rounded-lg p-4 animate-pulse">
        <div className="h-20 bg-muted rounded"></div>
      </div>
    );
  }

  // Already an ambassador - show stats
  if (isAmbassador && stats?.is_ambassador) {
    return (
      <div className="bg-gradient-to-br from-amber-500/10 to-orange-500/10 border border-amber-500/30 rounded-lg p-4">
        <div className="flex items-center justify-between mb-4">
          <AmbassadorBadge />
          {stats?.ambassador_since && (
            <span className="text-xs text-muted-foreground font-body">
              Since {format(parseISO(stats.ambassador_since), 'MMM yyyy')}
            </span>
          )}
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-3 gap-3 mb-4">
          <div className="bg-background/50 rounded-lg p-3 text-center">
            <div className="text-2xl font-mono font-bold text-foreground">{stats?.total_referrals || 0}</div>
            <div className="text-xs text-muted-foreground">Total Referrals</div>
          </div>
          <div className="bg-background/50 rounded-lg p-3 text-center">
            <div className="text-2xl font-mono font-bold text-foreground">{stats?.monthly_referrals || 0}</div>
            <div className="text-xs text-muted-foreground">This Month</div>
          </div>
          <div className="bg-background/50 rounded-lg p-3 text-center">
            <div className="text-2xl font-mono font-bold text-primary">FREE</div>
            <div className="text-xs text-muted-foreground">1 Year Access</div>
          </div>
        </div>

        {/* Referral Link */}
        <div className="bg-background/50 rounded-lg p-3">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-muted-foreground uppercase tracking-wide">Your Referral Link</span>
            <button
              onClick={copyReferralLink}
              className="text-primary hover:text-primary/80 transition-colors"
            >
              {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
            </button>
          </div>
          <div className="text-sm text-foreground font-mono truncate">
            edgemodeapp.com/auth?ref={stats?.referral_code}
          </div>
        </div>

        {/* Subscription End */}
        {stats?.subscription_end && (
          <div className="mt-3 text-center">
            <span className="text-xs text-muted-foreground">
              Free access until {format(parseISO(stats.subscription_end), 'MMM d, yyyy')}
            </span>
          </div>
        )}
      </div>
    );
  }

  // Not an ambassador - show activation form
  return (
    <div className="bg-card border border-border rounded-lg p-4">
      <div className="flex items-center gap-3 mb-4">
        <div className="w-10 h-10 bg-amber-500/20 rounded-full flex items-center justify-center">
          <Award className="w-5 h-5 text-amber-500" />
        </div>
        <div>
          <div className="text-foreground font-body font-medium">Founding Ambassador</div>
          <div className="text-muted-foreground text-sm font-body">Have a code? Enter it here</div>
        </div>
      </div>

      <form onSubmit={handleActivate} className="flex gap-2">
        <Input
          type="text"
          placeholder="Enter ambassador code"
          value={code}
          onChange={(e) => setCode(e.target.value.toUpperCase())}
          className="flex-1 bg-background border-border uppercase"
          data-testid="ambassador-code-input"
        />
        <Button
          type="submit"
          disabled={activating || !code.trim()}
          className="bg-gradient-to-r from-amber-500 to-orange-500 text-white hover:opacity-90"
          data-testid="activate-ambassador-btn"
        >
          {activating ? 'Activating...' : 'Activate'}
        </Button>
      </form>

      <p className="text-muted-foreground text-xs mt-3 font-body">
        Founding Ambassadors get 1 year free access + special recognition
      </p>
    </div>
  );
};
