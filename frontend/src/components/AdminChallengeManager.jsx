import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Trophy, Plus, Edit2, Trash2, Users, Calendar, 
  ChevronDown, ChevronUp, X, Loader2, Target, Clock, Star
} from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const METRIC_TYPES = [
  { value: 'total_sessions', label: 'Total Sessions' },
  { value: 'total_minutes', label: 'Total Minutes' },
  { value: 'consistency', label: 'Consistency %' },
  { value: 'pillar_sessions', label: 'Pillar Sessions' },
  { value: 'pillar_minutes', label: 'Pillar Minutes' }
];

const PILLARS = [
  'Fitness/Sports', 'Study/Learning', 'Creative/Art', 
  'Social/Relationships', 'Mental Health', 'Career/Skills'
];

const STATUS_COLORS = {
  upcoming: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  active: 'bg-green-500/20 text-green-400 border-green-500/30',
  completed: 'bg-zinc-500/20 text-zinc-400 border-zinc-500/30',
  cancelled: 'bg-red-500/20 text-red-400 border-red-500/30'
};

export const AdminChallengeManager = () => {
  const [challenges, setChallenges] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [expandedChallenge, setExpandedChallenge] = useState(null);
  const [participants, setParticipants] = useState({});
  const [creating, setCreating] = useState(false);
  
  // Form state
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    challenge_type: 'weekly',
    metric_type: 'total_sessions',
    pillar: null
  });

  useEffect(() => {
    fetchChallenges();
  }, []);

  const fetchChallenges = async () => {
    try {
      const response = await axios.get(`${API}/challenges/admin/all`);
      setChallenges(response.data.challenges || []);
    } catch (error) {
      toast.error('Failed to load challenges');
    } finally {
      setLoading(false);
    }
  };

  const fetchParticipants = async (challengeId) => {
    try {
      const response = await axios.get(`${API}/challenges/admin/${challengeId}/participants`);
      setParticipants(prev => ({ ...prev, [challengeId]: response.data.participants }));
    } catch (error) {
      toast.error('Failed to load participants');
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    if (!formData.name || !formData.description) {
      toast.error('Name and description are required');
      return;
    }

    setCreating(true);
    try {
      await axios.post(`${API}/challenges/admin/create`, formData);
      toast.success('Challenge created!');
      setShowCreateForm(false);
      setFormData({
        name: '',
        description: '',
        challenge_type: 'weekly',
        metric_type: 'total_sessions',
        pillar: null
      });
      fetchChallenges();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create challenge');
    } finally {
      setCreating(false);
    }
  };

  const handleStatusChange = async (challengeId, newStatus) => {
    try {
      await axios.put(`${API}/challenges/admin/${challengeId}?status=${newStatus}`);
      toast.success('Status updated');
      fetchChallenges();
    } catch (error) {
      toast.error('Failed to update status');
    }
  };

  const handleToggleFeatured = async (challengeId, currentlyFeatured) => {
    try {
      await axios.put(`${API}/challenges/admin/${challengeId}?featured=${!currentlyFeatured}`);
      toast.success(currentlyFeatured ? 'Removed from featured' : 'Added to featured!');
      fetchChallenges();
    } catch (error) {
      toast.error('Failed to update featured status');
    }
  };

  const handleDelete = async (challengeId, challengeName) => {
    if (!confirm(`Delete "${challengeName}"? This will remove all participants too.`)) return;
    
    try {
      await axios.delete(`${API}/challenges/admin/${challengeId}`);
      toast.success('Challenge deleted');
      fetchChallenges();
    } catch (error) {
      toast.error('Failed to delete challenge');
    }
  };

  const toggleExpand = (challengeId) => {
    if (expandedChallenge === challengeId) {
      setExpandedChallenge(null);
    } else {
      setExpandedChallenge(challengeId);
      if (!participants[challengeId]) {
        fetchParticipants(challengeId);
      }
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader2 className="w-6 h-6 text-primary animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-heading font-bold uppercase text-white flex items-center gap-2">
          <Trophy className="w-5 h-5 text-yellow-400" />
          Challenge Management
        </h3>
        <Button
          onClick={() => setShowCreateForm(!showCreateForm)}
          size="sm"
          className="bg-primary/20 text-primary hover:bg-primary/30"
        >
          <Plus className="w-4 h-4 mr-1" />
          New Challenge
        </Button>
      </div>

      {/* Create Form */}
      {showCreateForm && (
        <form onSubmit={handleCreate} className="bg-zinc-900 border border-zinc-800 rounded-lg p-4 space-y-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-heading uppercase text-zinc-400">Create New Challenge</span>
            <button type="button" onClick={() => setShowCreateForm(false)} className="text-zinc-500 hover:text-white">
              <X className="w-4 h-4" />
            </button>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="col-span-2">
              <Input
                placeholder="Challenge Name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="bg-zinc-950 border-zinc-700"
              />
            </div>
            <div className="col-span-2">
              <Input
                placeholder="Description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                className="bg-zinc-950 border-zinc-700"
              />
            </div>
            <select
              value={formData.challenge_type}
              onChange={(e) => setFormData({ ...formData, challenge_type: e.target.value })}
              className="bg-zinc-950 border border-zinc-700 rounded-md px-3 py-2 text-sm text-white"
            >
              <option value="weekly">Weekly</option>
              <option value="monthly">Monthly</option>
            </select>
            <select
              value={formData.metric_type}
              onChange={(e) => setFormData({ ...formData, metric_type: e.target.value })}
              className="bg-zinc-950 border border-zinc-700 rounded-md px-3 py-2 text-sm text-white"
            >
              {METRIC_TYPES.map(m => (
                <option key={m.value} value={m.value}>{m.label}</option>
              ))}
            </select>
            <div className="col-span-2">
              <select
                value={formData.pillar || ''}
                onChange={(e) => setFormData({ ...formData, pillar: e.target.value || null })}
                className="w-full bg-zinc-950 border border-zinc-700 rounded-md px-3 py-2 text-sm text-white"
              >
                <option value="">All Pillars (General)</option>
                {PILLARS.map(p => (
                  <option key={p} value={p}>{p}</option>
                ))}
              </select>
            </div>
          </div>

          <Button type="submit" disabled={creating} className="w-full">
            {creating ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Plus className="w-4 h-4 mr-2" />}
            Create Challenge
          </Button>
        </form>
      )}

      {/* Challenges List */}
      <div className="space-y-2">
        {challenges.length === 0 ? (
          <div className="text-center py-8 text-zinc-500">
            No challenges yet. Create one to get started!
          </div>
        ) : (
          challenges.map(challenge => (
            <div key={challenge.id} className="bg-zinc-900 border border-zinc-800 rounded-lg overflow-hidden">
              {/* Challenge Header */}
              <div 
                className="p-3 flex items-center justify-between cursor-pointer hover:bg-zinc-800/50"
                onClick={() => toggleExpand(challenge.id)}
              >
                <div className="flex items-center gap-3">
                  <Trophy className="w-4 h-4 text-yellow-400" />
                  <div>
                    <div className="font-medium text-white text-sm">{challenge.name}</div>
                    <div className="text-xs text-zinc-500 flex items-center gap-2">
                      <span className="capitalize">{challenge.challenge_type}</span>
                      <span>•</span>
                      <span>{challenge.metric_type.replace('_', ' ')}</span>
                      {challenge.pillar && (
                        <>
                          <span>•</span>
                          <span>{challenge.pillar.split('/')[0]}</span>
                        </>
                      )}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {challenge.featured && (
                    <span className="text-xs px-1.5 py-0.5 rounded bg-yellow-500/20 text-yellow-400 border border-yellow-500/30 flex items-center gap-1">
                      <Star className="w-3 h-3" /> Featured
                    </span>
                  )}
                  <span className={`text-xs px-2 py-0.5 rounded border ${STATUS_COLORS[challenge.status]}`}>
                    {challenge.status}
                  </span>
                  <span className="text-xs text-zinc-500 flex items-center gap-1">
                    <Users className="w-3 h-3" />
                    {challenge.participant_count || 0}
                  </span>
                  {expandedChallenge === challenge.id ? (
                    <ChevronUp className="w-4 h-4 text-zinc-500" />
                  ) : (
                    <ChevronDown className="w-4 h-4 text-zinc-500" />
                  )}
                </div>
              </div>

              {/* Expanded Details */}
              {expandedChallenge === challenge.id && (
                <div className="border-t border-zinc-800 p-3 space-y-3">
                  <p className="text-sm text-zinc-400">{challenge.description}</p>
                  
                  <div className="flex items-center gap-4 text-xs text-zinc-500">
                    <span className="flex items-center gap-1">
                      <Calendar className="w-3 h-3" />
                      {challenge.start_date} → {challenge.end_date}
                    </span>
                    <span className="flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      Created {new Date(challenge.created_at).toLocaleDateString()}
                    </span>
                  </div>

                  {/* Status Controls */}
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-zinc-500">Set Status:</span>
                    {['upcoming', 'active', 'completed', 'cancelled'].map(status => (
                      <button
                        key={status}
                        onClick={(e) => {
                          e.stopPropagation();
                          handleStatusChange(challenge.id, status);
                        }}
                        className={`text-xs px-2 py-1 rounded border transition-all ${
                          challenge.status === status 
                            ? STATUS_COLORS[status] 
                            : 'border-zinc-700 text-zinc-500 hover:border-zinc-600'
                        }`}
                      >
                        {status}
                      </button>
                    ))}
                  </div>

                  {/* Participants */}
                  {participants[challenge.id] && (
                    <div className="mt-3">
                      <div className="text-xs text-zinc-500 mb-2">Participants ({participants[challenge.id].length})</div>
                      {participants[challenge.id].length > 0 ? (
                        <div className="max-h-32 overflow-y-auto space-y-1">
                          {participants[challenge.id].map((p, i) => (
                            <div key={p.id} className="flex items-center justify-between text-xs bg-zinc-950 px-2 py-1 rounded">
                              <span className="text-zinc-300">
                                #{p.rank || i + 1} {p.username || 'Unknown'}
                              </span>
                              <span className="text-zinc-500">{p.current_score?.toFixed(1) || 0} pts</span>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div className="text-xs text-zinc-600">No participants yet</div>
                      )}
                    </div>
                  )}

                  {/* Delete Button */}
                  <div className="pt-2 border-t border-zinc-800">
                    <Button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDelete(challenge.id, challenge.name);
                      }}
                      variant="ghost"
                      size="sm"
                      className="text-red-400 hover:text-red-300 hover:bg-red-500/10"
                    >
                      <Trash2 className="w-3 h-3 mr-1" />
                      Delete Challenge
                    </Button>
                  </div>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
};
