import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import dynamic from 'next/dynamic';

// Dynamically import Chart.js to avoid SSR issues
const Chart = dynamic(() => import('react-chartjs-2').then((mod) => mod.Bar), {
  ssr: false,
  loading: () => <div className="h-64 bg-gray-50 rounded-lg flex items-center justify-center">Loading chart...</div>,
});

// We'll need to register Chart.js components
const registerChartComponents = async () => {
  const { 
    Chart, 
    CategoryScale, 
    LinearScale, 
    BarElement, 
    Title, 
    Tooltip, 
    Legend 
  } = await import('chart.js');
  
  Chart.register(
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend
  );
};

interface FundingStage {
  stage: string;
  percentage: number;
  description: string;
  typical_range: string;
  projects_count: number;
}

interface OpportunityMatch {
  id: number;
  title: string;
  organization: string;
  amount_usd: number;
  stage: string;
  deadline: string;
  link: string;
}

interface CollaborationSuggestion {
  id: number;
  title: string;
  project_count: number;
  combined_funding_potential: number;
  complementary_skills: string[];
}

interface FundingLifecycleSupportProps {
  className?: string;
}

export default function FundingLifecycleSupport({ className = '' }: FundingLifecycleSupportProps) {
  const [fundingStages, setFundingStages] = useState<FundingStage[]>([]);
  const [opportunities, setOpportunities] = useState<OpportunityMatch[]>([]);
  const [collaborations, setCollaborations] = useState<CollaborationSuggestion[]>([]);
  const [selectedStage, setSelectedStage] = useState<string>('seed');
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    registerChartComponents();
    
    const fetchLifecycleData = async () => {
      try {
        setLoading(true);
        // In production, replace with actual API endpoints
        const [stagesRes, oppsRes, collabRes] = await Promise.all([
          fetch('http://localhost:8000/api/v1/analytics/funding-stages'),
          fetch(`http://localhost:8000/api/v1/opportunities/stage-matching?stage=${selectedStage}`),
          fetch('http://localhost:8000/api/v1/analytics/collaboration-suggestions')
        ]);
        
        if (!stagesRes.ok || !oppsRes.ok || !collabRes.ok) {
          throw new Error(`HTTP error when fetching lifecycle data`);
        }
        
        const stagesData = await stagesRes.json();
        const oppsData = await oppsRes.json();
        const collabData = await collabRes.json();
        
        setFundingStages(stagesData);
        setOpportunities(oppsData);
        setCollaborations(collabData);
      } catch (error) {
        console.error('Failed to fetch lifecycle data:', error);
        setError('Failed to load funding lifecycle data.');
        
        // Fallback data for demonstration
        setFundingStages([
          { 
            stage: 'pre-seed', 
            percentage: 8, 
            description: 'Concept development and initial prototype', 
            typical_range: '$10K - $50K',
            projects_count: 24
          },
          { 
            stage: 'seed', 
            percentage: 69, 
            description: 'Early-stage funding to prove business viability', 
            typical_range: '$50K - $500K',
            projects_count: 187
          },
          { 
            stage: 'series-a', 
            percentage: 15, 
            description: 'First significant round to scale business operations', 
            typical_range: '$500K - $2M',
            projects_count: 42
          },
          { 
            stage: 'series-b', 
            percentage: 5, 
            description: 'Funding to expand market reach and scale further', 
            typical_range: '$2M - $10M',
            projects_count: 14
          },
          { 
            stage: 'growth', 
            percentage: 3, 
            description: 'Significant capital to accelerate growth and expansion', 
            typical_range: '$10M+',
            projects_count: 8
          }
        ]);
        
        setOpportunities([
          {
            id: 1,
            title: "AI Innovation Challenge Grant",
            organization: "African Development Bank",
            amount_usd: 250000,
            stage: "seed",
            deadline: "2025-09-15",
            link: "/funding/123"
          },
          {
            id: 2,
            title: "Tech Startup Accelerator Program",
            organization: "Google for Startups",
            amount_usd: 100000,
            stage: "seed",
            deadline: "2025-08-30",
            link: "/funding/124"
          },
          {
            id: 3,
            title: "Pan-African AI Research Grant",
            organization: "Microsoft",
            amount_usd: 175000,
            stage: "seed",
            deadline: "2025-10-01",
            link: "/funding/125"
          }
        ]);
        
        setCollaborations([
          {
            id: 1,
            title: "Healthcare AI Consortium",
            project_count: 4,
            combined_funding_potential: 750000,
            complementary_skills: ["Medical Research", "AI Development", "Data Science", "Regulatory Compliance"]
          },
          {
            id: 2,
            title: "Rural Agritech Alliance",
            project_count: 3,
            combined_funding_potential: 500000,
            complementary_skills: ["Agricultural Science", "Mobile Development", "Rural Distribution", "IoT"]
          },
          {
            id: 3,
            title: "Climate AI Network",
            project_count: 5,
            combined_funding_potential: 1200000,
            complementary_skills: ["Environmental Science", "Machine Learning", "Satellite Imagery", "Policy"]
          }
        ]);
      } finally {
        setLoading(false);
      }
    };

    fetchLifecycleData();
  }, [selectedStage]);

  // Prepare chart data
  const chartData = {
    labels: fundingStages.map(item => item.stage.toUpperCase()),
    datasets: [
      {
        label: 'Projects (%)',
        data: fundingStages.map(item => item.percentage),
        backgroundColor: fundingStages.map(item => 
          item.stage === 'seed' ? 'rgba(239, 68, 68, 0.8)' : 'rgba(59, 130, 246, 0.5)'
        ),
        borderColor: fundingStages.map(item => 
          item.stage === 'seed' ? 'rgba(239, 68, 68, 1)' : 'rgba(59, 130, 246, 1)'
        ),
        borderWidth: 1,
      }
    ]
  };

  // Chart options
  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      title: {
        display: true,
        text: 'Project Distribution by Funding Stage',
      },
      tooltip: {
        callbacks: {
          label: function(context: any) {
            const index = context.dataIndex;
            const stage = fundingStages[index];
            return [
              `Projects: ${stage.percentage}% (${stage.projects_count})`,
              `Range: ${stage.typical_range}`
            ];
          }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: 'Percentage of Projects (%)'
        }
      }
    }
  };

  if (loading) {
    return <div className="flex justify-center items-center h-64 bg-gray-50 rounded-lg">Loading funding lifecycle data...</div>;
  }

  if (error) {
    return (
      <div className="flex justify-center items-center h-64 bg-red-50 rounded-lg text-red-500">
        {error} Please try again later.
      </div>
    );
  }

  return (
    <div className={`${className} bg-white rounded-xl shadow-lg p-4`}>
      <div className="flex flex-col md:flex-row justify-between items-center mb-6">
        <h2 className="text-xl font-bold text-gray-800 mb-2 md:mb-0">Funding Lifecycle Support</h2>
        <div className="bg-red-50 px-4 py-2 rounded-lg border border-red-100">
          <span className="text-sm text-red-600 font-medium">69% of projects stuck at seed stage</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Chart and Stage selector */}
        <div className="lg:col-span-1">
          <div className="bg-gray-50 p-4 rounded-lg border border-gray-100 h-64 mb-4">
            <Chart data={chartData} options={chartOptions} />
          </div>
          
          <div className="bg-blue-50 p-4 rounded-lg border border-blue-100">
            <h3 className="font-medium text-blue-800 mb-3">Select Your Project Stage</h3>
            <div className="grid grid-cols-1 gap-2">
              {fundingStages.map((stage) => (
                <button
                  key={stage.stage}
                  onClick={() => setSelectedStage(stage.stage)}
                  className={`py-2 px-3 rounded-md text-sm font-medium transition-colors text-left flex justify-between items-center
                    ${selectedStage === stage.stage 
                      ? 'bg-blue-600 text-white' 
                      : 'bg-white text-gray-800 hover:bg-blue-100'}`}
                >
                  <span className="capitalize">{stage.stage} Stage</span>
                  <span className="text-xs px-2 py-1 rounded-full bg-opacity-20 
                    ${selectedStage === stage.stage ? 'bg-white text-blue-100' : 'bg-blue-100 text-blue-800'}">
                    {stage.percentage}%
                  </span>
                </button>
              ))}
            </div>
            
            <div className="mt-4 pt-4 border-t border-blue-200">
              <h4 className="text-sm font-medium text-blue-800 mb-2">
                {selectedStage.charAt(0).toUpperCase() + selectedStage.slice(1)} Stage
              </h4>
              <p className="text-xs text-gray-600">
                {fundingStages.find(s => s.stage === selectedStage)?.description}
              </p>
              <p className="text-xs text-blue-600 mt-1">
                Typical Range: {fundingStages.find(s => s.stage === selectedStage)?.typical_range}
              </p>
            </div>
          </div>
        </div>
        
        {/* Middle Column: Stage-appropriate matching */}
        <div className="lg:col-span-1">
          <div className="bg-gradient-to-b from-blue-50 to-white rounded-lg border border-blue-100 p-4 h-full">
            <h3 className="font-medium text-gray-800 mb-3 flex items-center">
              <svg className="w-5 h-5 text-blue-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path d="M5 3a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2V5a2 2 0 00-2-2H5zM5 11a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2v-2a2 2 0 00-2-2H5zM11 5a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V5zM11 13a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
              </svg>
              Stage-Appropriate Opportunities
            </h3>
            <div className="space-y-3">
              {opportunities.length === 0 ? (
                <p className="text-gray-500 text-sm">No matching opportunities available for your current stage.</p>
              ) : (
                opportunities.map((opp) => (
                  <Link href={opp.link} key={opp.id} className="block">
                    <div className="bg-white rounded-lg p-3 shadow-sm hover:shadow-md transition-shadow border border-gray-100">
                      <h4 className="font-medium text-blue-700">{opp.title}</h4>
                      <div className="mt-2 flex flex-wrap gap-2">
                        <span className="text-xs bg-blue-50 text-blue-600 px-2 py-0.5 rounded">{opp.organization}</span>
                        <span className="text-xs bg-green-50 text-green-600 px-2 py-0.5 rounded">${opp.amount_usd.toLocaleString()}</span>
                        <span className="text-xs bg-yellow-50 text-yellow-600 px-2 py-0.5 rounded capitalize">{opp.stage}</span>
                      </div>
                      <div className="mt-2 text-xs text-red-500 flex items-center">
                        <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
                        </svg>
                        Deadline: {new Date(opp.deadline).toLocaleDateString()}
                      </div>
                    </div>
                  </Link>
                ))
              )}
            </div>

            <div className="mt-4">
              <Link 
                href={`/funding?stage=${selectedStage}`} 
                className="text-blue-600 hover:text-blue-800 text-sm flex items-center"
              >
                <span>View all {selectedStage} stage opportunities</span>
                <svg className="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </Link>
            </div>
            
            {selectedStage === 'seed' && (
              <div className="mt-6 bg-yellow-50 p-3 rounded-lg border border-yellow-100">
                <h4 className="text-sm font-medium text-yellow-700 flex items-center">
                  <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2h-1v-3a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                  Breaking the Seed Stage Barrier
                </h4>
                <p className="text-xs text-gray-600 mt-1">
                  Projects in the seed stage for &gt;24 months have 68% lower chance of securing follow-on funding. Consider our growth acceleration resources.
                </p>
                <div className="mt-2">
                  <Link 
                    href="/resources/seed-to-series-a" 
                    className="text-xs text-yellow-700 font-medium hover:underline"
                  >
                    View Acceleration Guide →
                  </Link>
                </div>
              </div>
            )}
          </div>
        </div>
        
        {/* Right Column: Consortium building features */}
        <div className="lg:col-span-1">
          <div className="bg-gradient-to-b from-purple-50 to-white rounded-lg border border-purple-100 p-4 h-full">
            <h3 className="font-medium text-gray-800 mb-3 flex items-center">
              <svg className="w-5 h-5 text-purple-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3zM6 8a2 2 0 11-4 0 2 2 0 014 0zM16 18v-3a5.972 5.972 0 00-.75-2.906A3.005 3.005 0 0119 15v3h-3zM4.75 12.094A5.973 5.973 0 004 15v3H1v-3a3 3 0 013.75-2.906z" />
              </svg>
              Consortium Building Opportunities
            </h3>
            <div className="text-sm text-gray-600 mb-4">
              Projects with multi-partner collaboration are 3.2x more likely to secure larger grants. Form consortiums to access bigger funding pools.
            </div>
            
            <div className="space-y-3">
              {collaborations.map((collab) => (
                <div 
                  key={collab.id}
                  className="bg-white rounded-lg p-3 shadow-sm hover:shadow-md transition-shadow border border-gray-100"
                >
                  <h4 className="font-medium text-purple-700">{collab.title}</h4>
                  <div className="mt-1 text-xs text-gray-500">
                    {collab.project_count} complementary projects
                  </div>
                  <div className="mt-2">
                    <span className="text-xs bg-green-50 text-green-600 px-2 py-0.5 rounded">
                      Combined potential: ${collab.combined_funding_potential.toLocaleString()}
                    </span>
                  </div>
                  <div className="mt-2">
                    <h5 className="text-xs text-gray-500 mb-1">Complementary skills:</h5>
                    <div className="flex flex-wrap gap-1">
                      {collab.complementary_skills.map((skill, idx) => (
                        <span key={idx} className="text-xs bg-purple-50 text-purple-600 px-2 py-0.5 rounded">{skill}</span>
                      ))}
                    </div>
                  </div>
                  <div className="mt-3 flex justify-end">
                    <Link 
                      href={`/collaborations/${collab.id}`}
                      className="text-xs text-purple-600 hover:text-purple-800"
                    >
                      Explore collaboration →
                    </Link>
                  </div>
                </div>
              ))}
            </div>
            
            <div className="mt-4 pt-4 border-t border-purple-200">
              <h4 className="text-sm font-medium text-gray-700 mb-2">
                Post-Award Success
              </h4>
              <div className="flex justify-between items-center mb-2">
                <span className="text-xs text-gray-600">Successfully funded</span>
                <span className="text-xs font-medium">68%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-1.5 mb-4">
                <div className="bg-green-500 h-1.5 rounded-full" style={{ width: '68%' }}></div>
              </div>
              
              <div className="flex justify-between items-center mb-2">
                <span className="text-xs text-gray-600">Advanced to next stage</span>
                <span className="text-xs font-medium">31%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-1.5 mb-4">
                <div className="bg-blue-500 h-1.5 rounded-full" style={{ width: '31%' }}></div>
              </div>

              <div className="mt-3">
                <Link 
                  href="/resources/post-award-tracking" 
                  className="text-xs text-purple-600 hover:text-purple-800 flex items-center"
                >
                  <span>Track your funding journey</span>
                  <svg className="w-3 h-3 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
