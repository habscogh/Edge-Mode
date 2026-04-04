import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'sonner';
import { Button } from '../components/ui/button';
import {
  Coins,
  ShoppingBag,
  Package,
  Palette,
  Medal,
  Shield,
  User,
  Sparkles,
  Check,
  Lock,
  ChevronRight,
  ChevronLeft,
  Star,
  Crown
} from 'lucide-react';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

// Category icons mapping
const categoryIcons = {
  themes: Palette,
  badges: Medal,
  streak_shields: Shield,
  avatars: User,
  effects: Sparkles
};

// Rarity styles
const rarityStyles = {
  common: 'border-zinc-600 bg-zinc-800/50',
  uncommon: 'border-green-500/50 bg-green-900/20',
  rare: 'border-blue-500/50 bg-blue-900/20',
  epic: 'border-purple-500/50 bg-purple-900/20',
  legendary: 'border-yellow-500/50 bg-yellow-900/20 ring-1 ring-yellow-500/30'
};

const rarityLabels = {
  common: { text: 'Common', color: 'text-zinc-400' },
  uncommon: { text: 'Uncommon', color: 'text-green-400' },
  rare: { text: 'Rare', color: 'text-blue-400' },
  epic: { text: 'Epic', color: 'text-purple-400' },
  legendary: { text: 'Legendary', color: 'text-yellow-400' }
};

// Shop Item Card Component
const ShopItemCard = ({ item, owned, onPurchase, userCoins }) => {
  const [purchasing, setPurchasing] = useState(false);
  const canAfford = userCoins >= item.price;
  const RarityInfo = rarityLabels[item.rarity] || rarityLabels.common;

  const handlePurchase = async () => {
    if (owned || !canAfford) return;
    
    setPurchasing(true);
    try {
      const response = await axios.post(`${API}/shop/purchase/${item.id}`);
      toast.success(response.data.message);
      onPurchase(response.data);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Purchase failed');
    } finally {
      setPurchasing(false);
    }
  };

  return (
    <div 
      className={`relative rounded-xl p-4 border-2 transition-all ${rarityStyles[item.rarity] || rarityStyles.common} ${
        owned ? 'opacity-75' : 'hover:scale-[1.02]'
      }`}
      data-testid={`shop-item-${item.id}`}
    >
      {/* Rarity badge */}
      <div className={`absolute top-2 right-2 text-xs px-2 py-0.5 rounded-full bg-black/50 ${RarityInfo.color}`}>
        {RarityInfo.text}
      </div>

      {/* Item icon */}
      <div className="text-4xl mb-3">{item.icon}</div>

      {/* Item info */}
      <h3 className="text-white font-bold text-sm mb-1">{item.name}</h3>
      <p className="text-zinc-400 text-xs mb-3 line-clamp-2">{item.description}</p>

      {/* Price and action */}
      <div className="flex items-center justify-between mt-auto">
        <div className="flex items-center gap-1 text-yellow-400">
          <Coins className="w-4 h-4" />
          <span className="font-bold">{item.price}</span>
        </div>

        {owned ? (
          <span className="flex items-center gap-1 text-green-400 text-sm">
            <Check className="w-4 h-4" />
            Owned
          </span>
        ) : (
          <Button
            onClick={handlePurchase}
            disabled={!canAfford || purchasing}
            size="sm"
            className={`${
              canAfford 
                ? 'bg-primary hover:bg-primary/90 text-black' 
                : 'bg-zinc-700 text-zinc-400 cursor-not-allowed'
            }`}
            data-testid={`buy-${item.id}`}
          >
            {purchasing ? 'Buying...' : canAfford ? 'Buy' : <Lock className="w-4 h-4" />}
          </Button>
        )}
      </div>
    </div>
  );
};

// Inventory Item Card
const InventoryItemCard = ({ inventoryItem, onEquip, onUnequip }) => {
  const item = inventoryItem.item;
  if (!item) return null;

  const isEquipped = inventoryItem.is_equipped;
  const isConsumable = item.category === 'streak_shields';

  return (
    <div 
      className={`relative rounded-xl p-4 border-2 transition-all ${
        isEquipped 
          ? 'border-primary bg-primary/10 ring-2 ring-primary/30' 
          : 'border-zinc-700 bg-zinc-800/50'
      }`}
      data-testid={`inventory-item-${inventoryItem.id}`}
    >
      {isEquipped && (
        <div className="absolute top-2 right-2 bg-primary text-black text-xs px-2 py-0.5 rounded-full font-bold">
          Equipped
        </div>
      )}

      <div className="text-3xl mb-2">{item.icon}</div>
      <h3 className="text-white font-bold text-sm mb-1">{item.name}</h3>
      
      {isConsumable && inventoryItem.uses_remaining && (
        <p className="text-zinc-400 text-xs mb-2">
          {inventoryItem.uses_remaining} uses remaining
        </p>
      )}

      {!isConsumable && (
        <Button
          onClick={() => isEquipped ? onUnequip(inventoryItem.id) : onEquip(inventoryItem.id)}
          size="sm"
          variant={isEquipped ? "outline" : "default"}
          className="w-full mt-2"
        >
          {isEquipped ? 'Unequip' : 'Equip'}
        </Button>
      )}
    </div>
  );
};

// Main Shop Screen
const ShopScreen = () => {
  const navigate = useNavigate();
  const [categories, setCategories] = useState({});
  const [items, setItems] = useState([]);
  const [inventory, setInventory] = useState([]);
  const [activeCategory, setActiveCategory] = useState('all');
  const [activeTab, setActiveTab] = useState('shop'); // 'shop' or 'inventory'
  const [userCoins, setUserCoins] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [categoriesRes, itemsRes, inventoryRes, statusRes] = await Promise.all([
        axios.get(`${API}/shop/categories`),
        axios.get(`${API}/shop/items`),
        axios.get(`${API}/shop/inventory`),
        axios.get(`${API}/engagement/status`)
      ]);

      setCategories(categoriesRes.data.categories);
      setItems(itemsRes.data.items);
      setInventory(inventoryRes.data.inventory);
      setUserCoins(statusRes.data.coins || 0);
    } catch (error) {
      console.error('Failed to fetch shop data:', error);
      toast.error('Failed to load shop');
    } finally {
      setLoading(false);
    }
  };

  const handlePurchase = (purchaseData) => {
    setUserCoins(purchaseData.new_balance);
    fetchData(); // Refresh inventory
  };

  const handleEquip = async (inventoryId) => {
    try {
      const response = await axios.post(`${API}/shop/equip/${inventoryId}`);
      toast.success(response.data.message);
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to equip item');
    }
  };

  const handleUnequip = async (inventoryId) => {
    try {
      await axios.post(`${API}/shop/unequip/${inventoryId}`);
      toast.success('Item unequipped');
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to unequip item');
    }
  };

  const ownedItemIds = inventory.map(inv => inv.item_id);
  
  const filteredItems = activeCategory === 'all' 
    ? items 
    : items.filter(item => item.category === activeCategory);

  const filteredInventory = activeCategory === 'all'
    ? inventory
    : inventory.filter(inv => inv.category === activeCategory);

  if (loading) {
    return (
      <div className="min-h-screen bg-black p-4 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black pb-24" data-testid="shop-screen">
      {/* Header */}
      <div className="sticky top-0 z-10 bg-black/95 backdrop-blur-sm border-b border-zinc-800 p-4">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <button
              onClick={() => navigate(-1)}
              className="p-2 -ml-2 text-zinc-400 hover:text-white transition-colors"
              data-testid="back-button"
            >
              <ChevronLeft className="w-6 h-6" />
            </button>
            <ShoppingBag className="w-6 h-6 text-primary" />
            <h1 className="text-xl font-bold text-white">XP Shop</h1>
          </div>
          <div className="flex items-center gap-2 bg-yellow-500/20 text-yellow-400 px-3 py-1.5 rounded-full">
            <Coins className="w-5 h-5" />
            <span className="font-bold" data-testid="user-coins">{userCoins}</span>
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
        </div>

        {/* Category Filter */}
        <div className="flex gap-2 overflow-x-auto pb-2 hide-scrollbar">
          <Button
            onClick={() => setActiveCategory('all')}
            variant="ghost"
            size="sm"
            className={`shrink-0 ${activeCategory === 'all' ? 'bg-zinc-800 text-white' : 'text-zinc-400'}`}
          >
            All
          </Button>
          {Object.entries(categories).map(([key, cat]) => {
            const Icon = categoryIcons[key] || Star;
            return (
              <Button
                key={key}
                onClick={() => setActiveCategory(key)}
                variant="ghost"
                size="sm"
                className={`shrink-0 ${activeCategory === key ? 'bg-zinc-800 text-white' : 'text-zinc-400'}`}
              >
                <Icon className="w-4 h-4 mr-1" /> {cat.name}
              </Button>
            );
          })}
        </div>
      </div>

      {/* Content */}
      <div className="p-4">
        {activeTab === 'shop' ? (
          <>
            {/* Featured Section */}
            {activeCategory === 'all' && (
              <div className="mb-6">
                <div className="flex items-center gap-2 mb-3">
                  <Crown className="w-5 h-5 text-yellow-400" />
                  <h2 className="text-white font-bold">Featured Items</h2>
                </div>
                <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
                  {items.filter(i => i.rarity === 'legendary' || i.rarity === 'epic').slice(0, 4).map(item => (
                    <ShopItemCard
                      key={item.id}
                      item={item}
                      owned={ownedItemIds.includes(item.id)}
                      onPurchase={handlePurchase}
                      userCoins={userCoins}
                    />
                  ))}
                </div>
              </div>
            )}

            {/* All Items */}
            <div>
              <h2 className="text-white font-bold mb-3">
                {activeCategory === 'all' ? 'All Items' : categories[activeCategory]?.name}
              </h2>
              {filteredItems.length === 0 ? (
                <div className="text-center py-12 text-zinc-500">
                  <ShoppingBag className="w-12 h-12 mx-auto mb-3 opacity-50" />
                  <p>No items in this category</p>
                </div>
              ) : (
                <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
                  {filteredItems.map(item => (
                    <ShopItemCard
                      key={item.id}
                      item={item}
                      owned={ownedItemIds.includes(item.id)}
                      onPurchase={handlePurchase}
                      userCoins={userCoins}
                    />
                  ))}
                </div>
              )}
            </div>
          </>
        ) : (
          /* Inventory Tab */
          <div>
            <h2 className="text-white font-bold mb-3">Your Items</h2>
            {filteredInventory.length === 0 ? (
              <div className="text-center py-12 text-zinc-500">
                <Package className="w-12 h-12 mx-auto mb-3 opacity-50" />
                <p>No items yet</p>
                <Button
                  onClick={() => setActiveTab('shop')}
                  variant="outline"
                  className="mt-4"
                >
                  Browse Shop
                </Button>
              </div>
            ) : (
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
                {filteredInventory.map(invItem => (
                  <InventoryItemCard
                    key={invItem.id}
                    inventoryItem={invItem}
                    onEquip={handleEquip}
                    onUnequip={handleUnequip}
                  />
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Earn More Coins Banner */}
      <div 
        onClick={() => navigate('/dashboard')}
        className="fixed bottom-20 left-4 right-4 bg-gradient-to-r from-yellow-600/90 to-orange-600/90 rounded-xl p-4 backdrop-blur-sm cursor-pointer hover:from-yellow-500/90 hover:to-orange-500/90 transition-colors"
        data-testid="earn-coins-banner"
      >
        <div className="flex items-center justify-between">
          <div>
            <p className="text-white font-bold text-sm">Need more coins?</p>
            <p className="text-white/80 text-xs">Log sessions & claim daily rewards!</p>
          </div>
          <ChevronRight className="w-5 h-5 text-white" />
        </div>
      </div>
    </div>
  );
};

export default ShopScreen;
