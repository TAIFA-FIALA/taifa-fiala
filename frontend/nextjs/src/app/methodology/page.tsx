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
      color: "amber",
      icon: <Globe className="h-8 w-8" />
    },
    {
      number: "02", 
      title: "Crawl4AI Intelligence",
      subtitle: "Depth",
      description: "Intelligent web scraping to retrieve comprehensive funding details from source websites",
      metrics: ["Smart navigation", "Multi-format support", "95% uptime"],
      color: "emerald",
      icon: <Search className="h-8 w-8" />
    },
    {
      number: "03",
      title: "Serper.dev Targeting", 
      subtitle: "Precision",
      description: "Targeted Google searches to fill critical data gaps for high-relevance opportunities",
      metrics: ["≥70% relevance targeting", "90% field completion", "Smart extraction"],
      color: "orange",
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
    <div className="min-h-screen bg-gradient-to-br from-amber-50 to-orange-50">
      {/* Hero Section */}
      <section className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto py-16 px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              Technical Methodology & Architecture
            </h1>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
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
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Three-Stage Data Collection Pipeline</h2>
            <p className="text-gray-600">Volume → Depth → Precision</p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 mb-12">
            {stages.map((stage, index) => (
              <div key={index} className="relative">
                <div className={`bg-white p-8 rounded-xl shadow-lg border-l-4 border-${stage.color}-500 hover:shadow-xl transition-shadow`}>
                  <div className="flex items-center mb-4">
                    <div className={`w-12 h-12 bg-${stage.color}-100 text-${stage.color}-700 rounded-full flex items-center justify-center mr-4`}>
                      {stage.icon}
                    </div>
                    <div>
                      <div className={`text-sm font-bold text-${stage.color}-600`}>STAGE {stage.number}</div>
                      <div className="text-lg font-semibold text-gray-900">{stage.title}</div>
                      <div className={`text-sm font-medium text-${stage.color}-700`}>{stage.subtitle}</div>
                    </div>
                  </div>
                  
                  <p className="text-gray-700 mb-6">{stage.description}</p>
                  
                  <div className="space-y-2">
                    {stage.metrics.map((metric, idx) => (
                      <div key={idx} className="flex items-center text-sm">
                        <CheckCircle className={`h-4 w-4 text-${stage.color}-600 mr-2`} />
                        <span className="text-gray-600">{metric}</span>
                      </div>
                    ))}
                  </div>
                </div>
                
                {index < stages.length - 1 && (
                  <div className="hidden md:block absolute top-1/2 -right-4 transform -translate-y-1/2">
                    <ArrowRight className="h-8 w-8 text-gray-300" />
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Pipeline Flow Diagram */}
          <div className="bg-white p-8 rounded-xl shadow-lg">
            <h3 className="text-xl font-semibold text-gray-900 mb-6 text-center">Complete Pipeline Flow</h3>
            <div className="flex flex-col md:flex-row items-center justify-between space-y-4 md:space-y-0 md:space-x-4">
              <div className="flex-1 text-center">
                <div className="w-16 h-16 bg-amber-100 text-amber-700 rounded-full flex items-center justify-center mx-auto mb-2">
                  <Database className="h-8 w-8" />
                </div>
                <div className="text-sm font-medium">200+ RSS Feeds</div>
                <div className="text-xs text-gray-500">15-30 min polling</div>
              </div>
              
              <ArrowRight className="text-gray-300 hidden md:block" />
              
              <div className="flex-1 text-center">
                <div className="w-16 h-16 bg-emerald-100 text-emerald-700 rounded-full flex items-center justify-center mx-auto mb-2">
                  <Code className="h-8 w-8" />
                </div>
                <div className="text-sm font-medium">Intelligent Scraping</div>
                <div className="text-xs text-gray-500">Deep content extraction</div>
              </div>
              
              <ArrowRight className="text-gray-300 hidden md:block" />
              
              <div className="flex-1 text-center">
                <div className="w-16 h-16 bg-orange-100 text-orange-700 rounded-full flex items-center justify-center mx-auto mb-2">
                  <Search className="h-8 w-8" />
                </div>
                <div className="text-sm font-medium">Targeted Search</div>
                <div className="text-xs text-gray-500">Gap filling precision</div>
              </div>
              
              <ArrowRight className="text-gray-300 hidden md:block" />
              
              <div className="flex-1 text-center">
                <div className="w-16 h-16 bg-blue-100 text-blue-700 rounded-full flex items-center justify-center mx-auto mb-2">
                  <CheckCircle className="h-8 w-8" />
                </div>
                <div className="text-sm font-medium">Complete Dataset</div>
                <div className="text-xs text-gray-500">90%+ field completion</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Technology Stack */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Technology Stack</h2>
            <p className="text-gray-600">Modern, scalable architecture built for African AI intelligence</p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {techStack.map((stack, index) => (
              <div key={index} className={`p-6 rounded-xl border-2 ${stack.color}`}>
                <div className="flex items-center mb-4">
                  {stack.icon}
                  <h3 className="text-lg font-semibold text-gray-900 ml-2">{stack.category}</h3>
                </div>
                <ul className="space-y-2">
                  {stack.technologies.map((tech, idx) => (
                    <li key={idx} className="text-sm text-gray-700 flex items-center">
                      <div className="w-2 h-2 bg-gray-400 rounded-full mr-2"></div>
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
      <section className="py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Data Quality & Performance</h2>
            <p className="text-gray-600">Rigorous validation ensuring reliable intelligence</p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {qualityMetrics.map((metric, index) => (
              <div key={index} className="bg-white p-6 rounded-xl shadow-lg text-center">
                <div className={`text-3xl font-bold ${metric.color} mb-2`}>
                  {metric.current}
                </div>
                <div className="text-sm font-medium text-gray-900 mb-1">{metric.label}</div>
                <div className="text-xs text-gray-500">Target: {metric.target}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Future Roadmap */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Development Roadmap</h2>
            <p className="text-gray-600">Building toward AI by Africans, for Africans</p>
          </div>

          <div className="space-y-8">
            {futurePhases.map((phase, index) => (
              <div key={index} className="bg-gradient-to-r from-amber-50 to-orange-50 p-8 rounded-xl">
                <div className="flex flex-col md:flex-row items-start">
                  <div className="md:w-1/3 mb-4 md:mb-0">
                    <div className="text-sm font-bold text-amber-600 mb-1">{phase.phase}</div>
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">{phase.title}</h3>
                    <div className="inline-block bg-amber-100 text-amber-800 text-xs px-2 py-1 rounded-full">
                      {phase.timeline}
                    </div>
                  </div>
                  
                  <div className="md:w-2/3 md:pl-8">
                    <p className="text-gray-700 mb-4">{phase.description}</p>
                    <div className="grid grid-cols-2 gap-3">
                      {phase.features.map((feature, idx) => (
                        <div key={idx} className="flex items-center text-sm">
                          <CheckCircle className="h-4 w-4 text-emerald-600 mr-2" />
                          <span className="text-gray-600">{feature}</span>
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
      <section className="py-16 bg-gradient-to-r from-amber-700 to-orange-800 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold mb-6">Vision: AI by Africans, for Africans</h2>
          <p className="text-xl text-amber-100 max-w-4xl mx-auto leading-relaxed">
            TAIFA-FIALA's ultimate goal extends beyond data collection to become the central platform 
            enabling African-led AI development. Through transparent funding intelligence, project amplification, 
            and ecosystem building, we democratize access to AI development resources and ensure African voices 
            lead the continent's AI transformation.
          </p>
          
          <div className="mt-12 grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <Users className="h-12 w-12 mx-auto mb-4 text-amber-200" />
              <h3 className="text-lg font-semibold mb-2">For Students</h3>
              <p className="text-amber-100 text-sm">Educational resources and funding guidance</p>
            </div>
            <div className="text-center">
              <TrendingUp className="h-12 w-12 mx-auto mb-4 text-amber-200" />
              <h3 className="text-lg font-semibold mb-2">For Businesses</h3>
              <p className="text-amber-100 text-sm">Market intelligence and investment insights</p>
            </div>
            <div className="text-center">
              <Shield className="h-12 w-12 mx-auto mb-4 text-amber-200" />
              <h3 className="text-lg font-semibold mb-2">For Governments</h3>
              <p className="text-amber-100 text-sm">Policy development and strategic planning</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
