// components/pathway-selector/PathwaySelector.tsx
import { useState } from 'react';
import Link from 'next/link';
import { Microscope, Briefcase, DollarSign, Globe } from 'lucide-react';

// Define the pathways available to users with inverted color themes
const pathways = [
  {
    id: 'researcher',
    title: 'Researcher / Grantee',
    description: 'Find grants and funding opportunities for AI research projects',
    icon: Microscope,
    theme: 'grants',
    color: 'bg-slate-800',
    hoverColor: 'hover:bg-slate-700',
    textColor: 'text-white',
    accentColor: 'bg-blue-400',
    destination: '/funding/grants',
    features: ['Grant opportunities', 'Academic partnerships', 'Research funding']
  },
  {
    id: 'entrepreneur',
    title: 'Entrepreneur / Startup',
    description: 'Discover investment and accelerator opportunities for AI ventures',
    icon: Briefcase,
    theme: 'investments',
    color: 'bg-white',
    hoverColor: 'hover:bg-gray-50',
    textColor: 'text-gray-900',
    accentColor: 'bg-green-500',
    destination: '/funding/investments',
    features: ['VC funding', 'Accelerator programs', 'Pitch competitions']
  },
  {
    id: 'funder',
    title: 'Funder / Provider',
    description: 'Explore the funding landscape and find potential partners or recipients',
    icon: DollarSign,
    theme: 'neutral',
    color: 'bg-yellow-500',
    hoverColor: 'hover:bg-yellow-400',
    textColor: 'text-gray-900',
    accentColor: 'bg-yellow-600',
    destination: '/organizations?role=recipient',
    features: ['Recipient profiles', 'Impact analytics', 'Funding opportunities']
  },
  {
    id: 'explorer',
    title: 'Just Exploring',
    description: 'Browse the full database of AI funding in Africa',
    icon: Globe,
    theme: 'neutral',
    color: 'bg-purple-600',
    hoverColor: 'hover:bg-purple-500',
    textColor: 'text-white',
    accentColor: 'bg-purple-700',
    destination: '/funding',
    features: ['Complete database', 'All funding types', 'Analytics dashboard']
  }
];

export default function PathwaySelector() {
  const [selected, setSelected] = useState<string | null>(null);

  return (
    <div className="py-12 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-blue-dark mb-4">I am a...</h2>
          <p className="text-lg text-gray-600 max-w-3xl mx-auto">
            Select your role to personalize your TAIFA-FIALA experience
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {pathways.map((pathway) => (
            <div 
              key={pathway.id}
              className={`rounded-xl border-2 transition-all duration-300 cursor-pointer relative ${pathway.color} ${pathway.hoverColor}
                ${selected === pathway.id 
                  ? `shadow-xl transform -translate-y-2 ring-4 ring-opacity-50 ${pathway.accentColor.replace('bg-', 'ring-')}` 
                  : 'shadow-lg hover:shadow-xl hover:transform hover:-translate-y-1'}`}
              onClick={() => setSelected(pathway.id)}
            >
              <div className="p-6">
                <div className={`w-14 h-14 ${pathway.accentColor} ${pathway.theme === 'grants' ? 'text-white' : 'text-white'} rounded-full flex items-center justify-center mb-4 shadow-md`}>
                  <pathway.icon className="w-8 h-8" />
                </div>
                
                <h3 className={`text-xl font-bold mb-2 ${pathway.textColor}`}>{pathway.title}</h3>
                <p className={`mb-4 ${pathway.textColor} ${pathway.theme === 'grants' ? 'text-gray-300' : 'text-gray-600'}`}>
                  {pathway.description}
                </p>
                
                <ul className="mb-8">
                  {pathway.features.map((feature, index) => (
                    <li key={index} className={`flex items-center mb-1 ${pathway.textColor} ${pathway.theme === 'grants' ? 'text-gray-300' : 'text-gray-600'}`}>
                      <svg className={`w-4 h-4 mr-2 ${pathway.theme === 'grants' ? 'text-blue-400' : 'text-green-500'}`} fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                      {feature}
                    </li>
                  ))}
                </ul>
              </div>
              
              <div className={`p-4 border-t ${pathway.theme === 'grants' ? 'border-slate-600' : 'border-gray-200'}`}>
                <Link 
                  href={pathway.destination} 
                  className={`w-full inline-block text-center py-3 rounded-lg font-semibold transition-all duration-200
                    ${selected === pathway.id 
                      ? `${pathway.accentColor} text-white shadow-lg transform scale-105` 
                      : `${pathway.theme === 'grants' ? 'bg-slate-700 text-white hover:bg-slate-600' : 'bg-gray-100 text-gray-900 hover:bg-gray-200'}`}`}
                >
                  Continue as {pathway.title.split('/')[0].trim()} →
                </Link>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}