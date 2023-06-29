FROM node:lts AS deps

WORKDIR /app

COPY package*.json ./
COPY . .
RUN npm ci

ENV NEXT_PUBLIC_GITHUB_CLIENT_ID="06b962774236a4a8448f"

# CMD ["npm", "run", "start"]
ENTRYPOINT [ "./entrypoint.sh" ]