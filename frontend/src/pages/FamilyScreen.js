import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'sonner';
import { Button } from '../components/ui/button';
import { 
  ArrowLeft, 
  Users, 
  Mail,
  Check,
  Clock,
  Trash2,
  Plus,
  Copy
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export const FamilyScreen = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [parentData, setParentData] = useState(null);
  const [email, setEmail] = useState('');
  const [sending, setSending] = useState(false);

  useEffect(() => {
    fetchParentLinks();
  }, []);

  const fetchParentLinks = async () => {
    try {
      const response = await axios.get(`${API}/student/linked-parents`);
      setParentData(response.data);
    } catch (error) {
      console.error('Failed to fetch parent links:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleInviteParent = async () => {
    if (!email.trim()) {
      toast.error('Please enter an email address');
      return;
    }

    setSending(true);
    try {
      const response = await axios.post(`${API}/parent/invite`, { parent_email: email.trim() });
      toast.success('Invitation sent!');
      setEmail('');
      fetchParentLinks();
      
      // Show invite code
      if (response.data.invite_code) {
        toast.success(`Invite code: ${response.data.invite_code}`, { duration: 10000 });
      }
    } catch (error) {
      console.error('Failed to send invite:', error);
      toast.error(error.response?.data?.detail || 'Failed to send invitation');
    } finally {
      setSending(false);
    }
  };

  const handleUnlink = async (linkId) => {
    if (!window.confirm('Are you sure you want to remove this parent?')) return;

    try {
      await axios.delete(`${API}/parent/unlink/${linkId}`);
      toast.success('Parent unlinked');
      fetchParentLinks();
    } catch (error) {
      console.error('Failed to unlink:', error);
      toast.error('Failed to unlink parent');
    }
  };

  const copyInviteCode = (code) => {
    navigator.clipboard.writeText(code);
    toast.success('Invite code copied!');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-[#09090b]">
        <div className="text-zinc-400 font-mono">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#09090b] pb-24">
      {/* Header */}
      <div className="bg-zinc-950 border-b border-zinc-800 p-4">
        <div className="flex items-center gap-3">
          <button onClick={() => navigate(-1)} className="text-zinc-400 hover:text-white">
            <ArrowLeft className="w-6 h-6" />
          </button>
          <div>
            <h1 className="text-xl font-bold text-white">Family Access</h1>
            <p className="text-zinc-500 text-sm">Let parents track your progress</p>
          </div>
        </div>
      </div>

      <div className="p-4">
        {/* Invite Parent Section */}
        {parentData?.slots_remaining > 0 && (
          <div className="bg-zinc-900 rounded-lg p-4 mb-6">
            <h3 className="text-white font-medium mb-2 flex items-center gap-2">
              <Plus className="w-4 h-4 text-primary" />
              Invite a Parent
            </h3>
            <p className="text-zinc-500 text-sm mb-3">
              They'll be able to view your progress, streaks, and achievements
            </p>
            <div className="flex gap-2">
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="parent@email.com"
                className="flex-1 bg-zinc-950 border border-zinc-800 rounded-lg px-4 py-2 text-white placeholder-zinc-600 focus:outline-none focus:border-primary"
                data-testid="parent-email-input"
              />
              <Button
                onClick={handleInviteParent}
                disabled={sending}
                className="bg-primary hover:bg-primary/90 text-black"
                data-testid="send-invite-btn"
              >
                {sending ? 'Sending...' : 'Invite'}
              </Button>
            </div>
            <p className="text-zinc-600 text-xs mt-2">
              {parentData?.slots_remaining} of 2 invite slots remaining
            </p>
          </div>
        )}

        {/* Active Parents */}
        {parentData?.active_parents?.length > 0 && (
          <div className="mb-6">
            <h2 className="text-white font-medium mb-3 flex items-center gap-2">
              <Check className="w-4 h-4 text-primary" />
              Linked Parents ({parentData.active_parents.length})
            </h2>
            <div className="space-y-3">
              {parentData.active_parents.map((parent, idx) => (
                <div key={idx} className="bg-zinc-950 border border-zinc-800 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-primary/20 rounded-full flex items-center justify-center">
                        <Users className="w-5 h-5 text-primary" />
                      </div>
                      <div>
                        <div className="text-white font-medium">
                          {parent.parent_username || parent.parent_email}
                        </div>
                        <div className="text-zinc-500 text-sm">{parent.parent_email}</div>
                      </div>
                    </div>
                    <Button
                      onClick={() => handleUnlink(parent.link_id)}
                      variant="ghost"
                      size="sm"
                      className="text-red-500 hover:text-red-400 hover:bg-red-500/10"
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Pending Invites */}
        {parentData?.pending_invites?.length > 0 && (
          <div>
            <h2 className="text-white font-medium mb-3 flex items-center gap-2">
              <Clock className="w-4 h-4 text-amber-500" />
              Pending Invites ({parentData.pending_invites.length})
            </h2>
            <div className="space-y-3">
              {parentData.pending_invites.map((invite, idx) => (
                <div key={idx} className="bg-zinc-950 border border-amber-500/30 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-amber-500/20 rounded-full flex items-center justify-center">
                        <Mail className="w-5 h-5 text-amber-500" />
                      </div>
                      <div>
                        <div className="text-white">{invite.parent_email}</div>
                        <div className="text-zinc-500 text-sm">
                          Invited {new Date(invite.invited_at).toLocaleDateString()}
                        </div>
                      </div>
                    </div>
                    <Button
                      onClick={() => handleUnlink(invite.link_id)}
                      variant="ghost"
                      size="sm"
                      className="text-zinc-500 hover:text-zinc-400"
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                  <div className="text-xs text-zinc-500">
                    Waiting for parent to accept the invitation
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Empty State */}
        {parentData?.active_parents?.length === 0 && parentData?.pending_invites?.length === 0 && (
          <div className="text-center py-12 bg-zinc-900 rounded-lg">
            <Users className="w-12 h-12 text-zinc-700 mx-auto mb-4" />
            <h3 className="text-zinc-400 font-medium mb-2">No parents linked yet</h3>
            <p className="text-zinc-500 text-sm">
              Invite up to 2 parents to track your progress
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default FamilyScreen;
