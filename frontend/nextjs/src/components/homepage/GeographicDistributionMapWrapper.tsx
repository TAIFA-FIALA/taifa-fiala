'use client';

import dynamic from 'next/dynamic';
import { Suspense } from 'react';

// Dynamically import map component with SSR disabled to prevent hydration issues
const GeographicDistributionMap = dynamic(
  () => import('@/components/homepage/GeographicDistributionMap'),
  { 
    ssr: false,
    loading: () => (
      <div className="flex items-center justify-center h-96 bg-gray-50 rounded-lg">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-taifa-primary mx-auto mb-2"></div>
          <p className="text-gray-600">Loading map...</p>
        </div>
      </div>
    )
  }
);

const GeographicDistributionMapWrapper = () => {
  return (
    <Suspense fallback={
      <div className="flex items-center justify-center h-96 bg-gray-50 rounded-lg">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-taifa-primary mx-auto mb-2"></div>
          <p className="text-gray-600">Loading map...</p>
        </div>
      </div>
    }>
      <GeographicDistributionMap />
    </Suspense>
  );
};

export default GeographicDistributionMapWrapper;
