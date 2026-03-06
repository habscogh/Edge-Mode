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
  const [isCompleting, setIsCompleting] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    // Don't check for existing onboarding if we're in the middle of completing it
    if (!isCompleting) {
      checkExistingOnboarding();
    }
    fetchPillars();
  }, []);

  const checkExistingOnboarding = async () => {
    try {
      const response = await axios.get(`${API}/users/pillars`);
      if (response.data && response.data.length > 0) {
        // User has already completed onboarding
        console.log('User already completed onboarding, redirecting to dashboard');
        navigate('/dashboard');
      }
    } catch (error) {
      console.log('No existing onboarding found');
    }
  };

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
    if (value === '') {
      setTargets({ ...targets, [pillar]: '' });
    } else {
      const numValue = parseInt(value);
      setTargets({ ...targets, [pillar]: isNaN(numValue) ? '' : numValue });
    }
  };

  const isStep2Valid = () => {
    const valid = selectedPillars.every(p => {
      const targetValue = targets[p];
      return targetValue !== '' && targetValue !== null && targetValue !== undefined && targetValue > 0;
    });
    console.log('Step 2 validation:', { selectedPillars, targets, valid });
    return valid;
  };

  const handleNext = () => {
    if (step === 1 && selectedPillars.length >= 3 && selectedPillars.length <= 5) {
      // Reset targets completely for selected pillars to ensure empty fields
      const freshTargets = {};
      selectedPillars.forEach(pillar => {
        freshTargets[pillar] = '';
      });
      setTargets(freshTargets);
      setStep(2);
    }
  };

  const handleComplete = async () => {
    console.log('=== STARTING ONBOARDING COMPLETE ===');
    setIsCompleting(true);
    setLoading(true);
    
    try {
      const pillars = selectedPillars.map(pillar => ({
        pillar_name: pillar,
        weekly_target_sessions: targets[pillar] || 5
      }));

      console.log('Sending pillars:', pillars);
      
      const response = await axios.post(`${API}/onboarding/complete`, { pillars });
      console.log('✓ Onboarding response:', response.data);
      
      // Show success screen
      setStep(3);
      
      // Wait 2 seconds then navigate
      console.log('Waiting 2 seconds before redirect...');
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      console.log('Navigating to dashboard...');
      navigate('/dashboard', { replace: true });
      
    } catch (error) {
      console.error('✗ Onboarding failed:', error);
      console.error('Error details:', error.response?.data);
      
      // If onboarding already completed, just go to dashboard
      if (error.response?.status === 400) {
        const errorMsg = JSON.stringify(error.response?.data);
        if (errorMsg.includes('already completed')) {
          console.log('Onboarding already completed, redirecting to dashboard');
          navigate('/dashboard', { replace: true });
          return;
        }
      }
      
      alert('Failed to complete onboarding. Please try again or contact support.');
      setLoading(false);
      setIsCompleting(false);
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
          <h1 className="text-3xl font-heading font-bold uppercase tracking-tight text-white">EDGE MODE</h1>
        </div>

        <div className="mb-8">
          {/* Progress Bar */}
          <div className="relative mb-4">
            <div className="flex justify-between mb-2">
              <div className={`flex flex-col items-center ${step >= 1 ? 'text-primary' : 'text-zinc-600'}`}>
                <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold text-lg mb-1 ${
                  step >= 1 ? 'bg-primary text-primary-foreground' : 'bg-zinc-800 text-zinc-500'
                }`}>
                  {step > 1 ? <CheckCircle2 className="w-5 h-5" /> : '1'}
                </div>
                <span className="text-xs font-body">Choose Areas</span>
              </div>
              <div className={`flex flex-col items-center ${step >= 2 ? 'text-primary' : 'text-zinc-600'}`}>
                <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold text-lg mb-1 ${
                  step >= 2 ? 'bg-primary text-primary-foreground' : 'bg-zinc-800 text-zinc-500'
                }`}>
                  {step > 2 ? <CheckCircle2 className="w-5 h-5" /> : '2'}
                </div>
                <span className="text-xs font-body">Set Targets</span>
              </div>
            </div>
            {/* Connecting line */}
            <div className="absolute top-5 left-12 right-12 h-0.5 bg-zinc-800 -z-10">
              <div 
                className="h-full bg-primary transition-all duration-500" 
                style={{ width: step >= 2 ? '100%' : '0%' }}
              />
            </div>
          </div>
          <p className="text-center text-zinc-400 text-sm font-mono">STEP {step} OF 2</p>
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
            <p className="text-zinc-400 font-body mb-2">How many sessions per week for each area?</p>
            <p className="text-primary text-sm font-body mb-6 bg-primary/10 border border-primary/30 rounded-md px-3 py-2">
              💡 1 session = 30 minutes of focused work
            </p>

            <div className="space-y-4 mb-6">
              {selectedPillars.map((pillar) => (
                <div key={pillar} className="bg-zinc-950 border border-zinc-800 rounded-md p-4">
                  <label className="block text-white font-body mb-2">{pillar}</label>
                  <div className="flex items-center gap-3">
                    <Input
                      data-testid={`target-${pillar.toLowerCase().replace(/\//g, '-').replace(/\s+/g, '-')}`}
                      type="number"
                      placeholder=""
                      value={targets[pillar] === '' ? '' : targets[pillar]}
                      onChange={(e) => handleTargetChange(pillar, e.target.value)}
                      className="bg-zinc-900 border-zinc-800 text-white font-mono focus:ring-2 focus:ring-primary"
                    />
                    <span className="text-zinc-400 font-body whitespace-nowrap">sessions/week</span>
                  </div>
                  <p className="text-zinc-500 text-xs font-body mt-2">
                    Example: 5 sessions = 2.5 hours/week
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
                onClick={() => {
                  console.log('Complete button clicked!', { loading, valid: isStep2Valid() });
                  handleComplete();
                }}
                disabled={loading || !isStep2Valid()}
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