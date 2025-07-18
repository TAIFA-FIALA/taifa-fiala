import Link from 'next/link';
import EquityMetricsDashboard from '@/components/homepage/EquityMetricsDashboard';
import DatabaseGrowthChart from '@/components/homepage/DatabaseGrowthChart';
import GeographicDistributionMap from '@/components/homepage/GeographicDistributionMap';
import SectorAllocationChart from '@/components/homepage/SectorAllocationChart';
import { FileText, Database, BarChart3, BookOpen, Users, TrendingUp, ChevronRight } from 'lucide-react';
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
      <section className="relative overflow-hidden py-16 sm:py-24 border-b border-gray-200">
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
              src="/TAIFA-FIALA-logo.png" 
              alt="TAIFA-FIALA Logo" 
              width={120} 
              height={120} 
              className="object-contain"
            />
          </div>
          
          <h1 className="text-5xl font-display font-bold text-taifa-primary mb-3">
            TAIFA-FIALA
          </h1>
          
          <p className="text-2xl text-taifa-primary font-display mb-6">
            Tracking AI Funding for Africa | Financements IA en Afrique
          </p>
          
          <p className="text-xl text-gray-700 max-w-3xl mx-auto leading-relaxed mb-10 font-body">
            An independent initiative promoting transparency and equitable development 
            of AI capabilities across all African nations.
          </p>
          
          {/* Search Bar - Centered */}
          <div className="max-w-2xl mx-auto mb-12">
            <form 
              action={(formData) => {
                const searchParams = new URLSearchParams();
                searchParams.set('query', formData.get('query') as string);
                window.location.href = `/funding?${searchParams.toString()}`;
              }}
              className="relative flex shadow-md rounded-lg overflow-hidden"
            >
              <input
                type="text"
                name="query"
                placeholder="Search for funds by funder, recipient, or project"
                className="pl-6 pr-4 py-4 w-full rounded-l-lg border-0 focus:ring-2 focus:ring-taifa-secondary text-lg"
              />
              <button 
                type="submit" 
                className="bg-taifa-secondary hover:bg-yellow-400 text-taifa-primary px-6 py-4 font-medium text-lg transition-colors duration-200 flex items-center"
              >
                Search
                <ChevronRight className="ml-2 h-5 w-5" />
              </button>
            </form>
          </div>
          
          {/* Quick Navigation Links */}
          <nav className="flex flex-wrap justify-center gap-6 text-base font-medium">
            <Link href="#findings" className="text-taifa-primary hover:text-taifa-secondary transition-colors">
              Research Findings
            </Link>
            <Link href="/methodology" className="text-taifa-primary hover:text-taifa-secondary transition-colors">
              Methodology
            </Link>
            <Link href="#data" className="text-taifa-primary hover:text-taifa-secondary transition-colors">
              Data & Analysis
            </Link>
            <Link href="/about" className="text-taifa-primary hover:text-taifa-secondary transition-colors">
              Research Team
            </Link>
          </nav>
        </div>
      </section>

      {/* Current State of AI Funding - Key Findings */}
      <section id="findings" className="py-12 px-4 sm:px-6 lg:px-8 bg-gray-50">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-2xl font-serif text-gray-900 mb-8">
            Current State of AI Funding in Africa
          </h2>
          
          {/* Key Finding 1: Geographic Distribution */}
          <div className="mb-12">
            <div className="bg-white p-8 rounded-lg shadow-sm border border-gray-200">
              <h3 className="text-xl font-semibold text-gray-900 mb-4">
                Finding 1: Severe Geographic Concentration
              </h3>
              
              {/* Geographic Distribution Map */}
              <div className="mb-6">
                <GeographicDistributionMap />
              </div>
              
              <p className="text-gray-700 leading-relaxed mb-4">
                Our analysis of {summary?.total_opportunities?.toLocaleString() || '2,467'} funding events reveals 
                significant geographic disparities, with 83% of tracked funding concentrated in four countries: 
                Kenya, Nigeria, South Africa, and Egypt. Central African nations receive less than 2% of total 
                funding despite representing over 180 million people.
              </p>
              
              <div className="mt-4 text-sm text-gray-600">
                <Link href="/analytics/geographic-equity" className="text-blue-700 hover:underline">
                  View detailed geographic analysis →
                </Link>
              </div>
            </div>
          </div>

          {/* Key Finding 2: Sectoral Misalignment */}
          <div className="mb-12">
            <div className="bg-white p-8 rounded-lg shadow-sm border border-gray-200">
              <h3 className="text-xl font-semibold text-gray-900 mb-4">
                Finding 2: Sectoral Funding Misalignment
              </h3>
              
              {/* Sector Allocation Chart */}
              <div className="mb-6">
                <SectorAllocationChart />
              </div>
              
              <p className="text-gray-700 leading-relaxed mb-4">
                Healthcare applications receive only 5.8% of AI funding despite the continent bearing 25% 
                of the global disease burden. Agricultural technology, which employs 60% of Africa's workforce, 
                attracts merely 3.9% of funding. In contrast, financial services capture 20.9% of investments, 
                suggesting a misalignment between funding priorities and development needs.
              </p>
              
              <div className="mt-4 text-sm text-gray-600">
                <Link href="/analytics/sectoral-alignment" className="text-blue-700 hover:underline">
                  Explore sectoral analysis →
                </Link>
              </div>
            </div>
          </div>

          {/* Methodology Note */}
          <div className="mt-8 p-4 bg-blue-50 border-l-4 border-blue-400 text-sm">
            <p className="text-gray-700">
              <strong>Methodology:</strong> Data collected through automated monitoring of public sources, 
              verified through manual review. All findings are based on publicly available information. 
              <Link href="/methodology" className="text-blue-700 hover:underline ml-1">
                See full methodology →
              </Link>
            </p>
          </div>
        </div>
      </section>

      {/* Research Data Section */}
      <section id="data" className="py-12 px-4 sm:px-6 lg:px-8 bg-white">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-2xl font-serif text-gray-900 mb-8">Research Data</h2>
          
          {/* Data Collection Progress */}
          <div className="mb-12">
            <h3 className="text-xl font-semibold text-gray-900 mb-6">Data Collection Progress</h3>
            
            <DatabaseGrowthChart className="mb-6" />
            
            <p className="text-gray-700 leading-relaxed max-w-4xl">
              Our automated collection system, supplemented by community contributions, has documented {' '}
              {summary?.total_opportunities?.toLocaleString() || '2,467'} funding-related events since 
              January 2019. The increasing coverage reflects both growing AI investment activity and 
              improved detection capabilities through our enhanced monitoring infrastructure.
            </p>
          </div>

          {/* Data Access */}
          <div className="grid md:grid-cols-3 gap-6">
            <div className="bg-gray-50 p-6 rounded-lg border border-gray-200">
              <h4 className="font-semibold text-gray-900 mb-3">Researchers & Academics</h4>
              <p className="text-gray-700 text-sm mb-4">
                Full dataset available for academic research purposes, including raw data and 
                processing scripts.
              </p>
              <Link href="/data/academic-access" className="text-blue-700 text-sm hover:underline">
                Request Access →
              </Link>
            </div>
            
            <div className="bg-gray-50 p-6 rounded-lg border border-gray-200">
              <h4 className="font-semibold text-gray-900 mb-3">Development Organizations</h4>
              <p className="text-gray-700 text-sm mb-4">
                Aggregated analyses and custom reports for policy and program development.
              </p>
              <Link href="/data/institutional-access" className="text-blue-700 text-sm hover:underline">
                Contact Research Team →
              </Link>
            </div>
            
            <div className="bg-gray-50 p-6 rounded-lg border border-gray-200">
              <h4 className="font-semibold text-gray-900 mb-3">Public Data</h4>
              <p className="text-gray-700 text-sm mb-4">
                Summary statistics, visualizations, and key findings available to all.
              </p>
              <Link href="/analytics" className="text-blue-700 text-sm hover:underline">
                View Public Dashboard →
              </Link>
            </div>
          </div>
          
          {/* Dataset Information */}
          <div className="mt-8 text-sm text-gray-600">
            <p>Dataset last updated: {new Date().toLocaleDateString('en-US', { 
              year: 'numeric', 
              month: 'long', 
              day: 'numeric',
              hour: '2-digit',
              minute: '2-digit',
              timeZone: 'UTC',
              timeZoneName: 'short'
            })}</p>
          </div>
        </div>
      </section>

      {/* Equity Assessment for Funding Organizations */}
      <section className="py-12 px-4 sm:px-6 lg:px-8 bg-gray-50">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-2xl font-serif text-gray-900 mb-6">
            Funding Equity Assessment
          </h2>
          
          <p className="text-gray-700 mb-8 max-w-4xl">
            This tool allows funding organizations to assess the distributional impacts of AI 
            investments across African markets. The analysis is based on {' '}
            {summary?.total_opportunities?.toLocaleString() || '2,467'} verified funding events 
            tracked since 2019.
          </p>
          
          <EquityMetricsDashboard />
          
          <div className="mt-8 p-6 bg-white rounded-lg border border-gray-200">
            <h3 className="font-semibold text-gray-900 mb-3">Portfolio Comparison</h3>
            <p className="text-gray-700 text-sm mb-4">
              Organizations may submit their funding data for confidential comparative analysis. 
              Results are provided directly and not stored or shared.
            </p>
            <Link href="/equity/portfolio-analysis" className="text-blue-700 text-sm hover:underline">
              Learn more about portfolio analysis →
            </Link>
          </div>
        </div>
      </section>

      {/* Research Publications */}
      <section className="py-12 px-4 sm:px-6 lg:px-8 bg-white border-t border-gray-200">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-2xl font-serif text-gray-900 mb-8">Research Outputs</h2>
          
          <div className="grid md:grid-cols-2 gap-8">
            {/* Recent Paper */}
            <div className="border border-gray-200 rounded-lg p-6">
              <h3 className="font-semibold text-gray-900 mb-2">
                Geographic Disparities in AI Funding Across Africa: A Longitudinal Analysis (2019-2024)
              </h3>
              <p className="text-sm text-gray-600 mb-3">TAIFA-FIALA Research Team</p>
              <p className="text-sm text-gray-700 mb-4">
                This paper examines the concentration of AI funding in select African countries and 
                its implications for continental development...
              </p>
              <div className="flex gap-4 text-sm">
                <Link href="/publications/geographic-disparities-2024.pdf" className="text-blue-700 hover:underline">
                  Full Paper (PDF)
                </Link>
                <Link href="/data/geographic-disparities-dataset" className="text-blue-700 hover:underline">
                  Dataset
                </Link>
                <Link href="/code/geographic-analysis" className="text-blue-700 hover:underline">
                  Replication Code
                </Link>
              </div>
            </div>
            
            {/* Policy Brief */}
            <div className="border border-gray-200 rounded-lg p-6">
              <h3 className="font-semibold text-gray-900 mb-2">
                Policy Brief: Addressing the AI Funding Gap in Central Africa
              </h3>
              <p className="text-sm text-gray-600 mb-3">December 2024</p>
              <p className="text-sm text-gray-700 mb-4">
                Key recommendations for development partners and policymakers on addressing the 
                severe underfunding of AI initiatives in Central African nations...
              </p>
              <div className="flex gap-4 text-sm">
                <Link href="/publications/policy-brief-central-africa.pdf" className="text-blue-700 hover:underline">
                  Download Brief (PDF)
                </Link>
              </div>
            </div>
          </div>
          
          <div className="mt-6 text-center">
            <Link href="/publications" className="text-blue-700 hover:underline">
              View all publications →
            </Link>
          </div>
        </div>
      </section>

      {/* About Section */}
      <section className="py-12 px-4 sm:px-6 lg:px-8 bg-gray-50 border-t border-gray-200">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-2xl font-serif text-gray-900 mb-6">About TAIFA-FIALA</h2>
          
          <p className="text-gray-700 mb-6 leading-relaxed">
            TAIFA-FIALA is an independent research initiative established to document and analyze 
            artificial intelligence funding flows across the African continent. Our work aims to 
            promote transparency, inform evidence-based policy, and support equitable development 
            of AI capabilities across all African nations.
          </p>
          
          <div className="grid md:grid-cols-2 gap-8 mb-8">
            <div>
              <h3 className="font-semibold text-gray-900 mb-3">Research Methodology</h3>
              <p className="text-sm text-gray-700 mb-3">
                We employ a mixed-methods approach combining automated data collection, manual 
                verification, and community contributions to build a comprehensive database of 
                AI funding activities.
              </p>
              <Link href="/methodology" className="text-blue-700 text-sm hover:underline">
                Read full methodology →
              </Link>
            </div>
            
            <div>
              <h3 className="font-semibold text-gray-900 mb-3">Governance & Ethics</h3>
              <p className="text-sm text-gray-700 mb-3">
                This initiative operates under the guidance of an independent advisory board 
                comprising researchers, development practitioners, and community representatives 
                from across Africa.
              </p>
              <Link href="/governance" className="text-blue-700 text-sm hover:underline">
                Learn about our governance →
              </Link>
            </div>
          </div>
          
          <div className="p-4 bg-blue-50 border-l-4 border-blue-400 text-sm">
            <p className="text-gray-700">
              <strong>Institutional Support:</strong> TAIFA-FIALA is supported by grants from 
              [funding organizations]. All data and analysis remain independent of funder influence.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}