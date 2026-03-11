import React, { useState, useEffect } from 'react';
import { Users, Flame, Trophy, Clock, Quote } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

export const SocialProofSection = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPlatformStats();
  }, []);

  const fetchPlatformStats = async () => {
    try {
      const res = await fetch(`${BACKEND_URL}/api/platform-stats`);
      const json = await res.json();
      setData(json);
    } catch (err) {
      console.error('Failed to fetch platform stats:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return null;
  if (!data?.enabled) return null;

  const { stats, testimonials } = data;

  const formatNumber = (num) => {
    if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K+';
    }
    return num?.toLocaleString() || '0';
  };

  const statItems = [
    { icon: Users, label: 'Active Users', value: formatNumber(stats.total_users), color: 'text-blue-400' },
    { icon: Flame, label: 'Sessions Logged', value: formatNumber(stats.sessions_logged), color: 'text-orange-400' },
    { icon: Trophy, label: 'Badges Earned', value: formatNumber(stats.badges_earned), color: 'text-yellow-400' },
    { icon: Clock, label: 'Hours Tracked', value: formatNumber(stats.hours_logged), color: 'text-green-400' }
  ];

  return (
    <div className="bg-zinc-950 border border-zinc-800 rounded-md p-8 mb-8" data-testid="social-proof-section">
      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        {statItems.map((item, index) => (
          <div 
            key={index} 
            className="text-center p-4 bg-zinc-900/50 rounded-lg border border-zinc-800/50"
            data-testid={`stat-${item.label.toLowerCase().replace(' ', '-')}`}
          >
            <item.icon className={`w-6 h-6 ${item.color} mx-auto mb-2`} />
            <div className="text-2xl font-mono font-bold text-white">{item.value}</div>
            <div className="text-xs text-zinc-500 uppercase tracking-wide">{item.label}</div>
          </div>
        ))}
      </div>

      {/* Testimonials */}
      {testimonials && testimonials.length > 0 && (
        <div className="space-y-4">
          <h4 className="text-sm font-heading text-zinc-400 uppercase tracking-wide text-center mb-4">
            What Users Are Saying
          </h4>
          <div className="grid md:grid-cols-2 gap-4">
            {testimonials.slice(0, 4).map((testimonial, index) => (
              <div 
                key={testimonial.id || index}
                className="bg-zinc-900/30 border border-zinc-800/50 rounded-lg p-4"
                data-testid={`testimonial-${index}`}
              >
                <Quote className="w-5 h-5 text-primary/50 mb-2" />
                <p className="text-zinc-300 text-sm font-body italic mb-3">
                  "{testimonial.quote}"
                </p>
                <div className="flex items-center gap-3">
                  {testimonial.avatar_url ? (
                    <img 
                      src={testimonial.avatar_url} 
                      alt={testimonial.name}
                      className="w-8 h-8 rounded-full object-cover"
                    />
                  ) : (
                    <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center">
                      <span className="text-primary text-xs font-bold">
                        {testimonial.name?.charAt(0)?.toUpperCase() || '?'}
                      </span>
                    </div>
                  )}
                  <div>
                    <p className="text-white text-sm font-medium">{testimonial.name}</p>
                    <p className="text-zinc-500 text-xs">{testimonial.role}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* If no testimonials, show a simpler message */}
      {(!testimonials || testimonials.length === 0) && (
        <p className="text-center text-zinc-500 text-sm font-body">
          Join thousands of students building better habits every day
        </p>
      )}
    </div>
  );
};
