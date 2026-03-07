import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { X, Sparkles, Send } from 'lucide-react';
import { Button } from './ui/button';
import { useAuth } from '../context/AuthContext';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const MOODS = [
  { value: 'great', emoji: '🔥', label: 'Great' },
  { value: 'good', emoji: '😊', label: 'Good' },
  { value: 'okay', emoji: '😐', label: 'Okay' },
  { value: 'tough', emoji: '💪', label: 'Tough' },
];

export const ReflectionModal = ({ isOpen, onClose, sessionId, onComplete }) => {
  const { user, token } = useAuth();
  const [prompt, setPrompt] = useState('');
  const [response, setResponse] = useState('');
  const [mood, setMood] = useState(null);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (isOpen && user && token) {
      fetchPrompt();
    } else if (isOpen && !user) {
      setPrompt("What did you learn today?");
    }
  }, [isOpen, user, token]);

  const fetchPrompt = async () => {
    if (!user || !token) {
      setPrompt("What did you learn today?");
      return;
    }
    
    setLoading(true);
    try {
      const res = await axios.get(`${API}/reflections/prompt`);
      setPrompt(res.data.prompt);
    } catch (error) {
      console.error('Failed to fetch prompt:', error);
      setPrompt("What did you learn today?");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    if (!response.trim()) return;
    
    setSubmitting(true);
    try {
      await axios.post(`${API}/reflections/`, {
        prompt,
        response: response.trim(),
        session_id: sessionId,
        mood
      });
      onComplete && onComplete();
      onClose();
      // Reset state
      setResponse('');
      setMood(null);
    } catch (error) {
      console.error('Failed to save reflection:', error);
    } finally {
      setSubmitting(false);
    }
  };

  const handleSkip = () => {
    setResponse('');
    setMood(null);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-zinc-900 border border-zinc-800 rounded-xl w-full max-w-md overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="bg-gradient-to-r from-primary/20 to-emerald-500/20 p-4 border-b border-zinc-800">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-primary" />
              <h2 className="text-lg font-heading font-bold text-white uppercase tracking-wide">
                Quick Reflection
              </h2>
            </div>
            <button
              onClick={handleSkip}
              className="text-zinc-500 hover:text-white transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
          <p className="text-zinc-400 text-sm mt-1">
            Take a moment to reflect on your session
          </p>
        </div>

        {/* Content */}
        <div className="p-4 space-y-4">
          {/* Prompt */}
          <div className="bg-zinc-800/50 rounded-lg p-3 border border-zinc-700">
            <p className="text-white font-medium text-center">
              {loading ? '...' : `"${prompt}"`}
            </p>
          </div>

          {/* Mood selector */}
          <div>
            <p className="text-zinc-400 text-sm mb-2">How are you feeling?</p>
            <div className="flex gap-2">
              {MOODS.map((m) => (
                <button
                  key={m.value}
                  onClick={() => setMood(m.value)}
                  className={`flex-1 py-2 px-3 rounded-lg border transition-all ${
                    mood === m.value
                      ? 'bg-primary/20 border-primary text-white'
                      : 'bg-zinc-800 border-zinc-700 text-zinc-400 hover:border-zinc-600'
                  }`}
                >
                  <span className="text-xl">{m.emoji}</span>
                  <span className="text-xs block mt-1">{m.label}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Response input */}
          <div>
            <textarea
              data-testid="reflection-input"
              value={response}
              onChange={(e) => setResponse(e.target.value)}
              placeholder="Write your thoughts..."
              className="w-full bg-zinc-800 border border-zinc-700 rounded-lg p-3 text-white placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent resize-none h-24"
              maxLength={500}
            />
            <p className="text-zinc-500 text-xs text-right mt-1">
              {response.length}/500
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-zinc-800 flex gap-3">
          <Button
            variant="ghost"
            onClick={handleSkip}
            className="flex-1 text-zinc-400"
          >
            Skip
          </Button>
          <Button
            data-testid="reflection-submit-btn"
            onClick={handleSubmit}
            disabled={!response.trim() || submitting}
            className="flex-1 bg-primary text-primary-foreground hover:bg-primary/90"
          >
            {submitting ? (
              'Saving...'
            ) : (
              <>
                <Send className="w-4 h-4 mr-2" />
                Save
              </>
            )}
          </Button>
        </div>
      </div>
    </div>
  );
};
