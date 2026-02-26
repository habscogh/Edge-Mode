import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { CheckCircle2, ArrowLeft, Clock, Pencil, Trash2, X } from 'lucide-react';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export const LogScreen = () => {
  const [pillars, setPillars] = useState([]);
  const [selectedPillar, setSelectedPillar] = useState('');
  const [minutes, setMinutes] = useState('30');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [todaySessions, setTodaySessions] = useState([]);
  const [editingSession, setEditingSession] = useState(null);
  const [editMinutes, setEditMinutes] = useState('');
  const [editPillar, setEditPillar] = useState('');
  const [deleteConfirm, setDeleteConfirm] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchPillars();
    fetchTodaySessions();
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

  const fetchTodaySessions = async () => {
    try {
      const response = await axios.get(`${API}/sessions/today`);
      setTodaySessions(response.data);
    } catch (error) {
      console.error('Failed to fetch today sessions:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      await axios.post(`${API}/sessions/complete`, {
        pillar: selectedPillar,
        minutes_spent: parseInt(minutes) || 30
      });
      setSuccess(true);
      fetchTodaySessions();
      setTimeout(() => {
        setSuccess(false);
        navigate('/dashboard');
      }, 1500);
    } catch (error) {
      console.error('Failed to log session:', error);
      alert('Failed to log session');
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="min-h-screen bg-[#09090b] flex items-center justify-center p-4">
        <div className="text-center">
          <CheckCircle2 className="w-20 h-20 text-primary mx-auto mb-4" />
          <h2 className="text-2xl font-heading font-bold uppercase text-white mb-2">Session Logged!</h2>
          <p className="text-zinc-400 font-body">Keep building your streak</p>
        </div>
      </div>
    );
  }

  const getPillarSessions = (pillarName) => {
    return todaySessions.filter(s => s.pillar === pillarName).length;
  };

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

        <h1 className="text-3xl font-heading font-bold uppercase tracking-tight text-white mb-2">
          Log Session
        </h1>
        <p className="text-zinc-400 font-body mb-6">Mark your completed session</p>

        {todaySessions.length > 0 && (
          <div className="bg-primary/10 border border-primary/30 rounded-md p-4 mb-6">
            <div className="text-primary font-body font-bold mb-1">Today's Progress</div>
            <div className="text-white font-mono text-2xl">{todaySessions.length} sessions completed</div>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="bg-zinc-950 border border-zinc-800 rounded-md p-6">
            <label className="block text-white font-body mb-3">Select Activity</label>
            <div className="grid grid-cols-1 gap-2">
              {pillars.map((pillar) => {
                const sessionsToday = getPillarSessions(pillar.pillar_name);
                return (
                  <div
                    key={pillar.id}
                    data-testid={`select-pillar-${pillar.pillar_name.toLowerCase().replace(/\//g, '-').replace(/\s+/g, '-')}`}
                    onClick={() => setSelectedPillar(pillar.pillar_name)}
                    className={`p-4 border rounded-md cursor-pointer transition-all duration-200 ${
                      selectedPillar === pillar.pillar_name
                        ? 'bg-primary/10 border-primary'
                        : 'bg-zinc-900 border-zinc-800 hover:border-zinc-600'
                    }`}
                  >
                    <div className="flex justify-between items-center">
                      <div>
                        <span className="font-body text-white">{pillar.pillar_name}</span>
                        {sessionsToday > 0 && (
                          <span className="ml-2 text-xs font-mono text-primary">✓ {sessionsToday} today</span>
                        )}
                      </div>
                      <span className="text-zinc-400 text-sm font-mono">
                        {pillar.weekly_target_sessions} sessions/week
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="bg-zinc-950 border border-zinc-800 rounded-md p-6">
            <label className="block text-white font-body mb-3">Time Spent (Optional)</label>
            <div className="flex items-center gap-3">
              <Clock className="w-5 h-5 text-zinc-500" />
              <Input
                data-testid="minutes-input"
                type="number"
                placeholder="30"
                value={minutes}
                onChange={(e) => setMinutes(e.target.value)}
                min="1"
                className="bg-zinc-900 border-zinc-800 text-white font-mono text-2xl focus:ring-2 focus:ring-primary"
              />
              <span className="text-zinc-400 font-body whitespace-nowrap">minutes</span>
            </div>
            <p className="text-zinc-500 text-xs font-body mt-2">Track time for better insights</p>
          </div>

          <Button
            data-testid="submit-log-btn"
            type="submit"
            disabled={loading || !selectedPillar}
            className="w-full bg-primary text-primary-foreground hover:bg-primary/90 font-heading uppercase tracking-wide font-bold text-lg py-6"
          >
            {loading ? 'Saving...' : 'Complete Session'}
          </Button>
        </form>
      </div>
    </div>
  );
};