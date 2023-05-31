FROM node:lts

WORKDIR /app

# COPY package*.json .

COPY ./gui .
RUN npm install
RUN npm run build


CMD ["npm", "run", "start"]