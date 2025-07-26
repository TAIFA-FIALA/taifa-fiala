'use client';

import React, { useState } from 'react';
import { MapPin, TrendingUp, Zap, Users, Brain, DollarSign, Shield, Globe, Activity, Target, X } from 'lucide-react';

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
    color: 'var(--taifa-primary)',
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
    color: 'var(--taifa-secondary)',
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
    color: 'var(--taifa-accent)',
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
    color: 'var(--taifa-orange)',
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
    color: 'var(--taifa-red)',
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
    color: 'var(--taifa-olive)',
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
    color: 'var(--taifa-primary)',
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
    color: 'var(--taifa-secondary)',
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
    color: 'var(--taifa-accent)',
    category: 'policy'
  }
];

// Simplified Africa SVG map
const AfricaMapSVG: React.FC<{ onCountryClick: (countryId: string) => void, selectedCountry: string | null }> = ({ onCountryClick, selectedCountry }) => {
  return (
    <div className="relative w-full max-w-2xl mx-auto">
      <svg  
        viewBox="0 0 800660" 
        className="w-full h-full"
        style={{ maxHeight: '500px' }}
      >
        {/* Morocco */}
        <path
          id="morocco"
          d="M180 120 L280 110 L290 130 L285 150 L270 160 L250 155 L230 165 L210 155 L190 140 Z"
          fill={selectedCountry === 'morocco' ? 'var(--taifa-olive)' : 'var(--taifa-light)'}
          stroke="var(--taifa-border)" 
          strokeWidth="2"
          className="cursor-pointer hover:fill-taifa-secondary/30 transition-colors duration-200"
          onClick={() => onCountryClick('morocco')}
        />
        
        {/* Egypt */}
        <path
          id="egypt"
          d="M420 180 L480 175 L485 200 L490 220 L485 240 L470 250 L450 245 L430 235 L420 210 Z"
          fill={selectedCountry === 'egypt' ? 'var(--taifa-red)' : 'var(--taifa-light)'}
          stroke="var(--taifa-border)" 
          strokeWidth="2"
          className="cursor-pointer hover:fill-taifa-secondary/30 transition-colors duration-200"
          onClick={() => onCountryClick('egypt')}
        />
        
        {/* Nigeria */}
        <path
          id="nigeria"
          d="M250 350 L320 345 L330 360 L335 380 L325 400 L310 410 L290 415 L270 410 L255 395 L245 375 L248 360 Z"
          fill={selectedCountry === 'nigeria' ? 'var(--taifa-accent)' : 'var(--taifa-light)'}
          stroke="var(--taifa-border)" 
          strokeWidth="2"
          className="cursor-pointer hover:fill-taifa-secondary/30 transition-colors duration-200"
          onClick={() => onCountryClick('nigeria')}
        />
        
        {/* Ghana */}
        <path
          id="ghana"
          d="M210 400 L240 395 L245 410 L240 425 L225 430 L210 425 L205 410 Z"
          fill={selectedCountry === 'ghana' ? 'var(--taifa-orange)' : 'var(--taifa-light)'}
          stroke="var(--taifa-border)" 
          strokeWidth="2"
          className="cursor-pointer hover:fill-taifa-secondary/30 transition-colors duration-200"
          onClick={() => onCountryClick('ghana')}
        />
        
        {/* Togo */}
        <path
          id="togo"
          d="M225 430 L240 425 L242 440 L238 450 L230 452 L225 445 Z"
          fill={selectedCountry === 'togo' ? 'var(--taifa-red)' : 'var(--taifa-light)'}
          stroke="var(--taifa-border)" 
          strokeWidth="2"
          className="cursor-pointer hover:fill-taifa-secondary/30 transition-colors duration-200"
          onClick={() => onCountryClick('togo')}
        />
        
        {/* Kenya */}
        <path
          id="kenya"
          d="M480 400 L520 395 L525 415 L530 435 L525 450 L515 460 L500 465 L485 460 L475 445 L478 425 L480 405 Z"
          fill={selectedCountry === 'kenya' ? 'var(--taifa-secondary)' : 'var(--taifa-light)'}
          stroke="var(--taifa-border)" 
          strokeWidth="2"
          className="cursor-pointer hover:fill-taifa-secondary/30 transition-colors duration-200"
          onClick={() => onCountryClick('kenya')}
        />
        
        {/* Rwanda */}
        <path
          id="rwanda"
          d="M470 450 L485 445 L490 460 L485 470 L475 472 L470 465 Z"
          fill={selectedCountry === 'rwanda' ? 'var(--taifa-red)' : 'var(--taifa-light)'}
          stroke="var(--taifa-border)" 
          strokeWidth="2"
          className="cursor-pointer hover:fill-taifa-secondary/30 transition-colors duration-200"
          onClick={() => onCountryClick('rwanda')}
        />
        
        {/* South Africa */}
        <path
          id="south-africa"
          d="M350 620 L450 615 L480 625 L490 650 L485 680 L470 700 L450 710 L420 715 L390 710 L365 700 L350 685 L345 665 L348 645 Z"
          fill={selectedCountry === 'south-africa' ? 'var(--taifa-primary)' : 'var(--taifa-light)'}
          stroke="var(--taifa-border)" 
          strokeWidth="2"
          className="cursor-pointer hover:fill-taifa-secondary/30 transition-colors duration-200"
          onClick={() => onCountryClick('south-africa')}
        />
        
        {/* Mauritius (small island) */}
        <circle
          id="mauritius"
          cx="550"
          cy="680"
          r="8"
          fill={selectedCountry === 'mauritius' ? 'var(--taifa-accent)' : 'var(--taifa-light)'}
          stroke="var(--taifa-border)"
          strokeWidth="2"
          className="cursor-pointer hover:fill-taifa-secondary/30 transition-colors duration-200"
          onClick={() => onCountryClick('mauritius')}
        />
        
        {/* Africa continent outline */}
        <path
          d="20 Q150 continent 140 140 180 Q135 220 145 260 Q150 300 160 340 Q170 380 185 420 Q200 460 220 500 Q240 540 270 580 Q300 620 340 650 Q380 680 420 700 Q460 720 500 715 Q540 710 570 690 Q590 670 600 640 Q610 600 605 560 Q600 520 590 480 Q580 440 570 400 Q560 360 545 320 Q530 280 510 240 Q490 200 470 170 Q450 140 420 120 Q390 105 360 110 Q330 115 300 115 Q270 115 240 118 Q210 120 180 120 Z"
          fill="none"
          stroke="var(--taifa-muted)"
          strokeWidth="2"
          strokeDasharray="3,3"
          opacity="0.4"
        />
        
        {/* Country labels */}
        <text x="235" y="140" fontSize="11" fill="var(--taifa-muted)" textAnchor="middle" className="pointer-events-none font-medium">Morocco</text>
        <text x="450" y="210" fontSize="11" fill="var(--taifa-muted)" textAnchor="middle" className="pointer-events-none font-medium">Egypt</text>
        <text x="285" y="340" fontSize="11" fill="var(--taifa-muted)" textAnchor="middle" className="pointer-events-none font-medium font-medium">Nigeria</text>
        <text x="252" y="418" fontSize="11" fill="var(--taifa-muted)" textAnchor="middle" className="pointer-events-none font-medium font-medium">Ghana</text>
        <text x="232" y="385" fontSize="11" fill="var(--taifa-muted)" textAnchor="middle" className="pointer-events-none font-medium font-medium">Togo</text>
        <text x="505" y="418" fontSize="11" fill="var(--taifa-muted)" textAnchor="middle" className="pointer-events-none font-medium font-medium">Kenya</text>
        <text x="482" y="465" fontSize="10" fill="var(--taifa-muted)" textAnchor="middle" className="pointer-eventsnone font-medium font-medium">Rwanda</text>
        <text x="420" y="670" fontSize="11" fill="var(--taifa-muted)" textAnchor="middle" className="pointer-events-none font-medium font-medium">South Africa</text>
        <text x="565" y="690" fontSize="9" fill="var(--taifa-muted)" textAnchor="middle" className="pointer-events-none font-medium font-medium">Mauritius</text>
      </svg>    
      <div className="absolute bottom-4 left-4 bg-taifa-white/90 backdrop-blur-sm px-4 py-2 rounded-lg border border-taifa-border shadow-lg">
        <p className="text-sm text-taifa-muted flex items-center">
          <MapPin className="h-4 w-4 mr-2 text-taifa-secondary" />
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
    market: 'border-taifa-accent bg-taifa-accent/5',
    innovation: 'border-taifa-primary bg-taifa-primary/5',
    adoption: 'border-taifa-secondary bg-taifa-secondary/5',
    infrastructure: 'border-taifa-orange bg-taifa-orange/5',
    policy: 'border-taifa-olive bg-taifa-olive/5'
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
      <div className={`bg-taifa-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto border-2 ${categoryColors[country.category]} shadow-2xl`}>
        <div className="p-8">
          {/* Header */}
          <div className="flex items-start justify-between mb-6">
            <div className="flex items-center">
              <div className={`p-3 rounded-xl mr-4 ${categoryColors[country.category]}`} style={{ color: country.color }}>
                {country.icon}
              </div>
              <div>
                <h3 className="text-2xl font-bold text-taifa-primary">{country.name}</h3>
                <span className={`inline-block px-3 py-1 rounded-full text-xs font-medium ${categoryColors[country.category]}`} style={{ color: country.color }}>
                  {categoryLabels[country.category]}
                </span>
              </div>
            </div>
            <button 
              onClick={onClose}
              className="p-2 hover:bg-taifa-light rounded-lg transition-colors"
            >
              <X className="h-5 w-5 text-taifa-muted" />
            </button>
          </div>

          {/* Main statistic */}
          <div className="mb-6 p-6 bg-gradient-to-r from-taifa-light/50 to-taifa-white rounded-xl border border-taifa-border">
            <div className="text-4xl font-bold mb-2" style={{ color: country.color }}>
              {country.value}
            </div>
            <div className="text-xl font-semibold text-taifa-primary mb-3">
              {country.statistic}
            </div>
            <p className="text-taifa-muted leading-relaxed">
              {country.description}
            </p>
          </div>

          {/* Deeper insight */}
          <div className="p-6 bg-taifa-primary/5 rounded-xl border-l-4 border-taifa-primary">
            <h4 className="text-lg font-semibold text-taifa-primary mb-3">Key Insight</h4>
            <p className="text-taifa-muted leading-relaxed">
              {country.insight}
            </p>
          </div>

          {/* Action button */}
          <div className="mt-6 text-center">
            <button 
              onClick={onClose}
              className="px-6 py-3 bg-taifa-primary text-taifa-white rounded-lg hover:bg-taifa-secondary transition-colors font-medium"
            >
              Explore More Countries
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

// Main component
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

  return (
    <div className="relative">
      {/* Map container */}
      <div className="bg-taifa-white/80 backdrop-blur-sm rounded-2xl p-8 shadow-xl border border-taifa-border">
        <div className="text-center mb-8">
          <h3 className="text-3xl font-bold text-taifa-primary mb-4">AI Across Africa</h3>
          <p className="text-lg text-taifa-muted max-w-3xl mx-auto leading-relaxed">
            Discover fascinating AI statistics and innovations happening across the continent. Click on any highlighted country to explore their unique AI story.
          </p>
        </div>

        <AfricaMapSVG onCountryClick={handleCountryClick} selectedCountry={selectedCountry} />

        {/* Legend */}
        <div className="mt-8 grid grid-cols-2 md:grid-cols-5 gap-4 text-center">
          <div className="flex flex-col items-center">
            <div className="w-4 h-4 bg-taifa-accent rounded mb-2"></div>
            <span className="text-xs text-taifa-muted">Market Growth</span>
          </div>
          <div className="flex flex-col items-center">
            <div className="w-4 h-4 bg-taifa-primary rounded mb-2"></div>
            <span className="text-xs text-taifa-muted">Innovation</span>
          </div>
          <div className="flex flex-col items-center">
            <div className="w-4 h-4 bg-taifa-secondary rounded mb-2"></div>
            <span className="text-xs text-taifa-muted">AI Adoption</span>
          </div>
          <div className="flex flex-col items-center">
            <div className="w-4 h-4 bg-taifa-orange rounded mb-2"></div>
            <span className="text-xs text-taifa-muted">Infrastructure</span>
          </div>
          <div className="flex flex-col items-center">
            <div className="w-4 h-4 bg-taifa-olive rounded mb-2"></div>
            <span className="text-xs text-taifa-muted">Policy & Governance</span>
          </div>
        </div>
      </div>

      {/* Factoid card overlay */}
      <FactoidCard country={selectedCountryData} onClose={handleCloseCard} />
    </div>
  );
};

export default InteractiveAfricaAIMap;

