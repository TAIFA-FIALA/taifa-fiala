import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import Link from "next/link";

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
  description: "Bilingual platform tracking AI funding opportunities across Africa. Fresh data daily, instant search.",
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
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        {/* Professional Navigation */}
        <nav className="bg-gradient-to-r from-blue-900 to-red-900 shadow-lg">
          <div className="container mx-auto px-4">
            <div className="flex justify-between items-center py-4">
              {/* TAIFA-FIALA Branding */}
              <Link href="/" className="flex items-center space-x-3">
                <div className="flex items-center">
                  <span className="text-2xl font-bold text-blue-100">TAIFA</span>
                  <span className="text-xl text-gray-300 mx-1">|</span>
                  <span className="text-2xl font-bold text-red-100">FIALA</span>
                </div>
                <div className="hidden md:block">
                  <div className="text-xs text-gray-300">Tracking AI Funding for Africa</div>
                  <div className="text-xs text-gray-400">Financement IA pour l'Afrique</div>
                </div>
              </Link>

              {/* Navigation Links */}
              <div className="hidden md:flex items-center space-x-6">
                <Link href="/funding" className="text-gray-200 hover:text-white transition-colors">
                  💰 Funding Opportunities
                </Link>
                <Link href="/organizations" className="text-gray-200 hover:text-white transition-colors">
                  🏢 Organizations
                </Link>
                <Link href="/rwanda-demo" className="text-gray-200 hover:text-white transition-colors">
                  🇷🇼 Rwanda Demo
                </Link>
                <div className="flex items-center space-x-2 text-sm">
                  <span className="text-gray-300">🌍</span>
                  <button className="text-gray-200 hover:text-white transition-colors">EN</button>
                  <span className="text-gray-400">|</span>
                  <button className="text-gray-400 hover:text-white transition-colors">FR</button>
                </div>
              </div>

              {/* Mobile Menu Button */}
              <div className="md:hidden">
                <button className="text-gray-200 hover:text-white">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </nav>

        {/* Main Content */}
        <main className="min-h-screen bg-gray-50">
          {children}
        </main>

        {/* Footer */}
        <footer className="bg-gray-800 text-gray-300 py-8">
          <div className="container mx-auto px-4">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div>
                <h3 className="text-lg font-bold text-white mb-3">TAIFA-FIALA</h3>
                <p className="text-sm">Democratizing access to AI funding across Africa through bilingual, real-time opportunity discovery.</p>
              </div>
              <div>
                <h4 className="font-semibold text-white mb-3">Platform</h4>
                <ul className="space-y-2 text-sm">
                  <li><Link href="/funding" className="hover:text-white">Search Funding</Link></li>
                  <li><Link href="/organizations" className="hover:text-white">Organizations</Link></li>
                  <li><Link href="/submit-opportunity" className="hover:text-white">Submit Opportunity</Link></li>
                </ul>
              </div>
              <div>
                <h4 className="font-semibold text-white mb-3">About</h4>
                <ul className="space-y-2 text-sm">
                  <li><a href="#" className="hover:text-white">Our Mission</a></li>
                  <li><a href="#" className="hover:text-white">API Access</a></li>
                  <li><a href="#" className="hover:text-white">Community</a></li>
                </ul>
              </div>
              <div>
                <h4 className="font-semibold text-white mb-3">Connect</h4>
                <ul className="space-y-2 text-sm">
                  <li><a href="https://github.com/drjforrest/taifa" className="hover:text-white">GitHub</a></li>
                  <li><a href="#" className="hover:text-white">Contact</a></li>
                  <li><span className="text-xs">44 Data Sources • Daily Updates</span></li>
                </ul>
              </div>
            </div>
            <div className="border-t border-gray-700 mt-6 pt-6 text-center text-sm">
              <p>&copy; 2025 TAIFA-FIALA. Supporting AI development across Africa. 🌍</p>
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
