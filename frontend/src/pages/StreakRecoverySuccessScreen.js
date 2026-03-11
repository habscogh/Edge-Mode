import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import axios from 'axios';
import confetti from 'canvas-confetti';
import { Flame, Loader2, CheckCircle2, AlertTriangle, ArrowLeft, Zap } from 'lucide-react';
import { Button } from '../components/ui/button';
import { useAuth } from '../context/AuthContext';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export const StreakRecoverySuccessScreen = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { fetchUser } = useAuth();
  const [status, setStatus] = useState('checking');
  const [recoveredStreak, setRecoveredStreak] = useState(0);
  const [attempts, setAttempts] = useState(0);
  const maxAttempts = 10;

  useEffect(() => {
    const recoveryId = searchParams.get('recovery_id');
    if (!recoveryId) {
      navigate('/dashboard');
      return;
    }
    pollRecoveryStatus(recoveryId);
  }, []);

  const triggerConfetti = () => {
    confetti({
      particleCount: 100,
      spread: 70,
      origin: { y: 0.6 },
      colors: ['#f97316', '#fb923c', '#fdba74', '#22c55e']
    });
    setTimeout(() => {
      confetti({
        particleCount: 50,
        angle: 60,
        spread: 55,
        origin: { x: 0 },
        colors: ['#f97316', '#22c55e']
      });
      confetti({
        particleCount: 50,
        angle: 120,
        spread: 55,
        origin: { x: 1 },
        colors: ['#f97316', '#22c55e']
      });
    }, 200);
  };

  const pollRecoveryStatus = async (recoveryId, currentAttempt = 0) => {
    if (currentAttempt >= maxAttempts) {
      setStatus('timeout');
      return;
    }

    try {
      const response = await axios.get(`${API}/streak-recovery/status/${recoveryId}`);
      
      if (response.data.status === 'completed') {
        setStatus('success');
        setRecoveredStreak(response.data.recovered_streak);
        triggerConfetti();
        await fetchUser();
        return;
      }

      setAttempts(currentAttempt + 1);
      setTimeout(() => pollRecoveryStatus(recoveryId, currentAttempt + 1), 2000);
    } catch (error) {
      console.error('Failed to check recovery status:', error);
      setStatus('error');
    }
  };

  return (
    <div className="min-h-screen bg-[#09090b] flex items-center justify-center p-4">
      <div className="text-center max-w-md">
        {status === 'checking' && (
          <div className="animate-fade-in">
            <div className="relative">
              <Loader2 className="w-20 h-20 text-orange-500 mx-auto mb-6 animate-spin" />
              <Flame className="w-8 h-8 text-orange-400 absolute top-6 left-1/2 -translate-x-1/2 animate-pulse" />
            </div>
            <h2 className="text-2xl font-heading font-bold uppercase text-white mb-2">
              Restoring Your Streak
            </h2>
            <p className="text-zinc-400 font-body">Processing your recovery...</p>
            <div className="mt-6 flex justify-center gap-1">
              {[...Array(maxAttempts)].map((_, i) => (
                <div
                  key={i}
                  className={`w-2 h-2 rounded-full transition-all duration-300 ${
                    i <= attempts ? 'bg-orange-500' : 'bg-zinc-700'
                  }`}
                />
              ))}
            </div>
          </div>
        )}

        {status === 'success' && (
          <div className="animate-fade-in">
            <div className="relative mb-8">
              <div className="w-28 h-28 mx-auto bg-gradient-to-br from-orange-500 to-orange-600 rounded-full flex items-center justify-center shadow-lg shadow-orange-500/50">
                <Flame className="w-14 h-14 text-white" />
              </div>
              <div className="absolute -top-2 -right-4">
                <CheckCircle2 className="w-10 h-10 text-green-500" />
              </div>
            </div>

            <h1 className="text-4xl font-heading font-bold uppercase text-white mb-2">
              Streak Restored!
            </h1>
            <p className="text-zinc-300 font-body text-lg mb-2">
              Your <span className="text-orange-400 font-bold">{recoveredStreak}-day streak</span> is back!
            </p>
            <p className="text-zinc-500 font-body text-sm mb-8">
              Don't let it slip again — log a session today to keep the fire burning!
            </p>

            <div className="flex flex-col gap-3">
              <Button
                onClick={() => navigate('/log')}
                className="w-full bg-orange-500 hover:bg-orange-600 text-white font-heading uppercase py-6 text-lg"
              >
                <Flame className="w-5 h-5 mr-2" />
                Log Session Now
              </Button>
              <Button
                onClick={() => navigate('/dashboard')}
                variant="ghost"
                className="text-zinc-400 hover:text-white"
              >
                Go to Dashboard
              </Button>
            </div>
          </div>
        )}

        {status === 'error' && (
          <div className="animate-fade-in">
            <div className="w-20 h-20 rounded-full bg-red-500/20 flex items-center justify-center mx-auto mb-6 border-2 border-red-500/50">
              <AlertTriangle className="w-10 h-10 text-red-500" />
            </div>
            <h2 className="text-2xl font-heading font-bold uppercase text-white mb-2">
              Recovery Failed
            </h2>
            <p className="text-zinc-400 font-body mb-6">
              Something went wrong. If you were charged, please contact support.
            </p>
            <Button
              onClick={() => navigate('/dashboard')}
              className="bg-primary text-primary-foreground font-heading uppercase"
            >
              Back to Dashboard
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
              Your recovery is taking longer than expected. Check your dashboard in a moment.
            </p>
            <Button
              onClick={() => navigate('/dashboard')}
              className="bg-primary text-primary-foreground font-heading uppercase"
            >
              Go to Dashboard
            </Button>
          </div>
        )}
      </div>

      <style>{`
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
