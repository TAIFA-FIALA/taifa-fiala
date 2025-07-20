import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, 
  Legend, ResponsiveContainer, Cell, Label
} from 'recharts';

// Type for tooltip payload item
interface TooltipPayloadItem {
  color: string;
  name: string;
  value: number;
  payload: SectorData;
}

// Type for tooltip props
interface TooltipProps {
  active?: boolean;
  payload?: TooltipPayloadItem[];
  label?: string;
}

// Custom tooltip component
const CustomTooltip = ({ active, payload, label }: TooltipProps) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white p-2 border border-gray-200 shadow-sm rounded">
        <p className="font-medium">{label}</p>
        {payload.map((item: { color: string; name: string; value: number }, index: number) => (
          <p key={index} className="text-sm" style={{ color: item.color }}>
            {item.name}: {item.value}{item.name.includes('Percentage') || item.name.includes('Priority') ? '%' : ''}
          </p>
        ))}
      </div>
    );
  }
  return null;
};

interface SectorData {
  sector: string;
  funding_percentage: number;
  opportunity_count: number;
  development_priority_score: number; // 1-10 score based on alignment with AU/SDGs
  impact_potential: number; // 1-10 score
}

interface SectoralAlignmentDashboardProps {
  className?: string;
}

export default function SectoralAlignmentDashboard({ className = '' }: SectoralAlignmentDashboardProps) {
  const [sectorData, setSectorData] = useState<SectorData[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedFilter, setSelectedFilter] = useState<string>('funding_percentage');
  const [showDevelopmentPriorities, setShowDevelopmentPriorities] = useState<boolean>(false);
  
  useEffect(() => {
    const fetchSectorData = async () => {
      try {
        setLoading(true);
        // In production, replace with actual API endpoint
        const res = await fetch('http://localhost:8000/api/v1/analytics/sector-distribution');
        
        if (!res.ok) {
          throw new Error(`HTTP error! status: ${res.status}`);
        }
        
        const data = await res.json();
        setSectorData(data);
      } catch (error) {
        console.error('Failed to fetch sector data:', error);
        setError('Failed to load sector distribution data.');
        
        // Fallback data for demonstration
        setSectorData([
          { 
            sector: 'Healthcare', 
            funding_percentage: 5.8, 
            opportunity_count: 12, 
            development_priority_score: 9.5, 
            impact_potential: 9.2 
          },
          { 
            sector: 'Agriculture', 
            funding_percentage: 3.9, 
            opportunity_count: 8, 
            development_priority_score: 8.7, 
            impact_potential: 8.5 
          },
          { 
            sector: 'Climate/Environment', 
            funding_percentage: 1.3, 
            opportunity_count: 4, 
            development_priority_score: 9.8, 
            impact_potential: 9.0 
          },
          { 
            sector: 'Education', 
            funding_percentage: 12.4, 
            opportunity_count: 22, 
            development_priority_score: 8.2, 
            impact_potential: 7.9 
          },
          { 
            sector: 'Finance/Fintech', 
            funding_percentage: 28.6, 
            opportunity_count: 31, 
            development_priority_score: 6.5, 
            impact_potential: 7.2 
          },
          { 
            sector: 'General AI Research', 
            funding_percentage: 18.7, 
            opportunity_count: 25, 
            development_priority_score: 7.0, 
            impact_potential: 6.8 
          },
          { 
            sector: 'E-commerce', 
            funding_percentage: 14.2, 
            opportunity_count: 18, 
            development_priority_score: 5.2, 
            impact_potential: 5.9 
          },
          { 
            sector: 'Transportation', 
            funding_percentage: 9.8, 
            opportunity_count: 15, 
            development_priority_score: 7.5, 
            impact_potential: 7.3 
          },
          { 
            sector: 'Energy', 
            funding_percentage: 3.7, 
            opportunity_count: 7, 
            development_priority_score: 8.9, 
            impact_potential: 8.8 
          },
          { 
            sector: 'Other', 
            funding_percentage: 1.6, 
            opportunity_count: 5, 
            development_priority_score: 5.0, 
            impact_potential: 4.5 
          },
        ]);
      } finally {
        setLoading(false);
      }
    };

    fetchSectorData();
  }, []);

  // Calculate gap between priority score and funding
  const calculatePriorityGap = (sector: SectorData) => {
    return ((sector.development_priority_score / 10) * 100) - sector.funding_percentage;
  };

  // Sort data based on the selected filter
  const getSortedData = () => {
    if (showDevelopmentPriorities) {
      return [...sectorData].sort((a, b) => b.development_priority_score - a.development_priority_score);
    } else {
      return [...sectorData].sort((a, b) => {
        if (selectedFilter === 'funding_percentage') {
          return b.funding_percentage - a.funding_percentage;
        } else if (selectedFilter === 'opportunity_count') {
          return b.opportunity_count - a.opportunity_count;
        } else {
          return b.impact_potential - a.impact_potential;
        }
      });
    }
  };

  const sortedData = getSortedData();
  
  // Transform data for Recharts format
  const chartData = sortedData.map(item => {
    if (showDevelopmentPriorities) {
      return {
        sector: item.sector,
        'Development Priority Score (%)': (item.development_priority_score / 10) * 100,
        'Current Funding (%)': item.funding_percentage
      };
    } else {
      return {
        sector: item.sector,
        [selectedFilter === 'funding_percentage' ? 'Funding Percentage (%)' : 
         selectedFilter === 'opportunity_count' ? 'Opportunity Count' : 
         'Impact Potential Score']: 
         selectedFilter === 'funding_percentage' ? item.funding_percentage : 
         selectedFilter === 'opportunity_count' ? item.opportunity_count : 
         item.impact_potential
      };
    }
  });
  
  // Define chart colors
  const priorityScoreColor = 'rgba(75, 192, 192, 1)';
  const fundingColor = 'rgba(54, 162, 235, 1)';
  const barColor = fundingColor;
  
  // Chart title
  const chartTitle = showDevelopmentPriorities ? 
    'Development Priority vs. Current Funding by Sector' : 
    selectedFilter === 'funding_percentage' ? 'Funding Distribution by Sector' : 
    selectedFilter === 'opportunity_count' ? 'Opportunities by Sector' : 
    'Impact Potential by Sector';
    
  // Y-axis label
  const yAxisLabel = selectedFilter === 'opportunity_count' ? 'Number of Opportunities' : 
    showDevelopmentPriorities ? 'Percentage (%)' : 
    selectedFilter === 'funding_percentage' ? 'Funding Percentage (%)' : 'Score (1-10)';

  if (loading) {
    return <div className="flex justify-center items-center h-64 bg-gray-50 rounded-lg">Loading sector alignment data...</div>;
  }

  if (error) {
    return (
      <div className="flex justify-center items-center h-64 bg-red-50 rounded-lg text-red-500">
        {error} Please try again later.
      </div>
    );
  }

  // Find the sectors with the highest priority gap (priority score vs funding)
  const criticalGapSectors = [...sectorData]
    .sort((a, b) => calculatePriorityGap(b) - calculatePriorityGap(a))
    .slice(0, 3);

  return (
    <div className={`${className} bg-white rounded-xl shadow-lg p-4`}>
      <div className="flex flex-col md:flex-row justify-between items-center mb-4">
        <h2 className="text-xl font-bold text-gray-800 mb-2 md:mb-0">Sectoral Alignment Dashboard</h2>
        <div className="flex flex-wrap gap-2">
          <div className="flex items-center space-x-2">
            <label className="text-sm text-gray-600">View by:</label>
            <select
              value={selectedFilter}
              onChange={(e) => {
                setSelectedFilter(e.target.value);
                setShowDevelopmentPriorities(false);
              }}
              disabled={showDevelopmentPriorities}
              className="rounded-md border-gray-300 text-sm focus:border-blue-500 focus:ring focus:ring-blue-500 focus:ring-opacity-50"
            >
              <option value="funding_percentage">Funding Percentage</option>
              <option value="opportunity_count">Opportunity Count</option>
              <option value="impact_potential">Impact Potential</option>
            </select>
          </div>
          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              id="developmentPriorities"
              checked={showDevelopmentPriorities}
              onChange={() => setShowDevelopmentPriorities(!showDevelopmentPriorities)}
              className="rounded text-blue-600 focus:ring-blue-500"
            />
            <label htmlFor="developmentPriorities" className="text-sm text-gray-600">Compare with development priorities</label>
          </div>
        </div>
      </div>

      {/* Chart */}
      <div className="h-80 mt-4">
        <div className="text-center text-lg font-medium text-gray-700 mb-2">{chartTitle}</div>
        <ResponsiveContainer width="100%" height="90%">
          <BarChart
            data={chartData}
            margin={{ top: 20, right: 30, left: 20, bottom: 50 }}
          >
            <CartesianGrid strokeDasharray="3 3" vertical={false} />
            <XAxis 
              dataKey="sector" 
              tick={{ fontSize: 12 }} 
              interval={0} 
              angle={-45} 
              textAnchor="end"
            />
            <YAxis
              domain={[0, 'auto']}
              tickFormatter={(value) => selectedFilter === 'opportunity_count' ? value : `${value}${selectedFilter !== 'impact_potential' ? '%' : ''}`}
            >
              <Label 
                value={yAxisLabel} 
                angle={-90} 
                position="insideLeft" 
                style={{ textAnchor: 'middle' }} 
              />
            </YAxis>
            <Tooltip content={<CustomTooltip />} />
            <Legend verticalAlign="top" />
            
            {showDevelopmentPriorities ? (
              <>
                <Bar 
                  dataKey="Development Priority Score (%)" 
                  fill={priorityScoreColor} 
                  name="Development Priority Score (%)" 
                />
                <Bar 
                  dataKey="Current Funding (%)" 
                  fill={fundingColor} 
                  name="Current Funding (%)" 
                />
              </>
            ) : (
              <Bar 
                dataKey={Object.keys(chartData[0]).filter(key => key !== 'sector')[0]} 
                fill={barColor} 
              >
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={barColor} />
                ))}
              </Bar>
            )}
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Critical Gap Alert */}
      <div className="mt-6 bg-red-50 border border-red-200 rounded-lg p-4">
        <h3 className="text-lg font-medium text-red-700 flex items-center gap-2">
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
          Critical Funding Gap Alert
        </h3>
        <p className="text-sm text-gray-700 mb-3 mt-1">
          The following sectors have high development priority but are significantly underfunded:
        </p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {criticalGapSectors.map((sector) => (
            <div key={sector.sector} className="bg-white rounded border border-red-100 p-3">
              <h4 className="font-medium text-gray-800">{sector.sector}</h4>
              <div className="mt-1 flex justify-between text-sm">
                <span className="text-gray-500">Priority Score:</span>
                <span className="text-green-600 font-medium">{sector.development_priority_score}/10</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Current Funding:</span>
                <span className="text-red-600 font-medium">{sector.funding_percentage}%</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Gap:</span>
                <span className="text-red-600 font-bold">
                  {calculatePriorityGap(sector).toFixed(1)}% underfunded
                </span>
              </div>
            </div>
          ))}
        </div>
        <div className="mt-4 flex justify-end">
          <Link 
            href={`/funding?category=${criticalGapSectors[0].sector}`}
            className="text-sm bg-red-100 hover:bg-red-200 text-red-700 font-medium py-2 px-4 rounded transition-colors"
          >
            View {criticalGapSectors[0].sector} Opportunities
          </Link>
        </div>
      </div>

      {/* Development Goals Alignment */}
      <div className="mt-6">
        <h3 className="text-lg font-medium text-gray-800 mb-3">Alignment with Development Goals</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="border border-gray-200 rounded-lg p-4">
            <h4 className="font-medium text-gray-700 flex items-center gap-2">
              <span className="inline-block w-6 h-6 rounded-full bg-blue-500 text-white text-xs flex items-center justify-center">AU</span>
              African Union Agenda 2063
            </h4>
            <div className="mt-3 space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Goal 2: Education & Skills Revolution</span>
                <div className="w-1/2 bg-gray-200 rounded-full h-2.5">
                  <div className="bg-blue-600 h-2.5 rounded-full" style={{ width: '45%' }}></div>
                </div>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Goal 5: Modern Agriculture</span>
                <div className="w-1/2 bg-gray-200 rounded-full h-2.5">
                  <div className="bg-blue-600 h-2.5 rounded-full" style={{ width: '28%' }}></div>
                </div>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Goal 6: Blue/Ocean Economy</span>
                <div className="w-1/2 bg-gray-200 rounded-full h-2.5">
                  <div className="bg-blue-600 h-2.5 rounded-full" style={{ width: '12%' }}></div>
                </div>
              </div>
            </div>
          </div>

          <div className="border border-gray-200 rounded-lg p-4">
            <h4 className="font-medium text-gray-700 flex items-center gap-2">
              <span className="inline-block w-6 h-6 rounded-full bg-green-500 text-white text-xs flex items-center justify-center">UN</span>
              UN Sustainable Development Goals
            </h4>
            <div className="mt-3 space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">SDG 3: Good Health & Well-being</span>
                <div className="w-1/2 bg-gray-200 rounded-full h-2.5">
                  <div className="bg-green-500 h-2.5 rounded-full" style={{ width: '32%' }}></div>
                </div>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">SDG 13: Climate Action</span>
                <div className="w-1/2 bg-gray-200 rounded-full h-2.5">
                  <div className="bg-green-500 h-2.5 rounded-full" style={{ width: '18%' }}></div>
                </div>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">SDG 9: Industry & Innovation</span>
                <div className="w-1/2 bg-gray-200 rounded-full h-2.5">
                  <div className="bg-green-500 h-2.5 rounded-full" style={{ width: '65%' }}></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
