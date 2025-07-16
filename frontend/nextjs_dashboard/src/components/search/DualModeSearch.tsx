"use client";

import { useState, useEffect } from 'react';
import { Search, Filter, ToggleLeft, ToggleRight, Database, Clock, Globe, Users, Brain, TrendingUp } from 'lucide-react';

interface SearchMode {
  mode: 'discover' | 'explore';
  label: string;
  description: string;
  icon: React.ReactNode;
}

interface DatabaseStats {
  total_opportunities: number;
  active_opportunities: number;
  total_funding: number;
  unique_organizations: number;
  countries_covered: number;
  last_updated: string;
}

interface SearchFilters {
  query: string;
  min_amount: string;
  max_amount: string;
  deadline_after: string;
  deadline_before: string;
  status: string;
  funding_type: string;
  geographic_scope: string[];
  ai_domains: string[];
  organization_type: string;
  // Equity-aware filters
  underserved_focus: boolean;
  women_focus: boolean;
  youth_focus: boolean;
  rural_focus: boolean;
  inclusion_indicators: string[];
  bias_score_min: number;
  equity_score_min: number;
}

export default function DualModeSearch() {
  const [searchMode, setSearchMode] = useState<'discover' | 'explore'>('discover');
  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false);
  const [showEquityFilters, setShowEquityFilters] = useState(false);
  const [dbStats, setDbStats] = useState<DatabaseStats>({
    total_opportunities: 12847,
    active_opportunities: 8934,
    total_funding: 2400000000,
    unique_organizations: 1247,
    countries_covered: 54,
    last_updated: new Date().toISOString()
  });

  const [filters, setFilters] = useState<SearchFilters>({
    query: '',
    min_amount: '',
    max_amount: '',
    deadline_after: '',
    deadline_before: '',
    status: searchMode === 'discover' ? 'active' : '',
    funding_type: '',
    geographic_scope: [],
    ai_domains: [],
    organization_type: '',
    underserved_focus: false,
    women_focus: false,
    youth_focus: false,
    rural_focus: false,
    inclusion_indicators: [],
    bias_score_min: 0,
    equity_score_min: 0
  });

  const searchModes: SearchMode[] = [
    {
      mode: 'discover',
      label: 'Discover Mode',
      description: 'Active opportunities with upcoming deadlines',
      icon: <Clock className="w-5 h-5" />
    },
    {
      mode: 'explore',
      label: 'Explore Mode',
      description: 'All historical and current records',
      icon: <Database className="w-5 h-5" />
    }
  ];

  const fundingTypes = [
    { value: 'grant', label: 'Grants' },
    { value: 'investment', label: 'Investment' },
    { value: 'prize', label: 'Prizes & Competitions' },
    { value: 'fellowship', label: 'Fellowships' },
    { value: 'accelerator', label: 'Accelerators' },
    { value: 'other', label: 'Other' }
  ];

  const aiDomains = [
    'Healthcare', 'Agriculture', 'Education', 'Financial Services', 
    'Climate & Energy', 'Infrastructure', 'General AI', 'Research'
  ];

  const geographicScopes = [
    'East Africa', 'West Africa', 'Southern Africa', 'Central Africa', 
    'North Africa', 'Continental', 'Global'
  ];

  const inclusionIndicators = [
    'Women-led', 'Youth-focused', 'Rural communities', 'Underserved regions',
    'Disability inclusion', 'LGBTQ+ inclusive', 'Indigenous communities'
  ];

  const organizationTypes = [
    'Government', 'UN/International', 'Private Foundation', 'Corporate',
    'Academic', 'Non-profit', 'Venture Capital', 'Development Bank'
  ];

  useEffect(() => {
    // Update status filter when mode changes
    if (searchMode === 'discover') {
      setFilters(prev => ({ ...prev, status: 'active' }));
    } else {
      setFilters(prev => ({ ...prev, status: '' }));
    }
  }, [searchMode]);

  const handleModeToggle = () => {
    setSearchMode(prev => prev === 'discover' ? 'explore' : 'discover');
  };

  const handleFilterChange = (key: keyof SearchFilters, value: any) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const handleArrayFilterChange = (key: keyof SearchFilters, value: string, checked: boolean) => {
    setFilters(prev => ({
      ...prev,
      [key]: checked 
        ? [...(prev[key] as string[]), value]
        : (prev[key] as string[]).filter(item => item !== value)
    }));
  };

  const handleClearFilters = () => {
    setFilters({
      query: '',
      min_amount: '',
      max_amount: '',
      deadline_after: '',
      deadline_before: '',
      status: searchMode === 'discover' ? 'active' : '',
      funding_type: '',
      geographic_scope: [],
      ai_domains: [],
      organization_type: '',
      underserved_focus: false,
      women_focus: false,
      youth_focus: false,
      rural_focus: false,
      inclusion_indicators: [],
      bias_score_min: 0,
      equity_score_min: 0
    });
  };

  const formatNumber = (num: number) => {
    if (num >= 1e9) return `${(num / 1e9).toFixed(1)}B`;
    if (num >= 1e6) return `${(num / 1e6).toFixed(1)}M`;
    if (num >= 1e3) return `${(num / 1e3).toFixed(1)}K`;
    return num.toString();
  };

  const currentStats = searchMode === 'discover' 
    ? dbStats.active_opportunities 
    : dbStats.total_opportunities;

  return (
    <div className="bg-white rounded-xl shadow-lg border border-gray-200">
      {/* Header with Mode Toggle */}
      <div className="border-b border-gray-200 p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">AI Funding Search</h2>
            <p className="text-gray-600 mt-1">
              {searchMode === 'discover' 
                ? 'Find active opportunities with upcoming deadlines' 
                : 'Explore all historical and current funding data'}
            </p>
          </div>
          
          {/* Database Counter */}
          <div className="flex items-center space-x-4">
            <div className="text-right">
              <div className="text-2xl font-bold text-blue-600">
                {formatNumber(currentStats)}
              </div>
              <div className="text-sm text-gray-500">
                {searchMode === 'discover' ? 'Active' : 'Total'} Records
              </div>
            </div>
            <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
          </div>
        </div>

        {/* Mode Toggle */}
        <div className="flex items-center justify-center space-x-4 mb-6">
          <div className="flex items-center bg-gray-100 rounded-lg p-1">
            {searchModes.map((mode) => (
              <button
                key={mode.mode}
                onClick={() => setSearchMode(mode.mode)}
                className={`flex items-center space-x-2 px-4 py-2 rounded-md transition-colors ${
                  searchMode === mode.mode
                    ? 'bg-white text-blue-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-800'
                }`}
              >
                {mode.icon}
                <span className="font-medium">{mode.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-blue-50 rounded-lg p-3">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-lg font-bold text-blue-600">
                  {formatNumber(dbStats.total_opportunities)}
                </div>
                <div className="text-xs text-blue-800">Total Records</div>
              </div>
              <Database className="w-5 h-5 text-blue-500" />
            </div>
          </div>
          
          <div className="bg-green-50 rounded-lg p-3">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-lg font-bold text-green-600">
                  {formatNumber(dbStats.active_opportunities)}
                </div>
                <div className="text-xs text-green-800">Active Now</div>
              </div>
              <Clock className="w-5 h-5 text-green-500" />
            </div>
          </div>
          
          <div className="bg-purple-50 rounded-lg p-3">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-lg font-bold text-purple-600">
                  ${formatNumber(dbStats.total_funding)}
                </div>
                <div className="text-xs text-purple-800">Total Funding</div>
              </div>
              <TrendingUp className="w-5 h-5 text-purple-500" />
            </div>
          </div>
          
          <div className="bg-orange-50 rounded-lg p-3">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-lg font-bold text-orange-600">
                  {dbStats.countries_covered}
                </div>
                <div className="text-xs text-orange-800">Countries</div>
              </div>
              <Globe className="w-5 h-5 text-orange-500" />
            </div>
          </div>
        </div>

        {/* Main Search Bar */}
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Search className="h-5 w-5 text-gray-400" />
          </div>
          <input
            type="text"
            value={filters.query}
            onChange={(e) => handleFilterChange('query', e.target.value)}
            placeholder={searchMode === 'discover' 
              ? "Search active opportunities..." 
              : "Search all funding records..."}
            className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg"
          />
        </div>

        {/* Filter Toggles */}
        <div className="flex items-center justify-between mt-4">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => setShowAdvancedFilters(!showAdvancedFilters)}
              className="flex items-center space-x-2 px-3 py-2 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
            >
              <Filter className="w-4 h-4" />
              <span>Advanced Filters</span>
            </button>
            
            <button
              onClick={() => setShowEquityFilters(!showEquityFilters)}
              className="flex items-center space-x-2 px-3 py-2 bg-blue-100 rounded-lg hover:bg-blue-200 transition-colors"
            >
              <Users className="w-4 h-4" />
              <span>Equity Filters</span>
            </button>
          </div>
          
          <button
            onClick={handleClearFilters}
            className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
          >
            Clear All
          </button>
        </div>
      </div>

      {/* Advanced Filters */}
      {showAdvancedFilters && (
        <div className="border-b border-gray-200 p-6 bg-gray-50">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Advanced Filters</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {/* Funding Amount Range */}
            <div className="col-span-1">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Funding Amount (USD)
              </label>
              <div className="grid grid-cols-2 gap-2">
                <input
                  type="number"
                  value={filters.min_amount}
                  onChange={(e) => handleFilterChange('min_amount', e.target.value)}
                  placeholder="Min"
                  className="px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <input
                  type="number"
                  value={filters.max_amount}
                  onChange={(e) => handleFilterChange('max_amount', e.target.value)}
                  placeholder="Max"
                  className="px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>

            {/* Deadline Range */}
            <div className="col-span-1">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Deadline Range
              </label>
              <div className="grid grid-cols-2 gap-2">
                <input
                  type="date"
                  value={filters.deadline_after}
                  onChange={(e) => handleFilterChange('deadline_after', e.target.value)}
                  className="px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <input
                  type="date"
                  value={filters.deadline_before}
                  onChange={(e) => handleFilterChange('deadline_before', e.target.value)}
                  className="px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>

            {/* Funding Type */}
            <div className="col-span-1">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Funding Type
              </label>
              <select
                value={filters.funding_type}
                onChange={(e) => handleFilterChange('funding_type', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">All Types</option>
                {fundingTypes.map(type => (
                  <option key={type.value} value={type.value}>{type.label}</option>
                ))}
              </select>
            </div>

            {/* Organization Type */}
            <div className="col-span-1">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Organization Type
              </label>
              <select
                value={filters.organization_type}
                onChange={(e) => handleFilterChange('organization_type', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">All Organizations</option>
                {organizationTypes.map(type => (
                  <option key={type} value={type}>{type}</option>
                ))}
              </select>
            </div>

            {/* Status (only for explore mode) */}
            {searchMode === 'explore' && (
              <div className="col-span-1">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Status
                </label>
                <select
                  value={filters.status}
                  onChange={(e) => handleFilterChange('status', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">All Status</option>
                  <option value="active">Active</option>
                  <option value="closed">Closed</option>
                  <option value="awarded">Awarded</option>
                  <option value="cancelled">Cancelled</option>
                </select>
              </div>
            )}
          </div>

          {/* Multi-select filters */}
          <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* AI Domains */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                AI Domains
              </label>
              <div className="grid grid-cols-2 gap-2 max-h-32 overflow-y-auto">
                {aiDomains.map(domain => (
                  <div key={domain} className="flex items-center">
                    <input
                      type="checkbox"
                      id={`domain-${domain}`}
                      checked={filters.ai_domains.includes(domain)}
                      onChange={(e) => handleArrayFilterChange('ai_domains', domain, e.target.checked)}
                      className="h-4 w-4 text-blue-600 rounded focus:ring-blue-500"
                    />
                    <label htmlFor={`domain-${domain}`} className="ml-2 text-sm text-gray-700">
                      {domain}
                    </label>
                  </div>
                ))}
              </div>
            </div>

            {/* Geographic Scope */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Geographic Scope
              </label>
              <div className="grid grid-cols-2 gap-2 max-h-32 overflow-y-auto">
                {geographicScopes.map(scope => (
                  <div key={scope} className="flex items-center">
                    <input
                      type="checkbox"
                      id={`scope-${scope}`}
                      checked={filters.geographic_scope.includes(scope)}
                      onChange={(e) => handleArrayFilterChange('geographic_scope', scope, e.target.checked)}
                      className="h-4 w-4 text-blue-600 rounded focus:ring-blue-500"
                    />
                    <label htmlFor={`scope-${scope}`} className="ml-2 text-sm text-gray-700">
                      {scope}
                    </label>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Equity Filters */}
      {showEquityFilters && (
        <div className="border-b border-gray-200 p-6 bg-blue-50">
          <div className="flex items-center space-x-2 mb-4">
            <Brain className="w-5 h-5 text-blue-600" />
            <h3 className="text-lg font-semibold text-gray-900">Equity-Aware Filters</h3>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Focus Areas */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Focus Areas
              </label>
              <div className="space-y-2">
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="underserved-focus"
                    checked={filters.underserved_focus}
                    onChange={(e) => handleFilterChange('underserved_focus', e.target.checked)}
                    className="h-4 w-4 text-blue-600 rounded focus:ring-blue-500"
                  />
                  <label htmlFor="underserved-focus" className="ml-2 text-sm text-gray-700">
                    🌍 Underserved Regions Focus
                  </label>
                </div>
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="women-focus"
                    checked={filters.women_focus}
                    onChange={(e) => handleFilterChange('women_focus', e.target.checked)}
                    className="h-4 w-4 text-blue-600 rounded focus:ring-blue-500"
                  />
                  <label htmlFor="women-focus" className="ml-2 text-sm text-gray-700">
                    👩‍💼 Women-Led Initiatives
                  </label>
                </div>
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="youth-focus"
                    checked={filters.youth_focus}
                    onChange={(e) => handleFilterChange('youth_focus', e.target.checked)}
                    className="h-4 w-4 text-blue-600 rounded focus:ring-blue-500"
                  />
                  <label htmlFor="youth-focus" className="ml-2 text-sm text-gray-700">
                    🎓 Youth-Focused Programs
                  </label>
                </div>
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="rural-focus"
                    checked={filters.rural_focus}
                    onChange={(e) => handleFilterChange('rural_focus', e.target.checked)}
                    className="h-4 w-4 text-blue-600 rounded focus:ring-blue-500"
                  />
                  <label htmlFor="rural-focus" className="ml-2 text-sm text-gray-700">
                    🏘️ Rural Communities
                  </label>
                </div>
              </div>
            </div>

            {/* Inclusion Indicators */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Inclusion Indicators
              </label>
              <div className="grid grid-cols-1 gap-2 max-h-32 overflow-y-auto">
                {inclusionIndicators.map(indicator => (
                  <div key={indicator} className="flex items-center">
                    <input
                      type="checkbox"
                      id={`inclusion-${indicator}`}
                      checked={filters.inclusion_indicators.includes(indicator)}
                      onChange={(e) => handleArrayFilterChange('inclusion_indicators', indicator, e.target.checked)}
                      className="h-4 w-4 text-blue-600 rounded focus:ring-blue-500"
                    />
                    <label htmlFor={`inclusion-${indicator}`} className="ml-2 text-sm text-gray-700">
                      {indicator}
                    </label>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Equity Scores */}
          <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Minimum Equity Score: {filters.equity_score_min}
              </label>
              <input
                type="range"
                min="0"
                max="100"
                value={filters.equity_score_min}
                onChange={(e) => handleFilterChange('equity_score_min', Number(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>0</span>
                <span>50</span>
                <span>100</span>
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Minimum Bias Score: {filters.bias_score_min}
              </label>
              <input
                type="range"
                min="0"
                max="100"
                value={filters.bias_score_min}
                onChange={(e) => handleFilterChange('bias_score_min', Number(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>0</span>
                <span>50</span>
                <span>100</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Search Actions */}
      <div className="p-6 bg-gray-50">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium transition-colors flex items-center space-x-2"
            >
              <Search className="w-4 h-4" />
              <span>Search {searchMode === 'discover' ? 'Active' : 'All'} Opportunities</span>
            </button>
            
            <button
              className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-2 rounded-lg font-medium transition-colors flex items-center space-x-2"
            >
              <Brain className="w-4 h-4" />
              <span>Semantic Search</span>
            </button>
          </div>
          
          <div className="text-sm text-gray-500">
            Last updated: {new Date(dbStats.last_updated).toLocaleString()}
          </div>
        </div>
      </div>
    </div>
  );
}