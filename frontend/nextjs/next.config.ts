import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Minimal configuration for Vercel deployment
  experimental: {
    optimizePackageImports: ['date-fns'],
  },
  
  // API rewrites for production - proxy API requests to backend
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: process.env.NODE_ENV === 'production' 
          ? 'http://100.75.201.24:8030/api/:path*'  // Production backend
          : 'http://localhost:8030/api/:path*'       // Development backend
      },
      {
        source: '/health',
        destination: process.env.NODE_ENV === 'production'
          ? 'http://100.75.201.24:8030/health'      // Production health check
          : 'http://localhost:8030/health'           // Development health check
      }
    ];
  },
  
  // Image optimization
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**',
      },
    ],
  },
  
  // TypeScript configuration
  typescript: {
    ignoreBuildErrors: false,
  },
  
  // ESLint configuration
  eslint: {
    ignoreDuringBuilds: false,
  },
};

export default nextConfig;
