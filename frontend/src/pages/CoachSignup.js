import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
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
  ArrowRight,
  Copy,
  Check,
  Sparkles,
  MessageSquare,
  Share2,
  Link2
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export const CoachSignup = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    teamName: '',
    specialCode: ''
  });
  const [result, setResult] = useState(null);
  const [copied, setCopied] = useState(false);

  const handleInputChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (step === 1) {
      // Validate step 1
      if (!formData.name || !formData.email || !formData.password) {
        toast.error('Please fill in all fields');
        return;
      }
      if (formData.password.length < 6) {
        toast.error('Password must be at least 6 characters');
        return;
      }
      setStep(2);
      return;
    }

    // Step 2 - Create account
    if (!formData.teamName) {
      toast.error('Please enter your team name');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API}/auth/coach/register`, {
        email: formData.email,
        password: formData.password,
        name: formData.name,
        team_name: formData.teamName,
        special_code: formData.specialCode || null
      });

      setResult(response.data);
      
      // Log the coach in
      localStorage.setItem('forge_token', response.data.token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${response.data.token}`;
      
      setStep(3);
      toast.success('Coach account created!');
    } catch (error) {
      console.error('Coach registration failed:', error);
      toast.error(error.response?.data?.detail || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  const copyInviteLink = () => {
    const fullLink = `${window.location.origin}/join/${result.invite_code}`;
    navigator.clipboard.writeText(fullLink);
    setCopied(true);
    toast.success('Invite link copied!');
    setTimeout(() => setCopied(false), 2000);
  };

  const [messageCopied, setMessageCopied] = useState(false);
  
  const getPreWrittenMessage = () => {
    const teamLink = `${window.location.origin}/join/${result?.invite_code}`;
    return `I want everyone to join this app for the next 2 weeks and track your training and study time daily.

It takes a few seconds and will show you how consistent you really are.

Join here: ${teamLink}`;
  };

  const copyMessage = () => {
    navigator.clipboard.writeText(getPreWrittenMessage());
    setMessageCopied(true);
    toast.success('Message copied!');
    setTimeout(() => setMessageCopied(false), 2000);
  };

  const shareViaText = () => {
    const message = encodeURIComponent(getPreWrittenMessage());
    window.open(`sms:?body=${message}`, '_blank');
  };

  const shareViaEmail = () => {
    const subject = encodeURIComponent(`Join ${result?.team_name} on Edge Mode`);
    const body = encodeURIComponent(getPreWrittenMessage());
    window.open(`mailto:?subject=${subject}&body=${body}`, '_blank');
  };

  const shareNative = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: `Join ${result?.team_name}`,
          text: getPreWrittenMessage(),
          url: `${window.location.origin}/join/${result?.invite_code}`
        });
      } catch (err) {
        // User cancelled or error
        if (err.name !== 'AbortError') {
          copyMessage();
        }
      }
    } else {
      copyMessage();
    }
  };

  const goToDashboard = () => {
    window.location.href = '/coach-home';
  };

  return (
    <div className="min-h-screen bg-[#09090b] flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-primary/20 rounded-full flex items-center justify-center mx-auto mb-4">
            <Trophy className="w-8 h-8 text-primary" />
          </div>
          <h1 className="text-2xl font-bold text-white mb-2">Coach Signup</h1>
          <p className="text-zinc-500">Create your free coach account</p>
        </div>

        {/* Progress Steps */}
        <div className="flex items-center justify-center gap-2 mb-8">
          {[1, 2, 3].map((s) => (
            <div 
              key={s}
              className={`w-3 h-3 rounded-full transition-colors ${
                step >= s ? 'bg-primary' : 'bg-zinc-700'
              }`}
            />
          ))}
        </div>

        {/* Step 1: Account Info */}
        {step === 1 && (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-6">
              <h2 className="text-white font-medium mb-4">Your Information</h2>
              
              <div className="space-y-4">
                <div className="relative">
                  <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-zinc-500" />
                  <Input
                    name="name"
                    placeholder="Your Name"
                    value={formData.name}
                    onChange={handleInputChange}
                    className="pl-10 bg-zinc-950 border-zinc-800 text-white"
                    data-testid="coach-name-input"
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
                    data-testid="coach-email-input"
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
                    data-testid="coach-password-input"
                  />
                </div>
              </div>
            </div>

            <Button 
              type="submit"
              className="w-full bg-primary hover:bg-primary/90 text-black font-bold"
              data-testid="coach-next-btn"
            >
              Next <ArrowRight className="w-4 h-4 ml-2" />
            </Button>

            <p className="text-center text-zinc-500 text-sm">
              Already have an account?{' '}
              <a href="/auth" className="text-primary hover:underline">Sign in</a>
            </p>
          </form>
        )}

        {/* Step 2: Team Info */}
        {step === 2 && (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-6">
              <h2 className="text-white font-medium mb-4">Team Information</h2>
              
              <div className="space-y-4">
                <div className="relative">
                  <Users className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-zinc-500" />
                  <Input
                    name="teamName"
                    placeholder="Team Name (e.g., Varsity Basketball)"
                    value={formData.teamName}
                    onChange={handleInputChange}
                    className="pl-10 bg-zinc-950 border-zinc-800 text-white"
                    data-testid="team-name-input"
                  />
                </div>

                <div className="border-t border-zinc-800 pt-4">
                  <div className="flex items-center gap-2 mb-2">
                    <Sparkles className="w-4 h-4 text-amber-500" />
                    <span className="text-white text-sm font-medium">Special Code (Optional)</span>
                  </div>
                  <p className="text-zinc-500 text-xs mb-3">
                    Have a promo code? Enter it to give your players a 30-day trial instead of 14 days.
                  </p>
                  <Input
                    name="specialCode"
                    placeholder="Enter code (e.g., EDGE30)"
                    value={formData.specialCode}
                    onChange={handleInputChange}
                    className="bg-zinc-950 border-zinc-800 text-white uppercase"
                    data-testid="special-code-input"
                  />
                </div>
              </div>
            </div>

            <div className="flex gap-3">
              <Button 
                type="button"
                variant="outline"
                onClick={() => setStep(1)}
                className="flex-1 border-zinc-700 text-zinc-300"
              >
                Back
              </Button>
              <Button 
                type="submit"
                disabled={loading}
                className="flex-1 bg-primary hover:bg-primary/90 text-black font-bold"
                data-testid="create-coach-btn"
              >
                {loading ? 'Creating...' : 'Create Team'}
              </Button>
            </div>
          </form>
        )}

        {/* Step 3: Team Created - Invite Players */}
        {step === 3 && result && (
          <div className="space-y-4">
            {/* Header */}
            <div className="text-center">
              <div className="w-16 h-16 bg-primary/20 rounded-full flex items-center justify-center mx-auto mb-4">
                <Check className="w-8 h-8 text-primary" />
              </div>
              <h2 className="text-2xl font-bold text-white mb-1">Team Created</h2>
              
              {result.has_extended_trial && (
                <div className="bg-amber-500/20 text-amber-400 text-sm px-3 py-2 rounded-lg mt-3 inline-block">
                  Your players get a 30-day extended trial!
                </div>
              )}
            </div>

            {/* Primary Message */}
            <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-6">
              <h3 className="text-xl font-bold text-white mb-2">Invite your team now</h3>
              <p className="text-zinc-400 text-sm">
                Send this to your players to get started with a simple 2-week consistency challenge.
              </p>
            </div>

            {/* Pre-Written Message Box */}
            <div className="bg-zinc-950 border border-zinc-700 rounded-lg p-4">
              <div className="bg-zinc-900 border-l-4 border-primary rounded-r-lg p-4 text-zinc-300 text-sm leading-relaxed">
                <p className="mb-3">I want everyone to join this app for the next 2 weeks and track your training and study time daily.</p>
                <p className="mb-3">It takes a few seconds and will show you how consistent you really are.</p>
                <p>Join here: <span className="text-primary font-medium">{window.location.origin}/join/{result.invite_code}</span></p>
              </div>
              
              {/* Copy Message & Share Link Buttons */}
              <div className="flex gap-2 mt-4">
                <Button
                  onClick={copyMessage}
                  className="flex-1 bg-primary hover:bg-primary/90 text-black font-bold"
                  data-testid="copy-message-btn"
                >
                  {messageCopied ? <Check className="w-4 h-4 mr-2" /> : <Copy className="w-4 h-4 mr-2" />}
                  Copy Message
                </Button>
                <Button
                  onClick={copyInviteLink}
                  variant="outline"
                  className="flex-1 border-zinc-700 text-zinc-300 hover:bg-zinc-800"
                  data-testid="copy-link-btn"
                >
                  {copied ? <Check className="w-4 h-4 mr-2" /> : <Link2 className="w-4 h-4 mr-2" />}
                  Copy Link
                </Button>
              </div>
            </div>

            {/* Share Options */}
            <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-4">
              <div className="text-zinc-400 text-xs uppercase tracking-wide mb-3 font-medium">
                Share via
              </div>
              <div className="grid grid-cols-3 gap-2">
                <Button
                  onClick={shareViaText}
                  variant="outline"
                  className="border-zinc-700 text-zinc-300 hover:bg-zinc-800 flex flex-col items-center py-4 h-auto"
                  data-testid="share-text-btn"
                >
                  <MessageSquare className="w-5 h-5 mb-1" />
                  <span className="text-xs">Text</span>
                </Button>
                <Button
                  onClick={shareViaEmail}
                  variant="outline"
                  className="border-zinc-700 text-zinc-300 hover:bg-zinc-800 flex flex-col items-center py-4 h-auto"
                  data-testid="share-email-btn"
                >
                  <Mail className="w-5 h-5 mb-1" />
                  <span className="text-xs">Email</span>
                </Button>
                <Button
                  onClick={shareNative}
                  variant="outline"
                  className="border-zinc-700 text-zinc-300 hover:bg-zinc-800 flex flex-col items-center py-4 h-auto"
                  data-testid="share-native-btn"
                >
                  <Share2 className="w-5 h-5 mb-1" />
                  <span className="text-xs">Share</span>
                </Button>
              </div>
            </div>

            {/* Action Line */}
            <div className="text-center py-2">
              <p className="text-zinc-400 text-sm font-medium">
                Best results come when you introduce this to your team at practice or send it today.
              </p>
            </div>

            {/* Go to Dashboard */}
            <Button 
              onClick={goToDashboard}
              variant="outline"
              className="w-full border-zinc-700 text-zinc-300 hover:bg-zinc-800"
              data-testid="go-dashboard-btn"
            >
              Go to Coach Dashboard
            </Button>
          </div>
        )}

        {/* Footer */}
        <div className="mt-8 text-center">
          <p className="text-zinc-600 text-xs">
            Coach accounts are always free
          </p>
        </div>
      </div>
    </div>
  );
};

export default CoachSignup;
