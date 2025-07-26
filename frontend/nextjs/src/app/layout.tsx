import type { Metadata } from "next";
import { Lora, Inter } from "next/font/google";
import "./globals.css";
import Link from "next/link";
import Navbar from "@/components/layout/Navbar";

const lora = Lora({
  variable: "--font-lora",
  subsets: ["latin"],
  display: "swap",
});

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  display: "swap",
});

// Metadata removed from layout - should be defined in individual pages to avoid Next.js 14 conflicts

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${lora.variable} ${inter.variable} bg-gray-100 antialiased`}
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
                <p className="text-sm">Democratizing access to AI funding across Africa through data-driven transparency, equity and accountability.</p>
              </div>
              <div>
                <h4 className="font-semibold text-navy mb-3">Platform</h4>
                <ul className="space-y-2 text-sm">
                  <li><Link href="/funding" className="hover:text-taifa-orange transition-colors duration-300 ease-in-out">Search Funding</Link></li>
                  <li><Link href="/organizations" className="hover:text-taifa-orange transition-colors duration-300 ease-in-out">Organizations</Link></li>
                  <li><Link href="/submit-opportunity" className="hover:text-taifa-orange transition-colors duration-300 ease-in-out">Submit Opportunity</Link></li>
                </ul>
              </div>
              <div>
                <h4 className="font-semibold text-white mb-3">About</h4>
                <ul className="space-y-2 text-sm">
                  <li><Link href="/about" className="hover:text-taifa-orange transition-colors duration-300 ease-in-out">Our Mission</Link></li>
                  <li><Link href="/about#roadmap" className="hover:text-taifa-orange transition-colors duration-300 ease-in-out">Roadmap</Link></li>
                  <li><Link href="/about#contact" className="hover:text-taifa-orange transition-colors duration-300 ease-in-out">Contact Us</Link></li>
                </ul>
              </div>
              <div>
                <h4 className="font-semibold text-white mb-3">Connect</h4>
                <ul className="space-y-2 text-sm">
                  <li><a href="https://github.com/taifa-fiala" className="hover:text-taifa-orange transition-colors duration-300 ease-in-out">GitHub</a></li>
                  <li><Link href="/about#contact" className="hover:text-taifa-orange transition-colors duration-300 ease-in-out">Contact</Link></li>
                  <li><span className="text-xs">New Updates • Daily</span></li>
                </ul>
              </div>
            </div>
            <div className="border-t border-gray-700 mt-6 pt-6 text-center text-sm">
              <p>&copy; 2025 TAIFA-FIALA. Supporting Equitable AI development across Africa.</p>
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
