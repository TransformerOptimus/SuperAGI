/** @type {import('next').NextConfig} */
const nextConfig = {
  assetPrefix: process.env.NODE_ENV === "production" ? "/" : "./",
  output: 'standalone'
};

module.exports = nextConfig;
