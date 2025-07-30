import React from 'react';
import { Database, Search, Globe, Zap, Users, TrendingUp, CheckCircle, ArrowRight, Code, Server, Monitor, Shield } from 'lucide-react';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Technical Methodology & Architecture | TAIFA-FIALA',
  description: 'Comprehensive technical documentation of TAIFA-FIALA\'s three-stage AI funding intelligence pipeline: RSS aggregation, intelligent scraping, and targeted enrichment for African AI funding opportunities.',
  keywords: ['AI funding', 'African technology', 'data pipeline', 'funding intelligence', 'methodology', 'technical architecture'],
};

export default function MethodologyPage() {
  const stages = [
    {
      number: "01",
      title: "RSS Aggregate Polling",
      subtitle: "Volume",
      description: "Custom-curated RSS feeds from 200+ funding organizations across Africa and internationally",
      metrics: ["85-90% capture rate", "500-800 daily opportunities", "15-30 min polling"],
      icon: <Globe/>,
      colorClass: "slate-600",
      borderClass: "border-l-slate-600",
      bgClass: "bg-slate-600/10",
      textClass: "text-slate-600"
    },
    {
      number: "02", 
      title: "Crawl4AI Intelligence",
      subtitle: "Depth",
      description: "Intelligent web scraping to retrieve comprehensive funding details from source websites",
      metrics: ["Smart navigation", "Multi-format support", "95% uptime"],
      icon: <Search/>,
      colorClass: "amber-600",
      borderClass: "border-l-amber-600",
      bgClass: "bg-amber-600/10",
      textClass: "text-amber-600"
    },
    {
      number: "03",
      title: "Serper.dev Targeting", 
      subtitle: "Precision",
      description: "Targeted Google searches to fill critical data gaps for high-relevance opportunities",
      metrics: ["≥70% relevance targeting", "90% field completion", "Smart extraction"],
      icon: <Zap/>,
      colorClass: "slate-700",
      borderClass: "border-l-slate-700",
      bgClass: "bg-slate-700/10",
      textClass: "text-slate-700"
    }
  ];

  const techStack = [
    {
      category: "Backend",
      icon: <Server/>,
      technologies: ["PostgreSQL with spatial extensions", "FastAPI async processing", "Python ML pipeline", "Crawl4AI automation"],
      colorClass: "slate-700",
      bgClass: "bg-slate-700/5",
      borderClass: "border-slate-700",
      textClass: "text-slate-700"
    },
    {
      category: "Frontend", 
      icon: <Monitor/>,
      technologies: ["Next.js 14 with TypeScript", "Recharts visualization", "Tailwind CSS design system", "React Server Components"],
      colorClass: "amber-600",
      bgClass: "bg-amber-600/5",
      borderClass: "border-amber-600",
      textClass: "text-amber-600"
    },
    {
      category: "Infrastructure",
      icon: <Shield/>,
      technologies: ["Docker containerization", "OAuth 2.0 security", "Real-time monitoring", "Horizontal scaling"],
      colorClass: "site-burgandy",
      bgClass: "bg-site-burgandy",
      borderClass: "border-site-burgandy",
      textClass: "text-site-burgandy"
    }
  ];

  const qualityMetrics = [
    { label: "Field Completion", target: "90%+", current: "87%", textClass: "text-amber-600", borderClass: "border-amber-600/20" },
    { label: "Accuracy Rate", target: "95%+", current: "96%", textClass: "text-slate-700", borderClass: "border-slate-700/20" },
    { label: "Max Latency", target: "24h", current: "18h", textClass: "text-slate-600", borderClass: "border-slate-600/20" },
    { label: "Country Coverage", target: "54", current: "54", textClass: "text-slate-700", borderClass: "border-slate-700/20" }
  ];

  const futurePhases = [
    {
      phase: "Phase 2",
      title: "Funding Lifecycle Tracking",
      description: "Monitor actual disbursements, recipient organizations, and project implementation outcomes",
      features: ["Disbursement monitoring", "Spending pattern analysis", "Impact measurement", "Efficiency reporting"],
      timeline: "Q3 2025",
      colorClass: "slate-600",
      bgClass: "bg-slate-600/10",
      borderClass: "border-slate-600/20",
      textClass: "text-slate-600"
    },
    {
      phase: "Phase 3", 
      title: "Project Showcase & Amplification",
      description: "Platform features highlighting equity-deserving groups and successful AI projects",
      features: ["Funded project database", "Equity amplification tools", "Success story tracking", "Mentorship connections"],
      timeline: "Q1 2026",
      colorClass: "amber-600",
      bgClass: "bg-amber-600/10",
      borderClass: "border-amber-600/20",
      textClass: "text-amber-600"
    },
    {
      phase: "Phase 4",
      title: "Comprehensive Data Platform", 
      description: "Multi-stakeholder ecosystem serving students, businesses, and governments",
      features: ["Student resources", "Business intelligence", "Government dashboards", "Research portal"],
      timeline: "Q3 2026",
      colorClass: "slate-700",
      bgClass: "bg-slate-700/10",
      borderClass: "border-site-sage/20",
      textClass: "text-site-sage"
    }
  ];

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Hero Section */}
      <section className="relative bg-slate-50 border-slate-200/50 overflow-hidden">
        {/* Background Pattern */}
        <div className="absolute inset-0 opacity-20">
          <div className="absolute top-20 left-20 w-32 h-32 bg-slate-600 rounded-full blur-3xl"></div>
          <div className="absolute top-40 right-32 w-24 h-24 bg-amber-600 rounded-full blur-2xl"></div>
          <div className="absolute bottom-20 left-1/3 w-28 h-28 bg-brown-700 rounded-full blur-3xl"></div>
        </div>
        
        <div className="relative max-w-7xl mx-auto py-24 px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            {/* Enhanced Title with Badge */}
            <div className="inline-flex items-center px-4 py-2 bg-slate-600/10 border border-slate-600/20 rounded-full text-sm font-medium text-slate-600 mb-6 animate-fadeInUp">
              <Code className="h-4 w-4 mr-2" />
              Technical Documentation
            </div>
            
            <h1 className="text-6xl md:text-7xl font-bold text-slate-700 mb-6 animate-fadeInUp leading-tight" style={{ animationDelay: '0.1s' }}>
              Methodology: Architecture & Evaluation Metrics
            </h1>
            
            <p className="text-xl md:text-2xl text-slate-600 max-w-4xl mx-auto leading-relaxed animate-fadeInUp" style={{ animationDelay: '0.2s' }}>
              A sophisticated <span className="font-semibold text-slate-700">three-stage pipeline</span> combining automated aggregation, 
              intelligent scraping, and targeted enrichment for comprehensive 
              <span className="font-semibold text-slate-600">African AI funding intelligence</span>.
            </p>
            
            {/* Key Stats */}
            <div className="flex flex-wrap justify-center gap-8 mt-12 animate-fadeInUp" style={{ animationDelay: '0.3s' }}>
              <div className="text-center">
                <div className="text-5xl font-bold text-slate-600">200+</div>
                <div className="text-lg text-slate-600 font-medium">RSS Sources</div>
              </div>
              <div className="text-center">
                <div className="text-5xl font-bold text-amber-600">90%+</div>
                <div className="text-lg text-slate-600 font-medium">Field Completion</div>
              </div>
              <div className="text-center">
                <div className="text-5xl font-bold text-red-600">54</div>
                <div className="text-lg text-slate-600 font-medium">African Countries</div>
              </div>
              <div className="text-center">
                <div className="text-5xl font-bold text-slate-700">24h</div>
                <div className="text-lg text-slate-600 font-medium">Max Latency</div>
              </div>1
            </div>
          </div>
        </div>
      </section>

      {/* Three-Stage Pipeline */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-slate-700 mb-4">Three-Stage Data Collection Pipeline</h2>
            <p className="text-lg text-slate-600">Volume → Depth → Precision</p>
          </div>

          <div className="grid md:grid-cols-3 gap-10 mb-16">
            {stages.map((stage, index) => (
              <div key={index} className="relative group animate-fadeInUp" style={{ animationDelay: `${0.3 + index * 0.1}s` }}>
                <div className={`bg-white p-8 rounded-xl shadow-lg hover:shadow-2xl hover:-translate-y-2 transition-all duration-300 border-l-4 ${stage.borderClass}`}>
                  <div className="flex items-center mb-6">
                    <div className={`w-16 h-16 rounded-full flex items-center justify-center mr-5 border-2 ${stage.bgClass} ${stage.textClass} border-current`}>
                      {React.cloneElement(stage.icon, { className: "h-8 w-8" })}
                    </div>
                    <div>
                      <div className={`text-sm font-bold ${stage.textClass}`}>STAGE {stage.number}</div>
                      <div className="text-xl font-semibold text-slate-700">{stage.title}</div>
                      <div className={`text-md font-medium ${stage.textClass}`}>{stage.subtitle}</div>
                    </div>
                  </div>
                  
                  <p className="text-slate-600 mb-6 h-24">{stage.description}</p>
                  
                  <div className="space-y-3">
                    {stage.metrics.map((metric, idx) => (
                      <div key={idx} className="flex items-center text-sm">
                        <CheckCircle className={`h-5 w-5 ${stage.textClass}`} />
                        <span className="text-slate-600">{metric}</span>
                      </div>
                    ))}
                  </div>
                </div>
                
                {index < stages.length - 1 && (
                  <div className="hidden md:block absolute top-1/2 -right-5 transform -translate-y-1/2 group-hover:scale-125 transition-transform">
                    <ArrowRight className="h-10 w-10 text-slate-200/50" />
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Pipeline Flow Diagram */}
          <div className="bg-white/80 backdrop-blur-sm p-8 rounded-2xl shadow-xl border border-slate-200/50 animate-fadeInUp" style={{ animationDelay: '0.7s' }}>
            <h3 className="text-2xl font-semibold text-slate-700 mb-12 text-center">Complete Pipeline Flow</h3>
            <div className="flex flex-col md:flex-row items-center justify-between space-y-6 md:space-y-0 md:space-x-6">
              {[
                { icon: <Database className="h-8 w-8" />, title: "200+ RSS Feeds", subtitle: "15-30 min polling", bgClass: "bg-slate-600/10", textClass: "text-slate-600", borderClass: "border-slate-600" },
                { icon: <Code className="h-8 w-8" />, title: "Intelligent Scraping", subtitle: "Deep content extraction", bgClass: "bg-amber-600/10", textClass: "text-amber-600", borderClass: "border-amber-600" },
                { icon: <Search className="h-8 w-8" />, title: "Targeted Search", subtitle: "Gap filling precision", bgClass: "bg-slate-700/10", textClass: "text-slate-700", borderClass: "border-slate-700" },
                { icon: <CheckCircle className="h-8 w-8" />, title: "Complete Dataset", subtitle: "90%+ field completion", bgClass: "bg-slate-700/10", textClass: "text-slate-700", borderClass: "border-slate-700" }
              ].map((item, index, arr) => (
                <React.Fragment key={index}>
                  <div className="text-center group cursor-pointer">
                    <div className={`w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-3 border-2 group-hover:scale-110 transition-transform ${item.bgClass} ${item.textClass} ${item.borderClass}`}>
                      {item.icon}
                    </div>
                    <div className="text-md font-medium text-slate-700">{item.title}</div>
                    <div className="text-sm text-slate-600">{item.subtitle}</div>
                  </div>
                  {index < arr.length - 1 && <ArrowRight className="text-slate-600 hidden md:block h-10 w-10 stroke-2" />}
                </React.Fragment>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Technology Stack */}
      <section className={`py-20 ${techStack[0].bgClass} backdrop-blur-sm`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className={`${techStack[0].textClass} mb-4`}>Technology Stack</h2>
            <p className={`${techStack[0].textClass}`}>Modern, scalable architecture built for African AI intelligence</p>
          </div>

          <div className="grid md:grid-cols-3 gap-10">
            {techStack.map((stack, index) => (
              <div key={index} className={`p-8 rounded-2xl border-2 hover:shadow-xl transition-all duration-300 hover:-translate-y-1 animate-fadeInUp ${stack.borderClass} ${stack.bgClass}`} style={{ 
                animationDelay: `${0.3 + index * 0.1}s`,
                borderColor: index === 0 ? '#475569' : index === 1 ? '#d97706' : '#4b1212',
                backgroundColor: index === 0 ? 'rgba(71, 85, 105, 0.05)' : index === 1 ? 'rgba(217, 119, 6, 0.05)' : 'rgba(75, 18, 18, 0.05)'
              }}>
                <div className="flex items-center mb-5">
                  <div className={stack.textClass} style={{ color: index === 0 ? '#475569' : index === 1 ? '#d97706' : '#4b1212' }}>{React.cloneElement(stack.icon, { className: "h-8 w-8" })}</div>
                  <h3 className={`text-2xl font-semibold ml-4 ${stack.textClass}`} style={{ color: index === 0 ? '#475569' : index === 1 ? '#d97706' : '#4b1212' }}>{stack.category}</h3>
                </div>
                <ul className="space-y-3">
                  {stack.technologies.map((tech, idx) => (
                    <li key={idx} className="text-md text-slate-600 flex items-center">
                      <div className={`w-2.5 h-2.5 bg-white rounded-full mr-3 border ${stack.borderClass}`}></div>
                      {tech}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Quality Metrics */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-slate-700 mb-4">Data Quality & Performance</h2>
            <p className="text-lg text-slate-600">Rigorous validation ensuring reliable intelligence</p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {qualityMetrics.map((metric, index) => (
              <div key={index} className={`bg-white p-6 rounded-2xl shadow-lg text-center hover:scale-105 transition-transform duration-300 animate-fadeInUp border ${metric.borderClass}`} style={{ animationDelay: `${0.3 + index * 0.1}s` }}>
                <div className={`text-5xl font-bold mb-2 ${metric.textClass}`}>
                  {metric.current}
                </div>
                <div className="text-md font-medium text-slate-700 mb-1">{metric.label}</div>
                <div className="text-sm text-slate-600">Target: {metric.target}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Future Roadmap */}
      <section className="py-20 bg-white/80 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-slate-700 mb-4">Development Roadmap</h2>
            <p className="text-lg text-slate-600">Building AI by Africans, for Africans</p>
          </div>

          <div className="space-y-10">
            {futurePhases.map((phase, index) => (
              <div key={index} className={`${phase.bgClass} p-8 rounded-2xl border ${phase.borderClass} shadow-md hover:shadow-xl transition-shadow duration-300 animate-fadeInUp`} style={{ 
                animationDelay: `${0.3 + index * 0.1}s`,
                ...(index === 2 && {
                  backgroundColor: 'rgba(75, 18, 18, 0.1)',
                  borderColor: 'rgba(75, 18, 18, 0.1)'
                })
              }}>
                <div className="flex flex-col md:flex-row items-start">
                  <div className="md:w-1/3 mb-6 md:mb-0">
                    <div className={`text-md font-bold ${phase.textClass} mb-2`} style={index === 2 ? { color: '#4b1212' } : {}}>{phase.phase}</div>
                    <h3 className="text-2xl font-semibold text-slate-700 mb-3">{phase.title}</h3>
                    <div className={`inline-block ${phase.textClass} text-sm px-3 py-1 rounded-full border ${phase.borderClass} shadow-sm`} style={index === 2 ? { color: '#4b1212', borderColor: '#4b1212' } : {}}>
                      {phase.timeline}
                    </div>
                  </div>
                  
                  <div className="md:w-2/3 md:pl-8">
                    <p className="text-slate-600 mb-5 text-md">{phase.description}</p>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      {phase.features.map((feature, idx) => (
                        <div key={idx} className="flex items-center text-md">
                          <CheckCircle className={`h-5 w-5 ${phase.textClass} mr-3`} style={index === 2 ? { color: '#4b1212' } : {}} />
                          <span className="text-slate-600">{feature}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Vision Statement */}
      <section className="py-24 bg-gradient-to-br from-slate-700 to-slate-600">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-6xl font-bold mb-20 text-orange-500 animate-fadeInUp" style={{ animationDelay: '0.1s', color: '#f97316', marginBottom: '5rem' }}>Vision: AI by Africans, for Africans</h2>
          <p className="text-xl max-w-4xl mx-auto leading-relaxed text-amber-500 animate-fadeInUp" style={{ animationDelay: '0.2s', color: '#f97316' }}>
            TAIFA-FIALA&apos;s ultimate goal extends beyond data collection to become the central platform
            enabling African-led AI development. Through transparent funding intelligence, project amplification, 
            and ecosystem building, we democratize access to AI development resources and learning opportunities 
            to ensure African voices lead the continent&apos;s AI transformation.
          </p>
          
          <div className="mt-16 grid md:grid-cols-3 gap-10">
            {[
              { icon: <Users/>, title: "For Students", description: "Educational resources and funding guidance" },
              { icon: <TrendingUp/>, title: "For Businesses", description: "Market intelligence and investment insights" },
              { icon: <Shield/>, title: "For Governments", description: "Policy development and strategic planning" }
            ].map((item, index) => (
              <div key={index} className="text-center animate-fadeInUp" style={{ animationDelay: `${0.3 + index * 0.1}s` }}>
                <div className="w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-5 border-2 bg-amber-600/20 text-amber-600 border-amber-600/50">
                  {React.cloneElement(item.icon, { className: "h-10 w-10" })}
                </div>
                <h3 className="text-xl font-semibold mb-2 text-white" style={{ color: '#f97316' }}>{item.title}</h3>
                <p className="text-md text-white/80" style={{ color: '#f97316' }}>{item.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}