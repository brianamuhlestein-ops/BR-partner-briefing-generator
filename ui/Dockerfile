FROM node:22 AS build-stage

WORKDIR /app

COPY package.json ./
COPY package-lock.json ./
RUN npm ci

COPY index.html ./
COPY vite.config.ts ./
COPY tsconfig*.json ./
COPY src src
COPY public public

RUN npm run build

FROM nginx:1.27.5-alpine AS deploy-stage

COPY nginx.conf.template /etc/nginx/templates/default.conf.template
COPY --from=build-stage /app/dist /usr/share/nginx/html

EXPOSE 80
