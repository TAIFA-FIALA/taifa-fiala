'use client';

import React from 'react';
import Link from 'next/link';
import { FundingLifecycleSupport } from '@/components/equity-focus';

export default function FundingLifecyclePage() {
  return (
    <div className="min-h-screen px-4 py-12 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8 flex items-center justify-between">
          <div>
            <div className="flex items-center">
              <Link href="/analytics" className="text-blue hover:text-blue-dark mr-2">
                <span className="flex items-center">
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z" clipRule="evenodd" />
                  </svg>
                  <span className="ml-1">Back to Analytics</span>
                </span>
              </Link>
            </div>
            <h1 className="text-3xl font-bold text-blue-dark mt-2">Funding Lifecycle Support</h1>
            <p className="mt-2 text-lg text-gray-600">
              Breaking the &ldquo;seed trap&rdquo; and supporting AI startups through the full funding lifecycle.
            </p>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
          <FundingLifecycleSupport />
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
          <div className="bg-white rounded-xl shadow-md p-6 border border-gray-100">
            <h3 className="text-xl font-bold text-blue-dark mb-4">The Seed Trap</h3>
            <ul className="space-y-3">
              <li className="flex items-start">
                <div className="flex-shrink-0 w-5 h-5 rounded-full bg-red-100 text-red-600 flex items-center justify-center mt-0.5">
                  <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3 text-gray-700">
                  <span className="font-semibold">Stage Stagnation:</span> 69% of projects never progress beyond seed
                </div>
              </li>
              <li className="flex items-start">
                <div className="flex-shrink-0 w-5 h-5 rounded-full bg-red-100 text-red-600 flex items-center justify-center mt-0.5">
                  <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3 text-gray-700">
                  <span className="font-semibold">Missing Middle:</span> 45% drop in available funding at Series A
                </div>
              </li>
              <li className="flex items-start">
                <div className="flex-shrink-0 w-5 h-5 rounded-full bg-red-100 text-red-600 flex items-center justify-center mt-0.5">
                  <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3 text-gray-700">
                  <span className="font-semibold">Impact Loss:</span> AI solutions fail to reach full-scale deployment
                </div>
              </li>
            </ul>
          </div>
          
          <div className="bg-white rounded-xl shadow-md p-6 border border-gray-100">
            <h3 className="text-xl font-bold text-blue-dark mb-4">Growth Strategies</h3>
            <ul className="space-y-3">
              <li className="flex items-start">
                <div className="flex-shrink-0 w-5 h-5 rounded-full bg-green-100 text-green-600 flex items-center justify-center mt-0.5">
                  <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3 text-gray-700">
                  <span className="font-semibold">Staged Funding:</span> Growth capital reserved for promising seed projects
                </div>
              </li>
              <li className="flex items-start">
                <div className="flex-shrink-0 w-5 h-5 rounded-full bg-green-100 text-green-600 flex items-center justify-center mt-0.5">
                  <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3 text-gray-700">
                  <span className="font-semibold">Consortium Building:</span> Connect startups with strategic institutional partners
                </div>
              </li>
              <li className="flex items-start">
                <div className="flex-shrink-0 w-5 h-5 rounded-full bg-green-100 text-green-600 flex items-center justify-center mt-0.5">
                  <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3 text-gray-700">
                  <span className="font-semibold">Market Access:</span> Platform-enabled connections to scale customers and users
                </div>
              </li>
            </ul>
          </div>
          
          <div className="bg-white rounded-xl shadow-md p-6 border border-gray-100">
            <h3 className="text-xl font-bold text-blue-dark mb-4">Success Metrics</h3>
            <div className="space-y-4">
              <div className="pb-3 border-b border-gray-100">
                <div className="flex justify-between items-center">
                  <p className="font-semibold text-blue-dark">Stage Advancement Rate</p>
                  <span className="inline-block px-2 py-1 bg-amber-100 text-amber-800 text-xs font-semibold rounded-full">31%</span>
                </div>
                <p className="text-sm text-gray-600 mt-1">
                  Target: Increase to 50% within 24 months through targeted support
                </p>
              </div>
              <div className="pb-3 border-b border-gray-100">
                <div className="flex justify-between items-center">
                  <p className="font-semibold text-blue-dark">Funding Matched</p>
                  <span className="inline-block px-2 py-1 bg-green-100 text-green-800 text-xs font-semibold rounded-full">$4.2M</span>
                </div>
                <p className="text-sm text-gray-600 mt-1">
                  Growth capital connected to promising seed-stage ventures
                </p>
              </div>
              <div>
                <div className="flex justify-between items-center">
                  <p className="font-semibold text-blue-dark">Partnerships Formed</p>
                  <span className="inline-block px-2 py-1 bg-blue-100 text-blue-800 text-xs font-semibold rounded-full">34</span>
                </div>
                <p className="text-sm text-gray-600 mt-1">
                  Strategic alliances between startups and established organizations
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
