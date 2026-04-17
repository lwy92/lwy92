FROM docker.m.daocloud.io/node:20.20-alpine AS build
WORKDIR /app
COPY package.json .
COPY src ./src
RUN npm install && npm run build

FROM docker.m.daocloud.io/nginx:1.29.8-alpine
COPY --from=build /app/dist /usr/share/nginx/html
