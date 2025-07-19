'use client';

import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  ComposedChart,
  Area,
  AreaChart,
  Legend
} from 'recharts';
import { TrendingDown, AlertCircle, Users, DollarSign } from 'lucide-react';

const GenderEquityDashboard: React.FC = () => {
  // Data from the funding landscape report
  const genderTimelineData = [
    { year: '2019', female: 67, male: 234, femalePercent: 22.3 },
    { year: '2020', female: 58, male: 267, femalePercent: 17.8 },
    { year: '2021', female: 52, male: 289, femalePercent: 15.3 },
    { year: '2022', female: 49, male: 312, femalePercent: 13.6 },
    { year: '2023', female: 45, male: 334, femalePercent: 11.9 },
    { year: '2024', female: 48, male: 342, femalePercent: 12.3 }
  ];

  const sectorGenderData = [
    { sector: 'Healthcare', female: 24.1, male: 75.9, femaleLeadership: 'High' },
    { sector: 'Education', female: 31.2, male: 68.8, femaleLeadership: 'High' },
    { sector: 'Agriculture', female: 18.7, male: 81.3, femaleLeadership: 'Medium' },
    { sector: 'FinTech', female: 8.9, male: 91.1, femaleLeadership: 'Low' },
    { sector: 'Climate AI', female: 15.3, male: 84.7, femaleLeadership: 'Medium' },
    { sector: 'Infrastructure', female: 6.2, male: 93.8, femaleLeadership: 'Low' }
  ];

  const regionalGenderData = [
    { region: 'East Africa', female: 14.8, total: 287 },
    { region: 'West Africa', female: 11.2, total: 198 },
    { region: 'North Africa', female: 9.8, total: 156 },
    { region: 'Southern Africa', female: 13.4, total: 134 },
    { region: 'Central Africa', female: 8.9, total: 45 }
  ];

  const fundingComparisonData = [
    { category: 'Average Deal Size', female: 1.2, male: 4.8 },
    { category: 'Series A Success', female: 23, male: 67 },
    { category: 'Follow-on Funding', female: 18, male: 54 },
    { category: 'Exits', female: 3, male: 23 }
  ];

  const EARTH_COLORS = {
    terracotta: '#D2691E',
    sage: '#9CAF88',
    ochre: '#CC7722',
    warmGray: '#8B7D6B',
    deepRed: '#A0522D',
    mutedGreen: '#6B8E4E'
  };

  return (
    <div className="space-y-8">
      {/* Header with Key Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-red-50 p-4 rounded-lg border-l-4 border-red-400">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-2xl font-bold text-red-700">12.3%</div>
              <div className="text-sm text-red-600">Female-led orgs 2024</div>
            </div>
            <TrendingDown className="h-8 w-8 text-red-400" />
          </div>
        </div>
        
        <div className="bg-orange-50 p-4 rounded-lg border-l-4 border-orange-400">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-2xl font-bold text-orange-700">$48M</div>
              <div className="text-sm text-orange-600">Female founder funding</div>
            </div>
            <DollarSign className="h-8 w-8 text-orange-400" />
          </div>
        </div>
        
        <div className="bg-yellow-50 p-4 rounded-lg border-l-4 border-yellow-400">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-2xl font-bold text-yellow-700">6 years</div>
              <div className="text-sm text-yellow-600">Declining trend</div>
            </div>
            <AlertCircle className="h-8 w-8 text-yellow-400" />
          </div>
        </div>
        
        <div className="bg-blue-50 p-4 rounded-lg border-l-4 border-blue-400">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-2xl font-bold text-blue-700">1:4</div>
              <div className="text-sm text-blue-600">Female:Male ratio</div>
            </div>
            <Users className="h-8 w-8 text-blue-400" />
          </div>
        </div>
      </div>

      {/* Main Visualizations Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        
        {/* Timeline Chart - Showing Decline */}
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <h4 className="text-lg font-semibold text-gray-800 mb-4">
            Female Leadership Decline (2019-2024)
          </h4>
          <ResponsiveContainer width="100%" height={300}>
            <ComposedChart data={genderTimelineData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="year" stroke="#6b7280" />
              <YAxis yAxisId="left" stroke="#6b7280" />
              <YAxis yAxisId="right" orientation="right" stroke="#ef4444" />
              <Tooltip 
                formatter={(value, name) => [
                  typeof value === 'number' ? (name.includes('Percent') ? `${value}%` : value) : value,
                  name === 'femalePercent' ? 'Female %' : name === 'female' ? 'Female-led' : 'Male-led'
                ]}
              />
              <Legend />
              <Bar yAxisId="left" dataKey="female" fill={EARTH_COLORS.terracotta} name="Female-led" />
              <Bar yAxisId="left" dataKey="male" fill={EARTH_COLORS.warmGray} name="Male-led" />
              <Line 
                yAxisId="right" 
                type="monotone" 
                dataKey="femalePercent" 
                stroke="#ef4444" 
                strokeWidth={3}
                name="Female %"
              />
            </ComposedChart>
          </ResponsiveContainer>
        </div>

        {/* Sectoral Gender Distribution */}
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <h4 className="text-lg font-semibold text-gray-800 mb-4">
            Gender Representation by Sector
          </h4>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={sectorGenderData} layout="horizontal">
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis type="number" domain={[0, 100]} stroke="#6b7280" />
              <YAxis dataKey="sector" type="category" width={80} stroke="#6b7280" />
              <Tooltip formatter={(value) => [`${value}%`, '']} />
              <Legend />
              <Bar dataKey="female" fill={EARTH_COLORS.terracotta} name="Female %" />
              <Bar dataKey="male" fill={EARTH_COLORS.warmGray} name="Male %" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Regional Analysis */}
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <h4 className="text-lg font-semibold text-gray-800 mb-4">
            Regional Gender Disparities
          </h4>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={regionalGenderData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="region" stroke="#6b7280" />
              <YAxis stroke="#6b7280" />
              <Tooltip 
                formatter={(value, name) => [
                  `${value}%`,
                  'Female Leadership'
                ]}
              />
              <Bar dataKey="female" fill={EARTH_COLORS.ochre} name="Female Leadership %" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Funding Gap Analysis */}
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <h4 className="text-lg font-semibold text-gray-800 mb-4">
            Funding Performance Gaps
          </h4>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={fundingComparisonData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="category" stroke="#6b7280" />
              <YAxis stroke="#6b7280" />
              <Tooltip formatter={(value, name) => [
                name === 'female' || name === 'male' ? 
                  (value > 10 ? `$${value}M` : `${value}%`) : value,
                name === 'female' ? 'Female' : 'Male'
              ]} />
              <Legend />
              <Bar dataKey="female" fill={EARTH_COLORS.terracotta} name="Female-led" />
              <Bar dataKey="male" fill={EARTH_COLORS.warmGray} name="Male-led" />
            </BarChart>
          </ResponsiveContainer>
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
