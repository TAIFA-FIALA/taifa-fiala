'use client';

import React, { useState } from 'react';
import { MapPin, TrendingUp, Zap, Users, Brain, DollarSign, Shield, Globe, Activity, Target, X } from 'lucide-react';
import Image from 'next/image';

// Feature flag to enable/disable interactive map
// Set to false to disable interactive map functionality
const INTERACTIVE_MAP_ENABLED = process.env.NEXT_PUBLIC_INTERACTIVE_MAP_ENABLED === 'true';

if (INTERACTIVE_MAP_ENABLED) {
  console.log('✅ Interactive Africa AI Map is ENABLED');
} else {
  console.log('⚠️  Interactive Africa AI Map is DISABLED (feature flag)');
}

interface CountryData {
  id: string;
  name: string;
  statistic: string;
  value: string;
  description: string;
  insight: string;
  icon: React.ReactNode;
  color: string;
  category: 'market' | 'innovation' | 'adoption' | 'infrastructure' | 'policy';
}

interface FactoidCardProps {
  country: CountryData | null;
  onClose: () => void;
}

// Country data based on the statistics from the document
const countryData: CountryData[] = [
  {
    id: 'south-africa',
    name: 'South Africa',
    statistic: '600+ AI Companies',
    value: '600+',
    description: 'South Africa hosts over 600 AI companies, the most in Africa, reflecting its status as the continent\'s most developed tech ecosystem.',
    insight: 'Leading with strong research institutions, corporate R&D, and government AI policy framework. Home to DataProphet, which cuts manufacturing defects by 40% using AI.',
    icon: <Brain className="h-6 w-6" />,
    color: 'var(--color-site-slate)',
    category: 'innovation'
  },
  {
    id: 'kenya',
    name: 'Kenya',
    statistic: '27% Daily OpenAI Usage',
    value: '27%',
    description: 'Kenya shows world-leading engagement with AI tools - 27% of Kenyans use OpenAI services like ChatGPT daily.',
    insight: 'Highest AI tool adoption globally, driven by mobile internet penetration, young population, and strong English proficiency. Known as "Silicon Savannah".',
    icon: <Activity className="h-6 w-6" />,
    color: 'var(--color-site-gold)',
    category: 'adoption'
  },
  {
    id: 'nigeria',
    name: 'Nigeria',
    statistic: '400+ AI Firms & 60% Faster Loans',
    value: '400+',
    description: 'Nigeria hosts 400+ AI companies, with fintechs like Periculum using AI to speed up loan processing by 60%.',
    insight: 'Major fintech hub using AI for credit scoring and financial inclusion. Part of the "Big Four" capturing 83% of Africa\'s AI funding.',
    icon: <DollarSign className="h-6 w-6" />,
    color: 'var(--color-site-sage)',
    category: 'market'
  },
  {
    id: 'egypt',
    name: 'Egypt',
    statistic: '$50B AI-Powered E-Commerce',
    value: '$50B',
    description: 'Egypt\'s e-commerce market, fueled by AI recommendation engines, is projected to reach $50 billion by 2025.',
    insight: 'Rapid digital commerce growth driven by AI algorithms for personalization, dynamic pricing, and logistics optimization in a 100M+ population market.',
    icon: <TrendingUp className="h-6 w-6" />,
    color: 'var(--color-site-brown)',
    category: 'market'
  },
  {
    id: 'rwanda',
    name: 'Rwanda',
    statistic: '62% Adults on AI Telehealth',
    value: '62%',
    description: 'Rwanda\'s Babyl telemedicine platform uses AI triage to serve 62% of adults with 5M+ consultations and 91% satisfaction.',
    insight: 'Revolutionary AI-driven healthcare reducing unnecessary clinic visits by 54%. First African country with national AI policy (2020).',
    icon: <Shield className="h-6 w-6" />,
    color: 'var(--color-site-brown)',
    category: 'innovation'
  },
  {
    id: 'ghana',
    name: 'Ghana',
    statistic: '45% Reduction in Drug Stockouts',
    value: '45%',
    description: 'Ghana\'s mPharma uses AI predictive analytics to reduce drug stockouts by 45% and cut patient costs by 37%.',
    insight: 'AI-driven pharmaceutical supply chain optimization removing thousands of counterfeit drugs while improving availability and affordability.',
    icon: <Target className="h-6 w-6" />,
    color: 'var(--color-site-purple)',
    category: 'innovation'
  },
  {
    id: 'morocco',
    name: 'Morocco',
    statistic: 'Africa\'s Most Powerful Supercomputer',
    value: 'Toubkal',
    description: 'Morocco unveiled "Toubkal" in 2023, Africa\'s most powerful supercomputer to support AI research.',
    insight: 'Strategic investment in high-performance computing infrastructure, surpassing South Africa\'s previous top system to advance regional AI capabilities.',
    icon: <Zap className="h-6 w-6" />,
    color: 'var(--color-site-slate)',
    category: 'infrastructure'
  },
  {
    id: 'togo',
    name: 'Togo',
    statistic: '57,000 People Targeted with AI',
    value: '57,000',
    description: 'Togo used AI analytics to identify 57,000 new beneficiaries for its Novissi cash transfer program without physical surveys.',
    insight: 'Pioneering AI for social good, using satellite imagery and mobile data to improve social aid targeting and ensure relief reaches overlooked communities.',
    icon: <Users className="h-6 w-6" />,
    color: 'var(--color-site-gold)',
    category: 'policy'
  },
  {
    id: 'mauritius',
    name: 'Mauritius',
    statistic: 'Highest AI Readiness in Africa',
    value: '53.3/100',
    description: 'Mauritius leads Africa on the Government AI Readiness Index with a score of 53.3, excelling in government commitment and vision.',
    insight: 'Top-ranked for AI preparedness in governance, showing that smaller economies can advance AI policy and digital infrastructure effectively.',
    icon: <Globe className="h-6 w-6" />,
    color: 'var(--color-site-sage)',
    category: 'policy'
  }
];

// Interactive Africa SVG map using real Africa outline
const AfricaMapSVG: React.FC<{ onCountryClick: (countryId: string) => void, selectedCountry: string | null }> = ({ onCountryClick, selectedCountry }) => {
  return (
    <div className="relative w-full max-w-2xl mx-auto">
      {/* Background Africa SVG */}
      <div className="relative w-full h-96 bg-slate-50/20 rounded-lg overflow-hidden">
        <Image 
          src="/np_africa_3354_1A365D.svg" 
          alt="Map of Africa"
          fill
          className="object-contain opacity-30"
          priority={false}
        />
        
        {/* Interactive overlay with positioned country markers */}
        <div className="absolute inset-0">
          <svg viewBox="0 0 400 400" className="w-full h-full">
            {/* Morocco - Northwest Africa */}
            <circle
              id="morocco"
              cx="195"
              cy="90"
              r="8"
              fill={selectedCountry === 'morocco' ? 'var(--color-site-gold)' : 'var(--color-site-slate)'}
              stroke="white" 
              strokeWidth="2"
              className="cursor-pointer hover:opacity-80 transition-all duration-200 drop-shadow-lg"
              onClick={() => onCountryClick('morocco')}
            />
            
            {/* Egypt - Northeast Africa */}
            <circle
              id="egypt"
              cx="295"
              cy="95"
              r="8"
              fill={selectedCountry === 'egypt' ? 'var(--color-site-brown)' : 'var(--color-site-slate)'}
              stroke="white" 
              strokeWidth="2"
              className="cursor-pointer hover:opacity-80 transition-all duration-200 drop-shadow-lg"
              onClick={() => onCountryClick('egypt')}
            />
            
            {/* Nigeria - West Africa */}
            <circle
              id="nigeria"
              cx="190"
              cy="175"
              r="8"
              fill={selectedCountry === 'nigeria' ? 'var(--color-taifa-secondary)' : 'var(--color-site-slate)'}
              stroke="white" 
              strokeWidth="2"
              className="cursor-pointer hover:opacity-80 transition-all duration-200 drop-shadow-lg"
              onClick={() => onCountryClick('nigeria')}
            />
            
            {/* Ghana - West Africa */}
            <circle
              id="ghana"
              cx="180"
              cy="185"
              r="6"
              fill={selectedCountry === 'ghana' ? 'var(--color-site-purple)' : 'var(--color-site-slate)'}
              stroke="white" 
              strokeWidth="2"
              className="cursor-pointer hover:opacity-80 transition-all duration-200 drop-shadow-lg"
              onClick={() => onCountryClick('ghana')}
            />
            
            {/* Kenya - East Africa */}
            <circle
              id="kenya"
              cx="300"
              cy="195"
              r="8"
              fill={selectedCountry === 'kenya' ? 'var(--color-site-gold)' : 'var(--color-site-slate)'}
              stroke="white" 
              strokeWidth="2"
              className="cursor-pointer hover:opacity-80 transition-all duration-200 drop-shadow-lg"
              onClick={() => onCountryClick('kenya')}
            />
            
            {/* Rwanda - East Africa */}
            <circle
              id="rwanda"
              cx="285"
              cy="205"
              r="5"
              fill={selectedCountry === 'rwanda' ? 'var(--color-site-brown)' : 'var(--color-site-slate)'}
              stroke="white" 
              strokeWidth="2"
              className="cursor-pointer hover:opacity-80 transition-all duration-200 drop-shadow-lg"
              onClick={() => onCountryClick('rwanda')}
            />
            
            {/* South Africa - Southern Africa */}
            <circle
              id="south-africa"
              cx="270"
              cy="320"
              r="10"
              fill={selectedCountry === 'south-africa' ? 'var(--color-taifa-secondary)' : 'var(--color-site-slate)'}
              stroke="white" 
              strokeWidth="2"
              className="cursor-pointer hover:opacity-80 transition-all duration-200 drop-shadow-lg"
              onClick={() => onCountryClick('south-africa')}
            />
            
            {/* Mauritius - Island off East Coast */}
            <circle
              id="mauritius"
              cx="325"
              cy="280"
              r="4"
              fill={selectedCountry === 'mauritius' ? 'var(--color-taifa-secondary)' : 'var(--color-site-slate)'}
              stroke="white"
              strokeWidth="2"
              className="cursor-pointer hover:opacity-80 transition-all duration-200 drop-shadow-lg"
              onClick={() => onCountryClick('mauritius')}
            />
            
            {/* Country labels */}
            <text x="195" y="80" fontSize="12" fill="var(--color-site-slate)" textAnchor="middle" className="pointer-events-none font-semibold drop-shadow-sm">Morocco</text>
            <text x="295" y="85" fontSize="12" fill="var(--color-site-slate)" textAnchor="middle" className="pointer-events-none font-semibold drop-shadow-sm">Egypt</text>
            <text x="190" y="165" fontSize="12" fill="var(--color-site-slate)" textAnchor="middle" className="pointer-events-none font-semibold drop-shadow-sm">Nigeria</text>
            <text x="180" y="175" fontSize="10" fill="var(--color-site-slate)" textAnchor="middle" className="pointer-events-none font-semibold drop-shadow-sm">Ghana</text>
            <text x="300" y="185" fontSize="12" fill="var(--color-site-slate)" textAnchor="middle" className="pointer-events-none font-semibold drop-shadow-sm">Kenya</text>
            <text x="285" y="195" fontSize="9" fill="var(--color-site-slate)" textAnchor="middle" className="pointer-events-none font-semibold drop-shadow-sm">Rwanda</text>
            <text x="270" y="310" fontSize="12" fill="var(--color-site-slate)" textAnchor="middle" className="pointer-events-none font-semibold drop-shadow-sm">South Africa</text>
            <text x="325" y="270" fontSize="8" fill="var(--color-site-slate)" textAnchor="middle" className="pointer-events-none font-semibold drop-shadow-sm">Mauritius</text>
          </svg>
        </div>
      </div>
      
      <div className="absolute bottom-4 left-4 bg-white/90 backdrop-blur-sm px-4 py-2 rounded-lg border border-slate-200 shadow-lg">
        <p className="text-sm text-slate-600 flex items-center">
          <MapPin className="h-4 w-4 mr-2 text-site-gold" />
          Click on countries to explore AI insights
        </p>
      </div>
    </div>
  );
};

// Factoid card component
const FactoidCard: React.FC<FactoidCardProps> = ({ country, onClose }) => {
  if (!country) return null;

  const categoryColors = {
    market: 'border-site-sage bg-site-sage/5',
    innovation: 'border-site-slate bg-site-slate/5',
    adoption: 'border-site-gold bg-site-gold/5',
    infrastructure: 'border-site-brown bg-site-brown/5',
    policy: 'border-site-purple bg-site-purple/5'
  };

  const categoryLabels = {
    market: 'Market Growth',
    innovation: 'Innovation',
    adoption: 'AI Adoption',
    infrastructure: 'Infrastructure',
    policy: 'Policy & Governance'
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-fadeInUp">
      <div className={`bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto border-2 ${categoryColors[country.category]} shadow-2xl`}>
        <div className="p-8">
          {/* Header */}
          <div className="flex items-start justify-between mb-6">
            <div className="flex items-center">
              <div className={`p-3 rounded-xl mr-4 ${categoryColors[country.category]}`} style={{ color: country.color }}>
                {country.icon}
              </div>
              <div>
                <h3 className="text-2xl font-bold text-site-slate">{country.name}</h3>
                <span className={`inline-block px-3 py-1 rounded-full text-xs font-medium ${categoryColors[country.category]}`} style={{ color: country.color }}>
                  {categoryLabels[country.category]}
                </span>
              </div>
            </div>
            <button 
              onClick={onClose}
              className="p-2 hover:bg-slate-50 rounded-lg transition-colors"
            >
              <X className="h-5 w-5 text-slate-600" />
            </button>
          </div>

          {/* Main statistic */}
          <div className="mb-6 p-6 bg-gradient-to-r from-taifa-light/50 to-taifa-white rounded-xl border border-slate-200">
            <div className="text-4xl font-bold mb-2" style={{ color: country.color }}>
              {country.value}
            </div>
            <div className="text-xl font-semibold text-site-slate mb-3">
              {country.statistic}
            </div>
            <p className="text-slate-600 leading-relaxed">
              {country.description}
            </p>
          </div>

          {/* Deeper insight */}
          <div className="p-6 bg-site-slate/5 rounded-xl border-l-4 border-taifa-primary">
            <h4 className="text-lg font-semibold text-site-slate mb-3">Key Insight</h4>
            <p className="text-slate-600 leading-relaxed">
              {country.insight}
            </p>
          </div>

          {/* Action button */}
          <div className="mt-6 text-center">
            <button 
              onClick={onClose}
              className="px-6 py-3 bg-site-slate text-white rounded-lg hover:bg-site-gold transition-colors font-medium"
            >
              Explore More Countries
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

// Fallback component when interactive map is disabled
const InteractiveMapFallback: React.FC = () => {
  return (
    <div className="relative">
      <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-8 shadow-xl border border-slate-200">
        <div className="text-center mb-8">
          <h3 className="text-3xl font-bold text-site-slate mb-4">AI Across Africa</h3>
          <p className="text-lg text-slate-600 max-w-3xl mx-auto leading-relaxed">
            Interactive map functionality is currently under development. Check back soon for an engaging exploration of AI innovations across the continent.
          </p>
        </div>

        {/* Static placeholder */}
        <div className="relative w-full max-w-2xl mx-auto">
          <div className="relative w-full h-96 bg-slate-50/20 rounded-lg overflow-hidden flex items-center justify-center">
            <div className="text-center">
              <Globe className="h-16 w-16 text-slate-600 mx-auto mb-4" />
              <p className="text-slate-600 font-medium">Interactive Map Coming Soon</p>
              <p className="text-sm text-slate-600/70 mt-2">Feature currently disabled</p>
            </div>
          </div>
        </div>

        {/* Static legend */}
        <div className="mt-8 grid grid-cols-2 md:grid-cols-5 gap-4 text-center opacity-50">
          <div className="flex flex-col items-center">
            <div className="w-4 h-4 bg-site-sage rounded mb-2"></div>
            <span className="text-xs text-slate-600">Market Growth</span>
          </div>
          <div className="flex flex-col items-center">
            <div className="w-4 h-4 bg-site-slate rounded mb-2"></div>
            <span className="text-xs text-slate-600">Innovation</span>
          </div>
          <div className="flex flex-col items-center">
            <div className="w-4 h-4 bg-site-gold rounded mb-2"></div>
            <span className="text-xs text-slate-600">AI Adoption</span>
          </div>
          <div className="flex flex-col items-center">
            <div className="w-4 h-4 bg-site-brown rounded mb-2"></div>
            <span className="text-xs text-slate-600">Infrastructure</span>
          </div>
          <div className="flex flex-col items-center">
            <div className="w-4 h-4 bg-site-purple rounded mb-2"></div>
            <span className="text-xs text-slate-600">Policy & Governance</span>
          </div>
        </div>
      </div>
    </div>
  );
};

// Main component with feature flag logic
const InteractiveAfricaAIMap: React.FC = () => {
  const [selectedCountry, setSelectedCountry] = useState<string | null>(null);
  const [selectedCountryData, setSelectedCountryData] = useState<CountryData | null>(null);

  const handleCountryClick = (countryId: string) => {
    const country = countryData.find(c => c.id === countryId);
    if (country) {
      setSelectedCountry(countryId);
      setSelectedCountryData(country);
    }
  };

  const handleCloseCard = () => {
    setSelectedCountry(null);
    setSelectedCountryData(null);
  };

  // Return fallback component if feature is disabled
  if (!INTERACTIVE_MAP_ENABLED) {
    return <InteractiveMapFallback />;
  }

  return (
    <div className="relative">
      {/* Map container */}
      <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-8 shadow-xl border border-slate-200">
        <div className="text-center mb-8">
          <h3 className="text-3xl font-bold text-site-slate mb-4">AI Across Africa</h3>
          <p className="text-lg text-slate-600 max-w-3xl mx-auto leading-relaxed">
            Discover fascinating AI statistics and innovations happening across the continent. Click on any highlighted country to explore their unique AI story.
          </p>
        </div>

        <AfricaMapSVG onCountryClick={handleCountryClick} selectedCountry={selectedCountry} />

        {/* Legend */}
        <div className="mt-8 grid grid-cols-2 md:grid-cols-5 gap-4 text-center">
          <div className="flex flex-col items-center">
            <div className="w-4 h-4 bg-site-sage rounded mb-2"></div>
            <span className="text-xs text-slate-600">Market Growth</span>
          </div>
          <div className="flex flex-col items-center">
            <div className="w-4 h-4 bg-site-slate rounded mb-2"></div>
            <span className="text-xs text-slate-600">Innovation</span>
          </div>
          <div className="flex flex-col items-center">
            <div className="w-4 h-4 bg-site-gold rounded mb-2"></div>
            <span className="text-xs text-slate-600">AI Adoption</span>
          </div>
          <div className="flex flex-col items-center">
            <div className="w-4 h-4 bg-site-brown rounded mb-2"></div>
            <span className="text-xs text-slate-600">Infrastructure</span>
          </div>
          <div className="flex flex-col items-center">
            <div className="w-4 h-4 bg-site-purple rounded mb-2"></div>
            <span className="text-xs text-slate-600">Policy & Governance</span>
          </div>
        </div>
      </div>

      {/* Factoid card overlay */}
      <FactoidCard country={selectedCountryData} onClose={handleCloseCard} />
    </div>
  );
};

export default InteractiveAfricaAIMap;
