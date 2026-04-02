import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'sonner';
import { Gift, Coins, Zap, Star, TrendingUp } from 'lucide-react';
import { Button } from './ui/button';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

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
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showReward, setShowReward] = useState(false);
  const [rewardData, setRewardData] = useState(null);
  const [claiming, setClaiming] = useState(false);

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
        {/* Daily Reward Button */}
        {status?.can_claim_daily && (
          <Button
            onClick={claimDailyReward}
            disabled={claiming}
            className="w-full bg-gradient-to-r from-yellow-500 to-orange-500 hover:from-yellow-600 hover:to-orange-600 text-black font-bold py-3"
            data-testid="claim-daily-btn"
          >
            <Gift className="w-5 h-5 mr-2" />
            {claiming ? 'Claiming...' : 'Claim Daily Reward!'}
          </Button>
        )}

        {/* Stats Row */}
        <div className="grid grid-cols-3 gap-3">
          <div className="text-center p-2 bg-zinc-950 rounded-lg">
            <div className="flex items-center justify-center gap-1 text-yellow-400">
              <Coins className="w-4 h-4" />
              <span className="font-bold">{status?.coins || 0}</span>
            </div>
            <p className="text-xs text-zinc-500">Coins</p>
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

        {/* XP Progress */}
        <XPProgressBar levelInfo={status?.level_info} />
      </div>

      <DailyRewardPopup 
        isOpen={showReward} 
        onClose={() => setShowReward(false)} 
        rewardData={rewardData}
      />
    </>
  );
};

export { EngagementStatus, LevelBadge, XPProgressBar, DailyRewardPopup };
export default EngagementStatus;
