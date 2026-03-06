import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'sonner';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { 
  Users, 
  Mail, 
  Lock, 
  User,
  Trophy,
  Calendar,
  Sparkles,
  AlertCircle
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export const JoinTeam = () => {
  const { teamCode } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [teamInfo, setTeamInfo] = useState(null);
  const [error, setError] = useState(null);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    age: ''
  });

  useEffect(() => {
    fetchTeamInfo();
  }, [teamCode]);

  const fetchTeamInfo = async () => {
    try {
      const response = await axios.get(`${API}/team/${teamCode}`);
      setTeamInfo(response.data);
    } catch (error) {
      console.error('Failed to fetch team info:', error);
      setError('Invalid team link. Please check with your coach.');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Validation
    if (!formData.username || !formData.email || !formData.password || !formData.age) {
      toast.error('Please fill in all fields');
      return;
    }

    const age = parseInt(formData.age);
    if (isNaN(age) || age < 12 || age > 19) {
      toast.error('Age must be between 12 and 19');
      return;
    }

    if (formData.password.length < 6) {
      toast.error('Password must be at least 6 characters');
      return;
    }

    setSubmitting(true);
    try {
      const response = await axios.post(`${API}/auth/player/join-team?team_code=${teamCode}`, {
        username: formData.username,
        email: formData.email,
        password: formData.password,
        age: age
      });

      // Store token
      localStorage.setItem('token', response.data.token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${response.data.token}`;

      toast.success(response.data.message);
      
      // Redirect to onboarding
      navigate('/onboarding');
    } catch (error) {
      console.error('Registration failed:', error);
      toast.error(error.response?.data?.detail || 'Registration failed');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#09090b] flex items-center justify-center">
        <div className="text-zinc-400 font-mono">Loading team info...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-[#09090b] flex items-center justify-center p-4">
        <div className="w-full max-w-md text-center">
          <div className="w-16 h-16 bg-red-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
            <AlertCircle className="w-8 h-8 text-red-500" />
          </div>
          <h1 className="text-xl font-bold text-white mb-2">Invalid Team Link</h1>
          <p className="text-zinc-500 mb-6">{error}</p>
          <Button 
            onClick={() => navigate('/auth')}
            className="bg-primary hover:bg-primary/90 text-black"
          >
            Go to Regular Signup
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#09090b] flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Team Header */}
        <div className="text-center mb-6">
          <div className="w-16 h-16 bg-primary/20 rounded-full flex items-center justify-center mx-auto mb-4">
            <Trophy className="w-8 h-8 text-primary" />
          </div>
          <h1 className="text-2xl font-bold text-white mb-1">Join {teamInfo.team_name}</h1>
          <p className="text-zinc-500">Coach: {teamInfo.coach_name}</p>
        </div>

        {/* Team Stats */}
        <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-4 mb-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-zinc-400">
              <Users className="w-4 h-4" />
              <span>{teamInfo.member_count} players already joined</span>
            </div>
            <div className="flex items-center gap-1">
              {teamInfo.has_extended_trial && (
                <Sparkles className="w-4 h-4 text-amber-500" />
              )}
              <span className={teamInfo.has_extended_trial ? 'text-amber-500' : 'text-zinc-400'}>
                {teamInfo.trial_days}-day trial
              </span>
            </div>
          </div>
        </div>

        {/* Signup Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-6">
            <h2 className="text-white font-medium mb-4">Create Your Account</h2>
            
            <div className="space-y-4">
              <div className="relative">
                <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-zinc-500" />
                <Input
                  name="username"
                  placeholder="Username"
                  value={formData.username}
                  onChange={handleInputChange}
                  className="pl-10 bg-zinc-950 border-zinc-800 text-white"
                  data-testid="player-username-input"
                />
              </div>

              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-zinc-500" />
                <Input
                  name="email"
                  type="email"
                  placeholder="Email"
                  value={formData.email}
                  onChange={handleInputChange}
                  className="pl-10 bg-zinc-950 border-zinc-800 text-white"
                  data-testid="player-email-input"
                />
              </div>

              <div className="relative">
                <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-zinc-500" />
                <Input
                  name="age"
                  type="number"
                  min="12"
                  max="19"
                  placeholder="Age (12-19)"
                  value={formData.age}
                  onChange={handleInputChange}
                  className="pl-10 bg-zinc-950 border-zinc-800 text-white"
                  data-testid="player-age-input"
                />
              </div>

              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-zinc-500" />
                <Input
                  name="password"
                  type="password"
                  placeholder="Password"
                  value={formData.password}
                  onChange={handleInputChange}
                  className="pl-10 bg-zinc-950 border-zinc-800 text-white"
                  data-testid="player-password-input"
                />
              </div>
            </div>
          </div>

          <Button 
            type="submit"
            disabled={submitting}
            className="w-full bg-primary hover:bg-primary/90 text-black font-bold"
            data-testid="join-team-btn"
          >
            {submitting ? 'Joining...' : `Join ${teamInfo.team_name}`}
          </Button>

          <p className="text-center text-zinc-500 text-sm">
            Already have an account?{' '}
            <a href="/auth" className="text-primary hover:underline">Sign in</a>
          </p>
        </form>

        {/* Trial Info */}
        <div className="mt-6 text-center">
          <p className="text-zinc-600 text-xs">
            {teamInfo.has_extended_trial ? (
              <span className="text-amber-500">✨ Extended {teamInfo.trial_days}-day free trial for this team!</span>
            ) : (
              <span>{teamInfo.trial_days}-day free trial • No credit card required</span>
            )}
          </p>
        </div>
      </div>
    </div>
  );
};

export default JoinTeam;
