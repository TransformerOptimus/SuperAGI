/** @type {import('next').NextConfig} */
const nextConfig = {
    assetPrefix: process.env.NODE_ENV === "production" ? "/" : "./",
    env: {
        NEXT_PUBLIC_GITHUB_CLIENT_ID : process.env.NEXT_PUBLIC_GITHUB_CLIENT_ID
    },
    webpackDevMiddleware: config => {
    config.watchOptions = {
      poll: 1000,
      aggregateTimeout: 300,
    }
    return config
  }
}

module.exports = nextConfig
