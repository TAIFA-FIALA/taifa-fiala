'use client';

import { Map } from 'lucide-react';

// Sample data - in a real application, this would be passed as props
const geoData = [
  { region: 'East Africa', countries: 12, events: 890, total: '450M', perCapita: '$1.12' },
  { region: 'West Africa', countries: 15, events: 750, total: '250M', perCapita: '$0.65' },
  { region: 'Southern Africa', countries: 10, events: 520, total: '180M', perCapita: '$2.70' },
  { region: 'North Africa', countries: 5, events: 250, total: '120M', perCapita: '$0.50' },
  { region: 'Central Africa', countries: 9, events: 57, total: '12M', perCapita: '$0.07' },
];

const GeographicAnalysis = () => {
  return (
    <div className="lg:col-span-2 bg-taifa-white p-6 rounded-lg shadow-sm border border-gray-200">
      <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
        <Map className="mr-3 h-6 w-6 text-taifa-orange" />
        Geographic Distribution
      </h3>
      
      {/* Placeholder for AfricaMap component */}
      <div className="h-96 bg-taifa-white rounded flex items-center justify-center mb-6">
        <p className="text-taifa-muted">Africa Map with Funding Density Placeholder</p>
      </div>

      {/* Data Table */}
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Region
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Countries
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Funding Events
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Total Tracked (USD)
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Per Capita (USD)
              </th>
            </tr>
          </thead>
          <tbody className="bg-taifa-white divide-y divide-gray-200">
            {geoData.map((row) => (
              <tr key={row.region}>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{row.region}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{row.countries}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{row.events.toLocaleString()}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{row.total}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{row.perCapita}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default GeographicAnalysis;