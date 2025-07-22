'use client';

import React, { useState, useEffect, Suspense } from 'react';
import { format } from 'date-fns';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { getApiUrl, API_ENDPOINTS } from '@/lib/api-config';
import { 
  DollarSign, 
  Clock, 
  BarChart3, 
  TrendingUp, 
  Gem, 
  Target, 
  Building2, 
  Handshake, 
  CreditCard 
} from 'lucide-react';

interface InvestmentOpportunity {
  id: number;
  title: string;
  description: string;
  amount_usd: number;
  currency: string;
  deadline: string;
  status: string;
  organization_id: number;
  link?: string;
  contact_email?: string;
  categories?: string;
  // Investment-specific fields
  equity_percentage?: number;
  valuation_cap?: number;
  interest_rate?: number;
  repayment_terms?: string;
  investor_rights?: string;
  post_investment_support?: string;
  expected_roi?: number;
}

interface Organization {
  id: number;
  name: string;
}

const investmentCategories = ['Seed', 'Series A', 'Series B', 'Growth', 'Fintech', 'HealthTech', 'EdTech', 'AgriTech'];
const statuses = ['open', 'closed', 'awarded'];
const fundingStages = ['Pre-seed', 'Seed', 'Series A', 'Series B', 'Series C', 'Growth', 'Bridge'];

function InvestmentContent() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const [opportunities, setOpportunities] = useState<InvestmentOpportunity[]>([]);
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [countries, setCountries] = useState<string[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [totalCount, setTotalCount] = useState<number>(0);
  const [currentPage, setCurrentPage] = useState<number>(Number(searchParams.get('page')) || 1);
  const [itemsPerPage, setItemsPerPage] = useState<number>(Number(searchParams.get('limit')) || 10);

  // Filter states
  const [keyword, setKeyword] = useState<string>(searchParams.get('keyword') || '');
  const [minAmount, setMinAmount] = useState<string>(searchParams.get('min_amount_usd') || '');
  const [maxAmount, setMaxAmount] = useState<string>(searchParams.get('max_amount_usd') || '');
  const [startDate, setStartDate] = useState<string>(searchParams.get('start_deadline') || '');
  const [endDate, setEndDate] = useState<string>(searchParams.get('end_deadline') || '');
  const [selectedStatus, setSelectedStatus] = useState<string>(searchParams.get('status') || '');
  const [selectedCategories, setSelectedCategories] = useState<string[]>(searchParams.get('category')?.split(',') || []);
  const [selectedOrganization, setSelectedOrganization] = useState<string>(searchParams.get('organization_id') || '');
  const [selectedCountry, setSelectedCountry] = useState<string>(searchParams.get('country') || '');
  const [maxEquity, setMaxEquity] = useState<string>(searchParams.get('max_equity') || '');
  const [selectedStage, setSelectedStage] = useState<string>(searchParams.get('stage') || '');

  useEffect(() => {
    const fetchInitialData = async () => {
      try {
        const [orgsRes, countriesRes] = await Promise.all([
          fetch(getApiUrl(API_ENDPOINTS.organizations)),
          fetch(getApiUrl(API_ENDPOINTS.organizationsCountries)),
        ]);

        if (!orgsRes.ok) throw new Error(`HTTP error! status: ${orgsRes.status} for organizations`);
        if (!countriesRes.ok) throw new Error(`HTTP error! status: ${countriesRes.status} for countries`);

        const orgsData = await orgsRes.json();
        const countriesData = await countriesRes.json();

        setOrganizations(orgsData);
        setCountries(countriesData);
      } catch (err: unknown) {
        console.error("Failed to fetch initial data:", err);
        setError("Failed to load initial data (organizations, countries).");
      }
    };
    fetchInitialData();
  }, []);

  useEffect(() => {
    const fetchInvestmentOpportunities = async () => {
      setLoading(true);
      setError(null);

      const params = new URLSearchParams();
      params.append('funding_type', 'investment'); // Filter for investments only
      if (keyword) params.append('keyword', keyword);
      if (minAmount) params.append('min_amount_usd', minAmount);
      if (maxAmount) params.append('max_amount_usd', maxAmount);
      if (startDate) params.append('start_deadline', startDate);
      if (endDate) params.append('end_deadline', endDate);
      if (selectedStatus) params.append('status', selectedStatus);
      if (selectedCategories.length > 0) params.append('category', selectedCategories.join(','));
      if (selectedOrganization) params.append('organization_id', selectedOrganization);
      if (selectedCountry) params.append('country', selectedCountry);
      if (maxEquity) params.append('max_equity', maxEquity);
      if (selectedStage) params.append('stage', selectedStage);

      params.append('skip', String((currentPage - 1) * itemsPerPage));
      params.append('limit', String(itemsPerPage));

      const queryString = params.toString();
      router.push(`/funding/investments?${queryString}`);

      try {
        const res = await fetch(`${getApiUrl(API_ENDPOINTS.fundingOpportunities)}?${queryString}`);
        if (!res.ok) {
          throw new Error(`HTTP error! status: ${res.status}`);
        }
        const data = await res.json();
        setOpportunities(data.opportunities || data);
        setTotalCount(data.total_count || data.length);
      } catch (err: unknown) {
        console.error("Failed to fetch investment opportunities:", err);
        setError("Failed to load investment opportunities.");
      } finally {
        setLoading(false);
      }
    };

    fetchInvestmentOpportunities();
  }, [keyword, minAmount, maxAmount, startDate, endDate, selectedStatus, selectedCategories, selectedOrganization, selectedCountry, maxEquity, selectedStage, currentPage, itemsPerPage, router]);

  const handleClearFilters = () => {
    setKeyword('');
    setMinAmount('');
    setMaxAmount('');
    setStartDate('');
    setEndDate('');
    setSelectedStatus('');
    setSelectedCategories([]);
    setSelectedOrganization('');
    setSelectedCountry('');
    setMaxEquity('');
    setSelectedStage('');
    setCurrentPage(1);
    setItemsPerPage(10);
    router.push('/funding/investments');
  };

  const totalPages = Math.ceil(totalCount / itemsPerPage);

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900">
      <div className="container mx-auto p-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <Link href="/" className="text-green-600 hover:text-green-700 mb-4 inline-block font-medium">
            ← Back to Pathway Selection
          </Link>
          <h1 className="text-4xl font-extrabold text-gray-900 mb-4">Investment Opportunities</h1>
          <p className="text-gray-600 text-lg">
            Find venture capital, angel investors, and accelerator programs for your startup
          </p>
        </div>

        {/* Filter Section */}
        <div className="bg-white border border-gray-200 rounded-xl p-6 mb-8 shadow-sm">
          <h2 className="text-2xl font-bold mb-6 text-gray-900">Filter Investment Opportunities</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div>
              <label htmlFor="keyword" className="block text-sm font-medium text-gray-700 mb-2">Keyword</label>
              <input
                type="text"
                id="keyword"
                value={keyword}
                onChange={(e) => setKeyword(e.target.value)}
                className="w-full rounded-md bg-white border border-gray-300 text-gray-900 placeholder-gray-500 focus:border-green-500 focus:ring-2 focus:ring-green-500 focus:ring-opacity-50"
                placeholder="Search title or description"
              />
            </div>
            <div>
              <label htmlFor="minAmount" className="block text-sm font-medium text-gray-700 mb-2">Min Investment (USD)</label>
              <input
                type="number"
                id="minAmount"
                value={minAmount}
                onChange={(e) => setMinAmount(e.target.value)}
                className="w-full rounded-md bg-white border border-gray-300 text-gray-900 placeholder-gray-500 focus:border-green-500 focus:ring-2 focus:ring-green-500 focus:ring-opacity-50"
                placeholder="e.g., 50000"
              />
            </div>
            <div>
              <label htmlFor="maxAmount" className="block text-sm font-medium text-gray-700 mb-2">Max Investment (USD)</label>
              <input
                type="number"
                id="maxAmount"
                value={maxAmount}
                onChange={(e) => setMaxAmount(e.target.value)}
                className="w-full rounded-md bg-white border border-gray-300 text-gray-900 placeholder-gray-500 focus:border-green-500 focus:ring-2 focus:ring-green-500 focus:ring-opacity-50"
                placeholder="e.g., 1000000"
              />
            </div>
            <div>
              <label htmlFor="maxEquity" className="block text-sm font-medium text-gray-700 mb-2">Max Equity (%)</label>
              <input
                type="number"
                id="maxEquity"
                value={maxEquity}
                onChange={(e) => setMaxEquity(e.target.value)}
                className="w-full rounded-md bg-white border border-gray-300 text-gray-900 placeholder-gray-500 focus:border-green-500 focus:ring-2 focus:ring-green-500 focus:ring-opacity-50"
                placeholder="e.g., 20"
                min="0"
                max="100"
              />
            </div>
            <div>
              <label htmlFor="stage" className="block text-sm font-medium text-gray-700 mb-2">Funding Stage</label>
              <select
                id="stage"
                value={selectedStage}
                onChange={(e) => setSelectedStage(e.target.value)}
                className="w-full rounded-md bg-white border border-gray-300 text-gray-900 focus:border-green-500 focus:ring-2 focus:ring-green-500 focus:ring-opacity-50"
              >
                <option value="">All Stages</option>
                {fundingStages.map((stage) => (
                  <option key={stage} value={stage}>{stage}</option>
                ))}
              </select>
            </div>
            <div>
              <label htmlFor="startDate" className="block text-sm font-medium text-gray-700 mb-2">Deadline After</label>
              <input
                type="date"
                id="startDate"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="w-full rounded-md bg-white border border-gray-300 text-gray-900 focus:border-green-500 focus:ring-2 focus:ring-green-500 focus:ring-opacity-50"
              />
            </div>
            <div>
              <label htmlFor="endDate" className="block text-sm font-medium text-gray-700 mb-2">Deadline Before</label>
              <input
                type="date"
                id="endDate"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="w-full rounded-md bg-white border border-gray-300 text-gray-900 focus:border-green-500 focus:ring-2 focus:ring-green-500 focus:ring-opacity-50"
              />
            </div>
            <div>
              <label htmlFor="status" className="block text-sm font-medium text-gray-700 mb-2">Status</label>
              <select
                id="status"
                value={selectedStatus}
                onChange={(e) => setSelectedStatus(e.target.value)}
                className="w-full rounded-md bg-white border border-gray-300 text-gray-900 focus:border-green-500 focus:ring-2 focus:ring-green-500 focus:ring-opacity-50"
              >
                <option value="">All</option>
                {statuses.map((s) => (
                  <option key={s} value={s} className="capitalize">{s}</option>
                ))}
              </select>
            </div>
            <div>
              <label htmlFor="organization" className="block text-sm font-medium text-gray-700 mb-2">Investor/Organization</label>
              <select
                id="organization"
                value={selectedOrganization}
                onChange={(e) => setSelectedOrganization(e.target.value)}
                className="w-full rounded-md bg-white border border-gray-300 text-gray-900 focus:border-green-500 focus:ring-2 focus:ring-green-500 focus:ring-opacity-50"
              >
                <option value="">All</option>
                {organizations.map((org) => (
                  <option key={org.id} value={org.id}>{org.name}</option>
                ))}
              </select>
            </div>
            <div>
              <label htmlFor="country" className="block text-sm font-medium text-gray-700 mb-2">Country</label>
              <select
                id="country"
                value={selectedCountry}
                onChange={(e) => setSelectedCountry(e.target.value)}
                className="w-full rounded-md bg-white border border-gray-300 text-gray-900 focus:border-green-500 focus:ring-2 focus:ring-green-500 focus:ring-opacity-50"
              >
                <option value="">All</option>
                {countries.map((c) => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="mt-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">Investment Categories</label>
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-2">
              {investmentCategories.map((cat) => (
                <div key={cat} className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id={`category-${cat}`}
                    value={cat}
                    checked={selectedCategories.includes(cat)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setSelectedCategories([...selectedCategories, cat]);
                      } else {
                        setSelectedCategories(selectedCategories.filter((c) => c !== cat));
                      }
                    }}
                    className="h-4 w-4 text-green-600 bg-white border-gray-300 rounded focus:ring-green-500"
                  />
                  <label htmlFor={`category-${cat}`} className="text-sm text-gray-700">{cat}</label>
                </div>
              ))}
            </div>
          </div>
          
          <div className="mt-6 flex justify-end">
            <button
              onClick={handleClearFilters}
              className="px-6 py-2 bg-white border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-opacity-50"
            >
              Clear Filters
            </button>
          </div>
        </div>

        {/* Opportunities List */}
        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-green-600"></div>
            <p className="text-gray-600 mt-4">Loading investment opportunities...</p>
          </div>
        ) : error ? (
          <div className="text-center py-12">
            <p className="text-red-600">Error: {error}</p>
          </div>
        ) : opportunities.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-500">No investment opportunities found matching your criteria.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {opportunities.map((opportunity) => (
              <div key={opportunity.id} className="bg-white border border-gray-200 rounded-xl p-6 hover:border-green-400 hover:shadow-md transition-all duration-200">
                <div className="mb-4">
                  <h3 className="text-xl font-bold text-gray-900 mb-2">{opportunity.title}</h3>
                  <p className="text-gray-600 text-sm mb-4 line-clamp-3">{opportunity.description}</p>
                </div>
                
                <div className="space-y-3 text-sm">
                  {opportunity.amount_usd && (
                    <p className="text-green-600 font-semibold">
                      <DollarSign className="w-4 h-4 inline mr-1" />
                      Investment: ${opportunity.amount_usd.toLocaleString()} {opportunity.currency}
                    </p>
                  )}
                  <p className="text-orange-600">
                    <Clock className="w-4 h-4 inline mr-1" />
                    Deadline: {format(new Date(opportunity.deadline), 'PPP')}
                  </p>
                  <p className="text-emerald-600">
                    <BarChart3 className="w-4 h-4 inline mr-1" />
                    Status: <span className="capitalize">{opportunity.status}</span>
                  </p>
                  
                  {/* Investment-specific information */}
                  {opportunity.equity_percentage && (
                    <p className="text-red-600">
                      <TrendingUp className="w-4 h-4 inline mr-1" />
                      Equity: {opportunity.equity_percentage}%
                    </p>
                  )}
                  {opportunity.valuation_cap && (
                    <p className="text-blue-600">
                      <Gem className="w-4 h-4 inline mr-1" />
                      Valuation Cap: ${opportunity.valuation_cap.toLocaleString()}
                    </p>
                  )}
                  {opportunity.expected_roi && (
                    <p className="text-purple-600">
                      <Target className="w-4 h-4 inline mr-1" />
                      Expected ROI: {opportunity.expected_roi}%
                    </p>
                  )}
                  {opportunity.interest_rate && (
                    <p className="text-indigo-600">
                      <BarChart3 className="w-4 h-4 inline mr-1" />
                      Interest Rate: {opportunity.interest_rate}%
                    </p>
                  )}
                  
                  {opportunity.organization_id && (
                    <p className="text-gray-600">
                      <Building2 className="w-4 h-4 inline mr-1" />
                      Investor: {organizations.find(org => org.id === opportunity.organization_id)?.name || 'N/A'}
                    </p>
                  )}
                  
                  {opportunity.post_investment_support && (
                    <p className="text-cyan-600 text-xs">
                      <Handshake className="w-4 h-4 inline mr-1" />
                      Support: {opportunity.post_investment_support}
                    </p>
                  )}
                  
                  {opportunity.repayment_terms && (
                    <p className="text-gray-500 text-xs">
                      <CreditCard className="w-4 h-4 inline mr-1" />
                      Terms: {opportunity.repayment_terms}
                    </p>
                  )}
                </div>
                
                {opportunity.link && (
                  <div className="mt-4 pt-4 border-t border-gray-200">
                    <a 
                      href={opportunity.link} 
                      target="_blank" 
                      rel="noopener noreferrer" 
                      className="inline-block bg-green-600 hover:bg-green-700 text-white font-medium py-2 px-4 rounded-md transition-colors duration-200"
                    >
                      View Investment Details →
                    </a>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {/* Pagination Controls */}
        {totalPages > 1 && (
          <div className="flex justify-center items-center space-x-4 mt-8">
            <button
              onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
              disabled={currentPage === 1}
              className="px-4 py-2 bg-white border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>
            <span className="text-gray-700">Page {currentPage} of {totalPages}</span>
            <button
              onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
              disabled={currentPage === totalPages}
              className="px-4 py-2 bg-white border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
            <select
              value={itemsPerPage}
              onChange={(e) => {
                setItemsPerPage(Number(e.target.value));
                setCurrentPage(1);
              }}
              className="ml-4 rounded-md bg-white border border-gray-300 text-gray-900 focus:border-green-500 focus:ring-2 focus:ring-green-500 focus:ring-opacity-50"
            >
              <option value={10}>10 per page</option>
              <option value={20}>20 per page</option>
              <option value={50}>50 per page</option>
            </select>
          </div>
        )}
      </div>
    </div>
  );
}

export default function InvestmentsPage() {
  return (
    <Suspense fallback={<div className="flex justify-center items-center h-64">
      <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-green-500"></div>
    </div>}>
      <InvestmentContent />
    </Suspense>
  );
}
