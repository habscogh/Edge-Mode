import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Flame, AlertTriangle, Clock, CreditCard, X, Loader2, Zap } from 'lucide-react';
import { Button } from './ui/button';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export const StreakRecoveryModal = ({ isOpen, onClose, onRecoveryStarted }) => {
  const [eligibility, setEligibility] = useState(null);
  const [loading, setLoading] = useState(true);
  const [purchasing, setPurchasing] = useState(false);

  useEffect(() => {
    if (isOpen) {
      checkEligibility();
    }
  }, [isOpen]);

  const checkEligibility = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/streak-recovery/eligibility`);
      setEligibility(response.data);
    } catch (error) {
      console.error('Failed to check eligibility:', error);
      toast.error('Failed to check recovery eligibility');
    } finally {
      setLoading(false);
    }
  };

  const handlePurchase = async () => {
    setPurchasing(true);
    try {
      const response = await axios.post(`${API}/streak-recovery/create-checkout`, {
        origin_url: window.location.origin
      });
      
      if (response.data.url) {
        onRecoveryStarted?.();
        window.location.href = response.data.url;
      }
    } catch (error) {
      console.error('Failed to create checkout:', error);
      toast.error(error.response?.data?.detail || 'Failed to start recovery');
      setPurchasing(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
      <div className="bg-zinc-900 border border-zinc-800 rounded-xl max-w-md w-full overflow-hidden animate-fade-in">
        {/* Header */}
        <div className="bg-gradient-to-r from-orange-600 to-orange-500 p-4 relative">
          <button
            onClick={onClose}
            className="absolute top-3 right-3 text-white/80 hover:text-white"
          >
            <X className="w-5 h-5" />
          </button>
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center">
              <Flame className="w-6 h-6 text-white" />
            </div>
            <div>
              <h2 className="text-xl font-heading font-bold uppercase text-white">
                Streak Recovery
              </h2>
              <p className="text-orange-100 text-sm">Don't lose your progress!</p>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="p-5">
          {loading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="w-8 h-8 text-orange-500 animate-spin" />
            </div>
          ) : eligibility?.eligible ? (
            <>
              {/* Recoverable streak info */}
              <div className="bg-zinc-950 border border-zinc-800 rounded-lg p-4 mb-4">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-zinc-400 text-sm">Your broken streak</span>
                  <span className="text-orange-400 font-bold text-2xl">
                    {eligibility.previous_streak} days
                  </span>
                </div>
                <div className="flex items-center gap-2 text-zinc-500 text-sm">
                  <Clock className="w-4 h-4" />
                  <span>
                    {eligibility.recovery_window_days} day{eligibility.recovery_window_days !== 1 ? 's' : ''} left to recover
                  </span>
                </div>
              </div>

              {/* What you get */}
              <div className="space-y-2 mb-5">
                <p className="text-zinc-300 text-sm font-medium">What you get:</p>
                <ul className="space-y-1.5">
                  {[
                    `Restore your ${eligibility.previous_streak}-day streak instantly`,
                    'Keep your leaderboard position',
                    'Maintain your momentum',
                    'No questions asked'
                  ].map((item, i) => (
                    <li key={i} className="flex items-center gap-2 text-zinc-400 text-sm">
                      <Zap className="w-3.5 h-3.5 text-orange-400 flex-shrink-0" />
                      {item}
                    </li>
                  ))}
                </ul>
              </div>

              {/* Price and CTA */}
              <div className="space-y-3">
                <div className="flex items-center justify-between p-3 bg-orange-500/10 border border-orange-500/30 rounded-lg">
                  <span className="text-zinc-300 font-medium">One-time recovery</span>
                  <span className="text-orange-400 font-bold text-xl">
                    ${eligibility.recovery_price.toFixed(2)}
                  </span>
                </div>
                <Button
                  onClick={handlePurchase}
                  disabled={purchasing}
                  className="w-full bg-orange-500 hover:bg-orange-600 text-white font-heading uppercase py-5"
                >
                  {purchasing ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Processing...
                    </>
                  ) : (
                    <>
                      <CreditCard className="w-4 h-4 mr-2" />
                      Recover My Streak
                    </>
                  )}
                </Button>
                <p className="text-zinc-600 text-xs text-center">
                  Secure payment powered by Stripe
                </p>
              </div>
            </>
          ) : (
            /* Not eligible */
            <div className="text-center py-4">
              <div className="w-16 h-16 bg-zinc-800 rounded-full flex items-center justify-center mx-auto mb-4">
                <AlertTriangle className="w-8 h-8 text-zinc-500" />
              </div>
              <h3 className="text-lg font-heading font-bold uppercase text-white mb-2">
                No Recovery Needed
              </h3>
              <p className="text-zinc-400 text-sm mb-4">
                {eligibility?.reason || 'Your streak is intact! Keep grinding.'}
              </p>
              <Button
                onClick={onClose}
                variant="outline"
                className="border-zinc-700"
              >
                Got it
              </Button>
            </div>
          )}
        </div>
      </div>

      <style>{`
        .animate-fade-in {
          animation: fadeIn 0.3s ease-out;
        }
        @keyframes fadeIn {
          from { opacity: 0; transform: scale(0.95); }
          to { opacity: 1; transform: scale(1); }
        }
      `}</style>
    </div>
  );
};

// Hook to check if streak recovery is available
export const useStreakRecovery = () => {
  const [isEligible, setIsEligible] = useState(false);
  const [eligibilityData, setEligibilityData] = useState(null);

  const checkEligibility = async () => {
    try {
      const response = await axios.get(`${API}/streak-recovery/eligibility`);
      setIsEligible(response.data.eligible);
      setEligibilityData(response.data);
      return response.data;
    } catch (error) {
      setIsEligible(false);
      return null;
    }
  };

  return { isEligible, eligibilityData, checkEligibility };
};
