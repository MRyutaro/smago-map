# Reactのビルドを行う
FROM node:lts-alpine3.19 as build
WORKDIR /app
COPY ./ ./
RUN yarn install && yarn run build

# Nginxの設定を行う
FROM nginx:alpine
# ビルドしたReactのファイルをコピー
COPY --from=build /app/dist /var/www
COPY ./nginx /etc/nginx/conf.d

WORKDIR /var/www
CMD ["nginx", "-g", "daemon off;"]
