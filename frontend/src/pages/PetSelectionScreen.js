import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'sonner';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { 
  ArrowLeft,
  Check,
  Sparkles,
  Star,
  ShoppingBag,
  ChevronRight,
  Coins,
  Lock,
  Crown
} from 'lucide-react';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

// Rarity styles
const rarityStyles = {
  common: { bg: 'bg-zinc-800/50', border: 'border-zinc-600', text: 'text-zinc-400' },
  uncommon: { bg: 'bg-green-900/20', border: 'border-green-500/50', text: 'text-green-400' },
  rare: { bg: 'bg-blue-900/20', border: 'border-blue-500/50', text: 'text-blue-400' },
  epic: { bg: 'bg-purple-900/20', border: 'border-purple-500/50', text: 'text-purple-400' },
  legendary: { bg: 'bg-yellow-900/20', border: 'border-yellow-500/50', text: 'text-yellow-400' }
};

const categoryIcons = {
  animals: '🐾',
  fantasy: '🐉',
  abstract: '✨'
};

const PetSelectionScreen = () => {
  const navigate = useNavigate();
  const [availablePets, setAvailablePets] = useState({ starters: [], shop_pets: [] });
  const [selectedPet, setSelectedPet] = useState(null);
  const [customName, setCustomName] = useState('');
  const [userCoins, setUserCoins] = useState(0);
  const [hasStarterPet, setHasStarterPet] = useState(false);
  const [loading, setLoading] = useState(true);
  const [selecting, setSelecting] = useState(false);
  const [activeTab, setActiveTab] = useState('starters'); // 'starters' or 'shop'

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [petsRes, myPetRes, statusRes] = await Promise.all([
        axios.get(`${API}/pets/available`),
        axios.get(`${API}/pets/my-pet`),
        axios.get(`${API}/engagement/status`)
      ]);

      setAvailablePets(petsRes.data);
      setHasStarterPet(myPetRes.data.has_pet);
      setUserCoins(statusRes.data.coins || 0);

      // If user already has a pet, switch to shop tab
      if (myPetRes.data.has_pet) {
        setActiveTab('shop');
      }
    } catch (error) {
      console.error('Failed to fetch pet data:', error);
      toast.error('Failed to load pets');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectPet = async () => {
    if (!selectedPet || selecting) return;

    setSelecting(true);
    try {
      const response = await axios.post(`${API}/pets/select`, {
        pet_type: selectedPet.type,
        pet_name: customName || null
      });

      toast.success(response.data.message);
      navigate('/dashboard');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to select pet');
    } finally {
      setSelecting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-black p-4 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
      </div>
    );
  }

  const displayPets = activeTab === 'starters' ? availablePets.starters : availablePets.shop_pets;

  return (
    <div className="min-h-screen bg-black pb-24" data-testid="pet-selection-screen">
      {/* Header */}
      <div className="sticky top-0 z-10 bg-black/95 backdrop-blur-sm border-b border-zinc-800 p-4">
        <div className="flex items-center gap-3 mb-4">
          <button
            onClick={() => navigate(-1)}
            className="p-2 -ml-2 text-zinc-400 hover:text-white transition-colors"
          >
            <ArrowLeft className="w-6 h-6" />
          </button>
          <div>
            <h1 className="text-xl font-bold text-white flex items-center gap-2">
              <span>🐾</span> Choose Your Companion
            </h1>
            <p className="text-zinc-400 text-sm">Your pet grows with your progress!</p>
          </div>
        </div>

        {/* Coins display */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex gap-2">
            <Button
              onClick={() => setActiveTab('starters')}
              variant={activeTab === 'starters' ? 'default' : 'outline'}
              size="sm"
              disabled={hasStarterPet}
              className={activeTab === 'starters' ? 'bg-primary text-black' : ''}
            >
              <Sparkles className="w-4 h-4 mr-1" />
              Free Starters
              {hasStarterPet && <Check className="w-3 h-3 ml-1" />}
            </Button>
            <Button
              onClick={() => setActiveTab('shop')}
              variant={activeTab === 'shop' ? 'default' : 'outline'}
              size="sm"
              className={activeTab === 'shop' ? 'bg-primary text-black' : ''}
            >
              <ShoppingBag className="w-4 h-4 mr-1" /> Pet Shop
            </Button>
          </div>
          <div className="flex items-center gap-1 bg-yellow-500/20 text-yellow-400 px-3 py-1.5 rounded-full text-sm">
            <Coins className="w-4 h-4" />
            <span className="font-bold">{userCoins}</span>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="p-4">
        {/* Starter selection info */}
        {activeTab === 'starters' && !hasStarterPet && (
          <div className="bg-gradient-to-r from-purple-900/30 to-pink-900/30 border border-purple-500/30 rounded-xl p-4 mb-6">
            <div className="flex items-center gap-2 mb-2">
              <Star className="w-5 h-5 text-purple-400" />
              <span className="text-white font-bold">Choose Your First Pet!</span>
            </div>
            <p className="text-zinc-400 text-sm">
              Pick a free starter companion. Your pet will evolve as you maintain your streak!
            </p>
          </div>
        )}

        {hasStarterPet && activeTab === 'starters' && (
          <div className="bg-zinc-900 border border-zinc-700 rounded-xl p-4 mb-6 text-center">
            <Check className="w-8 h-8 text-green-500 mx-auto mb-2" />
            <p className="text-white font-bold">You already have a starter pet!</p>
            <p className="text-zinc-400 text-sm mt-1">Check out the Pet Shop for more companions.</p>
            <Button
              onClick={() => setActiveTab('shop')}
              className="mt-3 bg-primary text-black"
              size="sm"
            >
              <ShoppingBag className="w-4 h-4 mr-1" /> Browse Shop
            </Button>
          </div>
        )}

        {/* Pet grid */}
        <div className="grid grid-cols-2 gap-4">
          {displayPets.map((pet) => {
            const style = rarityStyles[pet.rarity] || rarityStyles.common;
            const isSelected = selectedPet?.type === pet.type;
            const canAfford = userCoins >= pet.price;
            const isLocked = !pet.is_starter && !canAfford && !pet.owned;

            return (
              <div
                key={pet.type}
                onClick={() => !pet.owned && !isLocked && setSelectedPet(pet)}
                className={`relative rounded-xl p-4 border-2 transition-all cursor-pointer ${style.bg} ${
                  isSelected 
                    ? 'border-primary ring-2 ring-primary/30' 
                    : pet.owned 
                      ? 'border-green-500/50 opacity-75'
                      : isLocked
                        ? 'border-zinc-700 opacity-50'
                        : style.border
                } ${!pet.owned && !isLocked ? 'hover:scale-[1.02]' : ''}`}
                data-testid={`pet-option-${pet.type}`}
              >
                {/* Rarity badge */}
                <div className={`absolute top-2 right-2 text-xs px-2 py-0.5 rounded-full bg-black/50 ${style.text}`}>
                  {pet.rarity}
                </div>

                {/* Category icon */}
                <div className="absolute top-2 left-2 text-lg">
                  {categoryIcons[pet.category]}
                </div>

                {/* Pet preview */}
                <div className="text-center py-4">
                  <div className="text-5xl mb-2">{pet.preview_icon}</div>
                  <div className="text-zinc-500 text-xs">→</div>
                  <div className="text-3xl opacity-50">{pet.max_icon}</div>
                </div>

                {/* Pet info */}
                <h3 className="text-white font-bold text-sm text-center">{pet.name}</h3>
                <p className="text-zinc-400 text-xs text-center mt-1 line-clamp-2">{pet.description}</p>

                {/* Price/Status */}
                <div className="mt-3 text-center">
                  {pet.owned ? (
                    <span className="text-green-400 text-sm flex items-center justify-center gap-1">
                      <Check className="w-4 h-4" /> Owned
                    </span>
                  ) : pet.is_starter ? (
                    <span className="text-purple-400 text-sm font-bold">FREE</span>
                  ) : (
                    <div className={`flex items-center justify-center gap-1 ${canAfford ? 'text-yellow-400' : 'text-zinc-500'}`}>
                      {!canAfford && <Lock className="w-3 h-3" />}
                      <Coins className="w-4 h-4" />
                      <span className="font-bold">{pet.price}</span>
                    </div>
                  )}
                </div>

                {/* Selected indicator */}
                {isSelected && (
                  <div className="absolute -top-1 -right-1 w-6 h-6 bg-primary rounded-full flex items-center justify-center">
                    <Check className="w-4 h-4 text-black" />
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Selection panel */}
        {selectedPet && (
          <div className="fixed bottom-0 left-0 right-0 bg-zinc-900 border-t border-zinc-700 p-4 safe-area-inset-bottom">
            <div className="flex items-center gap-4 mb-3">
              <div className="text-4xl">{selectedPet.preview_icon}</div>
              <div className="flex-1">
                <h3 className="text-white font-bold">{selectedPet.name}</h3>
                <p className="text-zinc-400 text-xs">{selectedPet.description}</p>
              </div>
            </div>

            {/* Custom name input */}
            <div className="mb-3">
              <Input
                placeholder={`Name your pet (default: ${selectedPet.name})`}
                value={customName}
                onChange={(e) => setCustomName(e.target.value)}
                className="bg-zinc-800 border-zinc-700"
                maxLength={20}
                data-testid="pet-name-input"
              />
            </div>

            <Button
              onClick={handleSelectPet}
              disabled={selecting}
              className="w-full bg-primary text-black hover:bg-primary/90 font-bold"
              data-testid="confirm-pet-btn"
            >
              {selecting ? 'Selecting...' : selectedPet.is_starter ? 'Choose This Pet!' : `Buy for ${selectedPet.price} Coins`}
            </Button>
          </div>
        )}
      </div>
    </div>
  );
};

export default PetSelectionScreen;
