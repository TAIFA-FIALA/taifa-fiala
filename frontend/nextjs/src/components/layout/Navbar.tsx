'use client';

import Link from 'next/link';
import Image from 'next/image';
import { useState } from 'react';

const Navbar = () => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  return (
    <nav className="bg-white border-b border-slate-200 sticky top-0 z-50 shadow-sm">
      <div className="max-w-7xl mx-auto px-6 sm:px-8 lg:px-10">
        <div className="flex items-center h-20">
          {/* Logo and Title */}
          <div className="flex-shrink-0 min-w-0">
            <Link href="/" className="flex items-center">
              <Image
                src="/taifa-logo.png"
                width={60}
                height={30}
                alt="TAIFA-FIALA"
                className="mr-2"
              />
              <span className="text-xl font-display font-semibold text-slate-800 whitespace-nowrap">TAIFA-FIALA</span>
            </Link>
          </div>
          
          {/* Navigation Links - Centered */}
          <div className="hidden md:flex items-center justify-center flex-1 mx-8">
            <div className="flex space-x-10">
              <Link href="/funding-landscape" className="text-slate-700 hover:text-amber-600 text-base font-medium nav-pill px-3 py-2 rounded-lg transition-colors">
                Funding Landscape
              </Link>
              <Link href="/theory-of-change" className="text-slate-700 hover:text-amber-600 text-base font-medium nav-pill px-3 py-2 rounded-lg transition-colors">
                Theory of Change
              </Link>
              <Link href="/methodology" className="text-slate-700 hover:text-amber-600 text-base font-medium nav-pill px-3 py-2 rounded-lg transition-colors">
                Methodology
              </Link>
              <Link href="/about" className="text-slate-700 hover:text-amber-600 text-base font-medium nav-pill px-3 py-2 rounded-lg transition-colors">
                About Us
              </Link>
            </div>
          </div>
          
          {/* Language Toggle - Right-aligned */}
          <div className="flex-shrink-0">
            <div className="flex items-center space-x-6">
              <div className="flex items-center space-x-3 text-base">
                <button className="text-slate-700 hover:text-amber-600 font-medium px-2 py-1 rounded transition-colors">EN</button>
                <span className="text-slate-400">|</span>
                <button className="text-slate-700 hover:text-amber-600 px-2 py-1 rounded transition-colors">FR</button>
              </div>
              
              {/* Mobile menu button */}
              <div className="md:hidden">
                <button 
                  className="text-slate-700 hover:text-amber-600"
                  onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Mobile menu, show/hide based on menu state */}
      {isMobileMenuOpen && (
        <div className="md:hidden px-4 pt-4 pb-6 space-y-2 sm:px-6 bg-white border-b border-slate-200">
          <Link href="/funding-landscape" className="block px-4 py-3 rounded-lg text-lg font-medium text-slate-700 text-center hover:text-amber-600 hover:bg-amber-50 transition-colors">
            Funding Landscape
          </Link>
          <Link href="/theory-of-change" className="block px-4 py-3 rounded-lg text-lg font-medium text-slate-700 text-center hover:text-amber-600 hover:bg-amber-50 transition-colors">
            Theory of Change
          </Link>
          <Link href="/methodology" className="block px-4 py-3 rounded-lg text-lg font-medium text-slate-700 text-center hover:text-amber-600 hover:bg-amber-50 transition-colors">
            Methodology
          </Link>
          <Link href="/about" className="block px-4 py-3 rounded-lg text-lg font-medium text-slate-700 text-center hover:text-amber-600 hover:bg-amber-50 transition-colors">
            About Us
          </Link>
        </div>
      )}
    </nav>
  );
};

export default Navbar;