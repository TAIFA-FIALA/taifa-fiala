'use client';

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart as RechartsPieChart, Pie, Cell, ComposedChart, Line } from 'recharts';

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
      <div className="bg-taifa-white rounded-xl p-8 shadow-lg mb-8 border border-taifa-border">
        <h3 className="text-2xl font-bold text-taifa-primary mb-6">Top Countries by Funding Volume</h3>
        <ResponsiveContainer width="100%" height={400}>
          <ComposedChart data={fundingByCountryData}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--color-taifa-border)" />
            <XAxis dataKey="country" tick={{ fill: 'var(--color-taifa-muted)' }} />
            <YAxis yAxisId="left" orientation="left" tick={{ fill: 'var(--color-taifa-muted)' }} />
            <YAxis yAxisId="right" orientation="right" tick={{ fill: 'var(--color-taifa-muted)' }} />
            <Tooltip 
              formatter={(value, name) => [
                name === 'funding' ? `$${value}M` : value,
                name === 'funding' ? 'Total Funding' : 'Number of Deals'
              ]}
              contentStyle={{ 
                backgroundColor: 'var(--color-taifa-white)', 
                border: '1px solid var(--color-taifa-border)',
                borderRadius: '8px',
                color: 'var(--color-taifa-primary)'
              }}
            />
            <Legend />
            <Bar yAxisId="left" dataKey="funding" fill="var(--color-taifa-primary)" name="Funding ($M)" />
            <Line yAxisId="right" type="monotone" dataKey="deals" stroke="var(--color-taifa-red)" strokeWidth={3} name="Deals" />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* Sector Distribution Chart Only - Remove Empty Timeline */}
      <div className="bg-taifa-white rounded-xl p-8 shadow-lg border border-taifa-border">
        <h3 className="text-2xl font-bold text-taifa-primary mb-6">Sector Distribution</h3>
        <ResponsiveContainer width="100%" height={400}>
          <RechartsPieChart>
            <Pie
              data={sectorDistributionData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percent }) => `${name} ${percent ? (percent * 100).toFixed(0) : 0}%`}
              outerRadius={140}
              fill="#8884d8"
              dataKey="value"
            >
              {sectorDistributionData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip 
              formatter={(value) => [`$${value}M`, 'Funding']}
              contentStyle={{ 
                backgroundColor: 'var(--color-taifa-white)', 
                border: '1px solid var(--color-taifa-border)',
                borderRadius: '8px',
                color: 'var(--color-taifa-primary)'
              }}
            />
          </RechartsPieChart>
        </ResponsiveContainer>
      </div>
    </>
  );
}
