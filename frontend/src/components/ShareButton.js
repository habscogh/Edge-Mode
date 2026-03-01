import React, { useState } from 'react';
import { Share2, Twitter, Facebook, Copy, Check, X } from 'lucide-react';
import { Button } from './ui/button';
import { toast } from 'sonner';

const APP_URL = 'https://edgemodeapp.com';

// Generate share text for different content types
export const generateShareText = (type, data) => {
  switch (type) {
    case 'badge':
      return {
        text: `I just earned the "${data.name}" badge on Edge Mode! ${data.icon}\n\n${data.description}\n\nTrack your progress: ${APP_URL}`,
        hashtags: 'EdgeMode,SelfImprovement,1PercentBetter'
      };
    
    case 'badge_summary':
      return {
        text: `I've earned ${data.earned} out of ${data.total} badges on Edge Mode! 🏆\n\nTracking my daily progress to become 1% better every day.\n\nJoin me: ${APP_URL}`,
        hashtags: 'EdgeMode,SelfImprovement,Achievements'
      };
    
    case 'streak':
      const streakEmoji = data.streak >= 30 ? '🔥🔥🔥' : data.streak >= 14 ? '🔥🔥' : '🔥';
      return {
        text: `${streakEmoji} ${data.streak}-day streak on Edge Mode!\n\nConsistency is key. I'm becoming 1% better every day.\n\nStart your journey: ${APP_URL}`,
        hashtags: 'EdgeMode,Streak,Consistency,SelfImprovement'
      };
    
    case 'weekly_stats':
      return {
        text: `📊 My Edge Mode Week:\n• ${data.sessions} sessions completed\n• ${data.minutes} minutes invested\n• ${data.consistency}% consistency\n\nBecoming 1% better every day! 💪\n\nTrack your progress: ${APP_URL}`,
        hashtags: 'EdgeMode,WeeklyReview,SelfImprovement'
      };
    
    case 'perfect_week':
      return {
        text: `✨ Perfect Week on Edge Mode!\n\nI logged sessions every single day this week. Consistency wins!\n\nJoin me: ${APP_URL}`,
        hashtags: 'EdgeMode,PerfectWeek,Consistency'
      };
    
    default:
      return {
        text: `I'm using Edge Mode to become 1% better every day! 💪\n\nJoin me: ${APP_URL}`,
        hashtags: 'EdgeMode,SelfImprovement'
      };
  }
};

// Share to Twitter/X
const shareToTwitter = (text, hashtags) => {
  const url = `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}&hashtags=${encodeURIComponent(hashtags)}`;
  window.open(url, '_blank', 'width=550,height=420');
};

// Share to Facebook
const shareToFacebook = (text) => {
  const url = `https://www.facebook.com/sharer/sharer.php?quote=${encodeURIComponent(text)}`;
  window.open(url, '_blank', 'width=550,height=420');
};

// Copy to clipboard
const copyToClipboard = async (text) => {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch (err) {
    // Fallback for older browsers
    const textArea = document.createElement('textarea');
    textArea.value = text;
    document.body.appendChild(textArea);
    textArea.select();
    document.execCommand('copy');
    document.body.removeChild(textArea);
    return true;
  }
};

// Use native Web Share API if available
const nativeShare = async (text, title) => {
  if (navigator.share) {
    try {
      await navigator.share({
        title: title || 'Edge Mode',
        text: text,
        url: APP_URL
      });
      return true;
    } catch (err) {
      if (err.name !== 'AbortError') {
        console.error('Share failed:', err);
      }
      return false;
    }
  }
  return false;
};

// Share Button Component
export const ShareButton = ({ type, data, variant = 'default', size = 'default', className = '' }) => {
  const [showMenu, setShowMenu] = useState(false);
  const [copied, setCopied] = useState(false);
  
  const { text, hashtags } = generateShareText(type, data);
  
  const handleShare = async () => {
    // Try native share first (mobile)
    const shared = await nativeShare(text, 'Edge Mode');
    if (!shared) {
      setShowMenu(true);
    }
  };
  
  const handleTwitter = () => {
    shareToTwitter(text, hashtags);
    setShowMenu(false);
  };
  
  const handleFacebook = () => {
    shareToFacebook(text);
    setShowMenu(false);
  };
  
  const handleCopy = async () => {
    const success = await copyToClipboard(text);
    if (success) {
      setCopied(true);
      toast.success('Copied to clipboard!');
      setTimeout(() => {
        setCopied(false);
        setShowMenu(false);
      }, 1500);
    }
  };
  
  return (
    <div className="relative">
      <Button
        variant={variant}
        size={size}
        onClick={handleShare}
        className={className}
        data-testid="share-button"
      >
        <Share2 className="w-4 h-4 mr-2" />
        Share
      </Button>
      
      {/* Share Menu Dropdown */}
      {showMenu && (
        <>
          {/* Backdrop */}
          <div 
            className="fixed inset-0 z-40" 
            onClick={() => setShowMenu(false)}
          />
          
          {/* Menu */}
          <div className="absolute right-0 top-full mt-2 z-50 bg-zinc-900 border border-zinc-700 rounded-lg shadow-xl p-2 min-w-[180px]">
            <button
              onClick={handleTwitter}
              className="w-full flex items-center gap-3 px-3 py-2 rounded-md hover:bg-zinc-800 transition-colors text-left"
              data-testid="share-twitter"
            >
              <Twitter className="w-4 h-4 text-[#1DA1F2]" />
              <span className="text-white text-sm">Twitter / X</span>
            </button>
            
            <button
              onClick={handleFacebook}
              className="w-full flex items-center gap-3 px-3 py-2 rounded-md hover:bg-zinc-800 transition-colors text-left"
              data-testid="share-facebook"
            >
              <Facebook className="w-4 h-4 text-[#4267B2]" />
              <span className="text-white text-sm">Facebook</span>
            </button>
            
            <button
              onClick={handleCopy}
              className="w-full flex items-center gap-3 px-3 py-2 rounded-md hover:bg-zinc-800 transition-colors text-left"
              data-testid="share-copy"
            >
              {copied ? (
                <Check className="w-4 h-4 text-green-500" />
              ) : (
                <Copy className="w-4 h-4 text-zinc-400" />
              )}
              <span className="text-white text-sm">
                {copied ? 'Copied!' : 'Copy to clipboard'}
              </span>
            </button>
          </div>
        </>
      )}
    </div>
  );
};

// Inline Share Icons (for compact layouts)
export const ShareIcons = ({ type, data, className = '' }) => {
  const [copied, setCopied] = useState(false);
  const { text, hashtags } = generateShareText(type, data);
  
  const handleCopy = async () => {
    const success = await copyToClipboard(text);
    if (success) {
      setCopied(true);
      toast.success('Copied to clipboard!');
      setTimeout(() => setCopied(false), 2000);
    }
  };
  
  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <button
        onClick={() => shareToTwitter(text, hashtags)}
        className="p-2 rounded-full bg-zinc-800 hover:bg-[#1DA1F2]/20 transition-colors"
        title="Share on Twitter"
        data-testid="share-icon-twitter"
      >
        <Twitter className="w-4 h-4 text-[#1DA1F2]" />
      </button>
      
      <button
        onClick={() => shareToFacebook(text)}
        className="p-2 rounded-full bg-zinc-800 hover:bg-[#4267B2]/20 transition-colors"
        title="Share on Facebook"
        data-testid="share-icon-facebook"
      >
        <Facebook className="w-4 h-4 text-[#4267B2]" />
      </button>
      
      <button
        onClick={handleCopy}
        className="p-2 rounded-full bg-zinc-800 hover:bg-zinc-700 transition-colors"
        title="Copy to clipboard"
        data-testid="share-icon-copy"
      >
        {copied ? (
          <Check className="w-4 h-4 text-green-500" />
        ) : (
          <Copy className="w-4 h-4 text-zinc-400" />
        )}
      </button>
    </div>
  );
};
