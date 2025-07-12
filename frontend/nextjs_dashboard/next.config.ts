import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Enable experimental features for production
  experimental: {
    optimizePackageImports: ['date-fns'],
  },
  
  // Output configuration for Railway
  output: 'standalone',
  
  // Environment variables
  env: {
    CUSTOM_KEY: process.env.CUSTOM_KEY,
  },
  
  // Public runtime config
  publicRuntimeConfig: {
    apiUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    appUrl: process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000',
  },
  
  // Image optimization
  images: {
    domains: ['example.org', 'demo.fund'], // Add domains for funding opportunity images
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**',
      },
    ],
  },
  
  // Redirects for bilingual domains
  async redirects() {
    return [
      // Redirect www to non-www
      {
        source: '/:path*',
        has: [{ type: 'host', value: 'www.taifa-africa.com' }],
        destination: 'https://taifa-africa.com/:path*',
        permanent: true,
      },
      {
        source: '/:path*',
        has: [{ type: 'host', value: 'www.fiala-afrique.com' }],
        destination: 'https://fiala-afrique.com/:path*',
        permanent: true,
      },
    ];
  },
  
  // Rewrites for API proxy (if needed)
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/:path*`,
      },
    ];
  },
  
  // Headers for security
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin',
          },
        ],
      },
    ];
  },
  
  // Webpack configuration
  webpack: (config, { isServer }) => {
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
      };
    }
    return config;
  },
  
  // TypeScript configuration
  typescript: {
    ignoreBuildErrors: false,
  },
  
  // ESLint configuration
  eslint: {
    ignoreDuringBuilds: false,
  },
  
  // Internationalization setup for bilingual support
  i18n: {
    locales: ['en', 'fr'],
    defaultLocale: 'en',
    domains: [
      {
        domain: 'taifa-africa.com',
        defaultLocale: 'en',
      },
      {
        domain: 'fiala-afrique.com', 
        defaultLocale: 'fr',
      },
    ],
  },
};

export default nextConfig;
