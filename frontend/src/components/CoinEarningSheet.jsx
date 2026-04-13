import React from 'react';
import { X, Coins, CalendarCheck, Scroll, Map, Heart, Users, Sparkles, ShoppingBag, ChevronRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const EARNING_METHODS = [
  {
    icon: CalendarCheck,
    title: 'Daily Login',
    description: 'Open the app daily to earn coins',
    reward: '1-5 coins/day',
    detail: 'Day 7 streak = 5 coins!',
    color: 'text-green-400',
    bg: 'bg-green-400/10',
    link: null
  },
  {
    icon: Scroll,
    title: 'Complete Quests',
    description: 'Finish daily & weekly quests',
    reward: '1-10 coins each',
    detail: 'New quests available daily',
    color: 'text-blue-400',
    bg: 'bg-blue-400/10',
    link: null
  },
  {
    icon: Map,
    title: 'Pet Expeditions',
    description: 'Log 59+ min sessions to unlock',
    reward: '2-25 coins each',
    detail: 'Longer sessions = bigger rewards',
    color: 'text-amber-400',
    bg: 'bg-amber-400/10',
    link: null
  },
  {
    icon: Heart,
    title: 'Pet Evolution Bonus',
    description: 'Evolve your pet for passive coin bonuses',
    reward: '+1-3 coins/session',
    detail: 'Higher evolution = more coins',
    color: 'text-pink-400',
    bg: 'bg-pink-400/10',
    link: '/pets'
  },
  {
    icon: Users,
    title: 'Refer Friends',
    description: 'Invite friends and hit milestones',
    reward: '25-300 coins',
    detail: '10 friends = 300 coin jackpot',
    color: 'text-purple-400',
    bg: 'bg-purple-400/10',
    link: '/referrals'
  },
  {
    icon: Sparkles,
    title: 'Companions',
    description: 'Equip companions for passive coin bonuses',
    reward: '+1-5 coins/session',
    detail: 'Rarer companions = bigger bonus',
    color: 'text-cyan-400',
    bg: 'bg-cyan-400/10',
    link: '/pets'
  }
];

const CoinEarningSheet = ({ isOpen, onClose, currentCoins = 0 }) => {
  const navigate = useNavigate();

  if (!isOpen) return null;

  const handleMethodClick = (link) => {
    if (link) {
      onClose();
      navigate(link);
    }
  };

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 transition-opacity"
        onClick={onClose}
        data-testid="coin-sheet-backdrop"
      />

      {/* Bottom Sheet */}
      <div
        className="fixed bottom-0 left-0 right-0 z-50 bg-zinc-900 border-t border-zinc-800 rounded-t-2xl max-h-[85vh] overflow-hidden animate-in slide-in-from-bottom duration-300"
        data-testid="coin-earning-sheet"
      >
        {/* Drag Handle */}
        <div className="flex justify-center pt-3 pb-1">
          <div className="w-10 h-1 bg-zinc-700 rounded-full" />
        </div>

        {/* Header */}
        <div className="flex items-center justify-between px-5 pb-3 pt-1">
          <div>
            <h2 className="text-lg font-bold text-white">Ways to Earn Coins</h2>
            <div className="flex items-center gap-1.5 mt-0.5">
              <Coins className="w-4 h-4 text-yellow-400" />
              <span className="text-yellow-400 font-bold">{currentCoins}</span>
              <span className="text-zinc-500 text-sm">current balance</span>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-full hover:bg-zinc-800 transition-colors"
            data-testid="coin-sheet-close"
          >
            <X className="w-5 h-5 text-zinc-400" />
          </button>
        </div>

        {/* Methods List */}
        <div className="overflow-y-auto px-4 pb-6 max-h-[65vh]">
          <div className="space-y-2.5">
            {EARNING_METHODS.map((method, index) => {
              const Icon = method.icon;
              return (
                <div
                  key={index}
                  onClick={() => handleMethodClick(method.link)}
                  className={`flex items-start gap-3 p-3.5 rounded-xl bg-zinc-800/60 border border-zinc-800 ${method.link ? 'cursor-pointer hover:bg-zinc-800 hover:border-zinc-700 transition-all' : ''}`}
                  data-testid={`coin-method-${index}`}
                >
                  <div className={`p-2.5 rounded-lg ${method.bg} shrink-0`}>
                    <Icon className={`w-5 h-5 ${method.color}`} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <h3 className="text-sm font-semibold text-white">{method.title}</h3>
                      <span className={`text-xs font-bold ${method.color} bg-black/30 px-2 py-0.5 rounded-full`}>
                        {method.reward}
                      </span>
                    </div>
                    <p className="text-xs text-zinc-400 mt-0.5">{method.description}</p>
                    <p className="text-xs text-zinc-500 mt-0.5 italic">{method.detail}</p>
                  </div>
                  {method.link && (
                    <ChevronRight className="w-4 h-4 text-zinc-600 shrink-0 mt-1" />
                  )}
                </div>
              );
            })}
          </div>

          {/* Shop CTA */}
          <div
            onClick={() => { onClose(); navigate('/shop'); }}
            className="mt-4 p-4 rounded-xl bg-gradient-to-r from-yellow-400/10 to-amber-400/10 border border-yellow-400/20 cursor-pointer hover:border-yellow-400/40 transition-all"
            data-testid="coin-sheet-shop-cta"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <ShoppingBag className="w-5 h-5 text-yellow-400" />
                <div>
                  <p className="text-sm font-semibold text-yellow-400">Spend Your Coins</p>
                  <p className="text-xs text-zinc-400">Badges, pets, vehicles & more</p>
                </div>
              </div>
              <ChevronRight className="w-5 h-5 text-yellow-400" />
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default CoinEarningSheet;
