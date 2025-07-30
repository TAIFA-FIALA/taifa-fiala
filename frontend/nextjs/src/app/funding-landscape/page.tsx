import { TrendingUp, AlertTriangle, DollarSign, Target, BarChart3, Heart, Zap, ArrowUp, ArrowDown, Activity, BookOpen, ArrowRight } from 'lucide-react';
import React from 'react';
import { Metadata } from 'next';
import FundingCharts from './components/FundingCharts';
import InteractiveAfricaAIMap from '@/components/analytics/interactive-map';
import { getAllBlogPosts, BlogPost } from '@/lib/blog';

export const metadata: Metadata = {
  title: 'African AI Funding Landscape: The Two-Track Surge | TAIFA-FIALA',
  description: 'Explore Africa\'s AI funding ecosystem experiencing volatile VC investment alongside steady grants. Discover the twin engines financing Africa\'s transition from AI adoption to AI creation.',
  keywords: 'African AI funding, venture capital Africa, AI4D grants, African AI startups, technology funding Africa, responsible AI',
};

// Data structures based on the actual report


// Real data from the report
const fundingByCountryData = [
  { country: 'Tunisia', funding: 244, deals: 9, color: 'var(--color-site-slate)', share: '30.4%' },
  { country: 'Kenya', funding: 242, deals: 30, color: 'var(--color-site-gold)', share: '30.2%' },
  { country: 'South Africa', funding: 150, deals: 29, color: 'var(--color-site-purple)', share: '18.7%' },
  { country: 'Egypt', funding: 83, deals: 44, color: 'var(--color-site-brown)', share: '10.4%' },
  { country: 'Nigeria', funding: 45, deals: 32, color: 'var(--color-site-olive)', share: '5.6%' },
  { country: 'Others', funding: 39, deals: 15, color: 'var(--color-site-steel)', share: '4.7%' },
];

const sectorDistributionData = [
  { name: 'Fintech & AI-as-a-Service', value: 45, funding: 361, color: 'var(--color-site-slate)' },
  { name: 'Language-tech', value: 15, funding: 120, color: 'var(--color-site-gold)' },
  { name: 'Climate-agri AI', value: 12, funding: 96, color: 'var(--color-site-purple)' },
  { name: 'Healthcare', value: 8, funding: 64, color: 'var(--color-site-steel)' },
  { name: 'Other sectors', value: 20, funding: 162, color: 'var(--color-site-olive)' },
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
    <header className="relative overflow-hidden" style={{ background: 'linear-gradient(to bottom right, #1e293b, #334155, #475569)' }}>
      <div className="absolute inset-0 bg-slate-900/20"></div>
      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 text-center">
        <div className="inline-flex items-center px-4 py-2 bg-white/10 border border-white/30 rounded-full text-sm font-medium text-white mb-4 animate-fadeInUp backdrop-blur-sm">
          <Activity className="h-4 w-4 mr-2" />
          Data-Driven Rapid Assessment • 2020-2025
        </div>
        <h1 className="text-5xl md:text-7xl font-bold mb-6 animate-fadeInUp leading-tight" style={{ animationDelay: '0.1s', color: '#ffffff' }}>
          Funding the African
          <span className="block" style={{ color: 'var(--color-site-gold)' }}>AI Surge</span>
        </h1>
        <p className="text-xl md:text-2xl text-slate-200 mb-12 max-w-4xl mx-auto animate-fadeInUp leading-relaxed" style={{ animationDelay: '0.2s' }}>
          Africa&apos;s AI ecosystem experiences a <strong>two-track funding dynamic</strong>: volatile VC investment rebounds after 2023 trough, while research grants rise steadily—together forming the twin engines financing Africa&apos;s transition from AI adoption to AI creation.
        </p>
        
        {/* Key insights preview */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-6xl mx-auto mb-8 animate-fadeInUp" style={{ animationDelay: '0.3s' }}>
          <div className="bg-white/10 backdrop-blur-sm p-6 rounded-2xl border border-white/20 hover:bg-white/20 transition-all duration-300">
            <div className="text-3xl md:text-4xl font-bold text-amber-400 mb-2">$803M</div>
            <div className="text-white text-sm font-medium mb-1">Cumulative AI Funding</div>
            <div className="text-white/70 text-xs">159 startups by mid-2025</div>
          </div>
          <div className="bg-white/10 backdrop-blur-sm p-6 rounded-2xl border border-white/20 hover:bg-white/20 transition-all duration-300">
            <div className="text-3xl md:text-4xl font-bold text-white mb-2">67%</div>
            <div className="text-white text-sm font-medium mb-1">Big Four Concentration</div>
            <div className="text-white/70 text-xs">Nigeria, South Africa, Kenya, Egypt</div>
          </div>
          <div className="bg-white/10 backdrop-blur-sm p-6 rounded-2xl border border-white/20 hover:bg-white/20 transition-all duration-300">
            <div className="text-3xl md:text-4xl font-bold" style={{ color: 'var(--color-site-terracotta)' }}>$755M</div>
            <div className="text-white text-sm font-medium mb-1">Venture Debt 2024</div>
            <div className="text-white/70 text-xs">3× higher than 2022 levels</div>
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
        colorClass: "taifa-secondary",
        borderClass: "border-taifa-secondary",
        bgClass: "bg-taifa-secondary/5",
        textClass: "text-taifa-secondary"
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
        colorClass: "taifa-accent",
        borderClass: "border-taifa-accent",
        bgClass: "bg-taifa-accent/5",
        textClass: "text-taifa-accent"
      }
    ];

    return (
      <section className="py-20 bg-slate-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <div className="inline-flex items-center px-4 py-2 bg-taifa-primary/10 border border-taifa-primary/20 rounded-full text-sm font-medium text-taifa-primary mb-6">
              <BarChart3 className="h-4 w-4 mr-2" />
              Twin Engines Analysis
            </div>
            <h2 className="text-4xl md:text-5xl font-bold text-taifa-primary mb-6 leading-tight">
              The Two-Track Funding Dynamic
            </h2>
            <p className="text-xl text-slate-600 max-w-4xl mx-auto leading-relaxed">
              Africa&apos;s AI funding operates on parallel tracks with distinct patterns, risks, and opportunities that together shape the continent&apos;s AI trajectory.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-12">
            {tracks.map((track, index) => (
              <div key={index} className={`p-10 rounded-3xl border-2 ${track.borderClass} ${track.bgClass} hover:shadow-2xl transition-all duration-500 hover:-translate-y-1`}>
                <div className="flex items-start justify-between mb-8">
                  <div>
                    <div className="flex items-center mb-4">
                      <div className="p-3 bg-white rounded-xl shadow-md mr-4">
                        {track.icon}
                      </div>
                      <div>
                        <h3 className="text-2xl font-bold text-taifa-primary">{track.title}</h3>
                        <p className={`${track.textClass} font-medium`}>{track.subtitle}</p>
                      </div>
                    </div>
                    <p className="text-slate-600 leading-relaxed mb-8">{track.description}</p>
                  </div>
                </div>
                
                <div className="grid grid-cols-3 gap-4">
                  {track.metrics.map((metric, idx) => (
                    <div key={idx} className="text-center p-4 bg-white/80 rounded-xl border border-slate-200">
                      <div className="text-2xl font-bold text-taifa-primary mb-1">{metric.value}</div>
                      <div className="text-xs text-slate-600 font-medium">{metric.label}</div>
                      <div className="flex justify-center mt-2">
                        {metric.trend === 'up' && <ArrowUp className="h-4 w-4 text-green-600" />}
                        {metric.trend === 'down' && <ArrowDown className="h-4 w-4 text-red-600" />}
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
        colorClass: "taifa-accent",
        borderClass: "border-taifa-accent",
        bgClass: "bg-taifa-accent/5",
        textClass: "text-taifa-accent"
      },
      {
        title: "Infrastructure Gap",
        value: "<0.1%",
        description: "Africa hosts <0.1% of global GPU capacity yet will need 30× today's compute by 2030 to train home-grown LLMs.",
        severity: "high" as const,
        colorClass: "taifa-secondary",
        borderClass: "border-taifa-secondary",
        bgClass: "bg-taifa-secondary/5",
        textClass: "text-taifa-secondary"
      },
      {
        title: "Gender Disparity",
        value: "≈2%",
        description: "Female-led AI start-ups captured only ≈2% of VC dollars in 2024 despite targeted schemes such as AI4D scholarships.",
        severity: "high" as const,
        colorClass: "taifa-accent",
        borderClass: "border-taifa-accent",
        bgClass: "bg-taifa-accent/5",
        textClass: "text-taifa-accent"
      }
    ];

    return (
      <section className="py-20 bg-slate-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <div className="inline-flex items-center px-4 py-2 bg-taifa-accent/10 border border-taifa-accent/20 rounded-full text-sm font-medium text-taifa-accent mb-6">
              <AlertTriangle className="h-4 w-4 mr-2" />
              Equity & Infrastructure Concerns
            </div>
            <h2 className="text-4xl md:text-5xl font-bold text-taifa-primary mb-6 leading-tight">
              Critical Gaps Persist
            </h2>
            <p className="text-xl text-slate-600 max-w-4xl mx-auto leading-relaxed">
              Despite overall growth, structural inequalities threaten Africa&apos;s AI potential, requiring targeted interventions to ensure inclusive development.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 mb-16">
            {alertCards.map((card, index) => (
              <div key={index} className={`p-8 rounded-2xl border-2 ${card.borderClass} ${card.bgClass} hover:shadow-xl transition-all duration-300 hover:-translate-y-1`}>
                <div className="flex items-start justify-between mb-6">
                  <div>
                    <h4 className="text-xl font-bold text-site-slate mb-2">{card.title}</h4>
                    <div className={`text-4xl font-bold ${card.textClass} mb-4`}>{card.value}</div>
                  </div>
                  <AlertTriangle className={`h-8 w-8 ${card.textClass}/60`} />
                </div>
                <p className="text-slate-600 leading-relaxed">{card.description}</p>
              </div>
            ))}
          </div>

          {/* Country leadership board */}
          <div className="bg-white/80 backdrop-blur-sm rounded-3xl p-12 shadow-xl border border-slate-200">
            <h3 className="text-3xl font-bold text-site-slate mb-8 text-center">Funding Leaders & Concentration</h3>
            <div className="grid md:grid-cols-2 gap-12">
              <div>
                <h4 className="text-xl font-semibold text-site-slate mb-6">Top Countries by Total Funding</h4>
                <div className="space-y-4">
                  {fundingByCountryData.slice(0, 4).map((country, index) => (
                    <div key={index} className="flex items-center justify-between p-4 bg-slate-50/50 rounded-xl border border-slate-200 hover:bg-slate-50 transition-colors">
                      <div className="flex items-center">
                        <div className="w-8 h-8 bg-site-slate/10 rounded-full flex items-center justify-center mr-4 border border-site-slate/20">
                          <span className="text-sm font-bold text-site-slate">#{index + 1}</span>
                        </div>
                        <div>
                          <span className="font-semibold text-site-slate">{country.country}</span>
                          <div className="text-sm text-slate-600">{country.deals} startups</div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-xl font-bold text-slate-600">${country.funding}M</div>
                        <div className="text-sm text-slate-600">{country.share}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              
              <div>
                <h4 className="text-xl font-semibold text-site-slate mb-6">Sectoral Patterns</h4>
                <div className="space-y-4">
                  {sectorDistributionData.slice(0, 4).map((sector, index) => (
                    <div key={index} className="flex justify-between items-center p-4 bg-slate-50/50 rounded-xl border border-slate-200">
                      <div>
                        <span className="font-medium text-site-slate">{sector.name}</span>
                        <div className="text-sm text-slate-600">${sector.funding}M funding</div>
                      </div>
                      <span className="text-xl font-bold text-site-gold">{sector.value}%</span>
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

  // Blog posts section featuring founder insights
  BlogPostsSection: () => {
    // Get blog posts from MDX files
    const blogPosts: BlogPost[] = getAllBlogPosts().slice(0, 4); // Show latest 4 posts

    return (
      <section className="py-20 bg-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <div className="inline-flex items-center px-4 py-2 bg-taifa-primary/10 border border-taifa-primary/20 rounded-full text-sm font-medium text-taifa-primary mb-6">
              <BookOpen className="h-4 w-4 mr-2" />
              Founder Insights
            </div>
            <h2 className="text-4xl md:text-5xl font-bold text-taifa-primary mb-6 leading-tight">
              Thoughts on African AI
            </h2>
            <p className="text-xl text-slate-600 max-w-4xl mx-auto leading-relaxed">
              Perspectives from the TAIFA-FIALA team on the evolving landscape of artificial intelligence in Africa, from funding dynamics to technical challenges and opportunities ahead.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8">
            {blogPosts.map((post, index) => (
              <article key={index} className="bg-white/80 backdrop-blur-sm p-8 rounded-2xl border border-slate-200 hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
                <div className="flex items-start justify-between mb-6">
                  <span className={`px-3 py-1 rounded-full text-xs font-medium border ${post.bgClass} ${post.borderClass} ${post.textClass}`}>
                    {post.category}
                  </span>
                  <span className="text-sm text-slate-500">{post.readTime}</span>
                </div>
                
                <h3 className="text-xl font-bold text-site-slate mb-4 leading-tight">
                  <a href={`/blog/${post.slug}`} className="hover:text-taifa-accent transition-colors duration-200">
                    {post.title}
                  </a>
                </h3>
                
                <p className="text-slate-600 leading-relaxed mb-6">
                  {post.excerpt}
                </p>
                
                <div className="flex items-center justify-between pt-4 border-t border-slate-200">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-taifa-primary/10 rounded-full flex items-center justify-center">
                      <span className="text-xs font-medium text-taifa-primary">
                        {post.author.split(' ').map(n => n[0]).join('')}
                      </span>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-slate-700">{post.author}</p>
                      <p className="text-xs text-slate-500">{post.date}</p>
                    </div>
                  </div>
                  
                  <a 
                    href={`/blog/${post.slug}`} 
                    className="text-sm font-medium text-taifa-accent hover:text-taifa-primary transition-colors duration-200 flex items-center space-x-1"
                  >
                    <span>Read more</span>
                    <ArrowRight className="h-3 w-3" />
                  </a>
                </div>
              </article>
            ))}
          </div>
        </div>
      </section>
    );
  },

  // Key takeaways and conclusion
  ConclusionSection: () => (
    <section className="py-20 bg-slate-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white/95 backdrop-blur-sm rounded-3xl p-12 shadow-2xl border border-slate-200">
          <div className="text-center mb-12">
            <h2 className="text-4xl md:text-5xl font-bold text-taifa-primary mb-6 leading-tight">
              Key Takeaways
            </h2>
            <p className="text-xl text-slate-600 max-w-3xl mx-auto leading-relaxed">
              Funding for African AI is no longer confined to cyclical VC pulses—it is buttressed by long-horizon grants and strategic infrastructure investments.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 mb-12">
            <div className="text-center p-8 bg-taifa-accent/5 rounded-2xl border border-taifa-accent/20">
              <div className="w-16 h-16 bg-taifa-accent/10 rounded-full flex items-center justify-center mx-auto mb-6 border border-taifa-accent/30">
                <DollarSign className="h-8 w-8 text-taifa-accent" />
              </div>
              <h4 className="text-xl font-bold text-taifa-primary mb-4">Twin-Engine Growth</h4>
              <p className="text-slate-600 leading-relaxed">VC volatility balanced by steady grant funding creates resilient ecosystem foundation.</p>
            </div>

            <div className="text-center p-8 bg-taifa-secondary/5 rounded-2xl border border-taifa-secondary/20">
              <div className="w-16 h-16 bg-taifa-secondary/10 rounded-full flex items-center justify-center mx-auto mb-6 border border-taifa-secondary/30">
                <AlertTriangle className="h-8 w-8 text-taifa-secondary" />
              </div>
              <h4 className="text-xl font-bold text-taifa-primary mb-4">Critical Gaps</h4>
              <p className="text-slate-600 leading-relaxed">Geographic concentration and infrastructure deficits require urgent policy intervention.</p>
            </div>

            <div className="text-center p-8 bg-taifa-primary/5 rounded-2xl border border-taifa-primary/20">
              <div className="w-16 h-16 bg-taifa-primary/10 rounded-full flex items-center justify-center mx-auto mb-6 border border-taifa-primary/30">
                <Target className="h-8 w-8 text-taifa-primary" />
              </div>
              <h4 className="text-xl font-bold text-taifa-primary mb-4">Strategic Window</h4>
              <p className="text-slate-600 leading-relaxed">2025-2027 represents crucial period for Africa&apos;s AI creator versus consumer trajectory.</p>
            </div>
          </div>

          <div className="text-center">
            <p className="text-lg text-taifa-primary font-medium italic">
              &quot;Bridging the compute-capacity gap and embedding gender-inclusive policies will decide whether the continent remains a consumer—or becomes a creator—of frontier AI technologies.&quot;
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
    'var(--color-taifa-primary)', 
    'var(--color-taifa-secondary)', 
    'var(--color-taifa-accent)', 
    'var(--color-taifa-orange)', 
    'var(--color-taifa-yellow)', 
    'var(--color-taifa-red)'
  ];

  return (
    <div className="min-h-screen bg-slate-50">
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
            <p className="text-xl text-slate-600 max-w-3xl mx-auto">
              Interactive visualizations revealing the complex dynamics shaping Africa&apos;s AI investment landscape
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
      <Components.BlogPostsSection />
      <Components.ConclusionSection />
     
    </div>
  );
}