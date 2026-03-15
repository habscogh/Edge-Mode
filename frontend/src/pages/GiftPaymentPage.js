import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Zap, Gift, Heart, CheckCircle, Loader2 } from 'lucide-react';
import { Button } from '../components/ui/button';
import { toast } from 'sonner';

const API = process.env.REACT_APP_BACKEND_URL;

const GiftPaymentPage = () => {
  const { giftCode } = useParams();
  const navigate = useNavigate();
  const [giftDetails, setGiftDetails] = useState(null);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);

  useEffect(() => {
    fetchGiftDetails();
  }, [giftCode]);

  const fetchGiftDetails = async () => {
    try {
      const res = await axios.get(`${API}/api/payments/gift/${giftCode}`);
      setGiftDetails(res.data);
    } catch (err) {
      console.error('Failed to fetch gift details:', err);
      toast.error('Invalid or expired gift link');
    } finally {
      setLoading(false);
    }
  };

  const handlePayment = async () => {
    setProcessing(true);
    try {
      const res = await axios.post(`${API}/api/payments/gift/${giftCode}/checkout?origin_url=${window.location.origin}`);
      if (res.data.url) {
        window.location.href = res.data.url;
      }
    } catch (err) {
      console.error('Failed to create checkout:', err);
      toast.error(err.response?.data?.detail || 'Failed to start payment');
      setProcessing(false);
    }
  };

  const formatPrice = (cents) => {
    return (cents / 100).toFixed(2);
  };

  const getPlanLabel = (plan) => {
    return plan === 'yearly' ? 'Yearly' : 'Monthly';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-primary animate-spin" />
      </div>
    );
  }

  if (!giftDetails) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center p-4">
        <div className="text-center">
          <Gift className="w-16 h-16 text-zinc-600 mx-auto mb-4" />
          <h1 className="text-2xl font-heading font-bold text-white mb-2">Link Not Found</h1>
          <p className="text-zinc-400">This gift link is invalid or has expired.</p>
        </div>
      </div>
    );
  }

  if (giftDetails.status === 'paid') {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center p-4">
        <div className="text-center">
          <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
          <h1 className="text-2xl font-heading font-bold text-white mb-2">Already Paid!</h1>
          <p className="text-zinc-400">This subscription has already been gifted.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-2 mb-4">
            <Zap className="w-8 h-8 text-primary" />
            <span className="text-2xl font-heading font-bold text-white uppercase tracking-tight">Edge Mode</span>
          </div>
          <div className="inline-flex items-center gap-2 bg-purple-500/20 border border-purple-500/30 rounded-full px-4 py-2">
            <Gift className="w-5 h-5 text-purple-400" />
            <span className="text-purple-300 font-body">Gift a Subscription</span>
          </div>
        </div>

        {/* Gift Card */}
        <div className="bg-zinc-950 border border-zinc-800 rounded-lg p-6 mb-6">
          <div className="text-center mb-6">
            <Heart className="w-12 h-12 text-pink-500 mx-auto mb-3" />
            <h2 className="text-xl font-heading font-bold text-white mb-2">
              Gift for {giftDetails.username}
            </h2>
            <p className="text-zinc-400 text-sm font-body">
              Help your teen build better habits with Edge Mode
            </p>
          </div>

          {/* Plan Details */}
          <div className="bg-zinc-900 rounded-lg p-4 mb-6">
            <div className="flex justify-between items-center mb-2">
              <span className="text-zinc-400 font-body">Plan</span>
              <span className="text-white font-medium">{getPlanLabel(giftDetails.plan)} Subscription</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-zinc-400 font-body">Amount</span>
              <span className="text-2xl font-mono font-bold text-primary">
                ${formatPrice(giftDetails.amount)}
              </span>
            </div>
          </div>

          {/* What They Get */}
          <div className="mb-6">
            <p className="text-zinc-500 text-xs uppercase tracking-wide mb-3">What they'll get:</p>
            <ul className="space-y-2 text-sm text-zinc-300 font-body">
              <li className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-primary flex-shrink-0" />
                Daily habit tracking across all areas
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-primary flex-shrink-0" />
                Streak tracking & achievements
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-primary flex-shrink-0" />
                Weekly performance insights
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-primary flex-shrink-0" />
                Community challenges & leaderboards
              </li>
            </ul>
          </div>

          {/* Pay Button */}
          <Button
            onClick={handlePayment}
            disabled={processing}
            className="w-full bg-gradient-to-r from-purple-500 to-pink-500 hover:opacity-90 text-white font-heading uppercase tracking-wide font-bold py-6 text-lg"
            data-testid="gift-pay-btn"
          >
            {processing ? (
              <>
                <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                Processing...
              </>
            ) : (
              <>
                <Gift className="w-5 h-5 mr-2" />
                Pay ${formatPrice(giftDetails.amount)} as Gift
              </>
            )}
          </Button>

          {/* Payment Methods */}
          <div className="mt-4 flex items-center justify-center gap-2 text-zinc-500 text-xs">
            <span>Pay with:</span>
            <span className="bg-zinc-800 px-2 py-1 rounded">Apple Pay</span>
            <span className="bg-zinc-800 px-2 py-1 rounded">Google Pay</span>
            <span className="bg-zinc-800 px-2 py-1 rounded">Card</span>
          </div>

          <p className="text-zinc-500 text-xs text-center mt-4 font-body">
            Secure payment powered by Stripe
          </p>
        </div>

        {/* Back Link */}
        <div className="text-center">
          <button
            onClick={() => navigate('/')}
            className="text-zinc-500 text-sm hover:text-white transition-colors"
          >
            Learn more about Edge Mode →
          </button>
        </div>
      </div>
    </div>
  );
};

export default GiftPaymentPage;
