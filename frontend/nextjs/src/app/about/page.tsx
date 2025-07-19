import React from 'react';
import { Mail, MapPin, Users, Calendar, ExternalLink } from 'lucide-react';
import Image from 'next/image';

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 to-orange-50">
      {/* Hero Section */}
      <section className="bg-white border-b border-gray-200">
        <div className="max-w-4xl mx-auto py-16 px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-6">
            About TAIFA-FIALA
          </h1>
          <p className="text-xl text-gray-700 leading-relaxed max-w-3xl mx-auto">
            An independent initiative promoting transparency, equity, and accountability in AI funding 
            across Africa. We apply advanced data analytics and research expertise to ensure AI development 
            serves all Africans, not just a privileged few.
          </p>
          <div className="mt-8 text-gray-600">
            <p className="text-lg">
              <strong>Mission:</strong> Preventing AI from perpetuating the same disparities as previous innovations 
              that promised much to Africans but failed to deliver equitably.
            </p>
          </div>
        </div>
      </section>

      {/* Leadership Team */}
      <section className="py-16">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Leadership Team</h2>
            <p className="text-gray-600">
              Combining African data analytics expertise with global research experience
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-12 max-w-5xl mx-auto">
            
            {/* Executive Director */}
            <div className="bg-white p-8 rounded-xl shadow-lg text-center">
              <div className="w-32 h-32 bg-amber-100 rounded-full mx-auto mb-6 flex items-center justify-center">
                <Users className="h-16 w-16 text-amber-700" />
              </div>
              
              <h3 className="text-xl font-bold text-gray-900 mb-2">Executive Director</h3>
              <div className="text-amber-700 font-medium mb-4">Africa Quantitative Sciences (AQS)</div>
              
              <p className="text-gray-700 leading-relaxed mb-6">
                Leading Africa Quantitative Sciences, Rwanda's premier data analytics firm, our Executive Director 
                brings extensive experience in transforming unstructured data into actionable insights across 
                African contexts. With a focus on public health outcomes and global health security, 
                they have pioneered innovative data-driven solutions that enhance vaccine and disease monitoring 
                while strengthening health systems across the continent. Their vision combines cutting-edge 
                technology with deep understanding of African operational realities.
              </p>
              
              <div className="flex justify-center items-center text-sm text-gray-500">
                <MapPin className="h-4 w-4 mr-1" />
                <span>Kigali, Rwanda</span>
              </div>
            </div>

            {/* Scientific Director */}
            <div className="bg-white p-8 rounded-xl shadow-lg text-center">
              <div className="w-32 h-32 bg-emerald-100 rounded-full mx-auto mb-6 flex items-center justify-center">
                <Users className="h-16 w-16 text-emerald-700" />
              </div>
              
              <h3 className="text-xl font-bold text-gray-900 mb-2">Dr. Jamie Forrest</h3>
              <div className="text-emerald-700 font-medium mb-4">Scientific Director</div>
              
              <p className="text-gray-700 leading-relaxed mb-6">
                Dr. Forrest holds a PhD in Population and Public Health and has dedicated their career to 
                addressing health and development challenges across Africa. With extensive experience living 
                and working in Rwanda for many years, and earlier career experience in South Africa, 
                they bring deep contextual understanding of African development dynamics. Their research 
                expertise in funding analysis and commitment to equity-driven innovation drives TAIFA-FIALA's 
                scientific approach to ensuring AI development serves all African communities.
              </p>
              
              <div className="flex justify-center items-center text-sm text-gray-500">
                <MapPin className="h-4 w-4 mr-1" />
                <span>Rwanda</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Initiative Background */}
      <section className="py-12 bg-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Why TAIFA-FIALA?</h2>
          <div className="bg-amber-50 p-8 rounded-xl border-l-4 border-amber-500">
            <p className="text-lg text-gray-800 leading-relaxed">
              History shows us that technological innovations often promise transformation for Africa 
              but frequently fail to deliver equitable benefits. From mobile banking to renewable energy, 
              we've seen how good intentions can perpetuate existing disparities. 
              <strong className="text-amber-800"> We founded TAIFA-FIALA to ensure AI doesn't repeat this pattern.</strong>
            </p>
            <p className="text-gray-700 mt-4">
              By combining rigorous data analytics with deep African experience, we track where AI funding 
              actually goes, who benefits, and whether promises translate to reality. Our goal is transparency 
              that enables truly inclusive AI development across the continent.
            </p>
          </div>
        </div>
      </section>

      {/* Coming Soon - Advisory Board */}
      <section className="py-16">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="bg-gradient-to-r from-amber-100 to-orange-100 p-8 rounded-xl border border-amber-200">
            <Calendar className="h-12 w-12 text-amber-700 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Coming Soon</h2>
            <h3 className="text-xl font-semibold text-amber-800 mb-3">Advisory Board</h3>
            <p className="text-gray-700 max-w-2xl mx-auto">
              We are assembling a distinguished advisory board of African AI researchers, policy makers, 
              and development practitioners to guide TAIFA-FIALA's strategic direction and ensure our 
              work serves the broader African AI ecosystem.
            </p>
            <div className="mt-6 text-sm text-amber-700 font-medium">
              Announcements forthcoming in Q4 2025
            </div>
          </div>
        </div>
      </section>

      {/* Contact & Collaboration */}
      <section className="py-16 bg-white border-t border-gray-200">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Contact & Collaboration</h2>
            <p className="text-gray-600 mb-6">
              Partner with us in building transparent, equitable AI development across Africa
            </p>
            
            {/* Funding Statement */}
            <div className="bg-amber-50 p-6 rounded-lg border-l-4 border-amber-500 max-w-3xl mx-auto mb-8">
              <p className="text-gray-800 leading-relaxed">
                <strong>TAIFA-FIALA is currently self-supporting.</strong> If you are interested in helping us 
                grow our reach and expand our platform to serve more African communities, 
                please get in touch with us below.
              </p>
            </div>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center p-6 bg-amber-50 rounded-lg">
              <Mail className="h-8 w-8 text-amber-700 mx-auto mb-3" />
              <h3 className="font-semibold text-gray-900 mb-2">General Inquiries</h3>
              <p className="text-gray-600 text-sm">
                Research partnerships and collaboration opportunities
              </p>
            </div>
            
            <div className="text-center p-6 bg-emerald-50 rounded-lg">
              <Users className="h-8 w-8 text-emerald-700 mx-auto mb-3" />
              <h3 className="font-semibold text-gray-900 mb-2">Grant Funding</h3>
              <p className="text-gray-600 text-sm">
                Supporting transparent AI development across Africa
              </p>
            </div>
            
            <div className="text-center p-6 bg-orange-50 rounded-lg">
              <ExternalLink className="h-8 w-8 text-orange-700 mx-auto mb-3" />
              <h3 className="font-semibold text-gray-900 mb-2">Data Access</h3>
              <p className="text-gray-600 text-sm">
                Academic and institutional research partnerships
              </p>
            </div>
          </div>

          <div className="mt-12 text-center">
            <div className="bg-gray-50 p-6 rounded-lg">
              <p className="text-sm text-gray-600 mb-2">
                <strong>Transparency Note:</strong> TAIFA-FIALA operates as an independent initiative.
              </p>
              <p className="text-xs text-gray-500">
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
