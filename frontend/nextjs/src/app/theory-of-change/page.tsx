import { ArrowDown, Target, Users, Globe, BarChart3, Shield, Heart, Lightbulb, TrendingUp, CheckCircle } from 'lucide-react';
import React from 'react';
import { Metadata } from 'next';
import Image from 'next/image';

export const metadata: Metadata = {
  title: 'Theory of Change | TAIFA-FIALA',
  description: 'Our comprehensive theory of change for transforming AI funding transparency and equity across Africa through systematic intervention and capacity building.',
  keywords: 'theory of change, AI funding transparency, African AI development, capacity building, systemic change',
};

interface Stage {
  number: string;
  title: string;
  description: string;
  outcomes: string[];
  icon: React.ReactNode;
  colorClass: string;
  bgClass: string;
}

export default function TheoryOfChangePage() {
  const stages: Stage[] = [
    {
      number: "1",
      title: "Data Collection & Transparency",
      description: "Establish comprehensive, real-time tracking of AI funding flows across Africa through systematic data aggregation and verification.",
      outcomes: [
        "Real-time funding database covering 54 African countries",
        "Transparent methodology for data collection and verification",
        "Public access to funding patterns and trends",
        "Standardized reporting frameworks for funding organizations"
      ],
      icon: <BarChart3 className="h-12 w-12" />,
      colorClass: "text-slate-600",
      bgClass: "bg-slate-600/20"
    },
    {
      number: "2",
      title: "Analysis & Insight Generation",
      description: "Transform raw funding data into actionable insights that reveal systemic inequities and identify intervention opportunities.",
      outcomes: [
        "Comprehensive funding landscape reports",
        "Geographic and demographic disparity analysis",
        "Sector-specific funding gap identification",
        "Evidence-based policy recommendations"
      ],
      icon: <Lightbulb className="h-12 w-12" />,
      colorClass: "text-amber-600",
      bgClass: "bg-amber-600/20"
    },
    {
      number: "3",
      title: "Stakeholder Engagement",
      description: "Build coalitions among funders, policymakers, researchers, and civil society to create momentum for systemic change.",
      outcomes: [
        "Active engagement with 50+ funding organizations",
        "Policy dialogue with African governments",
        "Research partnerships with academic institutions",
        "Civil society advocacy network development"
      ],
      icon: <Users className="h-12 w-12" />,
      colorClass: "text-site-brown",
      bgClass: "bg-site-brown/20"
    },
    {
      number: "4",
      title: "Capacity Building",
      description: "Strengthen local ecosystems through knowledge transfer, skill development, and institutional capacity enhancement.",
      outcomes: [
        "Training programs for local researchers and analysts",
        "Technical assistance for funding transparency initiatives",
        "Institutional partnerships with African organizations",
        "Open-source tools and methodologies"
      ],
      icon: <TrendingUp className="h-12 w-12" />,
      colorClass: "text-site-teal",
      bgClass: "bg-site-teal/20"
    },
    {
      number: "5",
      title: "Policy Influence",
      description: "Leverage evidence and stakeholder networks to influence funding policies and practices toward greater equity and transparency.",
      outcomes: [
        "Policy recommendations adopted by funding organizations",
        "Increased transparency requirements in funding processes",
        "Geographic diversity mandates in AI investment",
        "Gender equity improvements in funding allocation"
      ],
      icon: <Shield className="h-12 w-12" />,
      colorClass: "text-site-purple",
      bgClass: "bg-site-purple/20"
    },
    {
      number: "6",
      title: "Systemic Change",
      description: "Achieve sustainable transformation in AI funding patterns that prioritizes African needs, builds local capacity, and ensures equitable development.",
      outcomes: [
        "Equitable geographic distribution of AI funding",
        "Increased funding for African-led AI initiatives",
        "Strengthened local AI research and development capacity",
        "Sustainable funding ecosystem that reflects continental priorities"
      ],
      icon: <Globe className="h-12 w-12" />,
      colorClass: "text-site-sage",
      bgClass: "bg-site-sage/20"
    }
  ];

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Hero Section */}
      <section className="relative bg-slate-50 border-slate-200/50 overflow-hidden">
        <div className="relative max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            {/* Logo */}
            <div className="mb-4 animate-fadeInUp">
              <Image 
                src="/taifa-logo.png" 
                alt="TAIFA-FIALA Logo" 
                width={150} 
                height={150} 
                className="mx-auto" 
              />
            </div>
            
            <div className="inline-flex items-center px-4 py-2 bg-slate-600/10 border border-slate-600/20 rounded-full text-sm font-medium text-slate-600 mb-4 animate-fadeInUp">
            <Target className="h-4 w-4 mr-2" /> Systematic Change Framework
            </div>
            <h1 className="text-4xl md:text-6xl font-bold text-slate-700 mb-3 animate-fadeInUp leading-tight" style={{ animationDelay: '0.1s' }}>
              Theory of Change
            </h1>
            <p className="text-base md:text-lg text-slate-600/90 mb-6 max-w-4xl mx-auto animate-fadeInUp leading-relaxed" style={{ animationDelay: '0.2s' }}>
              Our comprehensive framework for transforming AI funding transparency and equity across Africa through systematic intervention, evidence-based advocacy, and sustainable capacity building.
            </p>
            
            {/* Key Principles */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-5xl mx-auto animate-fadeInUp" style={{ animationDelay: '0.3s' }}>
              <div className="bg-slate-600/10 backdrop-blur-sm p-4 rounded-2xl border border-slate-600/20">
                <Shield className="h-10 w-10 text-slate-600 mx-auto mb-2" />
                <div className="text-base font-bold text-slate-700 mb-1">Transparency</div>
                <div className="text-slate-600 text-xs">Open data and accountable processes</div>
              </div>
              <div className="bg-amber-600/10 backdrop-blur-sm p-4 rounded-2xl border border-amber-600/20">
                <Users className="h-10 w-10 text-amber-600 mx-auto mb-2" />
                <div className="text-base font-bold text-slate-700 mb-1">Equity</div>
                <div className="text-slate-600 text-xs">Fair distribution and inclusive access</div>
              </div>
              <div className="bg-site-brown/10 backdrop-blur-sm p-4 rounded-2xl border border-site-brown/20">
                <Globe className="h-10 w-10 text-site-brown mx-auto mb-2" />
                <div className="text-base font-bold text-slate-700 mb-1">Sustainability</div>
                <div className="text-slate-600 text-xs">Long-term systemic transformation</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Theory of Change Flow */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <div className="inline-flex items-center px-4 py-2 bg-slate-600/10 border border-slate-600/20 rounded-full text-sm font-medium text-slate-600 mb-6 animate-fadeInUp">
              <ArrowDown className="h-4 w-4 mr-2" />
              Strategic Pathway
            </div>
            <h2 className="text-4xl md:text-5xl font-bold text-slate-700 mb-6 leading-tight">
              Six-Stage Transformation Framework
            </h2>
            <p className="text-xl text-slate-600 max-w-4xl mx-auto leading-relaxed">
              Our theory of change outlines a systematic approach to achieving sustainable transformation in African AI funding patterns through evidence-based intervention and stakeholder engagement.
            </p>
          </div>

          {/* Stages Flow */}
          <div className="relative">
            {/* Connecting Line */}
            <div className="absolute left-8 top-10 bottom-10 w-1 bg-gradient-to-b from-slate-600 via-amber-600 via-site-brown via-site-teal via-site-purple to-site-sage rounded-full hidden md:block"></div>
            
            <div className="space-y-12">
              {stages.map((stage, index) => (
                <div 
                  key={stage.number} 
                  className="relative animate-fadeInUp" 
                  style={{ animationDelay: `${0.3 + index * 0.1}s` }}
                >
                  <div className="flex items-start gap-6">
                    {/* Stage Number */}
                    <div className="flex-shrink-0 relative z-10">
                      <div className={`w-16 h-16 ${stage.bgClass} rounded-full flex items-center justify-center border-4 border-white shadow-xl`}>
                        <span className={`text-2xl font-bold ${stage.colorClass}`}>{stage.number}</span>
                      </div>
                    </div>
                    
                    {/* Stage Content */}
                    <div className="flex-1 bg-white/80 backdrop-blur-sm rounded-3xl p-8 shadow-xl border border-slate-200/50 hover:shadow-2xl hover:-translate-y-1 transition-all duration-300">
                      <div className="flex items-start gap-6">
                        <div className={`w-16 h-16 ${stage.bgClass} rounded-2xl flex items-center justify-center border border-current border-opacity-20`}>
                          <div className={stage.colorClass}>
                            {stage.icon}
                          </div>
                        </div>
                        
                        <div className="flex-1">
                          <h3 className="text-2xl font-bold text-slate-700 mb-3">{stage.title}</h3>
                          <p className="text-slate-600 mb-6 leading-relaxed">{stage.description}</p>
                          
                          {/* Outcomes */}
                          <div className="space-y-3">
                            <h4 className="text-sm font-semibold text-slate-700 uppercase tracking-wide">Key Outcomes</h4>
                            <div className="grid md:grid-cols-2 gap-3">
                              {stage.outcomes.map((outcome, outcomeIndex) => (
                                <div key={outcomeIndex} className="flex items-start gap-3">
                                  <CheckCircle className={`h-5 w-5 ${stage.colorClass} flex-shrink-0 mt-0.5`} />
                                  <span className="text-sm text-slate-600 leading-relaxed">{outcome}</span>
                                </div>
                              ))}
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Impact Statement */}
          <div className="mt-20 text-center animate-fadeInUp" style={{ animationDelay: '0.9s' }}>
            <div className="bg-gradient-to-br from-slate-700 to-slate-600 p-12 rounded-3xl text-white shadow-2xl">
              <div className="w-20 h-20 bg-amber-600/20 rounded-full flex items-center justify-center mx-auto mb-6 border border-amber-600/50">
                <Heart className="h-10 w-10 text-amber-600" />
              </div>
              <h3 className="text-3xl font-bold mb-6" style={{ color: '#f97316' }}>Ultimate Vision</h3>
              <p className="text-xl text-amber-100 leading-relaxed max-w-4xl mx-auto">
                A transformed African AI ecosystem where funding flows transparently and equitably, 
                empowering local innovators and ensuring AI development serves all Africans, 
                not just a privileged few. This vision drives every aspect of our work and 
                guides our commitment to building a more just and inclusive future for African AI.
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
