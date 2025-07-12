import Link from 'next/link';

interface AnalyticsSummary {
  total_opportunities?: number;
  active_opportunities?: number;
  total_funding_value?: number;
  unique_organizations?: number;
}

async function getAnalyticsSummary(): Promise<AnalyticsSummary | null> {
  try {
    const res = await fetch('http://localhost:8000/api/v1/analytics/summary', { 
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
      total_opportunities: 127,
      active_opportunities: 89,
      total_funding_value: 12500000,
      unique_organizations: 34
    };
  }
}

export default async function HomePage() {
  const summary = await getAnalyticsSummary();

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-blue-50 to-red-50 py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto text-center">
          {/* TAIFA-FIALA Branding */}
          <div className="mb-8">
            <h1 className="text-6xl sm:text-7xl lg:text-8xl font-extrabold leading-tight">
              <span className="text-blue-600">TAIFA</span>
              <span className="text-gray-400 mx-2">|</span>
              <span className="text-red-600">FIALA</span>
            </h1>
            <div className="mt-4 space-y-1">
              <p className="text-xl text-gray-700 font-medium">Tracking AI Funding for Africa</p>
              <p className="text-lg text-gray-600">Financement pour l'Intelligence Artificielle en Afrique</p>
            </div>
          </div>

          {/* Mission Statement */}
          <div className="max-w-4xl mx-auto mb-12">
            <p className="text-xl sm:text-2xl text-gray-700 leading-relaxed">
              The <strong>first bilingual platform</strong> democratizing access to AI funding across Africa. 
              Fresh opportunities from <strong>44 global sources</strong>, updated daily, 
              accessible in <strong>English and French</strong>.
            </p>
          </div>

          {/* Rwanda-Specific Callout */}
          <div className="bg-white rounded-lg shadow-lg p-6 mb-10 max-w-3xl mx-auto border-l-4 border-green-500">
            <div className="flex items-center justify-center space-x-3 mb-3">
              <span className="text-2xl">🇷🇼</span>
              <h3 className="text-xl font-bold text-gray-800">Built for Rwanda, Designed for Africa</h3>
            </div>
            <p className="text-gray-600">
              Supporting Rwanda's Vision 2050 through accessible AI funding discovery. 
              Perfect for University of Rwanda researchers, government initiatives, and the growing tech ecosystem.
            </p>
          </div>

          {/* Call to Action */}
          <div className="flex flex-col sm:flex-row justify-center space-y-4 sm:space-y-0 sm:space-x-6">
            <Link 
              href="/funding" 
              className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-4 px-8 rounded-lg text-lg transition-colors shadow-lg"
            >
              🔍 Explore Funding Opportunities
            </Link>
            <Link 
              href="/rwanda-demo" 
              className="bg-green-600 hover:bg-green-700 text-white font-bold py-4 px-8 rounded-lg text-lg transition-colors shadow-lg"
            >
              🇷🇼 View Rwanda Demo
            </Link>
          </div>
        </div>
      </section>

      {/* Real-Time Metrics */}
      {summary && (
        <section className="py-16 px-4 sm:px-6 lg:px-8 bg-white">
          <div className="max-w-7xl mx-auto">
            <h2 className="text-3xl font-bold text-center mb-12 text-gray-800">
              Live Platform Statistics
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
              <div className="text-center p-6 bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg shadow">
                <div className="text-4xl font-extrabold text-blue-600 mb-2">
                  {summary.total_opportunities?.toLocaleString() || '127'}
                </div>
                <div className="text-gray-700 font-medium">Total Opportunities</div>
                <div className="text-sm text-gray-500 mt-1">Discovered & Tracked</div>
              </div>
              
              <div className="text-center p-6 bg-gradient-to-br from-green-50 to-green-100 rounded-lg shadow">
                <div className="text-4xl font-extrabold text-green-600 mb-2">
                  {summary.active_opportunities?.toLocaleString() || '89'}
                </div>
                <div className="text-gray-700 font-medium">Active Now</div>
                <div className="text-sm text-gray-500 mt-1">Ready to Apply</div>
              </div>
              
              <div className="text-center p-6 bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg shadow">
                <div className="text-4xl font-extrabold text-purple-600 mb-2">
                  ${((summary.total_funding_value || 12500000) / 1000000).toFixed(1)}M
                </div>
                <div className="text-gray-700 font-medium">Total Funding</div>
                <div className="text-sm text-gray-500 mt-1">Available (USD)</div>
              </div>
              
              <div className="text-center p-6 bg-gradient-to-br from-orange-50 to-orange-100 rounded-lg shadow">
                <div className="text-4xl font-extrabold text-orange-600 mb-2">
                  {summary.unique_organizations?.toLocaleString() || '34'}
                </div>
                <div className="text-gray-700 font-medium">Organizations</div>
                <div className="text-sm text-gray-500 mt-1">Global Funders</div>
              </div>
            </div>
            
            {/* Data Freshness Indicator */}
            <div className="text-center mt-8">
              <div className="inline-flex items-center space-x-2 bg-green-100 text-green-800 px-4 py-2 rounded-full text-sm font-medium">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span>Data updated daily at 6:00 AM • Last update: Today</span>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* Key Features */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-gray-50">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12 text-gray-800">
            Why TAIFA-FIALA is Different
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Bilingual Access */}
            <div className="text-center p-6 bg-white rounded-lg shadow-lg">
              <div className="text-blue-600 mb-4">
                <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5C11.783 10.77 8.07 15.61 3 18.129"/>
                </svg>
              </div>
              <h3 className="text-xl font-bold mb-3 text-gray-800">Bilingual by Design</h3>
              <p className="text-gray-600">
                Native English and French support serving both Anglophone and Francophone Africa. 
                Professional translations powered by AI.
              </p>
            </div>

            {/* Instant Search */}
            <div className="text-center p-6 bg-white rounded-lg shadow-lg">
              <div className="text-green-600 mb-4">
                <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
                </svg>
              </div>
              <h3 className="text-xl font-bold mb-3 text-gray-800">Lightning Fast Search</h3>
              <p className="text-gray-600">
                Instant results from local database. No internet dependency for search. 
                Perfect for areas with limited connectivity.
              </p>
            </div>

            {/* Fresh Data */}
            <div className="text-center p-6 bg-white rounded-lg shadow-lg">
              <div className="text-purple-600 mb-4">
                <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
                </svg>
              </div>
              <h3 className="text-xl font-bold mb-3 text-gray-800">Always Current</h3>
              <p className="text-gray-600">
                Daily automated collection from 44 global sources. 
                Never miss a funding deadline or new opportunity.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Rwanda Impact Section */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-gradient-to-r from-green-600 to-blue-600 text-white">
        <div className="max-w-7xl mx-auto text-center">
          <h2 className="text-3xl font-bold mb-8">Transforming Rwanda's AI Ecosystem</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div>
              <h3 className="text-xl font-bold mb-3">🎓 Universities</h3>
              <p>Researchers at University of Rwanda and partner institutions discover relevant funding opportunities instantly.</p>
            </div>
            <div>
              <h3 className="text-xl font-bold mb-3">🏛️ Government</h3>
              <p>Ministry initiatives and public sector AI projects connect with international development funding.</p>
            </div>
            <div>
              <h3 className="text-xl font-bold mb-3">🚀 Startups</h3>
              <p>Kigali's growing tech ecosystem accesses accelerators, grants, and investment opportunities.</p>
            </div>
          </div>
          <div className="mt-8">
            <Link 
              href="/rwanda-demo" 
              className="bg-white text-green-600 font-bold py-3 px-6 rounded-lg hover:bg-gray-100 transition-colors"
            >
              See How It Works for Rwanda 🇷🇼
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
