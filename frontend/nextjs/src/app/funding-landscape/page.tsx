import { TrendingUp, AlertTriangle, DollarSign, Briefcase, Target, BarChart3, PieChart, MapPin, Globe, Users, Shield, Heart, Calendar } from 'lucide-react';
import React from 'react';
import { Metadata } from 'next';
import FundingCharts from './components/FundingCharts';

export const metadata: Metadata = {
  title: 'African AI Funding Landscape | TAIFA-FIALA',
  description: 'Comprehensive analysis of AI funding across Africa (2019-2024). Discover funding patterns, geographic concentration, and sector distribution in African AI development.',
  keywords: 'African AI funding, venture capital Africa, AI investment landscape, African startups, technology funding Africa',
};

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
  <div className={`bg-white/80 backdrop-blur-sm p-8 rounded-2xl border-l-4 ${metric.color} shadow-xl hover:shadow-2xl hover:-translate-y-2 transition-all duration-300 animate-fadeInUp`}>
    <div className="flex items-center justify-between">
      <div>
        <div className="text-4xl font-bold text-taifa-primary mb-2">{metric.value}</div>
        <div className="text-sm text-taifa-muted font-medium">{metric.label}</div>
        {metric.trend && (
          <div className={`inline-flex items-center mt-2 px-2 py-1 rounded-full text-xs font-medium ${
            metric.trend === 'up' ? 'bg-green-100 text-green-800' : 
            metric.trend === 'down' ? 'bg-red-100 text-red-800' : 
            'bg-taifa-muted/10 text-taifa-muted'
          }`}>
            <TrendingUp className={`h-3 w-3 mr-1 ${
              metric.trend === 'down' ? 'rotate-180' : ''
            }`} />
            {metric.trend}
          </div>
        )}
      </div>
      <div className="text-4xl text-taifa-secondary/60">{metric.icon}</div>
    </div>
  </div>
);

const CountryCard: React.FC<{ country: CountryFunding; rank: number }> = ({ country, rank }) => (
  <div className="bg-white/80 backdrop-blur-sm p-6 rounded-2xl border border-taifa-secondary/20 hover:border-taifa-primary hover:shadow-xl hover:-translate-y-1 transition-all duration-300">
    <div className="flex items-center justify-between mb-3">
      <div className="flex items-center">
        <div className="w-8 h-8 bg-taifa-primary/10 rounded-full flex items-center justify-center mr-3 border border-taifa-primary/20">
          <span className="text-sm font-bold text-taifa-primary">#{rank}</span>
        </div>
        <span className="text-lg font-semibold text-taifa-primary">{country.country}</span>
      </div>
      <MapPin className="h-6 w-6 text-taifa-secondary" />
    </div>
    <div className="text-3xl font-bold text-taifa-accent mb-2">{country.amount}</div>
    {country.avgPerStartup && (
      <div className="text-sm text-taifa-muted font-medium bg-taifa-yellow/10 px-3 py-1 rounded-full inline-block">
        Avg: {country.avgPerStartup}/startup
      </div>
    )}
  </div>
);

const SectorBar: React.FC<{ sector: SectorData }> = ({ sector }) => (
  <div className="mb-4">
    <div className="flex justify-between items-center mb-2">
      <span className="text-sm font-medium text-taifa-primary">{sector.sector}</span>
      <span className="text-sm text-taifa-muted">{sector.percentage}%</span>
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
  const severityConfig = {
    high: {
      borderColor: 'border-red-500',
      bgColor: 'bg-gradient-to-br from-red-50 to-red-100',
      textColor: 'text-red-800',
      iconBg: 'bg-red-100',
      iconBorder: 'border-red-200',
      icon: <AlertTriangle className="h-5 w-5 text-red-600" />
    },
    medium: {
      borderColor: 'border-yellow-500',
      bgColor: 'bg-gradient-to-br from-yellow-50 to-yellow-100',
      textColor: 'text-yellow-800',
      iconBg: 'bg-yellow-100',
      iconBorder: 'border-yellow-200',
      icon: <AlertTriangle className="h-5 w-5 text-yellow-600" />
    },
    low: {
      borderColor: 'border-green-500',
      bgColor: 'bg-gradient-to-br from-green-50 to-green-100',
      textColor: 'text-green-800',
      iconBg: 'bg-green-100',
      iconBorder: 'border-green-200',
      icon: <Shield className="h-5 w-5 text-green-600" />
    }
  };

  const config = severityConfig[severity];

  return (
    <div className={`p-6 rounded-2xl border-l-4 ${config.borderColor} ${config.bgColor} shadow-lg hover:shadow-xl transition-all duration-300 hover:-translate-y-1`}>
      <div className="flex justify-between items-start mb-4">
        <div className="flex items-center">
          <div className={`w-10 h-10 ${config.iconBg} rounded-full flex items-center justify-center mr-3 border ${config.iconBorder}`}>
            {config.icon}
          </div>
          <h4 className={`font-bold text-lg ${config.textColor}`}>{title}</h4>
        </div>
        <span className={`text-3xl font-bold ${config.textColor}`}>{metric}</span>
      </div>
      <p className={`text-sm leading-relaxed ${config.textColor}/80 ml-13`}>{description}</p>
    </div>
  );
};

export default function FundingLandscapePage() {
  // Colors for charts
  const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#06B6D4', '#84CC16', '#F97316'];

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
    <div className="min-h-screen bg-gradient-to-br from-taifa-yellow/5 via-white to-taifa-secondary/5">
      {/* Hero Section */}
      <header className="bg-gradient-to-br from-taifa-primary via-taifa-secondary to-taifa-olive relative overflow-hidden">
        <div className="absolute inset-0 bg-black/10"></div>
        <div className="relative max-w-7xl mx-auto py-20 px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <div className="inline-flex items-center px-4 py-2 bg-white/20 border border-white/30 rounded-full text-sm font-medium text-white mb-6 animate-fadeInUp">
              <BarChart3 className="h-4 w-4 mr-2" />
              Comprehensive Analysis
            </div>
            <h1 className="text-5xl md:text-6xl font-bold text-white mb-6 animate-fadeInUp" style={{ animationDelay: '0.1s' }}>
              African AI Funding
              <span className="block text-taifa-yellow">Landscape</span>
            </h1>
            <p className="text-xl text-taifa-yellow mb-8 max-w-3xl mx-auto animate-fadeInUp" style={{ animationDelay: '0.2s' }}>
              Comprehensive analysis revealing funding patterns, geographic concentration, and sector distribution across Africa (2019-2024)
            </p>
            
            {/* Key Statistics */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto animate-fadeInUp" style={{ animationDelay: '0.3s' }}>
              <div className="bg-white/10 backdrop-blur-sm p-6 rounded-2xl border border-white/20">
                <div className="text-3xl font-bold text-white mb-2">$800M+</div>
                <div className="text-taifa-yellow text-sm">Total AI Funding</div>
              </div>
              <div className="bg-white/10 backdrop-blur-sm p-6 rounded-2xl border border-white/20">
                <div className="text-3xl font-bold text-white mb-2">54</div>
                <div className="text-taifa-yellow text-sm">African Countries</div>
              </div>
              <div className="bg-white/10 backdrop-blur-sm p-6 rounded-2xl border border-white/20">
                <div className="text-3xl font-bold text-white mb-2">83%</div>
                <div className="text-taifa-yellow text-sm">Concentrated in 4 Countries</div>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Key Metrics Dashboard */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <div className="inline-flex items-center px-4 py-2 bg-taifa-secondary/10 border border-taifa-secondary/20 rounded-full text-sm font-medium text-taifa-secondary mb-6 animate-fadeInUp">
              <DollarSign className="h-4 w-4 mr-2" />
              Key Insights
            </div>
            <h2 className="text-4xl font-bold text-taifa-primary mb-4 animate-fadeInUp" style={{ animationDelay: '0.1s' }}>Funding Overview</h2>
            <p className="text-lg text-taifa-muted max-w-3xl mx-auto animate-fadeInUp" style={{ animationDelay: '0.2s' }}>
              Critical metrics revealing the current state of AI investment across the African continent
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-16">
            {keyMetrics.map((metric, index) => (
              <div key={index} style={{ animationDelay: `${0.3 + index * 0.1}s` }}>
                <MetricCard metric={metric} />
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Geographic Concentration Story */}
      <section className="py-20 bg-gradient-to-br from-taifa-accent/5 to-taifa-olive/5">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-white/80 backdrop-blur-sm rounded-3xl p-12 shadow-2xl mb-16 border border-taifa-secondary/10">
            <div className="text-center mb-12">
              <div className="inline-flex items-center px-4 py-2 bg-red-100 border border-red-200 rounded-full text-sm font-medium text-red-800 mb-6 animate-fadeInUp">
                <AlertTriangle className="h-4 w-4 mr-2" />
                Critical Issue
              </div>
              <h2 className="text-4xl font-bold text-taifa-primary mb-4 animate-fadeInUp" style={{ animationDelay: '0.1s' }}>Geographic Concentration Crisis</h2>
              <p className="text-xl text-taifa-muted max-w-3xl mx-auto animate-fadeInUp" style={{ animationDelay: '0.2s' }}>
                The "Big Four" countries dominate AI funding while entire regions are systematically left behind
              </p>
            </div>
            
            <div className="grid md:grid-cols-2 gap-12">
              <div className="animate-fadeInUp" style={{ animationDelay: '0.3s' }}>
                <div className="flex items-center mb-8">
                  <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mr-4 border border-green-200">
                    <TrendingUp className="h-6 w-6 text-green-600" />
                  </div>
                  <h3 className="text-2xl font-bold text-taifa-primary">Top Funded Countries</h3>
                </div>
                <div className="space-y-6">
                  {topCountries.map((country, index) => (
                    <div key={country.country} style={{ animationDelay: `${0.4 + index * 0.1}s` }} className="animate-fadeInUp">
                      <CountryCard country={country} rank={index + 1} />
                    </div>
                  ))}
                </div>
              </div>
              
              <div className="animate-fadeInUp" style={{ animationDelay: '0.3s' }}>
                <div className="flex items-center mb-8">
                  <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mr-4 border border-red-200">
                    <AlertTriangle className="h-6 w-6 text-red-600" />
                  </div>
                  <h3 className="text-2xl font-bold text-taifa-primary">Critical Gaps</h3>
                </div>
                <div className="space-y-6">
                  <div className="animate-fadeInUp" style={{ animationDelay: '0.4s' }}>
                    <AlertCard 
                      title="Central Africa"
                      metric="<$20M"
                      description="Entire region with 180M+ people severely underfunded"
                      severity="high"
                    />
                  </div>
                  <div className="animate-fadeInUp" style={{ animationDelay: '0.5s' }}>
                    <AlertCard 
                      title="Gender Disparity"
                      metric="$48M"
                      description="Female founders received lowest funding since 2019"
                      severity="high"
                    />
                  </div>
                  <div className="animate-fadeInUp" style={{ animationDelay: '0.6s' }}>
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
        </div>
      </section>

      {/* Sectoral Misalignment */}
      <section className="py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-2 gap-8">
            <div className="bg-white rounded-xl p-8 shadow-lg">
              <h2 className="text-2xl font-bold text-taifa-primary mb-6 flex items-center">
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
              <h2 className="text-2xl font-bold text-taifa-primary mb-6 flex items-center">
                <BarChart3 className="mr-3 h-7 w-7 text-purple-600" />
                Major Initiatives
              </h2>
              <div className="space-y-6">
                <div className="border-l-4 border-blue-500 pl-4">
                  <div className="text-2xl font-bold text-blue-600">CAD $100M+</div>
                  <div className="text-sm text-taifa-primary">AI4D Africa Program Expansion</div>
                  <div className="text-xs text-taifa-muted mt-1">Scaled from CAD $20M base</div>
                </div>
                
                <div className="border-l-4 border-green-500 pl-4">
                  <div className="text-2xl font-bold text-green-600">CAD $130M</div>
                  <div className="text-sm text-taifa-primary">AI4D Funders Collaborative</div>
                  <div className="text-xs text-taifa-muted mt-1">Coordinated development funding</div>
                </div>
                
                <div className="border-l-4 border-purple-500 pl-4">
                  <div className="text-2xl font-bold text-purple-600">$641M</div>
                  <div className="text-sm text-taifa-primary">Private Sector Investment</div>
                  <div className="text-xs text-taifa-muted mt-1">2022-2023 period alone</div>
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
            <h2 className="text-3xl font-bold text-taifa-primary mb-4">Funding Landscape Deep Dive</h2>
            <p className="text-taifa-muted">Interactive analysis of Africa&apos;s AI funding patterns</p>
          </div>

          <FundingCharts 
            fundingByCountryData={fundingByCountryData}
            sectorDistributionData={sectorDistributionData}
            fundingTimelineData={fundingTimelineData}
            COLORS={COLORS}
          />

          {/* Regional Gaps Analysis - keeping this separate for now */}
          <div className="bg-white rounded-xl p-8 shadow-lg">
            <h3 className="text-2xl font-bold text-taifa-primary mb-6">Regional Funding Gaps</h3>
            <div className="space-y-4">
              {regionalGapsData.map((region, index) => (
                <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div>
                    <h4 className="font-semibold text-taifa-primary">{region.region}</h4>
                    <p className="text-sm text-taifa-muted">{region.population}M people</p>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold text-blue-600">${region.funding}M</div>
                    <div className="text-xs text-taifa-muted">Total Funding</div>
                  </div>
                </div>
              ))}
            </div>
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
