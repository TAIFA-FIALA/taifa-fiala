'use client';

import { useState, useEffect } from 'react';
import { ComposableMap, Geographies, Geography } from 'react-simple-maps';
import { scaleLinear } from 'd3-scale';
import { format } from 'd3-format';
import ReactTooltip from 'react-tooltip';
import africanCountriesGeo from '@/data/african_countries_geo.json';
import VisualizationErrorBoundary from '@/components/common/VisualizationErrorBoundary';

interface CountryData {
  country: string;
  fundingAmount: number;
  fundingCount: number;
  percentageTotal: number;
}

const GeographicDistributionMap = () => {
  const [tooltipContent, setTooltipContent] = useState('');
  const [data, setData] = useState<CountryData[]>([]);

  useEffect(() => {
    // Simulated data - replace with actual API call
    const mockData: CountryData[] = [
      { country: 'Nigeria', fundingAmount: 245000000, fundingCount: 487, percentageTotal: 28.4 },
      { country: 'Kenya', fundingAmount: 198000000, fundingCount: 412, percentageTotal: 22.9 },
      { country: 'South Africa', fundingAmount: 167000000, fundingCount: 356, percentageTotal: 19.3 },
      { country: 'Egypt', fundingAmount: 112000000, fundingCount: 289, percentageTotal: 12.9 },
      { country: 'Rwanda', fundingAmount: 45000000, fundingCount: 98, percentageTotal: 5.2 },
      { country: 'Ghana', fundingAmount: 34000000, fundingCount: 76, percentageTotal: 3.9 },
      // Add more countries as needed
    ];

    setData(mockData);
  }, []);

  const getFundingColor = (countryName: string) => {  
    const countryData = data.find(d => d.country === countryName);
    if (!countryData) return '#F5F5F5'; // Default color for countries with no data
    
    // Color scale
    const colorScale = scaleLinear<string>()
      .domain([0, 30])
      .range(['#E5E7EB', '#1B365D']);
      
    return colorScale(countryData.percentageTotal);
  };

  const formatNumber = format(',');

  const handleMouseEnter = (geo: any) => {
    const countryData = data.find(d => d.country === geo.properties.name);
    if (countryData) {
      setTooltipContent(`
        <div class="p-2">
          <strong>${geo.properties.name}</strong><br/>
          Funding: $${formatNumber(countryData.fundingAmount)}<br/>
          Events: ${countryData.fundingCount}<br/>
          Share: ${countryData.percentageTotal}%
        </div>
      `);
    } else {
      setTooltipContent(`
        <div class="p-2">
          <strong>${geo.properties.name}</strong><br/>
          No funding data available
        </div>
      `);
    }
  };

  return (
    <VisualizationErrorBoundary>
      <figure className="chart-container relative">
        <div className="chart-title" id="figure-1">Figure 1: Geographic Distribution of AI Funding (2019-2024)</div>
      
      <div className="relative w-full h-[500px]" data-tip="">
        <ComposableMap
          projectionConfig={{ scale: 450 }}
          width={800}
          height={500}
          style={{
            width: "100%",
            height: "auto"
          }}
        >
          <Geographies geography={africanCountriesGeo}>
            {({ geographies }) =>
              geographies.map(geo => (
                <Geography
                  key={geo.rsmKey}
                  geography={geo}
                  onMouseEnter={() => handleMouseEnter(geo)}
                  onMouseLeave={() => setTooltipContent('')}
                  style={{
                    default: {
                      fill: getFundingColor(geo.properties.name),
                      stroke: "#FFFFFF",
                      strokeWidth: 0.5,
                      outline: "none",
                    },
                    hover: {
                      fill: '#7B1F1D',
                      stroke: "#FFFFFF",
                      strokeWidth: 0.5,
                      outline: "none",
                    },
                    pressed: {
                      fill: '#7B1F1D',
                      stroke: "#FFFFFF",
                      strokeWidth: 0.5,
                      outline: "none",
                    },
                  }}
                />
              ))
            }
          </Geographies>
        </ComposableMap>
      </div>

      <figcaption className="chart-caption">
        Note: The map shows percentage distribution of tracked AI funding across Africa from 2019 to 2024. 
        Darker shades indicate higher funding concentration. Four countries (Nigeria, Kenya, South Africa, 
        and Egypt) account for 83% of total funding.
      </figcaption>
      
      {/* Legend */}
      <div className="absolute top-4 right-4 bg-white p-4 border border-gray-200 rounded">
        <div className="text-sm font-medium mb-2">Funding Share (%)</div>
        <div className="flex items-center space-x-2">
          <div className="w-4 h-4 bg-[#E5E7EB]"></div>
          <span className="text-xs">0%</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-4 h-4 bg-[#1B365D]"></div>
          <span className="text-xs">30%+</span>
        </div>
      </div>

      <ReactTooltip
        className="!bg-white !text-gray-800 !border !border-gray-200 !shadow-sm"
        html={true}
        data-html>
        {tooltipContent}
      </ReactTooltip>
      </figure>
    </VisualizationErrorBoundary>
  );
};

export default GeographicDistributionMap;
