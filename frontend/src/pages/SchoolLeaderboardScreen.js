import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { 
  ArrowLeft, 
  School, 
  Trophy, 
  TrendingUp, 
  Users,
  Medal,
  Flame
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export const SchoolLeaderboardScreen = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [leaderboardData, setLeaderboardData] = useState(null);
  const [mySchoolStats, setMySchoolStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('consistency');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [leaderboardRes, myStatsRes] = await Promise.all([
        axios.get(`${API}/schools/leaderboard`),
        axios.get(`${API}/schools/my-school-stats`)
      ]);
      setLeaderboardData(leaderboardRes.data);
      setMySchoolStats(myStatsRes.data);
    } catch (error) {
      console.error('Failed to fetch school leaderboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const getRankIcon = (rank) => {
    if (rank === 1) return <Medal className="w-5 h-5 text-yellow-500" />;
    if (rank === 2) return <Medal className="w-5 h-5 text-gray-400" />;
    if (rank === 3) return <Medal className="w-5 h-5 text-amber-600" />;
    return <span className="w-5 h-5 flex items-center justify-center text-zinc-500 font-mono text-sm">{rank}</span>;
  };

  const tabs = [
    { id: 'consistency', label: 'Consistency', icon: Flame },
    { id: 'performance', label: 'Performance', icon: TrendingUp },
    { id: 'most_users', label: 'Most Users', icon: Users },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-background">
        <div className="text-muted-foreground font-mono">Loading...</div>
      </div>
    );
  }

  const getActiveData = () => {
    if (!leaderboardData) return [];
    switch (activeTab) {
      case 'consistency':
        return leaderboardData.top_consistency || [];
      case 'performance':
        return leaderboardData.top_performance || [];
      case 'most_users':
        return leaderboardData.most_users || [];
      default:
        return [];
    }
  };

  const activeData = getActiveData();

  return (
    <div className="min-h-screen bg-background pb-24" data-testid="school-leaderboard-screen">
      <div className="p-6">
        {/* Header */}
        <div className="flex items-center gap-3 mb-6">
          <button 
            onClick={() => navigate(-1)}
            className="p-2 rounded-lg bg-card hover:bg-accent transition-colors"
            data-testid="back-btn"
          >
            <ArrowLeft className="w-5 h-5 text-muted-foreground" />
          </button>
          <div>
            <h1 className="text-2xl font-heading font-bold uppercase tracking-tight text-foreground">
              School Leaderboard
            </h1>
            <p className="text-muted-foreground font-body text-sm">
              Weekly rankings for US schools (Grades 8-12)
            </p>
          </div>
        </div>

        {/* My School Stats Card */}
        {mySchoolStats?.has_school ? (
          <div className="bg-primary/10 border border-primary/30 rounded-lg p-4 mb-6">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-10 h-10 bg-primary/20 rounded-full flex items-center justify-center">
                <School className="w-5 h-5 text-primary" />
              </div>
              <div>
                <div className="text-foreground font-heading font-bold">{mySchoolStats.school_name}</div>
                <div className="text-muted-foreground text-xs font-body">{mySchoolStats.total_users} Edge Mode users</div>
              </div>
            </div>
            <div className="grid grid-cols-3 gap-2 text-center">
              <div className="bg-background/50 rounded-md p-2">
                <div className="text-lg font-mono font-bold text-foreground">{mySchoolStats.avg_consistency}%</div>
                <div className="text-xs text-muted-foreground">Avg Consistency</div>
              </div>
              <div className="bg-background/50 rounded-md p-2">
                <div className="text-lg font-mono font-bold text-foreground">{mySchoolStats.avg_performance}</div>
                <div className="text-xs text-muted-foreground">Avg Performance</div>
              </div>
              <div className="bg-background/50 rounded-md p-2">
                <div className="text-lg font-mono font-bold text-foreground">{mySchoolStats.avg_streak}</div>
                <div className="text-xs text-muted-foreground">Avg Streak</div>
              </div>
            </div>
          </div>
        ) : (
          <div className="bg-card border border-border rounded-lg p-4 mb-6">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-muted rounded-full flex items-center justify-center">
                <School className="w-5 h-5 text-muted-foreground" />
              </div>
              <div>
                <div className="text-foreground font-body">Add your school to join the rankings!</div>
                <button 
                  onClick={() => navigate('/profile')}
                  className="text-primary text-sm font-body hover:underline"
                >
                  Go to Profile → Select School
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Tabs */}
        <div className="flex gap-2 mb-4 overflow-x-auto">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-full font-body text-sm whitespace-nowrap transition-colors ${
                activeTab === tab.id
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-card border border-border text-muted-foreground hover:bg-accent'
              }`}
              data-testid={`tab-${tab.id}`}
            >
              <tab.icon className="w-4 h-4" />
              {tab.label}
            </button>
          ))}
        </div>

        {/* Leaderboard Title */}
        <div className="flex items-center gap-2 mb-4">
          <Trophy className="w-5 h-5 text-yellow-500" />
          <h2 className="text-lg font-heading font-bold text-foreground">
            {activeTab === 'consistency' && 'Top Consistency Scores'}
            {activeTab === 'performance' && 'Top Performance Scores'}
            {activeTab === 'most_users' && 'Most Edge Mode Users'}
          </h2>
        </div>

        {/* Leaderboard List */}
        {activeData.length > 0 ? (
          <div className="space-y-2">
            {activeData.map((item, index) => (
              <div
                key={item.school_id || index}
                className={`bg-card border rounded-lg p-4 flex items-center justify-between ${
                  item.rank <= 3 ? 'border-yellow-500/30' : 'border-border'
                }`}
                data-testid={`school-rank-${item.rank}`}
              >
                <div className="flex items-center gap-3">
                  {getRankIcon(item.rank)}
                  <div>
                    <div className="text-foreground font-body font-medium">{item.school_name}</div>
                    <div className="text-muted-foreground text-xs font-body">
                      {item.user_count} {item.user_count === 1 ? 'user' : 'users'}
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  {activeTab === 'consistency' && (
                    <div className="text-xl font-mono font-bold text-primary">{item.avg_consistency}%</div>
                  )}
                  {activeTab === 'performance' && (
                    <div className="text-xl font-mono font-bold text-blue-500">{item.avg_performance}</div>
                  )}
                  {activeTab === 'most_users' && (
                    <div className="text-xl font-mono font-bold text-foreground">{item.user_count}</div>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="bg-card border border-border rounded-lg p-8 text-center">
            <School className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-foreground font-heading font-bold mb-2">No Schools Yet</h3>
            <p className="text-muted-foreground text-sm font-body">
              Be the first to add your school and start the leaderboard!
            </p>
          </div>
        )}

        {/* Footer Note */}
        <div className="mt-6 text-center">
          <p className="text-muted-foreground text-xs font-body">
            Rankings update weekly • Only schools with active users shown
          </p>
          {leaderboardData?.last_updated && (
            <p className="text-muted-foreground/50 text-xs font-body mt-1">
              Last updated: {new Date(leaderboardData.last_updated).toLocaleDateString()}
            </p>
          )}
        </div>
      </div>
    </div>
  );
};
