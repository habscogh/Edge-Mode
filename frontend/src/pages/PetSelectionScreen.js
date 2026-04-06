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
  Coins,
  Lock,
  RefreshCw
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
  fantasy: '🐉',
  scifi: '👾',
  activity: '⚡',
  gaming: '🎮'
};

const PetSelectionScreen = () => {
  const navigate = useNavigate();
  const [starters, setStarters] = useState([]);
  const [shopPets, setShopPets] = useState([]);
  const [selectedPet, setSelectedPet] = useState(null);
  const [customName, setCustomName] = useState('');
  const [userCoins, setUserCoins] = useState(0);
  const [hasStarterPet, setHasStarterPet] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selecting, setSelecting] = useState(false);
  const [activeTab, setActiveTab] = useState('starters');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Check if we have a token before making requests
      const token = localStorage.getItem('forge_token');
      if (!token) {
        console.log('No auth token found, redirecting to login');
        navigate('/auth');
        return;
      }

      // Create headers config to ensure token is sent
      const config = {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      };

      // Fetch all data with explicit auth headers (iOS Safari fix)
      console.log('Fetching pets data...');
      const petsRes = await axios.get(`${API}/pets/available`, config);
      console.log('Pets response:', petsRes.data);
      
      // Validate response structure
      if (!petsRes.data || typeof petsRes.data !== 'object') {
        throw new Error('Invalid pets response');
      }
      
      const startersData = petsRes.data?.starters || [];
      const shopPetsData = petsRes.data?.shop_pets || [];
      
      console.log('Fetching my pet status...');
      const myPetRes = await axios.get(`${API}/pets/my-pet`, config);
      console.log('My pet response:', myPetRes.data);
      
      const hasPet = myPetRes.data?.has_pet || false;
      
      console.log('Fetching engagement status...');
      const statusRes = await axios.get(`${API}/engagement/status`, config);
      console.log('Status response:', statusRes.data);
      
      const coins = statusRes.data?.coins || 0;
      
      // Batch state updates to prevent race conditions on iOS Safari
      setStarters(startersData);
      setShopPets(shopPetsData);
      setHasStarterPet(hasPet);
      setUserCoins(coins);
      
      if (hasPet) {
        setActiveTab('shop');
      }
      
      // Only set loading false after all state updates are queued
      setLoading(false);
      
    } catch (err) {
      console.error('Fetch error details:', {
        message: err.message,
        status: err.response?.status,
        data: err.response?.data,
        url: err.config?.url
      });
      
      // Handle auth errors specifically
      if (err.response?.status === 401) {
        console.log('Auth error - clearing token and redirecting');
        localStorage.removeItem('forge_token');
        navigate('/auth');
        return;
      }
      
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to load pets';
      setError(errorMsg);
      setLoading(false);
      toast.error('Failed to load pets. Tap to retry.');
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
    } catch (err) {
      console.error('Select error:', err);
      toast.error(err.response?.data?.detail || 'Failed to select pet');
    } finally {
      setSelecting(false);
    }
  };

  const handlePetTap = (pet) => {
    const canAfford = userCoins >= pet.price;
    const isLocked = !pet.is_starter && !canAfford && !pet.owned;
    
    if (!pet.owned && !isLocked) {
      setSelectedPet(pet);
      setCustomName('');
    }
  };

  // Loading state
  if (loading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-zinc-400">Loading pets...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center p-4">
        <div className="text-center">
          <div className="text-6xl mb-4">😿</div>
          <h2 className="text-white text-xl font-bold mb-2">Couldn't Load Pets</h2>
          <p className="text-zinc-400 mb-4">{error}</p>
          <Button onClick={fetchData} className="bg-primary text-black">
            <RefreshCw className="w-4 h-4 mr-2" /> Try Again
          </Button>
        </div>
      </div>
    );
  }

  const displayPets = activeTab === 'starters' ? starters : shopPets;

  return (
    <div className="min-h-screen bg-black pb-32" data-testid="pet-selection-screen">
      {/* Header */}
      <div className="sticky top-0 z-10 bg-black/95 backdrop-blur-sm border-b border-zinc-800 p-4">
        <div className="flex items-center gap-3 mb-4">
          <button
            type="button"
            onClick={() => navigate(-1)}
            className="p-2 -ml-2 text-zinc-400 hover:text-white"
          >
            <ArrowLeft className="w-6 h-6" />
          </button>
          <div className="flex-1">
            <h1 className="text-xl font-bold text-white flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-primary" />
              Choose Your Pet
            </h1>
            <p className="text-zinc-400 text-sm">Your companion on your journey</p>
          </div>
          <div className="flex items-center gap-1 bg-yellow-500/20 text-yellow-400 px-3 py-1.5 rounded-full text-sm">
            <Coins className="w-4 h-4" />
            <span className="font-bold">{userCoins}</span>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-2">
          <Button
            type="button"
            onClick={() => setActiveTab('starters')}
            disabled={hasStarterPet}
            variant={activeTab === 'starters' ? 'default' : 'outline'}
            className={`flex-1 ${activeTab === 'starters' ? 'bg-primary text-black' : ''} ${hasStarterPet ? 'opacity-50' : ''}`}
          >
            <Star className="w-4 h-4 mr-2" />
            Free Starters
            {hasStarterPet && <Lock className="w-3 h-3 ml-1" />}
          </Button>
          <Button
            type="button"
            onClick={() => setActiveTab('shop')}
            variant={activeTab === 'shop' ? 'default' : 'outline'}
            className={`flex-1 ${activeTab === 'shop' ? 'bg-primary text-black' : ''}`}
          >
            <ShoppingBag className="w-4 h-4 mr-2" />
            Pet Shop
          </Button>
        </div>
      </div>

      {/* Content */}
      <div className="p-4">
        {hasStarterPet && activeTab === 'starters' && (
          <div className="bg-zinc-800/50 rounded-xl p-4 mb-4 text-center">
            <p className="text-zinc-400 text-sm">
              You already have a starter pet! Browse the shop for more companions.
            </p>
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
              <button
                type="button"
                key={pet.type}
                onClick={() => handlePetTap(pet)}
                disabled={pet.owned || isLocked}
                className={`relative rounded-xl p-4 border-2 transition-all text-left w-full ${style.bg} ${
                  isSelected 
                    ? 'border-primary ring-2 ring-primary/30' 
                    : pet.owned 
                      ? 'border-green-500/50 opacity-75'
                      : isLocked
                        ? 'border-zinc-700 opacity-50'
                        : `${style.border} active:scale-95`
                }`}
                data-testid={`pet-option-${pet.type}`}
              >
                {/* Category icon */}
                <div className="absolute top-2 right-2 text-lg opacity-50">
                  {categoryIcons[pet.category] || '🐾'}
                </div>

                {/* Owned badge */}
                {pet.owned && (
                  <div className="absolute top-2 left-2 bg-green-500/20 text-green-400 text-[10px] px-2 py-0.5 rounded-full">
                    Owned
                  </div>
                )}

                {/* Locked badge */}
                {isLocked && (
                  <div className="absolute top-2 left-2 bg-zinc-700 text-zinc-400 text-[10px] px-2 py-0.5 rounded-full flex items-center gap-1">
                    <Lock className="w-3 h-3" /> {pet.price}
                  </div>
                )}

                {/* Pet preview */}
                <div className="text-center py-2">
                  <div className="text-4xl mb-1">{pet.preview_icon}</div>
                  <div className="text-lg opacity-50">→ {pet.max_icon}</div>
                </div>

                {/* Info */}
                <h3 className="text-white font-bold text-sm">{pet.name}</h3>
                <p className={`text-xs capitalize ${style.text}`}>{pet.rarity}</p>
                <p className="text-zinc-500 text-xs mt-1 line-clamp-2">{pet.description}</p>

                {/* Price for shop pets */}
                {!pet.is_starter && !pet.owned && (
                  <div className={`mt-2 flex items-center gap-1 text-xs ${canAfford ? 'text-yellow-400' : 'text-zinc-500'}`}>
                    <Coins className="w-3 h-3" />
                    <span>{pet.price} coins</span>
                  </div>
                )}

                {/* Selected indicator */}
                {isSelected && (
                  <div className="absolute -top-1 -right-1 w-6 h-6 bg-primary rounded-full flex items-center justify-center">
                    <Check className="w-4 h-4 text-black" />
                  </div>
                )}
              </button>
            );
          })}
        </div>
      </div>

      {/* Selection panel - Fixed at bottom */}
      {selectedPet && (
        <div 
          className="fixed bottom-0 left-0 right-0 bg-zinc-900 border-t border-zinc-700 p-4 z-50"
          style={{ paddingBottom: 'max(1rem, env(safe-area-inset-bottom))' }}
        >
          <div className="flex items-center gap-4 mb-3">
            <div className="text-4xl">{selectedPet.preview_icon}</div>
            <div className="flex-1">
              <h3 className="text-white font-bold">{selectedPet.name}</h3>
              <p className="text-zinc-400 text-xs line-clamp-1">{selectedPet.description}</p>
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
            type="button"
            onClick={handleSelectPet}
            disabled={selecting}
            className="w-full bg-primary text-black hover:bg-primary/90 font-bold py-6 text-lg"
            data-testid="confirm-pet-btn"
          >
            {selecting ? 'Selecting...' : selectedPet.is_starter ? 'Choose This Pet!' : `Buy for ${selectedPet.price} Coins`}
          </Button>
        </div>
      )}
    </div>
  );
};

export default PetSelectionScreen;
