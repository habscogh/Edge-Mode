import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Users, Plus, TrendingUp, Share2, UserPlus, LogOut, Crown } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { toast } from 'sonner';
import { useAuth } from '../context/AuthContext';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export const GroupsScreen = () => {
  const { user } = useAuth();
  const [groups, setGroups] = useState([]);
  const [selectedGroup, setSelectedGroup] = useState(null);
  const [leaderboard, setLeaderboard] = useState([]);
  const [newGroupName, setNewGroupName] = useState('');
  const [inviteCode, setInviteCode] = useState('');
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isJoinDialogOpen, setIsJoinDialogOpen] = useState(false);
  const [isTransferDialogOpen, setIsTransferDialogOpen] = useState(false);
  const [selectedMemberForTransfer, setSelectedMemberForTransfer] = useState('');
  const [groupMembers, setGroupMembers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchGroups();
  }, []);

  const fetchGroups = async () => {
    try {
      const response = await axios.get(`${API}/groups`);
      console.log('Fetched groups:', response.data.length, 'groups');
      setGroups(response.data);
      if (response.data.length > 0) {
        setSelectedGroup(response.data[0]);
        fetchGroupLeaderboard(response.data[0].id);
      }
    } catch (error) {
      console.error('Failed to fetch groups:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchGroupLeaderboard = async (groupId) => {
    try {
      const response = await axios.get(`${API}/groups/${groupId}/leaderboard`);
      setLeaderboard(response.data);
    } catch (error) {
      console.error('Failed to fetch leaderboard:', error);
    }
  };

  const handleCreateGroup = async () => {
    if (!newGroupName) return;

    try {
      await axios.post(`${API}/groups`, {
        name: newGroupName,
        type: 'private'
      });
      setNewGroupName('');
      setIsCreateDialogOpen(false);
      fetchGroups();
      toast.success('Group created successfully!');
    } catch (error) {
      console.error('Failed to create group:', error);
      toast.error('Failed to create group');
    }
  };

  const handleJoinGroup = async () => {
    if (!inviteCode) return;

    try {
      const response = await axios.post(`${API}/groups/join`, {
        invite_code: inviteCode.toUpperCase()
      });
      setInviteCode('');
      setIsJoinDialogOpen(false);
      
      // Force refresh groups to ensure we only see the newly joined group
      await fetchGroups();
      
      toast.success('Joined group successfully!');
    } catch (error) {
      console.error('Failed to join group:', error);
      toast.error('Invalid invite code');
    }
  };

  const copyInviteCode = (code) => {
    navigator.clipboard.writeText(code);
    toast.success('Invite code copied!');
  };

  const handleLeaveGroup = async (groupId, groupName) => {
    if (!window.confirm(`Are you sure you want to leave "${groupName}"?`)) {
      return;
    }

    try {
      const response = await axios.post(`${API}/groups/${groupId}/leave`);
      toast.success(response.data.message);
      fetchGroups();
      if (selectedGroup?.id === groupId) {
        setSelectedGroup(null);
      }
    } catch (error) {
      console.error('Failed to leave group:', error);
      const errorMsg = error.response?.data?.detail || 'Failed to leave group';
      if (errorMsg.includes('Transfer ownership')) {
        toast.error('You must transfer ownership before leaving');
      } else {
        toast.error(errorMsg);
      }
    }
  };

  const fetchGroupMembers = async (groupId) => {
    try {
      const response = await axios.get(`${API}/groups/${groupId}/leaderboard`);
      // Store with user mapping for transfer
      const membersWithIds = response.data.map(member => ({
        username: member.username,
        user_id: member.user_id || null
      }));
      setGroupMembers(membersWithIds);
    } catch (error) {
      console.error('Failed to fetch members:', error);
    }
  };

  const handleTransferOwnership = async () => {
    if (!selectedMemberForTransfer) return;

    try {
      const response = await axios.post(`${API}/groups/${selectedGroup.id}/transfer`, {
        new_owner_id: selectedMemberForTransfer
      });
      toast.success(response.data.message);
      setIsTransferDialogOpen(false);
      setSelectedMemberForTransfer('');
      fetchGroups();
    } catch (error) {
      console.error('Failed to transfer ownership:', error);
      toast.error(error.response?.data?.detail || 'Failed to transfer ownership');
    }
  };

  const handleGroupSelect = (group) => {
    setSelectedGroup(group);
    fetchGroupLeaderboard(group.id);
    if (group.created_by === user?.id) {
      fetchGroupMembers(group.id);
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
    <div className="min-h-screen bg-[#09090b] p-4 pb-24">
      <div className="max-w-2xl mx-auto pt-6">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-3xl font-heading font-bold uppercase tracking-tight text-white">
            Groups
          </h1>
          <div className="flex gap-2">
            <Dialog open={isJoinDialogOpen} onOpenChange={setIsJoinDialogOpen}>
              <DialogTrigger asChild>
                <Button
                  data-testid="join-group-btn"
                  variant="ghost"
                  className="bg-zinc-900 text-white hover:bg-zinc-800 font-heading uppercase"
                >
                  <UserPlus className="w-4 h-4 mr-2" />
                  Join
                </Button>
              </DialogTrigger>
              <DialogContent className="bg-zinc-950 border-zinc-800">
                <DialogHeader>
                  <DialogTitle className="font-heading uppercase text-white">Join Group</DialogTitle>
                </DialogHeader>
                <div className="space-y-4 mt-4">
                  <Input
                    data-testid="invite-code-input"
                    placeholder="Enter invite code"
                    value={inviteCode}
                    onChange={(e) => setInviteCode(e.target.value.toUpperCase())}
                    className="bg-zinc-900 border-zinc-800 text-white font-mono uppercase"
                  />
                  <Button
                    data-testid="join-group-submit-btn"
                    onClick={handleJoinGroup}
                    className="w-full bg-primary text-primary-foreground hover:bg-primary/90 font-heading uppercase"
                  >
                    Join Group
                  </Button>
                </div>
              </DialogContent>
            </Dialog>

            <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
              <DialogTrigger asChild>
                <Button
                  data-testid="create-group-btn"
                  className="bg-primary text-primary-foreground hover:bg-primary/90 font-heading uppercase"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Create
                </Button>
              </DialogTrigger>
              <DialogContent className="bg-zinc-950 border-zinc-800">
                <DialogHeader>
                  <DialogTitle className="font-heading uppercase text-white">Create Group</DialogTitle>
                </DialogHeader>
                <div className="space-y-4 mt-4">
                  <Input
                    data-testid="group-name-input"
                    placeholder="Group name"
                    value={newGroupName}
                    onChange={(e) => setNewGroupName(e.target.value)}
                    className="bg-zinc-900 border-zinc-800 text-white font-body"
                  />
                  <Button
                    data-testid="create-group-submit-btn"
                    onClick={handleCreateGroup}
                    className="w-full bg-primary text-primary-foreground hover:bg-primary/90 font-heading uppercase"
                  >
                    Create Group
                  </Button>
                </div>
              </DialogContent>
            </Dialog>
          </div>
        </div>

        {groups.length === 0 ? (
          <div className="text-center py-12">
            <Users className="w-16 h-16 text-zinc-700 mx-auto mb-4" />
            <p className="text-zinc-400 font-body mb-4">No groups yet</p>
            <p className="text-zinc-500 text-sm font-body">Create a group to compete with friends</p>
          </div>
        ) : (
          <>
            <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
              {groups.map((group) => (
                <button
                  key={group.id}
                  data-testid={`group-tab-${group.name.toLowerCase().replace(/\s+/g, '-')}`}
                  onClick={() => handleGroupSelect(group)}
                  className={`px-4 py-2 rounded-md font-body whitespace-nowrap transition-all duration-200 ${
                    selectedGroup?.id === group.id
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-zinc-900 text-zinc-400 hover:bg-zinc-800'
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <span>{group.name}</span>
                    <span className={`text-xs font-mono ${selectedGroup?.id === group.id ? 'text-primary-foreground/70' : 'text-zinc-600'}`}>
                      ({group.members.length})
                    </span>
                  </div>
                </button>
              ))}
            </div>

            {selectedGroup && (
              <>
                <div className="bg-zinc-950 border border-zinc-800 rounded-md p-4 mb-4">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="text-zinc-400 text-xs font-body uppercase tracking-wide mb-1">Invite Code</div>
                      <div className="text-white font-mono text-xl font-bold">{selectedGroup.invite_code}</div>
                      <p className="text-zinc-500 text-xs font-body mt-1">Share this code with friends to join</p>
                    </div>
                    <Button
                      data-testid="copy-invite-code-btn"
                      onClick={() => copyInviteCode(selectedGroup.invite_code)}
                      variant="ghost"
                      className="text-primary hover:text-primary/80"
                    >
                      <Share2 className="w-5 h-5" />
                    </Button>
                  </div>
                </div>

                {/* Transfer Ownership (only for creators) */}
                {selectedGroup.created_by === user?.id && selectedGroup.members.length > 1 && (
                  <div className="mb-4">
                    <Dialog open={isTransferDialogOpen} onOpenChange={setIsTransferDialogOpen}>
                      <DialogTrigger asChild>
                        <Button
                          data-testid="transfer-ownership-btn"
                          variant="ghost"
                          className="w-full text-yellow-500 hover:text-yellow-400 hover:bg-yellow-500/10 font-body"
                          onClick={() => fetchGroupMembers(selectedGroup.id)}
                        >
                          <Crown className="w-4 h-4 mr-2" />
                          Transfer Ownership
                        </Button>
                      </DialogTrigger>
                      <DialogContent className="bg-zinc-950 border-zinc-800">
                        <DialogHeader>
                          <DialogTitle className="font-heading uppercase text-white">Transfer Ownership</DialogTitle>
                        </DialogHeader>
                        <div className="space-y-4 mt-4">
                          <p className="text-zinc-400 text-sm font-body">
                            Select a member to become the new owner of this group:
                          </p>
                          <div className="space-y-2">
                            {groupMembers
                              .filter(member => member.username !== user?.username)
                              .map((member, idx) => (
                                <button
                                  key={idx}
                                  onClick={() => setSelectedMemberForTransfer(member.user_id)}
                                  className={`w-full p-3 border rounded-md text-left transition-all duration-200 ${
                                    selectedMemberForTransfer === member.user_id
                                      ? 'bg-primary/10 border-primary'
                                      : 'bg-zinc-900 border-zinc-800 hover:border-zinc-600'
                                  }`}
                                >
                                  <div className="text-white font-body">{member.username}</div>
                                </button>
                              ))}
                          </div>
                          <Button
                            data-testid="confirm-transfer-btn"
                            onClick={handleTransferOwnership}
                            disabled={!selectedMemberForTransfer}
                            className="w-full bg-yellow-500 text-black hover:bg-yellow-400 font-heading uppercase"
                          >
                            Confirm Transfer
                          </Button>
                        </div>
                      </DialogContent>
                    </Dialog>
                  </div>
                )}

                {/* Leave Group (only for non-creators) */}
                {selectedGroup.created_by !== user?.id && (
                  <div className="mb-4">
                    <Button
                      data-testid="leave-group-btn"
                      onClick={() => handleLeaveGroup(selectedGroup.id, selectedGroup.name)}
                      variant="ghost"
                      className="w-full text-red-500 hover:text-red-400 hover:bg-red-500/10 font-body"
                    >
                      <LogOut className="w-4 h-4 mr-2" />
                      Leave Group
                    </Button>
                  </div>
                )}
              </>
            )}

            <div className="bg-zinc-950 border border-zinc-800 rounded-md">
              <div className="p-4 border-b border-zinc-800">
                <h2 className="text-lg font-heading font-bold uppercase tracking-tight text-white">
                  Leaderboard
                </h2>
                <p className="text-zinc-400 text-sm font-body mt-1">This week's rankings</p>
              </div>

              <div className="divide-y divide-zinc-800">
                {leaderboard.map((entry, idx) => (
                  <div
                    key={idx}
                    data-testid={`leaderboard-entry-${idx}`}
                    className="p-4 hover:bg-zinc-900/50 transition-colors"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center font-mono font-bold ${
                          idx === 0 ? 'bg-yellow-500/20 text-yellow-500' :
                          idx === 1 ? 'bg-zinc-400/20 text-zinc-400' :
                          idx === 2 ? 'bg-orange-500/20 text-orange-500' :
                          'bg-zinc-800 text-zinc-400'
                        }`}>
                          {idx + 1}
                        </div>
                        <div>
                          <div className="text-white font-body">{entry.username}</div>
                          <div className="text-zinc-500 text-xs font-body">{entry.current_streak} day streak</div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-primary font-mono font-bold text-lg">{entry.performance_index}%</div>
                        <div className="text-zinc-500 text-xs font-body">{entry.consistency_pct}% consistent</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
};