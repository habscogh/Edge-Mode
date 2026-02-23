import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Trophy, Filter } from 'lucide-react';
import { Button } from '../components/ui/button';
import { useAuth } from '../context/AuthContext';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export const LeaderboardScreen = () => {
  const { user } = useAuth();
  const [leaderboard, setLeaderboard] = useState([]);
  const [ageFilter, setAgeFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [optedIn, setOptedIn] = useState(null); // Changed to null to distinguish between unloaded and false

  useEffect(() => {
    if (user) {
      setOptedIn(user.leaderboard_opt_in);
      // Only fetch leaderboard if user has opted in
      if (user.leaderboard_opt_in) {
        fetchLeaderboard();
      } else {
        setLoading(false);
      }
    }
  }, [user]);

  const fetchLeaderboard = async (filter = '') => {
    try {
      const params = filter ? `?age_group=${filter}` : '';
      const response = await axios.get(`${API}/leaderboard/global${params}`);
      setLeaderboard(response.data);
    } catch (error) {
      console.error('Failed to fetch leaderboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleOptIn = async () => {
    try {
      const response = await axios.post(`${API}/users/leaderboard-opt-in`);
      setOptedIn(response.data.leaderboard_opt_in);
      if (response.data.leaderboard_opt_in) {
        fetchLeaderboard(ageFilter);
      }
    } catch (error) {
      console.error('Failed to toggle opt-in:', error);
    }
  };

  const handleFilterChange = (filter) => {
    setAgeFilter(filter);
    fetchLeaderboard(filter);
  };

  if (!optedIn && optedIn !== null) {
    return (
      <div className="min-h-screen bg-[#09090b] p-4 pb-24 flex items-center justify-center">
        <div className="text-center max-w-md">
          <Trophy className="w-16 h-16 text-zinc-700 mx-auto mb-4" />
          <h2 className="text-2xl font-heading font-bold uppercase text-white mb-3">
            Join Global Leaderboard
          </h2>
          <p className="text-zinc-400 font-body mb-6">
            Compete anonymously with teens worldwide. Your username will be visible, but no personal data is shared.
          </p>
          <Button
            data-testid="opt-in-leaderboard-btn"
            onClick={handleOptIn}
            className="bg-primary text-primary-foreground hover:bg-primary/90 font-heading uppercase tracking-wide font-bold"
          >
            Opt In
          </Button>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-[#09090b]">
        <div className="text-zinc-400 font-mono">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#09090b] p-4 pb-24">
      <div className="max-w-2xl mx-auto pt-6">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-3xl font-heading font-bold uppercase tracking-tight text-white">
            Most Improved
          </h1>
          <Trophy className="w-8 h-8 text-primary" />
        </div>

        <p className="text-zinc-400 text-sm font-body mb-6">This week's top improvers</p>

        <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
          <button
            data-testid="filter-all-btn"
            onClick={() => handleFilterChange('')}
            className={`px-4 py-2 rounded-md font-body whitespace-nowrap transition-all duration-200 ${
              ageFilter === ''
                ? 'bg-primary text-primary-foreground'
                : 'bg-zinc-900 text-zinc-400 hover:bg-zinc-800'
            }`}
          >
            All Ages
          </button>
          <button
            data-testid="filter-12-14-btn"
            onClick={() => handleFilterChange('12-14')}
            className={`px-4 py-2 rounded-md font-body whitespace-nowrap transition-all duration-200 ${
              ageFilter === '12-14'
                ? 'bg-primary text-primary-foreground'
                : 'bg-zinc-900 text-zinc-400 hover:bg-zinc-800'
            }`}
          >
            12-14
          </button>
          <button
            data-testid="filter-15-17-btn"
            onClick={() => handleFilterChange('15-17')}
            className={`px-4 py-2 rounded-md font-body whitespace-nowrap transition-all duration-200 ${
              ageFilter === '15-17'
                ? 'bg-primary text-primary-foreground'
                : 'bg-zinc-900 text-zinc-400 hover:bg-zinc-800'
            }`}
          >
            15-17
          </button>
          <button
            data-testid="filter-18-19-btn"
            onClick={() => handleFilterChange('18-19')}
            className={`px-4 py-2 rounded-md font-body whitespace-nowrap transition-all duration-200 ${
              ageFilter === '18-19'
                ? 'bg-primary text-primary-foreground'
                : 'bg-zinc-900 text-zinc-400 hover:bg-zinc-800'
            }`}
          >
            18-19
          </button>
        </div>

        <div className="bg-zinc-950 border border-zinc-800 rounded-md mb-4">
          <div className="p-4 border-b border-zinc-800">
            <p className="text-zinc-400 text-sm font-body">Top 100 - Ranked by improvement % (resets weekly)</p>
          </div>

          <div className="divide-y divide-zinc-800">
            {leaderboard.length === 0 ? (
              <div className="p-8 text-center text-zinc-500 font-body">No participants yet this week</div>
            ) : (
              leaderboard.map((entry, idx) => (
                <div
                  key={idx}
                  data-testid={`global-leaderboard-entry-${idx}`}
                  className={`p-4 hover:bg-zinc-900/50 transition-colors ${
                    entry.username === user?.username ? 'bg-primary/10 border-l-4 border-l-primary' : ''
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center font-mono font-bold ${
                        idx === 0 ? 'bg-yellow-500/20 text-yellow-500' :
                        idx === 1 ? 'bg-zinc-400/20 text-zinc-400' :
                        idx === 2 ? 'bg-orange-500/20 text-orange-500' :
                        'bg-zinc-800 text-zinc-400'
                      }`}>
                        {idx + 1}
                      </div>
                      <div>
                        <div className="text-white font-body">{entry.username}</div>
                        <div className="text-zinc-500 text-xs font-body">{entry.age_group}</div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-primary font-mono font-bold text-lg">+{entry.improvement_pct}%</div>
                      <div className="text-zinc-500 text-xs font-body">{entry.performance_index}% score</div>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        <Button
          data-testid="opt-out-leaderboard-btn"
          onClick={handleOptIn}
          variant="ghost"
          className="w-full text-zinc-500 hover:text-zinc-300 font-body text-sm"
        >
          Leave Leaderboard
        </Button>
      </div>
    </div>
  );
};