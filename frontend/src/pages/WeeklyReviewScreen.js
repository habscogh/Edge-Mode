import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { TrendingUp, TrendingDown, Award, Calendar } from 'lucide-react';
import { format, parseISO } from 'date-fns';
import { ConsistencyRatingBadge, ConsistencyRatingScale } from '../components/ConsistencyRating';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export const WeeklyReviewScreen = () => {
  const [review, setReview] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchReview();
  }, []);

  const fetchReview = async () => {
    try {
      const response = await axios.get(`${API}/stats/weekly-review`);
      setReview(response.data);
    } catch (error) {
      console.error('Failed to fetch review:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-[#09090b]">
        <div className="text-zinc-400 font-mono">Loading...</div>
      </div>
    );
  }

  if (!review) return null;

  return (
    <div className="min-h-screen bg-[#09090b] p-4 pb-24">
      <div className="max-w-2xl mx-auto pt-6">
        <div className="flex items-center gap-3 mb-6">
          <Award className="w-8 h-8 text-primary" />
          <div>
            <h1 className="text-3xl font-heading font-bold uppercase tracking-tight text-white">
              Weekly Review
            </h1>
            <p className="text-zinc-400 text-sm font-body">
              {format(parseISO(review.week_start), 'MMM d')} - {format(parseISO(review.week_end), 'MMM d')}
            </p>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-3 mb-6">
          <div className="bg-zinc-950 border border-zinc-800 rounded-md p-4">
            <div className="text-zinc-400 text-xs font-body uppercase tracking-wide mb-1">Performance</div>
            <div className="text-2xl font-mono font-bold text-primary">{review.performance_index}%</div>
          </div>
          <div className="bg-zinc-950 border border-zinc-800 rounded-md p-4">
            <div className="text-zinc-400 text-xs font-body uppercase tracking-wide mb-1">Sessions</div>
            <div className="text-2xl font-mono font-bold text-white">{review.total_sessions}</div>
          </div>
          <div className="bg-zinc-950 border border-zinc-800 rounded-md p-4">
            <div className="text-zinc-400 text-xs font-body uppercase tracking-wide mb-1">Consistency</div>
            <div className="text-2xl font-mono font-bold text-white">{review.consistency_pct}%</div>
            <ConsistencyRatingBadge consistencyPct={review.consistency_pct} />
          </div>
        </div>

        <div className="bg-zinc-950 border border-zinc-800 rounded-md p-6 mb-6">
          <h2 className="text-lg font-heading font-bold uppercase tracking-tight text-white mb-4">
            Daily Output Change
          </h2>
          <div className="flex items-center gap-3">
            {review.average_daily_output_change >= 0 ? (
              <TrendingUp className="w-8 h-8 text-primary" />
            ) : (
              <TrendingDown className="w-8 h-8 text-red-500" />
            )}
            <div>
              <div className={`text-3xl font-mono font-bold ${
                review.average_daily_output_change >= 0 ? 'text-primary' : 'text-red-500'
              }`}>
                {review.average_daily_output_change > 0 ? '+' : ''}{review.average_daily_output_change}%
              </div>
              <div className="text-zinc-400 text-sm font-body">vs last week</div>
            </div>
          </div>
        </div>

        {review.improved_pillars.length > 0 && (
          <div className="bg-primary/10 border border-primary/30 rounded-md p-6 mb-6">
            <div className="flex items-center gap-2 mb-4">
              <TrendingUp className="w-5 h-5 text-primary" />
              <h3 className="text-lg font-heading font-bold uppercase tracking-tight text-primary">
                You Improved
              </h3>
            </div>
            <div className="space-y-3">
              {review.improved_pillars.map((pillar, idx) => (
                <div key={idx} className="flex justify-between items-center">
                  <span className="text-white font-body">{pillar.pillar_name}</span>
                  <div className="flex items-center gap-2">
                    <span className="text-primary font-mono font-bold">+{pillar.change} sessions</span>
                    <span className="text-zinc-500 text-sm font-mono">({pillar.current_sessions} this week)</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {review.dropped_pillars.length > 0 && (
          <div className="bg-red-500/10 border border-red-500/30 rounded-md p-6 mb-6">
            <div className="flex items-center gap-2 mb-4">
              <TrendingDown className="w-5 h-5 text-red-500" />
              <h3 className="text-lg font-heading font-bold uppercase tracking-tight text-red-500">
                Dropped Areas
              </h3>
            </div>
            <div className="space-y-3">
              {review.dropped_pillars.map((pillar, idx) => (
                <div key={idx} className="flex justify-between items-center">
                  <span className="text-white font-body">{pillar.pillar_name}</span>
                  <div className="flex items-center gap-2">
                    <span className="text-red-500 font-mono font-bold">-{pillar.change} sessions</span>
                    <span className="text-zinc-500 text-sm font-mono">({pillar.current_sessions} this week)</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {review.improved_pillars.length === 0 && review.dropped_pillars.length === 0 && (
          <div className="bg-zinc-950 border border-zinc-800 rounded-md p-6 text-center">
            <Calendar className="w-12 h-12 text-zinc-600 mx-auto mb-3" />
            <p className="text-zinc-400 font-body">No changes from last week</p>
          </div>
        )}
      </div>
    </div>
  );
};