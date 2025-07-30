'use client';

import { XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart as RechartsPieChart, Pie, Cell, ComposedChart, Line, Bar } from 'recharts';

interface CountryData {
  country: string;
  funding: number;
  deals: number;
  color: string;
  share: string;
}

interface SectorData {
  name: string;
  value: number;
  funding: number;
}

interface TimelineData {
  year: string;
  amount: number;
  type: string;
}

interface FundingChartsProps {
  fundingByCountryData: CountryData[];
  sectorDistributionData: SectorData[];
  fundingTimelineData: TimelineData[];
  COLORS: string[];
}

export default function FundingCharts({
  fundingByCountryData,
  sectorDistributionData,
  COLORS
}: FundingChartsProps) {
  return (
    <>
      {/* Funding by Country Chart */}
      <div className="bg-white rounded-xl p-8 shadow-lg mb-8 border border-slate-200">
        <h3 className="text-2xl font-bold text-site-slate mb-6">Top Countries by Funding Volume</h3>
        <ResponsiveContainer width="100%" height={400}>
          <ComposedChart data={fundingByCountryData}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--color-neutral-200)" />
            <XAxis dataKey="country" tick={{ fill: 'var(--color-slate-600)' }} />
            <YAxis yAxisId="left" orientation="left" tick={{ fill: 'var(--color-slate-600)' }} />
            <YAxis yAxisId="right" orientation="right" tick={{ fill: 'var(--color-slate-600)' }} />
            <Tooltip 
              formatter={(value, name) => [
                name === 'funding' ? `$${value}M` : value,
                name === 'funding' ? 'Total Funding' : 'Number of Deals'
              ]}
              contentStyle={{ 
                backgroundColor: 'white', 
                border: '1px solid var(--color-slate-200)',
                borderRadius: '8px',
                color: 'var(--color-site-slate)'
              }}
            />
            <Legend />
            <Bar yAxisId="left" dataKey="funding" fill="var(--color-site-slate)" name="Funding ($M)" />
            <Line yAxisId="right" type="monotone" dataKey="deals" stroke="var(--color-site-brown)" strokeWidth={3} name="Deals" />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* Sector Distribution Chart Only - Remove Empty Timeline */}
      <div className="bg-white rounded-xl p-8 shadow-lg border border-slate-200">
        <h3 className="text-2xl font-bold text-site-slate mb-6">Sector Distribution</h3>
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
                backgroundColor: 'white', 
                border: '1px solid var(--color-slate-200)',
                borderRadius: '8px',
                color: 'var(--color-site-slate)'
              }}
            />
          </RechartsPieChart>
        </ResponsiveContainer>
      </div>
    </>
  );
}
