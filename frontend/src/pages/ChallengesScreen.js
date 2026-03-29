import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'sonner';
import { Button } from '../components/ui/button';
import FriendChallenges from '../components/FriendChallenges';
import { 
  Trophy, 
  Calendar, 
  Users, 
  ChevronRight, 
  Clock, 
  Target, 
  Flame,
  Medal,
  ArrowLeft,
  Check,
  X
} from 'lucide-react';
import { format, parseISO, differenceInDays } from 'date-fns';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ChallengeCard = ({ challenge, onJoin, onLeave, onViewLeaderboard }) => {
  const isActive = challenge.status === 'active';
  const isUpcoming = challenge.status === 'upcoming';
  const isCompleted = challenge.status === 'completed';
  const isParticipating = challenge.is_participating;
  
  const startDate = parseISO(challenge.start_date);
  const endDate = parseISO(challenge.end_date);
  const daysLeft = differenceInDays(endDate, new Date());
  
  const getMetricLabel = () => {
    switch(challenge.metric_type) {
      case 'pillar_sessions': return 'Sessions';
      case 'pillar_minutes': return 'Minutes';
      case 'total_sessions': return 'Total Sessions';
      case 'total_minutes': return 'Total Minutes';
      case 'consistency': return 'Consistency %';
      default: return 'Score';
    }
  };

  const getChallengeIcon = () => {
    if (challenge.challenge_type === 'monthly') return <Calendar className="w-5 h-5" />;
    if (challenge.metric_type === 'consistency') return <Target className="w-5 h-5" />;
    if (challenge.metric_type.includes('minutes')) return <Clock className="w-5 h-5" />;
    return <Flame className="w-5 h-5" />;
  };

  return (
    <div 
      className={`bg-zinc-950 border rounded-lg p-4 mb-3 transition-all ${
        isParticipating ? 'border-primary/50' : 'border-zinc-800'
      } ${isCompleted ? 'opacity-60' : ''}`}
      data-testid={`challenge-card-${challenge.id}`}
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
            challenge.challenge_type === 'monthly' ? 'bg-amber-500/20 text-amber-500' : 'bg-primary/20 text-primary'
          }`}>
            {getChallengeIcon()}
          </div>
          <div>
            <h3 className="text-white font-medium font-body">{challenge.name}</h3>
            <div className="flex items-center gap-2 text-xs text-zinc-500">
              <span className={`px-2 py-0.5 rounded-full ${
                challenge.challenge_type === 'monthly' ? 'bg-amber-500/20 text-amber-400' : 'bg-primary/20 text-primary'
              }`}>
                {challenge.challenge_type === 'monthly' ? 'MONTHLY' : 'WEEKLY'}
              </span>
              {challenge.pillar && (
                <span className="text-zinc-400">{challenge.pillar.split('/')[0]}</span>
              )}
            </div>
          </div>
        </div>
        {isParticipating && (
          <div className="flex items-center gap-1 text-primary text-xs">
            <Check className="w-4 h-4" />
            <span>Joined</span>
          </div>
        )}
      </div>

      <p className="text-zinc-400 text-sm mb-3 font-body">{challenge.description}</p>

      <div className="flex items-center justify-between text-xs text-zinc-500 mb-3">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-1">
            <Users className="w-4 h-4" />
            <span>{challenge.participant_count} joined</span>
          </div>
          {isActive && (
            <div className="flex items-center gap-1">
              <Clock className="w-4 h-4" />
              <span>{daysLeft > 0 ? `${daysLeft} days left` : 'Ends today'}</span>
            </div>
          )}
          {isUpcoming && (
            <span className="text-amber-400">Starts {format(startDate, 'MMM d')}</span>
          )}
          {isCompleted && (
            <span className="text-zinc-500">Ended {format(endDate, 'MMM d')}</span>
          )}
        </div>
        <span className="text-zinc-400">{getMetricLabel()}</span>
      </div>

      {isParticipating && challenge.user_rank && (
        <div className="bg-zinc-900 rounded-lg p-3 mb-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Medal className={`w-5 h-5 ${
                challenge.user_rank === 1 ? 'text-amber-400' :
                challenge.user_rank === 2 ? 'text-zinc-300' :
                challenge.user_rank === 3 ? 'text-amber-600' : 'text-zinc-500'
              }`} />
              <span className="text-white font-mono">#{challenge.user_rank}</span>
            </div>
            <div className="text-right">
              <div className="text-primary font-mono font-bold">
                {challenge.metric_type === 'consistency' 
                  ? `${challenge.user_score?.toFixed(1)}%` 
                  : challenge.user_score}
              </div>
              <div className="text-zinc-500 text-xs">{getMetricLabel()}</div>
            </div>
          </div>
        </div>
      )}

      <div className="flex gap-2">
        {isActive && !isParticipating && (
          <Button 
            onClick={() => onJoin(challenge.id)}
            className="flex-1 bg-primary hover:bg-primary/90 text-black font-mono"
            data-testid={`join-challenge-${challenge.id}`}
          >
            Join Challenge
          </Button>
        )}
        {isActive && isParticipating && (
          <>
            <Button 
              onClick={() => onViewLeaderboard(challenge.id)}
              className="flex-1 bg-zinc-800 hover:bg-zinc-700 text-white font-mono"
              data-testid={`view-leaderboard-${challenge.id}`}
            >
              View Leaderboard
            </Button>
            <Button 
              onClick={() => onLeave(challenge.id)}
              variant="outline"
              className="border-zinc-700 hover:bg-zinc-800 text-zinc-400"
              data-testid={`leave-challenge-${challenge.id}`}
            >
              <X className="w-4 h-4" />
            </Button>
          </>
        )}
        {(isCompleted || isUpcoming) && (
          <Button 
            onClick={() => onViewLeaderboard(challenge.id)}
            className="flex-1 bg-zinc-800 hover:bg-zinc-700 text-white font-mono"
            data-testid={`view-leaderboard-${challenge.id}`}
          >
            {isCompleted ? 'View Results' : 'Preview'}
          </Button>
        )}
      </div>
    </div>
  );
};

const ChallengeLeaderboardModal = ({ challenge, leaderboard, userRank, userScore, onClose }) => {
  if (!challenge) return null;

  const getMetricLabel = () => {
    switch(challenge.metric_type) {
      case 'pillar_sessions': return 'Sessions';
      case 'pillar_minutes': return 'Minutes';
      case 'total_sessions': return 'Sessions';
      case 'total_minutes': return 'Minutes';
      case 'consistency': return 'Consistency';
      default: return 'Score';
    }
  };

  return (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
      <div className="bg-zinc-950 border border-zinc-800 rounded-lg w-full max-w-md max-h-[80vh] overflow-hidden">
        <div className="p-4 border-b border-zinc-800 flex items-center justify-between">
          <div>
            <h2 className="text-white font-bold font-body">{challenge.name}</h2>
            <p className="text-zinc-500 text-sm">{challenge.participant_count} participants</p>
          </div>
          <button 
            onClick={onClose}
            className="text-zinc-400 hover:text-white"
            data-testid="close-leaderboard-modal"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {userRank && (
          <div className="p-4 bg-primary/10 border-b border-zinc-800">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-primary/20 rounded-full flex items-center justify-center">
                  <span className="text-primary font-mono font-bold">#{userRank}</span>
                </div>
                <div>
                  <div className="text-white font-medium">Your Position</div>
                  <div className="text-zinc-400 text-sm">Keep pushing!</div>
                </div>
              </div>
              <div className="text-right">
                <div className="text-primary font-mono font-bold text-lg">
                  {challenge.metric_type === 'consistency' ? `${userScore?.toFixed(1)}%` : userScore}
                </div>
                <div className="text-zinc-500 text-xs">{getMetricLabel()}</div>
              </div>
            </div>
          </div>
        )}

        <div className="overflow-y-auto max-h-[50vh]">
          {leaderboard.length === 0 ? (
            <div className="p-8 text-center text-zinc-500">
              No participants yet. Be the first to join!
            </div>
          ) : (
            <div className="divide-y divide-zinc-800">
              {leaderboard.map((participant, index) => (
                <div 
                  key={participant.id}
                  className={`p-4 flex items-center justify-between ${
                    participant.rank <= 3 ? 'bg-zinc-900/50' : ''
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center font-mono font-bold ${
                      participant.rank === 1 ? 'bg-amber-500/20 text-amber-400' :
                      participant.rank === 2 ? 'bg-zinc-400/20 text-zinc-300' :
                      participant.rank === 3 ? 'bg-amber-700/20 text-amber-600' : 
                      'bg-zinc-800 text-zinc-400'
                    }`}>
                      {participant.rank <= 3 ? (
                        <Medal className="w-4 h-4" />
                      ) : (
                        participant.rank
                      )}
                    </div>
                    <div>
                      <div className="text-white font-medium">{participant.username}</div>
                      {participant.rank <= 3 && (
                        <div className="text-xs text-zinc-500">
                          {participant.rank === 1 ? '1st Place' : 
                           participant.rank === 2 ? '2nd Place' : '3rd Place'}
                        </div>
                      )}
                    </div>
                  </div>
                  <div className="text-right">
                    <div className={`font-mono font-bold ${
                      participant.rank === 1 ? 'text-amber-400' : 'text-white'
                    }`}>
                      {challenge.metric_type === 'consistency' 
                        ? `${participant.current_score?.toFixed(1)}%` 
                        : participant.current_score}
                    </div>
                    <div className="text-zinc-500 text-xs">{getMetricLabel()}</div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export const ChallengesScreen = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [challenges, setChallenges] = useState([]);
  const [myChallenges, setMyChallenges] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('all'); // 'all', 'my', 'weekly', 'monthly'
  const [selectedChallenge, setSelectedChallenge] = useState(null);
  const [leaderboardData, setLeaderboardData] = useState(null);

  useEffect(() => {
    fetchChallenges();
  }, []);

  const fetchChallenges = async () => {
    try {
      const [allRes, myRes] = await Promise.all([
        axios.get(`${API}/challenges`),
        axios.get(`${API}/challenges/my`)
      ]);
      setChallenges(allRes.data);
      setMyChallenges(myRes.data);
    } catch (error) {
      console.error('Failed to fetch challenges:', error);
      toast.error('Failed to load challenges');
    } finally {
      setLoading(false);
    }
  };

  const handleJoinChallenge = async (challengeId) => {
    try {
      await axios.post(`${API}/challenges/join`, { challenge_id: challengeId });
      toast.success('Successfully joined the challenge!');
      fetchChallenges();
    } catch (error) {
      console.error('Failed to join challenge:', error);
      toast.error(error.response?.data?.detail || 'Failed to join challenge');
    }
  };

  const handleLeaveChallenge = async (challengeId) => {
    try {
      await axios.post(`${API}/challenges/leave/${challengeId}`);
      toast.success('Left the challenge');
      fetchChallenges();
    } catch (error) {
      console.error('Failed to leave challenge:', error);
      toast.error(error.response?.data?.detail || 'Failed to leave challenge');
    }
  };

  const handleViewLeaderboard = async (challengeId) => {
    try {
      const response = await axios.get(`${API}/challenges/${challengeId}/leaderboard`);
      setSelectedChallenge(response.data.challenge);
      setLeaderboardData({
        leaderboard: response.data.leaderboard,
        userRank: response.data.user_rank,
        userScore: response.data.user_score
      });
    } catch (error) {
      console.error('Failed to fetch leaderboard:', error);
      toast.error('Failed to load leaderboard');
    }
  };

  const closeLeaderboard = () => {
    setSelectedChallenge(null);
    setLeaderboardData(null);
  };

  const getFilteredChallenges = () => {
    let filtered = challenges;
    
    if (activeTab === 'my') {
      return myChallenges;
    } else if (activeTab === 'weekly') {
      filtered = challenges.filter(c => c.challenge_type === 'weekly');
    } else if (activeTab === 'monthly') {
      filtered = challenges.filter(c => c.challenge_type === 'monthly');
    }
    
    // Sort: active first, then upcoming, then completed
    return filtered.sort((a, b) => {
      const statusOrder = { active: 0, upcoming: 1, completed: 2 };
      return statusOrder[a.status] - statusOrder[b.status];
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-[#09090b]">
        <div className="text-zinc-400 font-mono">Loading challenges...</div>
      </div>
    );
  }

  const filteredChallenges = getFilteredChallenges();
  const activeChallengesCount = challenges.filter(c => c.status === 'active').length;
  const myActiveChallenges = myChallenges.filter(c => c.status === 'active').length;

  return (
    <div className="min-h-screen bg-[#09090b] pb-24">
      {/* Header */}
      <div className="bg-zinc-950 border-b border-zinc-800 p-4">
        <div className="flex items-center gap-3 mb-4">
          <button 
            onClick={() => navigate(-1)} 
            className="text-zinc-400 hover:text-white"
            data-testid="back-btn"
          >
            <ArrowLeft className="w-6 h-6" />
          </button>
          <div>
            <h1 className="text-xl font-bold text-white font-heading">Challenges</h1>
            <p className="text-zinc-500 text-sm font-body">Compete & earn badges</p>
          </div>
        </div>

        {/* Stats Bar */}
        <div className="flex gap-4 mb-4">
          <div className="bg-zinc-900 rounded-lg px-4 py-2 flex-1 text-center">
            <div className="text-primary font-mono font-bold text-lg">{activeChallengesCount}</div>
            <div className="text-zinc-500 text-xs">Active</div>
          </div>
          <div className="bg-zinc-900 rounded-lg px-4 py-2 flex-1 text-center">
            <div className="text-amber-400 font-mono font-bold text-lg">{myActiveChallenges}</div>
            <div className="text-zinc-500 text-xs">Joined</div>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 overflow-x-auto pb-2">
          {[
            { id: 'all', label: 'All' },
            { id: 'my', label: 'My Challenges' },
            { id: 'weekly', label: 'Weekly' },
            { id: 'monthly', label: 'Monthly' }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2 rounded-full text-sm font-mono whitespace-nowrap transition-colors ${
                activeTab === tab.id
                  ? 'bg-primary text-black'
                  : 'bg-zinc-800 text-zinc-400 hover:bg-zinc-700'
              }`}
              data-testid={`tab-${tab.id}`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Friend Challenges Section */}
      <div className="p-4">
        <FriendChallenges />
      </div>

      {/* Challenge List */}
      <div className="p-4 pt-0">
        <h3 className="text-white font-bold mb-4 flex items-center gap-2">
          <Trophy className="w-5 h-5 text-amber-400" />
          Global Challenges
        </h3>
        {filteredChallenges.length === 0 ? (
          <div className="text-center py-12">
            <Trophy className="w-12 h-12 text-zinc-700 mx-auto mb-4" />
            <h3 className="text-zinc-400 font-medium mb-2">
              {activeTab === 'my' ? 'No challenges joined yet' : 'No challenges available'}
            </h3>
            <p className="text-zinc-500 text-sm">
              {activeTab === 'my' 
                ? 'Join a challenge to start competing!' 
                : 'New challenges are created weekly and monthly.'}
            </p>
          </div>
        ) : (
          filteredChallenges.map(challenge => (
            <ChallengeCard
              key={challenge.id}
              challenge={challenge}
              onJoin={handleJoinChallenge}
              onLeave={handleLeaveChallenge}
              onViewLeaderboard={handleViewLeaderboard}
            />
          ))
        )}
      </div>

      {/* Leaderboard Modal */}
      {selectedChallenge && leaderboardData && (
        <ChallengeLeaderboardModal
          challenge={selectedChallenge}
          leaderboard={leaderboardData.leaderboard}
          userRank={leaderboardData.userRank}
          userScore={leaderboardData.userScore}
          onClose={closeLeaderboard}
        />
      )}
    </div>
  );
};

export default ChallengesScreen;
