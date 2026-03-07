import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { School, Search, X, Check, Loader2, Plus, MapPin } from 'lucide-react';
import { Input } from './ui/input';
import { Button } from './ui/button';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// US States for dropdown
const US_STATES = [
  'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
  'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
  'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
  'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
  'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY', 'DC'
];

export const SchoolSelector = ({ currentSchool, onSchoolChange }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [searching, setSearching] = useState(false);
  const [saving, setSaving] = useState(false);
  const [showCustomForm, setShowCustomForm] = useState(false);
  const [customCity, setCustomCity] = useState('');
  const [customState, setCustomState] = useState('');
  const dropdownRef = useRef(null);
  const searchTimeout = useRef(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Debounced search
  useEffect(() => {
    if (searchQuery.length < 2) {
      setSearchResults([]);
      return;
    }

    if (searchTimeout.current) {
      clearTimeout(searchTimeout.current);
    }

    searchTimeout.current = setTimeout(async () => {
      setSearching(true);
      try {
        const response = await axios.get(`${API}/schools/search`, {
          params: { q: searchQuery }
        });
        setSearchResults(response.data.schools || []);
      } catch (error) {
        console.error('School search failed:', error);
        setSearchResults([]);
      } finally {
        setSearching(false);
      }
    }, 300);

    return () => {
      if (searchTimeout.current) {
        clearTimeout(searchTimeout.current);
      }
    };
  }, [searchQuery]);

  const handleSelectSchool = async (school) => {
    setSaving(true);
    try {
      await axios.post(`${API}/schools/set-school`, school);
      // Display format: "School Name (City, ST)"
      const displayName = school.city && school.state && school.state !== 'US' 
        ? `${school.name} (${school.city}, ${school.state})`
        : school.name;
      onSchoolChange(displayName);
      toast.success(`School set to ${school.name}`);
      setIsOpen(false);
      setSearchQuery('');
    } catch (error) {
      console.error('Failed to set school:', error);
      toast.error('Failed to set school');
    } finally {
      setSaving(false);
    }
  };

  const handleRemoveSchool = async () => {
    setSaving(true);
    try {
      await axios.delete(`${API}/schools/remove-school`);
      onSchoolChange(null);
      toast.success('School removed from profile');
      setIsOpen(false);
    } catch (error) {
      console.error('Failed to remove school:', error);
      toast.error('Failed to remove school');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="relative" ref={dropdownRef}>
      {/* Current school display / trigger */}
      <div 
        className="bg-card border border-border rounded-lg p-4 cursor-pointer hover:border-primary/50 transition-colors"
        onClick={() => setIsOpen(!isOpen)}
        data-testid="school-selector-trigger"
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
              currentSchool ? 'bg-primary/20' : 'bg-muted'
            }`}>
              <School className={`w-5 h-5 ${currentSchool ? 'text-primary' : 'text-muted-foreground'}`} />
            </div>
            <div>
              <div className="text-foreground font-body font-medium">
                {currentSchool || 'Select Your School'}
              </div>
              <div className="text-muted-foreground text-sm font-body">
                {currentSchool ? 'Click to change' : 'Optional - Join school leaderboard'}
              </div>
            </div>
          </div>
          {currentSchool && (
            <span className="px-2 py-1 bg-primary/20 text-primary text-xs font-mono rounded">
              SET
            </span>
          )}
        </div>
      </div>

      {/* Dropdown */}
      {isOpen && (
        <div className="absolute top-full left-0 right-0 mt-2 bg-card border border-border rounded-lg shadow-xl z-50 overflow-hidden">
          {/* Search input */}
          <div className="p-3 border-b border-border">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <Input
                type="text"
                placeholder="Search US schools (grades 8-12)..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 bg-background border-border"
                autoFocus
                data-testid="school-search-input"
              />
              {searchQuery && (
                <button
                  onClick={() => setSearchQuery('')}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                >
                  <X className="w-4 h-4" />
                </button>
              )}
            </div>
            <p className="text-muted-foreground text-xs mt-2 font-body">
              Type at least 2 characters to search
            </p>
          </div>

          {/* Results */}
          <div className="max-h-64 overflow-y-auto">
            {searching ? (
              <div className="p-4 text-center">
                <Loader2 className="w-6 h-6 text-primary animate-spin mx-auto" />
                <p className="text-muted-foreground text-sm mt-2">Searching schools...</p>
              </div>
            ) : searchResults.length > 0 ? (
              <div className="divide-y divide-border">
                {searchResults.map((school, index) => (
                  <button
                    key={school.nces_id || index}
                    onClick={() => handleSelectSchool(school)}
                    disabled={saving}
                    className="w-full p-3 text-left hover:bg-accent transition-colors flex items-center justify-between"
                    data-testid={`school-result-${index}`}
                  >
                    <div>
                      <div className="text-foreground font-body font-medium">{school.name}</div>
                      <div className="text-muted-foreground text-xs font-body">
                        {school.city}, {school.state} • Grades {school.grades}
                      </div>
                    </div>
                    {currentSchool === school.name && (
                      <Check className="w-5 h-5 text-primary" />
                    )}
                  </button>
                ))}
              </div>
            ) : searchQuery.length >= 3 ? (
              <div className="p-4">
                <p className="text-muted-foreground text-sm font-body text-center mb-3">
                  "{searchQuery}" not found in database
                </p>
                <Button
                  onClick={() => handleSelectSchool({
                    nces_id: `custom_${searchQuery.toLowerCase().replace(/[^a-z0-9]/g, '_')}`,
                    name: searchQuery,
                    city: '',
                    state: 'US',
                    grades: '8-12'
                  })}
                  disabled={saving}
                  className="w-full bg-primary text-primary-foreground hover:bg-primary/90"
                  data-testid="add-custom-school-btn"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Add "{searchQuery}" as my school
                </Button>
                <p className="text-muted-foreground/70 text-xs mt-2 text-center">
                  Your school will be added to the database
                </p>
              </div>
            ) : searchQuery.length >= 2 ? (
              <div className="p-4 text-center">
                <p className="text-muted-foreground text-sm font-body">Keep typing to search...</p>
                <p className="text-muted-foreground/70 text-xs mt-1">Enter at least 3 characters</p>
              </div>
            ) : (
              <div className="p-4 text-center">
                <School className="w-8 h-8 text-muted-foreground mx-auto mb-2" />
                <p className="text-muted-foreground text-sm font-body">
                  Search for your school above
                </p>
              </div>
            )}
          </div>

          {/* Remove school option */}
          {currentSchool && (
            <div className="p-3 border-t border-border bg-muted/30">
              <Button
                onClick={handleRemoveSchool}
                disabled={saving}
                variant="ghost"
                className="w-full text-destructive hover:text-destructive hover:bg-destructive/10"
                data-testid="remove-school-btn"
              >
                <X className="w-4 h-4 mr-2" />
                Remove School from Profile
              </Button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
