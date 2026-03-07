import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { ArrowLeft, BookOpen, Flame, TrendingUp, Calendar, ChevronDown } from 'lucide-react';
import { Button } from '../components/ui/button';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const MOOD_EMOJI = {
  great: '🔥',
  good: '😊',
  okay: '😐',
  tough: '💪'
};

export const JournalScreen = () => {
  const navigate = useNavigate();
  const [reflections, setReflections] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [hasMore, setHasMore] = useState(false);
  const [offset, setOffset] = useState(0);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [reflectionsRes, statsRes] = await Promise.all([
        axios.get(`${API}/reflections?limit=20&offset=0`),
        axios.get(`${API}/reflections/stats`)
      ]);
      setReflections(reflectionsRes.data.reflections);
      setHasMore(reflectionsRes.data.has_more);
      setStats(statsRes.data);
      setOffset(20);
    } catch (error) {
      console.error('Failed to fetch journal data:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadMore = async () => {
    setLoadingMore(true);
    try {
      const res = await axios.get(`${API}/reflections?limit=20&offset=${offset}`);
      setReflections([...reflections, ...res.data.reflections]);
      setHasMore(res.data.has_more);
      setOffset(offset + 20);
    } catch (error) {
      console.error('Failed to load more:', error);
    } finally {
      setLoadingMore(false);
    }
  };

  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);
    
    if (date.toDateString() === today.toDateString()) {
      return 'Today';
    } else if (date.toDateString() === yesterday.toDateString()) {
      return 'Yesterday';
    } else {
      return date.toLocaleDateString('en-US', { 
        weekday: 'short',
        month: 'short', 
        day: 'numeric' 
      });
    }
  };

  // Group reflections by date
  const groupedReflections = reflections.reduce((groups, reflection) => {
    const date = reflection.date;
    if (!groups[date]) {
      groups[date] = [];
    }
    groups[date].push(reflection);
    return groups;
  }, {});

  if (loading) {
    return (
      <div className="min-h-screen bg-[#09090b] flex items-center justify-center">
        <div className="text-zinc-400 font-mono">Loading journal...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#09090b] pb-24">
      {/* Header */}
      <div className="bg-zinc-950 border-b border-zinc-800 p-4 sticky top-0 z-10">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate(-1)}
            className="text-zinc-400 hover:text-white transition-colors"
          >
            <ArrowLeft className="w-6 h-6" />
          </button>
          <div className="flex items-center gap-2">
            <BookOpen className="w-6 h-6 text-primary" />
            <h1 className="text-xl font-heading font-bold uppercase tracking-tight text-white">
              Growth Journal
            </h1>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="p-4 grid grid-cols-3 gap-3">
          <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-3 text-center">
            <div className="text-2xl font-bold text-primary font-mono">
              {stats.total_reflections}
            </div>
            <div className="text-xs text-zinc-400">Total</div>
          </div>
          <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-3 text-center">
            <div className="flex items-center justify-center gap-1">
              <Flame className="w-5 h-5 text-orange-500" />
              <span className="text-2xl font-bold text-orange-500 font-mono">
                {stats.current_streak}
              </span>
            </div>
            <div className="text-xs text-zinc-400">Streak</div>
          </div>
          <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-3 text-center">
            <div className="flex items-center justify-center gap-1">
              <TrendingUp className="w-5 h-5 text-emerald-500" />
              <span className="text-2xl font-bold text-emerald-500 font-mono">
                {stats.longest_streak}
              </span>
            </div>
            <div className="text-xs text-zinc-400">Best</div>
          </div>
        </div>
      )}

      {/* Mood Distribution */}
      {stats && stats.mood_distribution && Object.keys(stats.mood_distribution).length > 0 && (
        <div className="px-4 pb-4">
          <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-3">
            <p className="text-xs text-zinc-400 mb-2">Mood Distribution</p>
            <div className="flex gap-4">
              {Object.entries(stats.mood_distribution).map(([mood, count]) => (
                <div key={mood} className="flex items-center gap-1">
                  <span className="text-lg">{MOOD_EMOJI[mood]}</span>
                  <span className="text-sm text-zinc-300 font-mono">{count}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Reflections List */}
      <div className="px-4 space-y-4">
        {Object.keys(groupedReflections).length === 0 ? (
          <div className="text-center py-12">
            <BookOpen className="w-16 h-16 text-zinc-700 mx-auto mb-4" />
            <h3 className="text-xl font-heading font-bold text-white mb-2">
              Your Journal is Empty
            </h3>
            <p className="text-zinc-400 text-sm mb-6">
              Start reflecting after your sessions to build your growth journal.
            </p>
            <Button
              onClick={() => navigate('/log')}
              className="bg-primary text-primary-foreground"
            >
              Log a Session
            </Button>
          </div>
        ) : (
          <>
            {Object.entries(groupedReflections).map(([date, dayReflections]) => (
              <div key={date}>
                {/* Date Header */}
                <div className="flex items-center gap-2 mb-2">
                  <Calendar className="w-4 h-4 text-zinc-500" />
                  <span className="text-sm font-medium text-zinc-400">
                    {formatDate(date)}
                  </span>
                </div>
                
                {/* Day's Reflections */}
                <div className="space-y-3">
                  {dayReflections.map((reflection) => (
                    <div
                      key={reflection.id}
                      className="bg-zinc-900 border border-zinc-800 rounded-lg p-4"
                    >
                      {/* Prompt */}
                      <p className="text-primary text-sm font-medium mb-2">
                        "{reflection.prompt}"
                      </p>
                      
                      {/* Response */}
                      <p className="text-white text-sm leading-relaxed">
                        {reflection.response}
                      </p>
                      
                      {/* Mood & Time */}
                      <div className="flex items-center justify-between mt-3 pt-3 border-t border-zinc-800">
                        {reflection.mood && (
                          <span className="text-lg" title={reflection.mood}>
                            {MOOD_EMOJI[reflection.mood]}
                          </span>
                        )}
                        <span className="text-xs text-zinc-500">
                          {new Date(reflection.created_at).toLocaleTimeString('en-US', {
                            hour: 'numeric',
                            minute: '2-digit'
                          })}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}

            {/* Load More */}
            {hasMore && (
              <div className="text-center py-4">
                <Button
                  variant="ghost"
                  onClick={loadMore}
                  disabled={loadingMore}
                  className="text-zinc-400"
                >
                  {loadingMore ? (
                    'Loading...'
                  ) : (
                    <>
                      <ChevronDown className="w-4 h-4 mr-2" />
                      Load More
                    </>
                  )}
                </Button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};
