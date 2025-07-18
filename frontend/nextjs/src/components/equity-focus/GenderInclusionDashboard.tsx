import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import dynamic from 'next/dynamic';
import { FileText, Target, Users } from 'lucide-react';

// Dynamically import Chart.js to avoid SSR issues
const PieChart = dynamic(() => import('react-chartjs-2').then((mod) => mod.Pie), {
  ssr: false,
  loading: () => <div className="h-64 bg-gray-50 rounded-lg flex items-center justify-center">Loading chart...</div>,
});

const LineChart = dynamic(() => import('react-chartjs-2').then((mod) => mod.Line), {
  ssr: false,
  loading: () => <div className="h-64 bg-gray-50 rounded-lg flex items-center justify-center">Loading chart...</div>,
});

// Register Chart.js components
const registerChartComponents = async () => {
  const { 
    Chart, 
    ArcElement,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title, 
    Tooltip, 
    Legend,
    Filler
  } = await import('chart.js');
  
  Chart.register(
    ArcElement,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
    Filler
  );
};

interface GenderData {
  gender: string;
  funding_percentage: number;
  project_count: number;
}

interface TrendData {
  year: number;
  female_led_percentage: number;
  youth_led_percentage: number;
  rural_percentage: number;
}

interface FeaturedFounder {
  name: string;
  organization: string;
  funding_received: number;
  image_url: string;
  country: string;
  sector: string;
  story_snippet: string;
  link: string;
}

interface GenderInclusionDashboardProps {
  className?: string;
}

export default function GenderInclusionDashboard({ className = '' }: GenderInclusionDashboardProps) {
  const [genderData, setGenderData] = useState<GenderData[]>([]);
  const [trendData, setTrendData] = useState<TrendData[]>([]);
  const [featuredFounders, setFeaturedFounders] = useState<FeaturedFounder[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    registerChartComponents();
    
    const fetchData = async () => {
      try {
        setLoading(true);
        // In production, replace with actual API endpoints
        const [genderRes, trendRes, foundersRes] = await Promise.all([
          fetch('http://localhost:8000/api/v1/analytics/gender-distribution'),
          fetch('http://localhost:8000/api/v1/analytics/inclusion-trends'),
          fetch('http://localhost:8000/api/v1/analytics/featured-founders')
        ]);
        
        if (!genderRes.ok || !trendRes.ok || !foundersRes.ok) {
          throw new Error(`HTTP error when fetching data`);
        }
        
        const genderData = await genderRes.json();
        const trendData = await trendRes.json();
        const foundersData = await foundersRes.json();
        
        setGenderData(genderData);
        setTrendData(trendData);
        setFeaturedFounders(foundersData);
      } catch (error) {
        console.error('Failed to fetch inclusion data:', error);
        setError('Failed to load inclusion data.');
        
        // Fallback data for demonstration
        setGenderData([
          { gender: 'Male-led', funding_percentage: 82, project_count: 412 },
          { gender: 'Female-led', funding_percentage: 2, project_count: 38 },
          { gender: 'Mixed teams', funding_percentage: 16, project_count: 85 },
        ]);
        
        setTrendData([
          { year: 2020, female_led_percentage: 1.2, youth_led_percentage: 5.8, rural_percentage: 0.9 },
          { year: 2021, female_led_percentage: 1.5, youth_led_percentage: 7.2, rural_percentage: 1.1 },
          { year: 2022, female_led_percentage: 1.7, youth_led_percentage: 8.5, rural_percentage: 1.4 },
          { year: 2023, female_led_percentage: 1.9, youth_led_percentage: 10.1, rural_percentage: 1.8 },
          { year: 2024, female_led_percentage: 2.0, youth_led_percentage: 12.4, rural_percentage: 2.3 },
        ]);
        
        setFeaturedFounders([
          {
            name: "Aisha Pandor",
            organization: "SweepSouth",
            funding_received: 7000000,
            image_url: "https://placeholder.co/400",
            country: "South Africa",
            sector: "AI Services",
            story_snippet: "Co-founded SweepSouth, an online platform connecting domestic workers with homeowners.",
            link: "/founders/aisha-pandor"
          },
          {
            name: "Charlette N'Guessan",
            organization: "BACE Group",
            funding_received: 250000,
            image_url: "https://placeholder.co/400",
            country: "Ghana",
            sector: "AI Facial Recognition",
            story_snippet: "First woman to win the Royal Academy of Engineering's Africa Prize for Engineering Innovation.",
            link: "/founders/charlette-nguessan"
          },
          {
            name: "Moulaye Taboure",
            organization: "Afrikrea",
            funding_received: 2500000,
            image_url: "https://placeholder.co/400",
            country: "Ivory Coast",
            sector: "E-commerce",
            story_snippet: "Founded the leading African e-commerce platform for African designers and makers.",
            link: "/founders/moulaye-taboure"
          }
        ]);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Pie chart data
  const genderPieData = {
    labels: genderData.map(item => item.gender),
    datasets: [
      {
        data: genderData.map(item => item.funding_percentage),
        backgroundColor: ['#1F2A44', '#4B9CD3', '#F0E68C'],
        borderWidth: 0,
      },
    ],
  };

  // Line chart data for trends
  const trendLineData = {
    labels: trendData.map(item => item.year),
    datasets: [
      {
        label: 'Female-led Projects',
        data: trendData.map(item => item.female_led_percentage),
        borderColor: '#4B9CD3',
        backgroundColor: 'rgba(75, 156, 211, 0.1)',
        fill: true,
        tension: 0.4
      },
      {
        label: 'Youth-led Projects',
        data: trendData.map(item => item.youth_led_percentage),
        borderColor: '#F0E68C',
        backgroundColor: 'rgba(240, 230, 140, 0.1)',
        fill: true,
        tension: 0.4
      },
      {
        label: 'Rural Projects',
        data: trendData.map(item => item.rural_percentage),
        borderColor: '#1F2A44',
        backgroundColor: 'rgba(31, 42, 68, 0.1)',
        fill: true,
        tension: 0.4
      }
    ],
  };

  // Chart options
  const pieOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'right' as const,
      },
      title: {
        display: true,
        text: 'Funding Distribution by Gender',
      },
    },
  };

  const lineOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'Inclusion Trends (2020-2024)',
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: 'Percentage of Total Funding (%)'
        }
      }
    }
  };

  if (loading) {
    return <div className="flex justify-center items-center h-64 bg-[#F0E68C] bg-opacity-10 rounded-lg text-[#1F2A44]">Loading inclusion data...</div>;
  }

  if (error) {
    return (
      <div className="flex justify-center items-center h-64 bg-[#1F2A44] bg-opacity-10 rounded-lg text-[#1F2A44]">
        {error} Please try again later.
      </div>
    );
  }

  return (
    <div className={`${className} bg-white rounded-xl shadow-lg p-4`}>
      <div className="flex flex-col md:flex-row justify-between items-center mb-6">
        <h2 className="text-xl font-bold text-gray-800 mb-2 md:mb-0">Gender & Inclusion Analytics</h2>
        <div className="flex items-center space-x-2">
          <Link 
            href="/funding?gender=female-led"
            className="bg-pink-100 hover:bg-pink-200 text-pink-700 text-sm font-medium py-2 px-4 rounded transition-colors"
          >
            View Female-led Opportunities
          </Link>
          <Link 
            href="/funding?demographic=youth"
            className="bg-blue-100 hover:bg-blue-200 text-blue-700 text-sm font-medium py-2 px-4 rounded transition-colors"
          >
            View Youth Opportunities
          </Link>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
        {/* Charts section */}
        <div className="lg:col-span-3 space-y-6">
          {/* Key stats */}
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-pink-50 p-4 rounded-lg border border-pink-100">
              <div className="text-xs text-gray-500 uppercase">Female-led funding</div>
              <div className="text-2xl font-bold text-pink-600 mt-1">
                {genderData.find(d => d.gender === 'Female-led')?.funding_percentage || 2}%
              </div>
              <div className="text-xs text-red-500 mt-1">
                23% below global average
              </div>
            </div>
            
            <div className="bg-blue-50 p-4 rounded-lg border border-blue-100">
              <div className="text-xs text-gray-500 uppercase">Youth-led funding</div>
              <div className="text-2xl font-bold text-blue-600 mt-1">
                {trendData[trendData.length - 1]?.youth_led_percentage || 12.4}%
              </div>
              <div className="text-xs text-green-500 mt-1">
                +2.3% from last year
              </div>
            </div>
            
            <div className="bg-purple-50 p-4 rounded-lg border border-purple-100">
              <div className="text-xs text-gray-500 uppercase">Rural funding</div>
              <div className="text-2xl font-bold text-purple-600 mt-1">
                {trendData[trendData.length - 1]?.rural_percentage || 2.3}%
              </div>
              <div className="text-xs text-red-500 mt-1">
                18% below target
              </div>
            </div>
          </div>

          {/* Pie Chart */}
          <div className="bg-gray-50 p-4 rounded-lg border border-gray-100 h-64">
            <PieChart data={genderPieData} options={pieOptions} />
          </div>
          
          {/* Line Chart */}
          <div className="bg-gray-50 p-4 rounded-lg border border-gray-100 h-64">
            <LineChart data={trendLineData} options={lineOptions} />
          </div>
        </div>
        
        {/* Success Stories Section */}
        <div className="lg:col-span-2">
          <div className="bg-gradient-to-br from-purple-100 to-pink-100 p-4 rounded-lg border border-pink-200">
            <h3 className="font-bold text-gray-800 mb-3">Featured Success Stories</h3>
            <div className="space-y-4">
              {featuredFounders.map((founder) => (
                <div key={founder.name} className="bg-white rounded-lg shadow p-3 flex space-x-3">
                  <div className="flex-shrink-0">
                    <div className="w-16 h-16 bg-gray-200 rounded-full overflow-hidden">
                      <img src={founder.image_url} alt={founder.name} className="w-full h-full object-cover" />
                    </div>
                  </div>
                  <div className="flex-grow">
                    <h4 className="font-medium text-gray-800">{founder.name}</h4>
                    <div className="text-sm text-gray-600">{founder.organization}</div>
                    <div className="flex items-center mt-1">
                      <span className="text-xs bg-blue-100 text-blue-600 px-2 py-0.5 rounded">{founder.country}</span>
                      <span className="text-xs bg-green-100 text-green-600 px-2 py-0.5 rounded ml-2">{founder.sector}</span>
                    </div>
                    <div className="text-xs text-gray-500 mt-1">
                      Received ${(founder.funding_received / 1000000).toFixed(1)}M in funding
                    </div>
                  </div>
                </div>
              ))}
            </div>
            
            <div className="mt-4">
              <h4 className="text-sm font-medium text-gray-700 mb-2">Inclusion Resources</h4>
              <div className="space-y-2">
                <Link href="/resources/gender-equity" className="text-xs bg-white text-purple-600 px-3 py-1.5 rounded block hover:bg-purple-50 transition-colors">
                  <FileText className="w-4 h-4 inline mr-1" />
                  Template: Gender-responsive Grant Applications
                </Link>
                <Link href="/resources/youth-funding" className="text-xs bg-white text-purple-600 px-3 py-1.5 rounded block hover:bg-purple-50 transition-colors">
                  <Target className="w-4 h-4 inline mr-1" />
                  Guide: Youth-led Project Development
                </Link>
                <Link href="/mentorship" className="text-xs bg-white text-purple-600 px-3 py-1.5 rounded block hover:bg-purple-50 transition-colors">
                  <Users className="w-4 h-4 inline mr-1" />
                  Connect with Female Founder Mentors
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Actionable Insights */}
      <div className="mt-6 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <h3 className="text-lg font-medium text-yellow-700 flex items-center gap-2">
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2h-1v-3a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
          Actionable Insights
        </h3>
        <ul className="mt-2 space-y-2 text-sm text-gray-700">
          <li className="flex items-start space-x-2">
            <svg className="w-4 h-4 text-yellow-500 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
            <span><strong>Female-led projects</strong> are 3.2x less likely to receive second-round funding. Consider targeted follow-on funding initiatives.</span>
          </li>
          <li className="flex items-start space-x-2">
            <svg className="w-4 h-4 text-yellow-500 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
            <span>Applications with <strong>gender-diverse teams</strong> show 28% higher success rates. Encourage collaborative proposals.</span>
          </li>
          <li className="flex items-start space-x-2">
            <svg className="w-4 h-4 text-yellow-500 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
            <span><strong>Rural projects</strong> have the highest impact scores but lowest application rates. Consider focused rural outreach.</span>
          </li>
        </ul>
      </div>
    </div>
  );
}
