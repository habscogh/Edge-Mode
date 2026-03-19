import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Users, ChevronDown, ChevronUp, Loader2, Copy, Check,
  UserCircle, Flame, Mail, Calendar, Crown, Shield, Trash2
} from 'lucide-react';
import { Button } from './ui/button';
import { toast } from 'sonner';
import { format, parseISO } from 'date-fns';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export const AdminGroupsManager = () => {
  const [groups, setGroups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expandedGroup, setExpandedGroup] = useState(null);
  const [copiedCode, setCopiedCode] = useState(null);
  const [deleting, setDeleting] = useState(null);

  useEffect(() => {
    fetchGroups();
  }, []);

  const fetchGroups = async () => {
    try {
      const response = await axios.get(`${API}/admin/groups`);
      setGroups(response.data.groups || []);
    } catch (error) {
      toast.error('Failed to load groups');
    } finally {
      setLoading(false);
    }
  };

  const deleteGroup = async (groupId, groupName) => {
    if (!window.confirm(`Delete "${groupName}"? This will remove the group and unlink all members. This cannot be undone.`)) {
      return;
    }
    
    setDeleting(groupId);
    try {
      await axios.delete(`${API}/admin/groups/${groupId}`);
      toast.success(`Group "${groupName}" deleted`);
      fetchGroups();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to delete group');
    } finally {
      setDeleting(null);
    }
  };

  const copyCode = (code) => {
    navigator.clipboard.writeText(code);
    setCopiedCode(code);
    toast.success('Invite code copied!');
    setTimeout(() => setCopiedCode(null), 2000);
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return 'N/A';
    try {
      return format(parseISO(dateStr), 'MMM d, yyyy');
    } catch {
      return 'N/A';
    }
  };

  // Separate teams (coach groups) from regular groups
  const teams = groups.filter(g => g.coach_id || g.type === 'team');
  const regularGroups = groups.filter(g => !g.coach_id && g.type !== 'team');

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
          <Users className="w-5 h-5 text-purple-400" />
          Groups & Teams
        </h3>
        <Button
          onClick={fetchGroups}
          size="sm"
          variant="ghost"
          className="text-zinc-400 hover:text-white"
        >
          <Loader2 className={`w-4 h-4 mr-1 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      {/* Stats Summary */}
      <div className="grid grid-cols-3 gap-3">
        <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-3 text-center">
          <div className="text-2xl font-bold text-white">{groups.length}</div>
          <div className="text-xs text-zinc-500">Total Groups</div>
        </div>
        <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-3 text-center">
          <div className="text-2xl font-bold text-purple-400">{teams.length}</div>
          <div className="text-xs text-zinc-500">Coach Teams</div>
        </div>
        <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-3 text-center">
          <div className="text-2xl font-bold text-blue-400">
            {groups.reduce((sum, g) => sum + (g.member_count || 0), 0)}
          </div>
          <div className="text-xs text-zinc-500">Total Members</div>
        </div>
      </div>

      {/* Coach Teams Section */}
      {teams.length > 0 && (
        <div className="space-y-2">
          <div className="text-xs text-zinc-500 uppercase tracking-wide flex items-center gap-2">
            <Crown className="w-3 h-3 text-amber-400" />
            Coach Teams ({teams.length})
          </div>
          {teams.map(group => (
            <GroupCard 
              key={group.id} 
              group={group} 
              expanded={expandedGroup === group.id}
              onToggle={() => setExpandedGroup(expandedGroup === group.id ? null : group.id)}
              onCopyCode={copyCode}
              copiedCode={copiedCode}
              formatDate={formatDate}
              isTeam={true}
              onDelete={deleteGroup}
              deleting={deleting}
            />
          ))}
        </div>
      )}

      {/* Regular Groups Section */}
      {regularGroups.length > 0 && (
        <div className="space-y-2 border-t border-zinc-800 pt-4">
          <div className="text-xs text-zinc-500 uppercase tracking-wide flex items-center gap-2">
            <Users className="w-3 h-3" />
            Private Groups ({regularGroups.length})
          </div>
          {regularGroups.map(group => (
            <GroupCard 
              key={group.id} 
              group={group} 
              expanded={expandedGroup === group.id}
              onToggle={() => setExpandedGroup(expandedGroup === group.id ? null : group.id)}
              onCopyCode={copyCode}
              copiedCode={copiedCode}
              formatDate={formatDate}
              isTeam={false}
              onDelete={deleteGroup}
              deleting={deleting}
            />
          ))}
        </div>
      )}

      {groups.length === 0 && (
        <div className="text-center py-8 text-zinc-500">
          No groups found
        </div>
      )}
    </div>
  );
};

const GroupCard = ({ group, expanded, onToggle, onCopyCode, copiedCode, formatDate, isTeam, onDelete, deleting }) => {
  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg overflow-hidden">
      {/* Group Header */}
      <div 
        className="p-3 cursor-pointer hover:bg-zinc-800/50 transition-colors"
        onClick={onToggle}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
              isTeam ? 'bg-purple-500/20' : 'bg-blue-500/20'
            }`}>
              {isTeam ? (
                <Shield className="w-5 h-5 text-purple-400" />
              ) : (
                <Users className="w-5 h-5 text-blue-400" />
              )}
            </div>
            <div>
              <div className="text-sm text-white font-medium flex items-center gap-2">
                {group.name}
                {group.has_extended_trial && (
                  <span className="text-xs px-1.5 py-0.5 bg-amber-500/20 text-amber-400 rounded">
                    Extended Trial
                  </span>
                )}
              </div>
              <div className="text-xs text-zinc-500">
                {isTeam && group.coach_name && `Coach: ${group.coach_name} • `}
                {group.member_count} member{group.member_count !== 1 ? 's' : ''}
              </div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {group.invite_code && (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onCopyCode(group.invite_code);
                }}
                className="flex items-center gap-1 font-mono text-xs bg-zinc-950 px-2 py-1 rounded hover:bg-zinc-700 transition-colors"
              >
                <span className="text-zinc-300">{group.invite_code}</span>
                {copiedCode === group.invite_code ? (
                  <Check className="w-3 h-3 text-green-400" />
                ) : (
                  <Copy className="w-3 h-3 text-zinc-500" />
                )}
              </button>
            )}
            {expanded ? (
              <ChevronUp className="w-4 h-4 text-zinc-500" />
            ) : (
              <ChevronDown className="w-4 h-4 text-zinc-500" />
            )}
          </div>
        </div>
      </div>

      {/* Expanded Members List */}
      {expanded && (
        <div className="border-t border-zinc-800 p-3 bg-zinc-950/50">
          <div className="text-xs text-zinc-500 uppercase tracking-wide mb-2">Members</div>
          {group.members && group.members.length > 0 ? (
            <div className="space-y-2">
              {group.members.map(member => (
                <div 
                  key={member.id} 
                  className="flex items-center justify-between py-2 px-3 bg-zinc-900 rounded-lg"
                >
                  <div className="flex items-center gap-3">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                      member.is_coach ? 'bg-purple-500/20' : 'bg-zinc-800'
                    }`}>
                      {member.is_coach ? (
                        <Crown className="w-4 h-4 text-purple-400" />
                      ) : (
                        <UserCircle className="w-4 h-4 text-zinc-400" />
                      )}
                    </div>
                    <div>
                      <div className="text-sm text-white flex items-center gap-2">
                        {member.name}
                        {member.is_coach && (
                          <span className="text-xs px-1.5 py-0.5 bg-purple-500/20 text-purple-400 rounded">
                            Coach
                          </span>
                        )}
                      </div>
                      <div className="text-xs text-zinc-500 flex items-center gap-2">
                        <Mail className="w-3 h-3" />
                        {member.email}
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="flex items-center gap-1 text-orange-400 text-sm">
                      <Flame className="w-3 h-3" />
                      {member.current_streak || 0}
                    </div>
                    <div className="text-xs text-zinc-500 flex items-center gap-1">
                      <Calendar className="w-3 h-3" />
                      {formatDate(member.join_date)}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-4 text-zinc-500 text-sm">
              No members in this group
            </div>
          )}
          
          {/* Group Footer Info */}
          <div className="mt-3 pt-3 border-t border-zinc-800 flex items-center justify-between text-xs text-zinc-500">
            <span>Created: {formatDate(group.created_at)}</span>
            <div className="flex items-center gap-3">
              <span>Type: {group.type || 'private'}</span>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onDelete(group.id, group.name);
                }}
                disabled={deleting === group.id}
                className="flex items-center gap-1 text-red-400 hover:text-red-300 transition-colors disabled:opacity-50"
              >
                {deleting === group.id ? (
                  <Loader2 className="w-3 h-3 animate-spin" />
                ) : (
                  <Trash2 className="w-3 h-3" />
                )}
                Delete Group
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminGroupsManager;
