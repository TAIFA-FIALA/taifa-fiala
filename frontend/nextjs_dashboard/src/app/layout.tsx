import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import Link from "next/link";
import Image from "next/image"; // Import the Image component
import Navbar from "@/components/layout/Navbar";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "TAIFA-FIALA | AI Funding Tracker for Africa",
  description: "A platform tracking AI funding opportunities across Africa. Fresh data daily, semantic search, data visualizations.",
  keywords: "AI funding, Africa, Rwanda, grants, artificial intelligence, French, English, bilingual",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased bg-gray-100`}
      >
        <Navbar />
        <main className="min-h-screen">
          {children}
        </main>

        {/* Footer */}
        <footer className="bg-gray-900 text-gray-300 py-8">
          <div className="container mx-auto px-4">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div>
                <h3 className="text-lg font-bold text-navy mb-3">TAIFA-FIALA</h3>
                <p className="text-sm">Democratizing access to AI funding across Africa through bilingual, real-time opportunity discovery.</p>
              </div>
              <div>
                <h4 className="font-semibold text-navy mb-3">Platform</h4>
                <ul className="space-y-2 text-sm">
                  <li><Link href="/funding" className="hover:text-yellow-300 transition-colors duration-300 ease-in-out">Search Funding</Link></li>
                  <li><Link href="/organizations" className="hover:text-yellow-300 transition-colors duration-300 ease-in-out">Organizations</Link></li>
                  <li><Link href="/submit-opportunity" className="hover:text-yellow-300 transition-colors duration-300 ease-in-out">Submit Opportunity</Link></li>
                </ul>
              </div>
              <div>
                <h4 className="font-semibold text-white mb-3">About</h4>
                <ul className="space-y-2 text-sm">
                  <li><Link href="/about" className="hover:text-yellow-300 transition-colors duration-300 ease-in-out">Our Mission</Link></li>
                  <li><Link href="/about#roadmap" className="hover:text-yellow-300 transition-colors duration-300 ease-in-out">Roadmap</Link></li>
                  <li><Link href="/about#contact" className="hover:text-yellow-300 transition-colors duration-300 ease-in-out">Contact Us</Link></li>
                </ul>
              </div>
              <div>
                <h4 className="font-semibold text-white mb-3">Connect</h4>
                <ul className="space-y-2 text-sm">
                  <li><a href="https://github.com/drjforrest/taifa" className="hover:text-yellow-300 transition-colors duration-300 ease-in-out">GitHub</a></li>
                  <li><Link href="/about#contact" className="hover:text-yellow-300 transition-colors duration-300 ease-in-out">Contact</Link></li>
                  <li><span className="text-xs">44 Data Sources • Daily Updates</span></li>
                </ul>
              </div>
            </div>
            <div className="border-t border-gray-700 mt-6 pt-6 text-center text-sm">
              <p>&copy; 2025 TAIFA-FIALA. Supporting AI development across Africa.</p>
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
