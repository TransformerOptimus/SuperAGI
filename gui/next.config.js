/** @type {import('next').NextConfig} */
const nextConfig = {
  assetPrefix: process.env.NODE_ENV === "production" ? "/" : "./",
    env: {
        NEXT_PUBLIC_GITHUB_CLIENT_ID : process.env.NEXT_PUBLIC_GITHUB_CLIENT_ID
    },
};

module.exports = nextConfig;
