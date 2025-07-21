'use client';

import Link from 'next/link';
import Image from 'next/image';
import { useState } from 'react';

const Navbar = () => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  return (
    <nav className="bg-taifa-light border-b border-gray-200 sticky top-0 z-50 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo and Title */}
          <div className="flex-shrink-0">
            <Link href="/" className="flex items-center">
              <Image
                src="/TAIFA-FIALA-Logo_transparent.png"
                width={60}
                height={30}
                alt="TAIFA-FIALA"
                className="mr-2"
              />
              <span className="text-2xl font-display font-semibold text-taifa-primary">TAIFA-FIALA</span>
            </Link>
          </div>
          
          {/* Navigation Links - Centered */}
          <div className="hidden md:flex items-center justify-center absolute left-1/2 transform -translate-x-1/2">
            <div className="flex space-x-8">
              <Link href="/funding-landscape" className="text-taifa-primary hover:text-taifa-accent text-sm font-medium nav-pill">
                Funding Landscape
              </Link>
              <Link href="/methodology" className="text-taifa-primary hover:text-taifa-accent text-sm font-medium nav-pill">
                Methodology
              </Link>
              <Link href="/about" className="text-taifa-primary hover:text-taifa-accent text-sm font-medium nav-pill">
                About Us
              </Link>
            </div>
          </div>
          
          {/* Language Toggle - Right-aligned */}
          <div className="flex-shrink-0">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2 text-sm">
                <button className="text-taifa-primary hover:text-taifa-secondary font-medium">EN</button>
                <span className="text-gray-400">|</span>
                <button className="text-taifa-primary hover:text-taifa-secondary">FR</button>
              </div>
              
              {/* Mobile menu button */}
              <div className="md:hidden">
                <button 
                  className="text-taifa-primary hover:text-taifa-secondary"
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
        <div className="md:hidden px-2 pt-2 pb-3 space-y-1 sm:px-3 bg-taifa-light border-b border-gray-200">
          <Link href="/funding-landscape" className="block px-3 py-2 rounded-md text-base font-medium text-taifa-primary hover:text-taifa-secondary">
            Funding Landscape
          </Link>
          <Link href="/methodology" className="block px-3 py-2 rounded-md text-base font-medium text-taifa-primary hover:text-taifa-secondary">
            Methodology
          </Link>
          <Link href="/about" className="block px-3 py-2 rounded-md text-base font-medium text-taifa-primary hover:text-taifa-secondary">
            About Us
          </Link>
        </div>
      )}
    </nav>
  );
};

export default Navbar;