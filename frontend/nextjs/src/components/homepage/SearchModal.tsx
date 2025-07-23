"use client";

import { useState, useEffect } from 'react';
import { X, Search, Loader2, AlertCircle, Database } from 'lucide-react';
import AnnouncementCard from '@/components/search/AnnouncementCard';
import { FundingAnnouncement } from '@/types/funding';
import { getApiUrl, API_ENDPOINTS } from '@/lib/api-config';

interface SearchModalProps {
  isOpen: boolean;
  onClose: () => void;
  initialQuery?: string;
}

interface SearchResponse {
  opportunities: FundingAnnouncement[];
  metadata: {
    total_count: number;
    traditional_results_count: number;
    final_count: number;
    search_strategy: string;
    vector_enhancement_used: boolean;
    search_timestamp: string;
  };
}

export default function SearchModal({ isOpen, onClose, initialQuery = '' }: SearchModalProps) {
  const [query, setQuery] = useState(initialQuery);
  const [results, setResults] = useState<FundingAnnouncement[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchMetadata, setSearchMetadata] = useState<SearchResponse['metadata'] | null>(null);
  const [hasSearched, setHasSearched] = useState(false);

  // Reset state when modal opens/closes
  useEffect(() => {
    if (isOpen && initialQuery) {
      setQuery(initialQuery);
      handleSearch();
    } else if (!isOpen) {
      setQuery('');
      setResults([]);
      setError(null);
      setSearchMetadata(null);
      setHasSearched(false);
    }
  }, [isOpen, initialQuery]);

  const handleSearch = async (searchQuery: string = query) => {
    if (!searchQuery.trim()) return;

    setLoading(true);
    setError(null);
    setHasSearched(true);

    try {
      const response = await fetch(
        getApiUrl(`${API_ENDPOINTS.intelligentSearch}?q=${encodeURIComponent(searchQuery)}&max_results=10&min_relevance=0.5`)
      );

      if (!response.ok) {
        throw new Error(`Search failed: ${response.status}`);
      }

      const data: SearchResponse = await response.json();
      setResults(data.opportunities || []);
      setSearchMetadata(data.metadata);
    } catch (err) {
      console.error('Search error:', err);
      setError('Search temporarily unavailable. Please try again later.');
      // Show demo data with "More data coming..." message
      setResults([
        {
          id: 1,
          title: "AI Healthcare Innovation Grant - Demo",
          description: "This is sample data to showcase our search functionality. More comprehensive data is being collected and will be available soon.",
          amount_exact: 150000,
          currency: "USD",
          deadline: "2024-12-31",
          status: "active",
          provider_organization: {
            id: 101,
            name: "Sample Foundation",
            type: "Private Foundation",
            country: "USA",
            is_granting_agency: true,
            is_venture_capital: false,
          },
          funding_type: {
            id: 201,
            name: "Development Grant",
            category: "grant",
            requires_equity: false,
            requires_repayment: false,
          },
          equity_score: 85,
          underserved_focus: true,
          women_focus: false,
          youth_focus: false,
          rural_focus: true,
          created_at: "2024-07-01",
          last_checked: "2024-07-15"
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleSearch();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 bg-gradient-to-r from-taifa-primary to-taifa-secondary">
          <div className="flex items-center space-x-3">
            <Search className="w-6 h-6 text-white" />
            <h2 className="text-xl font-bold text-white">Search Funding Announcements</h2>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-white/20 rounded-full transition-colors"
          >
            <X className="w-5 h-5 text-white" />
          </button>
        </div>

        {/* Search Form */}
        <div className="p-6 border-b border-gray-200">
          <form onSubmit={handleSubmit} className="flex space-x-3">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search funding announcements by funder, recipient, or project..."
              className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-taifa-secondary focus:border-taifa-secondary text-lg"
              autoFocus
            />
            <button
              type="submit"
              disabled={loading || !query.trim()}
              className="bg-taifa-secondary hover:bg-yellow-400 text-taifa-primary px-6 py-3 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
            >
              {loading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Search className="w-5 h-5" />
              )}
              <span>Search</span>
            </button>
          </form>
        </div>

        {/* Results */}
        <div className="flex-1 overflow-y-auto p-6">
          {/* Beta Notice */}
          <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex items-start space-x-3">
              <Database className="w-5 h-5 text-blue-600 mt-0.5" />
              <div>
                <h3 className="font-semibold text-blue-900 mb-1">Early Access Preview</h3>
                <p className="text-sm text-blue-700">
                  We're actively building our comprehensive database. Current results showcase our search capabilities 
                  More funding announcements are being added daily.
                </p>
              </div>
            </div>
          </div>

          {loading && (
            <div className="flex items-center justify-center py-12">
              <div className="text-center">
                <Loader2 className="w-8 h-8 animate-spin text-taifa-secondary mx-auto mb-3" />
                <p className="text-gray-600">Searching funding announcements...</p>
              </div>
            </div>
          )}

          {error && !loading && (
            <div className="flex items-center space-x-3 p-4 bg-yellow-50 border border-yellow-200 rounded-lg mb-6">
              <AlertCircle className="w-5 h-5 text-yellow-600" />
              <div>
                <p className="text-yellow-800 font-medium">Demo Mode Active</p>
                <p className="text-sm text-yellow-700">
                  Showing sample data while we build our comprehensive database.
                </p>
              </div>
            </div>
          )}

          {hasSearched && !loading && results.length === 0 && !error && (
            <div className="text-center py-12">
              <Search className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No results found</h3>
              <p className="text-gray-600">
                Try adjusting your search terms or check back soon as we're continuously adding new announcements.
              </p>
            </div>
          )}

          {results.length > 0 && (
            <>
              {/* Search Metadata */}
              {searchMetadata && (
                <div className="mb-6 p-4 bg-gray-50 rounded-lg">
                  <div className="flex items-center justify-between text-sm text-gray-600">
                    <span>
                      Found {searchMetadata.final_count} announcements
                      {searchMetadata.vector_enhancement_used && ' (enhanced with semantic search)'}
                    </span>
                    <span>Search strategy: {searchMetadata.search_strategy}</span>
                  </div>
                </div>
              )}

              {/* Results Grid */}
              <div className="space-y-6">
                {results.map((announcement) => (
                  <div key={announcement.id} className="relative">
                    <AnnouncementCard
                      announcement={announcement}
                      searchMode="discover"
                    />
                    {/* "More data coming" overlay for demo data */}
                    {(error || announcement.title.includes('Demo')) && (
                      <div className="absolute top-4 right-4 bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-xs font-medium">
                        More data coming...
                      </div>
                    )}
                  </div>
                ))}
              </div>

              {/* Footer Message */}
              <div className="mt-8 p-4 bg-taifa-yellow/10 border border-taifa-yellow/30 rounded-lg text-center">
                <p className="text-taifa-primary font-medium mb-2">
                  🚀 Building Africa's Most Comprehensive AI Funding Database
                </p>
                <p className="text-sm text-taifa-primary/80">
                  We're continuously expanding our database with new funding announcements. 
                  Check back regularly for the latest additions.
                </p>
              </div>
            </>
          )}

          {!hasSearched && (
            <div className="text-center py-12">
              <Search className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">Ready to search</h3>
              <p className="text-gray-600">
                Enter your search terms above to discover funding announcements across Africa.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
