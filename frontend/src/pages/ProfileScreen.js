import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { User, LogOut, CreditCard, Trophy, Loader2 } from 'lucide-react';
import { format } from 'date-fns';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export const ProfileScreen = () => {
  const { user, logout, fetchUser } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const handleSubscribe = async () => {
    setLoading(true);
    try {
      const originUrl = window.location.origin;
      const response = await axios.post(`${API}/payments/create-checkout`, {
        origin_url: originUrl
      });
      
      if (response.data.url) {
        window.location.href = response.data.url;
      }
    } catch (error) {
      console.error('Failed to create checkout:', error);
      alert('Failed to start subscription process. Please try again.');
      setLoading(false);
    }
  };

  if (!user) return null;

  return (
    <div className="min-h-screen bg-[#09090b] p-4 pb-24">
      <div className="max-w-2xl mx-auto pt-6">
        <h1 className="text-3xl font-heading font-bold uppercase tracking-tight text-white mb-6">
          Profile
        </h1>

        <div className="bg-zinc-950 border border-zinc-800 rounded-md p-6 mb-4">
          <div className="flex items-center gap-4 mb-6">
            <div className="w-16 h-16 rounded-full bg-primary/20 flex items-center justify-center">
              <User className="w-8 h-8 text-primary" />
            </div>
            <div>
              <h2 className="text-2xl font-heading font-bold uppercase text-white">{user.username}</h2>
              <p className="text-zinc-400 font-body text-sm">{user.email}</p>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4 mb-4">
            <div className="bg-zinc-900 border border-zinc-800 rounded-md p-4">
              <div className="text-zinc-400 text-xs font-body uppercase tracking-wide mb-1">Age</div>
              <div className="text-xl font-mono font-bold text-white">{user.age}</div>
            </div>
            <div className="bg-zinc-900 border border-zinc-800 rounded-md p-4">
              <div className="text-zinc-400 text-xs font-body uppercase tracking-wide mb-1">Joined</div>
              <div className="text-xl font-mono font-bold text-white">
                {format(new Date(user.join_date), 'MMM yyyy')}
              </div>
            </div>
          </div>

          <div className="bg-zinc-900 border border-zinc-800 rounded-md p-4">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <Trophy className="w-4 h-4 text-primary" />
                <span className="text-white font-body">Achievements</span>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-2 text-center">
              <div>
                <div className="text-2xl font-mono font-bold text-primary">{user.current_streak}</div>
                <div className="text-zinc-500 text-xs font-body">Current Streak</div>
              </div>
              <div>
                <div className="text-2xl font-mono font-bold text-white">{user.longest_streak}</div>
                <div className="text-zinc-500 text-xs font-body">Longest Streak</div>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-zinc-950 border border-zinc-800 rounded-md p-6 mb-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <CreditCard className="w-5 h-5 text-primary" />
              <div>
                <div className="text-white font-body">Subscription</div>
                <div className="text-zinc-400 text-sm font-body">$5.99/month</div>
              </div>
            </div>
            <div className={`px-3 py-1 rounded-full text-xs font-mono font-bold ${
              user.subscription_active
                ? 'bg-primary/20 text-primary'
                : 'bg-zinc-800 text-zinc-400'
            }`}>
              {user.subscription_active ? 'ACTIVE' : 'INACTIVE'}
            </div>
          </div>
        </div>

        <Button
          data-testid="logout-btn"
          onClick={handleLogout}
          variant="ghost"
          className="w-full text-red-500 hover:text-red-400 hover:bg-red-500/10 font-heading uppercase tracking-wide"
        >
          <LogOut className="w-5 h-5 mr-2" />
          Logout
        </Button>
      </div>
    </div>
  );
};