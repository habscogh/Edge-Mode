import React, { useRef, useState } from 'react';
import { Zap, Download, X, Instagram, Trophy, Star, Flame, Target, Clock, CheckCircle } from 'lucide-react';
import { Button } from './ui/button';
import html2canvas from 'html2canvas';
import { format } from 'date-fns';

const BADGE_ICONS = {
  '🏆': Trophy,
  '🔥': Flame,
  '💯': CheckCircle,
  '⏱️': Clock,
  '✨': Star,
  '🎯': Target
};

// Visual Achievement Card for sharing
export const AchievementCard = ({ badge, username }) => {
  const IconComponent = BADGE_ICONS[badge.icon] || Trophy;
  
  // Generate gradient based on badge category
  const getGradient = () => {
    switch (badge.category) {
      case 'streak':
        return 'from-orange-600 via-red-600 to-orange-700';
      case 'milestone':
        return 'from-yellow-600 via-amber-600 to-yellow-700';
      case 'consistency':
        return 'from-emerald-600 via-green-600 to-emerald-700';
      case 'mastery':
        return 'from-purple-600 via-violet-600 to-purple-700';
      default:
        return 'from-primary via-green-600 to-emerald-700';
    }
  };

  return (
    <div 
      className={`w-[360px] h-[480px] bg-gradient-to-br ${getGradient()} rounded-3xl p-8 flex flex-col items-center justify-between relative overflow-hidden`}
      style={{ fontFamily: 'Inter, system-ui, sans-serif' }}
    >
      {/* Background decoration */}
      <div className="absolute inset-0 opacity-30">
        <div className="absolute top-10 left-10 w-40 h-40 bg-white rounded-full blur-3xl" />
        <div className="absolute bottom-20 right-10 w-32 h-32 bg-white rounded-full blur-3xl" />
      </div>
      
      {/* Pattern overlay */}
      <div className="absolute inset-0 opacity-10" style={{
        backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`
      }} />
      
      {/* Content */}
      <div className="relative z-10 flex flex-col items-center w-full h-full">
        {/* Logo */}
        <div className="flex items-center gap-2 mb-4">
          <Zap className="w-6 h-6 text-white" />
          <span className="text-xl font-bold text-white tracking-tight">EDGE MODE</span>
        </div>
        
        {/* Achievement unlocked label */}
        <div className="bg-white/20 backdrop-blur-sm px-4 py-1 rounded-full mb-6">
          <span className="text-white text-xs font-bold uppercase tracking-widest">Achievement Unlocked</span>
        </div>
        
        {/* Main badge */}
        <div className="flex-1 flex flex-col items-center justify-center">
          <div className="w-28 h-28 bg-white/20 backdrop-blur-sm rounded-full flex items-center justify-center mb-4 border-4 border-white/30">
            <span className="text-6xl">{badge.icon}</span>
          </div>
          <div className="text-3xl font-black text-white text-center mb-2 uppercase tracking-wide">
            {badge.name}
          </div>
          <div className="text-white/80 text-center text-sm max-w-[280px]">
            {badge.description}
          </div>
        </div>
        
        {/* Footer */}
        <div className="text-center pt-4 border-t border-white/20 w-full">
          <div className="text-white/90 text-sm font-medium mb-1">@{username || 'EdgeMode'}</div>
          <div className="text-white/60 text-xs">edgemodeapp.com</div>
        </div>
      </div>
    </div>
  );
};

// Modal to share achievement
export const ShareAchievementModal = ({ badge, username, onClose }) => {
  const cardRef = useRef(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedImage, setGeneratedImage] = useState(null);

  const generateImage = async () => {
    if (!cardRef.current) return;
    setIsGenerating(true);
    
    try {
      const canvas = await html2canvas(cardRef.current, {
        backgroundColor: null,
        scale: 2,
        useCORS: true,
        logging: false,
      });
      
      const dataUrl = canvas.toDataURL('image/png');
      setGeneratedImage(dataUrl);
    } catch (error) {
      console.error('Failed to generate image:', error);
    } finally {
      setIsGenerating(false);
    }
  };

  const downloadImage = () => {
    if (!generatedImage) return;
    
    const link = document.createElement('a');
    link.download = `edge-mode-${badge.name.toLowerCase().replace(/\s+/g, '-')}.png`;
    link.href = generatedImage;
    link.click();
  };

  const shareNative = async () => {
    if (!generatedImage) {
      await generateImage();
      return;
    }
    
    // For mobile, try native share
    if (navigator.share && navigator.canShare) {
      try {
        const response = await fetch(generatedImage);
        const blob = await response.blob();
        const file = new File([blob], `edge-mode-badge.png`, { type: 'image/png' });
        
        if (navigator.canShare({ files: [file] })) {
          await navigator.share({
            files: [file],
            title: `I earned the ${badge.name} badge!`,
            text: `I just unlocked the "${badge.name}" badge on Edge Mode! ${badge.icon} #EdgeMode #1PercentBetter`,
          });
          return;
        }
      } catch (error) {
        if (error.name !== 'AbortError') {
          console.error('Share failed:', error);
        }
      }
    }
    // Fallback to download
    downloadImage();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80" data-testid="share-achievement-modal">
      <div className="bg-zinc-900 border border-zinc-700 rounded-2xl p-6 max-w-lg w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-bold text-white">Share Achievement</h3>
          <button onClick={onClose} className="text-zinc-500 hover:text-white" data-testid="close-share-modal">
            <X className="w-6 h-6" />
          </button>
        </div>
        
        {/* Preview Card */}
        <div className="flex justify-center mb-4 transform scale-[0.55] origin-top -my-16">
          <div ref={cardRef}>
            <AchievementCard badge={badge} username={username} />
          </div>
        </div>
        
        {/* Generated Image Preview */}
        {generatedImage && (
          <div className="mb-4 flex justify-center">
            <img 
              src={generatedImage} 
              alt="Generated achievement card" 
              className="max-h-32 rounded-lg border border-zinc-700"
            />
          </div>
        )}
        
        {/* Actions */}
        <div className="space-y-3">
          {!generatedImage ? (
            <Button
              onClick={generateImage}
              disabled={isGenerating}
              className="w-full bg-primary text-primary-foreground hover:bg-primary/90"
              data-testid="generate-image-btn"
            >
              {isGenerating ? 'Generating...' : 'Generate Shareable Image'}
            </Button>
          ) : (
            <>
              <Button
                onClick={shareNative}
                className="w-full bg-gradient-to-r from-purple-500 to-pink-500 text-white hover:opacity-90"
                data-testid="share-native-btn"
              >
                <Instagram className="w-5 h-5 mr-2" />
                Share to Social Media
              </Button>
              <Button
                onClick={downloadImage}
                variant="outline"
                className="w-full border-zinc-700 text-zinc-300 hover:bg-zinc-800"
                data-testid="download-image-btn"
              >
                <Download className="w-5 h-5 mr-2" />
                Download Image
              </Button>
            </>
          )}
        </div>
        
        <p className="text-zinc-500 text-xs text-center mt-4">
          Perfect for Instagram Stories, TikTok, or anywhere you want to flex your progress! 💪
        </p>
      </div>
    </div>
  );
};
