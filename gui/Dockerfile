FROM node:lts

WORKDIR /app

COPY . .
RUN npm install


ENV NEXT_PUBLIC_GITHUB_CLIENT_ID="06b962774236a4a8448f"

RUN npm run build
CMD ["npm", "run", "start"]