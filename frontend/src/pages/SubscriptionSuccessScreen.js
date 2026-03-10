import React, { useEffect, useState, useCallback } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import axios from 'axios';
import confetti from 'canvas-confetti';
import { CheckCircle2, Loader2, Zap, Share2, Twitter, Copy, Sparkles, Star, Crown } from 'lucide-react';
import { Button } from '../components/ui/button';
import { toast } from 'sonner';
import { useAuth } from '../context/AuthContext';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export const SubscriptionSuccessScreen = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { user, fetchUser } = useAuth();
  const [status, setStatus] = useState('checking');
  const [attempts, setAttempts] = useState(0);
  const [showShareOptions, setShowShareOptions] = useState(false);
  const maxAttempts = 10;

  // Confetti celebration effect
  const triggerConfetti = useCallback(() => {
    const duration = 4000;
    const animationEnd = Date.now() + duration;
    const defaults = { startVelocity: 30, spread: 360, ticks: 60, zIndex: 100 };

    const randomInRange = (min, max) => Math.random() * (max - min) + min;

    const interval = setInterval(() => {
      const timeLeft = animationEnd - Date.now();

      if (timeLeft <= 0) {
        return clearInterval(interval);
      }

      const particleCount = 50 * (timeLeft / duration);

      // Confetti from both sides
      confetti({
        ...defaults,
        particleCount,
        origin: { x: randomInRange(0.1, 0.3), y: Math.random() - 0.2 },
        colors: ['#22c55e', '#10b981', '#34d399', '#6ee7b7', '#fbbf24', '#f59e0b']
      });
      confetti({
        ...defaults,
        particleCount,
        origin: { x: randomInRange(0.7, 0.9), y: Math.random() - 0.2 },
        colors: ['#22c55e', '#10b981', '#34d399', '#6ee7b7', '#fbbf24', '#f59e0b']
      });
    }, 250);

    // Big burst in the center
    setTimeout(() => {
      confetti({
        particleCount: 100,
        spread: 70,
        origin: { y: 0.6 },
        colors: ['#22c55e', '#10b981', '#fbbf24']
      });
    }, 300);
  }, []);

  useEffect(() => {
    const sessionId = searchParams.get('session_id');
    if (!sessionId) {
      navigate('/profile');
      return;
    }

    pollPaymentStatus(sessionId);
  }, []);

  const pollPaymentStatus = async (sessionId, currentAttempt = 0) => {
    if (currentAttempt >= maxAttempts) {
      setStatus('timeout');
      return;
    }

    try {
      const response = await axios.get(`${API}/payments/status/${sessionId}`);
      
      if (response.data.payment_status === 'paid') {
        setStatus('success');
        // Trigger celebration
        setTimeout(() => triggerConfetti(), 500);
        // Refresh user data to get updated subscription status
        await fetchUser();
        return;
      }

      setAttempts(currentAttempt + 1);
      setTimeout(() => pollPaymentStatus(sessionId, currentAttempt + 1), 2000);
    } catch (error) {
      console.error('Failed to check payment status:', error);
      setStatus('error');
    }
  };

  const handleShare = (platform) => {
    const shareText = `🚀 Just leveled up! I'm now a premium Edge Mode member - committed to being 1% better every day! #EdgeMode #SelfImprovement`;
    const shareUrl = 'https://edgemodeapp.com';

    if (platform === 'twitter') {
      window.open(
        `https://twitter.com/intent/tweet?text=${encodeURIComponent(shareText)}&url=${encodeURIComponent(shareUrl)}`,
        '_blank'
      );
    } else if (platform === 'copy') {
      navigator.clipboard.writeText(`${shareText}\n\n${shareUrl}`);
      toast.success('Copied to clipboard!');
    } else if (platform === 'native' && navigator.share) {
      navigator.share({
        title: 'Edge Mode Premium',
        text: shareText,
        url: shareUrl
      }).catch(() => {});
    }
  };

  return (
    <div className="min-h-screen bg-[#09090b] flex items-center justify-center p-4 overflow-hidden">
      <div className="text-center max-w-md relative">
        {status === 'checking' && (
          <div className="animate-fade-in">
            <div className="relative">
              <Loader2 className="w-20 h-20 text-primary mx-auto mb-6 animate-spin" />
              <div className="absolute inset-0 w-20 h-20 mx-auto rounded-full bg-primary/20 animate-ping" />
            </div>
            <h2 className="text-2xl font-heading font-bold uppercase text-white mb-2">
              Processing Payment
            </h2>
            <p className="text-zinc-400 font-body">Confirming your subscription...</p>
            <div className="mt-6 flex justify-center gap-1">
              {[...Array(maxAttempts)].map((_, i) => (
                <div
                  key={i}
                  className={`w-2 h-2 rounded-full transition-all duration-300 ${
                    i <= attempts ? 'bg-primary' : 'bg-zinc-700'
                  }`}
                />
              ))}
            </div>
          </div>
        )}

        {status === 'success' && (
          <div className="animate-fade-in">
            {/* Animated success badge */}
            <div className="relative mb-8">
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="w-32 h-32 bg-primary/20 rounded-full animate-pulse" />
              </div>
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="w-24 h-24 bg-primary/30 rounded-full animate-ping" style={{ animationDuration: '2s' }} />
              </div>
              <div className="relative w-28 h-28 mx-auto bg-gradient-to-br from-primary to-emerald-400 rounded-full flex items-center justify-center shadow-lg shadow-primary/50">
                <Crown className="w-14 h-14 text-black" />
              </div>
              <div className="absolute -top-2 -right-2 animate-bounce">
                <Sparkles className="w-8 h-8 text-yellow-400" />
              </div>
              <div className="absolute -bottom-1 -left-2 animate-bounce" style={{ animationDelay: '0.5s' }}>
                <Star className="w-6 h-6 text-yellow-400 fill-yellow-400" />
              </div>
            </div>

            {/* Welcome message */}
            <h1 className="text-4xl font-heading font-bold uppercase text-white mb-2 tracking-tight">
              Welcome to
            </h1>
            <h2 className="text-3xl font-heading font-bold uppercase mb-4">
              <span className="bg-gradient-to-r from-primary via-emerald-400 to-primary bg-clip-text text-transparent animate-gradient">
                Edge Mode Premium
              </span>
            </h2>
            
            <p className="text-zinc-300 font-body text-lg mb-6">
              You're now part of the elite {user?.username ? `— let's go, ${user.username}!` : ''}
            </p>

            {/* Benefits unlocked */}
            <div className="bg-zinc-900/50 border border-zinc-800 rounded-xl p-5 mb-6 text-left">
              <h3 className="text-sm font-heading uppercase text-zinc-400 mb-3 flex items-center gap-2">
                <Zap className="w-4 h-4 text-primary" />
                Unlocked Features
              </h3>
              <ul className="space-y-2">
                {[
                  'Unlimited session logging',
                  'Advanced analytics & insights',
                  'School leaderboards',
                  'Weekly challenges',
                  'Growth journal & reflections',
                  'Priority support'
                ].map((feature, i) => (
                  <li key={i} className="flex items-center gap-2 text-zinc-300 font-body text-sm">
                    <CheckCircle2 className="w-4 h-4 text-primary flex-shrink-0" />
                    {feature}
                  </li>
                ))}
              </ul>
            </div>

            {/* Share section */}
            <div className="mb-6">
              <Button
                onClick={() => setShowShareOptions(!showShareOptions)}
                variant="outline"
                className="w-full border-zinc-700 hover:border-primary hover:bg-primary/10 transition-all"
              >
                <Share2 className="w-4 h-4 mr-2" />
                Share Your Achievement
              </Button>

              {showShareOptions && (
                <div className="mt-3 flex justify-center gap-3 animate-fade-in">
                  <Button
                    onClick={() => handleShare('twitter')}
                    size="sm"
                    className="bg-[#1DA1F2] hover:bg-[#1a8cd8] text-white"
                  >
                    <Twitter className="w-4 h-4 mr-1" />
                    Tweet
                  </Button>
                  <Button
                    onClick={() => handleShare('copy')}
                    size="sm"
                    variant="outline"
                    className="border-zinc-700"
                  >
                    <Copy className="w-4 h-4 mr-1" />
                    Copy
                  </Button>
                  {navigator.share && (
                    <Button
                      onClick={() => handleShare('native')}
                      size="sm"
                      variant="outline"
                      className="border-zinc-700"
                    >
                      <Share2 className="w-4 h-4 mr-1" />
                      More
                    </Button>
                  )}
                </div>
              )}
            </div>

            {/* CTA buttons */}
            <div className="flex flex-col gap-3">
              <Button
                onClick={() => navigate('/dashboard')}
                className="w-full bg-primary hover:bg-primary/90 text-primary-foreground font-heading uppercase py-6 text-lg"
              >
                <Zap className="w-5 h-5 mr-2" />
                Start Grinding
              </Button>
              <Button
                onClick={() => navigate('/profile')}
                variant="ghost"
                className="text-zinc-400 hover:text-white"
              >
                View Profile
              </Button>
            </div>
          </div>
        )}

        {status === 'error' && (
          <div className="animate-fade-in">
            <div className="w-20 h-20 rounded-full bg-red-500/20 flex items-center justify-center mx-auto mb-6 border-2 border-red-500/50">
              <span className="text-4xl">✗</span>
            </div>
            <h2 className="text-2xl font-heading font-bold uppercase text-white mb-2">
              Payment Error
            </h2>
            <p className="text-zinc-400 font-body mb-6">
              Something went wrong processing your payment. Don't worry, you haven't been charged.
            </p>
            <Button
              onClick={() => navigate('/profile')}
              className="bg-primary text-primary-foreground font-heading uppercase"
            >
              Back to Profile
            </Button>
          </div>
        )}

        {status === 'timeout' && (
          <div className="animate-fade-in">
            <div className="w-20 h-20 rounded-full bg-yellow-500/20 flex items-center justify-center mx-auto mb-6 border-2 border-yellow-500/50">
              <Loader2 className="w-10 h-10 text-yellow-500 animate-spin" />
            </div>
            <h2 className="text-2xl font-heading font-bold uppercase text-white mb-2">
              Still Processing
            </h2>
            <p className="text-zinc-400 font-body mb-6">
              Your payment is taking longer than expected. It may still go through — check your profile in a few minutes.
            </p>
            <div className="flex gap-3 justify-center">
              <Button
                onClick={() => {
                  setStatus('checking');
                  setAttempts(0);
                  const sessionId = searchParams.get('session_id');
                  if (sessionId) pollPaymentStatus(sessionId);
                }}
                variant="outline"
                className="border-zinc-700"
              >
                Try Again
              </Button>
              <Button
                onClick={() => navigate('/profile')}
                className="bg-primary text-primary-foreground font-heading uppercase"
              >
                Go to Profile
              </Button>
            </div>
          </div>
        )}
      </div>

      {/* Background decorations for success state */}
      {status === 'success' && (
        <>
          <div className="fixed top-0 left-0 w-full h-full pointer-events-none overflow-hidden">
            <div className="absolute top-20 left-10 w-64 h-64 bg-primary/5 rounded-full blur-3xl animate-pulse" />
            <div className="absolute bottom-20 right-10 w-96 h-96 bg-emerald-500/5 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }} />
          </div>
        </>
      )}

      <style>{`
        @keyframes gradient {
          0%, 100% { background-position: 0% 50%; }
          50% { background-position: 100% 50%; }
        }
        .animate-gradient {
          background-size: 200% 200%;
          animation: gradient 3s ease infinite;
        }
        .animate-fade-in {
          animation: fadeIn 0.5s ease-out;
        }
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </div>
  );
};
