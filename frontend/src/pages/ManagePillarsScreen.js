import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { 
  ArrowLeft, 
  Target, 
  Plus, 
  Trash2, 
  Edit2, 
  Check, 
  X,
  AlertCircle
} from 'lucide-react';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const PILLAR_ICONS = {
  'Fitness/Training': '💪',
  'Sports Practice': '⚽',
  'Study/Academics': '📚',
  'Skill Development': '🎯',
  'Reading/Learning': '📖',
  'Personal Project': '🚀',
  'Discipline Habits': '⏰'
};

export const ManagePillarsScreen = () => {
  const navigate = useNavigate();
  const [pillars, setPillars] = useState([]);
  const [availablePillars, setAvailablePillars] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editingId, setEditingId] = useState(null);
  const [editTarget, setEditTarget] = useState('');
  const [showAddModal, setShowAddModal] = useState(false);
  const [newPillar, setNewPillar] = useState('');
  const [newTarget, setNewTarget] = useState('3');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [pillarsRes, availableRes] = await Promise.all([
        axios.get(`${API}/users/pillars`),
        axios.get(`${API}/pillars`)
      ]);
      setPillars(pillarsRes.data);
      setAvailablePillars(availableRes.data.pillars);
    } catch (error) {
      console.error('Failed to fetch pillars:', error);
      toast.error('Failed to load pillars');
    } finally {
      setLoading(false);
    }
  };

  const handleEditStart = (pillar) => {
    setEditingId(pillar.id);
    setEditTarget(pillar.weekly_target_sessions.toString());
  };

  const handleEditSave = async (pillarId) => {
    const target = parseInt(editTarget);
    if (isNaN(target) || target < 1 || target > 14) {
      toast.error('Target must be between 1 and 14');
      return;
    }

    setSaving(true);
    try {
      await axios.put(`${API}/users/pillars/${pillarId}`, {
        weekly_target_sessions: target
      });
      toast.success('Target updated');
      setEditingId(null);
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to update');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (pillarId, pillarName) => {
    if (pillars.length <= 1) {
      toast.error('You must have at least 1 pillar');
      return;
    }

    if (!window.confirm(`Remove "${pillarName}" from your pillars? Your logged sessions will be preserved.`)) {
      return;
    }

    setSaving(true);
    try {
      await axios.delete(`${API}/users/pillars/${pillarId}`);
      toast.success('Pillar removed');
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to remove');
    } finally {
      setSaving(false);
    }
  };

  const handleAdd = async () => {
    if (!newPillar) {
      toast.error('Please select a pillar');
      return;
    }

    const target = parseInt(newTarget);
    if (isNaN(target) || target < 1 || target > 14) {
      toast.error('Target must be between 1 and 14');
      return;
    }

    setSaving(true);
    try {
      await axios.post(`${API}/users/pillars/add`, {
        pillar_name: newPillar,
        weekly_target_sessions: target
      });
      toast.success('Pillar added');
      setShowAddModal(false);
      setNewPillar('');
      setNewTarget('3');
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to add pillar');
    } finally {
      setSaving(false);
    }
  };

  // Get pillars that user doesn't have yet
  const unusedPillars = availablePillars.filter(
    p => !pillars.some(up => up.pillar_name === p)
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-[#09090b]">
        <div className="text-zinc-400 font-mono">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#09090b] pb-24" data-testid="manage-pillars-screen">
      <div className="p-6 max-w-2xl mx-auto">
        {/* Header */}
        <div className="flex items-center gap-3 mb-6">
          <button 
            onClick={() => navigate(-1)}
            className="p-2 rounded-lg bg-zinc-900 hover:bg-zinc-800 transition-colors"
          >
            <ArrowLeft className="w-5 h-5 text-zinc-400" />
          </button>
          <div>
            <h1 className="text-2xl font-heading font-bold uppercase tracking-tight text-white">
              Manage Pillars
            </h1>
            <p className="text-zinc-400 font-body text-sm">
              {pillars.length}/5 pillars active
            </p>
          </div>
        </div>

        {/* Info Banner */}
        <div className="bg-zinc-900/50 border border-zinc-800 rounded-lg p-4 mb-6 flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-zinc-500 flex-shrink-0 mt-0.5" />
          <p className="text-zinc-400 text-sm font-body">
            Pillars are the areas you want to improve. You can have 3-5 active pillars. 
            Removing a pillar won't delete your logged sessions.
          </p>
        </div>

        {/* Current Pillars */}
        <div className="space-y-3 mb-6">
          {pillars.map((pillar) => (
            <div 
              key={pillar.id}
              className="bg-zinc-950 border border-zinc-800 rounded-lg p-4"
              data-testid={`pillar-${pillar.pillar_name.replace(/\s/g, '-').toLowerCase()}`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-zinc-800 rounded-full flex items-center justify-center text-xl">
                    {PILLAR_ICONS[pillar.pillar_name] || '🎯'}
                  </div>
                  <div>
                    <div className="text-white font-body font-medium">
                      {pillar.pillar_name}
                    </div>
                    {editingId === pillar.id ? (
                      <div className="flex items-center gap-2 mt-1">
                        <Input
                          type="number"
                          value={editTarget}
                          onChange={(e) => setEditTarget(e.target.value)}
                          min="1"
                          max="14"
                          className="w-16 h-8 bg-zinc-800 border-zinc-700 text-sm"
                        />
                        <span className="text-zinc-500 text-sm">sessions/week</span>
                        <button
                          onClick={() => handleEditSave(pillar.id)}
                          disabled={saving}
                          className="p-1 rounded hover:bg-zinc-800 text-green-500"
                        >
                          <Check className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => setEditingId(null)}
                          className="p-1 rounded hover:bg-zinc-800 text-zinc-500"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </div>
                    ) : (
                      <div className="text-zinc-500 text-sm font-body">
                        Target: {pillar.weekly_target_sessions} sessions/week
                      </div>
                    )}
                  </div>
                </div>
                
                {editingId !== pillar.id && (
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handleEditStart(pillar)}
                      className="p-2 rounded-lg hover:bg-zinc-800 text-zinc-400 hover:text-white transition-colors"
                      title="Edit target"
                    >
                      <Edit2 className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleDelete(pillar.id, pillar.pillar_name)}
                      disabled={pillars.length <= 1}
                      className={`p-2 rounded-lg transition-colors ${
                        pillars.length <= 1 
                          ? 'text-zinc-700 cursor-not-allowed' 
                          : 'hover:bg-red-950 text-zinc-400 hover:text-red-400'
                      }`}
                      title={pillars.length <= 1 ? 'Must have at least 1 pillar' : 'Remove pillar'}
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Add Pillar Button */}
        {pillars.length < 5 && unusedPillars.length > 0 && (
          <Button
            onClick={() => setShowAddModal(true)}
            className="w-full bg-primary text-primary-foreground hover:bg-primary/90 font-heading uppercase"
            data-testid="add-pillar-btn"
          >
            <Plus className="w-4 h-4 mr-2" />
            Add Pillar ({5 - pillars.length} remaining)
          </Button>
        )}

        {pillars.length >= 5 && (
          <p className="text-center text-zinc-500 text-sm font-body">
            Maximum of 5 pillars reached
          </p>
        )}

        {/* Add Pillar Modal */}
        {showAddModal && (
          <>
            <div 
              className="fixed inset-0 bg-black/60 z-40"
              onClick={() => setShowAddModal(false)}
            />
            <div className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-50 bg-zinc-900 border border-zinc-700 rounded-lg p-6 w-[90%] max-w-md">
              <h3 className="text-lg font-heading font-bold uppercase text-white mb-4">
                Add New Pillar
              </h3>
              
              {/* Pillar Selection */}
              <div className="mb-4">
                <label className="text-zinc-400 text-sm font-body block mb-2">
                  Select Pillar
                </label>
                <div className="grid grid-cols-1 gap-2 max-h-48 overflow-y-auto">
                  {unusedPillars.map((pillar) => (
                    <button
                      key={pillar}
                      onClick={() => setNewPillar(pillar)}
                      className={`flex items-center gap-3 p-3 rounded-lg border transition-colors text-left ${
                        newPillar === pillar
                          ? 'border-primary bg-primary/10'
                          : 'border-zinc-700 hover:border-zinc-600'
                      }`}
                    >
                      <span className="text-xl">{PILLAR_ICONS[pillar] || '🎯'}</span>
                      <span className="text-white font-body">{pillar}</span>
                    </button>
                  ))}
                </div>
              </div>

              {/* Weekly Target */}
              <div className="mb-6">
                <label className="text-zinc-400 text-sm font-body block mb-2">
                  Weekly Target (sessions per week)
                </label>
                <Input
                  type="number"
                  value={newTarget}
                  onChange={(e) => setNewTarget(e.target.value)}
                  min="1"
                  max="14"
                  className="bg-zinc-800 border-zinc-700"
                />
              </div>

              {/* Actions */}
              <div className="flex gap-3">
                <Button
                  variant="outline"
                  onClick={() => setShowAddModal(false)}
                  className="flex-1 border-zinc-700"
                >
                  Cancel
                </Button>
                <Button
                  onClick={handleAdd}
                  disabled={!newPillar || saving}
                  className="flex-1 bg-primary text-primary-foreground"
                >
                  {saving ? 'Adding...' : 'Add Pillar'}
                </Button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
};
