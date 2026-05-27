FROM node:20-alpine

# OCI Image Metadata (helps with SBOM generation and artifact tracking)
LABEL org.opencontainers.image.title="Comic Book Library Frontend"
LABEL org.opencontainers.image.description="Vue.js frontend for Comic Book Library"
LABEL org.opencontainers.image.authors="Comic Book Library Team"
LABEL org.opencontainers.image.url="https://github.com/meryamdouiri/Comic-book-library"
LABEL org.opencontainers.image.source="https://github.com/meryamdouiri/Comic-book-library"
LABEL org.opencontainers.image.documentation="https://github.com/meryamdouiri/Comic-book-library/blob/main/README.md"
LABEL org.opencontainers.image.vendor="Comic Book Library"

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
