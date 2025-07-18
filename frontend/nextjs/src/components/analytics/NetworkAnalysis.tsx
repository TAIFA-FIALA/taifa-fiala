'use client';

import { Share2 } from 'lucide-react';

const NetworkAnalysis = () => {
  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
      <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
        <Share2 className="mr-3 h-6 w-6 text-blue-700" />
        Funding Network Structure
      </h3>
      
      {/* Placeholder for NetworkGraph component */}
      <div className="h-64 bg-gray-100 rounded flex items-center justify-center mb-6">
        <p className="text-gray-500">Funding Network Graph Placeholder</p>
      </div>

      {/* Insights */}
      <div>
        <h4 className="font-semibold text-gray-800 mb-2">Key Insights:</h4>
        <p className="text-sm text-gray-700">
          Analysis reveals hub-and-spoke patterns with key intermediary 
          organizations facilitating 67% of funding flows.
        </p>
      </div>
    </div>
  );
};

export default NetworkAnalysis;