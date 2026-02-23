import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import axios from 'axios';
import { CheckCircle2, Loader2 } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export const SubscriptionSuccessScreen = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState('checking');
  const [attempts, setAttempts] = useState(0);
  const maxAttempts = 10;

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
        return; // Stop polling, don't auto-redirect
      }

      // Continue polling
      setAttempts(currentAttempt + 1);
      setTimeout(() => pollPaymentStatus(sessionId, currentAttempt + 1), 2000);
    } catch (error) {
      console.error('Failed to check payment status:', error);
      setStatus('error');
    }
  };

  return (
    <div className="min-h-screen bg-[#09090b] flex items-center justify-center p-4">
      <div className="text-center max-w-md">
        {status === 'checking' && (
          <>
            <Loader2 className="w-16 h-16 text-primary mx-auto mb-4 animate-spin" />
            <h2 className="text-2xl font-heading font-bold uppercase text-white mb-2">
              Processing Payment
            </h2>
            <p className="text-zinc-400 font-body">Please wait while we confirm your subscription...</p>
            <p className="text-zinc-500 text-sm font-mono mt-4">Attempt {attempts + 1}/{maxAttempts}</p>
          </>
        )}

        {status === 'success' && (
          <>
            <CheckCircle2 className="w-16 h-16 text-primary mx-auto mb-4" />
            <h2 className="text-2xl font-heading font-bold uppercase text-white mb-2">
              Payment Complete!
            </h2>
            <p className="text-zinc-400 font-body mb-4">Your subscription is being activated</p>
            <div className="bg-zinc-900 border border-zinc-800 rounded-md p-4 mb-4">
              <p className="text-zinc-300 font-body text-sm mb-2">
                Please refresh your profile page to see your active subscription status.
              </p>
              <p className="text-zinc-500 text-xs font-body">
                Go to Profile → Pull down to refresh (or reload the page)
              </p>
            </div>
            <button
              onClick={() => navigate('/profile')}
              className="px-6 py-2 bg-primary text-primary-foreground rounded-md font-heading uppercase"
            >
              Go to Profile
            </button>
          </>
        )}

        {status === 'error' && (
          <>
            <div className="w-16 h-16 rounded-full bg-red-500/20 flex items-center justify-center mx-auto mb-4">
              <span className="text-3xl">✗</span>
            </div>
            <h2 className="text-2xl font-heading font-bold uppercase text-white mb-2">
              Payment Error
            </h2>
            <p className="text-zinc-400 font-body mb-4">Failed to process your payment</p>
            <button
              onClick={() => navigate('/profile')}
              className="px-6 py-2 bg-primary text-primary-foreground rounded-md font-heading uppercase"
            >
              Back to Profile
            </button>
          </>
        )}

        {status === 'timeout' && (
          <>
            <div className="w-16 h-16 rounded-full bg-yellow-500/20 flex items-center justify-center mx-auto mb-4">
              <span className="text-3xl">⏱</span>
            </div>
            <h2 className="text-2xl font-heading font-bold uppercase text-white mb-2">
              Taking Longer Than Expected
            </h2>
            <p className="text-zinc-400 font-body mb-4">
              Your payment may still be processing. Check your profile in a few minutes.
            </p>
            <button
              onClick={() => navigate('/profile')}
              className="px-6 py-2 bg-primary text-primary-foreground rounded-md font-heading uppercase"
            >
              Back to Profile
            </button>
          </>
        )}
      </div>
    </div>
  );
};