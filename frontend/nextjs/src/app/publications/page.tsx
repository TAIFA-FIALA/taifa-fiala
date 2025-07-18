import Link from 'next/link';
import { FileText, Book, Shield } from 'lucide-react';

import React from 'react';

// Toggle this flag to true when ready to display publications
const PUBLICATIONS_ENABLED = false;

interface Link {
  text: string;
  href: string;
}

interface PublicationCardProps {
  title: string;
  authors: string;
  abstract: string;
  links: Link[];
  type: 'paper' | 'brief' | 'report';
}

const PublicationCard: React.FC<PublicationCardProps> = ({ title, authors, abstract, links, type }) => (
  <div className="border border-gray-200 rounded-lg p-6 mb-6">
    <div className="flex items-center mb-3">
      {type === 'paper' && <FileText className="h-5 w-5 text-blue-700 mr-3" />}
      {type === 'brief' && <Book className="h-5 w-5 text-green-700 mr-3" />}
      {type === 'report' && <Shield className="h-5 w-5 text-purple-700 mr-3" />}
      <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
    </div>
    <p className="text-sm text-gray-600 mb-3">{authors}</p>
    <p className="text-sm text-gray-700 mb-4">{abstract}</p>
    <div className="flex flex-wrap gap-4 text-sm">
      {links.map(link => (
        <Link key={link.href} href={link.href} className="text-blue-700 hover:underline">
          {link.text}
        </Link>
      ))}
    </div>
  </div>
);

export default function PublicationsPage() {
  const publications = {
    papers: [
      {
        title: "Geographic Disparities in AI Funding Across Africa: A Longitudinal Analysis (2019-2024)",
        authors: "TAIFA-FIALA Research Team",
        abstract: "This paper examines the concentration of AI funding in select African countries and its implications for continental development, revealing significant disparities that correlate with existing economic and infrastructure gaps.",
        links: [
          { text: "Full Paper (PDF)", href: "/publications/geographic-disparities-2024.pdf" },
          { text: "Dataset", href: "/data/geographic-disparities-dataset" },
          { text: "Replication Code", href: "/code/geographic-analysis" },
        ],
        type: 'paper'
      }
    ],
    briefs: [
      {
        title: "Policy Brief: Addressing the AI Funding Gap in Central Africa",
        authors: "December 2024",
        abstract: "Key recommendations for development partners and policymakers on addressing the severe underfunding of AI initiatives in Central African nations, based on our comprehensive 5-year analysis.",
        links: [
          { text: "Download Brief (PDF)", href: "/publications/policy-brief-central-africa.pdf" },
        ],
        type: 'brief'
      }
    ],
    reports: [
       {
        title: "Technical Report: Data Collection and Verification Methodology",
        authors: "TAIFA-FIALA Methods Group",
        abstract: "A detailed account of the automated data collection pipeline, manual verification protocols, and data quality assessment framework used in the TAIFA-FIALA research initiative.",
        links: [
          { text: "Read Report (PDF)", href: "/publications/technical-report-methodology.pdf" },
        ],
        type: 'report'
      }
    ]
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Page Header */}
      <header className="bg-gray-50 border-b border-gray-200">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <h1 className="text-3xl font-serif text-gray-900">
            Research Outputs
          </h1>
        </div>
      </header>

      {/* Main Content */}
      <main className="py-8">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          
          {PUBLICATIONS_ENABLED ? (
            <>
              <section id="papers">
                <h2 className="text-2xl font-serif text-gray-900 mb-6 border-b pb-2">Peer-Reviewed Papers</h2>
                {publications.papers.map(pub => <PublicationCard key={pub.title} {...pub as PublicationCardProps} />)}
              </section>

              <section id="briefs" className="mt-12">
                <h2 className="text-2xl font-serif text-gray-900 mb-6 border-b pb-2">Policy Briefs</h2>
                {publications.briefs.map(pub => <PublicationCard key={pub.title} {...pub as PublicationCardProps} />)}
              </section>

              <section id="reports" className="mt-12">
                <h2 className="text-2xl font-serif text-gray-900 mb-6 border-b pb-2">Technical Reports</h2>
                {publications.reports.map(pub => <PublicationCard key={pub.title} {...pub as PublicationCardProps} />)}
              </section>
            </>
          ) : (
            <div className="py-12 text-center">
              <p className="text-lg text-gray-600">Research publications coming soon.</p>
            </div>
          )}

        </div>
      </main>
    </div>
  );
}