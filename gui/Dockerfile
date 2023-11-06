FROM node:18-alpine AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

# Rebuild the source code only when needed
FROM node:18-alpine AS builder

WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules

COPY . .
ARG NEXT_PUBLIC_API_BASE_URL=/api
ENV NEXT_PUBLIC_API_BASE_URL=$NEXT_PUBLIC_API_BASE_URL
ARG NEXT_PUBLIC_MIXPANEL_AUTH_ID
ENV NEXT_PUBLIC_MIXPANEL_AUTH_ID=$NEXT_PUBLIC_MIXPANEL_AUTH_ID
EXPOSE 3000

CMD ["npm", "run", "dev"]