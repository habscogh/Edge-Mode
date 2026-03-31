// Build: 1772758341
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Zap, CheckCircle2, Users, Flame, Trophy, Calendar, TrendingUp, Bell, Smartphone, Users2, Target, Shield, School, BookOpen } from 'lucide-react';
import { SocialProofSection } from '../components/SocialProofSection';

// Rotating habit quotes for landing page
const HABIT_QUOTES = [
  "If you are going to achieve excellence in big things, you develop the habit in little matters.",
  "First we make our habits, then our habits make us.",
  "95% of everything you do is the result of habit.",
  "Winners make a habit of doing things losers don't want to do.",
  "You are what you repeatedly do.",
  "Good habits formed at youth make all the difference.",
  "You'll never change your life until you change something you do daily.",
  "Winning is a habit. Unfortunately, so is losing.",
  "Tis easier to prevent bad habits than to break them.",
  "Successful people are simply those with successful habits.",
  "Your habits will determine your future.",
  "Excellence is not an act, but a habit.",
  "The secret of your success is found in your daily routine."
];

export const LandingPage = () => {
  const navigate = useNavigate();
  const [isYearly, setIsYearly] = useState(false);
  const [currentQuoteIndex, setCurrentQuoteIndex] = useState(0);

  // Rotate quotes every 10 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentQuoteIndex((prev) => (prev + 1) % HABIT_QUOTES.length);
    }, 10000);
    return () => clearInterval(interval);
  }, []);

  const features = [
    { icon: Target, text: "Track 3-5 personalized improvement pillars" },
    { icon: Flame, text: "Daily streak tracking & milestone badges" },
    { icon: TrendingUp, text: "Weekly performance reviews & analytics" },
    { icon: Calendar, text: "30-day progress graphs & history" },
    { icon: Trophy, text: "30+ achievement badges to unlock" },
    { icon: Users2, text: "Private groups with leaderboards" },
    { icon: School, text: "School leaderboards by city & state" },
    { icon: BookOpen, text: "Daily reflection prompts & growth journal" },
    { icon: Zap, text: "Weekly & monthly challenges" },
    { icon: Bell, text: "Smart reminders & notifications" },
    { icon: Smartphone, text: "Add to home screen (PWA)" },
    { icon: Shield, text: "Offline session logging" },
  ];

  return (
    <div className="min-h-screen bg-[#09090b] flex items-center justify-center p-6">
      <div className="max-w-2xl w-full">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center gap-3 mb-6">
            <Zap className="w-12 h-12 text-primary" />
            <h1 className="text-6xl font-heading font-bold uppercase tracking-tight text-white">
              EDGE MODE
            </h1>
          </div>
          <h2 className="text-2xl font-heading font-bold text-white mb-6">
            Be Better Than Yesterday
          </h2>
          <p className="text-lg text-zinc-300 font-body mb-4">
            A performance system for students and athletes who want an edge.
          </p>
          <p className="text-base text-zinc-400 font-body mb-4">
            Track your daily effort across training, school, and skills.
          </p>
          <p className="text-base text-zinc-400 font-body">
            Review your performance every week.
          </p>
          
          {/* Rotating Habit Quote */}
          <div className="mt-8 bg-gradient-to-r from-primary/20 via-primary/10 to-transparent border border-primary/30 rounded-lg p-4" data-testid="landing-rotating-quote">
            <p 
              key={currentQuoteIndex}
              className="text-white text-lg font-body italic text-center animate-fade-in"
            >
              "{HABIT_QUOTES[currentQuoteIndex]}"
            </p>
          </div>
        </div>

        {/* How It Works */}
        <div className="bg-zinc-950 border border-zinc-800 rounded-md p-8 mb-8">
          <h3 className="text-2xl font-heading font-bold uppercase tracking-tight text-white mb-6 text-center">
            How It Works
          </h3>
          <div className="space-y-4">
            <div className="flex items-start gap-4">
              <CheckCircle2 className="w-6 h-6 text-primary flex-shrink-0 mt-1" />
              <p className="text-white font-body">Choose 3-5 areas to improve</p>
            </div>
            <div className="flex items-start gap-4">
              <CheckCircle2 className="w-6 h-6 text-primary flex-shrink-0 mt-1" />
              <p className="text-white font-body">Log your minutes each day</p>
            </div>
            <div className="flex items-start gap-4">
              <CheckCircle2 className="w-6 h-6 text-primary flex-shrink-0 mt-1" />
              <p className="text-white font-body">Build your streak</p>
            </div>
            <div className="flex items-start gap-4">
              <CheckCircle2 className="w-6 h-6 text-primary flex-shrink-0 mt-1" />
              <p className="text-white font-body">Review your weekly performance</p>
            </div>
          </div>
        </div>

        {/* Social Proof Section - Platform Stats & Testimonials */}
        <SocialProofSection />

        {/* Beta Access Banner */}
        <div className="text-center mb-4">
          <span className="inline-block bg-primary/20 text-primary px-4 py-2 rounded-full font-bold text-sm uppercase tracking-wider">
            Beta Access is Free Right Now
          </span>
        </div>

        {/* CTA Button */}
        <Button
          data-testid="activate-edge-mode-btn"
          onClick={() => navigate('/auth')}
          className="w-full bg-primary text-primary-foreground hover:bg-primary/90 font-heading uppercase tracking-wide font-bold text-xl py-8 mb-4"
        >
          <Zap className="w-6 h-6 mr-3" />
          Activate Edge Mode
        </Button>

        {/* Coach Signup Button - More Prominent */}
        <Button
          data-testid="coach-signup-btn"
          onClick={() => navigate('/coach-signup')}
          variant="outline"
          className="w-full border-2 border-primary text-primary hover:bg-primary/10 font-heading uppercase tracking-normal font-bold py-6 mb-6 text-[10px]"
        >
          <Users className="w-4 h-4 mr-1 flex-shrink-0" />
          Coaches: Click Here to Create Your Free Team Group Account
        </Button>

        {/* Pricing Section */}
        <div className="bg-zinc-950 border border-zinc-800 rounded-md p-8 mb-8" data-testid="pricing-section">
          {/* Features Grid */}
          <div className="border-b border-zinc-800 pb-8 mb-8">
            <p className="text-zinc-400 text-sm font-body uppercase tracking-widest mb-8 text-center">
              Everything included:
            </p>
            <div className="grid grid-cols-2 gap-x-6 gap-y-5">
              {features.map((feature, index) => (
                <div key={index} className="flex items-start gap-3">
                  <feature.icon className="w-5 h-5 text-primary flex-shrink-0 mt-0.5" />
                  <span className="text-white text-sm font-body leading-tight">{feature.text}</span>
                </div>
              ))}
            </div>
          </div>

          <h3 className="text-2xl font-heading font-bold uppercase tracking-tight text-white mb-6 text-center">
            Simple Pricing
          </h3>

          {/* Toggle */}
          <div className="flex items-center justify-center gap-4 mb-6">
            <span className={`font-body text-sm ${!isYearly ? 'text-white' : 'text-zinc-500'}`}>Monthly</span>
            <button
              onClick={() => setIsYearly(!isYearly)}
              className={`relative w-14 h-7 rounded-full transition-colors ${isYearly ? 'bg-primary' : 'bg-zinc-700'}`}
              data-testid="pricing-toggle"
            >
              <div className={`absolute top-1 w-5 h-5 rounded-full bg-white transition-transform ${isYearly ? 'translate-x-8' : 'translate-x-1'}`} />
            </button>
            <span className={`font-body text-sm ${isYearly ? 'text-white' : 'text-zinc-500'}`}>
              Yearly <span className="text-primary font-bold">(Save 17%)</span>
            </span>
          </div>

          {/* Price Display */}
          <div className="text-center">
            <div className="flex items-end justify-center gap-1">
              <span className="text-5xl font-mono font-bold text-white">
                ${isYearly ? '49.99' : '4.99'}
              </span>
              <span className="text-zinc-400 font-body mb-2">
                /{isYearly ? 'year' : 'month'}
              </span>
            </div>
            {isYearly && (
              <p className="text-primary text-sm font-body mt-2">
                That's just $4.17/month!
              </p>
            )}
            {/* No Credit Card Notice - More Visible */}
            <div className="mt-3 inline-flex items-center gap-2 bg-primary/10 border border-primary/30 rounded-full px-4 py-1.5">
              <CheckCircle2 className="w-4 h-4 text-primary" />
              <span className="text-primary font-body text-sm font-medium">No card required to start</span>
            </div>
            {/* Payment Methods */}
            <div className="mt-3 flex items-center justify-center gap-3 text-zinc-500">
              <span className="text-xs">Pay with:</span>
              <div className="flex items-center gap-2">
                <span className="bg-zinc-800 px-2 py-1 rounded text-xs">Apple Pay</span>
                <span className="bg-zinc-800 px-2 py-1 rounded text-xs">Google Pay</span>
                <span className="bg-zinc-800 px-2 py-1 rounded text-xs">Card</span>
                <span className="bg-purple-900/50 text-purple-300 px-2 py-1 rounded text-xs">Parent Gift</span>
              </div>
            </div>
          </div>
        </div>

        {/* Support Email */}
        <div className="text-center">
          <p className="text-zinc-500 text-sm font-body mb-4">
            Support: <a href="mailto:admin@edgemodeapp.com" className="text-zinc-400 hover:text-primary transition-colors">admin@edgemodeapp.com</a>
          </p>
          <div className="flex justify-center gap-4 text-xs text-zinc-600">
            <a href="/faq" className="hover:text-zinc-400 transition-colors">FAQ</a>
            <span>•</span>
            <a href="/privacy" className="hover:text-zinc-400 transition-colors">Privacy Policy</a>
            <span>•</span>
            <a href="/terms" className="hover:text-zinc-400 transition-colors">Terms of Service</a>
          </div>
        </div>
      </div>
    </div>
  );
};