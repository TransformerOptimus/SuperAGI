FROM node:lts

WORKDIR /app

# COPY package*.json .

COPY ./gui .
RUN npm install
RUN npm run build

EXPOSE 3000
EXPOSE 80

CMD ["npm", "run", "start"]