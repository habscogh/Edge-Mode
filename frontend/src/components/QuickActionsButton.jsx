import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, X, Zap, Calendar, Trophy, TrendingUp, Users, Swords } from 'lucide-react';

export const QuickActionsButton = () => {
  const [isOpen, setIsOpen] = useState(false);
  const navigate = useNavigate();

  const actions = [
    { icon: Zap, label: 'Log Session', path: '/log', color: 'bg-primary' },
    { icon: Swords, label: 'Challenges', path: '/challenges', color: 'bg-orange-500' },
    { icon: Calendar, label: 'History', path: '/history', color: 'bg-blue-500' },
    { icon: Trophy, label: 'Achievements', path: '/achievements', color: 'bg-yellow-500' },
    { icon: TrendingUp, label: 'Weekly Review', path: '/review', color: 'bg-purple-500' },
    { icon: Users, label: 'Groups', path: '/groups', color: 'bg-pink-500' },
  ];

  const handleAction = (path) => {
    setIsOpen(false);
    navigate(path);
  };

  return (
    <>
      {/* Backdrop */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black/60 z-40 transition-opacity"
          onClick={() => setIsOpen(false)}
        />
      )}

      {/* Quick Actions Menu */}
      <div className="fixed bottom-24 right-4 z-50" data-testid="quick-actions-container">
        {/* Action buttons - appear when open */}
        <div className={`flex flex-col-reverse gap-3 mb-3 transition-all duration-300 ${
          isOpen ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4 pointer-events-none'
        }`}>
          {actions.map((action, index) => (
            <button
              key={action.path}
              onClick={() => handleAction(action.path)}
              className={`flex items-center gap-3 px-4 py-3 rounded-full shadow-lg transform transition-all duration-200 hover:scale-105 ${action.color} text-white`}
              style={{ 
                transitionDelay: isOpen ? `${index * 50}ms` : '0ms',
                transform: isOpen ? 'translateX(0)' : 'translateX(20px)'
              }}
              data-testid={`quick-action-${action.label.toLowerCase().replace(' ', '-')}`}
            >
              <action.icon className="w-5 h-5" />
              <span className="font-body font-medium text-sm whitespace-nowrap">{action.label}</span>
            </button>
          ))}
        </div>

        {/* Main FAB button */}
        <button
          onClick={() => setIsOpen(!isOpen)}
          className={`w-14 h-14 rounded-full shadow-lg flex items-center justify-center transition-all duration-300 ${
            isOpen 
              ? 'bg-zinc-700 rotate-45' 
              : 'bg-primary hover:bg-primary/90'
          }`}
          data-testid="quick-actions-fab"
        >
          {isOpen ? (
            <X className="w-6 h-6 text-white" />
          ) : (
            <Plus className="w-6 h-6 text-primary-foreground" />
          )}
        </button>
      </div>
    </>
  );
};
