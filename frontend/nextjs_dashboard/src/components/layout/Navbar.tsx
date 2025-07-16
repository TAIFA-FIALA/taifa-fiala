import Link from 'next/link';
import Image from 'next/image';

const Navbar = () => {
  return (
    <nav className="bg-gradient-to-b from-dark-gray-100 from-50% to-navy to-50% relative mb-0">
      {/* Logo positioned to hang below */}
      <div className="absolute left-10 bottom-0 transform translate-y-1/3 z-10">
        <Link href="/">
          <Image
            src="/TAIFA-FIALA-logo-navbar.png"
            alt="TAIFA-FIALA Logo"
            width={140}
            height={80}
            priority
          />
        </Link>
      </div>
      <div className="container mx-auto px-10 h-24 flex justify-between items-center">
        <div className="w-[140px] flex-shrink-0"></div>
        <div className="hidden md:flex items-center space-x-6 text-[#1F2A44] font-bold text-lg">
          <Link href="/funding" className="text-[#1F2A44] hover:text-[#4B9CD3] transition-colors duration-300">
            Funding
          </Link>
          <Link href="/organizations" className="text-[#1F2A44] hover:text-[#4B9CD3] transition-colors duration-300">
            Organizations
          </Link>
          <Link href="/analytics" className="text-[#1F2A44] hover:text-[#4B9CD3] transition-colors duration-300">
            Analytics
          </Link>
          <Link href="/about" className="text-[#1F2A44] hover:text-[#4B9CD3] transition-colors duration-300">
            About
          </Link>
        </div>
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2 font-medium text-lg">
            <button className="text-navy font-semibold hover:text-[#4B9CD3] transition-colors duration-300">EN</button>
            <span className="text-navy">|</span>
            <button className="text-navy hover:text-[#4B9CD3] transition-colors duration-300">FR</button>
          </div>
          <Link href="/submit-opportunity" className="bg-gold hover:bg-gold-dark text-[#F0E68C] font-bold py-2 px-4 rounded-lg transition-colors duration-300">
            Submit
          </Link>
        </div>
        <div className="md:hidden flex items-center">
          <button className="text-[#F0E68C] text-base">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16m4 6H4" />
            </svg>
          </button>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;