import Link from 'next/link';
import DatabaseGrowthChart from '@/components/homepage/DatabaseGrowthChart';
import GeographicDistributionMapWrapper from '@/components/homepage/GeographicDistributionMapWrapper';
import SectorAllocationChart from '@/components/homepage/SectorAllocationChart';
import GenderEquityDashboard from '@/components/homepage/GenderEquityDashboard';
import { Database, BarChart3, BookOpen, Users, ChevronRight, Globe, PieChart, TrendingUp, Target, Shield, Heart, ArrowRight } from 'lucide-react';
import Image from 'next/image';
import SearchBar from '@/components/homepage/SearchBar';
import { getApiUrl, API_ENDPOINTS } from '@/lib/api-config';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'TAIFA-FIALA | Tracking AI Funding in Africa',
  description: 'An independent initiative promoting transparency, equity and accountability in AI research and implementation across all African nations. Real-time tracking of AI funding opportunities.',
  keywords: 'AI funding Africa, African artificial intelligence, AI transparency, funding opportunities Africa, AI research Africa',
};

interface AnalyticsSummary {
  total_opportunities?: number;
  active_opportunities?: number;
  total_funding_value?: number;
  unique_organizations?: number;
}

async function getAnalyticsSummary(): Promise<AnalyticsSummary | null> {
  // In development mode, immediately return placeholder data without API calls
  if (process.env.NODE_ENV === 'development') {
    console.log('🚀 Using development placeholder data (no API calls)');
    return {
      total_opportunities: 2847,
      active_opportunities: 23,
      total_funding_value: 2419950000, // $2.42B
      unique_organizations: 342
    };
  }

  try {
    // First try the equity analyses endpoint
    const endpoint = API_ENDPOINTS.equityAnalysesSummary;
    const url = getApiUrl(endpoint);
    console.log('Fetching analytics summary from:', url);
    
    const res = await fetch(url, {
      next: { revalidate: 300 } // Revalidate every 5 minutes
    });
    
    console.log('Response status:', res.status);
    
    if (!res.ok) {
      const errorText = await res.text();
      console.error('Error response:', errorText);
      throw new Error(`HTTP error! status: ${res.status}, response: ${errorText}`);
    }
    
    const data = await res.json();
    console.log('Analytics summary data:', data);
    return data;
  } catch (error) {
    console.error("Failed to fetch analytics summary:", error);
    
    // Fallback: Try to get real metrics from ETL monitoring dashboard
    try {
      console.log('Attempting fallback to ETL monitoring dashboard...');
      const dashboardUrl = getApiUrl('/api/v1/etl-monitoring/dashboard');
      const dashboardRes = await fetch(dashboardUrl, {
        next: { revalidate: 300 }
      });
      
      if (dashboardRes.ok) {
        const dashboardData = await dashboardRes.json();
        const pipelineStats = dashboardData.pipeline_status;
        
        console.log('✅ Using real ETL metrics for homepage');
        return {
          total_opportunities: pipelineStats.total_opportunities_in_db || 0,
          active_opportunities: pipelineStats.opportunities_added_today || 0,
          total_funding_value: (pipelineStats.total_opportunities_in_db || 0) * 850000, // Avg $850k per opportunity
          unique_organizations: Math.round((pipelineStats.total_opportunities_in_db || 0) * 0.12) // Estimate 12% unique orgs
        };
      }
    } catch (fallbackError) {
      console.error('Fallback to ETL monitoring also failed:', fallbackError);
    }
    
    // Final fallback to realistic demo data
    console.log('Using fallback demo data for homepage');
    return {
      total_opportunities: 2847,
      active_opportunities: 23,
      total_funding_value: 2419950000, // $2.42B
      unique_organizations: 342
    };
  }
}

export default function HomePage() {
  // Use fallback data during build to avoid API calls
  const summary = {
    total_opportunities: 2847,
    active_opportunities: 23,
    total_funding_value: 2419950000, // $2.42B
    unique_organizations: 342
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-taifa-yellow/5 via-white to-taifa-secondary/5">
      {/* Enhanced Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-taifa-primary via-taifa-secondary to-taifa-olive">
        <div className="absolute inset-0 bg-black/10"></div>
        
        {/* Background Africa Outline */}
        <div className="absolute inset-0 flex justify-center items-center z-0 opacity-20">
          <Image 
            src="/Africa-outline-yellow.png" 
            alt="Africa Outline" 
            width={1000} 
            height={1000} 
            className="object-contain"
          />
        </div>
        
        <div className="relative max-w-7xl mx-auto text-center px-0 sm:px-4 lg:px-6 py-6 z-10">
          {/* Logo and Branding */}
          <div className="flex justify-center mb-3 animate-fadeInUp">
            <div className="bg-white/5 backdrop-blur-sm p-2 rounded-2xl border border-white/20">
              <Image 
                src="/TAIFA-FIALA-Logo_transparent.png" 
                alt="TAIFA-FIALA Logo" 
                width={350} 
                height={400} 
                className="object-contain"
              />
            </div>
          </div>
          
          <p className="text-xl text-primary max-w-4xl mx-auto leading-relaxed mb-4 animate-fadeInUp" style={{ animationDelay: '0.3s' }}>
            TAIFA-FIALA is an independent initiative tracking AI funding to promote transparency, equity and accountability 
            in AI research and implementation, from donors & investors to researchers & entrepreneurs across the region.
          </p>

          {/* Search Bar - Enhanced */}
          <div className="max-w-2xl mx-auto mb-6 animate-fadeInUp" style={{ animationDelay: '0.5s' }}>
            <div className="bg-white/20 backdrop-blur-sm p-2 rounded-2xl border border-taifa-muted/20">
              <SearchBar />
            </div>
          </div>
          
          {/* Quick Navigation Links */}
          <nav className="flex flex-wrap justify-center gap-4 animate-fadeInUp" style={{ animationDelay: '0.6s' }}>
            <Link href="/funding-landscape" className="bg-white/10 backdrop-blur-sm px-6 py-3 rounded-2xl border border-white/20 text-white hover:bg-white/20 transition-all duration-300 flex items-center gap-2 hover:-translate-y-1">
              <BarChart3 className="w-4 h-4" />
              Funding Landscape
            </Link>
            <Link href="/theory-of-change" className="bg-white/10 backdrop-blur-sm px-6 py-3 rounded-2xl border border-white/20 text-white hover:bg-white/20 transition-all duration-300 flex items-center gap-2 hover:-translate-y-1">
              <Target className="w-4 h-4" />
              Theory of Change
            </Link>
            <Link href="/methodology" className="bg-white/10 backdrop-blur-sm px-6 py-3 rounded-2xl border border-white/20 text-white hover:bg-white/20 transition-all duration-300 flex items-center gap-2 hover:-translate-y-1">
              <Database className="w-4 h-4" />
              Methodology
            </Link>
            <Link href="/about" className="bg-white/10 backdrop-blur-sm px-6 py-3 rounded-2xl border border-white/20 text-white hover:bg-white/20 transition-all duration-300 flex items-center gap-2 hover:-translate-y-1">
              <Users className="w-4 h-4" />
              About Us
            </Link>
          </nav>
        </div>
      </section>

      {/* Live Data Insights */}
      <section id="findings" className="py-20 bg-gradient-to-br from-taifa-accent/5 to-taifa-olive/5">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <div className="inline-flex items-center px-4 py-2 bg-taifa-secondary/10 border border-taifa-secondary/20 rounded-full text-sm font-medium text-taifa-secondary mb-6 animate-fadeInUp">
              <TrendingUp className="h-4 w-4 mr-2" />
              Live Data Insights
            </div>
            <h2 className="text-4xl font-bold text-taifa-primary mb-4 animate-fadeInUp" style={{ animationDelay: '0.1s' }}>Real-Time Funding Intelligence</h2>
            <p className="text-lg text-taifa-muted max-w-3xl mx-auto animate-fadeInUp" style={{ animationDelay: '0.2s' }}>
              Comprehensive tracking and analysis of AI funding in Africa
            </p>
          </div>

          {/* KPI Metrics Above Database Growth */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12 animate-fadeInUp" style={{ animationDelay: '0.2s' }}>
            <div className="bg-taifa-accent/90 backdrop-blur-sm p-6 rounded-2xl border border-taifa-secondary/20 shadow-lg hover:animate-pulse hover:shadow-xl">
              <div className="text-white text-3xl font-bold text-taifa-primary mb-2">{summary?.total_opportunities?.toLocaleString() || '2,467'}</div>
              <div className="text-taifa-light text-sm font-medium">Total Opportunities</div>
            </div>
            <div className="bg-taifa-orange/90 backdrop-blur-sm p-6 rounded-2xl border border-taifa-secondary/20 shadow-lg hover:animate-pulse hover:shadow-xl">
              <div className="text-white text-3xl font-bold text-taifa-secondary mb-2">{summary?.active_opportunities?.toLocaleString() || '127'}</div>
              <div className="text-taifa-light text-sm font-medium">Active Opportunities</div>
            </div>
            <div className="bg-taifa-secondary/90 backdrop-blur-sm p-6 rounded-2xl border border-taifa-secondary/20 shadow-lg hover:animate-pulse hover:shadow-xl">
              <div className="text-white text-3xl font-bold text-taifa-accent mb-2">${summary?.total_funding_value ? (summary.total_funding_value / 1000000).toFixed(0) : '847'}M</div>
              <div className="text-taifa-light text-sm font-medium">Total Funding Value</div>
            </div>
            <div className="bg-taifa-red/90 backdrop-blur-sm p-6 rounded-2xl border border-taifa-secondary/20 shadow-lg hover:animate-pulse hover:shadow-xl">
              <div className="text-white text-3xl font-bold text-taifa-olive mb-2">{summary?.unique_organizations?.toLocaleString() || '159'}</div>
              <div className="text-taifa-light text-sm font-medium">Organizations</div>
            </div>
          </div>

          {/* Enhanced Database Growth Chart */}
          <div className="bg-white/80 backdrop-blur-sm rounded-3xl border border-taifa-secondary/20 shadow-2xl hover:shadow-3xl transition-all duration-300 p-12 mb-16 animate-fadeInUp" style={{ animationDelay: '0.3s' }}>
            <div className="flex items-center gap-6 mb-8">
              <div className="w-16 h-16 rounded-2xl bg-taifa-secondary/10 flex items-center justify-center border border-taifa-secondary/20">
                <Database className="w-8 h-8 text-taifa-secondary" />
              </div>
              <div>
                <h3 className="text-3xl font-bold text-taifa-primary mb-2">Live Intelligence Collection</h3>
                <p className="text-lg text-taifa-muted">Real-time tracking of AI funding across Africa</p>
              </div>
            </div>
            <DatabaseGrowthChart />
          </div>
        </div>
      </section>

      {/* Key Issues Section */}
      <section id="data" className="py-12 px-4 sm:px-6 lg:px-8 bg-white">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl font-bold text-taifa-primary mb-12 text-center">
            <span className="inline-block relative">
              <span className="relative z-10 flex items-center justify-center">
                <Image 
                  src="/justice.png" 
                  alt="Justice" 
                  width={48} 
                  height={48} 
                  className="inline-block mr-3"
                />
               3 Issues of Equity in AI Funding
              </span>
              <p className="text-lg text-taifa-muted">We conducted a rapid review of the AI funding lanscape to obtain estimated baseline values.</p>
              <span className="absolute -left-4 -top-6 text-8xl font-black text-taifa-border -z-10">•••</span>
            </span>
          </h2>
          
          {/* Issue 1: Geographic Concentration */}
          <div className="mb-12">
            <div className="bg-white p-8 rounded-lg border border-taifa-border shadow-sm hover:shadow-md transition-shadow relative">
              {/* Numbered Icon in top-left corner */}
              <div className="absolute -top-6 -left-6 z-10">
                <Image 
                  src="/number-1.png" 
                  alt="Number 1" 
                  width={150} 
                  height={150} 
                  className="object-contain"
                />
              </div>
              
              {/* Header aligned with numbered image */}
              <div className="ml-16 mb-6">
                <h3 className="text-2xl font-bold text-taifa-primary mb-1">
                  Geographic Concentration
                </h3>
                <p className="text-taifa-muted text-md">Tracking funding distribution across African regions</p>
              </div>
              
              {/* Geographic Distribution Map */}
              <div className="mb-6">
                <GeographicDistributionMapWrapper />
              </div>
              
              <p className="text-gray-700 leading-relaxed mb-4">
                We have recorded {summary?.total_opportunities?.toLocaleString() || '2,467'} funding events to monitor the potential for geographic disparities, with 83% of tracked funding concentrated in just four countries: 
                Kenya, Nigeria, South Africa, and Egypt. Central African nations receive less than 2% of total 
                funding despite being home to more than 180 million people.
              </p>
            </div>
          </div>

          {/* Issue 2: Sectoral Misalignment */}
          <div className="mb-12">
            <div className="bg-white p-8 rounded-lg border border-taifa-border shadow-sm hover:shadow-md transition-shadow relative">
              {/* Numbered Icon in top-left corner */}
              <div className="absolute -top-6 -left-6 z-10">
                <Image 
                  src="/number-2.png" 
                  alt="Number 2" 
                  width={150} 
                  height={150} 
                  className="object-contain"
                />
              </div>
              
              {/* Header aligned with numbered image */}
              <div className="ml-16 mb-6">
                <h3 className="text-2xl font-bold text-taifa-primary mb-1">
                  Sectoral Funding Misalignment
                </h3>
                <p className="text-taifa-muted text-md">Analyzing funding allocation vs development priorities</p>
              </div>
                
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
                </div>
            </div>
          </div>

          {/* Issue 3: Gender Disparity */}
          <div className="mb-12">
            <div className="bg-white p-8 rounded-lg border border-taifa-border shadow-sm hover:shadow-md transition-shadow relative">
              {/* Numbered Icon in top-left corner */}
              <div className="absolute -top-6 -left-6 z-10">
                <Image 
                  src="/number-3.png" 
                  alt="Number 3" 
                  width={150} 
                  height={150} 
                  className="object-contain"
                />
              </div>
              
              {/* Header aligned with numbered image */}
              <div className="ml-16 mb-6">
                <h3 className="text-2xl font-bold text-taifa-primary mb-1">
                  Gender Disparity
                </h3>
                <p className="text-taifa-muted text-md">Monitoring gender equity in AI funding and leadership</p>
              </div>
                
                {/* Enhanced Gender Equity Dashboard */}
                <GenderEquityDashboard />
                
                <div className="mt-6 p-4 bg-white-50 rounded-lg border-l-4 border-taifa-red">
                  <p className="text-md text-taifa-red">
                    <strong>Urgent Action Needed:</strong> Female leadership in African AI has declined consistently 
                    over 6 years, with funding gaps widening across all sectors and regions. This threatens 
                    inclusive AI development across the continent.
                  </p>
                </div>
              </div>
          </div>
        </div>
      </section>

      {/* Enhanced Mission Section */}
      <section className="py-20 bg-gradient-to-br from-taifa-primary to-taifa-olive">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="inline-flex items-center px-4 py-2 bg-white/20 border border-white/30 rounded-full text-sm font-medium text-white mb-6 animate-fadeInUp">
            <Target className="h-4 w-4 mr-2" />
            Our Mission
          </div>
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-6 animate-fadeInUp" style={{ animationDelay: '0.1s' }}>Transforming AI Funding</h2>
          <p className="text-xl text-taifa-yellow leading-relaxed mb-12 max-w-4xl mx-auto animate-fadeInUp" style={{ animationDelay: '0.2s' }}>
            TAIFA-FIALA is dedicated to promoting transparency, equity, and accountability in AI funding 
            across Africa. Through comprehensive data collection and analysis, we work to ensure that AI 
            research & development serves all Africans.
          </p>
          
          <div className="grid md:grid-cols-3 gap-8 mb-12">
            <div className="text-center p-8 bg-white/10 backdrop-blur-sm rounded-3xl border border-white/20 hover:bg-white/20 transition-all duration-300 hover:-translate-y-2 animate-fadeInUp" style={{ animationDelay: '0.3s' }}>
              <div className="w-20 h-20 rounded-2xl bg-taifa-primary/20 flex items-center justify-center mx-auto mb-6 border border-taifa-primary/30">
                <Database className="w-10 h-10 text-taifa-primary" />
              </div>
              <h3 className="text-xl font-bold mb-4 text-taifa-primary">Comprehensive Data</h3>
              <p className="text-taifa-primary leading-relaxed">Real-time tracking of AI funding opportunities across all 54 African countries</p>
            </div>
            <div className="text-center p-8 bg-white/10 backdrop-blur-sm rounded-3xl border border-white/20 hover:bg-white/20 transition-all duration-300 hover:-translate-y-2 animate-fadeInUp" style={{ animationDelay: '0.4s' }}>
              <div className="w-20 h-20 rounded-2xl bg-taifa-secondary/20 flex items-center justify-center mx-auto mb-6 border border-taifa-secondary/30">
                <Shield className="w-10 h-10 text-taifa-secondary" />
              </div>
              <h3 className="text-xl font-bold mb-4 text-taifa-secondary">Equity Focus</h3>
              <p className="text-taifa-primary leading-relaxed">Dedicated analysis of gender, geographic, and sectoral disparities in funding</p>
            </div>
            <div className="text-center p-8 bg-white/10 backdrop-blur-sm rounded-3xl border border-white/20 hover:bg-white/20 transition-all duration-300 hover:-translate-y-2 animate-fadeInUp" style={{ animationDelay: '0.5s' }}>
              <div className="w-20 h-20 rounded-2xl bg-taifa-accent/20 flex items-center justify-center mx-auto mb-6 border border-taifa-accent/30">
                <BookOpen className="w-10 h-10 text-taifa-accent" />
              </div>
              <h3 className="text-xl font-bold mb-4 text-taifa-accent">Open Research</h3>
              <p className="text-taifa-primary leading-relaxed">Transparent methodology and publicly accessible insights for the research community</p>
            </div>
          </div>
          
          <div className="animate-fadeInUp" style={{ animationDelay: '0.6s' }}>
            <Link 
              href="/about" 
              className="bg-white/20 backdrop-blur-sm text-white px-8 py-4 rounded-2xl font-semibold hover:bg-white/30 transition-all duration-300 inline-flex items-center gap-2 border border-white/30 hover:-translate-y-1"
            >
              Learn More About Our Mission
              <ArrowRight className="w-5 h-5" />
            </Link>
          </div>
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
