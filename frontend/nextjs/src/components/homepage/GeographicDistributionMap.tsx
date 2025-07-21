'use client';

import { useState, useEffect, useRef } from 'react';
import { scaleLinear } from 'd3-scale';
import { Map, Overlay } from 'pigeon-maps';
import africanCountriesGeo from '@/data/african_countries_geo.json';
import VisualizationErrorBoundary from '@/components/common/VisualizationErrorBoundary';
import Image from 'next/image';
import { ScaleIcon } from 'lucide-react';

// Types for GeoJSON features
interface GeoJSONProperties {
  name: string;
  region: string;
  lat?: number;
  lon?: number;
  [key: string]: unknown;
}

interface GeoJSONGeometry {
  type: 'Polygon' | 'MultiPolygon';
  coordinates: number[][][] | number[][][][];
}

interface GeoJSONFeature {
  type: 'Feature';
  properties: GeoJSONProperties;
  geometry: GeoJSONGeometry;
}

interface GeoJSONFeatureCollection {
  type: 'FeatureCollection';
  features: GeoJSONFeature[];
}

interface CountryData {
  country: string;
  fundingAmount: number;
  fundingCount: number;
  percentageTotal: number;
  center?: [number, number]; // [longitude, latitude]
}

// Map center coordinates for Africa
const AFRICA_CENTER: [number, number] = [20, 5];
const DEFAULT_ZOOM = 2.5;

const GeographicDistributionMap = () => {
  const [tooltipContent, setTooltipContent] = useState<string | null>(null);
  const [tooltipPosition, setTooltipPosition] = useState<{x: number, y: number} | null>(null);
  const tooltipRef = useRef<HTMLDivElement>(null);
  const [data, setData] = useState<CountryData[]>([]);
  // Define the type for country polygons
  interface CountryPolygon {
    id: string;
    name: string;
    coordinates: [number, number][][];
    center?: [number, number];
    data?: CountryData;
  }

  const [countryPolygons, setCountryPolygons] = useState<CountryPolygon[]>([]);

  useEffect(() => {
    // Type assertion for the imported GeoJSON data
    const geoData = africanCountriesGeo as unknown as GeoJSONFeatureCollection;
    
    // Process GeoJSON data to extract polygons for each country
    const countries = geoData.features.map(feature => {
      const countryName = feature.properties.name;
      
      // Extract center point for the country if available
      let centerPoint: [number, number] | undefined;
      
      // Check for custom lat/lon properties in the GeoJSON if available
      const customLat = feature.properties.lat;
      const customLon = feature.properties.lon;
      
      if (customLat && customLon) {
        centerPoint = [customLon, customLat];
      } else if (feature.geometry.type === 'Polygon' && 
                feature.geometry.coordinates && 
                Array.isArray(feature.geometry.coordinates) && 
                feature.geometry.coordinates.length > 0 && 
                Array.isArray(feature.geometry.coordinates[0])) {
        // Calculate rough center from first polygon
        const coords = feature.geometry.coordinates[0];
        
        // Ensure coords is an array and each element is an array with at least 2 elements
        if (Array.isArray(coords) && coords.length > 0) {
          // Flatten the coordinates array to handle both Polygon and MultiPolygon cases
          const flatCoords = coords.flat();
          
          // Extract all longitudes and latitudes
          const lons: number[] = [];
          const lats: number[] = [];
          
          flatCoords.forEach(coord => {
            if (Array.isArray(coord) && coord.length >= 2) {
              lons.push(Number(coord[0]));
              lats.push(Number(coord[1]));
            }
          });
          
          if (lons.length > 0 && lats.length > 0) {
            const avgLon = lons.reduce((sum, val) => sum + val, 0) / lons.length;
            const avgLat = lats.reduce((sum, val) => sum + val, 0) / lats.length;
          
            centerPoint = [avgLon, avgLat];
          }
        }
      }
      
      return {
        id: feature.properties.name.toLowerCase().replace(/\s+/g, '-'),
        name: countryName,
        coordinates: feature.geometry.coordinates as [number, number][][],
        center: centerPoint,
        data: undefined
      };
    });
    
    setCountryPolygons(countries);
    
    // Simulated data with coordinates in [latitude, longitude] format for pigeon-maps
    const mockData: CountryData[] = [
      { country: 'Nigeria', fundingAmount: 245000000, fundingCount: 487, percentageTotal: 28.4, center: [9.0820, 8.6753] },
      { country: 'Kenya', fundingAmount: 198000000, fundingCount: 412, percentageTotal: 22.9, center: [-0.0236, 37.9062] },
      { country: 'South Africa', fundingAmount: 167000000, fundingCount: 356, percentageTotal: 19.3, center: [-28.8166, 24.7461] },
      { country: 'Egypt', fundingAmount: 112000000, fundingCount: 289, percentageTotal: 12.9, center: [26.8206, 30.8025] },
      { country: 'Rwanda', fundingAmount: 45000000, fundingCount: 98, percentageTotal: 5.2, center: [-1.9403, 29.8739] },
      { country: 'Ghana', fundingAmount: 34000000, fundingCount: 76, percentageTotal: 3.9, center: [7.9465, -1.0232] },
      { country: 'Tunisia', fundingAmount: 244400000, fundingCount: 9, percentageTotal: 15.8, center: [33.8869, 9.5375] },
      { country: 'Morocco', fundingAmount: 89000000, fundingCount: 67, percentageTotal: 6.2, center: [31.7917, -7.0926] },
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

  // Simple number formatter with thousands separator
  const formatNumber = (num: number): string => {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
  };

  const handleCountryHover = (countryName: string, event: React.MouseEvent) => {
    const countryData = data.find(d => d.country === countryName);
    
    // Get mouse position for tooltip positioning
    setTooltipPosition({
      x: event.clientX,
      y: event.clientY
    });
    
    if (countryData) {
      setTooltipContent(
        `${countryName} - $${formatNumber(countryData.fundingAmount)} - ${countryData.fundingCount} events - ${countryData.percentageTotal}% share`
      );
    } else {
      setTooltipContent(`${countryName} - No funding data available`);
    }
  };
  
  const handleMouseLeave = () => {
    setTooltipContent(null);
  };

  return (
    <VisualizationErrorBoundary>
      <div className="relative">
        <Image 
          src="/number-1.png" 
          alt="Number 1" 
          width={150} 
          height={150} 
          className="absolute -left-10 top-1/2 transform -translate-y-1/2" 
        />
        <figure className="chart-container relative pl-24">
          <div className="chart-title" id="figure-1">Figure 1: Geographic Distribution of AI Funding (2019-2024)</div>
          <div className="relative w-full h-[500px]" data-tip="">
            <Map
              height={500}
              defaultCenter={AFRICA_CENTER}
              defaultZoom={DEFAULT_ZOOM}
              attribution={false}
            >
              {/* Render African countries with color-coding based on funding data */}
              {countryPolygons.map((country, index) => {
                const countryName = country.name;
                const fillColor = getFundingColor(countryName);
                
                // Display markers for countries with significant funding
                const countryData = data.find(d => d.country === countryName);
                if (countryData && countryData.center) {
                  return (
                    <Overlay key={`marker-${index}`} anchor={countryData.center} offset={[0, 0]}>
                      <div
                        className="relative"
                        style={{
                          width: '100px',
                          height: '100px',
                          transform: 'translate(-50%, -50%)'
                        }}
                        onMouseEnter={(e) => handleCountryHover(countryName, e)}
                        onMouseLeave={handleMouseLeave}
                      >
                        <div
                          className="absolute rounded-full opacity-70 cursor-pointer"
                          style={{
                            backgroundColor: fillColor,
                            width: `${Math.max(20, countryData.percentageTotal * 3)}px`,
                            height: `${Math.max(20, countryData.percentageTotal * 3)}px`,
                            top: '50%',
                            left: '50%',
                            transform: 'translate(-50%, -50%)',
                            border: '1px solid rgba(255, 255, 255, 0.5)',
                          }}
                        />
                        <div 
                          className="absolute text-xs font-bold text-center whitespace-nowrap"
                          style={{
                            top: '100%',
                            left: '50%',
                            transform: 'translateX(-50%)',
                            color: countryData.percentageTotal > 10 ? '#1B365D' : '#666',
                            textShadow: '0 0 3px rgba(255, 255, 255, 0.8)'
                          }}
                        >
                          {countryName}
                        </div>
                      </div>
                    </Overlay>
                  );
                }
                return null;
              })}
            </Map>
          </div>

          <figcaption className="chart-caption">
            Note: The map shows percentage distribution of tracked AI funding across Africa from 2019 to 2024. 
            Larger circles indicate higher funding concentration. Four countries (Nigeria, Kenya, South Africa, 
            and Egypt) account for 83% of total funding.
          </figcaption>
          
          {/* Legend */}
          <div className="absolute top-4 right-4 bg-white p-4 border border-gray-200 rounded">
            <div className="text-sm font-medium mb-2">Funding Share (%)</div>
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 rounded-full bg-[#E5E7EB]"></div>
              <span className="text-xs">0%</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 rounded-full bg-[#1B365D]"></div>
              <span className="text-xs">30%+</span>
            </div>
          </div>

          {/* Custom tooltip implementation */}
          {tooltipContent && tooltipPosition && (
            <div
              ref={tooltipRef}
              className="absolute bg-white text-gray-800 border border-gray-200 shadow-sm p-2 rounded z-50 pointer-events-none"
              style={{
                left: `${tooltipPosition.x + 10}px`,
                top: `${tooltipPosition.y - 10}px`,
                maxWidth: '250px'
              }}
            >
              {tooltipContent}
            </div>
          )}
        </figure>
      </div>
    </VisualizationErrorBoundary>
  );
};

export default GeographicDistributionMap;
