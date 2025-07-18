'use client';

import { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from 'recharts';
import { TrendingUp, Database, RefreshCw } from 'lucide-react';

interface DataPoint {
  date: string;
  records: number;
  dailyGrowth: number;
}

interface DatabaseGrowthChartProps {
  className?: string;
}

export default function DatabaseGrowthChart({ className = '' }: DatabaseGrowthChartProps) {
  const [data, setData] = useState<DataPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [totalRecords, setTotalRecords] = useState(0);
  const [weeklyGrowth, setWeeklyGrowth] = useState(0);

  useEffect(() => {
    // Simulate fetching real data - replace with actual API call
    const fetchDatabaseGrowth = async () => {
      try {
        // Mock data for demonstration - replace with actual API
        const mockData = generateMockData();
        setData(mockData);
        setTotalRecords(mockData[mockData.length - 1]?.records || 0);
        
        // Calculate weekly growth
        const weekAgo = mockData[mockData.length - 8]?.records || 0;
        const current = mockData[mockData.length - 1]?.records || 0;
        const growth = ((current - weekAgo) / weekAgo) * 100;
        setWeeklyGrowth(growth);
        
      } catch (error) {
        console.error('Error fetching database growth:', error);
        // Fallback to mock data
        const mockData = generateMockData();
        setData(mockData);
        setTotalRecords(mockData[mockData.length - 1]?.records || 0);
      } finally {
        setLoading(false);
      }
    };

    fetchDatabaseGrowth();
    
    // Refresh every 5 minutes
    const interval = setInterval(fetchDatabaseGrowth, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const generateMockData = (): DataPoint[] => {
    const data: DataPoint[] = [];
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - 30); // Last 30 days
    
    let cumulativeRecords = 89; // Starting point
    
    for (let i = 0; i < 30; i++) {
      const currentDate = new Date(startDate);
      currentDate.setDate(startDate.getDate() + i);
      
      // Simulate realistic growth patterns
      const weekday = currentDate.getDay();
      const isWeekend = weekday === 0 || weekday === 6;
      
      // Lower growth on weekends, higher on weekdays
      const baseGrowth = isWeekend ? 2 : 8;
      const variance = Math.random() * 6 - 3; // -3 to +3 variance
      const dailyGrowth = Math.max(0, Math.floor(baseGrowth + variance));
      
      cumulativeRecords += dailyGrowth;
      
      data.push({
        date: currentDate.toISOString().split('T')[0],
        records: cumulativeRecords,
        dailyGrowth: dailyGrowth
      });
    }
    
    return data;
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric' 
    });
  };

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white p-4 border border-gray-200 rounded-lg shadow-lg">
          <p className="text-sm font-medium text-gray-600">{formatDate(label)}</p>
          <p className="text-lg font-bold text-[#1F2A44]">
            {data.records.toLocaleString()} records
          </p>
          <p className="text-sm text-[#4B9CD3]">
            +{data.dailyGrowth} today
          </p>
        </div>
      );
    }
    return null;
  };

  if (loading) {
    return (
      <div className={`bg-white rounded-xl shadow-lg border border-gray-100 p-8 ${className}`}>
        <div className="animate-pulse">
          <div className="flex items-center justify-between mb-6">
            <div className="h-6 bg-gray-200 rounded w-1/3"></div>
            <div className="h-4 bg-gray-200 rounded w-1/4"></div>
          </div>
          <div className="h-64 bg-gray-200 rounded mb-4"></div>
          <div className="flex justify-between">
            <div className="h-4 bg-gray-200 rounded w-1/4"></div>
            <div className="h-4 bg-gray-200 rounded w-1/4"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white rounded-xl shadow-lg border border-gray-100 overflow-hidden ${className}`}>
      {/* Header */}
      <div className="p-6 border-b border-gray-100">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <div className="w-10 h-10 flex items-center justify-center rounded-full bg-[#4B9CD3] bg-opacity-10 text-[#4B9CD3] mr-3">
              <Database className="h-5 w-5" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-gray-800">Database Growth</h3>
              <p className="text-sm text-gray-500">Live intelligence collection</p>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <div className="text-right">
              <div className="text-2xl font-bold text-[#1F2A44]">
                {totalRecords.toLocaleString()}
              </div>
              <div className="text-sm text-gray-500">total records</div>
            </div>
            <div className="flex items-center space-x-1 text-green-600">
              <TrendingUp className="h-4 w-4" />
              <span className="text-sm font-medium">+{weeklyGrowth.toFixed(1)}%</span>
            </div>
          </div>
        </div>
      </div>

      {/* Chart */}
      <div className="p-6">
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data}>
              <defs>
                <linearGradient id="colorGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#4B9CD3" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#4B9CD3" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis 
                dataKey="date" 
                tickFormatter={formatDate}
                axisLine={false}
                tickLine={false}
                tick={{ fontSize: 12, fill: '#666' }}
              />
              <YAxis 
                axisLine={false}
                tickLine={false}
                tick={{ fontSize: 12, fill: '#666' }}
                tickFormatter={(value) => `${(value / 1000).toFixed(1)}k`}
              />
              <Tooltip content={<CustomTooltip />} />
              <Area
                type="monotone"
                dataKey="records"
                stroke="#4B9CD3"
                strokeWidth={2}
                fill="url(#colorGradient)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Growth indicators */}
        <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-[#4B9CD3] bg-opacity-5 rounded-lg p-3">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-600">This Week</span>
              <span className="text-lg font-bold text-[#4B9CD3]">+{Math.floor(weeklyGrowth * 10)}</span>
            </div>
            <div className="text-xs text-gray-500 mt-1">New records added</div>
          </div>
          
          <div className="bg-[#F0E68C] bg-opacity-10 rounded-lg p-3">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-600">Daily Avg</span>
              <span className="text-lg font-bold text-[#1F2A44]">~{Math.floor(weeklyGrowth * 1.4)}</span>
            </div>
            <div className="text-xs text-gray-500 mt-1">Records per day</div>
          </div>
          
          <div className="bg-green-50 rounded-lg p-3">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-600">Data Sources</span>
              <span className="text-lg font-bold text-green-600">44+</span>
            </div>
            <div className="text-xs text-gray-500 mt-1">Active feeds</div>
          </div>
        </div>
      </div>

      {/* Live status indicator */}
      <div className="px-6 py-4 bg-gray-50 border-t border-gray-100">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span className="text-sm text-gray-600">Live updates every 5 minutes</span>
          </div>
          <div className="flex items-center space-x-2 text-gray-500">
            <RefreshCw className="h-4 w-4" />
            <span className="text-xs">Last update: just now</span>
          </div>
        </div>
      </div>
    </div>
  );
}