import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { 
  UserPlus, 
  Copy, 
  Check, 
  Mail, 
  Link2, 
  Users, 
  Send,
  ChevronRight,
  ArrowLeft,
  Gift,
  Trophy,
  Lock,
  Sparkles
} from 'lucide-react';
import { toast } from 'sonner';
import { useNavigate } from 'react-router-dom';
import { format, parseISO } from 'date-fns';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export const InviteFriendsScreen = () => {
  const { user, fetchUser } = useAuth();
  const navigate = useNavigate();
  const [referralInfo, setReferralInfo] = useState(null);
  const [exclusiveRewards, setExclusiveRewards] = useState(null);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);
  const [copiedCode, setCopiedCode] = useState(false);
  const [friendEmail, setFriendEmail] = useState('');
  const [friendName, setFriendName] = useState('');
  const [sending, setSending] = useState(false);
  const [showInviteForm, setShowInviteForm] = useState(false);
  const [claimingReward, setClaimingReward] = useState(false);

  useEffect(() => {
    fetchReferralInfo();
    fetchExclusiveRewards();
  }, []);

  const fetchReferralInfo = async () => {
    try {
      const response = await axios.get(`${API}/referral/info`);
      setReferralInfo(response.data);
    } catch (error) {
      console.error('Failed to fetch referral info:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchExclusiveRewards = async () => {
    try {
      const response = await axios.get(`${API}/referrals/my-code`);
      setExclusiveRewards(response.data);
    } catch (error) {
      console.error('Failed to fetch exclusive rewards:', error);
    }
  };

  const copyToClipboard = async (text, type) => {
    try {
      await navigator.clipboard.writeText(text);
      if (type === 'link') {
        setCopied(true);
        toast.success('Invite link copied!');
        setTimeout(() => setCopied(false), 2000);
      } else {
        setCopiedCode(true);
        toast.success('Referral code copied!');
        setTimeout(() => setCopiedCode(false), 2000);
      }
    } catch (err) {
      toast.error('Failed to copy');
    }
  };

  const handleSendInvite = async (e) => {
    e.preventDefault();
    if (!friendEmail) return;

    setSending(true);
    try {
      const response = await axios.post(`${API}/referral/send-invite`, {
        friend_email: friendEmail,
        friend_name: friendName || null
      });

      if (response.data.already_member) {
        toast.info('This person is already on Edge Mode!');
      } else if (response.data.already_invited) {
        toast.info('You already invited this person recently');
      } else {
        toast.success('Invite sent! 🎉');
        setFriendEmail('');
        setFriendName('');
        setShowInviteForm(false);
        fetchReferralInfo(); // Refresh to show updated list
      }
    } catch (error) {
      console.error('Failed to send invite:', error);
      toast.error('Failed to send invite');
    } finally {
      setSending(false);
    }
  };

  const handleClaimReward = async () => {
    setClaimingReward(true);
    try {
      const response = await axios.post(`${API}/referral/claim-reward`);
      toast.success(response.data.message);
      fetchReferralInfo();
      if (fetchUser) fetchUser();
    } catch (error) {
      console.error('Failed to claim reward:', error);
      toast.error(error.response?.data?.detail || 'Failed to claim reward');
    } finally {
      setClaimingReward(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-[#09090b]">
        <div className="text-zinc-400 font-mono">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#09090b] pb-24" data-testid="invite-friends-screen">
      <div className="p-6">
        {/* Header */}
        <div className="flex items-center gap-3 mb-6">
          <button 
            onClick={() => navigate(-1)}
            className="p-2 rounded-lg bg-zinc-900 hover:bg-zinc-800 transition-colors"
          >
            <ArrowLeft className="w-5 h-5 text-zinc-400" />
          </button>
          <div>
            <h1 className="text-2xl font-heading font-bold uppercase tracking-tight text-white">
              Invite Friends
            </h1>
            <p className="text-zinc-400 font-body text-sm">
              Share Edge Mode with your friends
            </p>
          </div>
        </div>

        {/* Stats Card */}
        <div className="bg-zinc-950 border border-zinc-800 rounded-lg p-4 mb-6">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 bg-primary/20 rounded-full flex items-center justify-center">
              <Users className="w-7 h-7 text-primary" />
            </div>
            <div>
              <div className="text-3xl font-mono font-bold text-white">
                {referralInfo?.total_referrals || 0}
              </div>
              <div className="text-zinc-500 text-sm font-body">Friends Joined</div>
            </div>
          </div>
        </div>

        {/* Rewards Card */}
        <div className="bg-gradient-to-r from-amber-500/10 to-orange-500/10 border border-amber-500/30 rounded-lg p-4 mb-6">
          <div className="flex items-center gap-2 mb-3">
            <Gift className="w-5 h-5 text-amber-500" />
            <span className="text-sm font-heading uppercase tracking-wide text-amber-400">
              Referral Rewards
            </span>
          </div>
          
          {/* Progress bar */}
          <div className="mb-3">
            <div className="flex justify-between text-xs text-zinc-400 mb-1">
              <span>Progress to free month</span>
              <span>{referralInfo?.progress_to_next_reward || 0}/{referralInfo?.reward_threshold || 3}</span>
            </div>
            <div className="h-2 bg-zinc-800 rounded-full overflow-hidden">
              <div 
                className="h-full bg-gradient-to-r from-amber-500 to-orange-500 transition-all duration-500"
                style={{ width: `${((referralInfo?.progress_to_next_reward || 0) / (referralInfo?.reward_threshold || 3)) * 100}%` }}
              />
            </div>
          </div>
          
          <p className="text-zinc-400 text-sm font-body mb-3">
            Invite {referralInfo?.reward_threshold || 3} friends → Get {referralInfo?.reward_days || 30} days free!
          </p>
          
          {referralInfo?.rewards_available > 0 && (
            <Button
              onClick={handleClaimReward}
              disabled={claimingReward}
              className="w-full bg-gradient-to-r from-amber-500 to-orange-500 text-white hover:opacity-90 font-bold"
              data-testid="claim-reward-btn"
            >
              <Trophy className="w-4 h-4 mr-2" />
              {claimingReward ? 'Claiming...' : `Claim Free Month (${referralInfo.rewards_available} available)`}
            </Button>
          )}
        </div>

        {/* Exclusive Rewards Section */}
        {exclusiveRewards?.milestones && (
          <div className="bg-gradient-to-r from-emerald-500/10 to-teal-500/10 border border-emerald-500/30 rounded-lg p-4 mb-6">
            <div className="flex items-center gap-2 mb-4">
              <Sparkles className="w-5 h-5 text-emerald-400" />
              <span className="text-sm font-heading uppercase tracking-wide text-emerald-400">
                Exclusive Rewards
              </span>
            </div>
            
            <p className="text-zinc-400 text-sm font-body mb-2">
              Unlock exclusive items by inviting friends!
            </p>
            <p className="text-amber-400/80 text-xs font-body mb-4 flex items-center gap-1">
              <Trophy className="w-3 h-3" />
              Note: Referrals must log a minimum of 3 sessions to count.
            </p>

            <div className="space-y-3">
              {exclusiveRewards.milestones.map((milestone) => (
                <div 
                  key={milestone.id}
                  className={`p-3 rounded-lg border transition-all ${
                    milestone.is_claimed 
                      ? 'bg-emerald-900/30 border-emerald-500/50' 
                      : milestone.is_unlocked
                        ? 'bg-primary/20 border-primary/50'
                        : 'bg-zinc-900/50 border-zinc-700'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div className={`text-2xl ${!milestone.is_unlocked && 'grayscale opacity-50'}`}>
                      {milestone.reward_icon}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <span className="text-white font-medium text-sm">{milestone.reward_name}</span>
                        {milestone.is_claimed && (
                          <Check className="w-4 h-4 text-emerald-400" />
                        )}
                        {milestone.is_unlocked && !milestone.is_claimed && (
                          <span className="text-xs bg-primary/30 text-primary px-2 py-0.5 rounded-full">NEW!</span>
                        )}
                      </div>
                      <p className="text-zinc-500 text-xs">{milestone.reward_description}</p>
                      
                      {/* Progress bar */}
                      <div className="mt-2">
                        <div className="flex justify-between text-xs mb-1">
                          <span className="text-zinc-400">
                            {milestone.current}/{milestone.referrals_required} friends
                          </span>
                          <span className="text-yellow-400">+{milestone.coins_bonus} coins</span>
                        </div>
                        <div className="h-1.5 bg-zinc-800 rounded-full overflow-hidden">
                          <div 
                            className={`h-full transition-all ${milestone.is_claimed ? 'bg-emerald-500' : 'bg-primary'}`}
                            style={{ width: `${milestone.progress_pct}%` }}
                          />
                        </div>
                      </div>
                    </div>
                    {!milestone.is_unlocked && (
                      <Lock className="w-4 h-4 text-zinc-600" />
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Share Link Section */}
        <div className="bg-zinc-950 border border-zinc-800 rounded-lg p-4 mb-4">
          <div className="flex items-center gap-2 mb-3">
            <Link2 className="w-4 h-4 text-primary" />
            <span className="text-sm font-heading uppercase tracking-wide text-zinc-400">
              Your Invite Link
            </span>
          </div>
          <div className="flex gap-2">
            <div className="flex-1 bg-zinc-900 border border-zinc-700 rounded-md px-3 py-2 overflow-hidden">
              <span className="text-zinc-300 text-sm font-mono truncate block">
                {referralInfo?.referral_link}
              </span>
            </div>
            <Button
              onClick={() => copyToClipboard(referralInfo?.referral_link, 'link')}
              variant="outline"
              className="border-zinc-700 hover:bg-zinc-800"
              data-testid="copy-link-btn"
            >
              {copied ? (
                <Check className="w-4 h-4 text-green-500" />
              ) : (
                <Copy className="w-4 h-4" />
              )}
            </Button>
          </div>
        </div>

        {/* Referral Code Section */}
        <div className="bg-zinc-950 border border-zinc-800 rounded-lg p-4 mb-6">
          <div className="flex items-center gap-2 mb-3">
            <span className="text-sm font-heading uppercase tracking-wide text-zinc-400">
              Your Referral Code
            </span>
          </div>
          <div className="flex gap-2 items-center">
            <div className="flex-1 bg-zinc-900 border border-zinc-700 rounded-md px-4 py-3 text-center">
              <span className="text-xl font-mono font-bold text-primary tracking-wider">
                {referralInfo?.referral_code}
              </span>
            </div>
            <Button
              onClick={() => copyToClipboard(referralInfo?.referral_code, 'code')}
              variant="outline"
              className="border-zinc-700 hover:bg-zinc-800"
              data-testid="copy-code-btn"
            >
              {copiedCode ? (
                <Check className="w-4 h-4 text-green-500" />
              ) : (
                <Copy className="w-4 h-4" />
              )}
            </Button>
          </div>
          <p className="text-zinc-500 text-xs text-center mt-2 font-body">
            Friends can enter this code when signing up
          </p>
        </div>

        {/* Email Invite Section */}
        {!showInviteForm ? (
          <Button
            onClick={() => setShowInviteForm(true)}
            className="w-full bg-primary text-primary-foreground hover:bg-primary/90 font-heading uppercase"
            data-testid="show-email-invite-btn"
          >
            <Mail className="w-4 h-4 mr-2" />
            Send Email Invite
          </Button>
        ) : (
          <div className="bg-zinc-950 border border-zinc-800 rounded-lg p-4 mb-6">
            <div className="flex items-center gap-2 mb-4">
              <Mail className="w-4 h-4 text-primary" />
              <span className="text-sm font-heading uppercase tracking-wide text-zinc-400">
                Send Email Invite
              </span>
            </div>
            <form onSubmit={handleSendInvite} className="space-y-3">
              <Input
                type="text"
                placeholder="Friend's name (optional)"
                value={friendName}
                onChange={(e) => setFriendName(e.target.value)}
                className="bg-zinc-900 border-zinc-700"
                data-testid="friend-name-input"
              />
              <Input
                type="email"
                placeholder="Friend's email *"
                value={friendEmail}
                onChange={(e) => setFriendEmail(e.target.value)}
                required
                className="bg-zinc-900 border-zinc-700"
                data-testid="friend-email-input"
              />
              <div className="flex gap-2">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setShowInviteForm(false)}
                  className="flex-1 border-zinc-700"
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  disabled={sending || !friendEmail}
                  className="flex-1 bg-primary text-primary-foreground hover:bg-primary/90"
                  data-testid="send-invite-btn"
                >
                  {sending ? (
                    'Sending...'
                  ) : (
                    <>
                      <Send className="w-4 h-4 mr-2" />
                      Send Invite
                    </>
                  )}
                </Button>
              </div>
            </form>
          </div>
        )}

        {/* Referral History */}
        {referralInfo?.referrals?.length > 0 && (
          <div className="mt-6">
            <h3 className="text-sm font-heading uppercase tracking-wide text-zinc-500 mb-3">
              Friends Who Joined
            </h3>
            <div className="space-y-2">
              {referralInfo.referrals.map((ref, index) => (
                <div 
                  key={index}
                  className="bg-zinc-950 border border-zinc-800 rounded-lg p-3 flex items-center justify-between"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-primary/20 rounded-full flex items-center justify-center">
                      <UserPlus className="w-4 h-4 text-primary" />
                    </div>
                    <span className="text-zinc-300 text-sm font-body">
                      {ref.referred_email}
                    </span>
                  </div>
                  <span className="text-zinc-500 text-xs font-mono">
                    {format(parseISO(ref.created_at), 'MMM d')}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Tips Section */}
        <div className="mt-8 p-4 bg-zinc-900/50 rounded-lg border border-zinc-800">
          <h3 className="text-sm font-heading uppercase tracking-wide text-zinc-500 mb-2">
            Tips for Inviting
          </h3>
          <ul className="text-zinc-400 text-sm font-body space-y-1">
            <li>• Share with friends who want to build better habits</li>
            <li>• Post your link on social media</li>
            <li>• Create a group and challenge friends together</li>
          </ul>
        </div>
      </div>
    </div>
  );
};
