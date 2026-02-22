import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { CheckCircle2, ArrowLeft } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export const LogScreen = () => {
  const [pillars, setPillars] = useState([]);
  const [selectedPillar, setSelectedPillar] = useState('');
  const [minutes, setMinutes] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    fetchPillars();
  }, []);

  const fetchPillars = async () => {
    try {
      const response = await axios.get(`${API}/users/pillars`);
      setPillars(response.data);
      if (response.data.length > 0) {
        setSelectedPillar(response.data[0].pillar_name);
      }
    } catch (error) {
      console.error('Failed to fetch pillars:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      await axios.post(`${API}/logs`, {
        pillar: selectedPillar,
        minutes_logged: parseInt(minutes)
      });
      setSuccess(true);
      setMinutes('');
      setTimeout(() => {
        setSuccess(false);
        navigate('/dashboard');
      }, 1500);
    } catch (error) {
      console.error('Failed to log activity:', error);
      alert('Failed to log activity');
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="min-h-screen bg-[#09090b] flex items-center justify-center p-4">
        <div className="text-center">
          <CheckCircle2 className="w-20 h-20 text-primary mx-auto mb-4" />
          <h2 className="text-2xl font-heading font-bold uppercase text-white">Logged!</h2>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#09090b] p-4 pb-24">
      <div className="max-w-2xl mx-auto pt-6">
        <button
          data-testid="back-btn"
          onClick={() => navigate('/dashboard')}
          className="flex items-center gap-2 text-zinc-400 hover:text-white mb-6 transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
          <span className="font-body">Back</span>
        </button>

        <h1 className="text-3xl font-heading font-bold uppercase tracking-tight text-white mb-6">
          Log Activity
        </h1>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="bg-zinc-950 border border-zinc-800 rounded-md p-6">
            <label className="block text-white font-body mb-3">Select Pillar</label>
            <div className="grid grid-cols-1 gap-2">
              {pillars.map((pillar) => (
                <div
                  key={pillar.id}
                  data-testid={`select-pillar-${pillar.pillar_name.toLowerCase().replace(/\//g, '-')}`}
                  onClick={() => setSelectedPillar(pillar.pillar_name)}
                  className={`p-4 border rounded-md cursor-pointer transition-all duration-200 ${
                    selectedPillar === pillar.pillar_name
                      ? 'bg-primary/10 border-primary'
                      : 'bg-zinc-900 border-zinc-800 hover:border-zinc-600'
                  }`}
                >
                  <div className="flex justify-between items-center">
                    <span className="font-body text-white">{pillar.pillar_name}</span>
                    <span className="text-zinc-400 text-sm font-mono">
                      {pillar.weekly_target_minutes} min/week
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-zinc-950 border border-zinc-800 rounded-md p-6">
            <label className="block text-white font-body mb-3">Minutes Completed</label>
            <Input
              data-testid="minutes-input"
              type="number"
              placeholder="30"
              value={minutes}
              onChange={(e) => setMinutes(e.target.value)}
              required
              min="1"
              className="bg-zinc-900 border-zinc-800 text-white font-mono text-2xl focus:ring-2 focus:ring-primary"
            />
          </div>

          <Button
            data-testid="submit-log-btn"
            type="submit"
            disabled={loading || !minutes || !selectedPillar}
            className="w-full bg-primary text-primary-foreground hover:bg-primary/90 font-heading uppercase tracking-wide font-bold text-lg py-6"
          >
            {loading ? 'Saving...' : 'Save Log'}
          </Button>
        </form>
      </div>
    </div>
  );
};