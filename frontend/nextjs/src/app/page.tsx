import Link from 'next/link';
import DatabaseGrowthChart from '@/components/homepage/DatabaseGrowthChart';
import GeographicDistributionMapWrapper from '@/components/homepage/GeographicDistributionMapWrapper';
import SectorAllocationChart from '@/components/homepage/SectorAllocationChart';
import GenderEquityDashboard from '@/components/homepage/GenderEquityDashboard';
import { Database, BarChart3, BookOpen, Users, TrendingUp, ChevronRight } from 'lucide-react';
import Image from 'next/image';
import SearchBar from '@/components/homepage/SearchBar';
import { getApiUrl, API_ENDPOINTS } from '@/lib/api-config';

interface AnalyticsSummary {
  total_opportunities?: number;
  active_opportunities?: number;
  total_funding_value?: number;
  unique_organizations?: number;
}

async function getAnalyticsSummary(): Promise<AnalyticsSummary | null> {
  try {
    const res = await fetch(getApiUrl(API_ENDPOINTS.equityAnalysesSummary), {
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
      total_opportunities: 2467,
      active_opportunities: 127,
      total_funding_value: 847000000,
      unique_organizations: 159
    };
  }
}

export default async function HomePage() {
  const summary = await getAnalyticsSummary();

  return (
    <div className="min-h-screen">
      {/* Modern Hero Section with Africa Outline */}
      <section className="relative overflow-hidden py-8 sm:py-12 border-b border-gray-200">
        {/* Background Africa Outline */}
        <div className="absolute inset-0 flex justify-center items-center z-0 opacity-10">
          <Image 
            src="/Africa-outline-yellow.png" 
            alt="Africa Outline" 
            width={800} 
            height={800} 
            className="object-contain"
          />
        </div>
        
        <div className="max-w-7xl mx-auto text-center px-4 sm:px-6 lg:px-8 relative z-10">
          {/* Logo and Branding */}
          <div className="flex justify-center mb-6">
            <Image 
              src="/TAIFA-FIALA-Logo_transparent.png" 
              alt="TAIFA-FIALA Logo" 
              width={320} 
              height={400} 
              className="object-contain"
            />
          </div>
          
          <div className="flex text-4xl font-bold justify-center mb-6">
            Tracking AI Funding in Africa | Financements Pour IA en Afrique
          </div>
          
          <p className="text-xl text-gray-700 max-w-3xl mx-auto leading-relaxed mb-10 font-body">
            An independent initiative promoting transparency, equity and accountability 
            in AI research and implementation across all African nations.
          </p>
          
          {/* Search Bar - Centered */}
          <div className="max-w-2xl mx-auto mb-12">
            <SearchBar />
          </div>
          
          {/* Quick Navigation Links */}
          <nav className="flex flex-wrap justify-center gap-6 text-base font-medium">
            <Link href="/funding-landscape" className="text-taifa-primary hover:text-taifa-secondary transition-colors flex items-center gap-2">
              <BarChart3 className="w-4 h-4" />
              Funding Landscape
            </Link>
            <Link href="/funding" className="text-taifa-primary hover:text-taifa-secondary transition-colors flex items-center gap-2">
              <BookOpen className="w-4 h-4" />
             Funding
            </Link>
            <Link href="/methodology" className="text-taifa-primary hover:text-taifa-secondary transition-colors flex items-center gap-2">
              <Database className="w-4 h-4" />
              Methodology
            </Link>
            <Link href="/about" className="text-taifa-primary hover:text-taifa-secondary transition-colors flex items-center gap-2">
              <Users className="w-4 h-4" />
              About Us  
            </Link>
          </nav>
        </div>
      </section>

      {/* Key Metrics Dashboard with Live Chart */}
      <section id="findings" className="py-12 px-4 sm:px-6 lg:px-8 bg-gray-50">
        <div className="max-w-7xl mx-auto">
          {/* Animated Metric Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
            <div className="bg-white p-6 rounded-xl shadow-lg text-center border-l-4 border-amber-600 transform hover:scale-105 transition-all duration-300 hover:shadow-xl">
              <div className="text-3xl font-bold text-amber-700 mb-2 animate-pulse">
                {summary?.total_opportunities?.toLocaleString() || '2,467'}
              </div>
              <div className="text-sm text-gray-600">Total Opportunities</div>
            </div>
            <div className="bg-white p-6 rounded-xl shadow-lg text-center border-l-4 border-emerald-600 transform hover:scale-105 transition-all duration-300 hover:shadow-xl">
              <div className="text-3xl font-bold text-emerald-700 mb-2 animate-pulse">
                {summary?.active_opportunities?.toLocaleString() || '127'}
              </div>
              <div className="text-sm text-gray-600">Active Opportunities</div>
            </div>
            <div className="bg-white p-6 rounded-xl shadow-lg text-center border-l-4 border-orange-600 transform hover:scale-105 transition-all duration-300 hover:shadow-xl">
              <div className="text-3xl font-bold text-orange-700 mb-2 animate-pulse">
                ${((summary?.total_funding_value || 847000000) / 1000000).toFixed(0)}M
              </div>
              <div className="text-sm text-gray-600">Total Funding Tracked</div>
            </div>
            <div className="bg-white p-6 rounded-xl shadow-lg text-center border-l-4 border-red-600 transform hover:scale-105 transition-all duration-300 hover:shadow-xl">
              <div className="text-3xl font-bold text-red-700 mb-2 animate-pulse">
                {summary?.unique_organizations?.toLocaleString() || '159'}
              </div>
              <div className="text-sm text-gray-600">Organizations</div>
            </div>
          </div>

          {/* Live Database Growth Chart */}
          <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold text-gray-900 mb-2">Live Intelligence Collection</h2>
              <p className="text-gray-600">Real-time tracking of AI funding opportunities across Africa</p>
            </div>
            <DatabaseGrowthChart />
          </div>
        </div>
      </section>

      {/* Key Issues Section */}
      <section id="data" className="py-12 px-4 sm:px-6 lg:px-8 bg-white">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-2xl font-display text-gray-900 mb-8 flex items-center gap-3">
            <TrendingUp className="w-6 h-6 text-taifa-primary" />
            Issues of Equity in AI Funding We are Tracking
          </h2>
          
          {/* Issue 1: Geographic Concentration */}
          <div className="mb-12">
            <div className="bg-white p-8 rounded-lg shadow-sm border border-gray-200">
              <h3 className="text-xl font-semibold text-gray-900 mb-4">
                Geographic Concentration
              </h3>
              
              {/* Geographic Distribution Map */}
              <div className="mb-6">
                <GeographicDistributionMapWrapper />
              </div>
              
              <p className="text-gray-700 leading-relaxed mb-4">
                We are watching {summary?.total_opportunities?.toLocaleString() || '2,467'} funding events to monitor the potential for geographic disparities, with 83% of tracked funding concentrated in just four countries: 
                Kenya, Nigeria, South Africa, and Egypt. Central African nations receive less than 2% of total 
                funding despite being home to more than 180 million people.
              </p>
              
              <div className="mt-4 text-sm text-gray-600">
                <Link href="/funding-landscape" className="text-blue-700 hover:underline inline-flex items-center gap-1">
                  View detailed analysis <ChevronRight className="w-4 h-4" />
                </Link>
              </div>
            </div>
          </div>

          {/* Issue 2: Sectoral Misalignment */}
          <div className="mb-12">
            <div className="bg-white p-8 rounded-lg shadow-sm border border-gray-200">
              <h3 className="text-xl font-semibold text-gray-900 mb-4">
                Sectoral Funding Misalignment 
              </h3>
              
              {/* Sector Allocation Chart */}
              <div className="mb-6">
                <SectorAllocationChart />
              </div>
              
              <p className="text-gray-700 leading-relaxed mb-4">
                Health applications receive only 5.8% of AI funding despite the continent bearing 25% 
                of the global disease burden. Agricultural technology, which employs 60% of Africa's workforce, 
                attracts merely 3.9% of funding. In contrast, financial services capture 20.9% of investments, 
                revealing a critical misalignment between funding priorities and development needs.
              </p>
              
              <div className="mt-4 text-sm text-gray-600">
                <Link href="/funding-landscape" className="text-blue-700 hover:underline inline-flex items-center gap-1">
                  Explore sectoral analysis <ChevronRight className="w-4 h-4" />
                </Link>
              </div>
            </div>
          </div>

          {/* Issue 3: Gender Disparity */}
          <div className="mb-12">
            <div className="bg-white p-8 rounded-lg shadow-sm border border-gray-200">
              <h3 className="text-xl font-semibold text-gray-900 mb-6 flex items-center gap-3">
                <Users className="w-5 h-5 text-red-600" />
                Gender Disparity
              </h3>
              
              {/* Enhanced Gender Equity Dashboard */}
              <GenderEquityDashboard />
              
              <div className="mt-6 p-4 bg-amber-50 rounded-lg border-l-4 border-amber-600">
                <p className="text-sm text-amber-800">
                  <strong>Urgent Action Needed:</strong> Female leadership in African AI has declined consistently 
                  over 6 years, with funding gaps widening across all sectors and regions. This threatens 
                  inclusive AI development across the continent.
                </p>
              </div>
              
              <div className="mt-4 text-sm text-gray-600">
                <Link href="/equity-assessment" className="text-amber-700 hover:underline inline-flex items-center gap-1">
                  View comprehensive gender equity analysis <ChevronRight className="w-4 h-4" />
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Brief About Us */}
      <section className="py-12 px-4 sm:px-6 lg:px-8 bg-gray-50">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl font-bold text-gray-900 mb-6">About TAIFA-FIALA</h2>
          <p className="text-xl text-gray-700 mb-8 leading-relaxed">
            TAIFA-FIALA is an independent initiative dedicated to promoting transparency, 
            equity, and accountability in AI funding across Africa. We provide comprehensive 
            data analysis and insights to support evidence-based decision making in the 
            African AI ecosystem.
          </p>
          
          <div className="grid md:grid-cols-3 gap-8 mb-8">
            <div className="text-center">
              <Database className="w-12 h-12 text-amber-700 mx-auto mb-4" />
              <h3 className="text-lg font-semibold mb-2">Comprehensive Data</h3>
              <p className="text-gray-600">Real-time tracking of AI funding opportunities across all 54 African countries</p>
            </div>
            <div className="text-center">
              <Users className="w-12 h-12 text-emerald-700 mx-auto mb-4" />
              <h3 className="text-lg font-semibold mb-2">Equity Focus</h3>
              <p className="text-gray-600">Dedicated analysis of gender, geographic, and sectoral disparities in funding</p>
            </div>
            <div className="text-center">
              <BookOpen className="w-12 h-12 text-orange-700 mx-auto mb-4" />
              <h3 className="text-lg font-semibold mb-2">Open Research</h3>
              <p className="text-gray-600">Transparent methodology and publicly accessible insights for the research community</p>
            </div>
          </div>
          
          <Link 
            href="/about" 
            className="bg-taifa-primary text-white px-8 py-3 rounded-lg font-semibold hover:bg-taifa-secondary transition-colors inline-flex items-center gap-2"
          >
            Learn More About Our Mission
            <ChevronRight className="w-4 h-4" />
          </Link>
        </div>
      </section>

      {/* CACHED CONTENT FOR FUTURE USE
      
      // AI Funding Landscape Dashboard
      <section className="py-12 px-4 sm:px-6 lg:px-8 bg-white">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-2xl font-display text-gray-900 mb-8 flex items-center gap-3">
            <BarChart3 className="w-6 h-6 text-taifa-primary" />
            AI Funding Landscape Dashboard
          </h2>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Geographic Distribution</h3>
              <GeographicDistributionMap />
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Sector Allocation vs Development Needs</h3>
              <SectorAllocationChart />
            </div>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Data Collection Progress</h3>
            <DatabaseGrowthChart />
          </div>
        </div>
      </section>

      // Equity & Inclusion Analysis Hub
      <section className="py-12 px-4 sm:px-6 lg:px-8 bg-gray-50">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-2xl font-display text-gray-900 mb-8 flex items-center gap-3">
            <Users className="w-6 h-6 text-taifa-primary" />
            Equity & Inclusion Analysis Hub
          </h2>
          
          <EquityMetricsDashboard />
        </div>
      </section>
      
      */}
    </div>
  );
}
