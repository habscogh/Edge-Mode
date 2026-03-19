import React, { useState, useEffect, useMemo } from 'react';
import axios from 'axios';
import { 
  Users, ChevronDown, ChevronUp, Loader2, Copy, Check,
  UserCircle, Flame, Mail, Calendar, Crown, Shield, Trash2,
  Search, Filter, AlertTriangle
} from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
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
  
  // Search and filter state
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState('all'); // 'all', 'teams', 'private', 'empty'

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

  // Check if group is empty (for teams: only coach, for private: 0 or 1 member)
  const isEmptyGroup = (group) => {
    const isTeam = group.coach_id || group.type === 'team';
    if (isTeam) {
      // Team is empty if only coach remains (1 member)
      return group.member_count <= 1;
    }
    // Private group is empty if 0 members
    return group.member_count === 0;
  };

  // Filter and search groups
  const filteredGroups = useMemo(() => {
    let result = groups;
    
    // Apply type filter
    if (filterType === 'teams') {
      result = result.filter(g => g.coach_id || g.type === 'team');
    } else if (filterType === 'private') {
      result = result.filter(g => !g.coach_id && g.type !== 'team');
    } else if (filterType === 'empty') {
      result = result.filter(g => isEmptyGroup(g));
    }
    
    // Apply search
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      result = result.filter(g => 
        g.name.toLowerCase().includes(query) ||
        g.coach_name?.toLowerCase().includes(query) ||
        g.invite_code?.toLowerCase().includes(query)
      );
    }
    
    return result;
  }, [groups, filterType, searchQuery]);

  // Separate filtered results into teams and regular groups
  const teams = filteredGroups.filter(g => g.coach_id || g.type === 'team');
  const regularGroups = filteredGroups.filter(g => !g.coach_id && g.type !== 'team');
  
  // Count empty groups
  const emptyGroupsCount = groups.filter(g => isEmptyGroup(g)).length;

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
      <div className="grid grid-cols-4 gap-3">
        <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-3 text-center">
          <div className="text-2xl font-bold text-white">{groups.length}</div>
          <div className="text-xs text-zinc-500">Total Groups</div>
        </div>
        <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-3 text-center">
          <div className="text-2xl font-bold text-purple-400">{groups.filter(g => g.coach_id || g.type === 'team').length}</div>
          <div className="text-xs text-zinc-500">Coach Teams</div>
        </div>
        <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-3 text-center">
          <div className="text-2xl font-bold text-blue-400">
            {groups.reduce((sum, g) => sum + (g.member_count || 0), 0)}
          </div>
          <div className="text-xs text-zinc-500">Total Members</div>
        </div>
        <div 
          className={`bg-zinc-900 border rounded-lg p-3 text-center cursor-pointer transition-colors ${
            filterType === 'empty' 
              ? 'border-amber-500 bg-amber-500/10' 
              : emptyGroupsCount > 0 
                ? 'border-amber-500/50 hover:bg-amber-500/10' 
                : 'border-zinc-800'
          }`}
          onClick={() => setFilterType(filterType === 'empty' ? 'all' : 'empty')}
        >
          <div className={`text-2xl font-bold ${emptyGroupsCount > 0 ? 'text-amber-400' : 'text-zinc-500'}`}>
            {emptyGroupsCount}
          </div>
          <div className="text-xs text-zinc-500 flex items-center justify-center gap-1">
            {emptyGroupsCount > 0 && <AlertTriangle className="w-3 h-3 text-amber-400" />}
            Empty
          </div>
        </div>
      </div>

      {/* Search and Filter Bar */}
      <div className="flex items-center gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
          <Input
            placeholder="Search groups, coaches, or invite codes..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9 bg-zinc-900 border-zinc-800 text-white placeholder:text-zinc-500"
          />
        </div>
        <div className="flex items-center gap-1 bg-zinc-900 border border-zinc-800 rounded-lg p-1">
          <button
            onClick={() => setFilterType('all')}
            className={`px-3 py-1.5 text-xs font-medium rounded transition-colors ${
              filterType === 'all' 
                ? 'bg-zinc-700 text-white' 
                : 'text-zinc-400 hover:text-white'
            }`}
          >
            All
          </button>
          <button
            onClick={() => setFilterType('teams')}
            className={`px-3 py-1.5 text-xs font-medium rounded transition-colors ${
              filterType === 'teams' 
                ? 'bg-purple-500/20 text-purple-400' 
                : 'text-zinc-400 hover:text-white'
            }`}
          >
            Teams
          </button>
          <button
            onClick={() => setFilterType('private')}
            className={`px-3 py-1.5 text-xs font-medium rounded transition-colors ${
              filterType === 'private' 
                ? 'bg-blue-500/20 text-blue-400' 
                : 'text-zinc-400 hover:text-white'
            }`}
          >
            Private
          </button>
          <button
            onClick={() => setFilterType('empty')}
            className={`px-3 py-1.5 text-xs font-medium rounded transition-colors flex items-center gap-1 ${
              filterType === 'empty' 
                ? 'bg-amber-500/20 text-amber-400' 
                : 'text-zinc-400 hover:text-white'
            }`}
          >
            <AlertTriangle className="w-3 h-3" />
            Empty
          </button>
        </div>
      </div>

      {/* Search Results Info */}
      {(searchQuery || filterType !== 'all') && (
        <div className="flex items-center justify-between text-sm">
          <span className="text-zinc-400">
            Showing {filteredGroups.length} of {groups.length} groups
            {searchQuery && <span className="text-zinc-500"> matching "{searchQuery}"</span>}
          </span>
          {(searchQuery || filterType !== 'all') && (
            <button 
              onClick={() => { setSearchQuery(''); setFilterType('all'); }}
              className="text-primary hover:underline"
            >
              Clear filters
            </button>
          )}
        </div>
      )}

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
              isEmpty={isEmptyGroup(group)}
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
              isEmpty={isEmptyGroup(group)}
            />
          ))}
        </div>
      )}

      {filteredGroups.length === 0 && (
        <div className="text-center py-8 text-zinc-500">
          {searchQuery || filterType !== 'all' ? 'No groups match your filters' : 'No groups found'}
        </div>
      )}
    </div>
  );
};

const GroupCard = ({ group, expanded, onToggle, onCopyCode, copiedCode, formatDate, isTeam, onDelete, deleting, isEmpty }) => {
  return (
    <div className={`bg-zinc-900 border rounded-lg overflow-hidden ${
      isEmpty ? 'border-amber-500/50' : 'border-zinc-800'
    }`}>
      {/* Group Header */}
      <div 
        className="p-3 cursor-pointer hover:bg-zinc-800/50 transition-colors"
        onClick={onToggle}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
              isEmpty ? 'bg-amber-500/20' : isTeam ? 'bg-purple-500/20' : 'bg-blue-500/20'
            }`}>
              {isEmpty ? (
                <AlertTriangle className="w-5 h-5 text-amber-400" />
              ) : isTeam ? (
                <Shield className="w-5 h-5 text-purple-400" />
              ) : (
                <Users className="w-5 h-5 text-blue-400" />
              )}
            </div>
            <div>
              <div className="text-sm text-white font-medium flex items-center gap-2">
                {group.name}
                {isEmpty && (
                  <span className="text-xs px-1.5 py-0.5 bg-amber-500/20 text-amber-400 rounded border border-amber-500/30">
                    Empty
                  </span>
                )}
                {group.has_extended_trial && (
                  <span className="text-xs px-1.5 py-0.5 bg-amber-500/20 text-amber-400 rounded">
                    Extended Trial
                  </span>
                )}
              </div>
              <div className="text-xs text-zinc-500">
                {isTeam && group.coach_name && `Coach: ${group.coach_name} • `}
                {group.member_count} member{group.member_count !== 1 ? 's' : ''}
                {isEmpty && isTeam && ' (coach only)'}
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
