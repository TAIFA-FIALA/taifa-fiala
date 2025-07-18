'use client';

import React from 'react';
import Link from 'next/link';
import { GenderInclusionDashboard } from '@/components/equity-focus';

export default function GenderInclusionPage() {
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
            <h1 className="text-3xl font-bold text-blue-dark mt-2">Gender & Inclusion Dashboard</h1>
            <p className="mt-2 text-lg text-gray-600">
              Tracking and addressing the gender funding gap and promoting inclusive AI development.
            </p>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
          <GenderInclusionDashboard />
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
          <div className="bg-white rounded-xl shadow-md p-6 border border-gray-100">
            <h3 className="text-xl font-bold text-blue-dark mb-4">Key Challenges</h3>
            <ul className="space-y-3">
              <li className="flex items-start">
                <div className="flex-shrink-0 w-5 h-5 rounded-full bg-red-100 text-red-600 flex items-center justify-center mt-0.5">
                  <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3 text-gray-700">
                  <span className="font-semibold">Severe Gender Gap:</span> Only 2% of funding to female-led AI projects
                </div>
              </li>
              <li className="flex items-start">
                <div className="flex-shrink-0 w-5 h-5 rounded-full bg-red-100 text-red-600 flex items-center justify-center mt-0.5">
                  <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3 text-gray-700">
                  <span className="font-semibold">Network Access:</span> 73% of accelerator spots go to male founders
                </div>
              </li>
              <li className="flex items-start">
                <div className="flex-shrink-0 w-5 h-5 rounded-full bg-red-100 text-red-600 flex items-center justify-center mt-0.5">
                  <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3 text-gray-700">
                  <span className="font-semibold">Intersectional Gaps:</span> Rural women receive 0.5% of total AI funding
                </div>
              </li>
            </ul>
          </div>
          
          <div className="bg-white rounded-xl shadow-md p-6 border border-gray-100">
            <h3 className="text-xl font-bold text-blue-dark mb-4">Targeted Interventions</h3>
            <ul className="space-y-3">
              <li className="flex items-start">
                <div className="flex-shrink-0 w-5 h-5 rounded-full bg-green-100 text-green-600 flex items-center justify-center mt-0.5">
                  <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3 text-gray-700">
                  <span className="font-semibold">Dedicated Funding:</span> 20% set-aside for women-led AI ventures
                </div>
              </li>
              <li className="flex items-start">
                <div className="flex-shrink-0 w-5 h-5 rounded-full bg-green-100 text-green-600 flex items-center justify-center mt-0.5">
                  <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3 text-gray-700">
                  <span className="font-semibold">Mentorship Network:</span> Connect 250+ experienced mentors with female founders
                </div>
              </li>
              <li className="flex items-start">
                <div className="flex-shrink-0 w-5 h-5 rounded-full bg-green-100 text-green-600 flex items-center justify-center mt-0.5">
                  <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3 text-gray-700">
                  <span className="font-semibold">Technical Capacity:</span> AI bootcamps targeting 5,000 women developers
                </div>
              </li>
            </ul>
          </div>
          
          <div className="bg-white rounded-xl shadow-md p-6 border border-gray-100">
            <h3 className="text-xl font-bold text-blue-dark mb-4">Success Stories</h3>
            <div className="space-y-4">
              <div className="pb-3 border-b border-gray-100">
                <p className="font-semibold text-blue-dark">FarmSense AI</p>
                <p className="text-sm text-gray-600 mt-1">
                  Women-led AgTech startup raised $2.4M to deploy AI soil analysis sensors, impacting 15,000 farmers.
                </p>
              </div>
              <div className="pb-3 border-b border-gray-100">
                <p className="font-semibold text-blue-dark">HealthMate Tanzania</p>
                <p className="text-sm text-gray-600 mt-1">
                  All-female team built AI maternal health app now serving 250,000 women in 4 countries.
                </p>
              </div>
              <div>
                <p className="font-semibold text-blue-dark">EduBot South Africa</p>
                <p className="text-sm text-gray-600 mt-1">
                  Founded by 3 female engineers, their AI education platform has reached 1.2M students.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
