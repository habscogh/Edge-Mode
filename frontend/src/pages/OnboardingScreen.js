import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Button } from '../components/ui/button';
import { Checkbox } from '../components/ui/checkbox';
import { Input } from '../components/ui/input';
import { Flame, CheckCircle2 } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export const OnboardingScreen = () => {
  const [step, setStep] = useState(1);
  const [availablePillars, setAvailablePillars] = useState([]);
  const [selectedPillars, setSelectedPillars] = useState([]);
  const [targets, setTargets] = useState({});
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    fetchPillars();
  }, []);

  const fetchPillars = async () => {
    try {
      const response = await axios.get(`${API}/pillars`);
      setAvailablePillars(response.data.pillars);
    } catch (error) {
      console.error('Failed to fetch pillars:', error);
    }
  };

  const togglePillar = (pillar) => {
    if (selectedPillars.includes(pillar)) {
      setSelectedPillars(selectedPillars.filter(p => p !== pillar));
      const newTargets = { ...targets };
      delete newTargets[pillar];
      setTargets(newTargets);
    } else {
      if (selectedPillars.length < 5) {
        setSelectedPillars([...selectedPillars, pillar]);
      }
    }
  };

  const handleTargetChange = (pillar, value) => {
    const numValue = value === '' ? 0 : parseInt(value);
    setTargets({ ...targets, [pillar]: numValue });
  };

  const isStep2Valid = () => {
    return selectedPillars.every(p => targets[p] && targets[p] > 0);
  };

  const handleNext = () => {
    if (step === 1 && selectedPillars.length >= 3 && selectedPillars.length <= 5) {
      setStep(2);
    }
  };

  const handleComplete = async () => {
    setLoading(true);
    try {
      const pillars = selectedPillars.map(pillar => ({
        pillar_name: pillar,
        weekly_target_sessions: targets[pillar] || 5
      }));

      await axios.post(`${API}/onboarding/complete`, { pillars });
      setStep(3);
      setTimeout(() => {
        navigate('/dashboard');
      }, 2000);
    } catch (error) {
      console.error('Onboarding failed:', error);
      setLoading(false);
    }
  };

  if (step === 3) {
    return (
      <div className="min-h-screen bg-[#09090b] flex items-center justify-center p-4">
        <div className="text-center">
          <CheckCircle2 className="w-20 h-20 text-primary mx-auto mb-6" />
          <h1 className="text-4xl font-heading font-bold uppercase tracking-tight text-white mb-4">
            YOUR SYSTEM IS BUILT
          </h1>
          <p className="text-zinc-400 font-body">Redirecting to dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#09090b] p-4">
      <div className="max-w-2xl mx-auto pt-8">
        <div className="flex items-center gap-3 mb-8">
          <Flame className="w-8 h-8 text-primary" />
          <h1 className="text-3xl font-heading font-bold uppercase tracking-tight text-white">FORGE</h1>
        </div>

        <div className="mb-8">
          <div className="flex gap-2 mb-2">
            <div className={`h-1 flex-1 rounded ${step >= 1 ? 'bg-primary' : 'bg-zinc-800'}`}></div>
            <div className={`h-1 flex-1 rounded ${step >= 2 ? 'bg-primary' : 'bg-zinc-800'}`}></div>
          </div>
          <p className="text-zinc-400 text-sm font-mono">STEP {step}/2</p>
        </div>

        {step === 1 && (
          <div>
            <h2 className="text-2xl font-heading font-bold uppercase tracking-tight text-white mb-2">
              WHAT DO YOU WANT TO IMPROVE?
            </h2>
            <p className="text-zinc-400 font-body mb-6">Choose 3-5 areas to focus on</p>

            <div className="space-y-3 mb-6">
              {availablePillars.map((pillar) => (
                <div
                  key={pillar}
                  data-testid={`pillar-${pillar.toLowerCase().replace(/\//g, '-').replace(/\s+/g, '-')}`}
                  onClick={() => togglePillar(pillar)}
                  className={`p-4 border rounded-md cursor-pointer transition-all duration-200 ${
                    selectedPillars.includes(pillar)
                      ? 'bg-primary/10 border-primary'
                      : 'bg-zinc-950 border-zinc-800 hover:border-zinc-600'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <Checkbox
                      checked={selectedPillars.includes(pillar)}
                      className="border-zinc-600"
                    />
                    <span className="font-body text-white">{pillar}</span>
                  </div>
                </div>
              ))}
            </div>

            <div className="text-zinc-400 text-sm font-mono mb-6">
              Selected: {selectedPillars.length}/5
            </div>

            <Button
              data-testid="onboarding-next-btn"
              onClick={handleNext}
              disabled={selectedPillars.length < 3 || selectedPillars.length > 5}
              className="w-full bg-primary text-primary-foreground hover:bg-primary/90 font-heading uppercase tracking-wide font-bold"
            >
              Next
            </Button>
          </div>
        )}

        {step === 2 && (
          <div>
            <h2 className="text-2xl font-heading font-bold uppercase tracking-tight text-white mb-2">
              SET WEEKLY TARGETS
            </h2>
            <p className="text-zinc-400 font-body mb-6">How many sessions per week for each area?</p>

            <div className="space-y-4 mb-6">
              {selectedPillars.map((pillar) => (
                <div key={pillar} className="bg-zinc-950 border border-zinc-800 rounded-md p-4">
                  <label className="block text-white font-body mb-2">{pillar}</label>
                  <div className="flex items-center gap-3">
                    <Input
                      data-testid={`target-${pillar.toLowerCase().replace(/\//g, '-').replace(/\s+/g, '-')}`}
                      type="number"
                      placeholder="5"
                      value={targets[pillar] || ''}
                      onChange={(e) => handleTargetChange(pillar, e.target.value)}
                      className="bg-zinc-900 border-zinc-800 text-white font-mono focus:ring-2 focus:ring-primary"
                    />
                    <span className="text-zinc-400 font-body whitespace-nowrap">sessions/week</span>
                  </div>
                  <p className="text-zinc-500 text-xs font-body mt-2">
                    Example: 5 workouts, 6 study sessions, 3 skill practices
                  </p>
                </div>
              ))}
            </div>

            <div className="flex gap-3">
              <Button
                data-testid="onboarding-back-btn"
                onClick={() => setStep(1)}
                variant="ghost"
                className="flex-1 font-heading uppercase tracking-wide"
              >
                Back
              </Button>
              <Button
                data-testid="onboarding-complete-btn"
                onClick={handleComplete}
                disabled={loading || selectedPillars.some(p => !targets[p] || targets[p] <= 0)}
                className="flex-1 bg-primary text-primary-foreground hover:bg-primary/90 font-heading uppercase tracking-wide font-bold"
              >
                {loading ? 'Building...' : 'Complete'}
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};