'use client';

// Core React and Next.js imports
import React, { useState, useEffect } from 'react';

// UI Components - using basic HTML elements as fallback for missing shadcn/ui components
// Note: Replace these with actual shadcn/ui imports when available
const Card = ({ children, className = "" }: { children: React.ReactNode; className?: string }) => (
  <div className={`bg-white rounded-lg border shadow-sm ${className}`}>{children}</div>
);
const CardContent = ({ children, className = "" }: { children: React.ReactNode; className?: string }) => (
  <div className={`p-6 ${className}`}>{children}</div>
);
const CardHeader = ({ children, className = "" }: { children: React.ReactNode; className?: string }) => (
  <div className={`p-6 pb-2 ${className}`}>{children}</div>
);
const CardTitle = ({ children, className = "" }: { children: React.ReactNode; className?: string }) => (
  <h3 className={`text-lg font-semibold ${className}`}>{children}</h3>
);
const Button = ({ children, className = "", variant = "default", size = "default", disabled = false, onClick, ...props }: {
  children: React.ReactNode;
  className?: string;
  variant?: string;
  size?: string;
  disabled?: boolean;
  onClick?: () => void;
  [key: string]: any;
}) => (
  <button 
    className={`px-4 py-2 rounded-md font-medium transition-colors ${
      variant === "outline" ? "border border-gray-300 bg-white hover:bg-gray-50" : "bg-blue-600 text-white hover:bg-blue-700"
    } ${disabled ? "opacity-50 cursor-not-allowed" : ""} ${className}`}
    disabled={disabled}
    onClick={onClick}
    {...props}
  >
    {children}
  </button>
);
const Tabs = ({ children, value, onValueChange, className = "" }: {
  children: React.ReactNode;
  value: string;
  onValueChange: (value: string) => void;
  className?: string;
}) => (
  <div className={className} data-value={value} data-onvaluechange={onValueChange}>
    {children}
  </div>
);
const TabsList = ({ children, className = "" }: { children: React.ReactNode; className?: string }) => (
  <div className={`flex bg-gray-100 rounded-lg p-1 ${className}`}>{children}</div>
);
const TabsTrigger = ({ children, value, className = "" }: { children: React.ReactNode; value: string; className?: string }) => (
  <button className={`px-3 py-1 rounded-md text-sm font-medium ${className}`} data-value={value}>
    {children}
  </button>
);
const TabsContent = ({ children, value, className = "" }: { children: React.ReactNode; value: string; className?: string }) => (
  <div className={className} data-value={value}>{children}</div>
);
const TooltipProvider = ({ children }: { children: React.ReactNode }) => <div>{children}</div>;
const Tooltip = ({ children }: { children: React.ReactNode }) => <div>{children}</div>;
const TooltipTrigger = ({ children, asChild }: { children: React.ReactNode; asChild?: boolean }) => <div>{children}</div>;
const TooltipContent = ({ children }: { children: React.ReactNode }) => <div className="hidden">{children}</div>;
const Select = ({ children, value, onValueChange }: { children: React.ReactNode; value: string; onValueChange: (value: string) => void }) => (
  <div data-value={value} data-onvaluechange={onValueChange}>{children}</div>
);
const SelectTrigger = ({ children }: { children: React.ReactNode }) => <div className="border rounded px-3 py-2">{children}</div>;
const SelectValue = ({ placeholder }: { placeholder?: string }) => <span>{placeholder}</span>;
const SelectContent = ({ children }: { children: React.ReactNode }) => <div>{children}</div>;
const SelectItem = ({ children, value }: { children: React.ReactNode; value: string }) => <div data-value={value}>{children}</div>;

// Re-exports from recharts to avoid naming conflicts
import {
  BarChart,
  Bar,
  LineChart as RechartsLineChart,
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
  Download, 
  Share2, 
  Filter, 
  AlertCircle, 
  DollarSign, 
  TrendingDown,
  ArrowRight
} from 'lucide-react';

// Chart color scheme
const CHART_COLORS = {
  female: '#C026D3',  // Fuchsia-600
  male: '#2563EB',    // Blue-600
  femaleLight: '#F0ABFC', // Fuchsia-200
  maleLight: '#93C5FD',   // Blue-300
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

interface TooltipProps {
  active?: boolean;
  payload?: Array<{
    name: string;
    value: number;
    color: string;
    dataKey?: string;
    payload?: any;
  }>;
  label?: string | number;
  formatter?: (value: number | string, name: string) => [number | string, string];
}

type TimePeriod = '1y' | '3y' | '5y' | 'all';
type ChartView = 'combo' | 'bar' | 'line' | 'area';

// Custom Tooltip Component
const CustomTooltip = ({ active, payload, label, formatter }: TooltipProps) => {
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

// Custom chart components
const XAxisTick = ({ x, y, payload }: { x: number; y: number; payload: any }) => (
  <g transform={`translate(${x},${y})`}>
    <text x={0} y={0} dy={16} textAnchor="middle" fill="#6B7280" fontSize={12}>
      {payload.value}
    </text>
  </g>
);

const YAxisTick = ({ x, y, payload }: { x: number; y: number; payload: any }) => (
  <g transform={`translate(${x},${y})`}>
    <text x={-10} y={0} dy={4} textAnchor="end" fill="#6B7280" fontSize={12}>
      {payload.value}
    </text>
  </g>
);

const GenderEquityDashboard = () => {
  // State management
  const [timePeriod, setTimePeriod] = useState<TimePeriod>('5y');
  const [chartView, setChartView] = useState<ChartView>('combo');
  const [showFilters, setShowFilters] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');
  const [isScrolled, setIsScrolled] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

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

    // Set initial values
    updateDimensions();
    
    // Add event listener for window resize
    window.addEventListener('resize', updateDimensions);
    
    // Cleanup
    return () => window.removeEventListener('resize', updateDimensions);
  }, []);

  // Calculate statistics
  const allGenderTimelineData: GenderTimelineData[] = [
    { year: 2018, female: 54, male: 201, total: 255, femalePercentage: 21.2 },
    { year: 2019, female: 67, male: 234, total: 301, femalePercentage: 22.3 },
    { year: 2020, female: 89, male: 289, total: 378, femalePercentage: 23.5 },
    { year: 2021, female: 124, male: 356, total: 480, femalePercentage: 25.8 },
    { year: 2022, female: 187, male: 412, total: 599, femalePercentage: 31.2 },
    { year: 2023, female: 245, male: 498, total: 743, femalePercentage: 33.0 },
    { year: 2024, female: 289, male: 512, total: 801, femalePercentage: 36.1 },
  ];

  const getFilteredData = (): GenderTimelineData[] => {
    const currentYear = new Date().getFullYear();
    let startYear = currentYear - 5;

    switch (timePeriod) {
      case '1y':
        startYear = currentYear - 1;
        break;
      case '3y':
        startYear = currentYear - 3;
        break;
      case '5y':
        startYear = currentYear - 5;
        break;
      case 'all':
      default:
        return allGenderTimelineData;
    }

    return allGenderTimelineData.filter((item) => item.year >= startYear);
  };

  const genderTimelineData = getFilteredData();

  const sectorGenderData: SectorGenderData[] = [
    { sector: 'AI/ML', femalePercent: 28, malePercent: 72 },
    { sector: 'FinTech', femalePercent: 32, malePercent: 68 },
    { sector: 'HealthTech', femalePercent: 45, malePercent: 55 },
    { sector: 'AgriTech', femalePercent: 38, malePercent: 62 },
    { sector: 'EdTech', femalePercent: 52, malePercent: 48 },
  ];

  const regionalGenderData: RegionalGenderData[] = [
    { region: 'East Africa', femalePercent: 35, total: 189 },
    { region: 'West Africa', femalePercent: 28, total: 245 },
    { region: 'Southern Africa', femalePercent: 41, total: 176 },
    { region: 'North Africa', femalePercent: 22, total: 143 },
    { region: 'Central Africa', femalePercent: 19, total: 98 },
  ];

  const fundingComparisonData: FundingComparisonData[] = [
    { category: 'Seed', female: 1200000, male: 4500000, total: 5700000, femalePercentage: 21.1 },
    { category: 'Series A', female: 4500000, male: 18000000, total: 22500000, femalePercentage: 16.7 },
    { category: 'Series B+', female: 12000000, male: 75000000, total: 87000000, femalePercentage: 12.1 },
  ];

  const totalFunding = genderTimelineData.reduce((sum, item) => sum + item.female + item.male, 0);
  const totalFemaleFunding = genderTimelineData.reduce((sum, item) => sum + item.female, 0);
  const totalMaleFunding = genderTimelineData.reduce((sum, item) => sum + item.male, 0);
  const totalFundingWomen = totalFemaleFunding * 1000000; // Convert to actual currency
  const totalFundingMen = totalMaleFunding * 1000000;
  const averageFemalePercent = (genderTimelineData.reduce((sum, item) => sum + item.femalePercentage, 0) / genderTimelineData.length).toFixed(1);

  const chartPadding = dimensions.isMobile 
    ? { left: 40, right: 20, top: 20, bottom: 40 }
    : { left: 60, right: 40, top: 20, bottom: 60 };

  const barSize = dimensions.isMobile ? 24 : 32;
  const barGap = dimensions.isMobile ? 4 : 8;

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

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
      <div className="space-y-8 p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          {[1, 2, 3, 4].map((i) => (
            <Card key={i} className="p-6">
              <div className="animate-pulse space-y-4">
                <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                <div className="h-8 bg-gray-200 rounded w-1/2"></div>
                <div className="h-4 bg-gray-100 rounded w-5/6"></div>
              </div>
            </Card>
          ))}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
              <div className="animate-pulse bg-gray-100 rounded-lg h-80 w-full" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 md:space-y-8 p-4 md:p-6">
      {/* Sticky header with filters */}
      <div className={`sticky top-0 z-10 bg-white/80 backdrop-blur-sm py-3 -mx-4 px-4 md:-mx-6 md:px-6 border-b transition-all duration-300 ${
        isScrolled ? 'shadow-sm' : ''
      }`}>
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Gender Equity in AI Funding</h2>
            <p className="text-sm text-gray-500">Tracking funding disparities and opportunities for women in Africa's AI ecosystem</p>
          </div>
          
          <div className="flex flex-wrap items-center gap-3 w-full md:w-auto">
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button 
                    variant="outline" 
                    size="sm" 
                    onClick={() => setShowFilters(!showFilters)}
                    className="gap-2"
                  >
                    <Filter className="h-4 w-4" />
                    <span className="hidden sm:inline">Filters</span>
                  </Button>
                </TooltipTrigger>
                <TooltipContent>
                  <p>Filter and customize the dashboard view</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>

            <Button variant="outline" size="sm" className="gap-2">
              <Download className="h-4 w-4" />
              <span className="hidden sm:inline">Export</span>
            </Button>
            
            <Button variant="outline" size="sm" className="gap-2">
              <Share2 className="h-4 w-4" />
              <span className="hidden sm:inline">Share</span>
            </Button>
          </div>
        </div>
        
        {/* Expanded filters */}
        {showFilters && (
          <div className="mt-4 pt-4 border-t grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Time Period</label>
              <Select value={timePeriod} onValueChange={(value) => setTimePeriod(value as TimePeriod)}>
                <SelectTrigger>
                  <SelectValue placeholder="Select time period" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="1y">Last 12 months</SelectItem>
                  <SelectItem value="3y">Last 3 years</SelectItem>
                  <SelectItem value="5y">Last 5 years</SelectItem>
                  <SelectItem value="all">All time</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Chart View</label>
              <Select value={chartView} onValueChange={(value) => setChartView(value as ChartView)}>
                <SelectTrigger>
                  <SelectValue placeholder="Select chart type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="combo">Combined View</SelectItem>
                  <SelectItem value="bar">Bar Chart</SelectItem>
                  <SelectItem value="line">Line Chart</SelectItem>
                  <SelectItem value="area">Area Chart</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="flex items-end">
              <Button className="w-full" onClick={() => {
                setTimePeriod('5y');
                setChartView('combo');
                setActiveTab('overview');
              }}>
                Reset Filters
              </Button>
            </div>
          </div>
        )}
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="trends">Trends</TabsTrigger>
          <TabsTrigger value="analysis">Analysis</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="mt-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <Card className="border-l-4 border-blue-500">
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-sm font-medium text-gray-500">Female Funding Share</CardTitle>
                  <DollarSign className="h-5 w-5 text-blue-500" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold" style={{ color: '#2563EB' }}>
                  {Math.round((totalFundingWomen / (totalFundingWomen + totalFundingMen)) * 100)}%
                </div>
                <p className="text-xs text-gray-500 mt-1">across {genderTimelineData.length} years</p>
              </CardContent>
            </Card>

            {/* Female Founder Funding Card */}
            <Card className="bg-gradient-to-br from-orange-50 to-orange-100 border-orange-100 hover:shadow-md transition-all duration-200">
              <CardContent className="p-6">
                <div className="flex items-center gap-3 mb-3">
                  <div className="w-10 h-10 rounded-full bg-orange-100 flex items-center justify-center">
                    <DollarSign className="w-5 h-5 text-orange-600" />
                  </div>
                  <h3 className="text-sm font-semibold text-gray-700">Female founder funding</h3>
                </div>
                <div className="text-3xl font-black text-orange-700 mb-2">$48M</div>
                <div className="text-xs font-medium text-orange-600">
                  <span className="bg-orange-50 px-2 py-1 rounded-full">
                    Only 12% of total funding
                  </span>
                </div>
              </CardContent>
            </Card>
            
            {/* Declining Trend Card */}
            <Card className="bg-gradient-to-br from-yellow-50 to-yellow-100 border-yellow-100 hover:shadow-md transition-all duration-200">
              <CardContent className="p-6">
                <div className="flex items-center gap-3 mb-3">
                  <div className="w-10 h-10 rounded-full bg-yellow-100 flex items-center justify-center">
                    <TrendingDown className="w-5 h-5 text-yellow-600" />
                  </div>
                  <h3 className="text-sm font-semibold text-gray-700">Declining trend</h3>
                </div>
                <div className="text-3xl font-black text-yellow-700 mb-2">6 years</div>
                <div className="text-xs font-medium text-yellow-600">
                  <span className="bg-yellow-50 px-2 py-1 rounded-full">
                    Since 2019 peak of 22.3%
                  </span>
                </div>
              </CardContent>
            </Card>
            
            {/* Funding Gap Card */}
            <Card className="bg-gradient-to-br from-blue-50 to-blue-100 border-blue-100 hover:shadow-md transition-all duration-200">
              <CardContent className="p-6">
                <div className="flex items-center gap-3 mb-3">
                  <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center">
                    <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                    </svg>
                  </div>
                  <h3 className="text-sm font-semibold text-gray-700">Funding gap</h3>
                </div>
                <div className="text-3xl font-black text-blue-700 mb-2">4.2x</div>
                <div className="text-xs font-medium text-blue-600">
                  <span className="bg-blue-50 px-2 py-1 rounded-full">
                    Less than male-led startups
                  </span>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Main Visualizations Grid */}
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
                    <defs>
                      <linearGradient id="femaleGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor={CHART_COLORS.female} stopOpacity={0.8} />
                        <stop offset="95%" stopColor={CHART_COLORS.femaleLight} stopOpacity={0.8} />
                      </linearGradient>
                      <linearGradient id="maleGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor={CHART_COLORS.male} stopOpacity={0.8} />
                        <stop offset="95%" stopColor={CHART_COLORS.maleLight} stopOpacity={0.8} />
                      </linearGradient>
                    </defs>
                    
                    <CartesianGrid 
                      vertical={false} 
                      stroke={CHART_COLORS.gridLine} 
                      strokeDasharray="3 3" 
                    />
                    
                    <XAxis 
                      dataKey="year" 
                      tickLine={false}
                      axisLine={{ stroke: CHART_COLORS.gridLine }}
                      tick={({ x, y, payload }) => (
                        <XAxisTick x={x} y={y} payload={payload} />
                      )}
                    />
                    
                    <YAxis 
                      yAxisId="left" 
                      orientation="left"
                      tickLine={false}
                      axisLine={false}
                      tick={({ x, y, payload }) => (
                        <YAxisTick x={x} y={y} payload={payload} />
                      )}
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
                      fill="url(#femaleGradient)" 
                      radius={[4, 4, 0, 0]}
                    />
                    <Bar 
                      yAxisId="left" 
                      dataKey="male" 
                      name="Male Founders" 
                      fill="url(#maleGradient)" 
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

            {/* Sector Analysis */}
            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Gender Gap by Sector
              </h3>
              <div className="w-full h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart 
                    data={sectorGenderData} 
                    layout="horizontal"
                    margin={{ top: 20, right: 30, left: 80, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke={CHART_COLORS.gridLine} />
                    <XAxis type="number" domain={[0, 100]} stroke={CHART_COLORS.text} />
                    <YAxis dataKey="sector" type="category" width={80} stroke={CHART_COLORS.text} />
                    <RechartsTooltip 
                      formatter={(value: number) => [`${value}%`, '']} 
                      content={<CustomTooltip />}
                    />
                    <Legend />
                    <Bar dataKey="femalePercent" fill={CHART_COLORS.female} name="Female %" />
                    <Bar dataKey="malePercent" fill={CHART_COLORS.male} name="Male %" />
                  </BarChart>
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
                    <Bar dataKey="femalePercent" fill="#D97706" name="Female Leadership %" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Funding Gap Analysis */}
            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Funding Performance Gaps
              </h3>
              <div className="w-full h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={fundingComparisonData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke={CHART_COLORS.gridLine} />
                    <XAxis dataKey="category" stroke={CHART_COLORS.text} />
                    <YAxis stroke={CHART_COLORS.text} />
                    <RechartsTooltip 
                      formatter={(value: number, name: string) => [
                        name === 'female' || name === 'male' ? 
                          (typeof value === 'number' && value > 10000 ? `$${(value/1000000).toFixed(1)}M` : `${value}%`) : value,
                        name === 'female' ? 'Female' : 'Male'
                      ]}
                      content={<CustomTooltip />}
                    />
                    <Legend />
                    <Bar dataKey="female" fill={CHART_COLORS.female} name="Female-led" />
                    <Bar dataKey="male" fill={CHART_COLORS.male} name="Male-led" />
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

          {/* Call to Action */}
          <div className="mt-10 text-center">
            <a 
              href="/equity-assessment" 
              className="inline-flex items-center justify-center px-8 py-4 bg-gradient-to-r from-pink-600 to-pink-700 hover:from-pink-700 hover:to-pink-800 text-white font-semibold rounded-xl shadow-lg hover:shadow-xl transition-all duration-200"
            >
              View Detailed Equity Analysis
              <ArrowRight className="ml-2 h-5 w-5 text-white" />
            </a>
            <p className="mt-4 text-sm text-gray-500">
              Explore our comprehensive analysis of gender equity in African AI funding
            </p>
          </div>
        </TabsContent>
        
        <TabsContent value="trends" className="mt-6">
          <div className="bg-white rounded-lg border p-6">
            <h3 className="text-lg font-semibold mb-4">Trend Analysis</h3>
            <p className="text-gray-600 mb-6">Coming soon: Detailed trend analysis and historical comparisons.</p>
            <Button variant="outline" disabled>View Detailed Trends</Button>
          </div>
        </TabsContent>
        
        <TabsContent value="analysis" className="mt-6">
          <div className="bg-white rounded-lg border p-6">
            <h3 className="text-lg font-semibold mb-4">In-Depth Analysis</h3>
            <p className="text-gray-600 mb-6">Coming soon: Comprehensive analysis and insights on gender equity in AI funding.</p>
            <div className="flex gap-3">
              <Button variant="outline" disabled>Download Report</Button>
              <Button variant="outline" disabled>View Methodology</Button>
            </div>
          </div>
        </TabsContent>
      </Tabs>
      
      {/* Footer */}
      <div className="mt-12 pt-6 border-t border-gray-200 text-center text-sm text-gray-500">
        <p>Data is updated quarterly. Last updated: {new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}</p>
        <p className="mt-2">Have questions about this data? <a href="#" className="text-blue-600 hover:underline">Contact our research team</a></p>
      </div>
    </div>
  );
};

export default GenderEquityDashboard;
