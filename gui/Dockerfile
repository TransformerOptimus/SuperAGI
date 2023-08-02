FROM node:lts

WORKDIR /app

COPY ./gui .
RUN npm install


ENV NEXT_PUBLIC_GITHUB_CLIENT_ID="06b962774236a4a8448f"
RUN ls
RUN cat package.json
RUN npm run build
RUN chmod +x ./entrypoint*
ENTRYPOINT ["entrypoint.sh"]