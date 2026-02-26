import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { ArrowLeft, Mail, CheckCircle2 } from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export const ForgotPassword = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [email, setEmail] = useState('');
  const [resetToken, setResetToken] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleRequestReset = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await axios.post(`${API}/auth/forgot-password`, { email });
      if (response.data.reset_token) {
        setResetToken(response.data.reset_token);
      }
      setStep(2);
    } catch (err) {
      setError('Failed to send reset email');
    } finally {
      setLoading(false);
    }
  };

  const handleResetPassword = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await axios.post(`${API}/auth/reset-password`, {
        token: resetToken,
        new_password: newPassword
      });
      setStep(3);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to reset password');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#09090b] flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {step !== 3 && (
          <button
            onClick={() => navigate('/auth')}
            className="flex items-center gap-2 text-zinc-400 hover:text-white mb-6 transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
            <span className="font-body">Back to login</span>
          </button>
        )}

        {step === 1 && (
          <div className="bg-zinc-950 border border-zinc-800 rounded-md p-6">
            <h1 className="text-2xl font-heading font-bold uppercase text-white mb-2">Forgot Password</h1>
            <p className="text-zinc-400 text-sm font-body mb-6">Enter your email to reset your password</p>

            <form onSubmit={handleRequestReset}>
              <Input
                type="email"
                placeholder="Email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="bg-zinc-900 border-zinc-800 text-white font-body mb-4"
              />

              {error && <div className="text-red-500 text-sm mb-4">{error}</div>}

              <Button
                type="submit"
                disabled={loading}
                className="w-full bg-primary text-primary-foreground hover:bg-primary/90 font-heading uppercase"
              >
                {loading ? 'Sending...' : 'Send Reset Link'}
              </Button>
            </form>
          </div>
        )}

        {step === 2 && (
          <div className="bg-zinc-950 border border-zinc-800 rounded-md p-6">
            <Mail className="w-12 h-12 text-primary mx-auto mb-4" />
            <h1 className="text-2xl font-heading font-bold uppercase text-white mb-2 text-center">Check Your Email</h1>
            <p className="text-zinc-400 text-sm font-body mb-6 text-center">
              We've sent a password reset link to {email}
            </p>

            {resetToken && (
              <form onSubmit={handleResetPassword}>
                <p className="text-zinc-500 text-xs mb-2">For testing: Use token {resetToken.substring(0, 10)}...</p>
                <Input
                  type="text"
                  placeholder="Reset token"
                  value={resetToken}
                  onChange={(e) => setResetToken(e.target.value)}
                  required
                  className="bg-zinc-900 border-zinc-800 text-white font-mono mb-3"
                />
                <Input
                  type="password"
                  placeholder="New password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  required
                  className="bg-zinc-900 border-zinc-800 text-white font-body mb-4"
                />

                {error && <div className="text-red-500 text-sm mb-4">{error}</div>}

                <Button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-primary text-primary-foreground hover:bg-primary/90 font-heading uppercase"
                >
                  {loading ? 'Resetting...' : 'Reset Password'}
                </Button>
              </form>
            )}
          </div>
        )}

        {step === 3 && (
          <div className="bg-zinc-950 border border-zinc-800 rounded-md p-6 text-center">
            <CheckCircle2 className="w-16 h-16 text-primary mx-auto mb-4" />
            <h1 className="text-2xl font-heading font-bold uppercase text-white mb-2">Password Reset!</h1>
            <p className="text-zinc-400 text-sm font-body mb-6">
              Your password has been successfully reset
            </p>
            <Button
              onClick={() => navigate('/auth')}
              className="bg-primary text-primary-foreground hover:bg-primary/90 font-heading uppercase"
            >
              Back to Login
            </Button>
          </div>
        )}
      </div>
    </div>
  );
};