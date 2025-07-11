import React, { useState, useEffect } from 'react';
import { format } from 'date-fns';
import { useRouter, useSearchParams } from 'next/navigation';

interface FundingOpportunity {
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
}

interface Organization {
  id: number;
  name: string;
}

const categories = ['AI', 'Education', 'Health', 'Agriculture', 'Fintech', 'Other'];
const statuses = ['open', 'closed', 'awarded'];

export default function FundingPage() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const [opportunities, setOpportunities] = useState<FundingOpportunity[]>([]);
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

  useEffect(() => {
    const fetchInitialData = async () => {
      try {
        const [orgsRes, countriesRes] = await Promise.all([
          fetch('http://localhost:8000/api/v1/organizations/'),
          fetch('http://localhost:8000/api/v1/organizations/countries'),
        ]);

        if (!orgsRes.ok) throw new Error(`HTTP error! status: ${orgsRes.status} for organizations`);
        if (!countriesRes.ok) throw new Error(`HTTP error! status: ${countriesRes.status} for countries`);

        const orgsData = await orgsRes.json();
        const countriesData = await countriesRes.json();

        setOrganizations(orgsData);
        setCountries(countriesData);
      } catch (err: any) {
        console.error("Failed to fetch initial data:", err);
        setError("Failed to load initial data (organizations, countries).");
      }
    };
    fetchInitialData();
  }, []);

  useEffect(() => {
    const fetchFundingOpportunities = async () => {
      setLoading(true);
      setError(null);

      const params = new URLSearchParams();
      if (keyword) params.append('keyword', keyword);
      if (minAmount) params.append('min_amount_usd', minAmount);
      if (maxAmount) params.append('max_amount_usd', maxAmount);
      if (startDate) params.append('start_deadline', startDate);
      if (endDate) params.append('end_deadline', endDate);
      if (selectedStatus) params.append('status', selectedStatus);
      if (selectedCategories.length > 0) params.append('category', selectedCategories.join(','));
      if (selectedOrganization) params.append('organization_id', selectedOrganization);
      if (selectedCountry) params.append('country', selectedCountry);

      params.append('skip', String((currentPage - 1) * itemsPerPage));
      params.append('limit', String(itemsPerPage));

      const queryString = params.toString();
      router.push(`/funding?${queryString}`, { shallow: true });

      try {
        const res = await fetch(`http://localhost:8000/api/v1/rfps/?${queryString}`);
        if (!res.ok) {
          throw new Error(`HTTP error! status: ${res.status}`);
        }
        const data = await res.json();
        setOpportunities(data.rfps); // Access rfps array
        setTotalCount(data.total_count); // Access total_count
      } catch (err: any) {
        console.error("Failed to fetch funding opportunities:", err);
        setError("Failed to load funding opportunities.");
      } finally {
        setLoading(false);
      }
    };

    fetchFundingOpportunities();
  }, [keyword, minAmount, maxAmount, startDate, endDate, selectedStatus, selectedCategories, selectedOrganization, selectedCountry, currentPage, itemsPerPage, router]);

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
    setCurrentPage(1);
    setItemsPerPage(10);
    router.push('/funding', { shallow: true });
  };

  const totalPages = Math.ceil(totalCount / itemsPerPage);

  return (
    <div className="container mx-auto p-4 py-8">
      <h1 className="text-3xl font-extrabold text-gray-900 mb-8 text-center">Funding Opportunities</h1>

      {/* Filter Section */}
      <div className="card p-6 mb-8">
        <h2 className="text-xl font-bold mb-4">Filter Opportunities</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div>
            <label htmlFor="keyword" className="block text-sm font-medium text-gray-700">Keyword</label>
            <input
              type="text"
              id="keyword"
              value={keyword}
              onChange={(e) => setKeyword(e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring focus:ring-primary focus:ring-opacity-50"
              placeholder="Search title or description"
            />
          </div>
          <div>
            <label htmlFor="minAmount" className="block text-sm font-medium text-gray-700">Min Amount (USD)</label>
            <input
              type="number"
              id="minAmount"
              value={minAmount}
              onChange={(e) => setMinAmount(e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring focus:ring-primary focus:ring-opacity-50"
              placeholder="e.g., 10000"
            />
          </div>
          <div>
            <label htmlFor="maxAmount" className="block text-sm font-medium text-gray-700">Max Amount (USD)</label>
            <input
              type="number"
              id="maxAmount"
              value={maxAmount}
              onChange={(e) => setMaxAmount(e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring focus:ring-primary focus:ring-opacity-50"
              placeholder="e.g., 50000"
            />
          </div>
          <div>
            <label htmlFor="startDate" className="block text-sm font-medium text-gray-700">Deadline After</label>
            <input
              type="date"
              id="startDate"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring focus:ring-primary focus:ring-opacity-50"
            />
          </div>
          <div>
            <label htmlFor="endDate" className="block text-sm font-medium text-gray-700">Deadline Before</label>
            <input
              type="date"
              id="endDate"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring focus:ring-primary focus:ring-opacity-50"
            />
          </div>
          <div>
            <label htmlFor="status" className="block text-sm font-medium text-gray-700">Status</label>
            <select
              id="status"
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring focus:ring-primary focus:ring-opacity-50"
            >
              <option value="">All</option>
              {statuses.map((s) => (
                <option key={s} value={s} className="capitalize">{s}</option>
              ))}
            </select>
          </div>
          <div>
            <label htmlFor="organization" className="block text-sm font-medium text-gray-700">Organization</label>
            <select
              id="organization"
              value={selectedOrganization}
              onChange={(e) => setSelectedOrganization(e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring focus:ring-primary focus:ring-opacity-50"
            >
              <option value="">All</option>
              {organizations.map((org) => (
                <option key={org.id} value={org.id}>{org.name}</option>
              ))}
            </select>
          </div>
          <div>
            <label htmlFor="country" className="block text-sm font-medium text-gray-700">Country</label>
            <select
              id="country"
              value={selectedCountry}
              onChange={(e) => setSelectedCountry(e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring focus:ring-primary focus:ring-opacity-50"
            >
              <option value="">All</option>
              {countries.map((c) => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>
        </div>
        <div className="mt-4">
          <label className="block text-sm font-medium text-gray-700">Categories</label>
          <div className="mt-1 grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-2">
            {categories.map((cat) => (
              <div key={cat} className="flex items-center">
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
                  className="h-4 w-4 text-primary border-gray-300 rounded focus:ring-primary"
                />
                <label htmlFor={`category-${cat}`} className="ml-2 text-sm text-gray-700">{cat}</label>
              </div>
            ))}
          </div>
        </div>
        <div className="mt-6 flex justify-end space-x-3">
          <button
            onClick={handleClearFilters}
            className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary"
          >
            Clear Filters
          </button>
        </div>
      </div>

      {/* Opportunities List */}
      {loading ? (
        <p className="text-center text-gray-600">Loading funding opportunities...</p>
      ) : error ? (
        <p className="text-center text-red-500">Error: {error}</p>
      ) : opportunities.length === 0 ? (
        <p className="text-center text-gray-600">No funding opportunities found matching your criteria.</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {opportunities.map((opportunity) => (
            <div key={opportunity.id} className="card flex flex-col justify-between">
              <div>
                <h2 className="text-xl font-bold text-gray-800 mb-2">{opportunity.title}</h2>
                <p className="text-gray-600 text-sm mb-4 line-clamp-4">{opportunity.description}</p>
              </div>
              <div className="space-y-2 text-sm">
                {opportunity.amount_usd && (
                  <p className="text-blue-600 font-semibold">Amount: {opportunity.amount_usd.toLocaleString()} {opportunity.currency}</p>
                )}
                <p className="text-red-600">Deadline: {format(new Date(opportunity.deadline), 'PPP')}</p>
                <p className="text-green-600">Status: <span className="capitalize">{opportunity.status}</span></p>
                {opportunity.organization_id && (
                  <p className="text-gray-500">
                    Organization: {organizations.find(org => org.id === opportunity.organization_id)?.name || 'N/A'}
                  </p>
                )}
                {opportunity.link && (
                  <a href={opportunity.link} target="_blank" rel="noopener noreferrer" className="text-primary hover:underline block mt-2">
                    View Details
                  </a>
                )}
              </div>
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
            className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Previous
          </button>
          <span className="text-gray-700">Page {currentPage} of {totalPages}</span>
          <button
            onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
            disabled={currentPage === totalPages}
            className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Next
          </button>
          <select
            value={itemsPerPage}
            onChange={(e) => {
              setItemsPerPage(Number(e.target.value));
              setCurrentPage(1); // Reset to first page when items per page changes
            }}
            className="ml-4 rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring focus:ring-primary focus:ring-opacity-50"
          >
            <option value={10}>10 per page</option>
            <option value={20}>20 per page</option>
            <option value={50}>50 per page</option>
          </select>
        </div>
      )}
    </div>
  );
}
