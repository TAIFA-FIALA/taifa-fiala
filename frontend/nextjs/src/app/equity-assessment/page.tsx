import Link from 'next/link';
import { UploadCloud, Users, TrendingDown, AlertTriangle } from 'lucide-react';
import StatCard from '@/components/equity-assessment/StatCard';

// Placeholder for data fetching logic
async function getEquityData() {
  // In a real application, you would fetch this data from your API
  return {
    recordCount: 2467,
    herfindahlIndex: 0.73,
    genderMetrics: {
      femaleLedFundingPercentage: 23,
      averageFundingGap: 2100000,
      femaleLeadershipPercentage: 15,
      femaleFounderGrowthRate: 8.5,
      sectorDisparities: {
        'AI/ML': { male: 78, female: 22 },
        'FinTech': { male: 65, female: 35 },
        'HealthTech': { male: 58, female: 42 },
        'AgriTech': { male: 72, female: 28 }
      }
    }
  };
}

export default async function EquityAssessmentPage() {
  const data = await getEquityData();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Page Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <h1 className="text-3xl font-display text-gray-900">
            Funding Equity Assessment
          </h1>
        </div>
      </header>

      {/* Main Content */}
      <main className="py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          
          {/* Introduction */}
          <div className="bg-white p-8 rounded-lg shadow-sm border border-gray-200 mb-8">
            <p className="text-lg text-gray-700 leading-relaxed">
              This tool allows funding organizations to assess the distributional 
              impacts of AI investments across African markets. The analysis is 
              based on {data.recordCount.toLocaleString()} verified funding events tracked since 2019.
            </p>
          </div>

          {/* Assessment Metrics */}
          <div className="mb-8">
            <h2 className="text-2xl font-display text-gray-900 mb-6">Assessment Metrics</h2>
            <div className="grid md:grid-cols-3 gap-6">
              <StatCard
                title="Geographic Equity"
                value={data.herfindahlIndex.toFixed(2)}
                description="Herfindahl-Hirschman Index"
                valueClassName="text-blue-700"
                className="animate-fadeInUp"
              />
              <StatCard
                title="Gender Equity"
                value={`${data.genderMetrics.femaleLedFundingPercentage}%`}
                description="Female-led startups funded"
                valueClassName="text-red-700"
                className="animate-fadeInUp"
              />
              <StatCard
                title="Average Funding Gap"
                value={`$${(data.genderMetrics.averageFundingGap / 1000000).toFixed(1)}M`}
                description="Male vs Female-led ventures"
                valueClassName="text-orange-700"
                className="animate-fadeInUp"
              />
            </div>
          </div>

          {/* Gender Disparity Deep Dive */}
          <div className="mb-8">
            <h2 className="text-2xl font-display text-gray-900 mb-6 flex items-center gap-3">
              <Users className="w-6 h-6 text-red-600" />
              Gender Disparity Analysis
            </h2>
            
            {/* Alert Banner */}
            <div className="bg-red-50 border border-red-200 rounded-lg p-6 mb-6">
              <div className="flex items-start gap-3">
                <AlertTriangle className="w-6 h-6 text-red-600 flex-shrink-0 mt-1" />
                <div>
                  <h3 className="font-semibold text-red-900 mb-2">Critical Gender Gap Identified</h3>
                  <p className="text-red-800">
                    Female-led AI startups in Africa receive only {data.genderMetrics.femaleLedFundingPercentage}% of total funding, 
                    despite representing a growing segment of the entrepreneurial ecosystem. This disparity is most pronounced 
                    in technical AI sectors and early-stage funding rounds.
                  </p>
                </div>
              </div>
            </div>

            {/* Key Metrics Grid */}
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              <StatCard
                title="Female-led funding share"
                value={`${data.genderMetrics.femaleLedFundingPercentage}%`}
                description=""
                Icon={TrendingDown}
                iconClassName="text-red-600"
                valueClassName="text-red-700 text-2xl"
                className="animate-fadeInUp text-center"
              />
              <StatCard
                title="Female AI leadership"
                value={`${data.genderMetrics.femaleLeadershipPercentage}%`}
                description=""
                Icon={Users}
                iconClassName="text-orange-600"
                valueClassName="text-orange-700 text-2xl"
                className="animate-fadeInUp text-center"
              />
              <StatCard
                title="Average funding gap"
                value={`$${(data.genderMetrics.averageFundingGap / 1000000).toFixed(1)}M`}
                description=""
                Icon={TrendingDown}
                iconClassName="text-red-600"
                valueClassName="text-red-700 text-2xl"
                className="animate-fadeInUp text-center"
              />
              <StatCard
                title="Female founder growth"
                value={`+${data.genderMetrics.femaleFounderGrowthRate}%`}
                description=""
                Icon={Users}
                iconClassName="text-green-600"
                valueClassName="text-green-700 text-2xl"
                className="animate-fadeInUp text-center"
              />
            </div>

            {/* Sector Analysis */}
            <div className="bg-white p-6 rounded-lg shadow-sm border mb-6">
              <h3 className="font-semibold text-gray-900 mb-4">Gender Distribution by AI Sector</h3>
              <div className="space-y-4">
                {Object.entries(data.genderMetrics.sectorDisparities).map(([sector, distribution]) => (
                  <div key={sector}>
                    <div className="flex justify-between items-center mb-2">
                      <span className="font-medium text-gray-900">{sector}</span>
                      <span className="text-sm text-gray-600">
                        {distribution.female}% female-led
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-3">
                      <div 
                        className="bg-gradient-to-r from-pink-500 to-purple-500 h-3 rounded-full"
                        style={{ width: `${distribution.female}%` }}
                      ></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Recommendations */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
              <h3 className="font-semibold text-blue-900 mb-4">Recommendations for Addressing Gender Disparities</h3>
              <ul className="space-y-3 text-blue-800">
                <li className="flex items-start gap-2">
                  <span className="w-2 h-2 bg-blue-600 rounded-full mt-2 flex-shrink-0"></span>
                  <span>Implement gender-inclusive funding criteria and evaluation processes</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="w-2 h-2 bg-blue-600 rounded-full mt-2 flex-shrink-0"></span>
                  <span>Create dedicated funding tracks for female-led AI ventures</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="w-2 h-2 bg-blue-600 rounded-full mt-2 flex-shrink-0"></span>
                  <span>Establish mentorship programs connecting female entrepreneurs with industry leaders</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="w-2 h-2 bg-blue-600 rounded-full mt-2 flex-shrink-0"></span>
                  <span>Increase female representation in investment decision-making roles</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="w-2 h-2 bg-blue-600 rounded-full mt-2 flex-shrink-0"></span>
                  <span>Provide technical training and capacity building programs for women in AI</span>
                </li>
              </ul>
            </div>
          </div>

          {/* Portfolio Analysis */}
          <div className="bg-white p-8 rounded-lg shadow-sm border border-gray-200">
            <h2 className="text-2xl font-display text-gray-900 mb-4">Portfolio Comparison</h2>
            <p className="text-gray-700 mb-6 max-w-4xl">
              Organizations may submit their funding data for confidential 
              comparative analysis. Results are provided directly and not 
              stored or shared.
            </p>
            <div>
              <Link href="/equity/portfolio-analysis" className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-taifa-primary hover:bg-taifa-secondary">
                <UploadCloud className="mr-3 h-5 w-5" />
                Upload Portfolio Data (CSV)
              </Link>
            </div>
          </div>

        </div>
      </main>
    </div>
  );
}