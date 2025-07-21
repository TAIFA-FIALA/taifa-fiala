'use client';

import { TrendingUp, AlertTriangle, DollarSign, Briefcase, Target, BarChart3, PieChart, MapPin } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart as RechartsPieChart, Pie, Cell, Line, ComposedChart, Area, AreaChart } from 'recharts';

import React from 'react';

// Data structures for the report
interface FundingMetric {
  value: string;
  label: string;
  icon: React.ReactNode;
  trend?: 'up' | 'down' | 'neutral';
  color: string;
}

interface CountryFunding {
  country: string;
  amount: string;
  deals?: number;
  avgPerStartup?: string;
}

interface SectorData {
  sector: string;
  percentage: number;
  color: string;
  funding?: string;
}


// Components for visual storytelling

// Chart data for visualizations
const fundingByCountryData = [
  { country: 'Tunisia', funding: 244.4, deals: 9, color: '#3E4B59' },
  { country: 'Kenya', funding: 242.3, deals: 30, color: '#F0A621' },
  { country: 'South Africa', funding: 150.4, deals: 29, color: '#007A56' },
  { country: 'Egypt', funding: 83.4, deals: 17, color: '#BA4D00' },
  { country: 'Nigeria', funding: 45.2, deals: 32, color: '#5F763B' },
  { country: 'Ghana', funding: 28.1, deals: 12, color: '#A62E2E' },
];

const sectorDistributionData = [
  { name: 'Financial Services', value: 20.9, funding: 134, color: '#3E4B59' },
  { name: 'Healthcare', value: 5.8, funding: 46, color: '#A62E2E' },
  { name: 'Agriculture', value: 3.9, funding: 31, color: '#007A56' },
  { name: 'Education', value: 8.2, funding: 66, color: '#F0A621' },
  { name: 'Climate AI', value: 1.3, funding: 10, color: '#5F763B' },
  { name: 'Other', value: 59.9, funding: 513, color: '#F0E68C' },
];

const fundingTimelineData = [
  { year: '2019', total: 87, private: 45, development: 42 },
  { year: '2020', total: 124, private: 78, development: 46 },
  { year: '2021', total: 189, private: 134, development: 55 },
  { year: '2022', total: 267, private: 195, development: 72 },
  { year: '2023', total: 334, private: 246, development: 88 },
  { year: '2024', total: 387, private: 289, development: 98 },
];

const regionalGapsData = [
  { region: 'East Africa', funding: 285.7, countries: 12, population: 445 },
  { region: 'West Africa', funding: 89.3, countries: 16, population: 381 },
  { region: 'North Africa', funding: 327.8, countries: 6, population: 246 },
  { region: 'Southern Africa', funding: 178.9, countries: 10, population: 174 },
  { region: 'Central Africa', funding: 18.3, countries: 9, population: 185 },
];


// Components for visual storytelling

const MetricCard: React.FC<{ metric: FundingMetric }> = ({ metric }) => (
  <div className={`bg-white p-6 rounded-xl border-l-4 ${metric.color} shadow-lg hover:shadow-xl transition-shadow`}>
    <div className="flex items-center justify-between">
      <div>
        <div className="text-3xl font-bold text-gray-900 mb-1">{metric.value}</div>
        <div className="text-sm text-gray-600">{metric.label}</div>
      </div>
      <div className="text-3xl text-gray-400">{metric.icon}</div>
    </div>
  </div>
);

const CountryCard: React.FC<{ country: CountryFunding; rank: number }> = ({ country, rank }) => (
  <div className="bg-white p-4 rounded-lg border border-taifa-border hover:border-taifa-primary transition-colors">
    <div className="flex items-center justify-between mb-2">
      <span className="text-lg font-semibold text-taifa-primary">#{rank} {country.country}</span>
      <MapPin className="h-5 w-5 text-taifa-secondary" />
    </div>
    <div className="text-2xl font-bold text-taifa-accent mb-1">{country.amount}</div>
    {country.avgPerStartup && (
      <div className="text-sm text-taifa-muted">Avg: {country.avgPerStartup}/startup</div>
    )}
  </div>
);

const SectorBar: React.FC<{ sector: SectorData }> = ({ sector }) => (
  <div className="mb-4">
    <div className="flex justify-between items-center mb-2">
      <span className="text-sm font-medium text-gray-700">{sector.sector}</span>
      <span className="text-sm text-gray-500">{sector.percentage}%</span>
    </div>
    <div className="w-full bg-gray-200 rounded-full h-3">
      <div 
        className={`h-3 rounded-full ${sector.color}`}
        style={{ width: `${sector.percentage * 4}%` }}
      ></div>
    </div>
  </div>
);

const AlertCard: React.FC<{ title: string; metric: string; description: string; severity: 'high' | 'medium' | 'low' }> = ({ title, metric, description, severity }) => {
  const severityColors = {
    high: 'border-red-500 bg-red-50',
    medium: 'border-yellow-500 bg-yellow-50',
    low: 'border-blue-500 bg-blue-50'
  };
  
  return (
    <div className={`p-4 rounded-lg border-l-4 ${severityColors[severity]}`}>
      <div className="flex items-center mb-2">
        <AlertTriangle className="h-5 w-5 text-red-600 mr-2" />
        <h4 className="font-semibold text-gray-800">{title}</h4>
      </div>
      <div className="text-2xl font-bold text-gray-900 mb-1">{metric}</div>
      <p className="text-sm text-gray-600">{description}</p>
    </div>
  );
};

export default function FundingLandscapePage() {
  // Data from the report
  const keyMetrics: FundingMetric[] = [
    {
      value: "$800M+",
      label: "Total AI Funding 2019-2024",
      icon: <DollarSign />,
      color: "border-taifa-accent",
      trend: 'up'
    },
    {
      value: "103",
      label: "Private Sector Deals",
      icon: <Briefcase />,
      color: "border-taifa-primary"
    },
    {
      value: "83%",
      label: "Funding to 4 Countries Only",
      icon: <AlertTriangle />,
      color: "border-taifa-red",
      trend: 'up'
    },
    {
      value: "16",
      label: "Countries with AI Strategies",
      icon: <Target />,
      color: "border-taifa-secondary"
    }
  ];

  const topCountries: CountryFunding[] = [
    { country: "Tunisia", amount: "$244.4M", avgPerStartup: "$27.2M" },
    { country: "Kenya", amount: "$242.3M", avgPerStartup: "$8.1M" },
    { country: "South Africa", amount: "$150.4M", avgPerStartup: "$5.2M" },
    { country: "Egypt", amount: "$83.4M", avgPerStartup: "$4.9M" },
  ];

  const sectorData: SectorData[] = [
    { sector: "Financial Services", percentage: 20.9, color: "bg-blue-500", funding: "$134M" },
    { sector: "Healthcare", percentage: 5.8, color: "bg-red-500", funding: "$46M" },
    { sector: "Agriculture", percentage: 3.9, color: "bg-green-500", funding: "$31M" },
    { sector: "Climate AI", percentage: 1.3, color: "bg-yellow-500", funding: "$10M" },
  ];

  return (
    <div className="min-h-screen bg-taifa-light">
      {/* Hero Section */}
      <header className="bg-white shadow-sm border-b border-taifa-border">
        <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-4xl font-bold text-taifa-primary mb-2">
              African AI Funding Landscape
            </h1>
            <p className="text-xl text-taifa-muted">2019-2024 Analysis</p>
          </div>
        </div>
      </header>

      {/* Key Metrics Dashboard */}
      <section className="py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
            {keyMetrics.map((metric, index) => (
              <MetricCard key={index} metric={metric} />
            ))}
          </div>
        </div>
      </section>

      {/* Geographic Concentration Story */}
      <section className="py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-white rounded-xl p-8 shadow-lg mb-12">
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold text-gray-900 mb-2">Geographic Concentration Crisis</h2>
              <p className="text-gray-600">The &quot;Big Four&quot; dominate while regions are left behind</p>
            </div>
            
            <div className="grid md:grid-cols-2 gap-8">
              <div>
                <h3 className="text-xl font-semibold mb-6 flex items-center">
                  <TrendingUp className="mr-2 h-6 w-6 text-green-600" />
                  Top Funded Countries
                </h3>
                <div className="space-y-4">
                  {topCountries.map((country, index) => (
                    <CountryCard key={country.country} country={country} rank={index + 1} />
                  ))}
                </div>
              </div>
              
              <div>
                <h3 className="text-xl font-semibold mb-6 flex items-center">
                  <AlertTriangle className="mr-2 h-6 w-6 text-red-600" />
                  Critical Gaps
                </h3>
                <div className="space-y-4">
                  <AlertCard 
                    title="Central Africa"
                    metric="<$20M"
                    description="Entire region with 180M+ people severely underfunded"
                    severity="high"
                  />
                  <AlertCard 
                    title="Gender Disparity"
                    metric="$48M"
                    description="Female founders received lowest funding since 2019"
                    severity="high"
                  />
                  <AlertCard 
                    title="Strategy Gap"
                    metric="39 Countries"
                    description="Still lack national AI strategies"
                    severity="medium"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Sectoral Misalignment */}
      <section className="py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-2 gap-8">
            <div className="bg-white rounded-xl p-8 shadow-lg">
              <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
                <PieChart className="mr-3 h-7 w-7 text-blue-600" />
                Sector Distribution
              </h2>
              <div className="space-y-4">
                {sectorData.map((sector, index) => (
                  <SectorBar key={index} sector={sector} />
                ))}
              </div>
              <div className="mt-6 p-4 bg-red-50 rounded-lg border-l-4 border-red-500">
                <p className="text-sm text-red-800">
                  <strong>Healthcare AI severely underfunded</strong> despite 25% global disease burden
                </p>
              </div>
            </div>

            <div className="bg-white rounded-xl p-8 shadow-lg">
              <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
                <BarChart3 className="mr-3 h-7 w-7 text-purple-600" />
                Major Initiatives
              </h2>
              <div className="space-y-6">
                <div className="border-l-4 border-blue-500 pl-4">
                  <div className="text-2xl font-bold text-blue-600">CAD $100M+</div>
                  <div className="text-sm text-gray-700">AI4D Africa Program Expansion</div>
                  <div className="text-xs text-gray-500 mt-1">Scaled from CAD $20M base</div>
                </div>
                
                <div className="border-l-4 border-green-500 pl-4">
                  <div className="text-2xl font-bold text-green-600">CAD $130M</div>
                  <div className="text-sm text-gray-700">AI4D Funders Collaborative</div>
                  <div className="text-xs text-gray-500 mt-1">Coordinated development funding</div>
                </div>
                
                <div className="border-l-4 border-purple-500 pl-4">
                  <div className="text-2xl font-bold text-purple-600">$641M</div>
                  <div className="text-sm text-gray-700">Private Sector Investment</div>
                  <div className="text-xs text-gray-500 mt-1">2022-2023 period alone</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Interactive Data Visualizations */}
      <section className="py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Funding Landscape Deep Dive</h2>
            <p className="text-gray-600">Interactive analysis of Africa&amp;apos;s AI funding patterns</p>
          </div>

          {/* Funding by Country Chart */}
          <div className="bg-white rounded-xl p-8 shadow-lg mb-8">
            <h3 className="text-2xl font-bold text-gray-900 mb-6">Top Countries by Funding Volume</h3>
            <ResponsiveContainer width="100%" height={400}>
              <ComposedChart data={fundingByCountryData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="country" />
                <YAxis yAxisId="left" orientation="left" />
                <YAxis yAxisId="right" orientation="right" />
                <Tooltip 
                  formatter={(value, name) => [
                    name === 'funding' ? `$${value}M` : value,
                    name === 'funding' ? 'Total Funding' : 'Number of Deals'
                  ]}
                />
                <Legend />
                <Bar yAxisId="left" dataKey="funding" fill="#3B82F6" name="Funding ($M)" />
                <Line yAxisId="right" type="monotone" dataKey="deals" stroke="#EF4444" strokeWidth={3} name="Deals" />
              </ComposedChart>
            </ResponsiveContainer>
          </div>

          {/* Sector Distribution and Timeline */}
          <div className="grid md:grid-cols-2 gap-8 mb-8">
            <div className="bg-white rounded-xl p-8 shadow-lg">
              <h3 className="text-2xl font-bold text-gray-900 mb-6">Sector Distribution</h3>
              <ResponsiveContainer width="100%" height={350}>
                <RechartsPieChart>
                  <Pie
                    data={sectorDistributionData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={(entry) => `${entry.name}: ${entry.value}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {sectorDistributionData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value) => [`${value}%`, 'Share']} />
                  <Legend />
                </RechartsPieChart>
              </ResponsiveContainer>
            </div>

            <div className="bg-white rounded-xl p-8 shadow-lg">
              <h3 className="text-2xl font-bold text-gray-900 mb-6">Funding Growth 2019-2024</h3>
              <ResponsiveContainer width="100%" height={350}>
                <AreaChart data={fundingTimelineData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="year" />
                  <YAxis />
                  <Tooltip formatter={(value) => [`$${value}M`, '']} />
                  <Legend />
                  <Area type="monotone" dataKey="development" stackId="1" stroke="#10B981" fill="#10B981" name="Development Funding" />
                  <Area type="monotone" dataKey="private" stackId="1" stroke="#3B82F6" fill="#3B82F6" name="Private Investment" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Regional Gaps Analysis */}
          <div className="bg-white rounded-xl p-8 shadow-lg">
            <h3 className="text-2xl font-bold text-gray-900 mb-6">Regional Funding Gaps</h3>
            <ResponsiveContainer width="100%" height={400}>
              <BarChart data={regionalGapsData} layout="horizontal">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis dataKey="region" type="category" width={100} />
                <Tooltip 
                  formatter={(value, name) => [
                    name === 'funding' ? `$${value}M` : `${value}M people`,
                    name === 'funding' ? 'Total Funding' : 'Population'
                  ]}
                />
                <Legend />
                <Bar dataKey="funding" fill="#3B82F6" name="Funding ($M)" />
              </BarChart>
            </ResponsiveContainer>
            <div className="mt-6 p-4 bg-red-50 rounded-lg border-l-4 border-red-500">
              <p className="text-sm text-red-800">
                <strong>Critical Gap:</strong> Central Africa receives only $18.3M despite 185M population - less than $0.10 per person
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
