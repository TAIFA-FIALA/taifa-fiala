import React from 'react';
import { Mail, MapPin, Users, Calendar, ExternalLink, Heart, Globe, Shield, Target, Award, Lightbulb } from 'lucide-react';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'About TAIFA-FIALA | Leadership & Mission',
  description: 'Learn about TAIFA-FIALA\'s mission to promote transparency, equity, and accountability in AI funding across Africa. Meet our leadership team and discover our vision for inclusive AI development.',
  keywords: ['TAIFA-FIALA', 'African AI', 'funding transparency', 'equity in technology', 'leadership team', 'AI development Africa'],
};

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-taifa-light via-white to-taifa-light">
      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-white via-taifa-light/30 to-white border-b border-gray-200/50 overflow-hidden">
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
              <Heart className="h-4 w-4 mr-2" />
              Our Story & Mission
            </div>
            
            <h1 className="text-6xl md:text-7xl font-bold text-taifa-primary mb-6 animate-fadeInUp leading-tight" style={{ animationDelay: '0.1s' }}>
              About
              <span className="block bg-gradient-to-r from-taifa-accent to-taifa-secondary bg-clip-text text-transparent">
                TAIFA-FIALA
              </span>
            </h1>
            
            <p className="text-xl md:text-2xl text-taifa-muted max-w-4xl mx-auto leading-relaxed animate-fadeInUp mb-8" style={{ animationDelay: '0.2s' }}>
              An <span className="font-semibold text-taifa-primary">independent initiative</span> promoting transparency, equity, and accountability in 
              <span className="font-semibold text-taifa-accent">AI funding across Africa</span>. We apply advanced data analytics and research expertise 
              to facilitate a vision where AI development serves all Africans, not just a privileged few.
            </p>
            
            {/* Mission Statement */}
            <div className="bg-gradient-to-r from-taifa-accent/10 to-taifa-secondary/10 p-8 rounded-2xl border border-taifa-accent/20 max-w-5xl mx-auto animate-fadeInUp" style={{ animationDelay: '0.3s' }}>
              <div className="flex items-center justify-center mb-4">
                <Target className="h-6 w-6 text-taifa-accent mr-3" />
                <span className="text-lg font-semibold text-taifa-primary">Our Mission</span>
              </div>
              <p className="text-lg text-taifa-muted leading-relaxed">
                Preventing AI development from perpetuating the same disparities as previous innovations 
                that promised much for Africans but failed to deliver equitably.
              </p>
            </div>
            
            {/* Core Values */}
            <div className="flex flex-wrap justify-center gap-8 mt-12 animate-fadeInUp" style={{ animationDelay: '0.4s' }}>
              <div className="text-center">
                <div className="w-16 h-16 bg-taifa-accent/10 rounded-full flex items-center justify-center mx-auto mb-3 border border-taifa-accent/20">
                  <Shield className="h-8 w-8 text-taifa-accent" />
                </div>
                <div className="text-sm font-semibold text-taifa-primary">Transparency</div>
              </div>
              <div className="text-center">
                <div className="w-16 h-16 bg-taifa-secondary/10 rounded-full flex items-center justify-center mx-auto mb-3 border border-taifa-secondary/20">
                  <Users className="h-8 w-8 text-taifa-secondary" />
                </div>
                <div className="text-sm font-semibold text-taifa-primary">Equity</div>
              </div>
              <div className="text-center">
                <div className="w-16 h-16 bg-taifa-olive/10 rounded-full flex items-center justify-center mx-auto mb-3 border border-taifa-olive/20">
                  <Award className="h-8 w-8 text-taifa-olive" />
                </div>
                <div className="text-sm font-semibold text-taifa-primary">Accountability</div>
              </div>
              <div className="text-center">
                <div className="w-16 h-16 bg-taifa-primary/10 rounded-full flex items-center justify-center mx-auto mb-3 border border-taifa-primary/20">
                  <Lightbulb className="h-8 w-8 text-taifa-primary" />
                </div>
                <div className="text-sm font-semibold text-taifa-primary">Innovation</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Leadership Team */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <div className="inline-flex items-center px-4 py-2 bg-taifa-primary/10 border border-taifa-primary/20 rounded-full text-sm font-medium text-taifa-primary mb-6 animate-fadeInUp">
              <Users className="h-4 w-4 mr-2" />
              Meet Our Team
            </div>
            <h2 className="text-4xl font-bold text-taifa-primary mb-4 animate-fadeInUp" style={{ animationDelay: '0.1s' }}>Leadership Team</h2>
            <p className="text-lg text-taifa-muted max-w-3xl mx-auto animate-fadeInUp" style={{ animationDelay: '0.2s' }}>
              Combining expertise in data science and a passion for local development that serves community needs.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-12 max-w-6xl mx-auto">
            
            {/* Executive Director */}
            <div className="bg-white/80 backdrop-blur-sm p-8 rounded-2xl shadow-xl border border-gray-200/50 text-center hover:shadow-2xl hover:-translate-y-2 transition-all duration-300 animate-fadeInUp" style={{ animationDelay: '0.3s' }}>
              <div className="w-32 h-32 bg-taifa-accent/10 border-2 border-taifa-accent/20 rounded-full mx-auto mb-6 flex items-center justify-center group-hover:scale-110 transition-transform">
                <Users className="h-16 w-16 text-taifa-accent" />
              </div>
              
              <h3 className="text-2xl font-bold text-taifa-primary mb-2">Hinda Ruton</h3>
              <div className="inline-block bg-taifa-accent/10 text-taifa-accent font-semibold px-4 py-2 rounded-full text-sm mb-6 border border-taifa-accent/20">Executive Director</div>
              
              <p className="text-taifa-muted leading-relaxed mb-6 text-left">
                Leading Africa Quantitative Sciences, Rwanda's premier data analytics firm, Hinda Ruton
                brings extensive experience in transforming unstructured data into actionable insights across 
                African contexts. With a focus on public health outcomes and global health security, 
                he has pioneered innovative data-driven solutions that enhance vaccine and disease monitoring 
                while strengthening health systems. His vision combines cutting-edge 
                technology with deep understanding of operational realities of African businesses and agencies and the needs of the local communities they serve.
              </p>
              
              <div className="flex justify-center items-center text-sm bg-taifa-accent/5 px-4 py-2 rounded-full border border-taifa-accent/20">
                <MapPin className="h-4 w-4 mr-2 text-taifa-accent" />
                <span className="text-taifa-primary font-medium">Kigali, Rwanda</span>
              </div>
            </div>

            {/* Scientific Director */}
            <div className="bg-white/80 backdrop-blur-sm p-8 rounded-2xl shadow-xl border border-gray-200/50 text-center hover:shadow-2xl hover:-translate-y-2 transition-all duration-300 animate-fadeInUp" style={{ animationDelay: '0.4s' }}>
              <div className="w-32 h-32 bg-taifa-secondary/10 border-2 border-taifa-secondary/20 rounded-full mx-auto mb-6 flex items-center justify-center group-hover:scale-110 transition-transform">
                <Users className="h-16 w-16 text-taifa-secondary" />
              </div>
              
              <h3 className="text-2xl font-bold text-taifa-primary mb-2">Dr. Jamie Forrest</h3>
              <div className="inline-block bg-taifa-secondary/10 text-taifa-secondary font-semibold px-4 py-2 rounded-full text-sm mb-6 border border-taifa-secondary/20">Scientific Director</div>
              
              <p className="text-taifa-muted leading-relaxed mb-6 text-left">
                Dr. Forrest holds a PhD in Population and Public Health and has dedicated his career to 
                addressing health and development challenges in African countries. With many years of living 
                and working in Rwanda, and earlier career experience in South Africa,  
                he brings deep contextual understanding of African development dynamics. His research interests and 
                expertise include digital health, clinical research, and equity-driven innovations like those driving TAIFA-FIALA's 
                scientific approach to holding AI development accountable for its promise to all Africans.
              </p>
              
              <div className="flex justify-center items-center text-sm bg-taifa-secondary/5 px-4 py-2 rounded-full border border-taifa-secondary/20">
                <MapPin className="h-4 w-4 mr-2 text-taifa-secondary" />
                <span className="text-taifa-primary font-medium">Canada / Rwanda</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Initiative Background */}
      <section className="py-20 bg-white/80 backdrop-blur-sm">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <div className="inline-flex items-center px-4 py-2 bg-taifa-olive/10 border border-taifa-olive/20 rounded-full text-sm font-medium text-taifa-olive mb-6 animate-fadeInUp">
              <Lightbulb className="h-4 w-4 mr-2" />
              Our Foundation
            </div>
            <h2 className="text-4xl font-bold text-taifa-primary mb-6 animate-fadeInUp" style={{ animationDelay: '0.1s' }}>Why TAIFA-FIALA?</h2>
          </div>
          
          <div className="bg-gradient-to-br from-taifa-olive/10 via-taifa-accent/5 to-taifa-secondary/10 p-10 rounded-2xl border border-taifa-olive/20 shadow-xl animate-fadeInUp" style={{ animationDelay: '0.2s' }}>
            <div className="max-w-4xl mx-auto">
              <p className="text-xl text-taifa-muted leading-relaxed mb-6">
                History shows us that technological innovations often promise transformation for Africa 
                but frequently fail to deliver the kind of equitable benefits that promise the tide to raise all boats. From mobile banking to renewable energy, 
                we've seen how good intentions can perpetuate existing disparities that are deeply rooted.
              </p>
              
              <div className="bg-white/60 backdrop-blur-sm p-6 rounded-xl border border-taifa-accent/20 mb-6">
                <p className="text-lg font-semibold text-taifa-primary">
                  We founded TAIFA-FIALA to ensure AI doesn't repeat this pattern.
                </p>
              </div>
              
              <p className="text-lg text-taifa-muted leading-relaxed">
                By combining rigorous data analytics with lived experience, we are setting out on an ambitious journey to track where AI funding comes from,
                where it actually goes, who benefits, and whether promises translate to reality. Our goal is transparency 
                that enables truly inclusive AI development across the continent.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Coming Soon - Advisory Board */}
      <section className="py-20">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="bg-gradient-to-br from-taifa-secondary/10 via-taifa-accent/5 to-taifa-olive/10 p-10 rounded-2xl border border-taifa-secondary/20 shadow-xl animate-fadeInUp">
            <div className="w-20 h-20 bg-taifa-secondary/10 rounded-full flex items-center justify-center mx-auto mb-6 border-2 border-taifa-secondary/20">
              <Calendar className="h-10 w-10 text-taifa-secondary" />
            </div>
            <div className="inline-block bg-taifa-secondary/10 text-taifa-secondary font-semibold px-4 py-2 rounded-full text-sm mb-4 border border-taifa-secondary/20">
              Coming Soon
            </div>
            <h2 className="text-3xl font-bold text-taifa-primary mb-4">Advisory Board</h2>
            <p className="text-lg text-taifa-muted max-w-3xl mx-auto leading-relaxed mb-6">
              We are assembling a distinguished advisory board of African AI researchers, policy makers, 
              and development practitioners to guide TAIFA-FIALA's strategic direction and ensure our
              work serves the broader African AI ecosystem.
            </p>
            <div className="inline-flex items-center px-6 py-3 bg-white/60 backdrop-blur-sm rounded-full border border-taifa-secondary/20">
              <Globe className="h-4 w-4 text-taifa-secondary mr-2" />
              <span className="text-taifa-primary font-medium">Announcements forthcoming</span>
            </div>
          </div>
        </div>
      </section>

      {/* Contact & Collaboration */}
      <section className="py-20 bg-gradient-to-br from-taifa-primary to-taifa-olive">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <div className="inline-flex items-center px-4 py-2 bg-white/20 border border-white/30 rounded-full text-sm font-medium text-white mb-6 animate-fadeInUp">
              <Mail className="h-4 w-4 mr-2" />
              Get In Touch
            </div>
            <h2 className="text-4xl font-bold text-white mb-6 animate-fadeInUp" style={{ animationDelay: '0.1s' }}>Contact & Collaboration</h2>
            <p className="text-xl text-taifa-orange mb-8 max-w-3xl mx-auto animate-fadeInUp" style={{ animationDelay: '0.2s' }}>
              Partner with us in building transparent, equitable AI development across Africa
            </p>
            
            {/* Funding Statement */}
            <div className="bg-white/10 backdrop-blur-sm p-8 rounded-2xl border border-white/20 max-w-4xl mx-auto mb-12 animate-fadeInUp" style={{ animationDelay: '0.3s' }}>
              <div className="flex items-center justify-center mb-4">
                <Heart className="h-6 w-6 text-taifa-orange mr-3" />
                <span className="text-lg font-semibold text-white">Self-Supporting Initiative</span>
              </div>
              <p className="text-taifa-primary leading-relaxed text-lg">
                <strong className="text-taifa-primary">TAIFA-FIALA is currently self-supporting.</strong> If you are interested in helping us 
                grow our reach and expand our platform to serve more African communities, 
                please get in touch with us below.
              </p>
            </div>
          </div>

          <div className="grid md:grid-cols-3 gap-8 animate-fadeInUp" style={{ animationDelay: '0.4s' }}>
            <div className="text-center p-8 bg-white/10 backdrop-blur-sm rounded-2xl border border-white/20 hover:bg-white/20 transition-all duration-300 hover:-translate-y-2">
              <div className="w-16 h-16 bg-taifa-accent/20 rounded-full flex items-center justify-center mx-auto mb-4 border border-taifa-accent/30">
                <Mail className="h-8 w-8 text-taifa-primary" />
              </div>
              <h3 className="font-semibold text-white mb-3 text-lg">General Inquiries</h3>
              <p className="text-taifa-primary text-sm leading-relaxed">
                Research partnerships and collaboration opportunities
              </p>
            </div>
            
            <div className="text-center p-8 bg-white/10 backdrop-blur-sm rounded-2xl border border-white/20 hover:bg-white/20 transition-all duration-300 hover:-translate-y-2">
              <div className="w-16 h-16 bg-taifa-secondary/20 rounded-full flex items-center justify-center mx-auto mb-4 border border-taifa-secondary/30">
                <Users className="h-8 w-8 text-taifa-primary" />
              </div>
              <h3 className="font-semibold text-white mb-3 text-lg">Grant Funding</h3>
              <p className="text-taifa-primary text-sm leading-relaxed">
                Supporting transparent AI development across Africa
              </p>
            </div>
            
            <div className="text-center p-8 bg-white/10 backdrop-blur-sm rounded-2xl border border-white/20 hover:bg-white/20 transition-all duration-300 hover:-translate-y-2">
              <div className="w-16 h-16 bg-taifa-olive/20 rounded-full flex items-center justify-center mx-auto mb-4 border border-taifa-olive/30">
                <ExternalLink className="h-8 w-8 text-taifa-primary" />
              </div>
              <h3 className="font-semibold text-white mb-3 text-lg">Data Access</h3>
              <p className="text-taifa-primary text-sm leading-relaxed">
                Academic and institutional research partnerships
              </p>
            </div>
          </div>

          <div className="mt-16 text-center animate-fadeInUp" style={{ animationDelay: '0.5s' }}>
            <div className="bg-white/10 backdrop-blur-sm p-8 rounded-2xl border border-white/20 max-w-4xl mx-auto">
              <div className="flex items-center justify-center mb-4">
                <Shield className="h-6 w-6 text-taifa-primary mr-3" />
                <span className="text-lg font-semibold text-white">Transparency Note</span>
              </div>
              <p className="text-taifa-primary leading-relaxed mb-4">
                <strong className="text-taifa-primary">TAIFA-FIALA operates as an independent initiative.</strong>
              </p>
              <p className="text-sm text-taifa-primary/80 leading-relaxed">
                Our funding sources and methodology are fully documented to ensure accountability 
                in our mission to promote transparency in African AI development.
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
