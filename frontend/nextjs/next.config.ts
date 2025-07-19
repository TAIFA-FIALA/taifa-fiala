import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Minimal configuration for Vercel deployment
  experimental: {
    optimizePackageImports: ['date-fns'],
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
