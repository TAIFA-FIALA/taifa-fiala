import React from 'react';
import Link from 'next/link';

export default function AnalyticsPage() {
  return (
    <div className="min-h-screen px-4 py-12 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <header className="mb-10">
          <h1 className="text-4xl font-bold text-blue-dark">Analytics Dashboard</h1>
          <p className="mt-2 text-lg text-gray-600">
            Explore comprehensive analytics on AI funding across Africa, uncovering disparities and opportunities.
          </p>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">
          {/* Overview Stats */}
          <div className="bg-gradient-to-br from-blue-dark to-blue p-8 rounded-xl shadow-lg text-white">
            <h2 className="text-2xl font-bold mb-4">AI Funding Landscape</h2>
            <div className="grid grid-cols-2 gap-6">
              <div>
                <div className="text-sm text-blue-100">Total Available Funding</div>
                <div className="text-4xl font-bold">$12.5M</div>
              </div>
              <div>
                <div className="text-sm text-blue-100">Funding Opportunities</div>
                <div className="text-4xl font-bold">127</div>
              </div>
              <div>
                <div className="text-sm text-blue-100">Funding Organizations</div>
                <div className="text-4xl font-bold">34</div>
              </div>
              <div>
                <div className="text-sm text-blue-100">Countries Covered</div>
                <div className="text-4xl font-bold">54</div>
              </div>
            </div>
          </div>

          {/* Key Challenges */}
          <div className="bg-white p-8 rounded-xl shadow-lg border border-gray-100">
            <h2 className="text-2xl font-bold text-blue-dark mb-4">Key Challenges Identified</h2>
            <ul className="space-y-3">
              <li className="flex items-start">
                <div className="flex-shrink-0 w-6 h-6 rounded-full bg-red-100 text-red-600 flex items-center justify-center mt-0.5">
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <span className="font-semibold text-gray-900">Geographic Inequity:</span>
                  <span className="text-gray-600"> 60% of funding goes to just 4 countries</span>
                </div>
              </li>
              <li className="flex items-start">
                <div className="flex-shrink-0 w-6 h-6 rounded-full bg-red-100 text-red-600 flex items-center justify-center mt-0.5">
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <span className="font-semibold text-gray-900">Gender Gap:</span>
                  <span className="text-gray-600"> Only 2% of funding goes to female-led projects</span>
                </div>
              </li>
              <li className="flex items-start">
                <div className="flex-shrink-0 w-6 h-6 rounded-full bg-red-100 text-red-600 flex items-center justify-center mt-0.5">
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <span className="font-semibold text-gray-900">The Seed Trap:</span>
                  <span className="text-gray-600"> 69% of projects stuck at seed funding stage</span>
                </div>
              </li>
              <li className="flex items-start">
                <div className="flex-shrink-0 w-6 h-6 rounded-full bg-red-100 text-red-600 flex items-center justify-center mt-0.5">
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <span className="font-semibold text-gray-900">Sectoral Misalignment:</span>
                  <span className="text-gray-600"> Critical development sectors are underfunded</span>
                </div>
              </li>
            </ul>
          </div>
        </div>

        {/* Analytics Modules */}
        <h2 className="text-2xl font-bold text-blue-dark mb-6">Equity-Focused Analytics</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">
          {/* Geographic Equity Card */}
          <Link href="/analytics/geographic-equity" className="group">
            <div className="bg-white p-6 rounded-xl shadow-md hover:shadow-lg transition-shadow duration-300 border border-gray-100 h-full flex flex-col">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center">
                  <div className="w-12 h-12 flex items-center justify-center rounded-full bg-blue-100 text-blue-600 mr-4">
                    <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M12 1.586l-4 4v12.828l4-4V1.586zM3.707 3.293A1 1 0 002 4v10a1 1 0 00.293.707L6 18.414V5.586L3.707 3.293zM17.707 5.293L14 1.586v12.828l2.293 2.293A1 1 0 0018 16V6a1 1 0 00-.293-.707z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <h3 className="text-xl font-bold text-blue-dark">Geographic Equity</h3>
                </div>
                <div className="text-blue-600 group-hover:translate-x-1 transition-transform duration-200">
                  <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10.293 5.293a1 1 0 011.414 0l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414-1.414L12.586 11H5a1 1 0 110-2h7.586l-2.293-2.293a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                </div>
              </div>
              <p className="text-gray-600 mb-4">
                Interactive map highlighting funding distribution disparities across African countries, with 60% of funding going to just 4 countries.
              </p>
              <div className="mt-auto pt-4 border-t border-gray-100 flex justify-between items-center text-sm">
                <span className="text-red-500 font-semibold">12 underserved regions</span>
                <span className="text-blue-600 font-semibold">View details →</span>
              </div>
            </div>
          </Link>
          
          {/* Sectoral Alignment Card */}
          <Link href="/analytics/sectoral-alignment" className="group">
            <div className="bg-white p-6 rounded-xl shadow-md hover:shadow-lg transition-shadow duration-300 border border-gray-100 h-full flex flex-col">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center">
                  <div className="w-12 h-12 flex items-center justify-center rounded-full bg-green-100 text-green-600 mr-4">
                    <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M2 10a8 8 0 018-8v8h8a8 8 0 11-16 0z" />
                      <path d="M12 2.252A8.014 8.014 0 0117.748 8H12V2.252z" />
                    </svg>
                  </div>
                  <h3 className="text-xl font-bold text-blue-dark">Sectoral Alignment</h3>
                </div>
                <div className="text-green-600 group-hover:translate-x-1 transition-transform duration-200">
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
                <span className="text-green-600 font-semibold">View details →</span>
              </div>
            </div>
          </Link>
          
          {/* Gender & Inclusion Card */}
          <Link href="/analytics/gender-inclusion" className="group">
            <div className="bg-white p-6 rounded-xl shadow-md hover:shadow-lg transition-shadow duration-300 border border-gray-100 h-full flex flex-col">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center">
                  <div className="w-12 h-12 flex items-center justify-center rounded-full bg-pink-100 text-pink-600 mr-4">
                    <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3zM6 8a2 2 0 11-4 0 2 2 0 014 0zM16 18v-3a5.972 5.972 0 00-.75-2.906A3.005 3.005 0 0119 15v3h-3zM4.75 12.094A5.973 5.973 0 004 15v3H1v-3a3 3 0 013.75-2.906z" />
                    </svg>
                  </div>
                  <h3 className="text-xl font-bold text-blue-dark">Gender & Inclusion</h3>
                </div>
                <div className="text-pink-600 group-hover:translate-x-1 transition-transform duration-200">
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
                <span className="text-pink-600 font-semibold">View details →</span>
              </div>
            </div>
          </Link>
          
          {/* Funding Lifecycle Card */}
          <Link href="/analytics/funding-lifecycle" className="group">
            <div className="bg-white p-6 rounded-xl shadow-md hover:shadow-lg transition-shadow duration-300 border border-gray-100 h-full flex flex-col">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center">
                  <div className="w-12 h-12 flex items-center justify-center rounded-full bg-purple-100 text-purple-600 mr-4">
                    <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <h3 className="text-xl font-bold text-blue-dark">Funding Lifecycle</h3>
                </div>
                <div className="text-purple-600 group-hover:translate-x-1 transition-transform duration-200">
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
                <span className="text-purple-600 font-semibold">View details →</span>
              </div>
            </div>
          </Link>
        </div>
        
        {/* Future Analytics Section */}
        <div className="bg-gray-50 rounded-xl p-8">
          <h2 className="text-2xl font-bold text-blue-dark mb-4">Coming Soon</h2>
          <p className="text-gray-600 mb-6">
            Additional analytics modules in development to further support equitable AI funding across Africa.
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white p-4 rounded-lg border border-gray-100 flex items-center space-x-3">
              <div className="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center">
                <svg className="w-5 h-5 text-gray-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-3a1 1 0 00-.867.5 1 1 0 11-1.731-1A3 3 0 0113 8a3.001 3.001 0 01-2 2.83V11a1 1 0 11-2 0v-1a1 1 0 011-1 1 1 0 100-2zm0 8a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd" />
                </svg>
              </div>
              <span className="text-gray-500 font-medium">Impact Metrics Dashboard</span>
            </div>
            
            <div className="bg-white p-4 rounded-lg border border-gray-100 flex items-center space-x-3">
              <div className="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center">
                <svg className="w-5 h-5 text-gray-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-3a1 1 0 00-.867.5 1 1 0 11-1.731-1A3 3 0 0113 8a3.001 3.001 0 01-2 2.83V11a1 1 0 11-2 0v-1a1 1 0 011-1 1 1 0 100-2zm0 8a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd" />
                </svg>
              </div>
              <span className="text-gray-500 font-medium">Policy Recommendation Tool</span>
            </div>
            
            <div className="bg-white p-4 rounded-lg border border-gray-100 flex items-center space-x-3">
              <div className="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center">
                <svg className="w-5 h-5 text-gray-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-3a1 1 0 00-.867.5 1 1 0 11-1.731-1A3 3 0 0113 8a3.001 3.001 0 01-2 2.83V11a1 1 0 11-2 0v-1a1 1 0 011-1 1 1 0 100-2zm0 8a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd" />
                </svg>
              </div>
              <span className="text-gray-500 font-medium">Capacity Building Analytics</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
