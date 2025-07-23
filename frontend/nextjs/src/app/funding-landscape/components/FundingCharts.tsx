'use client';

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart as RechartsPieChart, Pie, Cell, Line, ComposedChart, Area, AreaChart } from 'recharts';

interface FundingChartsProps {
  fundingByCountryData: any[];
  sectorDistributionData: any[];
  fundingTimelineData: any[];
  COLORS: string[];
}

export default function FundingCharts({ 
  fundingByCountryData, 
  sectorDistributionData, 
  fundingTimelineData, 
  COLORS 
}: FundingChartsProps) {
  return (
    <>
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
                label={({ name, percent }) => `${name} ${percent ? (percent * 100).toFixed(0) : 0}%`}
                outerRadius={120}
                fill="#8884d8"
                dataKey="value"
              >
                {sectorDistributionData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip formatter={(value) => [`$${value}M`, 'Funding']} />
            </RechartsPieChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-xl p-8 shadow-lg">
          <h3 className="text-2xl font-bold text-gray-900 mb-6">Funding Timeline (2019-2024)</h3>
          <ResponsiveContainer width="100%" height={350}>
            <AreaChart data={fundingTimelineData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="year" />
              <YAxis />
              <Tooltip formatter={(value) => [`$${value}M`, 'Funding']} />
              <Area type="monotone" dataKey="funding" stroke="#10B981" fill="#10B981" fillOpacity={0.3} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    </>
  );
}
