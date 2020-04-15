# build stage
FROM node:8 as build-stage
WORKDIR /app
# RUN apk add yarn
COPY package.json ./
COPY package-lock.json ./
RUN npm install
COPY . .
RUN npm run build

# production stage
FROM nginx:stable-alpine as production-stage
COPY --from=build-stage /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
