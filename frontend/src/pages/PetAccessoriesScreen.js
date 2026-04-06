import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'sonner';
import { Button } from '../components/ui/button';
import { 
  ArrowLeft,
  Check,
  Lock,
  Coins,
  Crown,
  Sparkles,
  ShoppingBag,
  Package,
  Star,
  Gift,
  Zap
} from 'lucide-react';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

// Rarity styles
const rarityStyles = {
  common: { bg: 'bg-zinc-800/50', border: 'border-zinc-600', text: 'text-zinc-400', glow: '' },
  uncommon: { bg: 'bg-green-900/20', border: 'border-green-500/50', text: 'text-green-400', glow: 'shadow-green-500/20' },
  rare: { bg: 'bg-blue-900/20', border: 'border-blue-500/50', text: 'text-blue-400', glow: 'shadow-blue-500/20' },
  epic: { bg: 'bg-purple-900/20', border: 'border-purple-500/50', text: 'text-purple-400', glow: 'shadow-purple-500/30' },
  legendary: { bg: 'bg-yellow-900/20', border: 'border-yellow-500/50', text: 'text-yellow-400', glow: 'shadow-yellow-500/30' }
};

// Unlock type icons
const unlockTypeIcons = {
  shop: <Coins className="w-3 h-3" />,
  level: <Star className="w-3 h-3" />,
  streak: <Zap className="w-3 h-3" />,
  achievement: <Crown className="w-3 h-3" />,
  referral: <Gift className="w-3 h-3" />
};

const PetAccessoriesScreen = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('shop'); // 'shop', 'inventory', 'unlockable'
  const [shopItems, setShopItems] = useState([]);
  const [inventory, setInventory] = useState([]);
  const [unlockable, setUnlockable] = useState([]);
  const [equipped, setEquipped] = useState({});
  const [userCoins, setUserCoins] = useState(0);
  const [loading, setLoading] = useState(true);
  const [purchasing, setPurchasing] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState('all');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [shopRes, invRes, unlockRes, equippedRes] = await Promise.all([
        axios.get(`${API}/pets/accessories/shop`),
        axios.get(`${API}/pets/accessories/inventory`),
        axios.get(`${API}/pets/accessories/unlockable`),
        axios.get(`${API}/pets/accessories/equipped`)
      ]);
      
      setShopItems(shopRes.data.items || []);
      setUserCoins(shopRes.data.user_coins || 0);
      setInventory(invRes.data.inventory || []);
      setUnlockable(unlockRes.data.unlockable || []);
      setEquipped(equippedRes.data.equipped || {});
    } catch (error) {
      console.error('Failed to fetch accessories:', error);
      toast.error('Failed to load accessories');
    } finally {
      setLoading(false);
    }
  };

  const handlePurchase = async (accessoryId) => {
    if (purchasing) return;
    setPurchasing(true);
    
    try {
      const response = await axios.post(`${API}/pets/accessories/purchase/${accessoryId}`);
      toast.success(response.data.message);
      setUserCoins(response.data.coins_remaining);
      fetchData(); // Refresh
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Purchase failed');
    } finally {
      setPurchasing(false);
    }
  };

  const handleClaim = async (accessoryId) => {
    try {
      const response = await axios.post(`${API}/pets/accessories/claim/${accessoryId}`);
      toast.success(response.data.message);
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Claim failed');
    }
  };

  const handleEquip = async (accessoryId) => {
    try {
      const response = await axios.post(`${API}/pets/accessories/equip`, {
        accessory_id: accessoryId
      });
      toast.success(response.data.message);
      if (response.data.theme_bonus) {
        toast.success(response.data.theme_bonus_message, { icon: '✨' });
      }
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Equip failed');
    }
  };

  const handleUnequip = async (slot) => {
    try {
      const response = await axios.post(`${API}/pets/accessories/unequip/${slot}`);
      toast.success(response.data.message);
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Unequip failed');
    }
  };

  const categories = ['all', 'hats', 'glasses', 'necklaces', 'back', 'effects'];

  if (loading) {
    return (
      <div className="min-h-screen bg-black p-4 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
      </div>
    );
  }

  const getDisplayItems = () => {
    let items = [];
    
    if (activeTab === 'shop') {
      items = shopItems.filter(i => !i.owned);
    } else if (activeTab === 'inventory') {
      items = inventory;
    } else if (activeTab === 'unlockable') {
      items = unlockable.filter(i => !i.owned);
    }
    
    if (selectedCategory !== 'all') {
      items = items.filter(i => i.category === selectedCategory);
    }
    
    return items;
  };

  const displayItems = getDisplayItems();
  const claimableCount = unlockable.filter(u => u.claimable).length;

  return (
    <div className="min-h-screen bg-black pb-24" data-testid="pet-accessories-screen">
      {/* Header */}
      <div className="sticky top-0 z-10 bg-black/95 backdrop-blur-sm border-b border-zinc-800 p-4">
        <div className="flex items-center gap-3 mb-4">
          <button
            onClick={() => navigate(-1)}
            className="p-2 -ml-2 text-zinc-400 hover:text-white transition-colors"
          >
            <ArrowLeft className="w-6 h-6" />
          </button>
          <div className="flex-1">
            <h1 className="text-xl font-bold text-white flex items-center gap-2">
              <Crown className="w-5 h-5 text-yellow-400" />
              Pet Accessories
            </h1>
            <p className="text-zinc-400 text-sm">Customize your companion!</p>
          </div>
          <div className="flex items-center gap-1 bg-yellow-500/20 text-yellow-400 px-3 py-1.5 rounded-full text-sm">
            <Coins className="w-4 h-4" />
            <span className="font-bold">{userCoins}</span>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-4">
          <Button
            onClick={() => setActiveTab('shop')}
            variant={activeTab === 'shop' ? 'default' : 'outline'}
            size="sm"
            className={activeTab === 'shop' ? 'bg-primary text-black' : ''}
          >
            <ShoppingBag className="w-4 h-4 mr-1" /> Shop
          </Button>
          <Button
            onClick={() => setActiveTab('inventory')}
            variant={activeTab === 'inventory' ? 'default' : 'outline'}
            size="sm"
            className={activeTab === 'inventory' ? 'bg-primary text-black' : ''}
          >
            <Package className="w-4 h-4 mr-1" /> Inventory ({inventory.length})
          </Button>
          <Button
            onClick={() => setActiveTab('unlockable')}
            variant={activeTab === 'unlockable' ? 'default' : 'outline'}
            size="sm"
            className={`${activeTab === 'unlockable' ? 'bg-primary text-black' : ''} relative`}
          >
            <Sparkles className="w-4 h-4 mr-1" /> Unlock
            {claimableCount > 0 && (
              <span className="absolute -top-1 -right-1 w-5 h-5 bg-green-500 rounded-full text-xs flex items-center justify-center text-white font-bold">
                {claimableCount}
              </span>
            )}
          </Button>
        </div>

        {/* Category filter */}
        <div className="flex gap-2 overflow-x-auto pb-2 -mx-4 px-4">
          {categories.map(cat => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-3 py-1 rounded-full text-xs whitespace-nowrap transition-colors ${
                selectedCategory === cat
                  ? 'bg-primary text-black font-bold'
                  : 'bg-zinc-800 text-zinc-400 hover:bg-zinc-700'
              }`}
            >
              {cat === 'all' ? 'All' : cat.charAt(0).toUpperCase() + cat.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Currently Equipped Section */}
      {Object.keys(equipped).length > 0 && activeTab === 'inventory' && (
        <div className="p-4 border-b border-zinc-800">
          <h3 className="text-white font-bold text-sm mb-3 flex items-center gap-2">
            <Star className="w-4 h-4 text-yellow-400" /> Currently Equipped
          </h3>
          <div className="flex flex-wrap gap-2">
            {Object.entries(equipped).map(([slot, acc]) => (
              <div
                key={slot}
                className="flex items-center gap-2 bg-zinc-800 rounded-lg px-3 py-2 border border-zinc-700"
              >
                <span className="text-xl">{acc.icon}</span>
                <div>
                  <p className="text-white text-xs font-medium">{acc.name}</p>
                  <p className="text-zinc-500 text-[10px] capitalize">{slot}</p>
                </div>
                <button
                  onClick={() => handleUnequip(slot)}
                  className="ml-2 text-zinc-500 hover:text-red-400 text-xs"
                >
                  ✕
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Items Grid */}
      <div className="p-4">
        {displayItems.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-4xl mb-4">
              {activeTab === 'shop' ? '🛍️' : activeTab === 'inventory' ? '📦' : '🎁'}
            </div>
            <p className="text-zinc-400">
              {activeTab === 'shop' && 'All shop items purchased!'}
              {activeTab === 'inventory' && 'No accessories yet. Visit the shop!'}
              {activeTab === 'unlockable' && 'All unlockable accessories claimed!'}
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-2 gap-3">
            {displayItems.map((item) => {
              const style = rarityStyles[item.rarity] || rarityStyles.common;
              const isEquipped = Object.values(equipped).some(e => e?.id === item.id);
              const equippedInSlot = equipped[item.slot];
              
              return (
                <div
                  key={item.id}
                  className={`relative rounded-xl p-3 border-2 transition-all ${style.bg} ${style.border} ${
                    isEquipped ? 'ring-2 ring-primary/50' : ''
                  } ${item.theme_match ? `shadow-lg ${style.glow}` : ''}`}
                  data-testid={`accessory-${item.id}`}
                >
                  {/* Rarity badge */}
                  <div className={`absolute top-2 right-2 text-[10px] px-1.5 py-0.5 rounded-full bg-black/50 ${style.text} capitalize`}>
                    {item.rarity}
                  </div>

                  {/* Theme match badge */}
                  {item.theme_match && (
                    <div className="absolute top-2 left-2 text-[10px] px-1.5 py-0.5 rounded-full bg-yellow-500/20 text-yellow-400">
                      ✨ Match
                    </div>
                  )}

                  {/* Icon */}
                  <div className="text-center py-3">
                    <div className="text-4xl mb-1">{item.icon}</div>
                  </div>

                  {/* Info */}
                  <h4 className="text-white font-bold text-xs text-center truncate">{item.name}</h4>
                  <p className="text-zinc-500 text-[10px] text-center mt-0.5 line-clamp-2">{item.description}</p>

                  {/* Action button / Status */}
                  <div className="mt-3">
                    {/* Shop items */}
                    {activeTab === 'shop' && (
                      <Button
                        onClick={() => handlePurchase(item.id)}
                        disabled={!item.can_afford || purchasing}
                        size="sm"
                        className="w-full bg-yellow-500 hover:bg-yellow-600 text-black text-xs"
                      >
                        {item.can_afford ? (
                          <>
                            <Coins className="w-3 h-3 mr-1" />
                            {item.price}
                          </>
                        ) : (
                          <>
                            <Lock className="w-3 h-3 mr-1" />
                            {item.price}
                          </>
                        )}
                      </Button>
                    )}

                    {/* Inventory items */}
                    {activeTab === 'inventory' && (
                      <Button
                        onClick={() => isEquipped ? handleUnequip(item.slot) : handleEquip(item.id)}
                        size="sm"
                        variant={isEquipped ? 'outline' : 'default'}
                        className={`w-full text-xs ${isEquipped ? 'border-primary text-primary' : 'bg-primary text-black'}`}
                      >
                        {isEquipped ? (
                          <>
                            <Check className="w-3 h-3 mr-1" /> Equipped
                          </>
                        ) : equippedInSlot ? (
                          'Replace'
                        ) : (
                          'Equip'
                        )}
                      </Button>
                    )}

                    {/* Unlockable items */}
                    {activeTab === 'unlockable' && (
                      item.claimable ? (
                        <Button
                          onClick={() => handleClaim(item.id)}
                          size="sm"
                          className="w-full bg-green-500 hover:bg-green-600 text-white text-xs"
                        >
                          <Gift className="w-3 h-3 mr-1" /> Claim!
                        </Button>
                      ) : (
                        <div className="text-center">
                          <div className="flex items-center justify-center gap-1 text-zinc-500 text-[10px]">
                            {unlockTypeIcons[item.unlock_type]}
                            <span>{item.unlock_reason}</span>
                          </div>
                          {item.progress && (
                            <div className="mt-1.5 h-1 bg-zinc-800 rounded-full overflow-hidden">
                              <div 
                                className="h-full bg-primary transition-all"
                                style={{ 
                                  width: `${(parseInt(item.progress.split('/')[0]) / parseInt(item.progress.split('/')[1])) * 100}%` 
                                }}
                              />
                            </div>
                          )}
                        </div>
                      )
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default PetAccessoriesScreen;
