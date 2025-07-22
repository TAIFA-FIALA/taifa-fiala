'use client';

import React, { useState, useEffect, Suspense } from 'react';
import { format } from 'date-fns';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { getApiUrl, API_ENDPOINTS } from '@/lib/api-config';
import { 
  DollarSign, 
  Clock, 
  ClipboardList, 
  Calendar, 
  RotateCcw, 
  Target, 
  Sparkles, 
  Building2, 
  BarChart3 
} from 'lucide-react';

interface GrantOpportunity {
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
  // Grant-specific fields
  reporting_requirements?: string;
  grant_duration_months?: number;
  renewable?: boolean;
  no_strings_attached?: boolean;
  project_based?: boolean;
}

interface Organization {
  id: number;
  name: string;
}

const grantCategories = ['Research', 'Education', 'Health', 'Agriculture', 'Technology', 'Social Impact'];
const statuses = ['open', 'closed', 'awarded'];

function GrantContent() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const [opportunities, setOpportunities] = useState<GrantOpportunity[]>([]);
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
  const [renewableOnly, setRenewableOnly] = useState<boolean>(searchParams.get('renewable') === 'true');
  const [projectBasedOnly, setProjectBasedOnly] = useState<boolean>(searchParams.get('project_based') === 'true');

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
    const fetchGrantOpportunities = async () => {
      setLoading(true);
      setError(null);

      const params = new URLSearchParams();
      params.append('funding_type', 'grant'); // Filter for grants only
      if (keyword) params.append('keyword', keyword);
      if (minAmount) params.append('min_amount_usd', minAmount);
      if (maxAmount) params.append('max_amount_usd', maxAmount);
      if (startDate) params.append('start_deadline', startDate);
      if (endDate) params.append('end_deadline', endDate);
      if (selectedStatus) params.append('status', selectedStatus);
      if (selectedCategories.length > 0) params.append('category', selectedCategories.join(','));
      if (selectedOrganization) params.append('organization_id', selectedOrganization);
      if (selectedCountry) params.append('country', selectedCountry);
      if (renewableOnly) params.append('renewable', 'true');
      if (projectBasedOnly) params.append('project_based', 'true');

      params.append('skip', String((currentPage - 1) * itemsPerPage));
      params.append('limit', String(itemsPerPage));

      const queryString = params.toString();
      router.push(`/funding/grants?${queryString}`);

      try {
        const res = await fetch(`${getApiUrl(API_ENDPOINTS.fundingOpportunities)}?${queryString}`);
        if (!res.ok) {
          throw new Error(`HTTP error! status: ${res.status}`);
        }
        const data = await res.json();
        setOpportunities(data.opportunities || data);
        setTotalCount(data.total_count || data.length);
      } catch (err: unknown) {
        console.error("Failed to fetch grant opportunities:", err);
        setError("Failed to load grant opportunities.");
      } finally {
        setLoading(false);
      }
    };

    fetchGrantOpportunities();
  }, [keyword, minAmount, maxAmount, startDate, endDate, selectedStatus, selectedCategories, selectedOrganization, selectedCountry, renewableOnly, projectBasedOnly, currentPage, itemsPerPage, router]);

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
    setRenewableOnly(false);
    setProjectBasedOnly(false);
    setCurrentPage(1);
    setItemsPerPage(10);
    router.push('/funding/grants');
  };

  const totalPages = Math.ceil(totalCount / itemsPerPage);

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      <div className="container mx-auto p-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <Link href="/" className="text-blue-400 hover:text-blue-300 mb-4 inline-block">
            ← Back to Pathway Selection
          </Link>
          <h1 className="text-4xl font-extrabold text-white mb-4">Grant Opportunities</h1>
          <p className="text-gray-300 text-lg">
            Discover funding opportunities for research, education, and social impact projects
          </p>
        </div>

        {/* Filter Section */}
        <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 mb-8">
          <h2 className="text-2xl font-bold mb-6 text-white">Filter Grant Opportunities</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div>
              <label htmlFor="keyword" className="block text-sm font-medium text-gray-300 mb-2">Keyword</label>
              <input
                type="text"
                id="keyword"
                value={keyword}
                onChange={(e) => setKeyword(e.target.value)}
                className="w-full rounded-md bg-slate-700 border border-slate-600 text-white placeholder-gray-400 focus:border-blue-400 focus:ring-2 focus:ring-blue-400 focus:ring-opacity-50"
                placeholder="Search title or description"
              />
            </div>
            <div>
              <label htmlFor="minAmount" className="block text-sm font-medium text-gray-300 mb-2">Min Amount (USD)</label>
              <input
                type="number"
                id="minAmount"
                value={minAmount}
                onChange={(e) => setMinAmount(e.target.value)}
                className="w-full rounded-md bg-slate-700 border border-slate-600 text-white placeholder-gray-400 focus:border-blue-400 focus:ring-2 focus:ring-blue-400 focus:ring-opacity-50"
                placeholder="e.g., 10000"
              />
            </div>
            <div>
              <label htmlFor="maxAmount" className="block text-sm font-medium text-gray-300 mb-2">Max Amount (USD)</label>
              <input
                type="number"
                id="maxAmount"
                value={maxAmount}
                onChange={(e) => setMaxAmount(e.target.value)}
                className="w-full rounded-md bg-slate-700 border border-slate-600 text-white placeholder-gray-400 focus:border-blue-400 focus:ring-2 focus:ring-blue-400 focus:ring-opacity-50"
                placeholder="e.g., 50000"
              />
            </div>
            <div>
              <label htmlFor="startDate" className="block text-sm font-medium text-gray-300 mb-2">Deadline After</label>
              <input
                type="date"
                id="startDate"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="w-full rounded-md bg-slate-700 border border-slate-600 text-white focus:border-blue-400 focus:ring-2 focus:ring-blue-400 focus:ring-opacity-50"
              />
            </div>
            <div>
              <label htmlFor="endDate" className="block text-sm font-medium text-gray-300 mb-2">Deadline Before</label>
              <input
                type="date"
                id="endDate"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="w-full rounded-md bg-slate-700 border border-slate-600 text-white focus:border-blue-400 focus:ring-2 focus:ring-blue-400 focus:ring-opacity-50"
              />
            </div>
            <div>
              <label htmlFor="status" className="block text-sm font-medium text-gray-300 mb-2">Status</label>
              <select
                id="status"
                value={selectedStatus}
                onChange={(e) => setSelectedStatus(e.target.value)}
                className="w-full rounded-md bg-slate-700 border border-slate-600 text-white focus:border-blue-400 focus:ring-2 focus:ring-blue-400 focus:ring-opacity-50"
              >
                <option value="">All</option>
                {statuses.map((s) => (
                  <option key={s} value={s} className="capitalize">{s}</option>
                ))}
              </select>
            </div>
            <div>
              <label htmlFor="organization" className="block text-sm font-medium text-gray-300 mb-2">Organization</label>
              <select
                id="organization"
                value={selectedOrganization}
                onChange={(e) => setSelectedOrganization(e.target.value)}
                className="w-full rounded-md bg-slate-700 border border-slate-600 text-white focus:border-blue-400 focus:ring-2 focus:ring-blue-400 focus:ring-opacity-50"
              >
                <option value="">All</option>
                {organizations.map((org) => (
                  <option key={org.id} value={org.id}>{org.name}</option>
                ))}
              </select>
            </div>
            <div>
              <label htmlFor="country" className="block text-sm font-medium text-gray-300 mb-2">Country</label>
              <select
                id="country"
                value={selectedCountry}
                onChange={(e) => setSelectedCountry(e.target.value)}
                className="w-full rounded-md bg-slate-700 border border-slate-600 text-white focus:border-blue-400 focus:ring-2 focus:ring-blue-400 focus:ring-opacity-50"
              >
                <option value="">All</option>
                {countries.map((c) => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </div>
          </div>
          
          {/* Grant-specific filters */}
          <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="flex items-center space-x-3">
              <input
                type="checkbox"
                id="renewable"
                checked={renewableOnly}
                onChange={(e) => setRenewableOnly(e.target.checked)}
                className="h-4 w-4 text-blue-400 bg-slate-700 border-slate-600 rounded focus:ring-blue-400"
              />
              <label htmlFor="renewable" className="text-sm text-gray-300">Renewable grants only</label>
            </div>
            <div className="flex items-center space-x-3">
              <input
                type="checkbox"
                id="projectBased"
                checked={projectBasedOnly}
                onChange={(e) => setProjectBasedOnly(e.target.checked)}
                className="h-4 w-4 text-blue-400 bg-slate-700 border-slate-600 rounded focus:ring-blue-400"
              />
              <label htmlFor="projectBased" className="text-sm text-gray-300">Project-based grants only</label>
            </div>
          </div>

          <div className="mt-4">
            <label className="block text-sm font-medium text-gray-300 mb-2">Categories</label>
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-2">
              {grantCategories.map((cat) => (
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
                    className="h-4 w-4 text-blue-400 bg-slate-700 border-slate-600 rounded focus:ring-blue-400"
                  />
                  <label htmlFor={`category-${cat}`} className="text-sm text-gray-300">{cat}</label>
                </div>
              ))}
            </div>
          </div>
          
          <div className="mt-6 flex justify-end">
            <button
              onClick={handleClearFilters}
              className="px-6 py-2 bg-slate-700 border border-slate-600 rounded-md text-white hover:bg-slate-600 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-opacity-50"
            >
              Clear Filters
            </button>
          </div>
        </div>

        {/* Opportunities List */}
        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-400"></div>
            <p className="text-gray-300 mt-4">Loading grant opportunities...</p>
          </div>
        ) : error ? (
          <div className="text-center py-12">
            <p className="text-red-400">Error: {error}</p>
          </div>
        ) : opportunities.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-400">No grant opportunities found matching your criteria.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {opportunities.map((opportunity) => (
              <div key={opportunity.id} className="bg-slate-800 border border-slate-700 rounded-xl p-6 hover:border-blue-400 transition-all duration-200">
                <div className="mb-4">
                  <h3 className="text-xl font-bold text-white mb-2">{opportunity.title}</h3>
                  <p className="text-gray-300 text-sm mb-4 line-clamp-3">{opportunity.description}</p>
                </div>
                
                <div className="space-y-3 text-sm">
                  {opportunity.amount_usd && (
                    <p className="text-blue-400 font-semibold">
                      <DollarSign className="w-4 h-4 inline mr-1" />
                      Grant Amount: ${opportunity.amount_usd.toLocaleString()} {opportunity.currency}
                    </p>
                  )}
                  <p className="text-yellow-400">
                    <Clock className="w-4 h-4 inline mr-1" />
                    Deadline: {format(new Date(opportunity.deadline), 'PPP')}
                  </p>
                  <p className="text-green-400">
                    <ClipboardList className="w-4 h-4 inline mr-1" />
                    Status: <span className="capitalize">{opportunity.status}</span>
                  </p>
                  
                  {/* Grant-specific information */}
                  {opportunity.grant_duration_months && (
                    <p className="text-purple-400">
                      <Calendar className="w-4 h-4 inline mr-1" />
                      Duration: {opportunity.grant_duration_months} months
                    </p>
                  )}
                  {opportunity.renewable && (
                    <p className="text-emerald-400">
                      <RotateCcw className="w-4 h-4 inline mr-1" />
                      Renewable grant
                    </p>
                  )}
                  {opportunity.project_based && (
                    <p className="text-cyan-400">
                      <Target className="w-4 h-4 inline mr-1" />
                      Project-based funding
                    </p>
                  )}
                  {opportunity.no_strings_attached && (
                    <p className="text-indigo-400">
                      <Sparkles className="w-4 h-4 inline mr-1" />
                      No strings attached
                    </p>
                  )}
                  
                  {opportunity.organization_id && (
                    <p className="text-gray-400">
                      <Building2 className="w-4 h-4 inline mr-1" />
                      Organization: {organizations.find(org => org.id === opportunity.organization_id)?.name || 'N/A'}
                    </p>
                  )}
                  
                  {opportunity.reporting_requirements && (
                    <p className="text-orange-400 text-xs">
                      <BarChart3 className="w-4 h-4 inline mr-1" />
                      Reporting: {opportunity.reporting_requirements}
                    </p>
                  )}
                </div>
                
                {opportunity.link && (
                  <div className="mt-4 pt-4 border-t border-slate-700">
                    <a 
                      href={opportunity.link} 
                      target="_blank" 
                      rel="noopener noreferrer" 
                      className="inline-block bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-md transition-colors duration-200"
                    >
                      View Grant Details →
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
              className="px-4 py-2 bg-slate-700 border border-slate-600 rounded-md text-white hover:bg-slate-600 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>
            <span className="text-gray-300">Page {currentPage} of {totalPages}</span>
            <button
              onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
              disabled={currentPage === totalPages}
              className="px-4 py-2 bg-slate-700 border border-slate-600 rounded-md text-white hover:bg-slate-600 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
            <select
              value={itemsPerPage}
              onChange={(e) => {
                setItemsPerPage(Number(e.target.value));
                setCurrentPage(1);
              }}
              className="ml-4 rounded-md bg-slate-700 border border-slate-600 text-white focus:border-blue-400 focus:ring-2 focus:ring-blue-400 focus:ring-opacity-50"
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

export default function GrantsPage() {
  return (
    <Suspense fallback={<div className="flex justify-center items-center h-64">
      <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500"></div>
    </div>}>
      <GrantContent />
    </Suspense>
  );
}
