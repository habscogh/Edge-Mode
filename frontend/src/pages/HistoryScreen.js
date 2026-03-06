import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Calendar, Clock, ChevronLeft, ChevronRight, Pencil, Trash2, X, StickyNote } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { toast } from 'sonner';
import { format, parseISO, startOfMonth, endOfMonth, eachDayOfInterval, isSameMonth, isSameDay, addMonths, subMonths } from 'date-fns';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export const HistoryScreen = () => {
  const navigate = useNavigate();
  const [sessions, setSessions] = useState([]);
  const [pillars, setPillars] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentMonth, setCurrentMonth] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState(null);
  const [editingSession, setEditingSession] = useState(null);
  const [editMinutes, setEditMinutes] = useState('');
  const [editPillar, setEditPillar] = useState('');
  const [editNote, setEditNote] = useState('');
  const [deleteConfirm, setDeleteConfirm] = useState(null);
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const handleBack = () => navigate(-1);

  const fetchData = async () => {
    try {
      const [sessionsRes, pillarsRes] = await Promise.all([
        axios.get(`${API}/sessions/history?days=90`),
        axios.get(`${API}/users/pillars`)
      ]);
      setSessions(sessionsRes.data);
      setPillars(pillarsRes.data);
    } catch (error) {
      console.error('Failed to fetch history:', error);
      toast.error('Failed to load session history');
    } finally {
      setLoading(false);
    }
  };

  const getSessionsForDate = (date) => {
    const dateStr = format(date, 'yyyy-MM-dd');
    return sessions.filter(s => s.date === dateStr);
  };

  const getDaysWithSessions = () => {
    const days = new Set();
    sessions.forEach(s => days.add(s.date));
    return days;
  };

  const handleEditSession = (session) => {
    setEditingSession(session);
    setEditMinutes(session.minutes_spent.toString());
    setEditPillar(session.pillar);
    setEditNote(session.note || '');
  };

  const handleSaveEdit = async () => {
    if (!editingSession) return;
    
    setActionLoading(true);
    try {
      await axios.put(`${API}/sessions/edit`, {
        session_id: editingSession.id,
        minutes_spent: parseInt(editMinutes) || 30,
        pillar: editPillar,
        note: editNote || null
      });
      toast.success('Session updated');
      setEditingSession(null);
      fetchData();
    } catch (error) {
      console.error('Failed to edit session:', error);
      toast.error('Failed to update session');
    } finally {
      setActionLoading(false);
    }
  };

  const handleDeleteSession = async (sessionId) => {
    setActionLoading(true);
    try {
      await axios.delete(`${API}/sessions/${sessionId}`);
      toast.success('Session deleted');
      setDeleteConfirm(null);
      fetchData();
    } catch (error) {
      console.error('Failed to delete session:', error);
      toast.error('Failed to delete session');
    } finally {
      setActionLoading(false);
    }
  };

  const renderCalendar = () => {
    const monthStart = startOfMonth(currentMonth);
    const monthEnd = endOfMonth(currentMonth);
    const days = eachDayOfInterval({ start: monthStart, end: monthEnd });
    const daysWithSessions = getDaysWithSessions();
    
    // Get day of week for first day (0 = Sunday)
    const startDay = monthStart.getDay();
    const emptyDays = Array(startDay).fill(null);

    return (
      <div className="bg-zinc-950 border border-zinc-800 rounded-md p-4 mb-6">
        <div className="flex items-center justify-between mb-4">
          <button
            onClick={() => setCurrentMonth(subMonths(currentMonth, 1))}
            className="p-2 text-zinc-400 hover:text-white hover:bg-zinc-800 rounded-md transition-colors"
          >
            <ChevronLeft className="w-5 h-5" />
          </button>
          <h3 className="text-white font-heading font-bold uppercase">
            {format(currentMonth, 'MMMM yyyy')}
          </h3>
          <button
            onClick={() => setCurrentMonth(addMonths(currentMonth, 1))}
            className="p-2 text-zinc-400 hover:text-white hover:bg-zinc-800 rounded-md transition-colors"
          >
            <ChevronRight className="w-5 h-5" />
          </button>
        </div>

        <div className="grid grid-cols-7 gap-1 mb-2">
          {['S', 'M', 'T', 'W', 'T', 'F', 'S'].map((day, i) => (
            <div key={i} className="text-center text-zinc-500 text-xs font-body py-2">
              {day}
            </div>
          ))}
        </div>

        <div className="grid grid-cols-7 gap-1">
          {emptyDays.map((_, i) => (
            <div key={`empty-${i}`} className="aspect-square" />
          ))}
          {days.map((day) => {
            const dateStr = format(day, 'yyyy-MM-dd');
            const hasSessions = daysWithSessions.has(dateStr);
            const isSelected = selectedDate && isSameDay(day, selectedDate);
            const isToday = isSameDay(day, new Date());
            const sessionsCount = getSessionsForDate(day).length;

            return (
              <button
                key={dateStr}
                onClick={() => setSelectedDate(isSelected ? null : day)}
                className={`aspect-square rounded-md flex flex-col items-center justify-center text-sm font-mono transition-all relative ${
                  isSelected
                    ? 'bg-primary text-primary-foreground'
                    : hasSessions
                    ? 'bg-primary/20 text-primary hover:bg-primary/30'
                    : isToday
                    ? 'bg-zinc-800 text-white'
                    : 'text-zinc-400 hover:bg-zinc-800'
                }`}
              >
                {format(day, 'd')}
                {hasSessions && !isSelected && (
                  <span className="absolute bottom-1 w-1 h-1 bg-primary rounded-full" />
                )}
                {isSelected && sessionsCount > 0 && (
                  <span className="text-[10px]">{sessionsCount}</span>
                )}
              </button>
            );
          })}
        </div>
      </div>
    );
  };

  const renderSelectedDateSessions = () => {
    if (!selectedDate) return null;
    
    const dateSessions = getSessionsForDate(selectedDate);
    
    return (
      <div className="bg-zinc-950 border border-zinc-800 rounded-md p-4 mb-6">
        <h3 className="text-white font-heading font-bold uppercase mb-4">
          {format(selectedDate, 'EEEE, MMM d')}
        </h3>
        
        {dateSessions.length === 0 ? (
          <p className="text-zinc-500 font-body text-sm">No sessions logged this day</p>
        ) : (
          <div className="space-y-3">
            {dateSessions.map((session) => (
              <div
                key={session.id}
                className="bg-zinc-900 border border-zinc-800 rounded-md p-3"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="text-white font-body font-medium">{session.pillar}</div>
                    <div className="flex items-center gap-3 text-zinc-400 text-sm mt-1">
                      <span className="font-mono">{session.minutes_spent} min</span>
                      <span>•</span>
                      <span>{format(parseISO(session.timestamp), 'h:mm a')}</span>
                    </div>
                    {session.note && (
                      <div className="mt-2 flex items-start gap-2 text-zinc-400 text-sm">
                        <StickyNote className="w-4 h-4 mt-0.5 text-yellow-500" />
                        <span className="italic">{session.note}</span>
                      </div>
                    )}
                  </div>
                  <div className="flex items-center gap-1">
                    <button
                      onClick={() => handleEditSession(session)}
                      className="p-2 text-zinc-400 hover:text-primary hover:bg-zinc-800 rounded-md transition-colors"
                    >
                      <Pencil className="w-4 h-4" />
                    </button>
                    <button
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
        )}
      </div>
    );
  };

  const renderRecentSessions = () => {
    const recentSessions = sessions.slice(0, 10);
    
    if (recentSessions.length === 0) {
      return (
        <div className="bg-zinc-950 border border-zinc-800 rounded-md p-6 text-center">
          <Calendar className="w-12 h-12 text-zinc-600 mx-auto mb-3" />
          <p className="text-zinc-400 font-body">No sessions logged yet</p>
          <Button
            onClick={() => navigate('/log')}
            className="mt-4 bg-primary text-primary-foreground"
          >
            Log Your First Session
          </Button>
        </div>
      );
    }

    return (
      <div className="space-y-3">
        <h3 className="text-white font-heading font-bold uppercase">Recent Sessions</h3>
        {recentSessions.map((session) => (
          <div
            key={session.id}
            className="bg-zinc-950 border border-zinc-800 rounded-md p-3"
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <span className="text-white font-body font-medium">{session.pillar}</span>
                  <span className="text-zinc-600">•</span>
                  <span className="text-zinc-400 text-sm font-mono">
                    {format(parseISO(session.date), 'MMM d')}
                  </span>
                </div>
                <div className="flex items-center gap-3 text-zinc-500 text-sm mt-1">
                  <Clock className="w-3 h-3" />
                  <span className="font-mono">{session.minutes_spent} min</span>
                </div>
                {session.note && (
                  <div className="mt-2 flex items-start gap-2 text-zinc-400 text-sm">
                    <StickyNote className="w-4 h-4 mt-0.5 text-yellow-500" />
                    <span className="italic line-clamp-1">{session.note}</span>
                  </div>
                )}
              </div>
              <div className="flex items-center gap-1">
                <button
                  onClick={() => handleEditSession(session)}
                  className="p-2 text-zinc-400 hover:text-primary hover:bg-zinc-800 rounded-md transition-colors"
                >
                  <Pencil className="w-4 h-4" />
                </button>
                <button
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
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-[#09090b]">
        <div className="text-zinc-400 font-mono">Loading...</div>
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

        <div className="flex items-center gap-3 mb-6">
          <Calendar className="w-8 h-8 text-primary" />
          <div>
            <h1 className="text-3xl font-heading font-bold uppercase tracking-tight text-white">
              History
            </h1>
            <p className="text-zinc-400 font-body">View and manage past sessions</p>
          </div>
        </div>

        <div className="bg-primary/10 border border-primary/30 rounded-md p-4 mb-6">
          <div className="text-primary font-body font-bold mb-1">Total Sessions</div>
          <div className="text-white font-mono text-2xl">{sessions.length}</div>
        </div>

        {renderCalendar()}
        {renderSelectedDateSessions()}
        {!selectedDate && renderRecentSessions()}

        {/* Edit Modal */}
        {editingSession && (
          <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
            <div className="bg-zinc-950 border border-zinc-800 rounded-lg w-full max-w-md p-6 max-h-[90vh] overflow-y-auto">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-heading font-bold uppercase text-white">Edit Session</h3>
                <button
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
                    type="number"
                    value={editMinutes}
                    onChange={(e) => setEditMinutes(e.target.value)}
                    min="1"
                    className="bg-zinc-900 border-zinc-800 text-white font-mono text-xl"
                  />
                </div>

                <div>
                  <label className="block text-zinc-400 text-sm font-body mb-2">Note (optional)</label>
                  <textarea
                    value={editNote}
                    onChange={(e) => setEditNote(e.target.value)}
                    placeholder="Add a note about this session..."
                    className="w-full bg-zinc-900 border border-zinc-800 rounded-md p-3 text-white font-body focus:ring-2 focus:ring-primary focus:outline-none resize-none h-24"
                  />
                </div>

                <div className="flex gap-3 pt-4">
                  <Button
                    variant="outline"
                    onClick={() => setEditingSession(null)}
                    className="flex-1 border-zinc-700 text-zinc-300 hover:bg-zinc-800"
                  >
                    Cancel
                  </Button>
                  <Button
                    onClick={handleSaveEdit}
                    disabled={actionLoading}
                    className="flex-1 bg-primary text-primary-foreground hover:bg-primary/90"
                  >
                    {actionLoading ? 'Saving...' : 'Save Changes'}
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
                This action cannot be undone.
              </p>
              <div className="flex gap-3">
                <Button
                  variant="outline"
                  onClick={() => setDeleteConfirm(null)}
                  className="flex-1 border-zinc-700 text-zinc-300 hover:bg-zinc-800"
                >
                  Cancel
                </Button>
                <Button
                  onClick={() => handleDeleteSession(deleteConfirm)}
                  disabled={actionLoading}
                  className="flex-1 bg-red-600 text-white hover:bg-red-700"
                >
                  {actionLoading ? 'Deleting...' : 'Delete'}
                </Button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
