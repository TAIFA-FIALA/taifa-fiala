import { GetServerSideProps } from 'next';
import GeographicAnalysis from '@/components/analytics/GeographicAnalysis';
import TemporalAnalysis from '@/components/analytics/TemporalAnalysis';
import NetworkAnalysis from '@/components/analytics/NetworkAnalysis';

// Placeholder for data fetching logic
async function getAnalyticsData() {
  // In a real application, you would fetch this data from your API
  return {
    lastUpdated: new Date().toISOString(),
    geographicData: {
      totalTracked: 847000000,
      fundingEvents: 2467,
      // ... more data
    },
    temporalData: {
      // ... data for timeline
    },
    networkData: {
      // ... data for graph
    }
  };
}

export default async function AnalyticsDashboardPage() {
  const data = await getAnalyticsData();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Page Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <h1 className="text-3xl font-serif text-gray-900">
            AI Funding Analysis for Africa
          </h1>
          <p className="mt-1 text-sm text-gray-500">
            Dataset last updated: {new Date(data.lastUpdated).toLocaleString('en-US', { dateStyle: 'long', timeStyle: 'short' })}
          </p>
        </div>
      </header>

      {/* Main Content */}
      <main className="py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            
            {/* Geographic Analysis - Column 1 */}
            <GeographicAnalysis />

            {/* Temporal and Network Analysis - Column 2 */}
            <div className="space-y-8">
              <TemporalAnalysis />
              <NetworkAnalysis />
            </div>

          </div>
        </div>
      </main>
    </div>
  );
}
