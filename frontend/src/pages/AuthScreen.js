import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Flame } from 'lucide-react';

export const AuthScreen = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [username, setUsername] = useState('');
  const [age, setAge] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login, register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (isLogin) {
        await login(email, password);
        navigate('/dashboard');
      } else {
        if (parseInt(age) < 12 || parseInt(age) > 19) {
          setError('Age must be between 12 and 19');
          setLoading(false);
          return;
        }
        await register(email, username, password, age);
        navigate('/onboarding');
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Authentication failed');
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#09090b] flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-3 mb-4">
            <Flame className="w-10 h-10 text-primary" />
            <h1 className="text-4xl font-heading font-bold uppercase tracking-tight text-white">EDGE MODE</h1>
          </div>
          <p className="text-zinc-400 text-sm font-body">Be Better Than Yesterday</p>
        </div>

        <div className="bg-zinc-950 border border-zinc-800 rounded-md p-6">
          <div className="flex gap-2 mb-6">
            <Button
              data-testid="login-tab-btn"
              onClick={() => setIsLogin(true)}
              variant={isLogin ? 'default' : 'ghost'}
              className={`flex-1 font-heading uppercase tracking-wide ${isLogin ? 'bg-primary text-primary-foreground' : 'text-zinc-400'}`}
            >
              Login
            </Button>
            <Button
              data-testid="signup-tab-btn"
              onClick={() => setIsLogin(false)}
              variant={!isLogin ? 'default' : 'ghost'}
              className={`flex-1 font-heading uppercase tracking-wide ${!isLogin ? 'bg-primary text-primary-foreground' : 'text-zinc-400'}`}
            >
              Sign Up
            </Button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Input
                data-testid="email-input"
                type="email"
                placeholder="Email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="bg-zinc-900 border-zinc-800 text-white font-body focus:ring-2 focus:ring-primary"
              />
            </div>

            {!isLogin && (
              <>
                <div>
                  <Input
                    data-testid="username-input"
                    type="text"
                    placeholder="Username"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    required
                    className="bg-zinc-900 border-zinc-800 text-white font-body focus:ring-2 focus:ring-primary"
                  />
                </div>
                <div>
                  <Input
                    data-testid="age-input"
                    type="number"
                    placeholder="Age (12-19)"
                    value={age}
                    onChange={(e) => setAge(e.target.value)}
                    required
                    min="12"
                    max="19"
                    className="bg-zinc-900 border-zinc-800 text-white font-mono focus:ring-2 focus:ring-primary"
                  />
                </div>
              </>
            )}

            <div>
              <Input
                data-testid="password-input"
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="bg-zinc-900 border-zinc-800 text-white font-body focus:ring-2 focus:ring-primary"
              />
            </div>

            {error && (
              <div data-testid="auth-error" className="text-red-500 text-sm font-body">
                {error}
              </div>
            )}

            <Button
              data-testid="auth-submit-btn"
              type="submit"
              disabled={loading}
              className="w-full bg-primary text-primary-foreground hover:bg-primary/90 font-heading uppercase tracking-wide font-bold"
            >
              {loading ? 'Processing...' : isLogin ? 'Login' : 'Create Account'}
            </Button>

            {isLogin && (
              <button
                type="button"
                onClick={() => navigate('/forgot-password')}
                className="w-full text-center text-sm text-zinc-400 hover:text-primary transition-colors mt-2"
              >
                Forgot password?
              </button>
            )}
          </form>
        </div>
      </div>
    </div>
  );
};