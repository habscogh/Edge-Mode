import React from 'react';
import { ArrowRight } from 'lucide-react';

export const getConsistencyRating = (consistencyPct) => {
  if (consistencyPct >= 90) return { rating: 'Excellent', color: 'text-primary', bgColor: 'bg-primary/20' };
  if (consistencyPct >= 75) return { rating: 'Strong', color: 'text-blue-400', bgColor: 'bg-blue-400/20' };
  if (consistencyPct >= 60) return { rating: 'Developing', color: 'text-yellow-400', bgColor: 'bg-yellow-400/20' };
  return { rating: 'Inconsistent', color: 'text-red-400', bgColor: 'bg-red-400/20' };
};

export const ConsistencyRatingBadge = ({ consistencyPct }) => {
  const { rating, color, bgColor } = getConsistencyRating(consistencyPct);
  
  return (
    <div className="flex items-center gap-2">
      <span className="text-zinc-500 text-xs font-body">Rating:</span>
      <div className={`px-2 py-1 rounded ${bgColor} flex items-center gap-1`}>
        <ArrowRight className={`w-3 h-3 ${color}`} />
        <span className={`text-xs font-body font-bold ${color}`}>{rating}</span>
      </div>
    </div>
  );
};

export const ConsistencyRatingScale = () => {
  return (
    <div className="bg-zinc-950 border border-zinc-800 rounded-md p-6">
      <h3 className="text-lg font-heading font-bold uppercase tracking-tight text-white mb-4">
        Consistency Ratings
      </h3>
      <div className="space-y-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <ArrowRight className="w-4 h-4 text-primary" />
            <span className="text-primary font-body font-bold">Excellent</span>
            <span className="text-zinc-500 text-sm font-mono">(90-100%)</span>
          </div>
          <p className="text-zinc-400 text-sm font-body ml-6">You showed up nearly every day.</p>
        </div>
        
        <div>
          <div className="flex items-center gap-2 mb-1">
            <ArrowRight className="w-4 h-4 text-blue-400" />
            <span className="text-blue-400 font-body font-bold">Strong</span>
            <span className="text-zinc-500 text-sm font-mono">(75-89%)</span>
          </div>
          <p className="text-zinc-400 text-sm font-body ml-6">You were consistent most of the week.</p>
        </div>
        
        <div>
          <div className="flex items-center gap-2 mb-1">
            <ArrowRight className="w-4 h-4 text-yellow-400" />
            <span className="text-yellow-400 font-body font-bold">Developing</span>
            <span className="text-zinc-500 text-sm font-mono">(60-74%)</span>
          </div>
          <p className="text-zinc-400 text-sm font-body ml-6">You showed up more than half the time.</p>
        </div>
        
        <div>
          <div className="flex items-center gap-2 mb-1">
            <ArrowRight className="w-4 h-4 text-red-400" />
            <span className="text-red-400 font-body font-bold">Inconsistent</span>
            <span className="text-zinc-500 text-sm font-mono">(Below 60%)</span>
          </div>
          <p className="text-zinc-400 text-sm font-body ml-6">You missed more days than you executed.</p>
        </div>
      </div>
    </div>
  );
};