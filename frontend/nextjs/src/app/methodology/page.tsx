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
      colorClass: "taifa-accent",
      borderClass: "border-l-taifa-accent",
      bgClass: "bg-taifa-accent/10",
      textClass: "text-taifa-accent"
    },
    {
      number: "02", 
      title: "Crawl4AI Intelligence",
      subtitle: "Depth",
      description: "Intelligent web scraping to retrieve comprehensive funding details from source websites",
      metrics: ["Smart navigation", "Multi-format support", "95% uptime"],
      icon: <Search/>,
      colorClass: "taifa-secondary",
      borderClass: "border-l-taifa-secondary",
      bgClass: "bg-taifa-secondary/10",
      textClass: "text-taifa-secondary"
    },
    {
      number: "03",
      title: "Serper.dev Targeting", 
      subtitle: "Precision",
      description: "Targeted Google searches to fill critical data gaps for high-relevance opportunities",
      metrics: ["≥70% relevance targeting", "90% field completion", "Smart extraction"],
      icon: <Zap/>,
      colorClass: "taifa-olive",
      borderClass: "border-l-taifa-olive",
      bgClass: "bg-taifa-olive/10",
      textClass: "text-taifa-olive"
    }
  ];

  const techStack = [
    {
      category: "Backend",
      icon: <Server/>,
      technologies: ["PostgreSQL with spatial extensions", "FastAPI async processing", "Python ML pipeline", "Crawl4AI automation"],
      colorClass: "taifa-primary",
      bgClass: "bg-taifa-primary/5",
      borderClass: "border-taifa-primary",
      textClass: "text-taifa-primary"
    },
    {
      category: "Frontend", 
      icon: <Monitor/>,
      technologies: ["Next.js 14 with TypeScript", "Recharts visualization", "Tailwind CSS design system", "React Server Components"],
      colorClass: "taifa-accent",
      bgClass: "bg-taifa-accent/5",
      borderClass: "border-taifa-accent",
      textClass: "text-taifa-accent"
    },
    {
      category: "Infrastructure",
      icon: <Shield/>,
      technologies: ["Docker containerization", "OAuth 2.0 security", "Real-time monitoring", "Horizontal scaling"],
      colorClass: "taifa-secondary",
      bgClass: "bg-taifa-secondary/5",
      borderClass: "border-taifa-secondary",
      textClass: "text-taifa-secondary"
    }
  ];

  const qualityMetrics = [
    { label: "Field Completion", target: "90%+", current: "87%", textClass: "text-taifa-secondary", borderClass: "border-taifa-secondary/20" },
    { label: "Accuracy Rate", target: "95%+", current: "96%", textClass: "text-taifa-primary", borderClass: "border-taifa-primary/20" },
    { label: "Max Latency", target: "24h", current: "18h", textClass: "text-taifa-accent", borderClass: "border-taifa-accent/20" },
    { label: "Country Coverage", target: "54", current: "54", textClass: "text-taifa-olive", borderClass: "border-taifa-olive/20" }
  ];

  const futurePhases = [
    {
      phase: "Phase 2",
      title: "Funding Lifecycle Tracking",
      description: "Monitor actual disbursements, recipient organizations, and project implementation outcomes",
      features: ["Disbursement monitoring", "Spending pattern analysis", "Impact measurement", "Efficiency reporting"],
      timeline: "Q3 2025"
    },
    {
      phase: "Phase 3", 
      title: "Project Showcase & Amplification",
      description: "Platform features highlighting equity-deserving groups and successful AI projects",
      features: ["Funded project database", "Equity amplification tools", "Success story tracking", "Mentorship connections"],
      timeline: "Q1 2026"
    },
    {
      phase: "Phase 4",
      title: "Comprehensive Data Platform", 
      description: "Multi-stakeholder ecosystem serving students, businesses, and governments",
      features: ["Student resources", "Business intelligence", "Government dashboards", "Research portal"],
      timeline: "Q3 2026"
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-b from-taifa-light via-taifa-light/50 to-taifa-light">
      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-taifa-white via-taifa-light/30 to-taifa-white border-b border-taifa-border/50 overflow-hidden">
        {/* Background Pattern */}
        <div className="absolute inset-0 opacity-5">
          <div className="absolute top-20 left-20 w-32 h-32 bg-taifa-accent rounded-full blur-3xl"></div>
          <div className="absolute top-40 right-32 w-24 h-24 bg-taifa-secondary rounded-full blur-2xl"></div>
          <div className="absolute bottom-20 left-1/3 w-28 h-28 bg-taifa-olive rounded-full blur-3xl"></div>
        </div>
        
        <div className="relative max-w-7xl mx-auto py-24 px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            {/* Enhanced Title with Badge */}
            <div className="inline-flex items-center px-4 py-2 bg-taifa-accent/10 border border-taifa-accent/20 rounded-full text-sm font-medium text-taifa-accent mb-6 animate-fadeInUp">
              <Code className="h-4 w-4 mr-2" />
              Technical Documentation
            </div>
            
            <h1 className="text-6xl md:text-7xl font-bold text-taifa-primary mb-6 animate-fadeInUp leading-tight" style={{ animationDelay: '0.1s' }}>
              Methodology &
              <span className="block bg-gradient-to-r from-taifa-accent to-taifa-secondary bg-clip-text text-transparent">
                Architecture
              </span>
            </h1>
            
            <p className="text-xl md:text-2xl text-taifa-muted max-w-4xl mx-auto leading-relaxed animate-fadeInUp" style={{ animationDelay: '0.2s' }}>
              A sophisticated <span className="font-semibold text-taifa-primary">three-stage pipeline</span> combining automated aggregation, 
              intelligent scraping, and targeted enrichment for comprehensive 
              <span className="font-semibold text-taifa-accent">African AI funding intelligence</span>.
            </p>
            
            {/* Key Stats */}
            <div className="flex flex-wrap justify-center gap-8 mt-12 animate-fadeInUp" style={{ animationDelay: '0.3s' }}>
              <div className="text-center">
                <div className="text-3xl font-bold text-taifa-accent">200+</div>
                <div className="text-sm text-taifa-muted font-medium">RSS Sources</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-taifa-secondary">90%+</div>
                <div className="text-sm text-taifa-muted font-medium">Field Completion</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-taifa-olive">54</div>
                <div className="text-sm text-taifa-muted font-medium">African Countries</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-taifa-primary">24h</div>
                <div className="text-sm text-taifa-muted font-medium">Max Latency</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Three-Stage Pipeline */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-taifa-primary mb-4">Three-Stage Data Collection Pipeline</h2>
            <p className="text-lg text-taifa-muted">Volume → Depth → Precision</p>
          </div>

          <div className="grid md:grid-cols-3 gap-10 mb-16">
            {stages.map((stage, index) => (
              <div key={index} className="relative group animate-fadeInUp" style={{ animationDelay: `${0.3 + index * 0.1}s` }}>
                <div className={`bg-taifa-white p-8 rounded-xl shadow-lg hover:shadow-2xl hover:-translate-y-2 transition-all duration-300 border-l-4 ${stage.borderClass}`}>
                  <div className="flex items-center mb-6">
                    <div className={`w-16 h-16 rounded-full flex items-center justify-center mr-5 border-2 ${stage.bgClass} ${stage.textClass} border-current`}>
                      {React.cloneElement(stage.icon, { className: "h-8 w-8" })}
                    </div>
                    <div>
                      <div className={`text-sm font-bold ${stage.textClass}`}>STAGE {stage.number}</div>
                      <div className="text-xl font-semibold text-taifa-primary">{stage.title}</div>
                      <div className={`text-md font-medium ${stage.textClass}`}>{stage.subtitle}</div>
                    </div>
                  </div>
                  
                  <p className="text-taifa-muted mb-6 h-24">{stage.description}</p>
                  
                  <div className="space-y-3">
                    {stage.metrics.map((metric, idx) => (
                      <div key={idx} className="flex items-center text-sm">
                        <CheckCircle className={`h-5 w-5 mr-3 ${stage.textClass}`} />
                        <span className="text-taifa-muted">{metric}</span>
                      </div>
                    ))}
                  </div>
                </div>
                
                {index < stages.length - 1 && (
                  <div className="hidden md:block absolute top-1/2 -right-5 transform -translate-y-1/2 group-hover:scale-125 transition-transform">
                    <ArrowRight className="h-10 w-10 text-taifa-border/50" />
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Pipeline Flow Diagram */}
          <div className="bg-taifa-white/80 backdrop-blur-sm p-8 rounded-2xl shadow-xl border border-taifa-border/50 animate-fadeInUp" style={{ animationDelay: '0.7s' }}>
            <h3 className="text-2xl font-semibold text-taifa-primary mb-8 text-center">Complete Pipeline Flow</h3>
            <div className="flex flex-col md:flex-row items-center justify-between space-y-6 md:space-y-0 md:space-x-6">
              {[
                { icon: <Database className="h-8 w-8" />, title: "200+ RSS Feeds", subtitle: "15-30 min polling", bgClass: "bg-taifa-accent/10", textClass: "text-taifa-accent", borderClass: "border-taifa-accent" },
                { icon: <Code className="h-8 w-8" />, title: "Intelligent Scraping", subtitle: "Deep content extraction", bgClass: "bg-taifa-secondary/10", textClass: "text-taifa-secondary", borderClass: "border-taifa-secondary" },
                { icon: <Search className="h-8 w-8" />, title: "Targeted Search", subtitle: "Gap filling precision", bgClass: "bg-taifa-olive/10", textClass: "text-taifa-olive", borderClass: "border-taifa-olive" },
                { icon: <CheckCircle className="h-8 w-8" />, title: "Complete Dataset", subtitle: "90%+ field completion", bgClass: "bg-taifa-primary/10", textClass: "text-taifa-primary", borderClass: "border-taifa-primary" }
              ].map((item, index, arr) => (
                <React.Fragment key={index}>
                  <div className="text-center group cursor-pointer">
                    <div className={`w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-3 border-2 group-hover:scale-110 transition-transform ${item.bgClass} ${item.textClass} ${item.borderClass}`}>
                      {item.icon}
                    </div>
                    <div className="text-md font-medium text-taifa-primary">{item.title}</div>
                    <div className="text-sm text-taifa-muted">{item.subtitle}</div>
                  </div>
                  {index < arr.length - 1 && <ArrowRight className="text-taifa-border/60 hidden md:block" />}
                </React.Fragment>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Technology Stack */}
      <section className="py-20 bg-taifa-white/80 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-taifa-primary mb-4">Technology Stack</h2>
            <p className="text-lg text-taifa-muted">Modern, scalable architecture built for African AI intelligence</p>
          </div>

          <div className="grid md:grid-cols-3 gap-10">
            {techStack.map((stack, index) => (
              <div key={index} className={`p-8 rounded-2xl border-2 hover:shadow-xl transition-all duration-300 hover:-translate-y-1 animate-fadeInUp ${stack.borderClass} ${stack.bgClass}`} style={{ animationDelay: `${0.3 + index * 0.1}s` }}>
                <div className="flex items-center mb-5">
                  <div className={stack.textClass}>{React.cloneElement(stack.icon, { className: "h-8 w-8" })}</div>
                  <h3 className={`text-2xl font-semibold ml-4 ${stack.textClass}`}>{stack.category}</h3>
                </div>
                <ul className="space-y-3">
                  {stack.technologies.map((tech, idx) => (
                    <li key={idx} className="text-md text-taifa-muted flex items-center">
                      <div className={`w-2.5 h-2.5 bg-taifa-white rounded-full mr-3 border ${stack.borderClass}`}></div>
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
            <h2 className="text-4xl font-bold text-taifa-primary mb-4">Data Quality & Performance</h2>
            <p className="text-lg text-taifa-muted">Rigorous validation ensuring reliable intelligence</p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {qualityMetrics.map((metric, index) => (
              <div key={index} className={`bg-taifa-white p-6 rounded-2xl shadow-lg text-center hover:scale-105 transition-transform duration-300 animate-fadeInUp border ${metric.borderClass}`} style={{ animationDelay: `${0.3 + index * 0.1}s` }}>
                <div className={`text-5xl font-bold mb-2 ${metric.textClass}`}>
                  {metric.current}
                </div>
                <div className="text-md font-medium text-taifa-primary mb-1">{metric.label}</div>
                <div className="text-sm text-taifa-muted">Target: {metric.target}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Future Roadmap */}
      <section className="py-20 bg-taifa-white/80 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-taifa-primary mb-4">Development Roadmap</h2>
            <p className="text-lg text-taifa-muted">Building toward AI by Africans, for Africans</p>
          </div>

          <div className="space-y-10">
            {futurePhases.map((phase, index) => (
              <div key={index} className="bg-taifa-light/80 p-8 rounded-2xl border border-taifa-border/50 shadow-md hover:shadow-xl transition-shadow duration-300 animate-fadeInUp" style={{ animationDelay: `${0.3 + index * 0.1}s` }}>
                <div className="flex flex-col md:flex-row items-start">
                  <div className="md:w-1/3 mb-6 md:mb-0">
                    <div className="text-md font-bold text-taifa-accent mb-2">{phase.phase}</div>
                    <h3 className="text-2xl font-semibold text-taifa-primary mb-3">{phase.title}</h3>
                    <div className="inline-block bg-taifa-white text-taifa-primary text-sm px-3 py-1 rounded-full border border-taifa-border/80 shadow-sm">
                      {phase.timeline}
                    </div>
                  </div>
                  
                  <div className="md:w-2/3 md:pl-8">
                    <p className="text-taifa-muted mb-5 text-md">{phase.description}</p>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      {phase.features.map((feature, idx) => (
                        <div key={idx} className="flex items-center text-md">
                          <CheckCircle className="h-5 w-5 text-taifa-accent mr-3" />
                          <span className="text-taifa-muted">{feature}</span>
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
      <section className="py-24 bg-gradient-to-br from-taifa-primary to-taifa-olive">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-4xl font-bold mb-6 text-taifa-white animate-fadeInUp" style={{ animationDelay: '0.1s' }}>Vision: AI by Africans, for Africans</h2>
          <p className="text-xl max-w-4xl mx-auto leading-relaxed text-taifa-orange animate-fadeInUp" style={{ animationDelay: '0.2s' }}>
            TAIFA-FIALA's ultimate goal extends beyond data collection to become the central platform 
            enabling African-led AI development. Through transparent funding intelligence, project amplification, 
            and ecosystem building, we democratize access to AI development resources and and ensure African voices 
            lead the continent's AI transformation.
          </p>
          
          <div className="mt-16 grid md:grid-cols-3 gap-10">
            {[
              { icon: <Users/>, title: "For Students", description: "Educational resources and funding guidance" },
              { icon: <TrendingUp/>, title: "For Businesses", description: "Market intelligence and investment insights" },
              { icon: <Shield/>, title: "For Governments", description: "Policy development and strategic planning" }
            ].map((item, index) => (
              <div key={index} className="text-center animate-fadeInUp" style={{ animationDelay: `${0.3 + index * 0.1}s` }}>
                <div className="w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-5 border-2 bg-taifa-secondary/20 text-taifa-secondary border-taifa-secondary/50">
                  {React.cloneElement(item.icon, { className: "h-10 w-10" })}
                </div>
                <h3 className="text-xl font-semibold mb-2 text-taifa-white">{item.title}</h3>
                <p className="text-md text-taifa-orange opacity-80">{item.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}