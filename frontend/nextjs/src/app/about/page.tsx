'use client';

import React, { useState } from 'react';
import { Globe, Scale, Search } from 'lucide-react';

// About Us page component
export default function AboutPage() {
  // Form state
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    organization: '',
    message: '',
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState(false);

  // Handle form input changes
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    // Simulate form submission
    // In a real implementation, this would be an API call
    setTimeout(() => {
      setIsSubmitting(false);
      setSubmitSuccess(true);
      setFormData({
        name: '',
        email: '',
        organization: '',
        message: '',
      });
      
      // Reset success message after 5 seconds
      setTimeout(() => setSubmitSuccess(false), 5000);
    }, 1500);
  };

  return (
    <div className="bg-gray-50 min-h-screen">
      {/* Hero section */}
      <section className="bg-gradient-to-r from-blue-900 to-red-900 text-white py-16">
        <div className="container mx-auto px-4">
          <h1 className="text-4xl font-bold mb-4 text-center">About TAIFA-FIALA</h1>
          <p className="text-xl text-center max-w-3xl mx-auto">
            Democratizing AI funding access across Africa through transparency, 
        and accountability in AI funding.
          </p>
        </div>
      </section>

      {/* Mission section */}
      <section className="py-16 bg-white">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-3xl font-bold mb-6 text-center">Our Mission</h2>
            <div className="prose lg:prose-lg mx-auto">
              <p className="mb-4">
                TAIFA-FIALA (Tracking AI Funding for Africa - Financement Pour L'intelligence Artificielle en Afrique) 
                is a community-driven membership organization and digital platform dedicated to democratizing 
                funding for artificial intelligence research and implementation in African countries.
              </p>
              <p className="mb-4">
                We are a group of passionate African researchers, technologists, and advocates committed to 
                increasing African representation in global AI through principles of equity, accountability, 
                and transparency on the part of donors, investors, grantees, and entrepreneurs.
              </p>
              <p className="mb-4">
                Our platform serves as the central hub for AI funding opportunities in Africa, bringing together 
                researchers, startups, funders, and implementers in a collaborative ecosystem. We leverage advanced 
                data collection technologies and human expertise to ensure high-quality, relevant, and timely 
                information for the African AI community.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Vision section with cards */}
      <section className="py-16 bg-gray-50">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold mb-12 text-center">Our Vision</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="text-blue-800 mb-4">
                <Globe className="w-12 h-12" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Geographic Equity</h3>
              <p className="text-gray-600">
                Ensuring AI funding reaches all African regions, not just the top four countries 
                that currently receive 83% of investments.
              </p>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="text-blue-800 mb-4">
                <Scale className="w-12 h-12" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Inclusive Access</h3>
              <p className="text-gray-600">
                Creating pathways for underrepresented groups, particularly women who currently 
                receive only 2% of AI funding in Africa.
              </p>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="text-blue-800 mb-4">
                <Search className="w-12 h-12" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Transparency</h3>
              <p className="text-gray-600">
                Bringing clarity to funding processes through comprehensive data collection, 
                analysis, and community-driven accountability.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Roadmap section */}
      <section id="roadmap" className="py-16 bg-white">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-3xl font-bold mb-6 text-center">Our Roadmap</h2>
            <div className="space-y-6">
              <div className="border-l-4 border-blue-800 pl-4">
                <h3 className="text-xl font-semibold">Enhanced Geographic Equity Features</h3>
                <p className="text-gray-600 mt-2">
                  Real-time visualization of funding concentration, opportunity amplification for 
                  neglected regions, and language expansion beyond French/English to include 
                  Portuguese, Arabic, and Swahili.
                </p>
              </div>
              
              <div className="border-l-4 border-blue-800 pl-4">
                <h3 className="text-xl font-semibold">Sectoral Alignment Dashboard</h3>
                <p className="text-gray-600 mt-2">
                  Dedicated tracking for underserved sectors like healthcare (5.8% of funding), 
                  agriculture (3.9%), and climate AI (1.3%), with impact potential metrics aligned to 
                  AU development goals and SDGs.
                </p>
              </div>
              
              <div className="border-l-4 border-blue-800 pl-4">
                <h3 className="text-xl font-semibold">Gender and Inclusion Analytics</h3>
                <p className="text-gray-600 mt-2">
                  Highlighting funding for women-led initiatives, providing inclusive application resources,
                  and featuring success stories from female and youth AI entrepreneurs.
                </p>
              </div>
              
              <div className="border-l-4 border-blue-800 pl-4">
                <h3 className="text-xl font-semibold">Funding Lifecycle Support</h3>
                <p className="text-gray-600 mt-2">
                  Stage-appropriate matching for projects, consortium building features to help 
                  smaller entities access larger grants, and post-award tracking to build evidence 
                  for future applications.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Contact section */}
      <section id="contact" className="py-16 bg-gray-100">
        <div className="container mx-auto px-4">
          <div className="max-w-3xl mx-auto bg-white rounded-lg shadow-lg p-8">
            <h2 className="text-3xl font-bold mb-6 text-center">Get in Touch</h2>
            <p className="text-center mb-8 text-gray-600">
              Have questions or want to collaborate with us? Send us a message and we'll get back to you.
            </p>
            
            {submitSuccess ? (
              <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-6">
                Thank you for your message! We'll get back to you soon.
              </div>
            ) : null}
            
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
                    Your Name
                  </label>
                  <input
                    type="text"
                    id="name"
                    name="name"
                    value={formData.name}
                    onChange={handleChange}
                    required
                    className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-800 focus:border-blue-800"
                  />
                </div>
                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                    Email Address
                  </label>
                  <input
                    type="email"
                    id="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    required
                    className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-800 focus:border-blue-800"
                  />
                </div>
              </div>
              
              <div>
                <label htmlFor="organization" className="block text-sm font-medium text-gray-700 mb-1">
                  Organization (optional)
                </label>
                <input
                  type="text"
                  id="organization"
                  name="organization"
                  value={formData.organization}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-800 focus:border-blue-800"
                />
              </div>
              
              <div>
                <label htmlFor="message" className="block text-sm font-medium text-gray-700 mb-1">
                  Your Message
                </label>
                <textarea
                  id="message"
                  name="message"
                  rows={4}
                  value={formData.message}
                  onChange={handleChange}
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-800 focus:border-blue-800"
                ></textarea>
              </div>
              
              <div className="flex justify-center">
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-6 py-3 bg-gradient-to-r from-blue-800 to-red-800 text-white font-medium rounded-md hover:opacity-90 transition-opacity disabled:opacity-70"
                >
                  {isSubmitting ? 'Sending...' : 'Send Message'}
                </button>
              </div>
            </form>
          </div>
        </div>
      </section>
    </div>
  );
}
