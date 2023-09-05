# Dockerfile

# Stage 1 - the build process
FROM node:latest as build-deps
WORKDIR /usr/src/app
COPY front/package*.json ./
RUN npm install
COPY ./front .
RUN npm run build

# Stage 2 - the production environment
FROM nginx:latest
COPY --from=build-deps /usr/src/app/dist /usr/share/nginx/html
COPY ./front/default.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]