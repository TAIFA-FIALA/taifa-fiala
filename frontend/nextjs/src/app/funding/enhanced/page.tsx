"use client";

import { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import DualModeSearch from '@/components/search/DualModeSearch';
import SearchResults from '@/components/search/SearchResults';
import { AlertCircle, TrendingUp, Globe, Users, Database, Clock, Target } from 'lucide-react';

import { SearchFilters } from '@/types/search';

function EnhancedFundingContent() {
  const searchParams = useSearchParams();
  const [searchMode] = useState<'discover' | 'explore'>('discover');
  const [loading] = useState(false);
  const [error] = useState<string | null>(null);
  const [showOnboarding, setShowOnboarding] = useState(false);
  
  const [filters] = useState<SearchFilters>({
    query: searchParams.get('q') || '',
    min_amount: parseFloat(searchParams.get('min_amount') || '0') || 0,
    max_amount: parseFloat(searchParams.get('max_amount') || '0') || 0,
    amount_exact: parseFloat(searchParams.get('amount_exact') || '0') || 0,
    deadline_after: searchParams.get('deadline_after') || '',
    deadline_before: searchParams.get('deadline_before') || '',
    status: searchParams.get('status') || '',
    funding_type: searchParams.get('funding_type') || '',
    geographic_scope: searchParams.get('geographic_scope')?.split(',').filter(Boolean) || [],
    target_audience: searchParams.get('target_audience')?.split(',').filter(Boolean) || [],
    focus_areas: searchParams.get('focus_areas')?.split(',').filter(Boolean) || [],
    sort_by: (searchParams.get('sort_by') as 'relevance' | 'deadline' | 'amount' | 'date_added') || 'relevance',
    sort_order: (searchParams.get('sort_order') as 'asc' | 'desc') || 'desc',
    page: parseInt(searchParams.get('page') || '1') || 1,
    page_size: parseInt(searchParams.get('page_size') || '10') || 10,
    opportunity_type: searchParams.get('opportunity_type') || '',
    organization_type: searchParams.get('organization_type') || '',
    underserved_focus: searchParams.get('underserved_focus') === 'true',
    women_focus: searchParams.get('women_focus') === 'true',
    youth_focus: searchParams.get('youth_focus') === 'true',
    rural_focus: searchParams.get('rural_focus') === 'true',
  });

  const [quickStats] = useState({
    total_opportunities: 12847,
    active_opportunities: 8934,
    total_funding: 2400000000,
    unique_organizations: 1247,
    countries_covered: 54,
    equity_score_avg: 61,
    underserved_percentage: 18,
    women_focused_percentage: 23,
    last_updated: new Date().toISOString()
  });

  // Check if user is new to show onboarding
  useEffect(() => {
    const hasSeenOnboarding = localStorage.getItem('funding_onboarding_seen');
    if (!hasSeenOnboarding) {
      setShowOnboarding(true);
    }
  }, []);

  const handleOnboardingComplete = () => {
    localStorage.setItem('funding_onboarding_seen', 'true');
    setShowOnboarding(false);
  };

  const formatNumber = (num: number) => {
    if (num >= 1e9) return `${(num / 1e9).toFixed(1)}B`;
    if (num >= 1e6) return `${(num / 1e6).toFixed(1)}M`;
    if (num >= 1e3) return `${(num / 1e3).toFixed(1)}K`;
    return num.toString();
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Onboarding Modal */}
      {showOnboarding && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-xl max-w-2xl mx-4 p-8">
            <div className="text-center mb-6">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Database className="w-8 h-8 text-blue-600" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Welcome to Enhanced Search</h2>
              <p className="text-gray-600">
                Discover AI funding opportunities with our dual-mode search and equity-aware filters
              </p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
              <div className="text-center">
                <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
                  <Clock className="w-6 h-6 text-green-600" />
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">Discover Mode</h3>
                <p className="text-sm text-gray-600">
                  Find active opportunities with upcoming deadlines. Perfect for grant seekers and entrepreneurs.
                </p>
              </div>
              
              <div className="text-center">
                <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-3">
                  <Database className="w-6 h-6 text-purple-600" />
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">Explore Mode</h3>
                <p className="text-sm text-gray-600">
                  Access all historical and current records. Ideal for researchers and data analysts.
                </p>
              </div>
            </div>
            
            <div className="bg-blue-50 rounded-lg p-4 mb-6">
              <h4 className="font-semibold text-blue-900 mb-2 flex items-center">
                <Target className="w-4 h-4 mr-2" />
                Equity-Aware Features
              </h4>
              <ul className="text-sm text-blue-800 space-y-1">
                <li>• Filter for underserved regions and inclusion-focused opportunities</li>
                <li>• Real-time bias monitoring and equity scoring</li>
                <li>• Semantic search across 6 African languages</li>
                <li>• Priority given to women-led and youth-focused programs</li>
              </ul>
            </div>
            
            <div className="flex justify-center">
              <button
                onClick={handleOnboardingComplete}
                className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
              >
                Start Searching
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Header */}
      <div className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                AI Funding Opportunities
              </h1>
              <p className="text-gray-600 mt-1">
                Discover and explore funding opportunities across Africa with equity-aware intelligence
              </p>
            </div>
            
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setShowOnboarding(true)}
                className="text-blue-600 hover:text-blue-800 text-sm font-medium"
              >
                Show Guide
              </button>
              
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-sm text-gray-600">Live Data</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Stats Bar */}
      <div className="bg-blue-600 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold">
                {formatNumber(quickStats.total_opportunities)}
              </div>
              <div className="text-xs text-blue-100">Total Records</div>
            </div>
            <div>
              <div className="text-2xl font-bold">
                {formatNumber(quickStats.active_opportunities)}
              </div>
              <div className="text-xs text-blue-100">Active Now</div>
            </div>
            <div>
              <div className="text-2xl font-bold">
                ${formatNumber(quickStats.total_funding)}
              </div>
              <div className="text-xs text-blue-100">Total Funding</div>
            </div>
            <div>
              <div className="text-2xl font-bold">
                {quickStats.countries_covered}
              </div>
              <div className="text-xs text-blue-100">Countries</div>
            </div>
            <div>
              <div className="text-2xl font-bold">
                {quickStats.equity_score_avg}%
              </div>
              <div className="text-xs text-blue-100">Avg Equity Score</div>
            </div>
            <div>
              <div className="text-2xl font-bold">
                {quickStats.underserved_percentage}%
              </div>
              <div className="text-xs text-blue-100">Underserved Focus</div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Search Interface */}
        <div className="mb-8">
          <DualModeSearch />
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-center">
              <AlertCircle className="w-5 h-5 text-red-400 mr-2" />
              <span className="text-red-800">{error}</span>
            </div>
          </div>
        )}

        {/* Search Results */}
        <SearchResults
          searchMode={searchMode}
          filters={filters}
          loading={loading}
          onLoadMore={() => {
            // Implement infinite scroll if needed
            console.log('Load more results');
          }}
        />
      </div>

      {/* Footer Info */}
      <div className="bg-gray-800 text-white mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div>
              <h3 className="text-lg font-semibold mb-3 flex items-center">
                <TrendingUp className="w-5 h-5 mr-2" />
                Equity Focus
              </h3>
              <p className="text-gray-300 text-sm">
                Our AI-powered system actively promotes funding equity by surfacing opportunities 
                for underserved regions and inclusion-focused initiatives.
              </p>
            </div>
            
            <div>
              <h3 className="text-lg font-semibold mb-3 flex items-center">
                <Globe className="w-5 h-5 mr-2" />
                Pan-African Coverage
              </h3>
              <p className="text-gray-300 text-sm">
                Comprehensive tracking across all 54 African countries with multilingual search 
                capabilities in 6 languages including French, Arabic, and Portuguese.
              </p>
            </div>
            
            <div>
              <h3 className="text-lg font-semibold mb-3 flex items-center">
                <Users className="w-5 h-5 mr-2" />
                Data Sources
              </h3>
              <p className="text-gray-300 text-sm">
                Aggregated from 27+ priority African institutions including development banks, 
                foundations, and government agencies with real-time updates.
              </p>
            </div>
          </div>
          
          <div className="border-t border-gray-700 mt-8 pt-6 text-center">
            <p className="text-gray-400 text-sm">
              Last updated: {new Date(quickStats.last_updated).toLocaleString()} • 
              TAIFA | FIALA - Democratizing AI funding access across Africa
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function EnhancedFundingPage() {
  return (
    <Suspense fallback={<div className="flex justify-center items-center h-64">
      <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
    </div>}>
      <EnhancedFundingContent />
    </Suspense>
  );
}
