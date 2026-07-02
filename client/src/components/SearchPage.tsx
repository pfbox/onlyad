import { useState } from 'react';
import { searchAds } from '../api/endpoints';
import type { Ad } from '../api/types';

const API_BASE = 'http://localhost:8000';

export default function SearchPage() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<Ad[]>([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);

  const handleSearch = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setSearched(true);
    try {
      const ads = await searchAds(query);
      setResults(ads);
    } catch (err) {
      console.error('Search failed:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="h-full flex flex-col bg-dark">
      {/* Search Bar */}
      <div className="p-4 pt-12">
        <div className="flex gap-2">
          <input
            type="text"
            value={query}
            onChange={e => setQuery(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleSearch()}
            placeholder="Search ads by brand, title, or description..."
            className="flex-1 px-4 py-3 bg-surface text-white rounded-full outline-none focus:ring-2 focus:ring-primary placeholder-gray-500"
          />
          <button
            onClick={handleSearch}
            className="px-6 py-3 bg-primary text-white rounded-full font-semibold hover:opacity-90"
          >
            Search
          </button>
        </div>
      </div>

      {/* Results */}
      <div className="flex-1 overflow-y-auto px-4 pb-20">
        {loading && (
          <div className="flex justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-4 border-primary border-t-transparent" />
          </div>
        )}

        {!loading && searched && results.length === 0 && (
          <p className="text-center text-gray-400 py-12">No results found for "{query}"</p>
        )}

        {!loading && results.length > 0 && (
          <div className="grid grid-cols-4 gap-2">
            {results.map(ad => (
              <div key={ad.id} className="bg-surface rounded-lg overflow-hidden">
                <div className="aspect-square bg-black">
                  {ad.media_type === 'video' ? (
                    <video
                      src={`${API_BASE}${ad.media_url}`}
                      className="w-full h-full object-cover"
                      controls
                      muted
                      playsInline
                    />
                  ) : (
                    <img
                      src={`${API_BASE}${ad.media_url}`}
                      alt={ad.title}
                      className="w-full h-full object-cover"
                    />
                  )}
                </div>
                <div className="p-2">
                  <span className="px-1.5 py-0.5 text-[9px] bg-primary/20 text-primary rounded-full">
                    {ad.category}
                  </span>
                  <h3 className="font-semibold text-xs mt-1 line-clamp-1">{ad.title}</h3>
                  <p className="text-[10px] text-gray-400 line-clamp-1">{ad.brand}</p>
                  <div className="flex items-center gap-1.5 text-[10px] mt-1">
                    <span className="text-green-400">👍 {ad.upvotes}</span>
                    <span className="text-red-400">👎 {ad.downvotes}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}