import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'sonner';
import { Button } from './ui/button';
import {
  Target,
  Clock,
  Gift,
  CheckCircle,
  ChevronRight,
  Coins,
  Zap,
  Calendar,
  Trophy,
  Flame
} from 'lucide-react';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

// Quest Card Component
const QuestCard = ({ quest, onClaim }) => {
  const [claiming, setClaiming] = useState(false);
  const isComplete = quest.is_completed;
  const isClaimed = quest.is_claimed;
  const canClaim = isComplete && !isClaimed;

  const handleClaim = async () => {
    setClaiming(true);
    try {
      const response = await axios.post(`${API}/quests/claim/${quest.id}`);
      toast.success(response.data.message);
      onClaim();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to claim reward');
    } finally {
      setClaiming(false);
    }
  };

  return (
    <div 
      className={`p-3 rounded-lg border transition-all ${
        isClaimed 
          ? 'bg-zinc-900/50 border-zinc-800 opacity-60' 
          : isComplete 
            ? 'bg-green-900/20 border-green-500/50 ring-1 ring-green-500/30' 
            : 'bg-zinc-900 border-zinc-800'
      }`}
      data-testid={`quest-${quest.id}`}
    >
      <div className="flex items-start gap-3">
        {/* Icon */}
        <div className={`text-2xl ${isClaimed ? 'grayscale' : ''}`}>
          {quest.icon}
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <h4 className="text-white font-medium text-sm truncate">{quest.name}</h4>
            <span 
              className="text-xs px-1.5 py-0.5 rounded-full"
              style={{ 
                backgroundColor: `${quest.difficulty_color}20`,
                color: quest.difficulty_color 
              }}
            >
              {quest.difficulty}
            </span>
          </div>
          <p className="text-zinc-500 text-xs mb-2">{quest.description}</p>

          {/* Progress bar */}
          <div className="h-1.5 bg-zinc-800 rounded-full overflow-hidden mb-2">
            <div 
              className={`h-full transition-all duration-500 ${
                isClaimed ? 'bg-zinc-600' : isComplete ? 'bg-green-500' : 'bg-primary'
              }`}
              style={{ width: `${quest.progress_pct}%` }}
            />
          </div>

          {/* Progress text and rewards */}
          <div className="flex items-center justify-between">
            <span className="text-xs text-zinc-500">
              {isClaimed ? (
                <span className="text-zinc-400 flex items-center gap-1">
                  <CheckCircle className="w-3 h-3" /> Claimed
                </span>
              ) : (
                `${quest.current}/${quest.target}`
              )}
            </span>
            
            <div className="flex items-center gap-2">
              {quest.reward_coins > 0 && (
                <span className="flex items-center gap-0.5 text-yellow-400 text-xs">
                  <Coins className="w-3 h-3" />
                  {quest.reward_coins}
                </span>
              )}
              {quest.reward_xp > 0 && (
                <span className="flex items-center gap-0.5 text-purple-400 text-xs">
                  <Zap className="w-3 h-3" />
                  {quest.reward_xp}
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Claim button */}
        {canClaim && (
          <Button
            onClick={handleClaim}
            disabled={claiming}
            size="sm"
            className="bg-green-600 hover:bg-green-700 text-white shrink-0"
            data-testid={`claim-${quest.id}`}
          >
            <Gift className="w-4 h-4" />
          </Button>
        )}
      </div>
    </div>
  );
};

// Quests Section Component (for Dashboard)
const QuestsSection = ({ compact = false }) => {
  const [dailyQuests, setDailyQuests] = useState([]);
  const [weeklyQuests, setWeeklyQuests] = useState([]);
  const [dailySummary, setDailySummary] = useState({});
  const [weeklySummary, setWeeklySummary] = useState({});
  const [activeTab, setActiveTab] = useState('daily');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchQuests();
  }, []);

  const fetchQuests = async () => {
    try {
      const response = await axios.get(`${API}/quests/all`);
      setDailyQuests(response.data.daily.quests);
      setWeeklyQuests(response.data.weekly.quests);
      setDailySummary(response.data.daily.summary);
      setWeeklySummary(response.data.weekly.summary);
    } catch (error) {
      console.error('Failed to fetch quests:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleClaimAll = async (type) => {
    try {
      const response = await axios.post(`${API}/quests/claim-all/${type}`);
      toast.success(response.data.message);
      fetchQuests();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to claim rewards');
    }
  };

  const currentQuests = activeTab === 'daily' ? dailyQuests : weeklyQuests;
  const currentSummary = activeTab === 'daily' ? dailySummary : weeklySummary;

  if (loading) {
    return (
      <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-4 animate-pulse">
        <div className="h-4 bg-zinc-800 rounded w-1/3 mb-3"></div>
        <div className="h-16 bg-zinc-800 rounded"></div>
      </div>
    );
  }

  // Calculate total available rewards
  const totalRewards = dailySummary.available_rewards + weeklySummary.available_rewards;

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg overflow-hidden" data-testid="quests-section">
      {/* Header */}
      <div className="p-4 border-b border-zinc-800">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <Target className="w-5 h-5 text-primary" />
            <h3 className="text-white font-bold">Quests</h3>
            {totalRewards > 0 && (
              <span className="bg-green-500/20 text-green-400 text-xs px-2 py-0.5 rounded-full flex items-center gap-1">
                <Gift className="w-3 h-3" /> {totalRewards} coins
              </span>
            )}
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-2">
          <button
            onClick={() => setActiveTab('daily')}
            className={`flex-1 py-2 px-3 rounded-lg text-sm font-medium transition-colors flex items-center justify-center gap-2 ${
              activeTab === 'daily' 
                ? 'bg-primary text-black' 
                : 'bg-zinc-800 text-zinc-400 hover:text-white'
            }`}
            data-testid="daily-tab"
          >
            <Clock className="w-4 h-4" />
            Daily
            <span className={`text-xs px-1.5 py-0.5 rounded-full ${
              activeTab === 'daily' ? 'bg-black/20' : 'bg-zinc-700'
            }`}>
              {dailySummary.completed}/{dailySummary.total}
            </span>
          </button>
          <button
            onClick={() => setActiveTab('weekly')}
            className={`flex-1 py-2 px-3 rounded-lg text-sm font-medium transition-colors flex items-center justify-center gap-2 ${
              activeTab === 'weekly' 
                ? 'bg-primary text-black' 
                : 'bg-zinc-800 text-zinc-400 hover:text-white'
            }`}
            data-testid="weekly-tab"
          >
            <Calendar className="w-4 h-4" />
            Weekly
            <span className={`text-xs px-1.5 py-0.5 rounded-full ${
              activeTab === 'weekly' ? 'bg-black/20' : 'bg-zinc-700'
            }`}>
              {weeklySummary.completed}/{weeklySummary.total}
            </span>
          </button>
        </div>
      </div>

      {/* Quest List */}
      <div className={`p-4 space-y-2 ${compact ? 'max-h-64 overflow-y-auto' : ''}`}>
        {currentQuests.slice(0, compact ? 3 : undefined).map(quest => (
          <QuestCard 
            key={quest.id} 
            quest={quest} 
            onClaim={fetchQuests}
          />
        ))}

        {compact && currentQuests.length > 3 && (
          <p className="text-center text-zinc-500 text-xs py-2">
            +{currentQuests.length - 3} more quests
          </p>
        )}
      </div>

      {/* Claim All Button */}
      {currentSummary.available_rewards > 0 && (
        <div className="p-4 pt-0">
          <Button
            onClick={() => handleClaimAll(activeTab)}
            className="w-full bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white"
            data-testid="claim-all-btn"
          >
            <Gift className="w-4 h-4 mr-2" />
            Claim All ({currentSummary.available_rewards} coins)
          </Button>
        </div>
      )}
    </div>
  );
};

// Mini Quests Widget (for sidebar or compact view)
const QuestsWidget = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const response = await axios.get(`${API}/quests/all`);
      setData(response.data);
    } catch (error) {
      console.error('Failed to fetch quests:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading || !data) return null;

  const totalCompleted = data.daily.summary.completed + data.weekly.summary.completed;
  const totalQuests = data.daily.summary.total + data.weekly.summary.total;
  const totalRewards = data.total_available_rewards;

  return (
    <div 
      className="bg-zinc-900 border border-zinc-800 rounded-lg p-3 cursor-pointer hover:border-zinc-700 transition-colors"
      data-testid="quests-widget"
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Target className="w-4 h-4 text-primary" />
          <span className="text-white text-sm font-medium">Quests</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-zinc-400 text-sm">{totalCompleted}/{totalQuests}</span>
          {totalRewards > 0 && (
            <span className="bg-green-500/20 text-green-400 text-xs px-2 py-0.5 rounded-full">
              +{totalRewards}
            </span>
          )}
          <ChevronRight className="w-4 h-4 text-zinc-500" />
        </div>
      </div>
    </div>
  );
};

export { QuestsSection, QuestsWidget, QuestCard };
export default QuestsSection;
