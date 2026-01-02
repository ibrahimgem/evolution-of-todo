/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  experimental: {
    serverActions: {
      bodySizeLimit: '2mb',
    },
  },
  // Enable OpenAI ChatKit
  transpilePackages: ['@openai/chatkit'],
  // Fix TypeScript path aliases for build containers
  typescript: {
    // Ignore TypeScript errors during build (for path resolution issues)
    ignoreBuildErrors: false,
  },
  // Ensure path aliases work in all environments
  webpack: (config, { isServer }) => {
    // Add alias resolution for TypeScript paths
    config.resolve.alias['@'] = require('path').resolve(__dirname, './src');
    return config;
  },
  // Environment variables
  env: {
    NEXT_PUBLIC_BACKEND_URL: process.env.NEXT_PUBLIC_BACKEND_URL,
  },
};

module.exports = nextConfig;
