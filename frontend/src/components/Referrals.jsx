import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'sonner';
import { Button } from './ui/button';
import {
  Users,
  Gift,
  Share2,
  Copy,
  Check,
  Lock,
  ChevronRight,
  Trophy,
  Crown,
  Sparkles,
  Link2
} from 'lucide-react';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

// Milestone Card Component
const MilestoneCard = ({ milestone }) => {
  const isUnlocked = milestone.is_unlocked;
  const isClaimed = milestone.is_claimed;

  return (
    <div 
      className={`p-4 rounded-xl border-2 transition-all ${
        isClaimed 
          ? 'bg-green-900/20 border-green-500/50' 
          : isUnlocked
            ? 'bg-primary/10 border-primary/50 animate-pulse'
            : 'bg-zinc-900 border-zinc-800'
      }`}
      data-testid={`milestone-${milestone.id}`}
    >
      <div className="flex items-center gap-3">
        <div className={`text-3xl ${!isUnlocked && 'grayscale opacity-50'}`}>
          {milestone.reward_icon}
        </div>
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <h4 className="text-white font-bold text-sm">{milestone.reward_name}</h4>
            {isClaimed && (
              <span className="bg-green-500/20 text-green-400 text-xs px-2 py-0.5 rounded-full flex items-center gap-1">
                <Check className="w-3 h-3" /> Unlocked
              </span>
            )}
            {isUnlocked && !isClaimed && (
              <span className="bg-primary/20 text-primary text-xs px-2 py-0.5 rounded-full animate-bounce">
                NEW!
              </span>
            )}
          </div>
          <p className="text-zinc-500 text-xs">{milestone.reward_description}</p>
          
          {/* Progress */}
          <div className="mt-2">
            <div className="flex items-center justify-between text-xs mb-1">
              <span className="text-zinc-400">
                {milestone.current}/{milestone.referrals_required} friends
              </span>
              <span className="text-yellow-400">+{milestone.coins_bonus} coins</span>
            </div>
            <div className="h-1.5 bg-zinc-800 rounded-full overflow-hidden">
              <div 
                className={`h-full transition-all ${isClaimed ? 'bg-green-500' : 'bg-primary'}`}
                style={{ width: `${milestone.progress_pct}%` }}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Exclusive Item Preview
const ExclusiveItemCard = ({ item }) => {
  const isUnlocked = item.is_unlocked;
  const isOwned = item.is_owned;

  return (
    <div 
      className={`p-3 rounded-lg border transition-all ${
        isOwned 
          ? 'bg-green-900/20 border-green-500/30' 
          : isUnlocked
            ? 'bg-primary/10 border-primary/30'
            : 'bg-zinc-900 border-zinc-800 opacity-60'
      }`}
    >
      <div className="flex items-center gap-3">
        <div className={`text-2xl ${!isUnlocked && 'grayscale'}`}>
          {item.icon}
        </div>
        <div className="flex-1">
          <p className="text-white text-sm font-medium">{item.name}</p>
          <p className="text-zinc-500 text-xs">
            {isOwned ? 'Owned!' : isUnlocked ? 'Unlocked!' : `${item.referrals_needed} more invites`}
          </p>
        </div>
        {!isUnlocked && <Lock className="w-4 h-4 text-zinc-600" />}
        {isOwned && <Check className="w-4 h-4 text-green-400" />}
      </div>
    </div>
  );
};

// Main Referral Section Component
const ReferralSection = () => {
  const [data, setData] = useState(null);
  const [exclusiveItems, setExclusiveItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);
  const [showAll, setShowAll] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [codeRes, itemsRes] = await Promise.all([
        axios.get(`${API}/referrals/my-code`),
        axios.get(`${API}/referrals/exclusive-items`)
      ]);
      setData(codeRes.data);
      setExclusiveItems(itemsRes.data.items);
    } catch (error) {
      console.error('Failed to fetch referral data:', error);
    } finally {
      setLoading(false);
    }
  };

  const copyCode = () => {
    if (data?.referral_code) {
      navigator.clipboard.writeText(data.referral_code);
      setCopied(true);
      toast.success('Referral code copied!');
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const shareLink = async () => {
    if (data?.referral_link) {
      if (navigator.share) {
        try {
          await navigator.share({
            title: 'Join me on Edge Mode!',
            text: `Use my code ${data.referral_code} to get bonus coins when you sign up!`,
            url: data.referral_link
          });
        } catch (err) {
          copyCode();
        }
      } else {
        navigator.clipboard.writeText(data.referral_link);
        toast.success('Invite link copied!');
      }
    }
  };

  if (loading) {
    return (
      <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-4 animate-pulse">
        <div className="h-4 bg-zinc-800 rounded w-1/3 mb-3"></div>
        <div className="h-20 bg-zinc-800 rounded"></div>
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg overflow-hidden" data-testid="referral-section">
      {/* Header */}
      <div className="p-4 border-b border-zinc-800 bg-gradient-to-r from-emerald-900/20 to-teal-900/20">
        <div className="flex items-center gap-2 mb-1">
          <Users className="w-5 h-5 text-emerald-400" />
          <h3 className="text-white font-bold">Invite Friends</h3>
          <span className="bg-emerald-500/20 text-emerald-400 text-xs px-2 py-0.5 rounded-full">
            Earn Exclusive Rewards
          </span>
        </div>
        <p className="text-zinc-400 text-sm">
          {data.referral_count} friend{data.referral_count !== 1 ? 's' : ''} invited
          {data.next_milestone && ` • ${data.referrals_until_next} more for ${data.next_milestone.reward_name}`}
        </p>
      </div>

      {/* Referral Code */}
      <div className="p-4 border-b border-zinc-800">
        <p className="text-zinc-400 text-xs mb-2">Your Referral Code</p>
        <div className="flex items-center gap-2">
          <div className="flex-1 bg-zinc-950 border border-zinc-700 rounded-lg px-4 py-3 font-mono text-lg text-white tracking-wider">
            {data.referral_code}
          </div>
          <Button
            onClick={copyCode}
            variant="outline"
            size="icon"
            className="shrink-0"
            data-testid="copy-code-btn"
          >
            {copied ? <Check className="w-4 h-4 text-green-400" /> : <Copy className="w-4 h-4" />}
          </Button>
          <Button
            onClick={shareLink}
            className="shrink-0 bg-emerald-600 hover:bg-emerald-700"
            data-testid="share-btn"
          >
            <Share2 className="w-4 h-4 mr-2" />
            Share
          </Button>
        </div>
      </div>

      {/* Exclusive Rewards Preview */}
      <div className="p-4 border-b border-zinc-800">
        <div className="flex items-center justify-between mb-3">
          <h4 className="text-white font-medium text-sm flex items-center gap-2">
            <Gift className="w-4 h-4 text-yellow-400" />
            Exclusive Rewards
          </h4>
          <button 
            onClick={() => setShowAll(!showAll)}
            className="text-primary text-xs flex items-center gap-1"
          >
            {showAll ? 'Show less' : 'View all'}
            <ChevronRight className={`w-3 h-3 transition-transform ${showAll ? 'rotate-90' : ''}`} />
          </button>
        </div>
        <div className="space-y-2">
          {(showAll ? exclusiveItems : exclusiveItems.slice(0, 2)).map(item => (
            <ExclusiveItemCard key={item.id} item={item} />
          ))}
        </div>
      </div>

      {/* Milestones */}
      <div className="p-4">
        <h4 className="text-white font-medium text-sm mb-3 flex items-center gap-2">
          <Trophy className="w-4 h-4 text-amber-400" />
          Milestones
        </h4>
        <div className="space-y-3">
          {data.milestones.map(milestone => (
            <MilestoneCard key={milestone.id} milestone={milestone} />
          ))}
        </div>
      </div>
    </div>
  );
};

// Compact Referral Widget (for dashboard)
const ReferralWidget = ({ onClick }) => {
  const [data, setData] = useState(null);

  useEffect(() => {
    axios.get(`${API}/referrals/my-code`)
      .then(res => setData(res.data))
      .catch(err => console.error(err));
  }, []);

  if (!data) return null;

  return (
    <div 
      onClick={onClick}
      className="bg-gradient-to-r from-emerald-900/30 to-teal-900/30 border border-emerald-500/30 rounded-lg p-4 cursor-pointer hover:border-emerald-500/50 transition-colors"
      data-testid="referral-widget"
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-emerald-500/20 rounded-full flex items-center justify-center">
            <Users className="w-5 h-5 text-emerald-400" />
          </div>
          <div>
            <p className="text-white font-medium text-sm">Invite Friends</p>
            <p className="text-emerald-400 text-xs">
              {data.referral_count} invited • {data.referrals_until_next || 0} until next reward
            </p>
          </div>
        </div>
        <ChevronRight className="w-5 h-5 text-zinc-500" />
      </div>
    </div>
  );
};

export { ReferralSection, ReferralWidget, MilestoneCard, ExclusiveItemCard };
export default ReferralSection;
