import Link from 'next/link';
import Image from 'next/image';

const Navbar = () => {
  return (
    <nav className="bg-scholarly-light border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo and Title */}
          <div className="flex items-center">
            <Link href="/" className="flex items-center">
              <span className="text-2xl font-serif text-scholarly-primary">TAIFA-FIALA</span>
            </Link>
          </div>
          
          {/* Navigation Links */}
          <div className="hidden md:flex items-center space-x-8">
            <Link href="/methodology" className="text-scholarly-primary hover:text-scholarly-secondary text-sm font-medium nav-pill">
              Methodology
            </Link>
            <Link href="/analytics" className="text-scholarly-primary hover:text-scholarly-secondary text-sm font-medium nav-pill">
              Data & Analysis
            </Link>
            <Link href="/publications" className="text-scholarly-primary hover:text-scholarly-secondary text-sm font-medium nav-pill">
              Publications
            </Link>
            <Link href="/funding" className="text-scholarly-primary hover:text-scholarly-secondary text-sm font-medium nav-pill">
              Funding Database
            </Link>
            <Link href="/about" className="text-scholarly-primary hover:text-scholarly-secondary text-sm font-medium nav-pill">
              About
            </Link>
          </div>
          
          {/* Language Toggle */}
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2 text-sm">
              <button className="text-scholarly-primary hover:text-scholarly-secondary font-medium">EN</button>
              <span className="text-gray-400">|</span>
              <button className="text-scholarly-primary hover:text-scholarly-secondary">FR</button>
            </div>
            
            {/* Mobile menu button */}
            <div className="md:hidden">
              <button className="text-scholarly-primary hover:text-scholarly-secondary">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;