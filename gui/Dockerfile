FROM node:lts AS deps

WORKDIR /app

COPY package*.json ./
RUN npm ci

FROM node:lts AS builder
WORKDIR /app
COPY . .
COPY --from=deps /app/node_modules ./node_modules

CMD ["npm", "run", "dev"]