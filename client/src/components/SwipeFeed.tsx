import { useState, useEffect, useCallback, useRef } from 'react';
import { getFeed, castVote } from '../api/endpoints';
import type { AdFeedItem } from '../api/types';

const API_BASE = 'http://localhost:8000';

interface SwipeFeedProps {
  isAuthenticated: boolean;
}

export default function SwipeFeed({ isAuthenticated }: SwipeFeedProps) {
  const [ads, setAds] = useState<AdFeedItem[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [swiping, setSwiping] = useState<'left' | 'right' | 'up' | 'down' | null>(null);
  const [error, setError] = useState<string | null>(null);
  const touchStartX = useRef(0);
  const touchStartY = useRef(0);
  const feedRef = useRef<HTMLDivElement>(null);

  const loadAds = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const excludeIds = ads.map(a => a.id).join(',');
      const newAds = await getFeed(10, excludeIds);
      if (newAds.length > 0) {
        setAds(prev => [...prev, ...newAds]);
      }
    } catch (err) {
      setError('Failed to load ads. Is the server running?');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [ads]);

  useEffect(() => {
    loadAds();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Load more when we're near the end
  useEffect(() => {
    if (ads.length > 0 && currentIndex >= ads.length - 3) {
      loadAds();
    }
  }, [currentIndex, ads.length, loadAds]);

  const handleSkip = useCallback(() => {
    setSwiping('right');
    setTimeout(() => {
      setCurrentIndex(prev => prev + 1);
      setSwiping(null);
    }, 300);
  }, []);

  const handleVote = useCallback(async (vote: number) => {
    const ad = ads[currentIndex];
    if (!ad) return;

    setSwiping(vote === 1 ? 'up' : 'down');

    setAds(prev => prev.map((a, i) => {
      if (i !== currentIndex) return a;
      const prevVote = a.user_vote;
      let { upvotes, downvotes } = a;
      if (vote === 1) {
        upvotes += 1;
        if (prevVote === -1) downvotes = Math.max(0, downvotes - 1);
      } else {
        downvotes += 1;
        if (prevVote === 1) upvotes = Math.max(0, upvotes - 1);
      }
      const total = upvotes + downvotes;
      const score = total > 0 ? (upvotes / total) * 100 : 0;
      return { ...a, upvotes, downvotes, score, user_vote: vote };
    }));

    if (isAuthenticated) {
      try {
        await castVote(ad.id, vote);
      } catch (err) {
        console.error('Vote failed:', err);
      }
    }

    setTimeout(() => {
      setCurrentIndex(prev => prev + 1);
      setSwiping(null);
    }, 300);
  }, [ads, currentIndex, isAuthenticated]);

  const handleGoBack = useCallback(() => {
    if (currentIndex > 0) {
      setCurrentIndex(prev => prev - 1);
    }
  }, [currentIndex]);

  const handleTouchStart = (e: React.TouchEvent) => {
    touchStartX.current = e.touches[0].clientX;
    touchStartY.current = e.touches[0].clientY;
  };

  const handleTouchEnd = (e: React.TouchEvent) => {
    const dx = e.changedTouches[0].clientX - touchStartX.current;
    const dy = e.changedTouches[0].clientY - touchStartY.current;

    if (Math.abs(dy) > Math.abs(dx) && Math.abs(dy) > 50) {
      if (dy < 0) {
        handleVote(1);
      } else {
        handleVote(-1);
      }
    } else if (Math.abs(dx) > Math.abs(dy) && Math.abs(dx) > 50) {
      handleSkip();
    }
  };

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      switch (e.key) {
        case 'ArrowRight':
          e.preventDefault();
          handleSkip();
          break;
        case 'ArrowLeft':
          e.preventDefault();
          handleGoBack();
          break;
        case 'ArrowUp':
          e.preventDefault();
          handleVote(1);
          break;
        case 'ArrowDown':
          e.preventDefault();
          handleVote(-1);
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleSkip, handleGoBack, handleVote]);

  const currentAd = ads[currentIndex];

  if (loading && ads.length === 0) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  if (error && ads.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-full px-6 text-center">
        <p className="text-gray-400 text-lg mb-4">{error}</p>
        <button
          onClick={loadAds}
          className="px-6 py-2 bg-primary text-white rounded-full font-semibold"
        >
          Retry
        </button>
      </div>
    );
  }

  if (!currentAd) {
    return (
      <div className="flex flex-col items-center justify-center h-full px-6 text-center">
        <p className="text-gray-400 text-lg mb-4">No more ads to show!</p>
        <button
          onClick={() => {
            setAds([]);
            setCurrentIndex(0);
            loadAds();
          }}
          className="px-6 py-2 bg-primary text-white rounded-full font-semibold"
        >
          Load More
        </button>
      </div>
    );
  }

  return (
    <div className="relative h-full w-full max-w-md mx-auto flex flex-col">
      {/* Swipe Area */}
      <div
        ref={feedRef}
        className="relative flex-1 overflow-hidden"
        onTouchStart={handleTouchStart}
        onTouchEnd={handleTouchEnd}
      >
        {/* Ad Card */}
        <div
          className={`absolute inset-0 flex items-center justify-center transition-transform duration-300 ${
            swiping === 'right' ? 'animate-swipe-right' : ''
          } ${swiping === 'left' ? 'animate-swipe-left' : ''} ${
            swiping === 'up' ? 'animate-swipe-up' : ''
          } ${swiping === 'down' ? 'animate-swipe-down' : ''}`}
        >
          <div className="relative w-full h-full bg-black">
            {/* Media */}
            {currentAd.media_type === 'video' ? (
              <video
                src={`${API_BASE}${currentAd.media_url}`}
                className="w-full h-full object-cover"
                controls
                autoPlay
                muted
                loop
                playsInline
              />
            ) : (
              <img
                src={`${API_BASE}${currentAd.media_url}`}
                alt={currentAd.title}
                className="w-full h-full object-cover"
              />
            )}

            {/* Info Overlay */}
            <div className="absolute bottom-0 left-0 right-0 p-6 bg-gradient-to-t from-black/90 via-black/40 to-transparent">
              <div className="flex items-center gap-2 mb-2">
                <span className="px-2 py-1 text-xs bg-primary/80 rounded-full">
                  {currentAd.category}
                </span>
                <span className="text-sm text-gray-300">{currentAd.brand}</span>
              </div>
              <h2 className="text-xl font-bold mb-1">{currentAd.title}</h2>
              {currentAd.description && (
                <p className="text-sm text-gray-200 mb-3 line-clamp-2">{currentAd.description}</p>
              )}

              {/* Tags */}
              {currentAd.tags && (
                <div className="flex flex-wrap gap-1 mb-3">
                  {currentAd.tags.split(',').map((tag, i) => (
                    <span key={i} className="text-xs text-gray-400 bg-white/10 px-2 py-0.5 rounded-full">
                      #{tag.trim()}
                    </span>
                  ))}
                </div>
              )}

              {/* Score */}
              <div className="flex items-center gap-4 text-sm">
                <span className="text-green-400">👍 {currentAd.upvotes}</span>
                <span className="text-red-400">👎 {currentAd.downvotes}</span>
                <span className="text-gray-400">Score: {Math.round(currentAd.score)}%</span>
              </div>
            </div>
          </div>
        </div>

        {/* Go Back Button */}
        {currentIndex > 0 && (
          <button
            onClick={handleGoBack}
            className="absolute top-4 left-4 z-10 w-10 h-10 rounded-full bg-white/20 flex items-center justify-center text-lg shadow-lg hover:bg-white/30 transition-colors active:scale-95"
          >
            ↩
          </button>
        )}

        {/* Progress indicator */}
        <div className={`absolute top-4 ${currentIndex > 0 ? 'left-14' : 'left-4'} right-4 z-10 flex gap-1`}>
          {ads.slice(currentIndex, currentIndex + 5).map((_, i) => (
            <div
              key={i}
              className={`h-1 flex-1 rounded-full ${
                i === 0 ? 'bg-white' : 'bg-white/30'
              }`}
            />
          ))}
        </div>

        {/* Not authenticated hint */}
        {!isAuthenticated && (
          <div className="absolute top-12 left-4 z-10 bg-yellow-500/90 text-black text-xs px-3 py-1 rounded-full">
            Sign in to save your votes
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="flex items-center justify-center gap-6 py-4 px-6 bg-dark">
        <button
          onClick={() => handleVote(-1)}
          className="flex items-center justify-center w-16 h-16 rounded-full bg-red-500/20 text-3xl hover:bg-red-500/40 active:scale-90 transition-all"
          aria-label="Dislike"
        >
          👎
        </button>
        <button
          onClick={handleSkip}
          className="flex items-center justify-center w-12 h-12 rounded-full bg-gray-500/20 text-xl hover:bg-gray-500/40 active:scale-90 transition-all"
          aria-label="Skip"
        >
          ⏭
        </button>
        <button
          onClick={() => handleVote(1)}
          className="flex items-center justify-center w-16 h-16 rounded-full bg-green-500/20 text-3xl hover:bg-green-500/40 active:scale-90 transition-all"
          aria-label="Like"
        >
          👍
        </button>
      </div>
    </div>
  );
}