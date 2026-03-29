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
  Trash2,
  Plus,
  Send
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

  const handleAddParent = async () => {
    if (!email.trim()) {
      toast.error('Please enter an email address');
      return;
    }

    // Basic email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email.trim())) {
      toast.error('Please enter a valid email address');
      return;
    }

    setSending(true);
    try {
      const response = await axios.post(`${API}/parent/add`, { parent_email: email.trim() });
      toast.success(response.data.message);
      setEmail('');
      fetchParentLinks();
    } catch (error) {
      console.error('Failed to add parent:', error);
      toast.error(error.response?.data?.detail || 'Failed to add parent');
    } finally {
      setSending(false);
    }
  };

  const handleRemoveParent = async (linkId, parentEmail) => {
    if (!window.confirm(`Remove ${parentEmail} from receiving your reports?`)) return;

    try {
      await axios.delete(`${API}/parent/remove/${linkId}`);
      toast.success('Parent removed');
      fetchParentLinks();
    } catch (error) {
      console.error('Failed to remove parent:', error);
      toast.error('Failed to remove parent');
    }
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
            <p className="text-zinc-500 text-sm">Parents receive weekly progress reports</p>
          </div>
        </div>
      </div>

      <div className="p-4">
        {/* How it works */}
        <div className="bg-zinc-900/50 border border-zinc-800 rounded-lg p-4 mb-6">
          <h3 className="text-white font-medium mb-3 flex items-center gap-2">
            <Mail className="w-4 h-4 text-primary" />
            How it works
          </h3>
          <ul className="text-zinc-400 text-sm space-y-2">
            <li className="flex items-start gap-2">
              <span className="text-primary font-bold">1.</span>
              Add your parent's email below
            </li>
            <li className="flex items-start gap-2">
              <span className="text-primary font-bold">2.</span>
              They receive a welcome email (no account needed!)
            </li>
            <li className="flex items-start gap-2">
              <span className="text-primary font-bold">3.</span>
              Every Sunday, they get your progress report
            </li>
            <li className="flex items-start gap-2">
              <span className="text-primary font-bold">4.</span>
              They also get notified of streak milestones & badges
            </li>
          </ul>
        </div>

        {/* Add Parent Section */}
        {parentData?.slots_remaining > 0 && (
          <div className="bg-zinc-900 rounded-lg p-4 mb-6">
            <h3 className="text-white font-medium mb-2 flex items-center gap-2">
              <Plus className="w-4 h-4 text-primary" />
              Add Parent Email
            </h3>
            <p className="text-zinc-500 text-sm mb-3">
              They'll start receiving your weekly reports automatically
            </p>
            <div className="flex gap-2">
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="parent@email.com"
                className="flex-1 bg-zinc-950 border border-zinc-800 rounded-lg px-4 py-2 text-white placeholder-zinc-600 focus:outline-none focus:border-primary"
                data-testid="parent-email-input"
                onKeyPress={(e) => e.key === 'Enter' && handleAddParent()}
              />
              <Button
                onClick={handleAddParent}
                disabled={sending}
                className="bg-primary hover:bg-primary/90 text-black font-bold"
                data-testid="add-parent-btn"
              >
                {sending ? 'Adding...' : <><Send className="w-4 h-4 mr-1" /> Add</>}
              </Button>
            </div>
            <p className="text-zinc-600 text-xs mt-2">
              {parentData?.slots_remaining} of 2 slots remaining
            </p>
          </div>
        )}

        {/* Added Parents */}
        {parentData?.parents?.length > 0 && (
          <div className="mb-6">
            <h2 className="text-white font-medium mb-3 flex items-center gap-2">
              <Check className="w-4 h-4 text-primary" />
              Receiving Reports ({parentData.parents.length})
            </h2>
            <div className="space-y-3">
              {parentData.parents.map((parent, idx) => (
                <div key={idx} className="bg-zinc-950 border border-zinc-800 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-primary/20 rounded-full flex items-center justify-center">
                        <Users className="w-5 h-5 text-primary" />
                      </div>
                      <div>
                        <div className="text-white font-medium">{parent.parent_email}</div>
                        <div className="text-zinc-500 text-xs">
                          Added {new Date(parent.added_at).toLocaleDateString()}
                        </div>
                      </div>
                    </div>
                    <Button
                      onClick={() => handleRemoveParent(parent.link_id, parent.parent_email)}
                      variant="ghost"
                      size="sm"
                      className="text-red-500 hover:text-red-400 hover:bg-red-500/10"
                      data-testid={`remove-parent-${idx}`}
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Empty State */}
        {parentData?.parents?.length === 0 && (
          <div className="text-center py-12 bg-zinc-900 rounded-lg">
            <Users className="w-12 h-12 text-zinc-700 mx-auto mb-4" />
            <h3 className="text-zinc-400 font-medium mb-2">No parents added yet</h3>
            <p className="text-zinc-500 text-sm">
              Add up to 2 parent emails to share your progress
            </p>
          </div>
        )}

        {/* Max Parents Reached */}
        {parentData?.slots_remaining === 0 && (
          <div className="bg-zinc-900/50 border border-zinc-800 rounded-lg p-4 text-center">
            <p className="text-zinc-400 text-sm">
              Maximum 2 parents added. Remove one to add a different email.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default FamilyScreen;
