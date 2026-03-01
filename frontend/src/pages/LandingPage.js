import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Zap, CheckCircle2 } from 'lucide-react';

export const LandingPage = () => {
  const navigate = useNavigate();

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

        {/* CTA Button */}
        <Button
          data-testid="activate-edge-mode-btn"
          onClick={() => navigate('/auth')}
          className="w-full bg-primary text-primary-foreground hover:bg-primary/90 font-heading uppercase tracking-wide font-bold text-xl py-8 mb-6"
        >
          <Zap className="w-6 h-6 mr-3" />
          Activate Edge Mode
        </Button>

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