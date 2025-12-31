/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  basePath: '/evolution-of-todo',
  trailingSlash: true,
  images: {
    unoptimized: true
  }
};

module.exports = nextConfig;
