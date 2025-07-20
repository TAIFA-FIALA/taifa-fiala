'use client';

import { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';
import VisualizationErrorBoundary from '@/components/common/VisualizationErrorBoundary';

interface SectorData {
  name: string;
  currentAllocation: number;
  developmentNeed: number;
  description: string;
}

const SectorAllocationChart = () => {
  const [data, setData] = useState<SectorData[]>([]);

  useEffect(() => {
    // Simulated data - replace with actual API call
    const mockData: SectorData[] = [
      {
        name: 'Healthcare',
        currentAllocation: 5.8,
        developmentNeed: 25,
        description: 'Despite bearing 25% of global disease burden'
      },
      {
        name: 'Agriculture',
        currentAllocation: 3.9,
        developmentNeed: 18,
        description: 'Employs 60% of African workforce'
      },
      {
        name: 'Education',
        currentAllocation: 7.2,
        developmentNeed: 15,
        description: 'Critical for long-term development'
      },
      {
        name: 'Financial Services',
        currentAllocation: 20.9,
        developmentNeed: 12,
        description: 'Overrepresented in funding allocation'
      },
      {
        name: 'Infrastructure',
        currentAllocation: 8.4,
        developmentNeed: 20,
        description: 'Essential for economic growth'
      },
      {
        name: 'Climate Tech',
        currentAllocation: 4.2,
        developmentNeed: 15,
        description: 'Addressing environmental challenges'
      },
    ];

    setData(mockData);
  }, []);

  interface TooltipProps {
    active?: boolean;
    payload?: Array<{
      payload: SectorData;
      value: number;
      name: string;
      color: string;
    }>;
    label?: string;
  }

  const CustomTooltip = ({ active, payload, label }: TooltipProps) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white p-4 border border-gray-200 rounded-lg shadow-sm">
          <div className="font-medium text-scholarly-primary mb-2">{label}</div>
          <div className="space-y-1 text-sm">
            <div className="flex items-center justify-between">
              <span className="text-gray-600">Current Allocation:</span>
              <span className="font-medium">{data.currentAllocation}%</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-600">Development Need:</span>
              <span className="font-medium">{data.developmentNeed}%</span>
            </div>
            <div className="mt-2 text-xs text-gray-500">
              {data.description}
            </div>
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <VisualizationErrorBoundary>
      <figure className="chart-container">
        <div className="chart-title" id="figure-2">
          Figure 2: Sectoral Allocation of AI Funding vs Development Priorities
        </div>
      
      <div className="h-[400px]">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={data}
            margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
            <XAxis 
              dataKey="name" 
              tick={{ fill: '#64748B', fontSize: 12 }}
              axisLine={{ stroke: '#E5E7EB' }}
            />
            <YAxis 
              tick={{ fill: '#64748B', fontSize: 12 }}
              axisLine={{ stroke: '#E5E7EB' }}
              label={{ 
                value: 'Percentage (%)', 
                angle: -90, 
                position: 'insideLeft',
                fill: '#64748B',
                fontSize: 12
              }}
            />
            <Tooltip content={<CustomTooltip />} />
            
            {/* Current Allocation Bars */}
            <Bar 
              dataKey="currentAllocation" 
              name="Current Allocation"
              fill="#3E4B59"
              radius={[4, 4, 0, 0]}
            />
            
            {/* Development Need Markers */}
            {data.map((entry, index) => (
              <ReferenceLine
                key={`ref-${index}`}
                y={entry.developmentNeed}
                segment={[{x: index - 0.25, y: entry.developmentNeed}, {x: index + 0.25, y: entry.developmentNeed}]}
                stroke="#BA4D00"
                strokeWidth={2}
                strokeDasharray="3 3"
              />
            ))}
          </BarChart>
        </ResponsiveContainer>
      </div>

      <figcaption className="chart-caption">
        Note: Bars show current funding allocation by sector. Dashed lines indicate estimated development 
        needs based on continental priorities and socioeconomic indicators. Healthcare and Agriculture show 
        significant underinvestment relative to their development importance.
      </figcaption>
      
      {/* Legend */}
      <div className="flex justify-center space-x-8 mt-4">
        <div className="flex items-center space-x-2">
          <div className="w-4 h-4 bg-[#3E4B59]"></div>
          <span className="text-sm text-gray-600">Current Allocation</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-6 h-[2px] bg-[#BA4D00] border-dashed"></div>
          <span className="text-sm text-gray-600">Development Need</span>
        </div>
      </div>
      </figure>
    </VisualizationErrorBoundary>
  );
};

export default SectorAllocationChart;
