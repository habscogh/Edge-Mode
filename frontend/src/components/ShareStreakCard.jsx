import React, { useRef, useState } from 'react';
import { Flame, Zap, Share2, Download, X, Instagram } from 'lucide-react';
import { Button } from './ui/button';
import html2canvas from 'html2canvas';

export const StreakCard = ({ streak, totalMinutes, consistency, username }) => {
  return (
    <div 
      className="w-[360px] h-[640px] bg-gradient-to-br from-zinc-900 via-zinc-800 to-zinc-900 rounded-3xl p-8 flex flex-col items-center justify-between relative overflow-hidden"
      style={{ fontFamily: 'Inter, system-ui, sans-serif' }}
    >
      {/* Background decoration */}
      <div className="absolute inset-0 opacity-20">
        <div className="absolute top-10 left-10 w-32 h-32 bg-primary rounded-full blur-3xl" />
        <div className="absolute bottom-20 right-10 w-40 h-40 bg-orange-500 rounded-full blur-3xl" />
      </div>
      
      {/* Content */}
      <div className="relative z-10 flex flex-col items-center w-full h-full">
        {/* Logo */}
        <div className="flex items-center gap-2 mb-8">
          <Zap className="w-8 h-8 text-primary" />
          <span className="text-2xl font-bold text-white tracking-tight">EDGE MODE</span>
        </div>
        
        {/* Main stat */}
        <div className="flex-1 flex flex-col items-center justify-center">
          <Flame className="w-20 h-20 text-orange-500 mb-4" />
          <div className="text-8xl font-black text-white mb-2">{streak}</div>
          <div className="text-2xl font-bold text-zinc-400 uppercase tracking-widest">
            Day Streak
          </div>
        </div>
        
        {/* Stats row */}
        <div className="w-full flex justify-around mb-8 py-4 border-y border-zinc-700">
          <div className="text-center">
            <div className="text-3xl font-bold text-white">{totalMinutes}</div>
            <div className="text-xs text-zinc-500 uppercase tracking-wide">Minutes</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-primary">{consistency}%</div>
            <div className="text-xs text-zinc-500 uppercase tracking-wide">Consistency</div>
          </div>
        </div>
        
        {/* Footer */}
        <div className="text-center">
          <div className="text-zinc-500 text-sm mb-1">@{username || 'EdgeMode'}</div>
          <div className="text-zinc-600 text-xs">edgemodeapp.com</div>
        </div>
      </div>
    </div>
  );
};

export const ShareStreakModal = ({ streak, totalMinutes, consistency, username, onClose }) => {
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
    link.download = `edge-mode-${streak}-day-streak.png`;
    link.href = generatedImage;
    link.click();
  };

  const shareToInstagram = async () => {
    if (!generatedImage) {
      await generateImage();
    }
    
    // For mobile, try native share
    if (navigator.share && navigator.canShare) {
      try {
        const response = await fetch(generatedImage);
        const blob = await response.blob();
        const file = new File([blob], `edge-mode-streak.png`, { type: 'image/png' });
        
        await navigator.share({
          files: [file],
          title: `My ${streak}-day streak on Edge Mode!`,
          text: `I'm on a ${streak}-day streak! 🔥 #EdgeMode #1PercentBetter`,
        });
      } catch (error) {
        // Fallback to download
        downloadImage();
      }
    } else {
      // Desktop fallback - just download
      downloadImage();
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80">
      <div className="bg-zinc-900 border border-zinc-700 rounded-2xl p-6 max-w-lg w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-xl font-bold text-white">Share Your Streak</h3>
          <button onClick={onClose} className="text-zinc-500 hover:text-white">
            <X className="w-6 h-6" />
          </button>
        </div>
        
        {/* Preview Card */}
        <div className="flex justify-center mb-6 transform scale-[0.6] origin-top -my-20">
          <div ref={cardRef}>
            <StreakCard 
              streak={streak}
              totalMinutes={totalMinutes}
              consistency={consistency}
              username={username}
            />
          </div>
        </div>
        
        {/* Generated Image Preview */}
        {generatedImage && (
          <div className="mb-6 flex justify-center">
            <img 
              src={generatedImage} 
              alt="Generated streak card" 
              className="max-h-40 rounded-lg border border-zinc-700"
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
            >
              {isGenerating ? 'Generating...' : 'Generate Image'}
            </Button>
          ) : (
            <>
              <Button
                onClick={shareToInstagram}
                className="w-full bg-gradient-to-r from-purple-500 to-pink-500 text-white hover:opacity-90"
              >
                <Instagram className="w-5 h-5 mr-2" />
                Share to Instagram/TikTok
              </Button>
              <Button
                onClick={downloadImage}
                variant="outline"
                className="w-full border-zinc-700 text-zinc-300 hover:bg-zinc-800"
              >
                <Download className="w-5 h-5 mr-2" />
                Download Image
              </Button>
            </>
          )}
        </div>
        
        <p className="text-zinc-500 text-xs text-center mt-4">
          Save the image and share to your favorite social platform!
        </p>
      </div>
    </div>
  );
};
