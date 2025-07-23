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
      icon: <BarChart3 className="h-8 w-8" />,
      colorClass: "text-taifa-primary",
      bgClass: "bg-taifa-primary/10"
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
      icon: <Lightbulb className="h-8 w-8" />,
      colorClass: "text-taifa-secondary",
      bgClass: "bg-taifa-secondary/10"
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
      icon: <Users className="h-8 w-8" />,
      colorClass: "text-taifa-accent",
      bgClass: "bg-taifa-accent/10"
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
      icon: <TrendingUp className="h-8 w-8" />,
      colorClass: "text-taifa-olive",
      bgClass: "bg-taifa-olive/10"
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
      icon: <Shield className="h-8 w-8" />,
      colorClass: "text-taifa-primary",
      bgClass: "bg-taifa-primary/10"
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
      icon: <Globe className="h-8 w-8" />,
      colorClass: "text-taifa-secondary",
      bgClass: "bg-taifa-secondary/10"
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-taifa-yellow/5 via-white to-taifa-secondary/5">
      {/* Hero Section */}
      <header className="bg-taifa-yellow relative overflow-hidden">
        <div className="absolute inset-0 bg-black/10"></div>
        <div className="relative max-w-7xl mx-auto py-20 px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            {/* Logo */}
            <div className="mb-8 animate-fadeInUp">
              <Image 
                src="/taifa-logo.png" 
                alt="TAIFA-FIALA Logo" 
                width={120} 
                height={120} 
                className="mx-auto" 
              />
            </div>
            
            <div className="inline-flex items-center px-4 py-2 bg-white/20 border border-taifa-primary/30 rounded-full text-sm font-medium text-white mb-6 animate-fadeInUp" style={{ animationDelay: '0.075s' }}>
              <Target className="h-4 w-4 mr-2" />
              Strategic Framework
            </div>
            <h1 className="text-5xl md:text-6xl font-bold text-taifa-primary mb-6 animate-fadeInUp" style={{ animationDelay: '0.1s' }}>
              Theory of
              <span className="block text-taifa-yellow">Change</span>
            </h1>
            <p className="text-xl text-taifa-yellow mb-8 max-w-4xl mx-auto animate-fadeInUp" style={{ animationDelay: '0.2s' }}>
              Our comprehensive framework for transforming AI funding transparency and equity across Africa through systematic intervention and capacity building
            </p>
            
            {/* Key Principles */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto animate-fadeInUp" style={{ animationDelay: '0.3s' }}>
              <div className="bg-white/10 backdrop-blur-sm p-6 rounded-2xl border border-white/20">
                <Shield className="h-8 w-8 text-taifa-yellow mx-auto mb-3" />
                <div className="text-lg font-bold text-white mb-2">Transparency</div>
                <div className="text-taifa-yellow text-sm">Open data and accountable processes</div>
              </div>
              <div className="bg-white/10 backdrop-blur-sm p-6 rounded-2xl border border-white/20">
                <Users className="h-8 w-8 text-taifa-yellow mx-auto mb-3" />
                <div className="text-lg font-bold text-white mb-2">Equity</div>
                <div className="text-taifa-yellow text-sm">Fair distribution and inclusive access</div>
              </div>
              <div className="bg-white/10 backdrop-blur-sm p-6 rounded-2xl border border-white/20">
                <Globe className="h-8 w-8 text-taifa-yellow mx-auto mb-3" />
                <div className="text-lg font-bold text-white mb-2">Sustainability</div>
                <div className="text-taifa-yellow text-sm">Long-term systemic transformation</div>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Theory of Change Flow */}
      <section className="py-20">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <div className="inline-flex items-center px-4 py-2 bg-taifa-secondary/10 border border-taifa-secondary/20 rounded-full text-sm font-medium text-taifa-secondary mb-6 animate-fadeInUp">
              <ArrowDown className="h-4 w-4 mr-2" />
              Strategic Pathway
            </div>
            <h2 className="text-4xl font-bold text-taifa-primary mb-4 animate-fadeInUp" style={{ animationDelay: '0.1s' }}>
              Our Theory of Change
            </h2>
            <p className="text-lg text-taifa-muted max-w-3xl mx-auto animate-fadeInUp" style={{ animationDelay: '0.2s' }}>
              A systematic approach to creating lasting change in African AI funding through evidence-based intervention
            </p>
          </div>

          {/* Stages Flow */}
          <div className="relative">
            {/* Connecting Line */}
            <div className="absolute left-8 top-16 bottom-16 w-1 bg-gradient-to-b from-taifa-primary via-taifa-secondary to-taifa-olive rounded-full hidden md:block"></div>
            
            <div className="space-y-12">
              {stages.map((stage, index) => (
                <div 
                  key={stage.number} 
                  className="relative animate-fadeInUp" 
                  style={{ animationDelay: `${0.3 + index * 0.1}s` }}
                >
                  <div className="flex items-start gap-8">
                    {/* Stage Number */}
                    <div className="flex-shrink-0 relative z-10">
                      <div className={`w-16 h-16 ${stage.bgClass} rounded-full flex items-center justify-center border-4 border-white shadow-xl`}>
                        <span className={`text-2xl font-bold ${stage.colorClass}`}>{stage.number}</span>
                      </div>
                    </div>
                    
                    {/* Stage Content */}
                    <div className="flex-1 bg-white/80 backdrop-blur-sm rounded-3xl p-8 shadow-xl border border-taifa-secondary/10 hover:shadow-2xl hover:-translate-y-1 transition-all duration-300">
                      <div className="flex items-start gap-6">
                        <div className={`w-16 h-16 ${stage.bgClass} rounded-2xl flex items-center justify-center border border-taifa-secondary/20`}>
                          <div className={stage.colorClass}>
                            {stage.icon}
                          </div>
                        </div>
                        
                        <div className="flex-1">
                          <h3 className="text-2xl font-bold text-taifa-primary mb-3">{stage.title}</h3>
                          <p className="text-taifa-muted mb-6 leading-relaxed">{stage.description}</p>
                          
                          {/* Outcomes */}
                          <div className="space-y-3">
                            <h4 className="text-sm font-semibold text-taifa-secondary uppercase tracking-wide">Key Outcomes</h4>
                            <div className="grid md:grid-cols-2 gap-3">
                              {stage.outcomes.map((outcome, outcomeIndex) => (
                                <div key={outcomeIndex} className="flex items-start gap-3">
                                  <CheckCircle className="h-5 w-5 text-taifa-accent flex-shrink-0 mt-0.5" />
                                  <span className="text-sm text-taifa-muted leading-relaxed">{outcome}</span>
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
            <div className="bg-gradient-to-br from-taifa-primary to-taifa-olive p-12 rounded-3xl text-white shadow-2xl">
              <div className="w-20 h-20 bg-white/20 rounded-full flex items-center justify-center mx-auto mb-6 border border-white/30">
                <Heart className="h-10 w-10 text-white" />
              </div>
              <h3 className="text-3xl font-bold mb-6">Ultimate Vision</h3>
              <p className="text-xl text-taifa-yellow leading-relaxed max-w-4xl mx-auto">
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
