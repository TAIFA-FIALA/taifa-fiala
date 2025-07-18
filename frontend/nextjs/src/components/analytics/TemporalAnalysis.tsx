'use client';

import { TrendingUp } from 'lucide-react';

const TemporalAnalysis = () => {
  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
      <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
        <TrendingUp className="mr-3 h-6 w-6 text-blue-700" />
        Temporal Patterns
      </h3>
      
      {/* Placeholder for TimelineVisualization component */}
      <div className="h-64 bg-gray-100 rounded flex items-center justify-center mb-6">
        <p className="text-gray-500">Funding Flows Over Time Placeholder</p>
      </div>

      {/* Observations */}
      <div>
        <h4 className="font-semibold text-gray-800 mb-2">Key Observations:</h4>
        <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
          <li>Funding announcements cluster in Q4 (October-December).</li>
          <li>3-6 month lag between partnership announcements and funding calls.</li>
          <li>Election years show a 34% decrease in government-led funding initiatives.</li>
        </ul>
      </div>
    </div>
  );
};

export default TemporalAnalysis;