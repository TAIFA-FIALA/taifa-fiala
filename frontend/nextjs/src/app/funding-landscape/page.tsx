import { TrendingUp, AlertTriangle, DollarSign, Briefcase, Target, BarChart3, PieChart, MapPin, Globe, Users, Shield, Heart, Calendar, Zap, ArrowUp, ArrowDown, Activity } from 'lucide-react';
import React from 'react';
import { Metadata } from 'next';
import FundingCharts from './components/FundingCharts';
import InteractiveAfricaAIMap from '@/components/analytics/interactive-map';

export const metadata: Metadata = {
  title: 'African AI Funding Landscape: The Two-Track Surge | TAIFA-FIALA',
  description: 'Explore Africa\'s AI funding ecosystem experiencing volatile VC investment alongside steady grants. Discover the twin engines financing Africa\'s transition from AI adoption to AI creation.',
  keywords: 'African AI funding, venture capital Africa, AI4D grants, African AI startups, technology funding Africa, responsible AI',
};

// Data structures based on the actual report
interface FundingMetric {
  value: string;
  label: string;
  icon: React.ReactNode;
  trend?: 'up' | 'down' | 'neutral';
  trendValue?: string;
  color: string;
  description?: string;
}

interface StoryCard {
  title: string;
  subtitle: string;
  value: string;
  description: string;
  icon: React.ReactNode;
  color: string;
  trend?: string;
}

interface FundingStream {
  name: string;
  amount: string;
  trend: string;
  implication: string;
  strategy: string;
  color: string;
  icon: React.ReactNode;
}

// Real data from the report
const fundingByCountryData = [
  { country: 'Tunisia', funding: 244, deals: 9, color: 'var(--taifa-primary)', share: '30.4%' },
  { country: 'Kenya', funding: 242, deals: 30, color: 'var(--taifa-secondary)', share: '30.2%' },
  { country: 'South Africa', funding: 150, deals: 29, color: 'var(--taifa-accent)', share: '18.7%' },
  { country: 'Egypt', funding: 83, deals: 44, color: 'var(--taifa-orange)', share: '10.4%' },
  { country: 'Nigeria', funding: 45, deals: 32, color: 'var(--taifa-olive)', share: '5.6%' },
  { country: 'Others', funding: 39, deals: 15, color: 'var(--taifa-red)', share: '4.7%' },
];

const sectorDistributionData = [
  { name: 'Fintech & AI-as-a-Service', value: 45, funding: 361, color: 'var(--taifa-primary)' },
  { name: 'Language-tech', value: 15, funding: 120, color: 'var(--taifa-secondary)' },
  { name: 'Climate-agri AI', value: 12, funding: 96, color: 'var(--taifa-accent)' },
  { name: 'Healthcare', value: 8, funding: 64, color: 'var(--taifa-red)' },
  { name: 'Other sectors', value: 20, funding: 162, color: 'var(--taifa-olive)' },
];

// Chart-compatible data for the FundingCharts component
const chartSectorData = [
  { name: 'Fintech & AI-as-a-Service', value: 45, funding: 361 },
  { name: 'Language-tech', value: 15, funding: 120 },
  { name: 'Climate-agri AI', value: 12, funding: 96 },
  { name: 'Healthcare', value: 8, funding: 64 },
  { name: 'Other sectors', value: 20, funding: 162 },
];

const fundingTimelineData = [
  { year: '2020', amount: 34.9, type: 'VC Peak Year' },
  { year: '2022', amount: 167.7, type: 'Record High' },
  { year: '2023', amount: 17.9, type: 'Market Trough' },
  { year: '2024', amount: 108.0, type: 'Strong Recovery' },
];

const Components = {
  // Hero section with key narrative
  HeroSection: () => (
    <header className="bg-gradient-to-br from-taifa-primary via-taifa-secondary/20 to-taifa-accent/10 relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-r from-taifa-primary/90 to-taifa-primary/70"></div>
      <div className="relative max-w-7xl mx-auto py-24 px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <div className="inline-flex items-center px-6 py-3 bg-taifa-white/20 border border-taifa-white/30 rounded-full text-sm font-medium text-taifa-white mb-8 animate-fadeInUp backdrop-blur-sm">
            <Activity className="h-4 w-4 mr-2" />
            Data-Driven Rapid Assessment • 2020-2025
          </div>
          <h1 className="text-5xl md:text-7xl font-bold text-taifa-white mb-8 animate-fadeInUp leading-tight" style={{ animationDelay: '0.1s' }}>
            Funding the African
            <span className="block text-taifa-orange">AI Surge</span>
          </h1>
          <p className="text-xl md:text-2xl text-taifa-orange/90 mb-12 max-w-4xl mx-auto animate-fadeInUp leading-relaxed" style={{ animationDelay: '0.2s' }}>
            Africa's AI ecosystem experiences a <strong>two-track funding dynamic</strong>: volatile VC investment rebounds after 2023 trough, while research grants rise steadily—together forming the twin engines financing Africa's transition from AI adoption to AI creation.
          </p>
          
          {/* Key insights preview */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto animate-fadeInUp" style={{ animationDelay: '0.3s' }}>
            <div className="bg-taifa-white/15 backdrop-blur-sm p-8 rounded-2xl border border-taifa-white/20 hover:bg-taifa-white/20 transition-all duration-300">
              <div className="text-4xl font-bold text-taifa-white mb-3">$803M</div>
              <div className="text-taifa-orange/90 text-sm font-medium mb-2">Cumulative AI Funding</div>
              <div className="text-taifa-white/80 text-xs">159 startups by mid-2025</div>
            </div>
            <div className="bg-taifa-white/15 backdrop-blur-sm p-8 rounded-2xl border border-taifa-white/20 hover:bg-taifa-white/20 transition-all duration-300">
              <div className="text-4xl font-bold text-taifa-white mb-3">67%</div>
              <div className="text-taifa-orange/90 text-sm font-medium mb-2">Big Four Concentration</div>
              <div className="text-taifa-white/80 text-xs">Nigeria, South Africa, Kenya, Egypt</div>
            </div>
            <div className="bg-taifa-white/15 backdrop-blur-sm p-8 rounded-2xl border border-taifa-white/20 hover:bg-taifa-white/20 transition-all duration-300">
              <div className="text-4xl font-bold text-taifa-white mb-3">$755M</div>
              <div className="text-taifa-orange/90 text-sm font-medium mb-2">Venture Debt 2024</div>
              <div className="text-taifa-white/80 text-xs">3× higher than 2022 levels</div>
            </div>
          </div>
        </div>
      </div>
    </header>
  ),

  // The two-track story
  TwoTrackNarrative: () => {
    const tracks = [
      {
        title: "Venture Capital Track",
        subtitle: "Volatile but Rebounding",
        description: "Private investment peaked at $167.7M in 2022, crashed to $17.9M in 2023, then rallied to ≈$108M in 2024 as global capital tightened.",
        metrics: [
          { label: "2022 Peak", value: "$167.7M", trend: "peak" },
          { label: "2023 Trough", value: "$17.9M", trend: "down" },
          { label: "2024 Rally", value: "≈$108M", trend: "up" },
        ],
        icon: <TrendingUp className="h-8 w-8" />,
        color: "border-taifa-secondary bg-taifa-secondary/5"
      },
      {
        title: "Grants & Development Track", 
        subtitle: "Steady Upward Trajectory",
        description: "Led by multilateral donors and Big Tech philanthropy, research grants climb steadily with major program expansions from AI4D and corporate commitments.",
        metrics: [
          { label: "AI4D Phase 2", value: "$70M", trend: "up" },
          { label: "Google Package", value: "$37M", trend: "up" },
          { label: "Microsoft SA", value: "$298M", trend: "up" },
        ],
        icon: <Heart className="h-8 w-8" />,
        color: "border-taifa-accent bg-taifa-accent/5"
      }
    ];

    return (
      <section className="py-20 bg-gradient-to-br from-taifa-light/50 to-taifa-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <div className="inline-flex items-center px-4 py-2 bg-taifa-primary/10 border border-taifa-primary/20 rounded-full text-sm font-medium text-taifa-primary mb-6">
              <BarChart3 className="h-4 w-4 mr-2" />
              Twin Engines Analysis
            </div>
            <h2 className="text-4xl md:text-5xl font-bold text-taifa-primary mb-6 leading-tight">
              The Two-Track Funding Dynamic
            </h2>
            <p className="text-xl text-taifa-muted max-w-4xl mx-auto leading-relaxed">
              Africa's AI funding operates on parallel tracks with distinct patterns, risks, and opportunities that together shape the continent's AI trajectory.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-12">
            {tracks.map((track, index) => (
              <div key={index} className={`p-10 rounded-3xl border-2 ${track.color} hover:shadow-2xl transition-all duration-500 hover:-translate-y-1`}>
                <div className="flex items-start justify-between mb-8">
                  <div>
                    <div className="flex items-center mb-4">
                      <div className="p-3 bg-taifa-white rounded-xl shadow-md mr-4">
                        {track.icon}
                      </div>
                      <div>
                        <h3 className="text-2xl font-bold text-taifa-primary">{track.title}</h3>
                        <p className="text-taifa-secondary font-medium">{track.subtitle}</p>
                      </div>
                    </div>
                    <p className="text-taifa-muted leading-relaxed mb-8">{track.description}</p>
                  </div>
                </div>
                
                <div className="grid grid-cols-3 gap-4">
                  {track.metrics.map((metric, idx) => (
                    <div key={idx} className="text-center p-4 bg-taifa-white/80 rounded-xl border border-taifa-border">
                      <div className="text-2xl font-bold text-taifa-primary mb-1">{metric.value}</div>
                      <div className="text-xs text-taifa-muted font-medium">{metric.label}</div>
                      <div className="flex justify-center mt-2">
                        {metric.trend === 'up' && <ArrowUp className="h-4 w-4 text-taifa-accent" />}
                        {metric.trend === 'down' && <ArrowDown className="h-4 w-4 text-taifa-red" />}
                        {metric.trend === 'peak' && <Zap className="h-4 w-4 text-taifa-secondary" />}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
    );
  },

  // Geographic concentration crisis
  GeographicCrisis: () => {
    const alertCards = [
      {
        title: "Big Four Dominance",
        value: "67%",
        description: "Nigeria, South Africa, Kenya & Egypt absorb 67% of equity AI funding, though their share is declining as North-African deal value surges 61% YoY.",
        severity: "high" as const,
        color: "border-taifa-red bg-taifa-red/5"
      },
      {
        title: "Infrastructure Gap",
        value: "<0.1%",
        description: "Africa hosts <0.1% of global GPU capacity yet will need 30× today's compute by 2030 to train home-grown LLMs.",
        severity: "high" as const,
        color: "border-taifa-orange bg-taifa-orange/5"
      },
      {
        title: "Gender Disparity",
        value: "≈2%",
        description: "Female-led AI start-ups captured only ≈2% of VC dollars in 2024 despite targeted schemes such as AI4D scholarships.",
        severity: "high" as const,
        color: "border-taifa-red bg-taifa-red/5"
      }
    ];

    return (
      <section className="py-20 bg-gradient-to-br from-taifa-red/5 to-taifa-orange/5">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <div className="inline-flex items-center px-4 py-2 bg-taifa-red/10 border border-taifa-red/20 rounded-full text-sm font-medium text-taifa-red mb-6">
              <AlertTriangle className="h-4 w-4 mr-2" />
              Equity & Infrastructure Concerns
            </div>
            <h2 className="text-4xl md:text-5xl font-bold text-taifa-primary mb-6 leading-tight">
              Critical Gaps Persist
            </h2>
            <p className="text-xl text-taifa-muted max-w-4xl mx-auto leading-relaxed">
              Despite overall growth, structural inequalities threaten Africa's AI potential, requiring targeted interventions to ensure inclusive development.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 mb-16">
            {alertCards.map((card, index) => (
              <div key={index} className={`p-8 rounded-2xl border-2 ${card.color} hover:shadow-xl transition-all duration-300 hover:-translate-y-1`}>
                <div className="flex items-start justify-between mb-6">
                  <div>
                    <h4 className="text-xl font-bold text-taifa-primary mb-2">{card.title}</h4>
                    <div className="text-4xl font-bold text-taifa-red mb-4">{card.value}</div>
                  </div>
                  <AlertTriangle className="h-8 w-8 text-taifa-red/60" />
                </div>
                <p className="text-taifa-muted leading-relaxed">{card.description}</p>
              </div>
            ))}
          </div>

          {/* Country leadership board */}
          <div className="bg-taifa-white/80 backdrop-blur-sm rounded-3xl p-12 shadow-xl border border-taifa-border">
            <h3 className="text-3xl font-bold text-taifa-primary mb-8 text-center">Funding Leaders & Concentration</h3>
            <div className="grid md:grid-cols-2 gap-12">
              <div>
                <h4 className="text-xl font-semibold text-taifa-primary mb-6">Top Countries by Total Funding</h4>
                <div className="space-y-4">
                  {fundingByCountryData.slice(0, 4).map((country, index) => (
                    <div key={index} className="flex items-center justify-between p-4 bg-taifa-light/50 rounded-xl border border-taifa-border hover:bg-taifa-light transition-colors">
                      <div className="flex items-center">
                        <div className="w-8 h-8 bg-taifa-primary/10 rounded-full flex items-center justify-center mr-4 border border-taifa-primary/20">
                          <span className="text-sm font-bold text-taifa-primary">#{index + 1}</span>
                        </div>
                        <div>
                          <span className="font-semibold text-taifa-primary">{country.country}</span>
                          <div className="text-sm text-taifa-muted">{country.deals} startups</div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-xl font-bold text-taifa-accent">${country.funding}M</div>
                        <div className="text-sm text-taifa-muted">{country.share}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              
              <div>
                <h4 className="text-xl font-semibold text-taifa-primary mb-6">Sectoral Patterns</h4>
                <div className="space-y-4">
                  {sectorDistributionData.slice(0, 4).map((sector, index) => (
                    <div key={index} className="flex justify-between items-center p-4 bg-taifa-light/50 rounded-xl border border-taifa-border">
                      <div>
                        <span className="font-medium text-taifa-primary">{sector.name}</span>
                        <div className="text-sm text-taifa-muted">${sector.funding}M funding</div>
                      </div>
                      <span className="text-xl font-bold text-taifa-secondary">{sector.value}%</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    );
  },

  // Future outlook section
  OutlookSection: () => {
    const outlookItems = [
      {
        title: "Compute Consortiums",
        description: "Pooled GPU clusters backed by AI4D and Smart Africa to cut inference costs 40-60% for local SMEs",
        timeline: "2025-2027",
        icon: <Shield className="h-6 w-6" />,
        color: "bg-taifa-accent/10 border-taifa-accent/30 text-taifa-accent"
      },
      {
        title: "Debt-Equity Hybrids", 
        description: "Venture-debt funds expand beyond fintech into model-hosting start-ups as revenue visibility improves",
        timeline: "2025-2026",
        icon: <Briefcase className="h-6 w-6" />,
        color: "bg-taifa-secondary/10 border-taifa-secondary/30 text-taifa-secondary"
      },
      {
        title: "Regulatory Premium",
        description: "Jurisdictions implementing Responsible-AI Index findings attract higher-quality capital at lower risk premiums",
        timeline: "2025-2027",
        icon: <Target className="h-6 w-6" />,
        color: "bg-taifa-primary/10 border-taifa-primary/30 text-taifa-primary"
      },
      {
        title: "LLM Localization",
        description: "African-language LLM checkpoints reach <2B parameters—small enough for on-device ag-extension and health chatbots",
        timeline: "2025-2027",
        icon: <Globe className="h-6 w-6" />,
        color: "bg-taifa-olive/10 border-taifa-olive/30 text-taifa-olive"
      }
    ];

    return (
      <section className="py-20 bg-gradient-to-br from-taifa-primary/5 to-taifa-accent/5">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <div className="inline-flex items-center px-4 py-2 bg-taifa-primary/10 border border-taifa-primary/20 rounded-full text-sm font-medium text-taifa-primary mb-6">
              <Calendar className="h-4 w-4 mr-2" />
              Strategic Outlook
            </div>
            <h2 className="text-4xl md:text-5xl font-bold text-taifa-primary mb-6 leading-tight">
              Outlook 2025-2027
            </h2>
            <p className="text-xl text-taifa-muted max-w-4xl mx-auto leading-relaxed">
              Four key trends will shape Africa's AI funding ecosystem, bridging the compute-capacity gap and determining whether the continent becomes a creator—not just consumer—of frontier AI technologies.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8">
            {outlookItems.map((item, index) => (
              <div key={index} className="bg-taifa-white/80 backdrop-blur-sm p-8 rounded-2xl border border-taifa-border hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
                <div className="flex items-start justify-between mb-6">
                  <div className={`p-3 rounded-xl border ${item.color}`}>
                    {item.icon}
                  </div>
                  <span className="text-sm font-medium text-taifa-muted bg-taifa-light/50 px-3 py-1 rounded-full">{item.timeline}</span>
                </div>
                <h4 className="text-xl font-bold text-taifa-primary mb-4">{item.title}</h4>
                <p className="text-taifa-muted leading-relaxed">{item.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>
    );
  },

  // Key takeaways and conclusion
  ConclusionSection: () => (
    <section className="py-20 bg-gradient-to-br from-taifa-primary via-taifa-secondary/10 to-taifa-accent/10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-taifa-white/95 backdrop-blur-sm rounded-3xl p-12 shadow-2xl border border-taifa-border">
          <div className="text-center mb-12">
            <h2 className="text-4xl md:text-5xl font-bold text-taifa-primary mb-6 leading-tight">
              Key Takeaways
            </h2>
            <p className="text-xl text-taifa-muted max-w-3xl mx-auto leading-relaxed">
              Funding for African AI is no longer confined to cyclical VC pulses—it is buttressed by long-horizon grants and strategic infrastructure investments.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 mb-12">
            <div className="text-center p-8 bg-taifa-accent/5 rounded-2xl border border-taifa-accent/20">
              <div className="w-16 h-16 bg-taifa-accent/10 rounded-full flex items-center justify-center mx-auto mb-6 border border-taifa-accent/30">
                <DollarSign className="h-8 w-8 text-taifa-accent" />
              </div>
              <h4 className="text-xl font-bold text-taifa-primary mb-4">Twin-Engine Growth</h4>
              <p className="text-taifa-muted leading-relaxed">VC volatility balanced by steady grant funding creates resilient ecosystem foundation.</p>
            </div>

            <div className="text-center p-8 bg-taifa-red/5 rounded-2xl border border-taifa-red/20">
              <div className="w-16 h-16 bg-taifa-red/10 rounded-full flex items-center justify-center mx-auto mb-6 border border-taifa-red/30">
                <AlertTriangle className="h-8 w-8 text-taifa-red" />
              </div>
              <h4 className="text-xl font-bold text-taifa-primary mb-4">Critical Gaps</h4>
              <p className="text-taifa-muted leading-relaxed">Geographic concentration and infrastructure deficits require urgent policy intervention.</p>
            </div>

            <div className="text-center p-8 bg-taifa-secondary/5 rounded-2xl border border-taifa-secondary/20">
              <div className="w-16 h-16 bg-taifa-secondary/10 rounded-full flex items-center justify-center mx-auto mb-6 border border-taifa-secondary/30">
                <Target className="h-8 w-8 text-taifa-secondary" />
              </div>
              <h4 className="text-xl font-bold text-taifa-primary mb-4">Strategic Window</h4>
              <p className="text-taifa-muted leading-relaxed">2025-2027 represents crucial period for Africa's AI creator versus consumer trajectory.</p>
            </div>
          </div>

          <div className="text-center">
            <p className="text-lg text-taifa-primary font-medium italic">
              "Bridging the compute-capacity gap and embedding gender-inclusive policies will decide whether the continent remains a consumer—or becomes a creator—of frontier AI technologies."
            </p>
          </div>
        </div>
      </div>
    </section>
  )
};

export default function FundingLandscapePage() {
  // Chart colors using TAIFA theme
  const COLORS = [
    'var(--taifa-primary)', 
    'var(--taifa-secondary)', 
    'var(--taifa-accent)', 
    'var(--taifa-orange)', 
    'var(--taifa-olive)', 
    'var(--taifa-red)'
  ];

  return (
    <div className="min-h-screen bg-taifa-white">
      <Components.HeroSection />
      <Components.TwoTrackNarrative />
      <Components.GeographicCrisis />
      
      {/* Interactive Data Visualizations */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <div className="inline-flex items-center px-4 py-2 bg-taifa-primary/10 border border-taifa-primary/20 rounded-full text-sm font-medium text-taifa-primary mb-6">
              <BarChart3 className="h-4 w-4 mr-2" />
              Data Deep Dive
            </div>
            <h2 className="text-4xl font-bold text-taifa-primary mb-4">Funding Patterns Analysis</h2>
            <p className="text-xl text-taifa-muted max-w-3xl mx-auto">
              Interactive visualizations revealing the complex dynamics shaping Africa's AI investment landscape
            </p>
          </div>

          <FundingCharts 
            fundingByCountryData={fundingByCountryData}
            sectorDistributionData={chartSectorData}
            fundingTimelineData={fundingTimelineData}
            COLORS={COLORS}
          />
        </div>
      </section>
      <InteractiveAfricaAIMap />
      <Components.OutlookSection />
      <Components.ConclusionSection />
     
    </div>
  );
}