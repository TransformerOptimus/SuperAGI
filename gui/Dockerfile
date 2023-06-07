FROM node:lts

WORKDIR /app

COPY package*.json ./
RUN npm install
RUN chown -R node /app/node_modules

COPY . .

CMD ["npm", "run", "dev"]