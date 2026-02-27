import React from 'react';
import { Zap } from 'lucide-react';

export const getPerformanceRating = (performanceIndex) => {
  if (performanceIndex >= 90) return { rating: 'Elite', color: 'text-purple-400', bgColor: 'bg-purple-400/20', description: 'Top-tier execution. You\'re operating at peak level.' };
  if (performanceIndex >= 75) return { rating: 'High Performer', color: 'text-primary', bgColor: 'bg-primary/20', description: 'Crushing your targets consistently.' };
  if (performanceIndex >= 60) return { rating: 'On Track', color: 'text-blue-400', bgColor: 'bg-blue-400/20', description: 'Solid progress. Keep pushing.' };
  if (performanceIndex >= 40) return { rating: 'Building', color: 'text-yellow-400', bgColor: 'bg-yellow-400/20', description: 'Foundation in place. Room to grow.' };
  return { rating: 'Getting Started', color: 'text-zinc-400', bgColor: 'bg-zinc-400/20', description: 'Every journey starts here. Stay committed.' };
};

export const PerformanceRatingBadge = ({ performanceIndex }) => {
  const { rating, color, bgColor } = getPerformanceRating(performanceIndex);
  
  return (
    <div className="flex items-center gap-2">
      <span className="text-zinc-500 text-xs font-body">Rating:</span>
      <div className={`px-2 py-1 rounded ${bgColor} flex items-center gap-1`}>
        <Zap className={`w-3 h-3 ${color}`} />
        <span className={`text-xs font-body font-bold ${color}`}>{rating}</span>
      </div>
    </div>
  );
};

export const PerformanceRatingScale = () => {
  return (
    <div className="bg-zinc-950 border border-zinc-800 rounded-md p-6">
      <h3 className="text-lg font-heading font-bold uppercase tracking-tight text-white mb-4">
        Performance Ratings
      </h3>
      <p className="text-zinc-500 text-sm font-body mb-4">
        Based on consistency + target completion
      </p>
      <div className="space-y-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Zap className="w-4 h-4 text-purple-400" />
            <span className="text-purple-400 font-body font-bold">Elite</span>
            <span className="text-zinc-500 text-sm font-mono">(90-100)</span>
          </div>
          <p className="text-zinc-400 text-sm font-body ml-6">Top-tier execution. You're operating at peak level.</p>
        </div>
        
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Zap className="w-4 h-4 text-primary" />
            <span className="text-primary font-body font-bold">High Performer</span>
            <span className="text-zinc-500 text-sm font-mono">(75-89)</span>
          </div>
          <p className="text-zinc-400 text-sm font-body ml-6">Crushing your targets consistently.</p>
        </div>
        
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Zap className="w-4 h-4 text-blue-400" />
            <span className="text-blue-400 font-body font-bold">On Track</span>
            <span className="text-zinc-500 text-sm font-mono">(60-74)</span>
          </div>
          <p className="text-zinc-400 text-sm font-body ml-6">Solid progress. Keep pushing.</p>
        </div>
        
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Zap className="w-4 h-4 text-yellow-400" />
            <span className="text-yellow-400 font-body font-bold">Building</span>
            <span className="text-zinc-500 text-sm font-mono">(40-59)</span>
          </div>
          <p className="text-zinc-400 text-sm font-body ml-6">Foundation in place. Room to grow.</p>
        </div>
        
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Zap className="w-4 h-4 text-zinc-400" />
            <span className="text-zinc-400 font-body font-bold">Getting Started</span>
            <span className="text-zinc-500 text-sm font-mono">(Below 40)</span>
          </div>
          <p className="text-zinc-400 text-sm font-body ml-6">Every journey starts here. Stay committed.</p>
        </div>
      </div>
    </div>
  );
};
