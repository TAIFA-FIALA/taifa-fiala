'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import dynamic from 'next/dynamic';
import { useRouter } from 'next/navigation';
import type { LatLngExpression } from 'leaflet';
import type { ControlPosition } from 'leaflet';

// Import the GeoJSON data
import africanCountriesGeoJSON from '@/data/african_countries_geo.json';

// Define types for GeoJSON data
interface GeoJSONGeometry {
  type: string;
  coordinates: number[][] | number[][][] | number[][][][];
}

interface GeoJSONFeature {
  type: 'Feature';
  properties: {
    name?: string;
    NAME?: string;
    ISO_A2?: string;
    iso_a2?: string;
    funding?: number;
    projects?: number;
  };
  geometry: GeoJSONGeometry;
}

interface GeoJSONCollection {
  type: 'FeatureCollection';
  features: GeoJSONFeature[];
}

interface CountryData {
  name: string;
  code: string;
  funding: number;
  projects: number;
}

interface FundingDistribution {
  country_code: string;
  country_name: string;
  total_funding: number;
  opportunity_count: number;
  percentage_of_total: number;
}

interface GeographicEquityMapProps {
  className?: string;
}

// Dynamically import Leaflet components to avoid SSR issues
interface MapContainerProps {
  center: LatLngExpression;
  zoom: number;
  style?: React.CSSProperties;
  children?: React.ReactNode;
  className?: string;
  [key: string]: any;
}

interface TileLayerProps {
  attribution?: string;
  url: string;
  [key: string]: any;
}

interface ZoomControlProps {
  position?: ControlPosition;
  [key: string]: any;
}

const MapContainer = dynamic<MapContainerProps>(
  () => import('react-leaflet').then((mod) => mod.MapContainer),
  { ssr: false }
);

const TileLayer = dynamic<TileLayerProps>(
  () => import('react-leaflet').then((mod) => mod.TileLayer),
  { ssr: false }
);

const GeoJSON = dynamic<any>(
  () => import('react-leaflet').then((mod) => mod.GeoJSON),
  { ssr: false }
);

const ZoomControl = dynamic<ZoomControlProps>(
  () => import('react-leaflet').then((mod) => mod.ZoomControl),
  { ssr: false }
);

// Sample data to use when API is not available
const demoCountryData: CountryData[] = [
  { name: "Nigeria", code: "NG", funding: 4500000, projects: 32 },
  { name: "Kenya", code: "KE", funding: 3200000, projects: 28 },
  { name: "South Africa", code: "ZA", funding: 2800000, projects: 24 },
  { name: "Egypt", code: "EG", funding: 1900000, projects: 18 },
  { name: "Ghana", code: "GH", funding: 950000, projects: 12 },
  { name: "Rwanda", code: "RW", funding: 750000, projects: 10 },
  { name: "Ethiopia", code: "ET", funding: 620000, projects: 8 },
  { name: "Tunisia", code: "TN", funding: 580000, projects: 7 },
  { name: "Morocco", code: "MA", funding: 510000, projects: 6 },
  { name: "Uganda", code: "UG", funding: 480000, projects: 6 },
  { name: "Senegal", code: "SN", funding: 320000, projects: 4 },
  { name: "Tanzania", code: "TZ", funding: 280000, projects: 4 },
];

// Use the imported GeoJSON data for African countries

const GeographicEquityMap: React.FC<GeographicEquityMapProps> = ({ className = '' }) => {
  const router = useRouter();
  const [fundingData, setFundingData] = useState<FundingDistribution[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedFilter, setSelectedFilter] = useState<string>('total_funding');
  const [underservedHighlight, setUnderservedHighlight] = useState<boolean>(false);
  const [selectedCountry, setSelectedCountry] = useState<FundingDistribution | null>(null);
  
  useEffect(() => {
    const fetchFundingDistribution = async () => {
      try {
        setLoading(true);
        // In production, replace with actual API endpoint
        const res = await fetch('http://localhost:8000/api/v1/analytics/funding-distribution');
        
        if (!res.ok) {
          throw new Error(`HTTP error! status: ${res.status}`);
        }
        
        const data = await res.json();
        setFundingData(data);
      } catch (error) {
        console.error('Failed to fetch funding distribution:', error);
        setError('Failed to load funding distribution data.');
        
        // Fallback data for demonstration
        setFundingData([
          { country_code: 'NG', country_name: 'Nigeria', total_funding: 8500000, opportunity_count: 25, percentage_of_total: 28 },
          { country_code: 'KE', country_name: 'Kenya', total_funding: 6200000, opportunity_count: 19, percentage_of_total: 21 },
          { country_code: 'ZA', country_name: 'South Africa', total_funding: 5700000, opportunity_count: 17, percentage_of_total: 19 },
          { country_code: 'EG', country_name: 'Egypt', total_funding: 4300000, opportunity_count: 14, percentage_of_total: 15 },
          { country_code: 'GH', country_name: 'Ghana', total_funding: 2100000, opportunity_count: 8, percentage_of_total: 7 },
          { country_code: 'RW', country_name: 'Rwanda', total_funding: 1500000, opportunity_count: 6, percentage_of_total: 5 },
          { country_code: 'ET', country_name: 'Ethiopia', total_funding: 800000, opportunity_count: 4, percentage_of_total: 3 },
          { country_code: 'CM', country_name: 'Cameroon', total_funding: 200000, opportunity_count: 2, percentage_of_total: 1 },
          { country_code: 'ML', country_name: 'Mali', total_funding: 150000, opportunity_count: 1, percentage_of_total: 0.5 },
          { country_code: 'TD', country_name: 'Chad', total_funding: 50000, opportunity_count: 1, percentage_of_total: 0.5 },
        ]);
      } finally {
        setLoading(false);
      }
    };

    fetchFundingDistribution();
  }, []);

  const getCountryColor = (countryCode: string) => {
    const countryData = fundingData.find(item => item.country_code === countryCode);
    
    if (!countryData) return '#e5e7eb'; // Default gray for countries without data
    
    if (underservedHighlight && countryData.percentage_of_total < 2) {
      // Highlight underserved regions in red
      return '#ef4444';
    }
    
    let value = 0;
    switch(selectedFilter) {
      case 'total_funding':
        value = countryData.total_funding;
        break;
      case 'opportunity_count':
        value = countryData.opportunity_count;
        break;
      case 'percentage_of_total':
        value = countryData.percentage_of_total;
        break;
      default:
        value = countryData.total_funding;
    }
    
    // Color scale from light blue to dark blue based on value
    if (value <= 0) return '#e5e7eb';
    if (value < 100000) return '#dbeafe';
    if (value < 500000) return '#bfdbfe';
    if (value < 1000000) return '#93c5fd';
    if (value < 3000000) return '#60a5fa';
    if (value < 5000000) return '#3b82f6';
    return '#1d4ed8';
  };

  const onCountryClick = (countryCode: string) => {
    const countryData = fundingData.find(item => item.country_code === countryCode);
    if (countryData) {
      setSelectedCountry(countryData);
      // Optionally navigate to country-specific page
      // router.push(`/funding?country=${countryData.country_name}`);
    }
  };

  const countryStyle = (feature: any) => {
    return {
      fillColor: getCountryColor(feature.properties.ISO_A2 || feature.properties.iso_a2),
      weight: 1,
      opacity: 1,
      color: 'white',
      fillOpacity: 0.7
    };
  };

  const onEachCountry = (feature: any, layer: any) => {
    const countryCode = feature.properties.ISO_A2 || feature.properties.iso_a2;
    const countryData = fundingData.find(item => item.country_code === countryCode);
    
    if (countryData) {
      layer.bindTooltip(`
        <strong>${countryData.country_name}</strong><br />
        Total Funding: $${countryData.total_funding.toLocaleString()}<br />
        Opportunities: ${countryData.opportunity_count}<br />
        % of Total: ${countryData.percentage_of_total.toFixed(1)}%
      `);
      
      layer.on({
        click: () => onCountryClick(countryCode)
      });
    } else {
      const name = feature.properties.name || feature.properties.NAME;
      layer.bindTooltip(`<strong>${name}</strong><br />No funding data available`);
    }
  };

  if (loading) {
    return <div className="flex justify-center items-center h-64 bg-gray-50 rounded-lg">Loading funding distribution map...</div>;
  }

  if (error) {
    return (
      <div className="flex justify-center items-center h-64 bg-red-50 rounded-lg text-red-500">
        {error} Please try again later.
      </div>
    );
  }

  return (
    <div className={`${className} bg-white rounded-xl shadow-lg p-4`}>
      <div className="flex flex-col md:flex-row justify-between items-center mb-4">
        <h2 className="text-xl font-bold text-gray-800 mb-2 md:mb-0">Geographic Funding Distribution</h2>
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <label className="text-sm text-gray-600">View by:</label>
            <select
              value={selectedFilter}
              onChange={(e) => setSelectedFilter(e.target.value)}
              className="rounded-md border-gray-300 text-sm focus:border-blue-500 focus:ring focus:ring-blue-500 focus:ring-opacity-50"
            >
              <option value="total_funding">Total Funding</option>
              <option value="opportunity_count">Opportunity Count</option>
              <option value="percentage_of_total">% of Total</option>
            </select>
          </div>
          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              id="underserved"
              checked={underservedHighlight}
              onChange={() => setUnderservedHighlight(!underservedHighlight)}
              className="rounded text-blue-600 focus:ring-blue-500"
            />
            <label htmlFor="underserved" className="text-sm text-gray-600">Highlight underserved regions</label>
          </div>
        </div>
      </div>

      <div className="h-96 rounded-lg overflow-hidden border border-gray-200">
        <MapContainer
          center={[0, 20]} // Center on Africa
          zoom={2}
          style={{ height: "100%", width: "100%" }}
        >
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          />
          <GeoJSON
            data={africanCountriesGeoJSON as any}
            style={countryStyle}
            onEachFeature={onEachCountry}
          />
          <ZoomControl position="bottomright" />
        </MapContainer>
      </div>

      {selectedCountry && (
        <div className="mt-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
          <div className="flex justify-between items-center mb-2">
            <h3 className="text-lg font-bold text-gray-800">{selectedCountry.country_name}</h3>
            <button 
              onClick={() => setSelectedCountry(null)}
              className="text-sm text-gray-500 hover:text-gray-700"
            >
              Close
            </button>
          </div>
          <div className="grid grid-cols-3 gap-4">
            <div>
              <p className="text-sm text-gray-600">Total Funding</p>
              <p className="text-lg font-bold text-blue-600">${selectedCountry.total_funding.toLocaleString()}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Opportunities</p>
              <p className="text-lg font-bold text-green-600">{selectedCountry.opportunity_count}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">% of Total</p>
              <p className="text-lg font-bold text-purple-600">{selectedCountry.percentage_of_total.toFixed(1)}%</p>
            </div>
          </div>
          <div className="mt-3">
            <Link href={`/funding?country=${selectedCountry.country_name}`} className="text-blue-600 hover:underline text-sm">
              View all funding opportunities in {selectedCountry.country_name}
            </Link>
          </div>
        </div>
      )}

      <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-red-50 p-3 rounded-lg border border-red-100">
          <h3 className="text-sm font-medium text-gray-700">Underserved Regions</h3>
          <p className="text-lg font-bold text-red-600">
            {fundingData.filter(item => item.percentage_of_total < 2).length} countries
          </p>
          <p className="text-xs text-gray-500">Receiving &lt;2% of total funding</p>
        </div>
        
        <div className="bg-blue-50 p-3 rounded-lg border border-blue-100">
          <h3 className="text-sm font-medium text-gray-700">Top Recipients</h3>
          <p className="text-lg font-bold text-blue-600">
            {fundingData.filter(item => item.percentage_of_total > 10).length} countries
          </p>
          <p className="text-xs text-gray-500">Receiving &gt;10% of total funding</p>
        </div>
        
        <div className="bg-green-50 p-3 rounded-lg border border-green-100">
          <h3 className="text-sm font-medium text-gray-700">Total Mapped</h3>
          <p className="text-lg font-bold text-green-600">${(fundingData.reduce((sum, item) => sum + item.total_funding, 0) / 1000000).toFixed(1)}M</p>
          <p className="text-xs text-gray-500">Across {fundingData.length} countries</p>
        </div>
        
        <div className="bg-yellow-50 p-3 rounded-lg border border-yellow-100">
          <h3 className="text-sm font-medium text-gray-700">Gini Coefficient</h3>
          <p className="text-lg font-bold text-yellow-600">0.78</p>
          <p className="text-xs text-gray-500">High inequality in distribution</p>
        </div>
      </div>
    </div>
  );
};

export default GeographicEquityMap;
