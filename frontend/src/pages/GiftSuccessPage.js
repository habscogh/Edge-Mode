import React, { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Gift, CheckCircle, Heart, Sparkles } from 'lucide-react';
import { Button } from '../components/ui/button';
import confetti from 'canvas-confetti';

const API = process.env.REACT_APP_BACKEND_URL;

const GiftSuccessPage = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [giftDetails, setGiftDetails] = useState(null);
  const giftCode = searchParams.get('gift_code');

  useEffect(() => {
    // Trigger confetti
    const duration = 3000;
    const end = Date.now() + duration;

    const frame = () => {
      confetti({
        particleCount: 3,
        angle: 60,
        spread: 55,
        origin: { x: 0 },
        colors: ['#a855f7', '#ec4899', '#10b981']
      });
      confetti({
        particleCount: 3,
        angle: 120,
        spread: 55,
        origin: { x: 1 },
        colors: ['#a855f7', '#ec4899', '#10b981']
      });

      if (Date.now() < end) {
        requestAnimationFrame(frame);
      }
    };
    frame();

    // Fetch gift details
    if (giftCode) {
      fetchGiftStatus();
    }
  }, [giftCode]);

  const fetchGiftStatus = async () => {
    try {
      const res = await axios.get(`${API}/api/payments/gift/${giftCode}/status`);
      setGiftDetails(res.data);
    } catch (err) {
      console.error('Failed to fetch gift status:', err);
    }
  };

  return (
    <div className="min-h-screen bg-black flex items-center justify-center p-4">
      <div className="max-w-md w-full text-center">
        {/* Success Icon */}
        <div className="relative mb-6">
          <div className="w-24 h-24 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center mx-auto">
            <Gift className="w-12 h-12 text-white" />
          </div>
          <div className="absolute -top-2 -right-2 w-10 h-10 bg-green-500 rounded-full flex items-center justify-center border-4 border-black">
            <CheckCircle className="w-6 h-6 text-white" />
          </div>
        </div>

        {/* Thank You Message */}
        <h1 className="text-3xl font-heading font-bold text-white mb-3">
          Thank You! <Heart className="inline w-6 h-6 text-pink-500" />
        </h1>
        
        <p className="text-zinc-300 font-body mb-6">
          Your gift has been received! 
          {giftDetails?.username && (
            <span className="text-primary font-bold"> {giftDetails.username}</span>
          )} now has full access to Edge Mode.
        </p>

        {/* What Happens Next */}
        <div className="bg-zinc-950 border border-zinc-800 rounded-lg p-6 mb-6 text-left">
          <h3 className="text-white font-heading font-bold mb-4 flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-yellow-500" />
            What happens next?
          </h3>
          <ul className="space-y-3 text-sm text-zinc-300 font-body">
            <li className="flex items-start gap-3">
              <CheckCircle className="w-4 h-4 text-green-500 flex-shrink-0 mt-0.5" />
              <span>The subscription is now active on their account</span>
            </li>
            <li className="flex items-start gap-3">
              <CheckCircle className="w-4 h-4 text-green-500 flex-shrink-0 mt-0.5" />
              <span>They can start tracking their daily progress immediately</span>
            </li>
            <li className="flex items-start gap-3">
              <CheckCircle className="w-4 h-4 text-green-500 flex-shrink-0 mt-0.5" />
              <span>You've helped them take a big step toward building better habits!</span>
            </li>
          </ul>
        </div>

        {/* Receipt Note */}
        <p className="text-zinc-500 text-xs font-body mb-6">
          A receipt has been sent to your email address.
        </p>

        {/* CTA */}
        <Button
          onClick={() => navigate('/')}
          variant="outline"
          className="border-zinc-700 text-zinc-300 hover:bg-zinc-800"
        >
          Learn More About Edge Mode
        </Button>
      </div>
    </div>
  );
};

export default GiftSuccessPage;
