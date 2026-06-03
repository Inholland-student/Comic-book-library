FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci --force

COPY --chown=node:node . .
RUN npm run build


FROM nginx:1.27-alpine

RUN apk update && apk upgrade --no-cache

COPY nginx.conf.template /etc/nginx/templates/default.conf.template
COPY --from=builder /app/dist /usr/share/nginx/html

RUN chown -R nginx:nginx /usr/share/nginx/html /etc/nginx/conf.d /var/cache/nginx /var/log/nginx \
    && touch /var/run/nginx.pid \
    && chown nginx:nginx /var/run/nginx.pid

ENV BACKEND_PROXY_TARGET=http://127.0.0.1:5000

USER nginx

EXPOSE 5173

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:5173/ || exit 1
