import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Home, Activity, Users, Trophy, Calendar, User, ShoppingBag } from 'lucide-react';

export const BottomNav = () => {
  const location = useLocation();
  const navigate = useNavigate();

  const navItems = [
    { path: '/dashboard', icon: Home, label: 'Home', testId: 'nav-home' },
    { path: '/log', icon: Activity, label: 'Log', testId: 'nav-log' },
    { path: '/shop', icon: ShoppingBag, label: 'Shop', testId: 'nav-shop' },
    { path: '/groups', icon: Users, label: 'Groups', testId: 'nav-groups' },
    { path: '/leaderboard', icon: Trophy, label: 'Rank', testId: 'nav-leaderboard' },
    { path: '/profile', icon: User, label: 'Profile', testId: 'nav-profile' },
  ];

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-black/80 backdrop-blur-lg border-t border-zinc-800 z-50 overflow-x-auto">
      <div className="flex justify-around items-center h-16 px-2 min-w-max">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path;
          return (
            <button
              key={item.path}
              data-testid={item.testId}
              onClick={() => navigate(item.path)}
              className={`flex flex-col items-center justify-center gap-1 px-2 py-2 rounded-md transition-all duration-200 ${
                isActive
                  ? 'text-primary'
                  : 'text-zinc-500 hover:text-zinc-300'
              }`}
            >
              <Icon className="w-5 h-5" strokeWidth={isActive ? 2.5 : 2} />
              <span className="text-xs font-body whitespace-nowrap">{item.label}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
};