import { GetServerSideProps } from 'next';
import Link from 'next/link';
import { ShieldCheck, BarChart, UploadCloud } from 'lucide-react';

// Placeholder for data fetching logic
async function getEquityData() {
  // In a real application, you would fetch this data from your API
  return {
    recordCount: 2467,
    herfindahlIndex: 0.73,
  };
}

export default async function EquityAssessmentPage() {
  const data = await getEquityData();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Page Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <h1 className="text-3xl font-serif text-gray-900">
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
            <h2 className="text-2xl font-serif text-gray-900 mb-6">Assessment Metrics</h2>
            <div className="grid md:grid-cols-3 gap-6">
              {/* Geographic Equity */}
              <div className="bg-white p-6 rounded-lg shadow-sm border">
                <h3 className="font-semibold text-gray-900 mb-3">Geographic Equity</h3>
                <p className="text-4xl font-bold text-blue-700">{data.herfindahlIndex.toFixed(2)}</p>
                <p className="text-sm text-gray-600">Herfindahl-Hirschman Index</p>
                <p className="text-xs text-gray-500 mt-2">High concentration (0 = perfect distribution, 1 = complete concentration)</p>
              </div>
              {/* Sectoral Alignment */}
              <div className="bg-white p-6 rounded-lg shadow-sm border">
                <h3 className="font-semibold text-gray-900 mb-3">Sectoral Alignment</h3>
                <div className="h-24 bg-gray-100 rounded flex items-center justify-center">
                  <p className="text-gray-500">Alignment Matrix Placeholder</p>
                </div>
              </div>
              {/* Demographic Inclusion */}
              <div className="bg-white p-6 rounded-lg shadow-sm border">
                <h3 className="font-semibold text-gray-900 mb-3">Demographic Inclusion</h3>
                <div className="h-24 bg-gray-100 rounded flex items-center justify-center">
                  <p className="text-gray-500">Inclusion Metrics Placeholder</p>
                </div>
              </div>
            </div>
          </div>

          {/* Portfolio Analysis */}
          <div className="bg-white p-8 rounded-lg shadow-sm border border-gray-200">
            <h2 className="text-2xl font-serif text-gray-900 mb-4">Portfolio Comparison</h2>
            <p className="text-gray-700 mb-6 max-w-4xl">
              Organizations may submit their funding data for confidential 
              comparative analysis. Results are provided directly and not 
              stored or shared.
            </p>
            <div>
              <Link href="/equity/portfolio-analysis" className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-blue-700 hover:bg-blue-800">
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