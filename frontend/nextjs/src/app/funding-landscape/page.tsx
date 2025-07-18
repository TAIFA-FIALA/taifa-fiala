import Link from 'next/link';
import { Map, Lightbulb, Briefcase, Landmark, Building } from 'lucide-react';

import React from 'react';

interface FunderCategoryProps {
  title: string;
  icon: React.ReactNode;
  children: React.ReactNode;
}

const FunderCategory: React.FC<FunderCategoryProps> = ({ title, icon, children }) => (
  <div>
    <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
      {icon}
      {title}
    </h3>
    <div className="space-y-3 text-sm text-gray-700">
      {children}
    </div>
  </div>
);

interface PatternProps {
  title: string;
  description: string;
  evidenceLink: string;
}

const Pattern: React.FC<PatternProps> = ({ title, description, evidenceLink }) => (
  <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
    <h4 className="font-semibold text-gray-800 mb-2">{title}</h4>
    <p className="text-sm text-gray-700 mb-3">{description}</p>
    <Link href={evidenceLink} className="text-sm text-blue-700 hover:underline">
      View supporting data →
    </Link>
  </div>
);

export default function FundingLandscapePage() {
  return (
    <div className="min-h-screen bg-white">
      {/* Page Header */}
      <header className="bg-gray-50 border-b border-gray-200">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <h1 className="text-3xl font-serif text-gray-900">
            Understanding the AI Funding Ecosystem
          </h1>
        </div>
      </header>

      {/* Main Content */}
      <main className="py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          
          {/* Ecosystem Map */}
          <section className="mb-12">
            <h2 className="text-2xl font-serif text-gray-900 mb-6">Ecosystem Map: Funder Categories</h2>
            <div className="grid md:grid-cols-3 gap-8">
              <FunderCategory title="Development Finance Institutions" icon={<Landmark className="mr-3 h-5 w-5 text-blue-700" />}>
                <p>African Development Bank (AfDB)</p>
                <p>World Bank Group (IDA, IFC)</p>
                <p>European Investment Bank (EIB)</p>
              </FunderCategory>
              <FunderCategory title="Bilateral & Multilateral Agencies" icon={<Briefcase className="mr-3 h-5 w-5 text-blue-700" />}>
                <p>USAID / Prosper Africa</p>
                <p>GIZ (Germany)</p>
                <p>Agence Française de Développement (AFD)</p>
                <p>Foreign, Commonwealth & Development Office (FCDO, UK)</p>
              </FunderCategory>
              <FunderCategory title="Private & Philanthropic Foundations" icon={<Building className="mr-3 h-5 w-5 text-blue-700" />}>
                <p>Bill & Melinda Gates Foundation</p>
                <p>Mastercard Foundation</p>
                <p>Google.org / Google for Startups</p>
                <p>Schmidt Futures</p>
              </FunderCategory>
            </div>
          </section>

          {/* Funding Patterns */}
          <section>
            <h2 className="text-2xl font-serif text-gray-900 mb-6">Observed Funding Patterns</h2>
            <div className="grid md:grid-cols-2 gap-6">
              <Pattern 
                title="Partnership-to-Funding Pipeline"
                description="Analysis of 347 partnership announcements shows 72% result in formal funding programs within 180 days."
                evidenceLink="/data/patterns/partnership-pipeline"
              />
              <Pattern 
                title="Consortium-Based Granting"
                description="A growing trend where multiple funders pool resources for large-scale, multi-country AI research grants, often requiring academic-private partnerships."
                evidenceLink="/data/patterns/consortium-grants"
              />
               <Pattern 
                title="Local Tech Hub Intermediation"
                description="International funders increasingly channel funds through established local tech hubs and innovation centers to de-risk investments and leverage local networks."
                evidenceLink="/data/patterns/tech-hub-intermediation"
              />
               <Pattern 
                title="Data-for-Funding Swaps"
                description="Emerging pattern where access to proprietary or public-sector datasets is used as a component of counterpart funding from AI firms."
                evidenceLink="/data/patterns/data-for-funding"
              />
            </div>
          </section>

        </div>
      </main>
    </div>
  );
}