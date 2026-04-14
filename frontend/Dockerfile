FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy app code
COPY . .

# Expose port 5173 (Vite default)
EXPOSE 5173

# Run Vite dev server
CMD ["npm", "run", "dev"]
