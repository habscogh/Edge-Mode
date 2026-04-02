import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'sonner';
import { Button } from './ui/button';
import { Input } from './ui/input';
import FriendStreaks from './FriendStreaks';
import {
  Users,
  Swords,
  Trophy,
  Clock,
  Target,
  Check,
  X,
  Plus,
  Mail,
  ChevronRight,
  Flame,
  Send
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const GOAL_TYPES = [
  { value: 'sessions', label: 'Sessions Logged', icon: Target },
  { value: 'minutes', label: 'Total Minutes', icon: Clock },
  { value: 'consistency', label: 'Consistency %', icon: Flame }
];

const DURATIONS = [
  { value: 3, label: '3 days' },
  { value: 7, label: '1 week' },
  { value: 14, label: '2 weeks' },
  { value: 30, label: '1 month' }
];

const CreateChallengeModal = ({ onClose, onCreated }) => {
  const [friendEmail, setFriendEmail] = useState('');
  const [name, setName] = useState('');
  const [goalType, setGoalType] = useState('sessions');
  const [goalValue, setGoalValue] = useState(10);
  const [duration, setDuration] = useState(7);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!friendEmail || !name) {
      toast.error('Please fill in all fields');
      return;
    }

    setSubmitting(true);
    try {
      const response = await axios.post(`${API}/challenges/friend/create`, {
        friend_email: friendEmail,
        name,
        goal_type: goalType,
        goal_value: goalValue,
        duration_days: duration
      });
      toast.success(response.data.message);
      onCreated();
      onClose();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create challenge');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-4">
      <div className="bg-zinc-900 border border-zinc-800 rounded-lg w-full max-w-md max-h-[90vh] overflow-y-auto">
        <div className="p-4 border-b border-zinc-800 flex items-center justify-between">
          <h3 className="text-white font-bold flex items-center gap-2">
            <Swords className="w-5 h-5 text-primary" />
            Challenge a Friend
          </h3>
          <button onClick={onClose} className="text-zinc-400 hover:text-white">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-4 space-y-4">
          <div>
            <label className="block text-zinc-400 text-sm mb-2">Friend's Email</label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
              <Input
                type="email"
                value={friendEmail}
                onChange={(e) => setFriendEmail(e.target.value)}
                placeholder="friend@example.com"
                className="pl-10 bg-zinc-950 border-zinc-700"
                required
                data-testid="friend-email-input"
              />
            </div>
          </div>

          <div>
            <label className="block text-zinc-400 text-sm mb-2">Challenge Name</label>
            <Input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Who can log more this week?"
              className="bg-zinc-950 border-zinc-700"
              required
              data-testid="challenge-name-input"
            />
          </div>

          <div>
            <label className="block text-zinc-400 text-sm mb-2">Competition Type</label>
            <div className="grid grid-cols-3 gap-2">
              {GOAL_TYPES.map((type) => (
                <button
                  key={type.value}
                  type="button"
                  onClick={() => setGoalType(type.value)}
                  className={`p-3 rounded-lg border transition-colors text-center ${
                    goalType === type.value
                      ? 'border-primary bg-primary/10 text-primary'
                      : 'border-zinc-700 bg-zinc-950 text-zinc-400 hover:border-zinc-600'
                  }`}
                >
                  <type.icon className="w-5 h-5 mx-auto mb-1" />
                  <span className="text-xs">{type.label}</span>
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-zinc-400 text-sm mb-2">Duration</label>
            <div className="grid grid-cols-4 gap-2">
              {DURATIONS.map((d) => (
                <button
                  key={d.value}
                  type="button"
                  onClick={() => setDuration(d.value)}
                  className={`py-2 px-3 rounded-lg border text-sm transition-colors ${
                    duration === d.value
                      ? 'border-primary bg-primary/10 text-primary'
                      : 'border-zinc-700 bg-zinc-950 text-zinc-400 hover:border-zinc-600'
                  }`}
                >
                  {d.label}
                </button>
              ))}
            </div>
          </div>

          <div className="flex gap-2 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              className="flex-1 border-zinc-700"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={submitting}
              className="flex-1 bg-primary hover:bg-primary/90 text-black font-bold"
              data-testid="send-challenge-btn"
            >
              {submitting ? 'Sending...' : <><Send className="w-4 h-4 mr-2" /> Send Challenge</>}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

const PendingChallengeCard = ({ challenge, type, onRespond }) => {
  const [responding, setResponding] = useState(false);

  const handleRespond = async (action) => {
    setResponding(true);
    try {
      const response = await axios.post(`${API}/challenges/friend/respond`, {
        challenge_id: challenge.id,
        action
      });
      toast.success(response.data.message);
      onRespond();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to respond');
    } finally {
      setResponding(false);
    }
  };

  return (
    <div className="bg-zinc-950 border border-zinc-800 rounded-lg p-4" data-testid={`pending-challenge-${challenge.id}`}>
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-amber-500/20 rounded-full flex items-center justify-center">
            <Swords className="w-5 h-5 text-amber-500" />
          </div>
          <div>
            <h4 className="text-white font-medium">{challenge.name}</h4>
            <p className="text-zinc-500 text-sm">
              {type === 'received' 
                ? `From: ${challenge.challenger_name}`
                : `To: ${challenge.challenged_name}`
              }
            </p>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-4 text-sm text-zinc-400 mb-4">
        <span className="flex items-center gap-1">
          <Target className="w-4 h-4" />
          {challenge.goal_type === 'sessions' ? 'Sessions' : 
           challenge.goal_type === 'minutes' ? 'Minutes' : 'Consistency'}
        </span>
        <span className="flex items-center gap-1">
          <Clock className="w-4 h-4" />
          {challenge.duration_days} days
        </span>
      </div>

      {type === 'received' && (
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={() => handleRespond('decline')}
            disabled={responding}
            className="flex-1 border-zinc-700 text-zinc-400"
          >
            <X className="w-4 h-4 mr-1" /> Decline
          </Button>
          <Button
            onClick={() => handleRespond('accept')}
            disabled={responding}
            className="flex-1 bg-primary hover:bg-primary/90 text-black font-bold"
            data-testid="accept-challenge-btn"
          >
            <Check className="w-4 h-4 mr-1" /> Accept
          </Button>
        </div>
      )}

      {type === 'sent' && (
        <div className="text-center py-2 text-zinc-500 text-sm">
          Waiting for response...
        </div>
      )}
    </div>
  );
};

const ActiveChallengeCard = ({ challenge }) => {
  const myScore = challenge.is_challenger ? challenge.challenger_score : challenge.challenged_score;
  const opponentScore = challenge.is_challenger ? challenge.challenged_score : challenge.challenger_score;
  const opponentName = challenge.is_challenger ? challenge.challenged_name : challenge.challenger_name;
  const isWinning = myScore > opponentScore;
  const isTied = myScore === opponentScore;

  return (
    <div className="bg-zinc-950 border border-primary/30 rounded-lg p-4" data-testid={`active-challenge-${challenge.id}`}>
      <div className="flex items-center justify-between mb-4">
        <div>
          <h4 className="text-white font-medium">{challenge.name}</h4>
          <p className="text-zinc-500 text-sm">vs {opponentName}</p>
        </div>
        <div className={`px-3 py-1 rounded-full text-sm font-medium ${
          isWinning ? 'bg-green-500/20 text-green-400' :
          isTied ? 'bg-amber-500/20 text-amber-400' :
          'bg-red-500/20 text-red-400'
        }`}>
          {isWinning ? 'Winning!' : isTied ? 'Tied' : 'Behind'}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="text-center p-3 bg-zinc-900 rounded-lg">
          <div className="text-2xl font-mono font-bold text-primary">{myScore}</div>
          <div className="text-zinc-500 text-xs">You</div>
        </div>
        <div className="text-center p-3 bg-zinc-900 rounded-lg">
          <div className="text-2xl font-mono font-bold text-zinc-400">{opponentScore}</div>
          <div className="text-zinc-500 text-xs">{opponentName}</div>
        </div>
      </div>

      <div className="flex items-center justify-between text-sm text-zinc-400">
        <span className="flex items-center gap-1">
          <Clock className="w-4 h-4" />
          {challenge.days_remaining} days left
        </span>
        <span className="capitalize">{challenge.goal_type}</span>
      </div>
    </div>
  );
};

const FriendChallenges = () => {
  const [pendingChallenges, setPendingChallenges] = useState({ received: [], sent: [] });
  const [activeChallenges, setActiveChallenges] = useState([]);
  const [history, setHistory] = useState([]);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [activeTab, setActiveTab] = useState('active'); // 'active', 'pending', 'history'
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    try {
      const [pendingRes, activeRes, historyRes] = await Promise.all([
        axios.get(`${API}/challenges/friend/pending`),
        axios.get(`${API}/challenges/friend/active`),
        axios.get(`${API}/challenges/friend/history`)
      ]);
      setPendingChallenges(pendingRes.data);
      setActiveChallenges(activeRes.data.challenges);
      setHistory(historyRes.data.challenges);
    } catch (error) {
      console.error('Failed to fetch friend challenges:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const totalPending = pendingChallenges.received.length + pendingChallenges.sent.length;

  if (loading) {
    return (
      <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-zinc-800 rounded w-1/3"></div>
          <div className="h-24 bg-zinc-800 rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Friend Streaks Section */}
      <FriendStreaks compact />

      {/* Friend Challenges Section */}
      <div className="bg-zinc-900 border border-zinc-800 rounded-lg overflow-hidden">
        <div className="p-4 border-b border-zinc-800 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Swords className="w-5 h-5 text-primary" />
            <h3 className="text-white font-bold">Friend Challenges</h3>
            <span className="text-xs bg-primary/20 text-primary px-2 py-0.5 rounded-full">1v1</span>
          </div>
          <Button
            onClick={() => setShowCreateModal(true)}
            size="sm"
            className="bg-primary hover:bg-primary/90 text-black font-bold"
            data-testid="create-friend-challenge-btn"
          >
            <Plus className="w-4 h-4 mr-1" /> Challenge
          </Button>
        </div>

      {/* Tabs */}
      <div className="flex border-b border-zinc-800">
        <button
          onClick={() => setActiveTab('active')}
          className={`flex-1 py-3 text-sm font-medium transition-colors ${
            activeTab === 'active' ? 'text-primary border-b-2 border-primary' : 'text-zinc-400'
          }`}
        >
          Active ({activeChallenges.length})
        </button>
        <button
          onClick={() => setActiveTab('pending')}
          className={`flex-1 py-3 text-sm font-medium transition-colors relative ${
            activeTab === 'pending' ? 'text-primary border-b-2 border-primary' : 'text-zinc-400'
          }`}
        >
          Pending ({totalPending})
          {pendingChallenges.received.length > 0 && (
            <span className="absolute top-2 right-1/4 w-2 h-2 bg-red-500 rounded-full"></span>
          )}
        </button>
        <button
          onClick={() => setActiveTab('history')}
          className={`flex-1 py-3 text-sm font-medium transition-colors ${
            activeTab === 'history' ? 'text-primary border-b-2 border-primary' : 'text-zinc-400'
          }`}
        >
          History ({history.length})
        </button>
      </div>

      <div className="p-4 space-y-4">
        {activeTab === 'active' && (
          <>
            {activeChallenges.length === 0 ? (
              <div className="text-center py-8 text-zinc-500">
                <Swords className="w-12 h-12 mx-auto mb-3 opacity-50" />
                <p>No active challenges</p>
                <p className="text-sm mt-1">Challenge a friend to get started!</p>
              </div>
            ) : (
              activeChallenges.map((c) => <ActiveChallengeCard key={c.id} challenge={c} />)
            )}
          </>
        )}

        {activeTab === 'pending' && (
          <>
            {pendingChallenges.received.length > 0 && (
              <div>
                <h4 className="text-zinc-400 text-sm mb-3">Received Challenges</h4>
                <div className="space-y-3">
                  {pendingChallenges.received.map((c) => (
                    <PendingChallengeCard key={c.id} challenge={c} type="received" onRespond={fetchData} />
                  ))}
                </div>
              </div>
            )}

            {pendingChallenges.sent.length > 0 && (
              <div>
                <h4 className="text-zinc-400 text-sm mb-3">Sent Challenges</h4>
                <div className="space-y-3">
                  {pendingChallenges.sent.map((c) => (
                    <PendingChallengeCard key={c.id} challenge={c} type="sent" onRespond={fetchData} />
                  ))}
                </div>
              </div>
            )}

            {totalPending === 0 && (
              <div className="text-center py-8 text-zinc-500">
                <Mail className="w-12 h-12 mx-auto mb-3 opacity-50" />
                <p>No pending challenges</p>
              </div>
            )}
          </>
        )}

        {activeTab === 'history' && (
          <>
            {history.length === 0 ? (
              <div className="text-center py-8 text-zinc-500">
                <Trophy className="w-12 h-12 mx-auto mb-3 opacity-50" />
                <p>No completed challenges yet</p>
              </div>
            ) : (
              <div className="space-y-3">
                {history.map((c) => (
                  <div
                    key={c.id}
                    className={`bg-zinc-950 border rounded-lg p-4 ${
                      c.won ? 'border-green-500/30' : c.winner_id === 'tie' ? 'border-amber-500/30' : 'border-zinc-800'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="text-white font-medium">{c.name}</h4>
                      <div className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                        c.won ? 'bg-green-500/20 text-green-400' :
                        c.winner_id === 'tie' ? 'bg-amber-500/20 text-amber-400' :
                        'bg-zinc-800 text-zinc-400'
                      }`}>
                        {c.won ? 'WON' : c.winner_id === 'tie' ? 'TIE' : 'LOST'}
                      </div>
                    </div>
                    <div className="flex items-center justify-between text-sm text-zinc-400">
                      <span>vs {c.is_challenger ? c.challenged_name : c.challenger_name}</span>
                      <span>{c.challenger_score} - {c.challenged_score}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </>
        )}
      </div>

      {showCreateModal && (
        <CreateChallengeModal
          onClose={() => setShowCreateModal(false)}
          onCreated={fetchData}
        />
      )}
      </div>
    </div>
  );
};

export default FriendChallenges;
