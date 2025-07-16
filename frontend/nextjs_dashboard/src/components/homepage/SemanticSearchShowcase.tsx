"use client";

import { useState, useEffect } from 'react';
import { Search, Globe, Brain, Zap, Languages } from 'lucide-react';

interface SearchExample {
  query: string;
  language: string;
  flag: string;
  results: number;
  highlights: string[];
}

export default function SemanticSearchShowcase() {
  const [activeExample, setActiveExample] = useState(0);
  const [isSearching, setIsSearching] = useState(false);
  const [currentQuery, setCurrentQuery] = useState('');

  const searchExamples: SearchExample[] = [
    {
      query: "AI healthcare funding rural Central Africa",
      language: "English",
      flag: "🇬🇧",
      results: 23,
      highlights: ["Mali telemedicine grants", "CAR digital health initiative", "Chad mobile health funding"]
    },
    {
      query: "financement agriculture intelligente Afrique francophone",
      language: "Français",
      flag: "🇫🇷",
      results: 18,
      highlights: ["Sénégal agtech incubateur", "Côte d'Ivoire smart farming", "Burkina Faso precision agriculture"]
    },
    {
      query: "تمويل الذكاء الاصطناعي للشباب",
      language: "العربية",
      flag: "🇸🇦",
      results: 12,
      highlights: ["Morocco youth AI program", "Tunisia startup accelerator", "Egypt tech entrepreneurship"]
    },
    {
      query: "financiamento IA mulheres empreendedoras",
      language: "Português",
      flag: "🇵🇹",
      results: 15,
      highlights: ["Angola women in tech", "Mozambique female founders", "São Tomé digital innovation"]
    }
  ];

  const vectorCapabilities = [
    {
      icon: <Globe className="w-6 h-6" />,
      title: "Cross-Language Discovery",
      description: "Finds semantically similar opportunities across 6 African languages",
      color: "bg-blue-50 border-blue-200 text-blue-800"
    },
    {
      icon: <Brain className="w-6 h-6" />,
      title: "Contextual Understanding",
      description: "Understands regional contexts and cultural nuances in funding criteria",
      color: "bg-purple-50 border-purple-200 text-purple-800"
    },
    {
      icon: <Zap className="w-6 h-6" />,
      title: "Bias-Aware Ranking",
      description: "Automatically surfaces underrepresented regions and inclusion-focused opportunities",
      color: "bg-green-50 border-green-200 text-green-800"
    },
    {
      icon: <Languages className="w-6 h-6" />,
      title: "Semantic Similarity",
      description: "Connects related opportunities even with different terminologies",
      color: "bg-orange-50 border-orange-200 text-orange-800"
    }
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveExample((prev) => (prev + 1) % searchExamples.length);
    }, 4000);

    return () => clearInterval(interval);
  }, []);

  const handleSearch = () => {
    setIsSearching(true);
    setTimeout(() => setIsSearching(false), 2000);
  };

  return (
    <div className="bg-gradient-to-br from-gray-50 to-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-2xl font-bold mb-2">Semantic Search Intelligence</h3>
            <p className="text-blue-100">Vector-powered discovery across languages and contexts</p>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
            <span className="text-sm font-medium">AI Active</span>
          </div>
        </div>
      </div>

      <div className="p-6">
        {/* Interactive Search Demo */}
        <div className="mb-8">
          <div className="bg-white rounded-lg shadow-inner border-2 border-gray-100 p-6">
            <div className="flex items-center space-x-4 mb-4">
              <div className="flex-1 relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Search className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  type="text"
                  value={currentQuery || searchExamples[activeExample].query}
                  onChange={(e) => setCurrentQuery(e.target.value)}
                  placeholder="Try semantic search in any language..."
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 placeholder-gray-500"
                />
              </div>
              <button
                onClick={handleSearch}
                disabled={isSearching}
                className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white px-6 py-3 rounded-lg font-medium transition-colors flex items-center space-x-2"
              >
                {isSearching ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    <span>Searching...</span>
                  </>
                ) : (
                  <>
                    <Search className="w-4 h-4" />
                    <span>Search</span>
                  </>
                )}
              </button>
            </div>

            {/* Language Toggle */}
            <div className="flex items-center space-x-2 mb-4">
              <span className="text-sm font-medium text-gray-700">Language:</span>
              <div className="flex space-x-2">
                {searchExamples.map((example, index) => (
                  <button
                    key={index}
                    onClick={() => setActiveExample(index)}
                    className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                      activeExample === index
                        ? 'bg-blue-100 text-blue-800 border border-blue-300'
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    }`}
                  >
                    {example.flag} {example.language}
                  </button>
                ))}
              </div>
            </div>

            {/* Results Preview */}
            {isSearching ? (
              <div className="space-y-3">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="animate-pulse">
                    <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                    <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-700">
                    Found {searchExamples[activeExample].results} relevant opportunities
                  </span>
                  <span className="text-xs text-gray-500">Semantic similarity: 94%</span>
                </div>
                <div className="space-y-2">
                  {searchExamples[activeExample].highlights.map((highlight, index) => (
                    <div key={index} className="flex items-center space-x-2">
                      <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                      <span className="text-sm text-gray-700">{highlight}</span>
                      <span className="text-xs text-green-600 font-medium">98% match</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Vector Capabilities */}
        <div className="mb-8">
          <h4 className="text-lg font-semibold text-gray-900 mb-4">Vector Intelligence Capabilities</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {vectorCapabilities.map((capability, index) => (
              <div key={index} className={`border rounded-lg p-4 ${capability.color}`}>
                <div className="flex items-center space-x-3 mb-2">
                  {capability.icon}
                  <span className="font-medium">{capability.title}</span>
                </div>
                <p className="text-sm opacity-90">{capability.description}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Technical Architecture */}
        <div className="bg-gray-50 rounded-lg p-6">
          <h4 className="text-lg font-semibold text-gray-900 mb-4">🧠 How Vector Intelligence Works</h4>
          <div className="space-y-4">
            <div className="flex items-start space-x-4">
              <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                <span className="text-blue-600 font-bold text-sm">1</span>
              </div>
              <div>
                <h5 className="font-medium text-gray-900">Content Embedding</h5>
                <p className="text-sm text-gray-600">
                  Every opportunity is converted into a 1536-dimensional vector capturing semantic meaning
                </p>
              </div>
            </div>
            
            <div className="flex items-start space-x-4">
              <div className="flex-shrink-0 w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
                <span className="text-purple-600 font-bold text-sm">2</span>
              </div>
              <div>
                <h5 className="font-medium text-gray-900">Equity-Aware Indexing</h5>
                <p className="text-sm text-gray-600">
                  Metadata includes geographic bias signals, sectoral alignment, and inclusion indicators
                </p>
              </div>
            </div>
            
            <div className="flex items-start space-x-4">
              <div className="flex-shrink-0 w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                <span className="text-green-600 font-bold text-sm">3</span>
              </div>
              <div>
                <h5 className="font-medium text-gray-900">Similarity Search</h5>
                <p className="text-sm text-gray-600">
                  Cosine similarity finds related opportunities across languages and regions
                </p>
              </div>
            </div>
            
            <div className="flex items-start space-x-4">
              <div className="flex-shrink-0 w-8 h-8 bg-orange-100 rounded-full flex items-center justify-center">
                <span className="text-orange-600 font-bold text-sm">4</span>
              </div>
              <div>
                <h5 className="font-medium text-gray-900">Bias-Aware Ranking</h5>
                <p className="text-sm text-gray-600">
                  Results are re-ranked to surface underrepresented opportunities and promote equity
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Database Stats */}
        <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-blue-50 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-blue-600">1.2M+</div>
            <div className="text-sm text-blue-800">Vector Embeddings</div>
          </div>
          <div className="bg-purple-50 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-purple-600">6</div>
            <div className="text-sm text-purple-800">African Languages</div>
          </div>
          <div className="bg-green-50 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-green-600">94%</div>
            <div className="text-sm text-green-800">Semantic Accuracy</div>
          </div>
        </div>
      </div>
    </div>
  );
}