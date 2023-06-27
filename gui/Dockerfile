FROM node:lts AS deps

WORKDIR /app

# COPY package*.json .

COPY ./gui .
RUN npm ci
RUN npm run build

EXPOSE 3000
EXPOSE 80
RUN chmod +x ./entrypoint*

ENV NEXT_PUBLIC_GITHUB_CLIENT_ID="06b962774236a4a8448f"

# CMD ["npm", "run", "start"]
ENTRYPOINT [ "./entrypoint.sh" ]
