"use client";

import { useState, useEffect } from 'react';
import { 
  Grid, List, ChevronLeft, ChevronRight, RotateCcw, 
  SortAsc, SortDesc, Filter, Download, Share2 
} from 'lucide-react';
import OpportunityCard from './OpportunityCard';

interface FundingOpportunity {
  id: number;
  title: string;
  description: string;
  amount_min?: number;
  amount_max?: number;
  amount_exact?: number;
  currency: string;
  deadline?: string;
  status: string;
  provider_organization?: {
    name: string;
    type: string;
    country?: string;
  };
  funding_type?: {
    name: string;
    category: string;
  };
  equity_score?: number;
  underserved_focus?: boolean;
  women_focus?: boolean;
  youth_focus?: boolean;
  rural_focus?: boolean;
  created_at?: string;
  last_checked?: string;
}

interface SearchResultsProps {
  searchMode: 'discover' | 'explore';
  filters: any;
  loading: boolean;
  onLoadMore?: () => void;
}

interface SearchResultsState {
  opportunities: FundingOpportunity[];
  total: number;
  currentPage: number;
  totalPages: number;
  perPage: number;
  sortBy: string;
  sortOrder: 'asc' | 'desc';
  viewMode: 'grid' | 'list';
  selectedFilters: string[];
}

export default function SearchResults({ searchMode, filters, loading, onLoadMore }: SearchResultsProps) {
  const [state, setState] = useState<SearchResultsState>({
    opportunities: [],
    total: 0,
    currentPage: 1,
    totalPages: 1,
    perPage: 20,
    sortBy: 'deadline',
    sortOrder: 'asc',
    viewMode: 'grid',
    selectedFilters: []
  });

  const [showSortOptions, setShowSortOptions] = useState(false);
  const [isExporting, setIsExporting] = useState(false);

  const sortOptions = [
    { value: 'deadline', label: 'Deadline', icon: '📅' },
    { value: 'amount', label: 'Funding Amount', icon: '💰' },
    { value: 'equity_score', label: 'Equity Score', icon: '⚖️' },
    { value: 'relevance', label: 'Relevance', icon: '🎯' },
    { value: 'created_at', label: 'Recently Added', icon: '🕐' },
    { value: 'organization', label: 'Organization', icon: '🏢' }
  ];

  // Mock data for demonstration
  const mockOpportunities: FundingOpportunity[] = [
    {
      id: 1,
      title: "AI for Healthcare Innovation Grant",
      description: "Supporting the development of AI-powered healthcare solutions for underserved communities in Central Africa. Focus on maternal health, infectious disease monitoring, and telemedicine infrastructure.",
      amount_exact: 150000,
      currency: "USD",
      deadline: "2024-09-15",
      status: "active",
      provider_organization: {
        name: "Bill & Melinda Gates Foundation",
        type: "Private Foundation",
        country: "USA"
      },
      funding_type: {
        name: "Development Grant",
        category: "grant"
      },
      equity_score: 85,
      underserved_focus: true,
      women_focus: false,
      youth_focus: false,
      rural_focus: true,
      created_at: "2024-07-01",
      last_checked: "2024-07-15"
    },
    {
      id: 2,
      title: "AgriTech Seed Investment Program",
      description: "Early-stage investment for agricultural technology startups focusing on smallholder farmers in East Africa. Looking for innovative solutions in crop monitoring, precision agriculture, and supply chain optimization.",
      amount_min: 50000,
      amount_max: 500000,
      currency: "USD",
      deadline: "2024-08-30",
      status: "active",
      provider_organization: {
        name: "Acumen Fund",
        type: "Impact Investor",
        country: "Kenya"
      },
      funding_type: {
        name: "Seed Investment",
        category: "investment"
      },
      equity_score: 72,
      underserved_focus: true,
      women_focus: true,
      youth_focus: true,
      rural_focus: true,
      created_at: "2024-06-15",
      last_checked: "2024-07-14"
    },
    {
      id: 3,
      title: "Women in AI Research Fellowship",
      description: "Supporting women researchers in artificial intelligence across African universities. Covers research expenses, conference attendance, and mentorship programs. Focus on machine learning applications in local contexts.",
      amount_exact: 25000,
      currency: "USD",
      deadline: "2024-10-01",
      status: "active",
      provider_organization: {
        name: "Google AI",
        type: "Corporate",
        country: "USA"
      },
      funding_type: {
        name: "Research Fellowship",
        category: "fellowship"
      },
      equity_score: 90,
      underserved_focus: false,
      women_focus: true,
      youth_focus: true,
      rural_focus: false,
      created_at: "2024-07-10",
      last_checked: "2024-07-16"
    }
  ];

  useEffect(() => {
    // Simulate API call
    const fetchResults = async () => {
      // In real implementation, this would fetch from API based on filters
      const filteredOpportunities = mockOpportunities.filter(opp => {
        if (searchMode === 'discover' && opp.status !== 'active') return false;
        if (filters.funding_type && opp.funding_type?.category !== filters.funding_type) return false;
        if (filters.underserved_focus && !opp.underserved_focus) return false;
        if (filters.women_focus && !opp.women_focus) return false;
        if (filters.youth_focus && !opp.youth_focus) return false;
        if (filters.rural_focus && !opp.rural_focus) return false;
        if (filters.min_amount && opp.amount_exact && opp.amount_exact < filters.min_amount) return false;
        if (filters.max_amount && opp.amount_exact && opp.amount_exact > filters.max_amount) return false;
        return true;
      });

      setState(prev => ({
        ...prev,
        opportunities: filteredOpportunities,
        total: filteredOpportunities.length,
        totalPages: Math.ceil(filteredOpportunities.length / prev.perPage)
      }));
    };

    fetchResults();
  }, [searchMode, filters]);

  const handleSort = (sortBy: string) => {
    setState(prev => ({
      ...prev,
      sortBy,
      sortOrder: prev.sortBy === sortBy && prev.sortOrder === 'asc' ? 'desc' : 'asc'
    }));
    setShowSortOptions(false);
  };

  const handlePageChange = (page: number) => {
    setState(prev => ({ ...prev, currentPage: page }));
  };

  const handlePerPageChange = (perPage: number) => {
    setState(prev => ({ 
      ...prev, 
      perPage,
      currentPage: 1,
      totalPages: Math.ceil(prev.total / perPage)
    }));
  };

  const handleViewModeChange = (viewMode: 'grid' | 'list') => {
    setState(prev => ({ ...prev, viewMode }));
  };

  const handleExport = async () => {
    setIsExporting(true);
    // Simulate export
    setTimeout(() => {
      setIsExporting(false);
    }, 2000);
  };

  const getDisplayedOpportunities = () => {
    const start = (state.currentPage - 1) * state.perPage;
    const end = start + state.perPage;
    return state.opportunities.slice(start, end);
  };

  const displayedOpportunities = getDisplayedOpportunities();

  return (
    <div className="space-y-6">
      {/* Results Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">
              {searchMode === 'discover' ? 'Active Opportunities' : 'All Opportunities'}
            </h2>
            <p className="text-sm text-gray-600">
              {loading ? 'Loading...' : `${state.total} opportunities found`}
            </p>
          </div>
          
          {/* Active Filters */}
          {state.selectedFilters.length > 0 && (
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-500">Filters:</span>
              <div className="flex flex-wrap gap-2">
                {state.selectedFilters.map((filter, index) => (
                  <span key={index} className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs">
                    {filter}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="flex items-center space-x-3">
          {/* Sort */}
          <div className="relative">
            <button
              onClick={() => setShowSortOptions(!showSortOptions)}
              className="flex items-center space-x-2 px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              {state.sortOrder === 'asc' ? <SortAsc className="w-4 h-4" /> : <SortDesc className="w-4 h-4" />}
              <span className="text-sm">Sort by {sortOptions.find(o => o.value === state.sortBy)?.label}</span>
            </button>
            
            {showSortOptions && (
              <div className="absolute right-0 mt-2 w-48 bg-white border border-gray-300 rounded-lg shadow-lg z-10">
                {sortOptions.map((option) => (
                  <button
                    key={option.value}
                    onClick={() => handleSort(option.value)}
                    className={`w-full px-4 py-2 text-left hover:bg-gray-50 flex items-center space-x-2 ${
                      state.sortBy === option.value ? 'bg-blue-50 text-blue-600' : 'text-gray-700'
                    }`}
                  >
                    <span>{option.icon}</span>
                    <span className="text-sm">{option.label}</span>
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* View Mode */}
          <div className="flex items-center border border-gray-300 rounded-lg">
            <button
              onClick={() => handleViewModeChange('grid')}
              className={`p-2 ${state.viewMode === 'grid' ? 'bg-blue-100 text-blue-600' : 'text-gray-600 hover:bg-gray-50'}`}
            >
              <Grid className="w-4 h-4" />
            </button>
            <button
              onClick={() => handleViewModeChange('list')}
              className={`p-2 ${state.viewMode === 'list' ? 'bg-blue-100 text-blue-600' : 'text-gray-600 hover:bg-gray-50'}`}
            >
              <List className="w-4 h-4" />
            </button>
          </div>

          {/* Export */}
          <button
            onClick={handleExport}
            disabled={isExporting}
            className="flex items-center space-x-2 px-3 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 transition-colors"
          >
            <Download className="w-4 h-4" />
            <span className="text-sm">{isExporting ? 'Exporting...' : 'Export'}</span>
          </button>

          {/* Share */}
          <button className="flex items-center space-x-2 px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
            <Share2 className="w-4 h-4" />
            <span className="text-sm">Share</span>
          </button>
        </div>
      </div>

      {/* Results */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, index) => (
            <div key={index} className="bg-white rounded-xl shadow-lg border border-gray-200 p-6 animate-pulse">
              <div className="space-y-4">
                <div className="h-6 bg-gray-200 rounded w-3/4"></div>
                <div className="h-4 bg-gray-200 rounded w-1/2"></div>
                <div className="space-y-2">
                  <div className="h-3 bg-gray-200 rounded"></div>
                  <div className="h-3 bg-gray-200 rounded w-5/6"></div>
                </div>
                <div className="flex space-x-2">
                  <div className="h-6 bg-gray-200 rounded w-16"></div>
                  <div className="h-6 bg-gray-200 rounded w-20"></div>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : displayedOpportunities.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-gray-400 mb-4">
            <Filter className="w-12 h-12 mx-auto" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No opportunities found</h3>
          <p className="text-gray-600 mb-4">
            {searchMode === 'discover' 
              ? 'No active opportunities match your search criteria.' 
              : 'No opportunities match your search criteria.'}
          </p>
          <button
            onClick={() => {/* Reset filters */}}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors mx-auto"
          >
            <RotateCcw className="w-4 h-4" />
            <span>Reset Filters</span>
          </button>
        </div>
      ) : (
        <div className={
          state.viewMode === 'grid' 
            ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6' 
            : 'space-y-4'
        }>
          {displayedOpportunities.map((opportunity) => (
            <OpportunityCard
              key={opportunity.id}
              opportunity={opportunity}
              searchMode={searchMode}
              onViewDetails={(id) => console.log('View details for', id)}
            />
          ))}
        </div>
      )}

      {/* Pagination */}
      {!loading && displayedOpportunities.length > 0 && state.totalPages > 1 && (
        <div className="flex items-center justify-between border-t border-gray-200 pt-6">
          <div className="flex items-center space-x-4">
            <div className="text-sm text-gray-600">
              Showing {(state.currentPage - 1) * state.perPage + 1} to {Math.min(state.currentPage * state.perPage, state.total)} of {state.total} opportunities
            </div>
            
            <select
              value={state.perPage}
              onChange={(e) => handlePerPageChange(Number(e.target.value))}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value={10}>10 per page</option>
              <option value={20}>20 per page</option>
              <option value={50}>50 per page</option>
              <option value={100}>100 per page</option>
            </select>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={() => handlePageChange(state.currentPage - 1)}
              disabled={state.currentPage === 1}
              className="flex items-center space-x-2 px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <ChevronLeft className="w-4 h-4" />
              <span>Previous</span>
            </button>

            {/* Page Numbers */}
            <div className="flex items-center space-x-1">
              {[...Array(Math.min(5, state.totalPages))].map((_, index) => {
                const pageNum = index + 1;
                return (
                  <button
                    key={pageNum}
                    onClick={() => handlePageChange(pageNum)}
                    className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                      state.currentPage === pageNum
                        ? 'bg-blue-600 text-white'
                        : 'text-gray-700 hover:bg-gray-100'
                    }`}
                  >
                    {pageNum}
                  </button>
                );
              })}
              
              {state.totalPages > 5 && (
                <>
                  <span className="px-2 text-gray-500">...</span>
                  <button
                    onClick={() => handlePageChange(state.totalPages)}
                    className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                      state.currentPage === state.totalPages
                        ? 'bg-blue-600 text-white'
                        : 'text-gray-700 hover:bg-gray-100'
                    }`}
                  >
                    {state.totalPages}
                  </button>
                </>
              )}
            </div>

            <button
              onClick={() => handlePageChange(state.currentPage + 1)}
              disabled={state.currentPage === state.totalPages}
              className="flex items-center space-x-2 px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <span>Next</span>
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* Load More (for infinite scroll alternative) */}
      {onLoadMore && state.currentPage < state.totalPages && (
        <div className="text-center pt-6">
          <button
            onClick={onLoadMore}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Load More Opportunities
          </button>
        </div>
      )}
    </div>
  );
}