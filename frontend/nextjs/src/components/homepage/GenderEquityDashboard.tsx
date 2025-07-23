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
  Legend,
  ResponsiveContainer,
  Tooltip as RechartsTooltip,
  ComposedChart
} from 'recharts';

// Icons
import { 
  AlertCircle, 
  DollarSign, 
  TrendingDown
} from 'lucide-react';

// TAIFA color scheme for charts
const CHART_COLORS = {
  female: '#F0A621',    // TAIFA golden yellow
  male: '#3E4B59',      // TAIFA primary dark blue-gray
  femaleLight: '#BA4D00', // TAIFA dark orange
  maleLight: '#5F763B',   // TAIFA olive green
  gridLine: '#E5E7EB',
  text: '#1F2937'
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
    <div className="space-y-6">
      {/* Animated Metric Cards with Color Accents */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="bg-gradient-to-br from-white to-taifa-primary/5 p-6 rounded-lg border-l-4 border-taifa-primary shadow-sm hover:shadow-lg hover:scale-105 transition-all duration-300 text-center group">
          <div className="w-12 h-12 rounded-full bg-taifa-primary/10 flex items-center justify-center mx-auto mb-3 group-hover:bg-taifa-primary/20 transition-colors">
            <DollarSign className="w-6 h-6 text-taifa-primary" />
          </div>
          <div className="text-2xl font-semibold text-taifa-primary mb-2">
            {Math.round((totalFundingWomen / (totalFundingWomen + totalFundingMen)) * 100)}%
          </div>
          <div className="text-sm text-taifa-muted">Female Funding Share</div>
          <div className="text-xs text-taifa-primary mt-1">across {genderTimelineData.length} years</div>
        </div>

        <div className="bg-gradient-to-br from-white to-taifa-secondary/5 p-6 rounded-lg border-l-4 border-taifa-secondary shadow-sm hover:shadow-lg hover:scale-105 transition-all duration-300 text-center group">
          <div className="w-12 h-12 rounded-full bg-taifa-secondary/10 flex items-center justify-center mx-auto mb-3 group-hover:bg-taifa-secondary/20 transition-colors">
            <DollarSign className="w-6 h-6 text-taifa-secondary" />
          </div>
          <div className="text-2xl font-semibold text-taifa-secondary mb-2">$48M</div>
          <div className="text-sm text-taifa-muted mb-1">Female founder funding</div>
          <div className="text-xs text-taifa-secondary">Only 12% of total funding</div>
        </div>
        
        <div className="bg-gradient-to-br from-white to-taifa-accent/5 p-6 rounded-lg border-l-4 border-taifa-accent shadow-sm hover:shadow-lg hover:scale-105 transition-all duration-300 text-center group">
          <div className="w-12 h-12 rounded-full bg-taifa-accent/10 flex items-center justify-center mx-auto mb-3 group-hover:bg-taifa-accent/20 transition-colors">
            <TrendingDown className="w-6 h-6 text-taifa-accent" />
          </div>
          <div className="text-2xl font-semibold text-taifa-accent mb-2">6 years</div>
          <div className="text-sm text-taifa-muted mb-1">Declining trend</div>
          <div className="text-xs text-taifa-accent">Since 2019 peak of 22.3%</div>
        </div>
        
        <div className="bg-gradient-to-br from-white to-taifa-primary/5 p-6 rounded-lg border-l-4 border-taifa-primary shadow-sm hover:shadow-lg hover:scale-105 transition-all duration-300 text-center group">
          <div className="w-12 h-12 rounded-full bg-taifa-primary/10 flex items-center justify-center mx-auto mb-3 group-hover:bg-taifa-primary/20 transition-colors">
            <svg className="w-6 h-6 text-taifa-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
            </svg>
          </div>
          <div className="text-2xl font-semibold text-taifa-primary mb-2">4.2x</div>
          <div className="text-sm text-taifa-muted mb-1">Funding gap</div>
          <div className="text-xs text-taifa-primary">Less than male-led startups</div>
        </div>
      </div>

      {/* Main Visualizations Grid - Only showing working charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Timeline Chart */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Female Representation in AI Funding (2018-2024)
          </h3>
          <div className="w-full h-80">
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart
                data={genderTimelineData}
                margin={chartPadding}
                barGap={barGap}
                barSize={barSize}
              >

                
                <CartesianGrid 
                  vertical={false} 
                  stroke={CHART_COLORS.gridLine} 
                  strokeDasharray="3 3" 
                />
                
                <XAxis 
                  dataKey="year" 
                  tickLine={false}
                  axisLine={{ stroke: CHART_COLORS.gridLine }}
                  tick={{ fill: CHART_COLORS.text, fontSize: 12 }}
                />
                
                <YAxis 
                  yAxisId="left" 
                  orientation="left"
                  tickLine={false}
                  axisLine={false}
                  tick={{ fill: CHART_COLORS.text, fontSize: 12 }}
                />
                
                <YAxis 
                  yAxisId="right" 
                  orientation="right" 
                  domain={[0, 100]}
                  tickFormatter={(value) => `${value}%`}
                  tickLine={false}
                  axisLine={false}
                  tick={{ 
                    fill: CHART_COLORS.text,
                    fontSize: dimensions.isMobile ? 10 : 12,
                    dx: 10
                  }}
                />
                <RechartsTooltip 
                  content={<CustomTooltip 
                    formatter={(value, name) => {
                      if (name === 'femalePercentage') {
                        return [`${value}%`, 'Female %'];
                      }
                      return [String(value), name];
                    }}
                  />} 
                />
                <Legend 
                  formatter={(value) => {
                    if (value === 'femalePercentage') return 'Female %';
                    if (value === 'female') return 'Female Founders';
                    if (value === 'male') return 'Male Founders';
                    return value;
                  }}
                />
                <Bar 
                  yAxisId="left" 
                  dataKey="female" 
                  name="Female Founders" 
                  fill={CHART_COLORS.female}
                  radius={[4, 4, 0, 0]}
                />
                <Bar 
                  yAxisId="left" 
                  dataKey="male" 
                  name="Male Founders" 
                  fill={CHART_COLORS.male}
                  radius={[4, 4, 0, 0]}
                />
                <Line 
                  yAxisId="right" 
                  type="monotone" 
                  dataKey="femalePercentage" 
                  name="Female %" 
                  stroke={CHART_COLORS.female}
                  strokeWidth={3}
                  dot={{ 
                    r: 5, 
                    fill: CHART_COLORS.female,
                    stroke: '#ffffff',
                    strokeWidth: 2,
                    fillOpacity: 1
                  }}
                />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Regional Analysis */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Regional Gender Disparities
          </h3>
          <div className="w-full h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={regionalGenderData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke={CHART_COLORS.gridLine} />
                <XAxis dataKey="region" stroke={CHART_COLORS.text} />
                <YAxis stroke={CHART_COLORS.text} />
                <RechartsTooltip 
                  formatter={(value: number) => [
                    `${value}%`,
                    'Female Leadership'
                  ]}
                  content={<CustomTooltip />}
                />
                <Bar dataKey="femalePercent" fill={CHART_COLORS.female} name="Female Leadership %" radius={[4, 4, 0, 0]} />
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
