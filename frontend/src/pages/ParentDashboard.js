import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'sonner';
import { Button } from '../components/ui/button';
import { 
  ArrowLeft, 
  User, 
  Flame,
  Target,
  Calendar,
  TrendingUp,
  Award,
  Clock,
  ChevronRight,
  Bell
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const StudentCard = ({ student, onView }) => {
  return (
    <div 
      className="bg-zinc-950 border border-zinc-800 rounded-lg p-4 cursor-pointer hover:border-primary/50 transition-colors"
      onClick={() => onView(student.id)}
      data-testid={`student-card-${student.id}`}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 bg-primary/20 rounded-full flex items-center justify-center">
            <span className="text-primary font-bold text-lg">
              {student.username?.charAt(0).toUpperCase()}
            </span>
          </div>
          <div>
            <h3 className="text-white font-medium">{student.username}</h3>
            <div className="flex items-center gap-2 text-sm">
              <span className="text-zinc-500">Age {student.age}</span>
              {student.current_streak > 0 && (
                <span className="flex items-center gap-1 text-amber-500">
                  <Flame className="w-3 h-3" />
                  {student.current_streak} day streak
                </span>
              )}
            </div>
          </div>
        </div>
        <ChevronRight className="w-5 h-5 text-zinc-500" />
      </div>
    </div>
  );
};

const StudentDashboardView = ({ studentId, onBack }) => {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(null);

  useEffect(() => {
    fetchStudentDashboard();
  }, [studentId]);

  const fetchStudentDashboard = async () => {
    try {
      const response = await axios.get(`${API}/parent/student/${studentId}/dashboard`);
      setData(response.data);
    } catch (error) {
      console.error('Failed to fetch student dashboard:', error);
      toast.error('Failed to load student data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-zinc-400 font-mono">Loading...</div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="text-center py-12 text-zinc-500">
        Unable to load student data
      </div>
    );
  }

  return (
    <div>
      {/* Header */}
      <div className="bg-zinc-950 border-b border-zinc-800 p-4 -mx-4 -mt-4 mb-4">
        <div className="flex items-center gap-3">
          <button onClick={onBack} className="text-zinc-400 hover:text-white">
            <ArrowLeft className="w-6 h-6" />
          </button>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-primary/20 rounded-full flex items-center justify-center">
              <span className="text-primary font-bold">
                {data.student?.username?.charAt(0).toUpperCase()}
              </span>
            </div>
            <div>
              <h2 className="text-white font-bold">{data.student?.username}</h2>
              <p className="text-zinc-500 text-sm">Age {data.student?.age}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Streak Banner */}
      <div className="bg-gradient-to-r from-amber-500/20 to-orange-500/20 border border-amber-500/30 rounded-lg p-4 mb-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Flame className="w-8 h-8 text-amber-500" />
            <div>
              <div className="text-amber-500 font-bold text-2xl">{data.student?.current_streak} days</div>
              <div className="text-amber-500/70 text-sm">Current Streak</div>
            </div>
          </div>
          <div className="text-right">
            <div className="text-zinc-400 text-sm">Best: {data.student?.longest_streak} days</div>
          </div>
        </div>
      </div>

      {/* Weekly Stats */}
      <div className="bg-zinc-900 rounded-lg p-4 mb-4">
        <h3 className="text-white font-medium mb-3 flex items-center gap-2">
          <Calendar className="w-4 h-4 text-primary" />
          This Week
        </h3>
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-zinc-950 rounded-lg p-3 text-center">
            <div className="text-2xl font-mono font-bold text-primary">{data.weekly_stats?.sessions}</div>
            <div className="text-zinc-500 text-sm">Sessions</div>
          </div>
          <div className="bg-zinc-950 rounded-lg p-3 text-center">
            <div className="text-2xl font-mono font-bold text-white">{data.weekly_stats?.consistency_pct}%</div>
            <div className="text-zinc-500 text-sm">Consistency</div>
          </div>
          <div className="bg-zinc-950 rounded-lg p-3 text-center">
            <div className="text-2xl font-mono font-bold text-zinc-300">{data.weekly_stats?.days_active}</div>
            <div className="text-zinc-500 text-sm">Days Active</div>
          </div>
          <div className="bg-zinc-950 rounded-lg p-3 text-center">
            <div className="text-2xl font-mono font-bold text-zinc-300">{data.weekly_stats?.performance_index}</div>
            <div className="text-zinc-500 text-sm">Performance</div>
          </div>
        </div>
      </div>

      {/* Monthly Stats */}
      <div className="bg-zinc-900 rounded-lg p-4 mb-4">
        <h3 className="text-white font-medium mb-3 flex items-center gap-2">
          <TrendingUp className="w-4 h-4 text-primary" />
          This Month
        </h3>
        <div className="flex items-center justify-between">
          <div>
            <div className="text-2xl font-mono font-bold text-white">{data.monthly_stats?.total_sessions}</div>
            <div className="text-zinc-500 text-sm">Total Sessions</div>
          </div>
          <div className="text-right">
            <div className="text-2xl font-mono font-bold text-zinc-300">{data.monthly_stats?.total_minutes}</div>
            <div className="text-zinc-500 text-sm">Minutes Logged</div>
          </div>
        </div>
      </div>

      {/* Pillars */}
      {data.pillars && data.pillars.length > 0 && (
        <div className="bg-zinc-900 rounded-lg p-4 mb-4">
          <h3 className="text-white font-medium mb-3 flex items-center gap-2">
            <Target className="w-4 h-4 text-primary" />
            Focus Areas
          </h3>
          <div className="space-y-3">
            {data.pillars.map((pillar, idx) => {
              const progress = pillar.target > 0 
                ? Math.min((pillar.sessions_this_week / pillar.target) * 100, 100) 
                : 0;
              return (
                <div key={idx}>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-zinc-300">{pillar.pillar_name}</span>
                    <span className="text-zinc-500 text-sm">
                      {pillar.sessions_this_week}/{pillar.target} sessions
                    </span>
                  </div>
                  <div className="h-2 bg-zinc-800 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-primary rounded-full transition-all"
                      style={{ width: `${progress}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Badges */}
      <div className="flex items-center gap-2 text-zinc-400 mb-4">
        <Award className="w-5 h-5 text-amber-500" />
        <span>{data.badges_earned} badges earned</span>
      </div>

      {/* Recent Activity */}
      {data.recent_sessions && data.recent_sessions.length > 0 && (
        <div className="bg-zinc-900 rounded-lg p-4">
          <h3 className="text-white font-medium mb-3 flex items-center gap-2">
            <Clock className="w-4 h-4 text-primary" />
            Recent Activity
          </h3>
          <div className="space-y-2">
            {data.recent_sessions.slice(0, 5).map((session, idx) => (
              <div key={idx} className="flex items-center justify-between py-2 border-b border-zinc-800 last:border-0">
                <div>
                  <div className="text-zinc-300">{session.pillar}</div>
                  <div className="text-zinc-500 text-sm">{session.date}</div>
                </div>
                <div className="text-zinc-400 text-sm">{session.minutes_spent} min</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export const ParentDashboard = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [students, setStudents] = useState([]);
  const [selectedStudent, setSelectedStudent] = useState(null);
  const [inviteCode, setInviteCode] = useState('');
  const [accepting, setAccepting] = useState(false);

  useEffect(() => {
    fetchLinkedStudents();
  }, []);

  const fetchLinkedStudents = async () => {
    try {
      const response = await axios.get(`${API}/parent/linked-students`);
      setStudents(response.data.students || []);
    } catch (error) {
      console.error('Failed to fetch linked students:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAcceptInvite = async () => {
    if (!inviteCode.trim()) {
      toast.error('Please enter an invite code');
      return;
    }

    setAccepting(true);
    try {
      const response = await axios.post(`${API}/parent/accept`, { invite_code: inviteCode.trim() });
      toast.success(response.data.message);
      setInviteCode('');
      fetchLinkedStudents();
    } catch (error) {
      console.error('Failed to accept invite:', error);
      toast.error(error.response?.data?.detail || 'Invalid invite code');
    } finally {
      setAccepting(false);
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
            <h1 className="text-xl font-bold text-white">Parent Dashboard</h1>
            <p className="text-zinc-500 text-sm">Track your child's progress</p>
          </div>
        </div>
      </div>

      <div className="p-4">
        {selectedStudent ? (
          <StudentDashboardView 
            studentId={selectedStudent} 
            onBack={() => setSelectedStudent(null)}
          />
        ) : (
          <>
            {/* Accept Invite Section */}
            <div className="bg-zinc-900 rounded-lg p-4 mb-6">
              <h3 className="text-white font-medium mb-2 flex items-center gap-2">
                <Bell className="w-4 h-4 text-primary" />
                Link a Student
              </h3>
              <p className="text-zinc-500 text-sm mb-3">
                Enter the invite code your child shared with you
              </p>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={inviteCode}
                  onChange={(e) => setInviteCode(e.target.value.toUpperCase())}
                  placeholder="PARENT-XXXXXX"
                  className="flex-1 bg-zinc-950 border border-zinc-800 rounded-lg px-4 py-2 text-white placeholder-zinc-600 focus:outline-none focus:border-primary"
                  data-testid="invite-code-input"
                />
                <Button
                  onClick={handleAcceptInvite}
                  disabled={accepting}
                  className="bg-primary hover:bg-primary/90 text-black"
                  data-testid="accept-invite-btn"
                >
                  {accepting ? 'Linking...' : 'Link'}
                </Button>
              </div>
            </div>

            {/* Linked Students */}
            <h2 className="text-white font-medium mb-3">
              Linked Students ({students.length})
            </h2>

            {students.length === 0 ? (
              <div className="text-center py-12 bg-zinc-900 rounded-lg">
                <User className="w-12 h-12 text-zinc-700 mx-auto mb-4" />
                <h3 className="text-zinc-400 font-medium mb-2">No students linked yet</h3>
                <p className="text-zinc-500 text-sm">
                  Ask your child to send you an invite from their profile
                </p>
              </div>
            ) : (
              <div className="space-y-3">
                {students.map(student => (
                  <StudentCard 
                    key={student.id} 
                    student={student}
                    onView={setSelectedStudent}
                  />
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default ParentDashboard;
