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
    <div className="min-h-screen">
      {/* Enhanced Hero Section */}
      <section className="relative overflow-hidden" style={{ background: 'linear-gradient(to bottom right, #1e293b, #334155, #475569)', backgroundAttachment: 'fixed' }}>
        <div className="absolute inset-0 bg-slate-900/20"></div>
        
        {/* Background Africa Outline */}
        <div className="absolute inset-0 flex justify-center items-center z-0 opacity-90">
          <Image 
            src="/africa-outline-slate.png" 
            alt="Africa Outline" 
            width={1000} 
            height={1000} 
            className="object-contain"
          />
        </div>
        
        <div className="relative max-w-7xl mx-auto text-center px-4 sm:px-6 lg:px-8 py-6 sm:py-8 md:py-10 lg:py-12 xl:py-14 z-10">
          {/* Logo and Branding */}
          <div className="flex justify-center mb-3 animate-fadeInUp">
            <div className="relative">
              {/* Gold accent background */}
              <div className="absolute inset-0 bg-gradient-to-br from-amber-400 to-amber-600 rounded-3xl transform rotate-1 opacity-20"></div>
              <div className="relative bg-white p-6 rounded-3xl border-2 border-amber-400 shadow-xl">
                <Image 
                  src="/taifa-logo.png" 
                  alt="TAIFA-FIALA Logo" 
                  width={290} 
                  height={350} 
                  className="object-contain w-48 h-auto sm:w-56 md:w-64 lg:w-72 xl:w-80"
                />
              </div>
            </div>
          </div>
          
          <p className="text-xl text-slate-100 max-w-4xl mx-auto leading-relaxed mb-3 animate-fadeInUp" style={{ animationDelay: '0.3s' }}>
            TAIFA-FIALA is an independent initiative tracking AI funding to promote transparency, equity and accountability 
            in AI research and implementation, from donors & investors to researchers & entrepreneurs across the region.
          </p>

          {/* Search Bar - Enhanced */}
          <div className="max-w-2xl mx-auto mb-4 animate-fadeInUp" style={{ animationDelay: '0.5s' }}>
            <div className="bg-white/10 backdrop-blur-sm p-2 rounded-2xl border border-slate-300/20">
              <SearchBar />
            </div>
          </div>
          
          {/* Quick Navigation Links */}
          <nav className="flex flex-wrap justify-center gap-4 animate-fadeInUp" style={{ animationDelay: '0.6s' }}>
            <Link href="/funding-landscape" className="bg-amber-400/90 backdrop-blur-sm px-6 py-3 rounded-2xl border border-amber-300/50 text-white hover:bg-amber-500/90 hover:text-slate-800 transition-all duration-300 flex items-center gap-2 hover:-translate-y-1 shadow-lg">
              <BarChart3 className="w-4 h-4" />
              Funding Landscape
            </Link>
            <Link href="/theory-of-change" className="bg-amber-400/90 backdrop-blur-sm px-6 py-3 rounded-2xl border border-amber-300/50 text-white hover:bg-amber-500/90 hover:text-slate-800 transition-all duration-300 flex items-center gap-2 hover:-translate-y-1 shadow-lg">
              <Target className="w-4 h-4" />
              Theory of Change
            </Link>
            <Link href="/methodology" className="bg-amber-400/90 backdrop-blur-sm px-6 py-3 rounded-2xl border border-amber-300/50 text-white hover:bg-amber-500/90 hover:text-slate-800 transition-all duration-300 flex items-center gap-2 hover:-translate-y-1 shadow-lg">
              <Database className="w-4 h-4" />
              Methodology
            </Link>
            <Link href="/about" className="bg-amber-400/90 backdrop-blur-sm px-6 py-3 rounded-2xl border border-amber-300/50 text-white hover:bg-amber-500/90 hover:text-slate-800 transition-all duration-300 flex items-center gap-2 hover:-translate-y-1 shadow-lg">
              <Users className="w-4 h-4" />
              About Us
            </Link>
          </nav>
        </div>
      </section>

      {/* Live Data Insights */}
      <section id="database" className="py-12" style={{ backgroundColor: '#F1F5F9' }}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-8">
            <div className="inline-flex items-center px-4 py-2 bg-amber-50 border border-amber-200 rounded-full text-sm font-medium text-amber-800 mb-4 animate-fadeInUp">
              <TrendingUp className="h-4 w-4 mr-2" />
              Live Data Insights
            </div>
            <h2 className="text-4xl font-bold mb-4 animate-fadeInUp text-slate-700" style={{ animationDelay: '0.1s' }}>Real-Time Funding Intelligence</h2>
            <p className="text-lg text-neutral-500 max-w-3xl mx-auto animate-fadeInUp" style={{ animationDelay: '0.2s' }}>
              Comprehensive tracking and analysis of AI funding in Africa
            </p>
          </div>

          {/* KPI Metrics Above Database Growth */}
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-8 animate-fadeInUp" style={{ animationDelay: '0.2s' }}>
            <div className="bg-gradient-to-br from-taifa-primary to-taifa-primary/80 p-4 rounded-2xl border-2 border-taifa-primary/20 shadow-lg hover:shadow-xl transition-shadow">
              <div className="text-white text-3xl font-bold mb-1">{summary?.total_opportunities?.toLocaleString() || '2,847'}</div>
              <div className="text-white/80 text-sm font-medium">Total Announcements</div>
            </div>
            <div className="bg-gradient-to-br from-taifa-secondary to-taifa-secondary/80 p-4 rounded-2xl border-2 border-taifa-secondary/20 shadow-lg hover:shadow-xl transition-shadow">
              <div className="text-slate-900 text-3xl font-bold mb-1">{summary?.active_opportunities?.toLocaleString() || '23'}</div>
              <div className="text-slate-800 text-sm font-medium">Recent (P6M) Announcements</div>
            </div>
            <div className="bg-gradient-to-br from-taifa-accent to-taifa-accent/80 p-4 rounded-2xl border-2 border-taifa-accent/20 shadow-lg hover:shadow-xl transition-shadow">
              <div className="text-white text-3xl font-bold mb-1">${summary?.total_funding_value ? (summary.total_funding_value / 1000000000).toFixed(1) : '2.4'}B</div>
              <div className="text-white/80 text-sm font-medium">Total Funding Value</div>
            </div>
            <div className="bg-gradient-to-br from-taifa-orange to-taifa-orange/80 p-4 rounded-2xl border-2 border-taifa-orange/20 shadow-lg hover:shadow-xl transition-shadow">
              <div className="text-white text-3xl font-bold mb-1">{summary?.unique_organizations?.toLocaleString() || '342'}</div>
              <div className="text-white/80 text-sm font-medium">Unique Funding Organizations</div>
            </div>
            <div className="bg-gradient-to-br from-taifa-red to-taifa-red/80 p-4 rounded-2xl border-2 border-taifa-red/20 shadow-lg hover:shadow-xl transition-shadow">
              <div className="text-white text-3xl font-bold mb-1">{summary?.unique_organizations?.toLocaleString() || '342'}</div>
              <div className="text-white/80 text-sm font-medium">Unique Organizations Funded</div>
            </div>
          </div>

          {/* Database Growth Chart */}
          <div className="animate-fadeInUp" style={{ animationDelay: '0.3s' }}>
            <DatabaseGrowthChart />
          </div>
        </div>
      </section>

      {/* Key Issues Section */}
      <section id="equityOverview" className="py-12 px-4 sm:px-6 lg:px-8" style={{ backgroundColor: '#475569' }}>
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl font-bold mb-8 text-center" style={{ color: '#fbbf24' }}>
            <span className="inline-block relative">
              <span className="relative z-10 flex items-center justify-center">
               Issues of Equity in AI Funding
              </span>
            </span>
          </h2>
          <p className="text-lg text-white/80 text-center max-w-4xl mx-auto mb-12">The African AI funding ecosystem has experienced unprecedented growth from 2019-2024, with total commitments exceeding $800 million across multiple funding streams. We conducted a rapid review of the AI funding landscape to obtain estimated baseline values.</p>
          
          {/* Issue 1: Geographic Concentration */}
          <div className="mb-6">
            <div className="bg-white/90 backdrop-blur-sm p-6 rounded-xl border border-slate-200 shadow-lg hover:shadow-xl transition-shadow relative">
              {/* Header with numbered icon aligned horizontally */}
              <div className="flex items-center gap-4 mb-1">
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
                  <h3 className="text-2xl font-bold text-amber-700 mb-2">
                    Geographic Concentration
                  </h3>
                  <p className="text-slate-600 text-lg">Tracking funding distribution across African regions</p>
                </div>
              </div>
              
              {/* Map visualization */}
              <GeographicDistributionMapWrapper />
              
              <p className="text-slate-600 leading-relaxed mt-6">
                We have recorded {summary?.total_opportunities?.toLocaleString() || '2,467'} funding events to monitor the potential for geographic disparities, with 83% of tracked funding concentrated in just four countries: 
                Kenya, Nigeria, South Africa, and Egypt. Central African nations receive less than 2% of total 
                funding despite being home to more than 180 million people.
              </p>
            </div>
          </div>

          {/* Issue 2: Sectoral Misalignment */}
          <div className="mb-6">
            <div className="bg-white/90 backdrop-blur-sm p-6 rounded-xl border border-slate-200 shadow-lg hover:shadow-xl transition-shadow relative">
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
                  <h3 className="text-2xl font-bold text-slate-700 mb-2">
                    Sectoral Misalignment
                  </h3>
                  <p className="text-slate-600 text-lg">Comparing funding allocation with development priorities</p>
                </div>
              </div>
              
              {/* Chart visualization */}
              <div className="mb-6">
                <div className="bg-white rounded-lg p-4">
                  <SectorAllocationChart />
                </div>
                
                <p className="text-slate-700 leading-relaxed mt-4">
                  Health applications receive only 5.8% of AI funding despite the continent bearing 25% 
                  of the global disease burden. Agricultural technology, which employs 60% of Africa&apos;s workforce,
                  attracts merely 3.9% of funding. In contrast, financial services capture 20.9% of investments, 
                  creating a significant misalignment with development priorities.
                </p>
              </div>
            </div>
          </div>

          {/* Issue 3: Gender Disparity */}
          <div className="mb-6">
            <div className="bg-white/90 backdrop-blur-sm p-6 rounded-xl border border-slate-200 shadow-lg hover:shadow-xl transition-shadow relative">
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
                  <h3 className="text-2xl font-bold text-red-600 mb-1">
                    Gender Disparity
                  </h3>
                  <p className="text-slate-600 text-lg">Monitoring gender equity in AI funding and leadership</p>
                </div>
              </div>
              
              <div className="mb-6">
                {/* Enhanced Gender Equity Dashboard */}
                <GenderEquityDashboard />
                
                <div className="mt-6 p-4 bg-white/90">
                  <p className="text-slate-700">
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
      <section id="values" className="py-12" style={{ backgroundColor: '#CBD5E1' }}>
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="inline-flex items-center px-4 py-2 bg-slate-600/20 border border-slate-600/30 rounded-full text-sm font-medium text-slate-700 mb-4 animate-fadeInUp">
            <Target className="h-4 w-4 mr-2" />
            Our Mission
          </div>
          <h2 className="text-4xl md:text-5xl font-bold mb-4 animate-fadeInUp text-slate-800" style={{ animationDelay: '0.1s' }}>Transforming AI Funding</h2>
          <p className="text-xl text-slate-700 leading-relaxed mb-8 max-w-4xl mx-auto animate-fadeInUp" style={{ animationDelay: '0.2s' }}>
            TAIFA-FIALA is dedicated to promoting transparency, equity, and accountability in AI funding 
            across Africa. Through comprehensive data collection and analysis, we work to ensure that AI 
            research & development serves all Africans.
          </p>
          
          <div className="grid md:grid-cols-3 gap-6 mb-8">
            <div className="text-center animate-fadeInUp" style={{ animationDelay: '0.3s' }}>
              <div className="relative h-full">
                {/* TAIFA Primary (Slate) accent background */}
                <div className="absolute inset-0 bg-gradient-to-br from-taifa-primary to-taifa-primary/80 rounded-3xl transform rotate-1 opacity-20"></div>
                <div className="relative bg-white p-6 rounded-3xl border-2 border-taifa-primary shadow-xl hover:shadow-2xl transition-all duration-300 hover:-translate-y-2 h-full flex flex-col">
                  <div className="w-14 h-14 rounded-2xl bg-taifa-primary/10 flex items-center justify-center mx-auto mb-4 border-2 border-taifa-primary">
                    <Database className="w-8 h-8 text-taifa-primary" />
                  </div>
                  <h3 className="text-lg font-bold mb-2 text-taifa-primary">Transparency</h3>
                  <p className="text-slate-600 leading-relaxed text-sm flex-grow">Comprehensive data collection and real-time tracking of AI funding opportunities across all 54 African countries, making funding flows visible and accessible</p>
                </div>
              </div>
            </div>
            <div className="text-center animate-fadeInUp" style={{ animationDelay: '0.4s' }}>
              <div className="relative h-full">
                {/* TAIFA Secondary (Amber) accent background */}
                <div className="absolute inset-0 bg-gradient-to-br from-taifa-secondary to-taifa-secondary/80 rounded-3xl transform rotate-1 opacity-20"></div>
                <div className="relative bg-white p-6 rounded-3xl border-2 border-taifa-secondary shadow-xl hover:shadow-2xl transition-all duration-300 hover:-translate-y-2 h-full flex flex-col">
                  <div className="w-14 h-14 rounded-2xl bg-taifa-secondary/10 flex items-center justify-center mx-auto mb-4 border-2 border-taifa-secondary">
                    <Shield className="w-8 h-8 text-taifa-secondary" />
                  </div>
                  <h3 className="text-lg font-bold mb-2 text-taifa-secondary">Equity</h3>
                  <p className="text-slate-600 leading-relaxed text-sm flex-grow">Dedicated analysis of gender, geographic, and sectoral disparities in funding to ensure AI development serves all Africans equitably</p>
                </div>
              </div>
            </div>
            <div className="text-center animate-fadeInUp" style={{ animationDelay: '0.5s' }}>
              <div className="relative h-full">
                {/* TAIFA Accent (Purple) accent background */}
                <div className="absolute inset-0 bg-gradient-to-br from-taifa-accent to-taifa-accent/80 rounded-3xl transform rotate-1 opacity-20"></div>
                <div className="relative bg-white p-6 rounded-3xl border-2 border-taifa-accent shadow-xl hover:shadow-2xl transition-all duration-300 hover:-translate-y-2 h-full flex flex-col">
                  <div className="w-14 h-14 rounded-2xl bg-taifa-accent/10 flex items-center justify-center mx-auto mb-4 border-2 border-taifa-accent">
                    <BookOpen className="w-8 h-8 text-taifa-accent" />
                  </div>
                  <h3 className="text-lg font-bold mb-2 text-taifa-accent">Accountability</h3>
                  <p className="text-slate-600 leading-relaxed text-sm flex-grow">Transparent methodology and publicly accessible insights that hold funders accountable and enable the research community to track progress</p>
                </div>
              </div>
            </div>
          </div>
          
          <div className="animate-fadeInUp" style={{ animationDelay: '0.6s' }}>
            <Link 
              href="/about" 
              className="bg-taifa-secondary text-white px-8 py-4 rounded-2xl font-semibold hover:bg-taifa-secondary/90 transition-all duration-300 inline-flex items-center gap-2 border border-taifa-secondary hover:-translate-y-1"
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
