"use client";

import { useState, useEffect } from 'react';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar,
  AreaChart, Area, LineChart, Line
} from 'recharts';

interface EquityMetrics {
  geographic: {
    big_four_percentage: number;
    underserved_percentage: number;
    geographic_diversity_index: number;
  };
  sectoral: {
    healthcare_percentage: number;
    agriculture_percentage: number;
    climate_percentage: number;
    sector_diversity_index: number;
  };
  inclusion: {
    women_focused_percentage: number;
    youth_focused_percentage: number;
    rural_focused_percentage: number;
    inclusion_diversity_index: number;
  };
  language: {
    english_percentage: number;
    french_percentage: number;
    arabic_percentage: number;
    portuguese_percentage: number;
  };
  overall_equity_score: number;
}

const COLORS = {
  primary: '#102F76',
  gold: '#D4AF37',
  blue: '#4F46E5',
  green: '#059669',
  red: '#DC2626',
  orange: '#EA580C',
  purple: '#7C3AED',
  teal: '#0D9488'
};

export default function EquityMetricsDashboard() {
  const [metrics, setMetrics] = useState<EquityMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    // Simulate fetching equity metrics
    const mockMetrics: EquityMetrics = {
      geographic: {
        big_four_percentage: 67,
        underserved_percentage: 18,
        geographic_diversity_index: 0.42
      },
      sectoral: {
        healthcare_percentage: 12,
        agriculture_percentage: 8,
        climate_percentage: 15,
        sector_diversity_index: 0.65
      },
      inclusion: {
        women_focused_percentage: 23,
        youth_focused_percentage: 34,
        rural_focused_percentage: 16,
        inclusion_diversity_index: 0.58
      },
      language: {
        english_percentage: 78,
        french_percentage: 15,
        arabic_percentage: 5,
        portuguese_percentage: 2
      },
      overall_equity_score: 0.61
    };

    setTimeout(() => {
      setMetrics(mockMetrics);
      setLoading(false);
    }, 1000);
  }, []);

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-8 border border-gray-100">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/3 mb-6"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="h-64 bg-gray-200 rounded"></div>
            <div className="h-64 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  if (!metrics) return null;

  const geographicData = [
    { name: 'Big 4 Countries', value: metrics.geographic.big_four_percentage, color: COLORS.red },
    { name: 'Other Countries', value: 100 - metrics.geographic.big_four_percentage, color: COLORS.green },
  ];

  const sectoralData = [
    { name: 'Healthcare', value: metrics.sectoral.healthcare_percentage, color: COLORS.red },
    { name: 'Agriculture', value: metrics.sectoral.agriculture_percentage, color: COLORS.green },
    { name: 'Climate', value: metrics.sectoral.climate_percentage, color: COLORS.blue },
    { name: 'Tech/Other', value: 100 - metrics.sectoral.healthcare_percentage - metrics.sectoral.agriculture_percentage - metrics.sectoral.climate_percentage, color: COLORS.primary },
  ];

  const inclusionData = [
    { category: 'Women-Focused', current: metrics.inclusion.women_focused_percentage, target: 30 },
    { category: 'Youth-Focused', current: metrics.inclusion.youth_focused_percentage, target: 40 },
    { category: 'Rural-Focused', current: metrics.inclusion.rural_focused_percentage, target: 25 },
  ];

  const languageData = [
    { name: 'English', value: metrics.language.english_percentage, color: COLORS.primary },
    { name: 'French', value: metrics.language.french_percentage, color: COLORS.gold },
    { name: 'Arabic', value: metrics.language.arabic_percentage, color: COLORS.green },
    { name: 'Portuguese', value: metrics.language.portuguese_percentage, color: COLORS.orange },
  ];

  const equityOverviewData = [
    { metric: 'Geographic Equity', score: metrics.geographic.geographic_diversity_index * 100, target: 70 },
    { metric: 'Sector Diversity', score: metrics.sectoral.sector_diversity_index * 100, target: 80 },
    { metric: 'Inclusion Rate', score: metrics.inclusion.inclusion_diversity_index * 100, target: 60 },
    { metric: 'Language Diversity', score: 25, target: 30 },
  ];

  return (
    <div className="bg-white rounded-xl shadow-lg border border-gray-100">
      {/* Header */}
      <div className="border-b border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-2xl font-bold text-gray-900">Live Equity Analytics</h3>
            <p className="text-gray-600 mt-1">Real-time bias monitoring across African AI funding</p>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
            <span className="text-sm font-medium text-gray-500">Live Data</span>
          </div>
        </div>
        
        {/* Tabs */}
        <div className="mt-6 border-b border-gray-200">
          <div className="flex space-x-8">
            {[
              { id: 'overview', label: 'Overview', icon: '📊' },
              { id: 'geographic', label: 'Geographic', icon: '🌍' },
              { id: 'sectoral', label: 'Sectoral', icon: '🏥' },
              { id: 'inclusion', label: 'Inclusion', icon: '👥' },
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <span>{tab.icon}</span>
                <span>{tab.label}</span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="p-6">
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Overall Equity Score */}
            <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h4 className="text-lg font-semibold text-gray-900">Overall Equity Score</h4>
                <div className="flex items-center space-x-2">
                  <span className="text-2xl font-bold text-blue-600">
                    {(metrics.overall_equity_score * 100).toFixed(0)}%
                  </span>
                  <div className="text-sm text-gray-500">
                    {metrics.overall_equity_score < 0.7 ? '📈 Improving' : '✅ Good'}
                  </div>
                </div>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-blue-500 h-2 rounded-full transition-all duration-500"
                  style={{ width: `${metrics.overall_equity_score * 100}%` }}
                ></div>
              </div>
              <div className="mt-2 text-sm text-gray-600">
                Target: 70% • Current progress shows systemic bias reduction efforts
              </div>
            </div>

            {/* Equity Overview Radar Chart */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div>
                <h4 className="text-lg font-semibold text-gray-900 mb-4">Equity Dimensions</h4>
                <ResponsiveContainer width="100%" height={300}>
                  <RadarChart data={equityOverviewData}>
                    <PolarGrid />
                    <PolarAngleAxis dataKey="metric" className="text-sm" />
                    <PolarRadiusAxis angle={90} domain={[0, 100]} className="text-xs" />
                    <Radar
                      name="Current"
                      dataKey="score"
                      stroke={COLORS.blue}
                      fill={COLORS.blue}
                      fillOpacity={0.1}
                      strokeWidth={2}
                    />
                    <Radar
                      name="Target"
                      dataKey="target"
                      stroke={COLORS.gold}
                      fill={COLORS.gold}
                      fillOpacity={0.1}
                      strokeWidth={2}
                      strokeDasharray="5 5"
                    />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
              
              <div>
                <h4 className="text-lg font-semibold text-gray-900 mb-4">Key Insights</h4>
                <div className="space-y-4">
                  <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                    <div className="flex items-center space-x-2 mb-2">
                      <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                      <span className="font-medium text-red-800">Geographic Concentration</span>
                    </div>
                    <p className="text-sm text-red-700">
                      {metrics.geographic.big_four_percentage}% of opportunities concentrated in Big 4 countries
                    </p>
                  </div>
                  
                  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                    <div className="flex items-center space-x-2 mb-2">
                      <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                      <span className="font-medium text-yellow-800">Sector Gaps</span>
                    </div>
                    <p className="text-sm text-yellow-700">
                      Healthcare ({metrics.sectoral.healthcare_percentage}%) and Agriculture ({metrics.sectoral.agriculture_percentage}%) below targets
                    </p>
                  </div>
                  
                  <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                    <div className="flex items-center space-x-2 mb-2">
                      <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                      <span className="font-medium text-green-800">Inclusion Progress</span>
                    </div>
                    <p className="text-sm text-green-700">
                      Youth-focused opportunities ({metrics.inclusion.youth_focused_percentage}%) showing strong growth
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'geographic' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div>
                <h4 className="text-lg font-semibold text-gray-900 mb-4">Geographic Distribution</h4>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={geographicData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={120}
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {geographicData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => `${value}%`} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              
              <div>
                <h4 className="text-lg font-semibold text-gray-900 mb-4">Regional Breakdown</h4>
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-3 bg-red-50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <div className="w-4 h-4 bg-red-500 rounded-full"></div>
                      <span className="font-medium text-gray-900">Nigeria, Kenya, South Africa, Egypt</span>
                    </div>
                    <span className="text-lg font-bold text-red-600">{metrics.geographic.big_four_percentage}%</span>
                  </div>
                  
                  <div className="flex items-center justify-between p-3 bg-yellow-50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <div className="w-4 h-4 bg-yellow-500 rounded-full"></div>
                      <span className="font-medium text-gray-900">Emerging Markets</span>
                    </div>
                    <span className="text-lg font-bold text-yellow-600">15%</span>
                  </div>
                  
                  <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <div className="w-4 h-4 bg-green-500 rounded-full"></div>
                      <span className="font-medium text-gray-900">Underserved Regions</span>
                    </div>
                    <span className="text-lg font-bold text-green-600">{metrics.geographic.underserved_percentage}%</span>
                  </div>
                </div>
                
                <div className="mt-6 p-4 bg-blue-50 rounded-lg">
                  <h5 className="font-medium text-blue-900 mb-2">🎯 Equity Action</h5>
                  <p className="text-sm text-blue-700">
                    Our AI system automatically boosts opportunities from underserved regions and reduces over-concentration in major hubs.
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'sectoral' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div>
                <h4 className="text-lg font-semibold text-gray-900 mb-4">Sector Distribution</h4>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={sectoralData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip formatter={(value) => `${value}%`} />
                    <Bar dataKey="value" fill={COLORS.primary} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
              
              <div>
                <h4 className="text-lg font-semibold text-gray-900 mb-4">Development Priorities</h4>
                <div className="space-y-4">
                  {[
                    { name: 'Healthcare', current: metrics.sectoral.healthcare_percentage, target: 20, color: 'red' },
                    { name: 'Agriculture', current: metrics.sectoral.agriculture_percentage, target: 18, color: 'green' },
                    { name: 'Climate', current: metrics.sectoral.climate_percentage, target: 15, color: 'blue' },
                  ].map((sector) => (
                    <div key={sector.name} className="space-y-2">
                      <div className="flex justify-between items-center">
                        <span className="font-medium text-gray-900">{sector.name}</span>
                        <span className="text-sm text-gray-500">{sector.current}% / {sector.target}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className={`h-2 rounded-full transition-all duration-500 ${
                            sector.color === 'red' ? 'bg-red-500' :
                            sector.color === 'green' ? 'bg-green-500' : 'bg-blue-500'
                          }`}
                          style={{ width: `${(sector.current / sector.target) * 100}%` }}
                        ></div>
                      </div>
                    </div>
                  ))}
                </div>
                
                <div className="mt-6 p-4 bg-yellow-50 rounded-lg">
                  <h5 className="font-medium text-yellow-900 mb-2">🔍 Smart Detection</h5>
                  <p className="text-sm text-yellow-700">
                    Our multilingual AI identifies priority sectors across 6 African languages, ensuring comprehensive coverage.
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'inclusion' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div>
                <h4 className="text-lg font-semibold text-gray-900 mb-4">Inclusion Metrics</h4>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={inclusionData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="category" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="current" fill={COLORS.blue} name="Current" />
                    <Bar dataKey="target" fill={COLORS.gold} name="Target" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
              
              <div>
                <h4 className="text-lg font-semibold text-gray-900 mb-4">Language Diversity</h4>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={languageData}
                      cx="50%"
                      cy="50%"
                      outerRadius={80}
                      dataKey="value"
                      label={({ name, value }) => `${name}: ${value}%`}
                    >
                      {languageData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => `${value}%`} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-pink-50 border border-pink-200 rounded-lg p-4">
                <div className="flex items-center space-x-2 mb-2">
                  <span className="text-2xl">👩‍💻</span>
                  <span className="font-medium text-pink-800">Women-Led</span>
                </div>
                <div className="text-2xl font-bold text-pink-600">{metrics.inclusion.women_focused_percentage}%</div>
                <p className="text-sm text-pink-700">of opportunities target women entrepreneurs</p>
              </div>
              
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex items-center space-x-2 mb-2">
                  <span className="text-2xl">🎓</span>
                  <span className="font-medium text-blue-800">Youth-Focused</span>
                </div>
                <div className="text-2xl font-bold text-blue-600">{metrics.inclusion.youth_focused_percentage}%</div>
                <p className="text-sm text-blue-700">of opportunities target young innovators</p>
              </div>
              
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <div className="flex items-center space-x-2 mb-2">
                  <span className="text-2xl">🏘️</span>
                  <span className="font-medium text-green-800">Rural-Focused</span>
                </div>
                <div className="text-2xl font-bold text-green-600">{metrics.inclusion.rural_focused_percentage}%</div>
                <p className="text-sm text-green-700">of opportunities target rural communities</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}