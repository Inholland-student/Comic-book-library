FROM node:20-alpine

WORKDIR /app

RUN apk upgrade --no-cache

COPY package*.json ./

RUN npm ci

COPY . .

RUN addgroup -S app && adduser -S app -G app && chown -R app:app /app

USER app

EXPOSE 5173

CMD ["npm", "run", "dev"]
