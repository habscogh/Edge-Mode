import React, { useState, useRef } from 'react';
import { X, Download, Share2, Sparkles } from 'lucide-react';
import { Button } from './ui/button';
import { toast } from 'sonner';
import html2canvas from 'html2canvas';

const rarityColors = {
  legendary: { bg: 'from-yellow-900/80 to-amber-900/80', border: 'border-yellow-500', text: 'text-yellow-400' },
  rare: { bg: 'from-blue-900/80 to-cyan-900/80', border: 'border-blue-500', text: 'text-blue-400' },
  uncommon: { bg: 'from-green-900/80 to-emerald-900/80', border: 'border-green-500', text: 'text-green-400' },
  common: { bg: 'from-zinc-800/80 to-zinc-900/80', border: 'border-zinc-600', text: 'text-zinc-400' }
};

const ShareableStoryCard = ({ expedition, onClose }) => {
  const cardRef = useRef(null);
  const [generating, setGenerating] = useState(false);
  
  if (!expedition) return null;
  
  const colors = rarityColors[expedition.rarity] || rarityColors.common;
  
  const handleDownload = async () => {
    if (!cardRef.current) return;
    
    setGenerating(true);
    try {
      const canvas = await html2canvas(cardRef.current, {
        backgroundColor: '#09090b',
        scale: 2,
        useCORS: true
      });
      
      const link = document.createElement('a');
      link.download = `${expedition.pet_name}-adventure-${Date.now()}.png`;
      link.href = canvas.toDataURL('image/png');
      link.click();
      toast.success('Story card downloaded!');
    } catch (error) {
      toast.error('Failed to generate image');
    } finally {
      setGenerating(false);
    }
  };
  
  const handleShare = async () => {
    if (!cardRef.current) return;
    
    setGenerating(true);
    try {
      const canvas = await html2canvas(cardRef.current, {
        backgroundColor: '#09090b',
        scale: 2,
        useCORS: true
      });
      
      canvas.toBlob(async (blob) => {
        if (navigator.share && navigator.canShare) {
          const file = new File([blob], 'pet-adventure.png', { type: 'image/png' });
          if (navigator.canShare({ files: [file] })) {
            await navigator.share({
              title: `${expedition.pet_name}'s Adventure`,
              text: `Check out my pet's adventure on Edge Mode!`,
              files: [file]
            });
            toast.success('Shared successfully!');
          } else {
            handleDownload();
          }
        } else {
          handleDownload();
        }
        setGenerating(false);
      }, 'image/png');
    } catch (error) {
      toast.error('Failed to share');
      setGenerating(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/90 backdrop-blur-sm">
      <div className="relative w-full max-w-sm">
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute -top-12 right-0 p-2 rounded-full bg-zinc-800 hover:bg-zinc-700 text-white z-10"
        >
          <X className="w-5 h-5" />
        </button>
        
        {/* The shareable card */}
        <div
          ref={cardRef}
          className={`bg-gradient-to-br ${colors.bg} rounded-2xl overflow-hidden border-2 ${colors.border}`}
          style={{ padding: '24px' }}
        >
          {/* Header */}
          <div className="text-center mb-4">
            <div className="inline-flex items-center gap-2 bg-black/40 px-4 py-2 rounded-full">
              <Sparkles className="w-4 h-4 text-amber-400" />
              <span className="text-white font-bold text-sm">PET ADVENTURE</span>
            </div>
          </div>
          
          {/* Pet */}
          <div className="text-center mb-4">
            <div className="text-7xl mb-2 filter drop-shadow-lg">{expedition.pet_icon || '🐾'}</div>
            <h2 className="text-2xl font-bold text-white">{expedition.pet_name}</h2>
          </div>
          
          {/* Expedition name */}
          <div className="text-center mb-4">
            <span className={`text-sm px-3 py-1 rounded-full ${colors.text} bg-black/30 capitalize`}>
              {expedition.rarity} • {expedition.expedition_name}
            </span>
          </div>
          
          {/* Story */}
          <div className="bg-black/30 rounded-xl p-4 mb-4">
            <p className="text-white text-center leading-relaxed italic">
              "{expedition.story}"
            </p>
          </div>
          
          {/* Rewards */}
          <div className="flex justify-center gap-4 mb-4">
            <div className="bg-yellow-500/20 px-4 py-2 rounded-lg text-center">
              <div className="text-2xl font-bold text-yellow-400">+{expedition.rewards?.coins || 0}</div>
              <div className="text-xs text-yellow-400/70">Coins</div>
            </div>
            <div className="bg-purple-500/20 px-4 py-2 rounded-lg text-center">
              <div className="text-2xl font-bold text-purple-400">+{expedition.rewards?.xp || 0}</div>
              <div className="text-xs text-purple-400/70">XP</div>
            </div>
          </div>
          
          {/* Souvenir if found */}
          {expedition.rewards?.item && (
            <div className="text-center mb-4">
              <div className="inline-flex items-center gap-2 bg-amber-500/20 px-4 py-2 rounded-full">
                <span className="text-2xl">{expedition.rewards.item.icon}</span>
                <span className="text-amber-400 font-medium">{expedition.rewards.item.name}</span>
              </div>
            </div>
          )}
          
          {/* Branding */}
          <div className="text-center pt-2 border-t border-white/10">
            <p className="text-zinc-500 text-xs">Edge Mode • 1% Better Every Day</p>
          </div>
        </div>
        
        {/* Action buttons */}
        <div className="flex gap-3 mt-4">
          <Button
            onClick={handleDownload}
            disabled={generating}
            className="flex-1 bg-zinc-800 hover:bg-zinc-700 text-white"
          >
            <Download className="w-4 h-4 mr-2" />
            {generating ? 'Generating...' : 'Download'}
          </Button>
          <Button
            onClick={handleShare}
            disabled={generating}
            className="flex-1 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white"
          >
            <Share2 className="w-4 h-4 mr-2" />
            Share
          </Button>
        </div>
      </div>
    </div>
  );
};

export default ShareableStoryCard;
