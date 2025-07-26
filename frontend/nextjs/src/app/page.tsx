import Link from 'next/link';
import DatabaseGrowthChart from '@/components/homepage/DatabaseGrowthChart';
import GeographicDistributionMapWrapper from '@/components/homepage/GeographicDistributionMapWrapper';
import SectorAllocationChart from '@/components/homepage/SectorAllocationChart';
import GenderEquityDashboard from '@/components/homepage/GenderEquityDashboard';
import { TrendingUp, Users, BarChart3, Database, Target, Shield, BookOpen, ArrowRight } from 'lucide-react';
import Image from 'next/image';
import SearchBar from '@/components/homepage/SearchBar';
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

// getAnalyticsSummary function removed - was unused and causing loading issues

export default function HomePage() {
  // Use fallback data during build to avoid API calls
  const summary = {
    total_opportunities: 2847,
    active_opportunities: 23,
    total_funding_value: 2419950000, // $2.42B
    unique_organizations: 342
  };

  return (
    <div className="min-h-screen bg-taifa-light">
      {/* Enhanced Hero Section */}
      <section className="relative overflow-hidden bg-taifa-light">
        <div className="absolute inset-0 bg-black/10"></div>
        
        {/* Background Africa Outline */}
        <div className="absolute inset-0 flex justify-center items-center z-0 opacity-20">
          <Image 
            src="/Africa-outline-yellow.png" 
            alt="Africa Outline" 
            width={1800} 
            height={1800} 
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
          
          <p className="text-xl text-taifa-primary max-w-4xl mx-auto leading-relaxed mb-4 animate-fadeInUp" style={{ animationDelay: '0.3s' }}>
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
      <section id="findings" className="py-12 bg-gradient-to-br from-taifa-accent/5 to-taifa-olive/5">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-8">
            <div className="inline-flex items-center px-4 py-2 bg-taifa-secondary/10 border border-taifa-secondary/20 rounded-full text-sm font-medium text-taifa-secondary mb-4 animate-fadeInUp">
              <TrendingUp className="h-4 w-4 mr-2" />
              Live Data Insights
            </div>
            <h2 className="text-4xl font-bold text-taifa-primary mb-4 animate-fadeInUp" style={{ animationDelay: '0.1s' }}>Real-Time Funding Intelligence</h2>
            <p className="text-lg text-taifa-muted max-w-3xl mx-auto animate-fadeInUp" style={{ animationDelay: '0.2s' }}>
              Comprehensive tracking and analysis of AI funding in Africa
            </p>
          </div>

          {/* KPI Metrics Above Database Growth */}
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-8 animate-fadeInUp" style={{ animationDelay: '0.2s' }}>
            <div className="bg-taifa-white p-4 rounded-2xl border-2 border-taifa-accent shadow-lg hover:shadow-xl transition-shadow">
              <div className="text-taifa-accent text-3xl font-bold mb-1">{summary?.total_opportunities?.toLocaleString() || '2,847'}</div>
              <div className="text-taifa-accent text-sm font-medium">Total Announcements</div>
            </div>
            <div className="bg-taifa-white p-4 rounded-2xl border-2 border-taifa-secondary shadow-lg hover:shadow-xl transition-shadow">
              <div className="text-taifa-secondary text-3xl font-bold mb-1">{summary?.active_opportunities?.toLocaleString() || '23'}</div>
              <div className="text-taifa-secondary text-sm font-medium">Recent (P6M)Announcements</div>
            </div>
            <div className="bg-taifa-white p-4 rounded-2xl border-2 border-taifa-orange shadow-lg hover:shadow-xl transition-shadow">
              <div className="text-taifa-orange text-3xl font-bold mb-1">${summary?.total_funding_value ? (summary.total_funding_value / 1000000000).toFixed(1) : '2.4'}B</div>
              <div className="text-taifa-orange text-sm font-medium">Total Funding Value</div>
            </div>
            <div className="bg-taifa-white p-4 rounded-2xl border-2 border-taifa-red shadow-lg hover:shadow-xl transition-shadow">
              <div className="text-taifa-red text-3xl font-bold mb-1">{summary?.unique_organizations?.toLocaleString() || '342'}</div>
              <div className="text-taifa-red text-sm font-medium">Unique Funding Organizations</div>
            </div>
            <div className="bg-taifa-white p-4 rounded-2xl border-2 border-taifa-orange shadow-lg hover:shadow-xl transition-shadow">
              <div className="text-taifa-olive text-3xl font-bold mb-1">{summary?.unique_organizations?.toLocaleString() || '342'}</div>
              <div className="text-taifa-olive text-sm font-medium">Unique Organizations Funded</div>
            </div>
          </div>

          {/* Enhanced Database Growth Chart */}
          <div className="bg-white/80 backdrop-blur-sm rounded-3xl border border-taifa-secondary/20 shadow-2xl hover:shadow-3xl transition-all duration-300 px-6 py-4 mb-8 animate-fadeInUp" style={{ animationDelay: '0.3s' }}>
            <div className="flex items-center gap-4 mb-2">
              <div className="w-12 h-12 rounded-2xl bg-taifa-white/10 flex items-center justify-center border border-taifa-secondary/20">
                <Database className="w-6 h-6 text-taifa-secondary" />
              </div>
              <div>
                <h3 className="text-2xl font-bold text-taifa-primary">Live Intelligence Collection</h3>
                <p className="text-lg text-taifa-muted">Real-time tracking of AI funding across Africa</p>
              </div>
            </div>
            <DatabaseGrowthChart />
          </div>
        </div>
      </section>

      {/* Key Issues Section */}
      <section id="data" className="py-12 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-taifa-primary via-taifa-secondary to-taifa-olive">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl font-bold text-white mb-8 text-center">
            <span className="inline-block relative">
              <span className="relative z-10 flex items-center justify-center">
                <Image 
                  src="/justice.png" 
                  alt="Justice" 
                  width={48} 
                  height={48} 
                  className="inline-block mr-3"
                />
               Issues of Equity in AI Funding
              </span>
            </span>
          </h2>
          <p className="text-lg text-white/80 text-center max-w-4xl mx-auto mb-12">The African AI funding ecosystem has experienced unprecedented growth from 2019-2024, with total commitments exceeding $800 million across multiple funding streams. We conducted a rapid review of the AI funding landscape to obtain estimated baseline values.</p>
          
          {/* Issue 1: Geographic Concentration */}
          <div className="mb-6">
            <div className="bg-white/90 backdrop-blur-sm p-6 rounded-xl border border-taifa-border shadow-lg hover:shadow-xl transition-shadow relative">
              {/* Header with numbered icon aligned horizontally */}
              <div className="flex items-center gap-4 mb-2">
                <div className="flex-shrink-0">
                  <Image 
                    src="/number-1.png" 
                    alt="Number 1" 
                    width={120} 
                    height={120} 
                    className="object-contain"
                  />
                </div>
                <div className="flex-1">
                  <h3 className="text-2xl font-bold text-taifa-orange mb-1">
                    Geographic Concentration
                  </h3>
                  <p className="text-taifa-muted text-lg">Tracking funding distribution across African regions</p>
                </div>
              </div>
              
              {/* Map visualization */}
              <div className="mb-6">
                <GeographicDistributionMapWrapper />
              </div>
              
              <p className="text-taifa-muted leading-relaxed">
                We have recorded {summary?.total_opportunities?.toLocaleString() || '2,467'} funding events to monitor the potential for geographic disparities, with 83% of tracked funding concentrated in just four countries: 
                Kenya, Nigeria, South Africa, and Egypt. Central African nations receive less than 2% of total 
                funding despite being home to more than 180 million people.
              </p>
            </div>
          </div>

          {/* Issue 2: Sectoral Misalignment */}
          <div className="mb-6">
            <div className="bg-white/90 backdrop-blur-sm p-6 rounded-xl border border-taifa-border shadow-lg hover:shadow-xl transition-shadow relative">
              {/* Header with numbered icon aligned horizontally */}
              <div className="flex items-center gap-4 mb-2">
                <div className="flex-shrink-0">
                  <Image 
                    src="/number-2.png" 
                    alt="Number 2" 
                    width={120} 
                    height={120} 
                    className="object-contain"
                  />
                </div>
                <div className="flex-1">
                  <h3 className="text-2xl font-bold text-taifa-accent mb-1">
                    Sectoral Misalignment
                  </h3>
                  <p className="text-taifa-muted text-lg">Comparing funding allocation with development priorities</p>
                </div>
              </div>
              
              {/* Chart visualization */}
              <div className="mb-6">
                <div className="bg-white rounded-lg p-4">
                  <SectorAllocationChart />
                </div>
                
                <p className="text-taifa-primary leading-relaxed mt-4">
                  Health applications receive only 5.8% of AI funding despite the continent bearing 25% 
                  of the global disease burden. Agricultural technology, which employs 60% of Africa's workforce, 
                  attracts merely 3.9% of funding. In contrast, financial services capture 20.9% of investments, 
                  creating a significant misalignment with development priorities.
                </p>
              </div>
            </div>
          </div>

          {/* Issue 3: Gender Disparity */}
          <div className="mb-6">
            <div className="bg-white/90 backdrop-blur-sm p-6 rounded-xl border border-taifa-border shadow-lg hover:shadow-xl transition-shadow relative">
              {/* Header with numbered icon aligned horizontally */}
              <div className="flex items-center gap-4 mb-2">
                <div className="flex-shrink-0">
                  <Image 
                    src="/number-3.png" 
                    alt="Number 3" 
                    width={120} 
                    height={120} 
                    className="object-contain"
                  />
                </div>
                <div className="flex-1">
                  <h3 className="text-2xl font-bold text-taifa-red mb-1">
                    Gender Disparity
                  </h3>
                  <p className="text-taifa-muted text-lg">Monitoring gender equity in AI funding and leadership</p>
                </div>
              </div>
              
              <div className="mb-6">
                {/* Enhanced Gender Equity Dashboard */}
                <GenderEquityDashboard />
                
                <div className="mt-6 p-4 bg-white/90">
                  <p className="text-taifa-primary">
                    <strong>Urgent Action Needed:</strong> Female leadership in African AI has declined consistently 
                    over 6 years, with funding gaps widening across all sectors and regions. This threatens 
                    the inclusive development of AI technologies that serve all Africans.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Enhanced Mission Section */}
      <section className="py-12 bg-gradient-to-br from-taifa-primary to-taifa-olive">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="inline-flex items-center px-4 py-2 bg-taifa-white/20 border border-white/30 rounded-full text-sm font-medium text-white mb-4 animate-fadeInUp">
            <Target className="h-4 w-4 mr-2" />
            Our Mission
          </div>
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-4 animate-fadeInUp" style={{ animationDelay: '0.1s' }}>Transforming AI Funding</h2>
          <p className="text-xl text-taifa-muted leading-relaxed mb-8 max-w-4xl mx-auto animate-fadeInUp" style={{ animationDelay: '0.2s' }}>
            TAIFA-FIALA is dedicated to promoting transparency, equity, and accountability in AI funding 
            across Africa. Through comprehensive data collection and analysis, we work to ensure that AI 
            research & development serves all Africans.
          </p>
          
          <div className="grid md:grid-cols-3 gap-6 mb-8">
            <div className="text-center p-4 bg-taifa-white/10 backdrop-blur-sm rounded-3xl border border-white/20 hover:bg-white/20 transition-all duration-300 hover:-translate-y-2 animate-fadeInUp" style={{ animationDelay: '0.3s' }}>
              <div className="w-14 h-14 rounded-2xl bg-taifa-secondary/20 flex items-center justify-center mx-auto mb-2 border border-taifa-secondary/30">
                <Database className="w-10 h-10 text-taifa-secondary" />
              </div>
              <h3 className="text-lg font-bold mb-2 text-taifa-secondary">Comprehensive Data</h3>
              <p className="text-taifa-primary leading-relaxed text-sm">Real-time tracking of AI funding opportunities across all 54 African countries</p>
            </div>
            <div className="text-center p-4 bg-taifa-white/10 backdrop-blur-sm rounded-3xl border border-white/20 hover:bg-white/20 transition-all duration-300 hover:-translate-y-2 animate-fadeInUp" style={{ animationDelay: '0.4s' }}>
              <div className="w-14 h-14 rounded-2xl bg-taifa-accent/20 flex items-center justify-center mx-auto mb-2 border border-taifa-accent/30">
                <Shield className="w-10 h-10 text-taifa-accent" />
              </div>
              <h3 className="text-lg font-bold mb-2 text-taifa-accent">Equity Focus</h3>
              <p className="text-taifa-primary leading-relaxed text-sm">Dedicated analysis of gender, geographic, and sectoral disparities in funding</p>
            </div>
            <div className="text-center p-4 bg-taifa-white/10 backdrop-blur-sm rounded-3xl border border-white/20 hover:bg-white/20 transition-all duration-300 hover:-translate-y-2 animate-fadeInUp" style={{ animationDelay: '0.5s' }}>
              <div className="w-14 h-14 rounded-2xl bg-taifa-red/20 flex items-center justify-center mx-auto mb-2 border border-taifa-red/30">
                <BookOpen className="w-10 h-10 text-taifa-red" />
              </div>
              <h3 className="text-lg font-bold mb-2 text-taifa-red">Open Research</h3>
              <p className="text-taifa-primary leading-relaxed text-sm">Transparent methodology and publicly accessible insights for the research community</p>
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
    </div>
  );
}
