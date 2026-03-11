import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Users, Plus, Edit2, Trash2, Copy, Check, X, 
  Loader2, Shield, Calendar, Hash, ChevronDown, ChevronUp
} from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export const AdminCoachManager = () => {
  const [codes, setCodes] = useState([]);
  const [coaches, setCoaches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [showCoaches, setShowCoaches] = useState(false);
  const [creating, setCreating] = useState(false);
  const [copiedCode, setCopiedCode] = useState(null);
  
  // Form state
  const [formData, setFormData] = useState({
    code: '',
    description: '',
    max_uses: 0,
    extended_trial_days: 30
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [codesRes, coachesRes] = await Promise.all([
        axios.get(`${API}/admin/coach-codes`),
        axios.get(`${API}/admin/coaches`)
      ]);
      setCodes(codesRes.data.codes || []);
      setCoaches(coachesRes.data.coaches || []);
    } catch (error) {
      toast.error('Failed to load coach data');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    if (!formData.code.trim()) {
      toast.error('Code is required');
      return;
    }

    setCreating(true);
    try {
      await axios.post(`${API}/admin/coach-codes`, null, {
        params: {
          code: formData.code,
          description: formData.description,
          max_uses: formData.max_uses,
          extended_trial_days: formData.extended_trial_days
        }
      });
      toast.success('Coach code created!');
      setShowCreateForm(false);
      setFormData({ code: '', description: '', max_uses: 0, extended_trial_days: 30 });
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create code');
    } finally {
      setCreating(false);
    }
  };

  const handleToggleActive = async (codeId, currentActive) => {
    try {
      await axios.put(`${API}/admin/coach-codes/${codeId}`, null, {
        params: { is_active: !currentActive }
      });
      toast.success(currentActive ? 'Code deactivated' : 'Code activated');
      fetchData();
    } catch (error) {
      toast.error('Failed to update code');
    }
  };

  const handleDelete = async (codeId, code) => {
    if (!confirm(`Delete coach code "${code}"? This cannot be undone.`)) return;
    
    try {
      await axios.delete(`${API}/admin/coach-codes/${codeId}`);
      toast.success('Code deleted');
      fetchData();
    } catch (error) {
      toast.error('Failed to delete code');
    }
  };

  const copyCode = (code) => {
    navigator.clipboard.writeText(code);
    setCopiedCode(code);
    toast.success('Code copied!');
    setTimeout(() => setCopiedCode(null), 2000);
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
          <Shield className="w-5 h-5 text-blue-400" />
          Coach Management
        </h3>
        <Button
          onClick={() => setShowCreateForm(!showCreateForm)}
          size="sm"
          className="bg-blue-500/20 text-blue-400 hover:bg-blue-500/30"
        >
          <Plus className="w-4 h-4 mr-1" />
          New Code
        </Button>
      </div>

      {/* Stats Summary */}
      <div className="grid grid-cols-3 gap-3">
        <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-3 text-center">
          <div className="text-2xl font-bold text-white">{codes.length}</div>
          <div className="text-xs text-zinc-500">Total Codes</div>
        </div>
        <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-3 text-center">
          <div className="text-2xl font-bold text-blue-400">{codes.filter(c => c.is_active).length}</div>
          <div className="text-xs text-zinc-500">Active</div>
        </div>
        <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-3 text-center">
          <div className="text-2xl font-bold text-green-400">{coaches.length}</div>
          <div className="text-xs text-zinc-500">Coaches</div>
        </div>
      </div>

      {/* Create Form */}
      {showCreateForm && (
        <form onSubmit={handleCreate} className="bg-zinc-900 border border-zinc-800 rounded-lg p-4 space-y-3">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-heading uppercase text-zinc-400">Create New Code</span>
            <button type="button" onClick={() => setShowCreateForm(false)} className="text-zinc-500 hover:text-white">
              <X className="w-4 h-4" />
            </button>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <Input
              placeholder="CODE (e.g., COACH2025)"
              value={formData.code}
              onChange={(e) => setFormData({ ...formData, code: e.target.value.toUpperCase() })}
              className="bg-zinc-950 border-zinc-700 uppercase"
            />
            <Input
              placeholder="Description (optional)"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="bg-zinc-950 border-zinc-700"
            />
            <div>
              <label className="text-xs text-zinc-500 mb-1 block">Max Uses (0 = unlimited)</label>
              <Input
                type="number"
                min="0"
                value={formData.max_uses}
                onChange={(e) => setFormData({ ...formData, max_uses: parseInt(e.target.value) || 0 })}
                className="bg-zinc-950 border-zinc-700"
              />
            </div>
            <div>
              <label className="text-xs text-zinc-500 mb-1 block">Extended Trial Days</label>
              <Input
                type="number"
                min="1"
                value={formData.extended_trial_days}
                onChange={(e) => setFormData({ ...formData, extended_trial_days: parseInt(e.target.value) || 30 })}
                className="bg-zinc-950 border-zinc-700"
              />
            </div>
          </div>

          <Button type="submit" disabled={creating} className="w-full">
            {creating ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Plus className="w-4 h-4 mr-2" />}
            Create Code
          </Button>
        </form>
      )}

      {/* Coach Codes List */}
      <div className="space-y-2">
        <div className="text-xs text-zinc-500 uppercase tracking-wide">Coach Codes</div>
        {codes.length === 0 ? (
          <div className="text-center py-4 text-zinc-500 text-sm">
            No codes yet. Create one to get started!
          </div>
        ) : (
          codes.map(code => (
            <div key={code.id} className="bg-zinc-900 border border-zinc-800 rounded-lg p-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <button
                    onClick={() => copyCode(code.code)}
                    className="flex items-center gap-2 font-mono text-sm bg-zinc-950 px-2 py-1 rounded hover:bg-zinc-800 transition-colors"
                  >
                    <span className="text-white font-bold">{code.code}</span>
                    {copiedCode === code.code ? (
                      <Check className="w-3 h-3 text-green-400" />
                    ) : (
                      <Copy className="w-3 h-3 text-zinc-500" />
                    )}
                  </button>
                  <span className={`text-xs px-2 py-0.5 rounded ${
                    code.is_active 
                      ? 'bg-green-500/20 text-green-400 border border-green-500/30' 
                      : 'bg-zinc-500/20 text-zinc-400 border border-zinc-500/30'
                  }`}>
                    {code.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <Button
                    onClick={() => handleToggleActive(code.id, code.is_active)}
                    variant="ghost"
                    size="sm"
                    className={code.is_active ? "text-yellow-400" : "text-green-400"}
                  >
                    {code.is_active ? 'Deactivate' : 'Activate'}
                  </Button>
                  <Button
                    onClick={() => handleDelete(code.id, code.code)}
                    variant="ghost"
                    size="sm"
                    className="text-red-400 hover:text-red-300"
                  >
                    <Trash2 className="w-3 h-3" />
                  </Button>
                </div>
              </div>
              <div className="flex items-center gap-4 mt-2 text-xs text-zinc-500">
                {code.description && <span>{code.description}</span>}
                <span className="flex items-center gap-1">
                  <Hash className="w-3 h-3" />
                  {code.usage_count || 0} uses
                  {code.max_uses > 0 && ` / ${code.max_uses} max`}
                </span>
                <span className="flex items-center gap-1">
                  <Calendar className="w-3 h-3" />
                  {code.extended_trial_days}d trial
                </span>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Coaches List (Collapsible) */}
      <div className="border-t border-zinc-800 pt-4">
        <button
          onClick={() => setShowCoaches(!showCoaches)}
          className="flex items-center justify-between w-full text-left"
        >
          <span className="text-xs text-zinc-500 uppercase tracking-wide flex items-center gap-2">
            <Users className="w-4 h-4" />
            Registered Coaches ({coaches.length})
          </span>
          {showCoaches ? <ChevronUp className="w-4 h-4 text-zinc-500" /> : <ChevronDown className="w-4 h-4 text-zinc-500" />}
        </button>

        {showCoaches && (
          <div className="mt-3 space-y-2">
            {coaches.length === 0 ? (
              <div className="text-center py-4 text-zinc-500 text-sm">No coaches registered yet</div>
            ) : (
              coaches.map(coach => (
                <div key={coach.id} className="bg-zinc-900/50 border border-zinc-800 rounded-lg p-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="text-sm text-white font-medium">{coach.name || coach.email}</div>
                      <div className="text-xs text-zinc-500">{coach.email}</div>
                    </div>
                    <div className="text-right">
                      <div className="text-sm text-zinc-300">{coach.team_name || 'No team'}</div>
                      <div className="text-xs text-zinc-500">
                        {coach.team_member_count || 0} player{coach.team_member_count !== 1 ? 's' : ''}
                      </div>
                    </div>
                  </div>
                  {coach.special_code && (
                    <div className="mt-2 text-xs text-zinc-500">
                      Used code: <span className="font-mono text-blue-400">{coach.special_code}</span>
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        )}
      </div>
    </div>
  );
};
