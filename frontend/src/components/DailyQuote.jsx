import React, { useState, useEffect } from 'react';
import { Quote, RefreshCw } from 'lucide-react';

// Curated quotes for teen self-improvement
const MOTIVATIONAL_QUOTES = [
  { text: "Small daily improvements are the key to staggering long-term results.", author: "Unknown" },
  { text: "You don't have to be great to start, but you have to start to be great.", author: "Zig Ziglar" },
  { text: "The only person you should try to be better than is the person you were yesterday.", author: "Unknown" },
  { text: "Success is the sum of small efforts repeated day in and day out.", author: "Robert Collier" },
  { text: "It's not about being the best. It's about being better than you were yesterday.", author: "Unknown" },
  { text: "Hard work beats talent when talent doesn't work hard.", author: "Tim Notke" },
  { text: "The difference between ordinary and extraordinary is that little extra.", author: "Jimmy Johnson" },
  { text: "Don't watch the clock; do what it does. Keep going.", author: "Sam Levenson" },
  { text: "Your future is created by what you do today, not tomorrow.", author: "Robert Kiyosaki" },
  { text: "Champions keep playing until they get it right.", author: "Billie Jean King" },
  { text: "Discipline is choosing between what you want now and what you want most.", author: "Abraham Lincoln" },
  { text: "The pain you feel today will be the strength you feel tomorrow.", author: "Unknown" },
  { text: "Progress, not perfection.", author: "Unknown" },
  { text: "You are never too old to set another goal or to dream a new dream.", author: "C.S. Lewis" },
  { text: "Every expert was once a beginner.", author: "Helen Hayes" },
  { text: "The secret of getting ahead is getting started.", author: "Mark Twain" },
  { text: "What you do today can improve all your tomorrows.", author: "Ralph Marston" },
  { text: "Push yourself because no one else is going to do it for you.", author: "Unknown" },
  { text: "Great things never come from comfort zones.", author: "Unknown" },
  { text: "Wake up with determination. Go to bed with satisfaction.", author: "Unknown" },
  { text: "Believe you can and you're halfway there.", author: "Theodore Roosevelt" },
  { text: "The only way to do great work is to love what you do.", author: "Steve Jobs" },
  { text: "Don't limit your challenges. Challenge your limits.", author: "Unknown" },
  { text: "Success is not final, failure is not fatal: it is the courage to continue that counts.", author: "Winston Churchill" },
  { text: "You miss 100% of the shots you don't take.", author: "Wayne Gretzky" },
  { text: "It always seems impossible until it's done.", author: "Nelson Mandela" },
  { text: "Strive for progress, not perfection.", author: "Unknown" },
  { text: "The harder you work for something, the greater you'll feel when you achieve it.", author: "Unknown" },
  { text: "Dream big. Start small. Act now.", author: "Robin Sharma" },
  { text: "Your only limit is your mind.", author: "Unknown" },
  { text: "Fall seven times, stand up eight.", author: "Japanese Proverb" }
];

// Get quote based on day of year for consistent daily rotation
const getDailyQuote = () => {
  const now = new Date();
  const start = new Date(now.getFullYear(), 0, 0);
  const diff = now - start;
  const oneDay = 1000 * 60 * 60 * 24;
  const dayOfYear = Math.floor(diff / oneDay);
  return MOTIVATIONAL_QUOTES[dayOfYear % MOTIVATIONAL_QUOTES.length];
};

// Get a random quote (for refresh)
const getRandomQuote = (currentQuote) => {
  let newQuote;
  do {
    newQuote = MOTIVATIONAL_QUOTES[Math.floor(Math.random() * MOTIVATIONAL_QUOTES.length)];
  } while (newQuote.text === currentQuote?.text && MOTIVATIONAL_QUOTES.length > 1);
  return newQuote;
};

export const DailyQuote = ({ className = '' }) => {
  const [quote, setQuote] = useState(getDailyQuote());
  const [isRefreshing, setIsRefreshing] = useState(false);

  const handleRefresh = () => {
    setIsRefreshing(true);
    setTimeout(() => {
      setQuote(getRandomQuote(quote));
      setIsRefreshing(false);
    }, 300);
  };

  return (
    <div 
      className={`bg-gradient-to-br from-zinc-900 to-zinc-950 border border-zinc-800 rounded-md p-4 ${className}`}
      data-testid="daily-quote-card"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <Quote className="w-4 h-4 text-primary" />
            <span className="text-zinc-500 text-xs font-body uppercase tracking-wide">Daily Motivation</span>
          </div>
          <p className="text-white text-sm font-body leading-relaxed italic">
            "{quote.text}"
          </p>
          <p className="text-zinc-500 text-xs font-body mt-2">
            — {quote.author}
          </p>
        </div>
        <button
          onClick={handleRefresh}
          className="p-1.5 rounded-full hover:bg-zinc-800 transition-colors text-zinc-500 hover:text-zinc-300"
          title="Get a new quote"
          data-testid="refresh-quote-btn"
        >
          <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
        </button>
      </div>
    </div>
  );
};
