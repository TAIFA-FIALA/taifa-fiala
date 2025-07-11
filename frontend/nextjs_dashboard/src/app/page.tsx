import Link from 'next/link';

interface AnalyticsSummary {
  active_rfps_count: number;
  unique_funders_count: number;
  total_funding_value: number;
}

async function getAnalyticsSummary(): Promise<AnalyticsSummary | null> {
  try {
    const res = await fetch('http://localhost:8000/api/v1/analytics/summary', { cache: 'no-store' });
    if (!res.ok) {
      throw new Error(`HTTP error! status: ${res.status}`);
    }
    return res.json();
  } catch (error) {
    console.error("Failed to fetch analytics summary:", error);
    return null;
  }
}

export default async function HomePage() {
  const summary = await getAnalyticsSummary();

  return (
    <div className="min-h-[calc(100vh-64px)] flex flex-col items-center justify-center bg-gray-50 text-gray-900 dark:bg-gray-900 dark:text-gray-100">
      {/* Hero Section */}
      <section className="text-center py-20 px-4 sm:px-6 lg:px-8">
        <h1 className="text-5xl sm:text-6xl lg:text-7xl font-extrabold leading-tight mb-6">
          Empowering Africa's AI Future
        </h1>
        <p className="text-xl sm:text-2xl text-gray-600 dark:text-gray-300 mb-10 max-w-3xl mx-auto">
          Connecting African AI initiatives with global funding opportunities and fostering collaborative growth.
        </p>
        <div className="flex flex-col sm:flex-row justify-center space-y-4 sm:space-y-0 sm:space-x-4">
          <Link href="/funding" className="btn-primary text-lg px-8 py-3">
            Explore Funding
          </Link>
          <Link href="/submit-rfp" className="btn-primary bg-gray-200 text-gray-800 hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-200 dark:hover:bg-gray-600 text-lg px-8 py-3">
            Submit Your RFP
          </Link>
        </div>
      </section>

      {/* Metrics Section */}
      {summary && (
        <section className="w-full max-w-6xl mx-auto py-12 px-4 sm:px-6 lg:px-8 bg-white dark:bg-gray-800 rounded-lg shadow-lg mb-10">
          <h2 className="text-3xl font-bold text-center mb-8">Current Funding Landscape</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="flex flex-col items-center text-center p-4 bg-gray-100 dark:bg-gray-700 rounded-lg">
              <p className="text-5xl font-extrabold text-primary">{summary.active_rfps_count}</p>
              <p className="text-lg text-gray-600 dark:text-gray-300">Active RFPs</p>
            </div>
            <div className="flex flex-col items-center text-center p-4 bg-gray-100 dark:bg-gray-700 rounded-lg">
              <p className="text-5xl font-extrabold text-secondary">{summary.unique_funders_count}</p>
              <p className="text-lg text-gray-600 dark:text-gray-300">Unique Funders</p>
            </div>
            <div className="flex flex-col items-center text-center p-4 bg-gray-100 dark:bg-gray-700 rounded-lg">
              <p className="text-5xl font-extrabold text-accent">${summary.total_funding_value?.toLocaleString()}</p>
              <p className="text-lg text-gray-600 dark:text-gray-300">Total Funding Value</p>
            </div>
          </div>
        </section>
      )}

      {/* Feature Section */}
      <section className="w-full max-w-6xl mx-auto py-16 px-4 sm:px-6 lg:px-8 bg-white dark:bg-gray-800 rounded-lg shadow-lg mb-10">
        <h2 className="text-4xl font-bold text-center mb-12">Why Join Us?</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="flex flex-col items-center text-center">
            <div className="text-primary mb-4">
              {/* Icon Placeholder */}
              <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3-.895 3-2-1.343-2-3-2zM12 14c-1.657 0-3 .895-3 2v1h6v-1c0-1.105-1.343-2-3-2z"/></svg>
            </div>
            <h3 className="text-xl font-semibold mb-2">Discover Opportunities</h3>
            <p className="text-gray-600 dark:text-gray-300">Access a curated list of funding opportunities tailored for AI development in Africa.</p>
          </div>
          <div className="flex flex-col items-center text-center">
            <div className="text-primary mb-4">
              {/* Icon Placeholder */}
              <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
            </div>
            <h3 className="text-xl font-semibold mb-2">Showcase Your Work</h3>
            <p className="text-gray-600 dark:text-gray-300">Highlight your organization and projects to a global network of funders.</p>
          </div>
          <div className="flex flex-col items-center text-center">
            <div className="text-primary mb-4">
              {/* Icon Placeholder */}
              <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/></svg>
            </div>
            <h3 className="text-xl font-semibold mb-2">Collaborate & Grow</h3>
            <p className="text-gray-600 dark:text-gray-300">Connect with like-minded organizations and drive collective impact.</p>
          </div>
        </div>
      </section>
    </div>
  );
}
