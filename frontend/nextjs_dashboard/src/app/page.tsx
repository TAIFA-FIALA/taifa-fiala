import Link from 'next/link';
import EquityMetricsDashboard from '@/components/homepage/EquityMetricsDashboard';
import SemanticSearchShowcase from '@/components/homepage/SemanticSearchShowcase';
import DatabaseScopeVisualization from '@/components/homepage/DatabaseScopeVisualization';
import DatabaseGrowthChart from '@/components/homepage/DatabaseGrowthChart';
import { Globe, RefreshCw, Users2, Languages, Search, Building2, Target, Brain, MapPin, TrendingUp, Award } from 'lucide-react';
import Image from 'next/image';

interface AnalyticsSummary {
  total_opportunities?: number;
  active_opportunities?: number;
  total_funding_value?: number;
  unique_organizations?: number;
}

async function getAnalyticsSummary(): Promise<AnalyticsSummary | null> {
  try {
    const res = await fetch('http://localhost:8000/api/v1/equity-analyses/summary', { 
      cache: 'no-store',
      next: { revalidate: 300 } // Revalidate every 5 minutes
    });
    if (!res.ok) {
      throw new Error(`HTTP error! status: ${res.status}`);
    }
    return res.json();
  } catch (error) {
    console.error("Failed to fetch analytics summary:", error);
    // Return demo data if API is unavailable
    return {
      total_opportunities: 103,
      active_opportunities: 70,
      total_funding_value: 803200000,
      unique_organizations: 34
    };
  }
}

export default async function HomePage() {
  const summary = await getAnalyticsSummary();

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-[#1F2A44] via-[#1F2A44] to-[#4B9CD3] pt-4 pb-8 px-4 sm:px-6 lg:px-8 text-white relative overflow-hidden">
        <div className="max-w-7xl mx-auto text-center relative z-10">
          {/* Pan-African Map Background */}
          <div className="absolute inset-0 flex items-center justify-center opacity-10 pointer-events-none">
            <div className="relative w-96 h-96 md:w-[550px] md:h-[550px]">
              <Image
                src="/Africa-outline-grey.png"
                alt="Africa outline"
                fill
                className="object-contain"
                priority
              />
            </div>
          </div>
          
          {/* TAIFA-FIALA Branding */}
          <div className="mb-8 relative z-10">
            <h1 className="text-6xl sm:text-7xl lg:text-8xl font-extrabold leading-tight">
              <span className="text-[#F0E68C]">TAIFA</span>
              <span className="text-[#4b9cd3] mx-2">|</span>
              <span className="text-[#F0E68C]">FIALA</span>
            </h1>
            <div className="mt-2 mb-1">
              <p className="text-2xl text-white font-medium leading-tight">Comprehensive AI Intelligence Platform for Africa</p>
              <p className="text-xl text-[#4b9cd3] leading-tight">Plateforme d'Intelligence Artificielle Complète pour l'Afrique</p>
            </div>
          </div>

          {/* Mission Statement */}
          <div className="max-w-3xl mx-auto mb-6 relative">
            <div className="bg-navy bg-opacity-50 backdrop-blur-sm p-4 pt-8 pb-4 rounded-xl border border-[#4B9CD3] border-opacity-30 shadow-lg">
              <div className="absolute top-0 left-0 right-0 flex justify-center transform -translate-y-1/2">
                <div className="flex space-x-4 bg-gradient-to-r from-navy via-[#4B9CD3] to-navy p-2 px-4 rounded-full shadow-lg border border-[#F0E68C] border-opacity-20">
                  <div className="bg-[#F0E68C] bg-opacity-30 p-1.5 rounded-full">
                    <Globe className="h-4 w-4 text-[#F0E68C]" />
                  </div>
                  <div className="bg-[#F0E68C] bg-opacity-30 p-1.5 rounded-full">
                    <RefreshCw className="h-4 w-4 text-[#F0E68C]" />
                  </div>
                  <div className="bg-[#F0E68C] bg-opacity-30 p-1.5 rounded-full">
                    <Users2 className="h-4 w-4 text-[#F0E68C]" />
                  </div>
                  <div className="bg-[#F0E68C] bg-opacity-30 p-1.5 rounded-full">
                    <Languages className="h-4 w-4 text-[#F0E68C]" />
                  </div>
                </div>
              </div>
              
              <p className="text-base sm:text-lg text-white leading-snug text-center mb-4">
                Democratizing access to AI intelligence with comprehensive data collection, funding opportunities, policy insights, and market intelligence for the African AI ecosystem.
              </p>
              
              <div className="flex flex-wrap justify-center gap-x-6 gap-y-1">
                <span className="text-xs text-[#F0E68C] text-center font-medium">Pan-African Focus</span>
                <span className="text-xs text-[#F0E68C] text-center font-medium">Daily Updates</span>
                <span className="text-xs text-[#F0E68C] text-center font-medium">44+ Global Sources</span>
                <span className="text-xs text-[#F0E68C] text-center font-medium">Bilingual Platform</span>
              </div>
            </div>
          </div>

          {/* Quick Search Feature */}
          <div className="bg-white bg-opacity-20 backdrop-blur-sm rounded-lg shadow-lg p-4 mb-6 max-w-3xl mx-auto border border-white border-opacity-30">
            <form className="flex flex-col sm:flex-row gap-2" action="/funding" method="GET">
              <div className="flex-grow relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <svg className="h-5 w-5 text-gray-300" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clipRule="evenodd" />
                  </svg>
                </div>
                <input 
                  type="text" 
                  name="query" 
                  placeholder="Search AI funding, policy updates, market intelligence..." 
                  className="pl-10 w-full rounded-lg py-3 bg-white bg-opacity-90 border border-white border-opacity-50 focus:ring-2 focus:ring-accent focus:border-transparent text-gray-800"
                />
              </div>
              <button type="submit" className="bg-[#F0E68C] hover:bg-[#E6D768] text-[#1F2A44] font-bold py-3 px-6 rounded-lg transition-colors shadow-lg flex-shrink-0">
                Search Now
              </button>
            </form>
          </div>

          {/* Call to Action */}
          <div className="flex flex-col sm:flex-row justify-center space-y-4 sm:space-y-0 sm:space-x-6">
            <Link 
              href="/funding" 
              className="bg-[#F0E68C] hover:bg-[#E6D768] text-[#1F2A44] font-bold py-3 px-7 rounded-md text-base transition-colors shadow-md flex items-center gap-2"
            >
              <Search className="h-5 w-5" />
              Explore AI Intelligence
            </Link>
            <Link 
              href="/funders" 
              className="bg-transparent hover:bg-navy hover:bg-opacity-10 border border-navy text-navy font-bold py-3 px-7 rounded-md text-base transition-colors shadow-md flex items-center gap-2"
            >
              <Building2 className="h-5 w-5" />
              View Funder Profiles
            </Link>
          </div>
        </div>
      </section>

      {/* Interactive Analytics Dashboard */}
      {summary && (
        <section className="py-16 px-4 sm:px-6 lg:px-8 bg-white">
          <div className="max-w-7xl mx-auto">
            <div className="flex flex-col md:flex-row justify-between items-center mb-12">
              <h2 className="text-3xl font-bold text-gray-800 mb-4 md:mb-0">
                Live Intelligence Dashboard
              </h2>
              <div className="flex items-center space-x-2 text-[#4B9CD3]">
                <svg className="w-5 h-5 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                <span className="text-sm font-medium">Realtime intelligence from across Africa</span>
              </div>
            </div>
            
            {/* KPI Cards with Map Background */}
            <div className="relative">
              {/* Subtle Map of Africa in background */}
              <div className="absolute inset-0 opacity-5 pointer-events-none hidden md:block">
                <div className="w-full h-full flex items-center justify-center">
                  <div className="relative w-96 h-96">
                    <Image
                      src="/Africa-outline-grey.png"
                      alt="Africa outline background"
                      fill
                      className="object-contain"
                    />
                  </div>
                </div>
              </div>
              
              {/* KPI Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 relative z-10">
                {/* Total Opportunities */}
                <div className="bg-white rounded-xl shadow-lg overflow-hidden border border-gray-100 hover:shadow-xl transition-shadow duration-300">
                  <div className="p-5 relative">
                    <div className="absolute top-5 right-5 text-[#4B9CD3] opacity-20">
                      <svg className="w-12 h-12" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M3.5 2a.5.5 0 01.5.5v14a.5.5 0 01-1 0v-14a.5.5 0 01.5-.5zm4 0a.5.5 0 01.5.5v14a.5.5 0 01-1 0v-14a.5.5 0 01.5-.5zm4 0a.5.5 0 01.5.5v14a.5.5 0 01-1 0v-14a.5.5 0 01.5-.5zm4 0a.5.5 0 01.5.5v14a.5.5 0 01-1 0v-14a.5.5 0 01.5-.5z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <h3 className="text-sm font-medium text-gray-500">Total Intelligence Records</h3>
                    <div className="mt-2 flex items-baseline">
                      <div className="text-4xl font-extrabold text-gray-800">
                        {summary.total_opportunities?.toLocaleString() || '127'}
                      </div>
                      <div className="ml-2 text-sm font-medium text-green-500 flex items-center">
                        <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M12 7a1 1 0 10-2 0v5.586l-1.293-1.293a1 1 0 00-1.414 1.414l3 3a1 1 0 001.414 0l3-3a1 1 0 00-1.414-1.414L12 12.586V7z" clipRule="evenodd" />
                        </svg>
                        <span>+12%</span>
                      </div>
                    </div>
                    <div className="text-xs text-gray-500 mt-1">Funding, policy, market & tech intelligence</div>
                  </div>
                  <div className="bg-[#4B9CD3] bg-opacity-10 px-5 py-2">
                    <div className="text-xs text-[#4B9CD3] font-medium flex justify-between">
                      <span>View all</span>
                      <span>→</span>
                    </div>
                  </div>
                </div>

                {/* Active Opportunities */}
                <div className="bg-white rounded-xl shadow-lg overflow-hidden border border-gray-100 hover:shadow-xl transition-shadow duration-300">
                  <div className="p-5 relative">
                    <div className="absolute top-5 right-5 text-[#F0E68C] opacity-30">
                      <svg className="w-12 h-12" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M5 2a1 1 0 011 1v1h8V3a1 1 0 112 0v1h1a2 2 0 012 2v10a2 2 0 01-2 2H5a2 2 0 01-2-2V6a2 2 0 012-2h1V3a1 1 0 011-1zm11 14a1 1 0 001-1V6a1 1 0 00-1-1H5a1 1 0 00-1 1v10a1 1 0 001 1h11z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <h3 className="text-sm font-medium text-gray-500">Active Opportunities</h3>
                    <div className="mt-2 flex items-baseline">
                      <div className="text-4xl font-extrabold text-gray-800">
                        {summary.active_opportunities?.toLocaleString() || '89'}
                      </div>
                      <div className="ml-2 text-sm font-medium text-[#F0E68C] flex items-center">
                        <span>→</span>
                      </div>
                    </div>
                    <div className="text-xs text-gray-500 mt-1">Current open funding applications</div>
                  </div>
                  <div className="bg-[#F0E68C] bg-opacity-10 px-5 py-2">
                    <div className="text-xs text-[#F0E68C] font-medium flex justify-between">
                      <span>Closing soon</span>
                      <span>12</span>
                    </div>
                  </div>
                </div>

                {/* Total Funding Value */}
                <div className="bg-white rounded-xl shadow-lg overflow-hidden border border-gray-100 hover:shadow-xl transition-shadow duration-300">
                  <div className="p-5 relative">
                    <div className="absolute top-5 right-5 text-[#4B9CD3] opacity-20">
                      <svg className="w-12 h-12" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M8.433 7.418c.155-.103.346-.196.567-.267v1.698a2.305 2.305 0 01-.567-.267C8.07 8.34 8 8.114 8 8c0-.114.07-.34.433-.582zM11 12.849v-1.698c.22.071.412.164.567.267.364.243.433.468.433.582 0 .114-.07.34-.433.582a2.305 2.305 0 01-.567.267z" />
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-13a1 1 0 10-2 0v.092a4.535 4.535 0 00-1.676.662C6.602 6.234 6 7.009 6 8c0 .99.602 1.765 1.324 2.246.48.32 1.054.545 1.676.662v1.941c-.391-.127-.68-.317-.843-.504a1 1 0 10-1.51 1.31c.562.649 1.413 1.076 2.353 1.253V15a1 1 0 102 0v-.092a4.535 4.535 0 001.676-.662C13.398 13.766 14 12.991 14 12c0-.99-.602-1.765-1.324-2.246A4.535 4.535 0 0011 9.092V7.151c.391.127.68.317.843.504a1 1 0 101.511-1.31c-.563-.649-1.413-1.076-2.354-1.253V5z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <h3 className="text-sm font-medium text-gray-500">Total AI Funding Tracked</h3>
                    <div className="mt-2 flex items-baseline">
                      <div className="text-4xl font-extrabold text-gray-800">
                        ${((summary.total_funding_value || 803200000) / 1000000).toFixed(1)}M
                      </div>
                      <div className="ml-2 text-xs font-medium text-gray-500">
                        <span>USD</span>
                      </div>
                    </div>
                    <div className="text-xs text-gray-500 mt-1">Available for African AI initiatives (2019-2024)</div>
                  </div>
                  <div className="bg-[#4B9CD3] bg-opacity-10 px-5 py-2">
                    <div className="text-xs text-[#4B9CD3] font-medium flex justify-between">
                      <span>By funding type</span>
                      <span>→</span>
                    </div>
                  </div>
                </div>

                {/* Organizations */}
                <div className="bg-white rounded-xl shadow-lg overflow-hidden border border-gray-100 hover:shadow-xl transition-shadow duration-300">
                  <div className="p-5 relative">
                    <div className="absolute top-5 right-5 text-[#F0E68C] opacity-30">
                      <svg className="w-12 h-12" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z" />
                      </svg>
                    </div>
                    <h3 className="text-sm font-medium text-gray-500">Data Sources</h3>
                    <div className="mt-2 flex items-baseline">
                      <div className="text-4xl font-extrabold text-gray-800">
                        {summary.unique_organizations?.toLocaleString() || '159'}
                      </div>
                    </div>
                    <div className="text-xs text-gray-500 mt-1">RSS feeds, APIs, and intelligence sources</div>
                  </div>
                  <div className="bg-[#F0E68C] bg-opacity-10 px-5 py-2">
                    <div className="text-xs text-[#F0E68C] font-medium flex justify-between">
                      <span>View data sources</span>
                      <span>→</span>
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Database Growth Chart */}
              <div className="mt-12">
                <DatabaseGrowthChart className="" />
              </div>
              
              {/* Filters and Data Freshness */}
              <div className="mt-6 flex flex-col md:flex-row justify-between items-center text-sm">
                <div className="flex flex-wrap gap-2 mb-4 md:mb-0">
                  <Link href="/funding?type=grants" className="bg-[#4B9CD3] bg-opacity-10 text-[#4B9CD3] px-3 py-1 rounded-full hover:bg-[#4B9CD3] hover:bg-opacity-20 transition-colors">
                    Grants
                  </Link>
                  <Link href="/funding?type=accelerators" className="bg-[#4B9CD3] bg-opacity-10 text-[#4B9CD3] px-3 py-1 rounded-full hover:bg-[#4B9CD3] hover:bg-opacity-20 transition-colors">
                    Accelerators
                  </Link>
                  <Link href="/funding?type=fellowships" className="bg-[#4B9CD3] bg-opacity-10 text-[#4B9CD3] px-3 py-1 rounded-full hover:bg-[#4B9CD3] hover:bg-opacity-20 transition-colors">
                    Fellowships
                  </Link>
                  <Link href="/funding?type=competitions" className="bg-[#4B9CD3] bg-opacity-10 text-[#4B9CD3] px-3 py-1 rounded-full hover:bg-[#4B9CD3] hover:bg-opacity-20 transition-colors">
                    Competitions
                  </Link>
                </div>
                
                <div className="inline-flex items-center space-x-2 bg-green-50 text-green-700 px-4 py-2 rounded-full font-medium">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                  <span>Last update: Today at 06:00 UTC</span>
                </div>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* Equity Focus Features */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-[#4B9CD3] bg-opacity-5">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <div className="inline-block mb-4">
              <span className="inline-block px-4 py-1 text-sm font-semibold rounded-full bg-[#1F2A44] text-white">
                NEW FEATURES
              </span>
            </div>
            <h2 className="text-3xl font-bold text-gray-800 mb-4">Equity-Focused Analytics</h2>
            <p className="max-w-3xl mx-auto text-lg text-gray-600">
              Addressing funding disparities and promoting inclusive growth across the African AI ecosystem.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* Geographic Equity Card */}
            <Link href="/analytics/geographic-equity" className="group">
              <div className="bg-white p-6 rounded-xl shadow-md hover:shadow-lg transition-shadow duration-300 border border-gray-100 h-full flex flex-col">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center">
                    <div className="w-12 h-12 flex items-center justify-center rounded-full bg-[#4B9CD3] bg-opacity-20 text-[#4B9CD3] mr-4">
                      <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M12 1.586l-4 4v12.828l4-4V1.586zM3.707 3.293A1 1 0 002 4v10a1 1 0 00.293.707L6 18.414V5.586L3.707 3.293zM17.707 5.293L14 1.586v12.828l2.293 2.293A1 1 0 0018 16V6a1 1 0 00-.293-.707z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <h3 className="text-xl font-bold text-gray-800">Geographic Equity</h3>
                  </div>
                  <div className="text-[#4B9CD3] group-hover:translate-x-1 transition-transform duration-200">
                    <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10.293 5.293a1 1 0 011.414 0l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414-1.414L12.586 11H5a1 1 0 110-2h7.586l-2.293-2.293a1 1 0 010-1.414z" clipRule="evenodd" />
                    </svg>
                  </div>
                </div>
                <p className="text-gray-600 mb-4">
                  Interactive map highlighting funding distribution disparities across African countries. Five countries dominate 90% of African AI funding, with Tunisia and Kenya leading at over $240 million each, while Central Africa remains critically underserved.
                </p>
                <div className="mt-auto pt-4 border-t border-gray-100 flex justify-between items-center text-sm">
                  <span className="text-red-500 font-semibold">Central Africa critically underserved</span>
                  <span className="text-[#4B9CD3] font-semibold">View details →</span>
                </div>
              </div>
            </Link>
            
            {/* Sectoral Alignment Card */}
            <Link href="/analytics/sectoral-alignment" className="group">
              <div className="bg-white p-6 rounded-xl shadow-md hover:shadow-lg transition-shadow duration-300 border border-gray-100 h-full flex flex-col">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center">
                    <div className="w-12 h-12 flex items-center justify-center rounded-full bg-[#4B9CD3] bg-opacity-20 text-[#4B9CD3] mr-4">
                      <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M2 10a8 8 0 018-8v8h8a8 8 0 11-16 0z" />
                        <path d="M12 2.252A8.014 8.014 0 0117.748 8H12V2.252z" />
                      </svg>
                    </div>
                    <h3 className="text-xl font-bold text-gray-800">Sectoral Alignment</h3>
                  </div>
                  <div className="text-[#4B9CD3] group-hover:translate-x-1 transition-transform duration-200">
                    <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10.293 5.293a1 1 0 011.414 0l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414-1.414L12.586 11H5a1 1 0 110-2h7.586l-2.293-2.293a1 1 0 010-1.414z" clipRule="evenodd" />
                    </svg>
                  </div>
                </div>
                <p className="text-gray-600 mb-4">
                  Analysis of funding distribution across sectors and alignment with AU Agenda 2063 and UN SDGs priorities for maximum development impact.
                </p>
                <div className="mt-auto pt-4 border-t border-gray-100 flex justify-between items-center text-sm">
                  <span className="text-amber-500 font-semibold">3 critical funding gaps</span>
                  <span className="text-[#4B9CD3] font-semibold">View details →</span>
                </div>
              </div>
            </Link>
            
            {/* Gender & Inclusion Card */}
            <Link href="/analytics/gender-inclusion" className="group">
              <div className="bg-white p-6 rounded-xl shadow-md hover:shadow-lg transition-shadow duration-300 border border-gray-100 h-full flex flex-col">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center">
                    <div className="w-12 h-12 flex items-center justify-center rounded-full bg-[#F0E68C] bg-opacity-20 text-[#1F2A44] mr-4">
                      <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3zM6 8a2 2 0 11-4 0 2 2 0 014 0zM16 18v-3a5.972 5.972 0 00-.75-2.906A3.005 3.005 0 0119 15v3h-3zM4.75 12.094A5.973 5.973 0 004 15v3H1v-3a3 3 0 013.75-2.906z" />
                      </svg>
                    </div>
                    <h3 className="text-xl font-bold text-gray-800">Gender & Inclusion</h3>
                  </div>
                  <div className="text-[#1F2A44] group-hover:translate-x-1 transition-transform duration-200">
                    <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10.293 5.293a1 1 0 011.414 0l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414-1.414L12.586 11H5a1 1 0 110-2h7.586l-2.293-2.293a1 1 0 010-1.414z" clipRule="evenodd" />
                    </svg>
                  </div>
                </div>
                <p className="text-gray-600 mb-4">
                  Tracking the gender funding gap, with only 2% of funding going to female-led projects, and showcasing success stories from diverse founders.
                </p>
                <div className="mt-auto pt-4 border-t border-gray-100 flex justify-between items-center text-sm">
                  <span className="text-red-500 font-semibold">23% below global average</span>
                  <span className="text-[#1F2A44] font-semibold">View details →</span>
                </div>
              </div>
            </Link>
            
            {/* Funding Lifecycle Card */}
            <Link href="/analytics/funding-lifecycle" className="group">
              <div className="bg-white p-6 rounded-xl shadow-md hover:shadow-lg transition-shadow duration-300 border border-gray-100 h-full flex flex-col">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center">
                    <div className="w-12 h-12 flex items-center justify-center rounded-full bg-[#1F2A44] bg-opacity-20 text-[#1F2A44] mr-4">
                      <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <h3 className="text-xl font-bold text-gray-800">Funding Lifecycle</h3>
                  </div>
                  <div className="text-[#1F2A44] group-hover:translate-x-1 transition-transform duration-200">
                    <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10.293 5.293a1 1 0 011.414 0l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414-1.414L12.586 11H5a1 1 0 110-2h7.586l-2.293-2.293a1 1 0 010-1.414z" clipRule="evenodd" />
                    </svg>
                  </div>
                </div>
                <p className="text-gray-600 mb-4">
                  Breaking the 'seed trap' with 69% of projects stuck at seed stage, providing resources for follow-on funding and consortium building.
                </p>
                <div className="mt-auto pt-4 border-t border-gray-100 flex justify-between items-center text-sm">
                  <span className="text-amber-500 font-semibold">31% stage advancement rate</span>
                  <span className="text-[#1F2A44] font-semibold">View details →</span>
                </div>
              </div>
            </Link>
          </div>
          
          <div className="flex justify-center mt-10">
            <Link 
              href="/analytics" 
              className="bg-[#1F2A44] hover:bg-[#4B9CD3] border text-white font-bold py-3 px-8 rounded-lg text-base transition-colors shadow-md flex items-center gap-2"
            >
              <span>Explore All Analytics</span>
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
              </svg>
            </Link>
          </div>
        </div>
      </section>

      {/* Live Equity Analytics Dashboard */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-gray-50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <div className="inline-block mb-4">
              <span className="inline-block px-4 py-1 text-sm font-semibold rounded-full bg-[#4B9CD3] text-white flex items-center gap-2">
                <Target className="h-4 w-4" />
                Equity-Aware Intelligence
              </span>
            </div>
            <h2 className="text-3xl font-bold text-gray-800 mb-4">Live Equity Analytics</h2>
            <p className="max-w-3xl mx-auto text-lg text-gray-600">
              Real-time monitoring of funding equity across geographic, sectoral, and inclusion dimensions
            </p>
          </div>
          
          <EquityMetricsDashboard />
        </div>
      </section>

      {/* Semantic Search Intelligence */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-white">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <div className="inline-block mb-4">
              <span className="inline-block px-4 py-1 text-sm font-semibold rounded-full bg-[#1F2A44] text-white flex items-center gap-2">
                <Brain className="h-4 w-4" />
                Vector-Powered Search
              </span>
            </div>
            <h2 className="text-3xl font-bold text-gray-800 mb-4">Semantic Search Intelligence</h2>
            <p className="max-w-3xl mx-auto text-lg text-gray-600">
              Discover opportunities across languages and contexts with AI-powered semantic understanding
            </p>
          </div>
          
          <SemanticSearchShowcase />
        </div>
      </section>

      {/* Database Intelligence */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-gray-50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <div className="inline-block mb-4">
              <span className="inline-block px-4 py-1 text-sm font-semibold rounded-full bg-[#4B9CD3] text-white flex items-center gap-2">
                <MapPin className="h-4 w-4" />
                Continental Coverage
              </span>
            </div>
            <h2 className="text-3xl font-bold text-gray-800 mb-4">Database Intelligence</h2>
            <p className="max-w-3xl mx-auto text-lg text-gray-600">
              Comprehensive tracking of AI funding opportunities across all 54 African countries
            </p>
          </div>
          
          <DatabaseScopeVisualization />
        </div>
      </section>
      
      {/* Platform Differentiators */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-white">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <div className="inline-block mb-4">
              <span className="inline-block px-4 py-1 text-sm font-semibold rounded-full bg-[#1F2A44] text-white">
                TAIFA | FIALA Differentiators
              </span>
            </div>
            <h2 className="text-3xl font-bold text-gray-800 mb-4">Key Platform Features</h2>
            <p className="max-w-3xl mx-auto text-lg text-gray-600">
              Our platform is designed to address the specific needs of African researchers, entrepreneurs, and institutions seeking AI funding.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Pan-African Focus */}
            <div className="bg-white p-8 rounded-xl shadow-lg border-t-4 border-[#4B9CD3] hover:shadow-xl transition-shadow duration-300">
              <div className="w-16 h-16 flex items-center justify-center rounded-full bg-[#4B9CD3] bg-opacity-10 text-[#4B9CD3] mb-5 mx-auto">
                <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M3 6a3 3 0 013-3h10a1 1 0 01.8 1.6L14.25 8l2.55 3.4A1 1 0 0116 13H6a1 1 0 00-1 1v3a1 1 0 11-2 0V6z" clipRule="evenodd" />
                </svg>
              </div>
              <h3 className="text-xl font-bold text-gray-800 mb-3 text-center">Pan-African Focus</h3>
              <p className="text-gray-600 text-center">
                Our database is curated specifically for African initiatives, prioritizing opportunities that are relevant to the continent's AI ecosystem.
              </p>
              <div className="mt-5 flex justify-center">
                <div className="inline-flex space-x-1 items-center text-[#4B9CD3] font-medium text-sm">
                  <span>All 54 countries covered</span>
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
                  </svg>
                </div>
              </div>
            </div>
            
            {/* Bilingual Platform */}
            <div className="bg-white p-8 rounded-xl shadow-lg border-t-4 border-[#F0E68C] hover:shadow-xl transition-shadow duration-300">
              <div className="w-16 h-16 flex items-center justify-center rounded-full bg-yellow-50 text-[#F0E68C] mb-5 mx-auto">
                <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M2 5a2 2 0 012-2h7a2 2 0 012 2v4a2 2 0 01-2 2H9l-3 3v-3H4a2 2 0 01-2-2V5z" />
                  <path d="M15 7v2a4 4 0 01-4 4H9.828l-1.766 1.767c.28.149.599.233.938.233h2l3 3v-3h2a2 2 0 002-2V9a2 2 0 00-2-2h-1z" />
                </svg>
              </div>
              <h3 className="text-xl font-bold text-gray-800 mb-3 text-center">Bilingual Support</h3>
              <p className="text-gray-600 text-center">
                Full support for both English and French across all features, ensuring inclusivity for Francophone African communities.
              </p>
              <div className="mt-5 flex justify-center">
                <div className="inline-flex space-x-2 items-center">
                  <span className="rounded-full bg-[#4B9CD3] bg-opacity-10 text-[#4B9CD3] px-3 py-1 text-xs font-medium">English</span>
                  <span className="rounded-full bg-yellow-50 text-[#F0E68C] px-3 py-1 text-xs font-medium">Français</span>
                </div>
              </div>
            </div>
            
            {/* Rich Data */}
            <div className="bg-white p-8 rounded-xl shadow-lg border-t-4 border-[#4B9CD3] hover:shadow-xl transition-shadow duration-300">
              <div className="w-16 h-16 flex items-center justify-center rounded-full bg-[#4B9CD3] bg-opacity-10 text-[#4B9CD3] mb-5 mx-auto">
                <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M3 3a1 1 0 000 2v8a2 2 0 002 2h2.586l-1.293 1.293a1 1 0 101.414 1.414L10 15.414l2.293 2.293a1 1 0 001.414-1.414L12.414 15H15a2 2 0 002-2V5a1 1 0 100-2H3zm11 4a1 1 0 10-2 0v4a1 1 0 102 0V7zm-3 1a1 1 0 10-2 0v3a1 1 0 102 0V8zM8 9a1 1 0 00-2 0v2a1 1 0 102 0V9z" clipRule="evenodd" />
                </svg>
              </div>
              <h3 className="text-xl font-bold text-gray-800 mb-3 text-center">Rich Analytics</h3>
              <p className="text-gray-600 text-center">
                Detailed insights on funding trends, geographic distribution, and opportunity types to inform your funding strategy.
              </p>
              <div className="mt-5 flex justify-center">
                <div className="inline-flex space-x-1 items-center text-[#4B9CD3] font-medium text-sm">
                  <span>View detailed analytics</span>
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
                  </svg>
                </div>
              </div>
            </div>
          </div>
          
          {/* Second row of features */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-8">
            {/* Daily Updates */}
            <div className="bg-white p-8 rounded-xl shadow-lg border-t-4 border-[#F0E68C] hover:shadow-xl transition-shadow duration-300">
              <div className="w-16 h-16 flex items-center justify-center rounded-full bg-yellow-50 text-[#F0E68C] mb-5 mx-auto">
                <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
                </svg>
              </div>
              <h3 className="text-xl font-bold text-gray-800 mb-3 text-center">Daily Updates</h3>
              <p className="text-gray-600 text-center">
                Fresh opportunities added every day, with automated alerts for new funding sources that match your profile.
              </p>
              <div className="mt-5 flex justify-center">
                <span className="inline-flex items-center text-[#4B9CD3] text-sm font-medium">
                  <div className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></div>
                  <span>Last update: Today</span>
                </span>
              </div>
            </div>
            
            {/* Advanced Search */}
            <div className="bg-white p-8 rounded-xl shadow-lg border-t-4 border-[#4B9CD3] hover:shadow-xl transition-shadow duration-300">
              <div className="w-16 h-16 flex items-center justify-center rounded-full bg-[#4B9CD3] bg-opacity-10 text-[#4B9CD3] mb-5 mx-auto">
                <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clipRule="evenodd" />
                </svg>
              </div>
              <h3 className="text-xl font-bold text-gray-800 mb-3 text-center">Advanced Search</h3>
              <p className="text-gray-600 text-center">
                Powerful filters by funding type, amount, eligibility, deadlines, and geographic focus to find your perfect opportunity.
              </p>
              <div className="mt-5 flex justify-center">
                <Link href="/funding" className="text-[#4B9CD3] font-medium text-sm flex items-center space-x-1">
                  <span>Try advanced search</span>
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
                  </svg>
                </Link>
              </div>
            </div>
            
            {/* Funder Profiles */}
            <div className="bg-white p-8 rounded-xl shadow-lg border-t-4 border-[#F0E68C] hover:shadow-xl transition-shadow duration-300">
              <div className="w-16 h-16 flex items-center justify-center rounded-full bg-yellow-50 text-[#F0E68C] mb-5 mx-auto">
                <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3zM6 8a2 2 0 11-4 0 2 2 0 014 0zM16 18v-3a5.972 5.972 0 00-.75-2.906A3.005 3.005 0 0119 15v3h-3zM4.75 12.094A5.973 5.973 0 004 15v3H1v-3a3 3 0 013.75-2.906z" />
                </svg>
              </div>
              <h3 className="text-xl font-bold text-gray-800 mb-3 text-center">Funder Insights</h3>
              <p className="text-gray-600 text-center">
                Detailed profiles of major funding organizations, their priorities, past grants, and tips for successful applications.
              </p>
              <div className="mt-5 flex justify-center">
                <Link href="/funders" className="text-[#1F2A44] font-medium text-sm flex items-center space-x-1">
                  <span>Browse funder profiles</span>
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
                  </svg>
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Pan-African Impact Showcase */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-[#1F2A44] via-[#4B9CD3] to-[#F0E68C] text-white">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <span className="inline-block px-4 py-1 text-sm font-semibold rounded-full bg-white bg-opacity-20 text-white mb-4">
              Success Stories
            </span>
            <h2 className="text-3xl md:text-4xl font-bold mb-4">Supporting Africa's AI Ecosystem</h2>
            <p className="max-w-3xl mx-auto text-lg opacity-90">
              Over CAD$300 million committed to AI development in Africa, with major funding from IDRC, FCDO, and Gates Foundation (2019-2024).
            </p>
            <p className="max-w-3xl mx-auto text-lg opacity-90 mt-2">
              AI4D program expanding from $20M to $100M+, demonstrating increasing investment in African AI.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Case Study 1: Universities */}
            <div className="bg-white bg-opacity-10 backdrop-blur-sm rounded-xl p-8 hover:bg-opacity-15 transition-all duration-300 border border-white border-opacity-20">
              <div className="flex items-center justify-center w-16 h-16 bg-gold bg-opacity-20 rounded-full mb-6 mx-auto">
                <Award className="h-8 w-8 text-[#F0E68C]" />
              </div>
              <h3 className="text-xl font-bold mb-4 text-center">Research Institutions</h3>
              <p className="text-white text-opacity-90 text-center mb-6">
                Universities across Africa utilize our curated database to connect with global research grants and collaborative opportunities.
              </p>
              <div className="flex justify-center">
                <span className="text-sm inline-flex items-center bg-white bg-opacity-20 rounded-full px-4 py-2">
                  <span className="mr-2">10+ Universities</span>
                  <span className="w-2 h-2 rounded-full bg-green-400"></span>
                </span>
              </div>
            </div>
            
            {/* Case Study 2: Government */}
            <div className="bg-white bg-opacity-10 backdrop-blur-sm rounded-xl p-8 hover:bg-opacity-15 transition-all duration-300 border border-white border-opacity-20">
              <div className="flex items-center justify-center w-16 h-16 bg-gold bg-opacity-20 rounded-full mb-6 mx-auto">
                <Building2 className="h-8 w-8 text-[#F0E68C]" />
              </div>
              <h3 className="text-xl font-bold mb-4 text-center">Government Initiatives</h3>
              <p className="text-white text-opacity-90 text-center mb-6">
                Public sector AI projects and digital transformation initiatives find international development funding through our platform.
              </p>
              <div className="flex justify-center">
                <span className="text-sm inline-flex items-center bg-white bg-opacity-20 rounded-full px-4 py-2">
                  <span className="mr-2">6 Countries</span>
                  <span className="w-2 h-2 rounded-full bg-green-400"></span>
                </span>
              </div>
            </div>
            
            {/* Case Study 3: Startups */}
            <div className="bg-white bg-opacity-10 backdrop-blur-sm rounded-xl p-8 hover:bg-opacity-15 transition-all duration-300 border border-white border-opacity-20">
              <div className="flex items-center justify-center w-16 h-16 bg-gold bg-opacity-20 rounded-full mb-6 mx-auto">
                <TrendingUp className="h-8 w-8 text-[#F0E68C]" />
              </div>
              <h3 className="text-xl font-bold mb-4 text-center">Tech Startups</h3>
              <p className="text-white text-opacity-90 text-center mb-6">
                Africa's vibrant startup ecosystem uses TAIFA | FIALA to discover accelerator programs, grants, and investment opportunities.
              </p>
              <div className="flex justify-center">
                <span className="text-sm inline-flex items-center bg-white bg-opacity-20 rounded-full px-4 py-2">
                  <span className="mr-2">25+ Startups</span>
                  <span className="w-2 h-2 rounded-full bg-green-400"></span>
                </span>
              </div>
            </div>
          </div>
          
          {/* Pan-African Impact Summary */}
          <div className="mt-16 bg-white bg-opacity-10 backdrop-blur-sm rounded-xl p-8 border border-white border-opacity-20">
            <div className="text-center">
              <h3 className="text-2xl font-bold mb-4">Supporting Innovation Across Africa</h3>
              <p className="mb-6 text-white text-opacity-90 max-w-3xl mx-auto">
                Our platform connects African innovators with global opportunities, fostering sustainable growth and equitable development across the continent.
              </p>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div className="text-center bg-[#1F2A44] bg-opacity-30 rounded-lg p-4 shadow-sm">
                  <div className="text-3xl font-bold text-[#F0E68C]">54</div>
                  <div className="text-sm text-white text-opacity-90 font-medium mt-1">Countries Covered</div>
                </div>
                <div className="text-center bg-[#1F2A44] bg-opacity-30 rounded-lg p-4 shadow-sm">
                  <div className="text-3xl font-bold text-[#F0E68C]">$300M+</div>
                  <div className="text-sm text-white text-opacity-90 font-medium mt-1">AI Funding Tracked</div>
                </div>
                <div className="text-center bg-[#1F2A44] bg-opacity-30 rounded-lg p-4 shadow-sm">
                  <div className="text-3xl font-bold text-[#F0E68C]">100+</div>
                  <div className="text-sm text-white text-opacity-90 font-medium mt-1">Active Organizations</div>
                </div>
              </div>
              <Link 
                href="/analytics" 
                className="inline-flex items-center bg-[#F0E68C] hover:bg-[#E6D768] text-[#1F2A44] font-bold py-3 px-7 rounded-md text-base transition-colors shadow-md"
              >
                <TrendingUp className="h-5 w-5 mr-2" />
                View Impact Analytics
              </Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
