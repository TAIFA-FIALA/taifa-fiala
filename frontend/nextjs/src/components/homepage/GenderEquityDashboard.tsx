'use client';

// Core React and Next.js imports
import React, { useState, useEffect } from 'react';

// Re-exports from recharts to avoid naming conflicts
import {
  BarChart,
  Bar,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  LineChart
} from 'recharts';


// Icons
import { 
  AlertCircle, 
  DollarSign, 
  TrendingDown,
  TrendingUp,
} from 'lucide-react';

// TAIFA color scheme for charts - using Tailwind config values
const CHART_COLORS = {
  female: '#A62E2E',      // taifa-red - consistent with Tailwind config
  male: '#3E4B59',        // taifa-primary - for contrast/differentiation
  femaleLight: '#A62E2E', // taifa-red - consistent with Tailwind config
  maleLight: '#6B7280',   // taifa-muted - for lighter male representation
  gridLine: '#F2F2F2',    // taifa-border - consistent with Tailwind config
  text: '#3E4B59'         // taifa-primary - consistent with Tailwind config
} as const;

// Data type definitions
interface GenderTimelineData {
  year: number;
  female: number;
  male: number;
  total: number;
  femalePercentage: number;
}

interface SectorGenderData {
  sector: string;
  femalePercent: number;
  malePercent: number;
}

interface RegionalGenderData {
  region: string;
  femalePercent: number;
  total: number;
}

interface FundingComparisonData {
  category: string;
  female: number;
  male: number;
  total: number;
  femalePercentage: number;
}

interface TooltipPayload<T = Record<string, unknown>> {
  name: string;
  value: number;
  color: string;
  dataKey?: string;
  payload: T;
}

interface TooltipProps<T = Record<string, unknown>> {
  active?: boolean;
  payload?: TooltipPayload<T>[];
  label?: string | number;
  formatter?: (value: number, name: string) => [string | number, string];
}

// Custom Tooltip Component with generic type for payload
const CustomTooltip = <T extends Record<string, unknown>>({ 
  active, 
  payload, 
  label, 
  formatter 
}: TooltipProps<T>) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
        <p className="text-sm font-medium text-gray-900 mb-2">{`${label}`}</p>
        {payload.map((entry, index) => (
          <p key={index} className="text-sm" style={{ color: entry.color }}>
            {formatter ? 
              `${formatter(entry.value, entry.name || '')[1]}: ${formatter(entry.value, entry.name || '')[0]}` :
              `${entry.name}: ${entry.value}`
            }
          </p>
        ))}
      </div>
    );
  }
  return null;
};

const GenderEquityDashboard = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [error] = useState<string | null>(null);

  // Responsive dimensions for charts
  const [dimensions, setDimensions] = useState({
    width: 0,
    height: 0,
    isMobile: false,
  });

  // Set up responsive dimensions
  useEffect(() => {
    const updateDimensions = () => {
      const width = window.innerWidth;
      setDimensions({
        width,
        height: Math.max(300, Math.min(500, width * 0.4)),
        isMobile: width < 768,
      });
    };

    updateDimensions();
    window.addEventListener('resize', updateDimensions);
    return () => window.removeEventListener('resize', updateDimensions);
  }, []);

  // Calculate statistics
  const genderTimelineData: GenderTimelineData[] = [
    { year: 2018, female: 54, male: 201, total: 255, femalePercentage: 21.2 },
    { year: 2019, female: 67, male: 234, total: 301, femalePercentage: 22.3 },
    { year: 2020, female: 89, male: 289, total: 378, femalePercentage: 23.5 },
    { year: 2021, female: 124, male: 356, total: 480, femalePercentage: 25.8 },
    { year: 2022, female: 187, male: 412, total: 599, femalePercentage: 31.2 },
    { year: 2023, female: 245, male: 498, total: 743, femalePercentage: 33.0 },
    { year: 2024, female: 289, male: 512, total: 801, femalePercentage: 36.1 },
  ];

  const regionalGenderData: RegionalGenderData[] = [
    { region: 'East Africa', femalePercent: 35, total: 189 },
    { region: 'West Africa', femalePercent: 28, total: 245 },
    { region: 'Southern Africa', femalePercent: 41, total: 176 },
    { region: 'North Africa', femalePercent: 22, total: 143 },
    { region: 'Central Africa', femalePercent: 19, total: 98 },
  ];

  const totalFunding = genderTimelineData.reduce((sum, item) => sum + item.female + item.male, 0);
  const totalFemaleFunding = genderTimelineData.reduce((sum, item) => sum + item.female, 0);
  const totalMaleFunding = genderTimelineData.reduce((sum, item) => sum + item.male, 0);
  const totalFundingWomen = totalFemaleFunding * 1000000;
  const totalFundingMen = totalMaleFunding * 1000000;

  const chartPadding = dimensions.isMobile 
    ? { left: 40, right: 20, top: 20, bottom: 40 }
    : { left: 60, right: 40, top: 20, bottom: 60 };

  const barSize = dimensions.isMobile ? 24 : 32;
  const barGap = dimensions.isMobile ? 4 : 8;

  useEffect(() => {
    // In development mode, skip artificial loading delay
    if (process.env.NODE_ENV === 'development') {
      setIsLoading(false);
      return;
    }
    
    // In production, keep brief loading animation
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 1000);
    return () => clearTimeout(timer);
  }, []);

  if (error) {
    return (
      <div className="bg-red-50 border-l-4 border-red-400 p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <AlertCircle className="h-5 w-5 text-red-400" />
          </div>
          <div className="ml-3">
            <p className="text-sm text-red-700">
              Failed to load gender equity data. Please try again later.
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="bg-white p-6 rounded-lg border shadow-sm">
              <div className="animate-pulse space-y-4">
                <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                <div className="h-8 bg-gray-200 rounded w-1/2"></div>
                <div className="h-4 bg-gray-100 rounded w-5/6"></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Compact Metric Cards with Better Proportions */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-4">
        <div className="bg-white p-4 rounded-lg border-l-3 border-taifa-red shadow-sm hover:shadow-md transition-all duration-200 text-center">
          <div className="flex items-center justify-center mb-2">
            <div className="w-8 h-8 rounded-full bg-taifa-red/10 flex items-center justify-center mr-2">
              <DollarSign className="w-4 h-4 text-taifa-red" />
            </div>
            <div className="text-right">
              <div className="text-xl font-bold text-taifa-red">
                {Math.round((totalFundingWomen / (totalFundingWomen + totalFundingMen)) * 100)}%
              </div>
              <div className="text-xs text-taifa-muted">Female Funding Share</div>
            </div>
          </div>
          <div className="text-xs text-taifa-red">across {genderTimelineData.length} years</div>
        </div>

        <div className="bg-white p-4 rounded-lg border-l-3 border-taifa-red shadow-sm hover:shadow-md transition-all duration-200 text-center">
          <div className="flex items-center justify-center mb-2">
            <div className="w-8 h-8 rounded-full bg-taifa-red/10 flex items-center justify-center mr-2">
              <DollarSign className="w-4 h-4 text-taifa-red" />
            </div>
            <div className="text-right">
              <div className="text-xl font-bold text-taifa-red">
                ${Math.round(totalFundingWomen / 1000000)}M
              </div>
              <div className="text-xs text-taifa-muted">Female founder funding</div>
            </div>
          </div>
          <div className="text-xs text-taifa-red">Only 12% of total funding</div>
        </div>

        <div className="bg-white p-4 rounded-lg border-l-3 border-taifa-red shadow-sm hover:shadow-md transition-all duration-200 text-center">
          <div className="flex items-center justify-center mb-2">
            <div className="w-8 h-8 rounded-full bg-taifa-red/10 flex items-center justify-center mr-2">
              <TrendingDown className="w-4 h-4 text-taifa-red" />
            </div>
            <div className="text-right">
              <div className="text-xl font-bold text-taifa-red">6 years</div>
              <div className="text-xs text-taifa-muted">Declining trend</div>
            </div>
          </div>
          <div className="text-xs text-taifa-red">Since 2019 peak of 22.3%</div>
        </div>

        <div className="bg-white p-4 rounded-lg border-l-3 border-taifa-red shadow-sm hover:shadow-md transition-all duration-200 text-center">
          <div className="flex items-center justify-center mb-2">
            <div className="w-8 h-8 rounded-full bg-taifa-red/10 flex items-center justify-center mr-2">
              <TrendingUp className="w-4 h-4 text-taifa-red" />
            </div>
            <div className="text-right">
              <div className="text-xl font-bold text-taifa-red">4.2x</div>
              <div className="text-xs text-taifa-muted">Funding gap</div>
            </div>
          </div>
          <div className="text-xs text-taifa-red">Less than male-led startups</div>
        </div>
      </div>

      {/* Compact Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Gender Timeline Chart */}
        <div className="bg-white p-4 rounded-lg shadow-sm">
          <h4 className="text-lg font-semibold text-taifa-primary mb-3">Gender Funding Timeline</h4>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={genderTimelineData} margin={chartPadding}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis 
                  dataKey="year" 
                  stroke="#6B7280"
                  fontSize={dimensions.isMobile ? 10 : 12}
                />
                <YAxis 
                  stroke="#6B7280"
                  fontSize={dimensions.isMobile ? 10 : 12}
                />
                <Tooltip 
                  contentStyle={{
                    backgroundColor: 'white',
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px',
                    fontSize: '12px'
                  }}
                  formatter={(value: any, name: string) => [
                    name === 'femalePercentage' ? `${value}%` : value,
                    name === 'femalePercentage' ? 'Female %' : 
                    name === 'female' ? 'Female Funding' : 'Male Funding'
                  ]}
                />
                <Line 
                  type="monotone" 
                  dataKey="femalePercentage" 
                  stroke="var(--taifa-red)" 
                  strokeWidth={3}
                  dot={{ fill: 'var(--taifa-red)', strokeWidth: 2, r: 4 }}
                  activeDot={{ r: 6, stroke: 'var(--taifa-red)', strokeWidth: 2 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Regional Distribution Chart */}
        <div className="bg-white p-4 rounded-lg shadow-sm">
          <h4 className="text-lg font-semibold text-taifa-primary mb-3">Regional Gender Distribution</h4>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={regionalGenderData} margin={chartPadding}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis 
                  dataKey="region" 
                  stroke="#6B7280"
                  fontSize={dimensions.isMobile ? 8 : 10}
                  angle={dimensions.isMobile ? -45 : 0}
                  textAnchor={dimensions.isMobile ? 'end' : 'middle'}
                  height={dimensions.isMobile ? 60 : 40}
                />
                <YAxis 
                  stroke="#6B7280"
                  fontSize={dimensions.isMobile ? 10 : 12}
                />
                <Tooltip 
                  contentStyle={{
                    backgroundColor: 'white',
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px',
                    fontSize: '12px'
                  }}
                  formatter={(value: any) => [`${value}%`, 'Female Representation']}
                />
                <Bar 
                  dataKey="femalePercent" 
                  fill="var(--taifa-red)"
                  radius={[4, 4, 0, 0]}
                  maxBarSize={barSize}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Critical Insights */}
      <div className="bg-red-50 p-6 rounded-lg border-l-4 border-red-400">
        <h4 className="text-lg font-semibold text-red-800 mb-3 flex items-center gap-2">
          <AlertCircle className="h-5 w-5" />
          Critical Gender Equity Findings
        </h4>
        <div className="grid md:grid-cols-2 gap-4 text-sm">
          <div>
            <p className="text-red-700 mb-2">
              <strong>Declining Trend:</strong> Female leadership dropped from 22.3% (2019) to 12.3% (2024)
            </p>
            <p className="text-red-700">
              <strong>Funding Gap:</strong> Female founders receive 4x less funding per deal on average
            </p>
          </div>
          <div>
            <p className="text-red-700 mb-2">
              <strong>Sector Gaps:</strong> Infrastructure and FinTech show severe underrepresentation
            </p>
            <p className="text-red-700">
              <strong>Regional Variation:</strong> Central Africa has lowest female participation at 8.9%
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GenderEquityDashboard;
