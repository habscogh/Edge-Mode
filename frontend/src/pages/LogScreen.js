import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { CheckCircle2, ArrowLeft, Clock, Pencil, Trash2, X, StickyNote, WifiOff } from 'lucide-react';
import { toast } from 'sonner';
import { MilestoneCelebration, checkMilestoneHit } from '../components/MilestoneCelebration';
import { OfflineIndicator } from '../components/OfflineIndicator';
import { PushNotificationPrompt } from '../components/PushNotificationPrompt';
import { useOfflineSync } from '../hooks/useOfflineSync';
import { usePushNotifications } from '../hooks/usePushNotifications';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export const LogScreen = () => {
  const { user, fetchUser } = useAuth();
  const { isOnline, saveOffline, pendingCount } = useOfflineSync();
  const { isSupported, isSubscribed, subscribe } = usePushNotifications();
  const [pillars, setPillars] = useState([]);
  const [selectedPillar, setSelectedPillar] = useState('');
  const [minutes, setMinutes] = useState('30');
  const [note, setNote] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [todaySessions, setTodaySessions] = useState([]);
  const [editingSession, setEditingSession] = useState(null);
  const [editMinutes, setEditMinutes] = useState('');
  const [editPillar, setEditPillar] = useState('');
  const [editNote, setEditNote] = useState('');
  const [deleteConfirm, setDeleteConfirm] = useState(null);
  const [milestoneToShow, setMilestoneToShow] = useState(null);
  const [showPushPrompt, setShowPushPrompt] = useState(false);
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
      // Send client's local date to get accurate "today" sessions
      const localDate = new Date().toISOString().split('T')[0];
      const response = await axios.get(`${API}/sessions/today?local_date=${localDate}`);
      setTodaySessions(response.data);
    } catch (error) {
      console.error('Failed to fetch today sessions:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Store previous streak to check for milestones
    const previousStreak = user?.current_streak || 0;
    
    // Get client's local date
    const localDate = new Date().toISOString().split('T')[0];
    
    // Prepare session data
    const sessionData = {
      pillar: selectedPillar,
      minutes_spent: parseInt(minutes) || 30,
      note: note || null,
      local_date: localDate
    };
    
    setLoading(true);

    try {
      // If offline, save locally
      if (!isOnline) {
        await saveOffline(sessionData);
        toast.success(
          <div className="flex items-center gap-2">
            <WifiOff className="w-4 h-4" />
            <span>Saved offline! Will sync when online.</span>
          </div>
        );
        setSuccess(true);
        setNote('');
        setTimeout(() => {
          setSuccess(false);
          navigate('/dashboard');
        }, 1500);
        return;
      }
      
      const response = await axios.post(`${API}/sessions/complete`, sessionData);
      
      // Check for newly earned badges and show toast notifications
      if (response.data.new_badges && response.data.new_badges.length > 0) {
        response.data.new_badges.forEach(badge => {
          toast.success(
            <div className="flex items-center gap-3">
              <span className="text-2xl">{badge.icon}</span>
              <div>
                <div className="font-bold">Badge Unlocked!</div>
                <div className="text-sm opacity-80">{badge.name}</div>
              </div>
            </div>,
            { duration: 5000 }
          );
        });
      }
      
      setSuccess(true);
      setNote('');
      fetchTodaySessions();
      
      // Refresh user data and check for milestone
      if (fetchUser) await fetchUser();
      
      // Get updated streak
      const updatedUserRes = await axios.get(`${API}/auth/me`);
      const newStreak = updatedUserRes.data?.current_streak || 0;
      
      const milestone = checkMilestoneHit(previousStreak, newStreak);
      if (milestone) {
        // Show milestone celebration instead of navigating away immediately
        setSuccess(false);
        setMilestoneToShow({ milestone, streak: newStreak });
      } else {
        setTimeout(() => {
          setSuccess(false);
          navigate('/dashboard');
        }, 1500);
      }
    } catch (error) {
      console.error('Failed to log session:', error);
      
      // If network error, save offline
      if (!navigator.onLine || error.message === 'Network Error') {
        try {
          await saveOffline(sessionData);
          toast.success(
            <div className="flex items-center gap-2">
              <WifiOff className="w-4 h-4" />
              <span>Saved offline! Will sync when online.</span>
            </div>
          );
          setSuccess(true);
          setNote('');
          setTimeout(() => {
            setSuccess(false);
            navigate('/dashboard');
          }, 1500);
        } catch (offlineError) {
          toast.error('Failed to save session');
        }
      } else {
        toast.error('Failed to log session');
      }
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

  const handleEditSession = (session) => {
    setEditingSession(session);
    setEditMinutes(session.minutes_spent.toString());
    setEditPillar(session.pillar);
    setEditNote(session.note || '');
  };

  const handleSaveEdit = async () => {
    if (!editingSession) return;
    
    setLoading(true);
    try {
      await axios.put(`${API}/sessions/edit`, {
        session_id: editingSession.id,
        minutes_spent: parseInt(editMinutes) || 30,
        pillar: editPillar,
        note: editNote || null
      });
      toast.success('Session updated successfully');
      setEditingSession(null);
      fetchTodaySessions();
    } catch (error) {
      console.error('Failed to edit session:', error);
      toast.error('Failed to update session');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteSession = async (sessionId) => {
    setLoading(true);
    try {
      await axios.delete(`${API}/sessions/${sessionId}`);
      toast.success('Session deleted');
      setDeleteConfirm(null);
      fetchTodaySessions();
    } catch (error) {
      console.error('Failed to delete session:', error);
      toast.error('Failed to delete session');
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="min-h-screen bg-[#09090b] p-4 pb-24">
      {/* Offline Indicator */}
      <OfflineIndicator />
      
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

          <div className="bg-zinc-950 border border-zinc-800 rounded-md p-6">
            <label className="block text-white font-body mb-3">
              <StickyNote className="w-4 h-4 inline mr-2 text-yellow-500" />
              Add Note (Optional)
            </label>
            <textarea
              data-testid="session-note-input"
              value={note}
              onChange={(e) => setNote(e.target.value)}
              placeholder="What did you work on? Any reflections?"
              className="w-full bg-zinc-900 border border-zinc-800 rounded-md p-3 text-white font-body focus:ring-2 focus:ring-primary focus:outline-none resize-none h-20"
            />
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

        {/* Today's Sessions List with Edit/Delete */}
        {todaySessions.length > 0 && (
          <div className="mt-8">
            <h2 className="text-xl font-heading font-bold uppercase text-white mb-4">
              Today's Sessions
            </h2>
            <div className="space-y-3">
              {todaySessions.map((session) => (
                <div
                  key={session.id}
                  data-testid={`session-item-${session.id}`}
                  className="bg-zinc-950 border border-zinc-800 rounded-md p-4"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="text-white font-body font-medium">{session.pillar}</div>
                      <div className="flex items-center gap-3 text-zinc-400 text-sm">
                        <span className="font-mono">{session.minutes_spent} min</span>
                        <span>•</span>
                        <span>{formatTime(session.timestamp)}</span>
                      </div>
                      {session.note && (
                        <div className="mt-2 flex items-start gap-2 text-zinc-400 text-sm">
                          <StickyNote className="w-4 h-4 mt-0.5 text-yellow-500 flex-shrink-0" />
                          <span className="italic">{session.note}</span>
                        </div>
                      )}
                    </div>
                    <div className="flex items-center gap-2">
                      <button
                        data-testid={`edit-session-${session.id}`}
                        onClick={() => handleEditSession(session)}
                        className="p-2 text-zinc-400 hover:text-primary hover:bg-zinc-800 rounded-md transition-colors"
                      >
                        <Pencil className="w-4 h-4" />
                      </button>
                      <button
                        data-testid={`delete-session-${session.id}`}
                        onClick={() => setDeleteConfirm(session.id)}
                        className="p-2 text-zinc-400 hover:text-red-500 hover:bg-zinc-800 rounded-md transition-colors"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Edit Modal */}
        {editingSession && (
          <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
            <div className="bg-zinc-950 border border-zinc-800 rounded-lg w-full max-w-md p-6 max-h-[90vh] overflow-y-auto">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-heading font-bold uppercase text-white">Edit Session</h3>
                <button
                  data-testid="close-edit-modal"
                  onClick={() => setEditingSession(null)}
                  className="text-zinc-400 hover:text-white"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-zinc-400 text-sm font-body mb-2">Activity</label>
                  <select
                    data-testid="edit-pillar-select"
                    value={editPillar}
                    onChange={(e) => setEditPillar(e.target.value)}
                    className="w-full bg-zinc-900 border border-zinc-800 rounded-md p-3 text-white font-body focus:ring-2 focus:ring-primary focus:outline-none"
                  >
                    {pillars.map((pillar) => (
                      <option key={pillar.id} value={pillar.pillar_name}>
                        {pillar.pillar_name}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-zinc-400 text-sm font-body mb-2">Minutes</label>
                  <Input
                    data-testid="edit-minutes-input"
                    type="number"
                    value={editMinutes}
                    onChange={(e) => setEditMinutes(e.target.value)}
                    min="1"
                    className="bg-zinc-900 border-zinc-800 text-white font-mono text-xl focus:ring-2 focus:ring-primary"
                  />
                </div>

                <div>
                  <label className="block text-zinc-400 text-sm font-body mb-2">Note (optional)</label>
                  <textarea
                    data-testid="edit-note-input"
                    value={editNote}
                    onChange={(e) => setEditNote(e.target.value)}
                    placeholder="Add a note about this session..."
                    className="w-full bg-zinc-900 border border-zinc-800 rounded-md p-3 text-white font-body focus:ring-2 focus:ring-primary focus:outline-none resize-none h-20"
                  />
                </div>

                <div className="flex gap-3 pt-4">
                  <Button
                    data-testid="cancel-edit-btn"
                    variant="outline"
                    onClick={() => setEditingSession(null)}
                    className="flex-1 border-zinc-700 text-zinc-300 hover:bg-zinc-800"
                  >
                    Cancel
                  </Button>
                  <Button
                    data-testid="save-edit-btn"
                    onClick={handleSaveEdit}
                    disabled={loading}
                    className="flex-1 bg-primary text-primary-foreground hover:bg-primary/90"
                  >
                    {loading ? 'Saving...' : 'Save Changes'}
                  </Button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Delete Confirmation Modal */}
        {deleteConfirm && (
          <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
            <div className="bg-zinc-950 border border-zinc-800 rounded-lg w-full max-w-sm p-6">
              <h3 className="text-xl font-heading font-bold uppercase text-white mb-2">Delete Session?</h3>
              <p className="text-zinc-400 font-body mb-6">
                This action cannot be undone. The session will be permanently removed.
              </p>
              <div className="flex gap-3">
                <Button
                  data-testid="cancel-delete-btn"
                  variant="outline"
                  onClick={() => setDeleteConfirm(null)}
                  className="flex-1 border-zinc-700 text-zinc-300 hover:bg-zinc-800"
                >
                  Cancel
                </Button>
                <Button
                  data-testid="confirm-delete-btn"
                  onClick={() => handleDeleteSession(deleteConfirm)}
                  disabled={loading}
                  className="flex-1 bg-red-600 text-white hover:bg-red-700"
                >
                  {loading ? 'Deleting...' : 'Delete'}
                </Button>
              </div>
            </div>
          </div>
        )}
        
        {/* Milestone Celebration Modal */}
        {milestoneToShow && (
          <MilestoneCelebration
            milestone={milestoneToShow.milestone}
            streak={milestoneToShow.streak}
            onClose={() => {
              setMilestoneToShow(null);
              navigate('/dashboard');
            }}
          />
        )}
      </div>
    </div>
  );
};