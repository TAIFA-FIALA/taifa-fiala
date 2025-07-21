import React from 'react';
import { Database, Search, Globe, Zap, Users, TrendingUp, CheckCircle, ArrowRight, Code, Server, Monitor, Shield } from 'lucide-react';

export default function MethodologyPage() {
  const stages = [
    {
      number: "01",
      title: "RSS Aggregate Polling",
      subtitle: "Volume",
      description: "Custom-curated RSS feeds from 200+ funding organizations across Africa and internationally",
      metrics: ["85-90% capture rate", "500-800 daily opportunities", "15-30 min polling"],
      color: "#F0A621",
      icon: <Globe className="h-8 w-8" />
    },
    {
      number: "02", 
      title: "Crawl4AI Intelligence",
      subtitle: "Depth",
      description: "Intelligent web scraping to retrieve comprehensive funding details from source websites",
      metrics: ["Smart navigation", "Multi-format support", "95% uptime"],
      color: "'#F0A621",
      icon: <Search className="h-8 w-8" />
    },
    {
      number: "03",
      title: "Serper.dev Targeting", 
      subtitle: "Precision",
      description: "Targeted Google searches to fill critical data gaps for high-relevance opportunities",
      metrics: ["≥70% relevance targeting", "90% field completion", "Smart extraction"],
      color: "#5F763B'",
      icon: <Zap className="h-8 w-8" />
    }
  ];

  const techStack = [
    {
      category: "Backend",
      icon: <Server className="h-6 w-6" />,
      technologies: ["PostgreSQL with spatial extensions", "FastAPI async processing", "Python ML pipeline", "Crawl4AI automation"],
      color: "bg-blue-50 border-blue-200"
    },
    {
      category: "Frontend", 
      icon: <Monitor className="h-6 w-6" />,
      technologies: ["Next.js 14 with TypeScript", "Recharts visualization", "Tailwind CSS design system", "React Server Components"],
      color: "bg-green-50 border-green-200"
    },
    {
      category: "Infrastructure",
      icon: <Shield className="h-6 w-6" />,
      technologies: ["Docker containerization", "OAuth 2.0 security", "Real-time monitoring", "Horizontal scaling"],
      color: "bg-purple-50 border-purple-200"
    }
  ];

  const qualityMetrics = [
    { label: "Field Completion", target: "90%+", current: "87%", color: "text-emerald-700" },
    { label: "Accuracy Rate", target: "95%+", current: "96%", color: "text-blue-700" },
    { label: "Max Latency", target: "24h", current: "18h", color: "text-amber-700" },
    { label: "Country Coverage", target: "54", current: "54", color: "text-orange-700" }
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
    <div className="min-h-screen bg-taifa-light">
      {/* Hero Section */}
      <section className="bg-white border-b border-taifa-border">
        <div className="max-w-7xl mx-auto py-16 px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-4xl font-bold text-taifa-primary mb-4">
              Technical Methodology & Architecture
            </h1>
            <p className="text-xl text-taifa-muted max-w-3xl mx-auto">
              Sophisticated three-stage pipeline combining automated aggregation, intelligent scraping, 
              and targeted enrichment for comprehensive African AI funding intelligence
            </p>
          </div>
        </div>
      </section>

      {/* Three-Stage Pipeline */}
      <section className="py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-taifa-primary mb-4">Three-Stage Data Collection Pipeline</h2>
            <p className="text-taifa-muted">Volume → Depth → Precision</p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 mb-12">
            {stages.map((stage, index) => {
              const stageColors = [
                { border: 'border-taifa-accent', bg: 'bg-taifa-light', text: 'text-taifa-accent' },
                { border: 'border-taifa-secondary', bg: 'bg-taifa-light', text: 'text-taifa-secondary' },
                { border: 'border-taifa-primary', bg: 'bg-taifa-light', text: 'text-taifa-primary' }
              ];
              const colors = stageColors[index];
              
              return (
                <div key={index} className="relative">
                  <div className={`bg-white p-8 rounded-xl shadow-lg border-l-4 ${colors.border} hover:shadow-xl transition-shadow`}>
                    <div className="flex items-center mb-4">
                      <div className={`w-12 h-12 ${colors.bg} ${colors.text} rounded-full flex items-center justify-center mr-4`}>
                        {stage.icon}
                      </div>
                      <div>
                        <div className={`text-sm font-bold ${colors.text}`}>STAGE {stage.number}</div>
                        <div className="text-lg font-semibold text-taifa-primary">{stage.title}</div>
                        <div className={`text-sm font-medium ${colors.text}`}>{stage.subtitle}</div>
                      </div>
                    </div>
                    
                    <p className="text-taifa-muted mb-6">{stage.description}</p>
                    
                    <div className="space-y-2">
                      {stage.metrics.map((metric, idx) => (
                        <div key={idx} className="flex items-center text-sm">
                          <CheckCircle className={`h-4 w-4 ${colors.text} mr-2`} />
                          <span className="text-taifa-muted">{metric}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  {index < stages.length - 1 && (
                    <div className="hidden md:block absolute top-1/2 -right-4 transform -translate-y-1/2">
                      <ArrowRight className="h-8 w-8 text-taifa-border" />
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {/* Pipeline Flow Diagram */}
          <div className="bg-white p-8 rounded-xl shadow-lg border border-taifa-border">
            <h3 className="text-xl font-semibold text-taifa-primary mb-6 text-center">Complete Pipeline Flow</h3>
            <div className="flex flex-col md:flex-row items-center justify-between space-y-4 md:space-y-0 md:space-x-4">
              <div className="flex-1 text-center">
                <div className="w-16 h-16 bg-taifa-light text-taifa-accent rounded-full flex items-center justify-center mx-auto mb-2">
                  <Database className="h-8 w-8" />
                </div>
                <div className="text-sm font-medium text-taifa-primary">200+ RSS Feeds</div>
                <div className="text-xs text-taifa-muted">15-30 min polling</div>
              </div>
              
              <ArrowRight className="text-taifa-border hidden md:block" />
              
              <div className="flex-1 text-center">
                <div className="w-16 h-16 bg-taifa-light text-taifa-secondary rounded-full flex items-center justify-center mx-auto mb-2">
                  <Code className="h-8 w-8" />
                </div>
                <div className="text-sm font-medium text-taifa-primary">Intelligent Scraping</div>
                <div className="text-xs text-taifa-muted">Deep content extraction</div>
              </div>
              
              <ArrowRight className="text-taifa-border hidden md:block" />
              
              <div className="flex-1 text-center">
                <div className="w-16 h-16 bg-taifa-light text-taifa-primary rounded-full flex items-center justify-center mx-auto mb-2">
                  <Search className="h-8 w-8" />
                </div>
                <div className="text-sm font-medium text-taifa-primary">Targeted Search</div>
                <div className="text-xs text-taifa-muted">Gap filling precision</div>
              </div>
              
              <ArrowRight className="text-taifa-border hidden md:block" />
              
              <div className="flex-1 text-center">
                <div className="w-16 h-16 bg-taifa-light text-taifa-secondary rounded-full flex items-center justify-center mx-auto mb-2">
                  <CheckCircle className="h-8 w-8" />
                </div>
                <div className="text-sm font-medium text-taifa-primary">Complete Dataset</div>
                <div className="text-xs text-taifa-muted">90%+ field completion</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Technology Stack */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-taifa-primary mb-4">Technology Stack</h2>
            <p className="text-taifa-muted">Modern, scalable architecture built for African AI intelligence</p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {techStack.map((stack, index) => {
              const stackColors = [
                'bg-taifa-light border-taifa-primary',
                'bg-taifa-light border-taifa-secondary', 
                'bg-taifa-light border-taifa-accent'
              ];
              return (
                <div key={index} className={`p-6 rounded-xl border-2 ${stackColors[index]}`}>
                  <div className="flex items-center mb-4">
                    <div className="text-taifa-primary">{stack.icon}</div>
                    <h3 className="text-lg font-semibold text-taifa-primary ml-2">{stack.category}</h3>
                  </div>
                  <ul className="space-y-2">
                    {stack.technologies.map((tech, idx) => (
                      <li key={idx} className="text-sm text-taifa-muted flex items-center">
                        <div className="w-2 h-2 bg-taifa-border rounded-full mr-2"></div>
                        {tech}
                      </li>
                    ))}
                  </ul>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Quality Metrics */}
      <section className="py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-taifa-primary mb-4">Data Quality & Performance</h2>
            <p className="text-taifa-muted">Rigorous validation ensuring reliable intelligence</p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {qualityMetrics.map((metric, index) => {
              const metricColors = [
                'text-taifa-secondary',
                'text-taifa-primary', 
                'text-taifa-accent',
                'text-taifa-secondary'
              ];
              return (
                <div key={index} className="bg-white p-6 rounded-xl shadow-lg text-center border border-taifa-border">
                  <div className={`text-3xl font-bold ${metricColors[index]} mb-2`}>
                    {metric.current}
                  </div>
                  <div className="text-sm font-medium text-taifa-primary mb-1">{metric.label}</div>
                  <div className="text-xs text-taifa-muted">Target: {metric.target}</div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Future Roadmap */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-taifa-primary mb-4">Development Roadmap</h2>
            <p className="text-taifa-muted">Building toward AI by Africans, for Africans</p>
          </div>

          <div className="space-y-8">
            {futurePhases.map((phase, index) => (
              <div key={index} className="bg-taifa-light p-8 rounded-xl border border-taifa-border">
                <div className="flex flex-col md:flex-row items-start">
                  <div className="md:w-1/3 mb-4 md:mb-0">
                    <div className="text-sm font-bold text-taifa-accent mb-1">{phase.phase}</div>
                    <h3 className="text-xl font-semibold text-taifa-primary mb-2">{phase.title}</h3>
                    <div className="inline-block bg-white text-taifa-primary text-xs px-2 py-1 rounded-full border border-taifa-border">
                      {phase.timeline}
                    </div>
                  </div>
                  
                  <div className="md:w-2/3 md:pl-8">
                    <p className="text-taifa-muted mb-4">{phase.description}</p>
                    <div className="grid grid-cols-2 gap-3">
                      {phase.features.map((feature, idx) => (
                        <div key={idx} className="flex items-center text-sm">
                          <CheckCircle className="h-4 w-4 text-taifa-secondary mr-2" />
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
      <section className="py-16" style={{ background: 'linear-gradient(to right, #3E4B59, #5F763B)' }}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold mb-6 text-white">Vision: AI by Africans, for Africans</h2>
          <p className="text-xl max-w-4xl mx-auto leading-relaxed" style={{ color: '#F0E68C' }}>
            TAIFA-FIALA&amp;apos;s ultimate goal extends beyond data collection to become the central platform 
            enabling African-led AI development. Through transparent funding intelligence, project amplification, 
            and ecosystem building, we democratize access to AI development resources and ensure African voices 
            lead the continent&amp;apos;s AI transformation.
          </p>
          
          <div className="mt-12 grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <Users className="h-12 w-12 mx-auto mb-4" style={{ color: '#F0A621' }} />
              <h3 className="text-lg font-semibold mb-2 text-white">For Students</h3>
              <p className="text-sm" style={{ color: '#F0E68C' }}>Educational resources and funding guidance</p>
            </div>
            <div className="text-center">
              <TrendingUp className="h-12 w-12 mx-auto mb-4" style={{ color: '#F0A621' }} />
              <h3 className="text-lg font-semibold mb-2 text-white">For Businesses</h3>
              <p className="text-sm" style={{ color: '#F0E68C' }}>Market intelligence and investment insights</p>
            </div>
            <div className="text-center">
              <Shield className="h-12 w-12 mx-auto mb-4" style={{ color: '#F0A621' }} />
              <h3 className="text-lg font-semibold mb-2 text-white">For Governments</h3>
              <p className="text-sm" style={{ color: '#F0E68C' }}>Policy development and strategic planning</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}