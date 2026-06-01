FROM node:20-alpine

RUN npm install -g npm@latest

WORKDIR /app

COPY package*.json ./

RUN npm ci

COPY . .

RUN addgroup -S app && adduser -S app -G app && chown -R app:app /app

USER app

EXPOSE 5173

# Run Vite dev server
CMD ["npm", "run", "dev"]
