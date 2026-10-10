/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    unoptimized: true,
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://127.0.0.1:8000/api/:path*',
      },
      {
        source: '/assets/:path*',
        destination: 'http://127.0.0.1:8000/assets/:path*',
      },
      {
        source: '/outputs/:path*',
        destination: 'http://127.0.0.1:8000/outputs/:path*',
      },
    ];
  },
};

module.exports = nextConfig;
