FROM node:22 AS build-stage

WORKDIR /app

COPY ui/package.json ./
COPY ui/package-lock.json ./
RUN npm ci

COPY ui/index.html ./
COPY ui/vite.config.ts ./
COPY ui/tsconfig*.json ./
COPY ui/src src
COPY ui/public public
COPY docs/exercise/gannon/core-briefings ../docs/exercise/gannon/core-briefings
COPY docs/exercise/gannon/email-briefing-graphics ../docs/exercise/gannon/email-briefing-graphics

RUN npm run build

FROM nginx:1.27.5-alpine AS deploy-stage

COPY ui/nginx.conf.template /etc/nginx/templates/default.conf.template
COPY --from=build-stage /app/dist /usr/share/nginx/html

EXPOSE 80
