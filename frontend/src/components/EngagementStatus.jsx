import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'sonner';
import { Gift, Coins, Zap, Star, TrendingUp, Timer, Sparkles, ShoppingBag, HelpCircle } from 'lucide-react';
import { Button } from './ui/button';
import CoinEarningSheet from './CoinEarningSheet';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

// XP Event Banner Component
const XPEventBanner = ({ event }) => {
  const [timeLeft, setTimeLeft] = useState({ hours: 0, minutes: 0 });

  useEffect(() => {
    if (!event?.ends_at) return;

    const updateTimer = () => {
      const now = new Date();
      const endsAt = new Date(event.ends_at);
      const diff = endsAt - now;
      
      if (diff <= 0) {
        setTimeLeft({ hours: 0, minutes: 0 });
        return;
      }
      
      const hours = Math.floor(diff / (1000 * 60 * 60));
      const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
      setTimeLeft({ hours, minutes });
    };

    updateTimer();
    const interval = setInterval(updateTimer, 60000); // Update every minute
    return () => clearInterval(interval);
  }, [event?.ends_at]);

  if (!event) return null;

  return (
    <div 
      className="relative overflow-hidden rounded-lg p-3 bg-gradient-to-r from-purple-600/20 via-pink-500/20 to-orange-500/20 border border-purple-500/30"
      data-testid="xp-event-banner"
    >
      {/* Animated shimmer effect */}
      <div 
        className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent"
        style={{
          animation: 'shimmer 2s infinite',
          backgroundSize: '200% 100%'
        }}
      />
      <style>{`
        @keyframes shimmer {
          0% { background-position: 200% 0; }
          100% { background-position: -200% 0; }
        }
      `}</style>
      
      <div className="relative flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="text-2xl animate-bounce">{event.icon || '⚡'}</div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-white font-bold text-sm">{event.name}</span>
              <span className="px-2 py-0.5 bg-purple-500/30 text-purple-300 text-xs font-bold rounded-full">
                {event.multiplier}x XP
              </span>
            </div>
            <p className="text-zinc-400 text-xs">{event.description}</p>
          </div>
        </div>
        
        <div className="flex items-center gap-1 text-amber-400 bg-black/30 px-2 py-1 rounded-lg">
          <Timer className="w-3 h-3" />
          <span className="text-xs font-mono font-bold">
            {timeLeft.hours}h {timeLeft.minutes}m
          </span>
        </div>
      </div>
    </div>
  );
};

const DailyRewardPopup = ({ isOpen, onClose, rewardData }) => {
  if (!isOpen || !rewardData) return null;

  return (
    <div className="fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-4">
      <div className="bg-zinc-900 border border-primary/50 rounded-xl w-full max-w-sm p-6 text-center animate-in zoom-in-95 duration-300">
        <div className="w-20 h-20 bg-primary/20 rounded-full flex items-center justify-center mx-auto mb-4">
          <Gift className="w-10 h-10 text-primary animate-bounce" />
        </div>
        
        <h2 className="text-2xl font-bold text-white mb-2">Daily Reward!</h2>
        <p className="text-zinc-400 mb-6">Day {rewardData.login_streak} streak!</p>
        
        <div className="flex justify-center gap-6 mb-6">
          <div className="text-center">
            <div className="flex items-center justify-center gap-1 text-yellow-400">
              <Coins className="w-5 h-5" />
              <span className="text-2xl font-bold">+{rewardData.coins_earned}</span>
            </div>
            <p className="text-xs text-zinc-500">Coins</p>
          </div>
          <div className="text-center">
            <div className="flex items-center justify-center gap-1 text-purple-400">
              <Zap className="w-5 h-5" />
              <span className="text-2xl font-bold">+{rewardData.xp_earned}</span>
            </div>
            <p className="text-xs text-zinc-500">XP</p>
          </div>
        </div>
        
        {rewardData.leveled_up && (
          <div className="bg-primary/20 border border-primary/30 rounded-lg p-3 mb-4">
            <p className="text-primary font-bold">🎉 LEVEL UP!</p>
            <p className="text-white">Level {rewardData.level_info?.level}</p>
          </div>
        )}
        
        <Button onClick={onClose} className="w-full bg-primary hover:bg-primary/90 text-black font-bold">
          Awesome!
        </Button>
      </div>
    </div>
  );
};

const LevelBadge = ({ level, title, size = 'md' }) => {
  const sizeClasses = {
    sm: 'w-8 h-8 text-xs',
    md: 'w-12 h-12 text-sm',
    lg: 'w-16 h-16 text-lg'
  };

  const levelColors = {
    1: 'from-zinc-600 to-zinc-700',
    5: 'from-blue-500 to-blue-600',
    10: 'from-green-500 to-green-600',
    15: 'from-purple-500 to-purple-600',
    20: 'from-yellow-500 to-orange-500',
    25: 'from-red-500 to-pink-500',
  };

  let colorClass = 'from-zinc-600 to-zinc-700';
  for (const [lvl, color] of Object.entries(levelColors).reverse()) {
    if (level >= parseInt(lvl)) {
      colorClass = color;
      break;
    }
  }

  return (
    <div className="flex items-center gap-2">
      <div className={`${sizeClasses[size]} rounded-full bg-gradient-to-br ${colorClass} flex items-center justify-center font-bold text-white shadow-lg`}>
        {level}
      </div>
      {title && <span className="text-zinc-400 text-xs">{title}</span>}
    </div>
  );
};

const XPProgressBar = ({ levelInfo }) => {
  if (!levelInfo) return null;

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-4">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <LevelBadge level={levelInfo.level} title={levelInfo.title} size="sm" />
          <span className="text-white font-medium">Level {levelInfo.level}</span>
        </div>
        <span className="text-zinc-400 text-sm">{levelInfo.total_xp.toLocaleString()} XP</span>
      </div>
      <div className="h-2 bg-zinc-800 rounded-full overflow-hidden">
        <div 
          className="h-full bg-gradient-to-r from-primary to-green-400 transition-all duration-500"
          style={{ width: `${levelInfo.progress_pct}%` }}
        />
      </div>
      <div className="flex justify-between mt-1 text-xs text-zinc-500">
        <span>{levelInfo.xp_in_level} XP</span>
        <span>{levelInfo.xp_to_next_level} XP to Level {levelInfo.level + 1}</span>
      </div>
    </div>
  );
};

const EngagementStatus = () => {
  const navigate = useNavigate();
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showReward, setShowReward] = useState(false);
  const [rewardData, setRewardData] = useState(null);
  const [claiming, setClaiming] = useState(false);
  const [showCoinSheet, setShowCoinSheet] = useState(false);

  useEffect(() => {
    fetchStatus();
  }, []);

  const fetchStatus = async () => {
    try {
      const response = await axios.get(`${API}/engagement/status`);
      setStatus(response.data);
    } catch (error) {
      console.error('Failed to fetch engagement status:', error);
    } finally {
      setLoading(false);
    }
  };

  const claimDailyReward = async () => {
    setClaiming(true);
    try {
      const response = await axios.post(`${API}/engagement/daily-login`);
      if (!response.data.already_claimed) {
        setRewardData(response.data);
        setShowReward(true);
        fetchStatus(); // Refresh status
      } else {
        toast.info('Already claimed today!');
      }
    } catch (error) {
      toast.error('Failed to claim reward');
    } finally {
      setClaiming(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-4 animate-pulse">
        <div className="h-4 bg-zinc-800 rounded w-1/2 mb-3"></div>
        <div className="h-8 bg-zinc-800 rounded"></div>
      </div>
    );
  }

  return (
    <>
      <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-4 space-y-4">
        {/* Active XP Event Banner */}
        {status?.active_event && (
          <XPEventBanner event={status.active_event} />
        )}

        {/* Daily Reward Button */}
        {status?.can_claim_daily && (
          <Button
            onClick={claimDailyReward}
            disabled={claiming}
            className="w-full bg-gradient-to-r from-yellow-500 to-orange-500 hover:from-yellow-600 hover:to-orange-600 text-black font-bold py-3"
            data-testid="claim-daily-btn"
          >
            <Gift className="w-5 h-5 mr-2" />
            {claiming ? 'Claiming...' : (
              <>
                Claim Daily Reward!
                {status?.active_event && (
                  <span className="ml-2 text-xs bg-black/20 px-2 py-0.5 rounded-full">
                    {status.active_event.multiplier}x XP
                  </span>
                )}
              </>
            )}
          </Button>
        )}

        {/* Stats Row */}
        <div className="grid grid-cols-3 gap-3">
          <div 
            onClick={() => setShowCoinSheet(true)}
            className="text-center p-2 bg-zinc-950 rounded-lg cursor-pointer hover:bg-zinc-900 transition-colors group"
            data-testid="coins-earning-info"
          >
            <div className="flex items-center justify-center gap-1 text-yellow-400">
              <Coins className="w-4 h-4" />
              <span className="font-bold">{status?.coins || 0}</span>
            </div>
            <p className="text-xs text-zinc-500 group-hover:text-yellow-400/70 transition-colors flex items-center justify-center gap-1">
              <HelpCircle className="w-3 h-3" /> Earn Coins
            </p>
          </div>
          <div className="text-center p-2 bg-zinc-950 rounded-lg">
            <div className="flex items-center justify-center gap-1 text-orange-400">
              <TrendingUp className="w-4 h-4" />
              <span className="font-bold">{status?.login_streak || 0}</span>
            </div>
            <p className="text-xs text-zinc-500">Login Streak</p>
          </div>
          <div className="text-center p-2 bg-zinc-950 rounded-lg">
            <div className="flex items-center justify-center gap-1 text-purple-400">
              <Zap className="w-4 h-4" />
              <span className="font-bold">{status?.xp || 0}</span>
            </div>
            <p className="text-xs text-zinc-500">Total XP</p>
          </div>
        </div>

        {/* Vehicle Flex */}
        {status?.active_vehicle && (
          <div 
            onClick={() => navigate('/profile')}
            className="flex items-center gap-2 p-2 bg-zinc-950 rounded-lg cursor-pointer hover:bg-zinc-900 transition-colors"
            data-testid="dashboard-vehicle-flex"
          >
            <span className="text-2xl">{status.active_vehicle.icon}</span>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-semibold text-white truncate">{status.active_vehicle.name}</p>
              <p className="text-xs text-zinc-500 capitalize">{status.active_vehicle.rarity}</p>
            </div>
            <span className="text-xs text-zinc-600">My Ride</span>
          </div>
        )}

        {/* XP Progress */}
        <XPProgressBar levelInfo={status?.level_info} />
      </div>

      <DailyRewardPopup 
        isOpen={showReward} 
        onClose={() => setShowReward(false)} 
        rewardData={rewardData}
      />

      <CoinEarningSheet
        isOpen={showCoinSheet}
        onClose={() => setShowCoinSheet(false)}
        currentCoins={status?.coins || 0}
      />
    </>
  );
};

export { EngagementStatus, LevelBadge, XPProgressBar, DailyRewardPopup, XPEventBanner };
export default EngagementStatus;
