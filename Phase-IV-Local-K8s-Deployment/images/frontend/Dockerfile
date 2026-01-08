# Frontend Dockerfile for Todo Chatbot

# Build Stage: Install dependencies
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files and install dependencies
COPY package*.json ./
RUN npm ci

# Copy source code
COPY . .

# Build Stage: Build Next.js application
RUN npm run build

# Runtime Stage: Production image
FROM node:20-alpine

WORKDIR /app

# Use existing 'node' user (UID/GID 1000) from node:alpine base image

# Copy build artifacts and dependencies from builder
COPY --from=builder --chown=node:node /app/node_modules ./node_modules
COPY --from=builder --chown=node:node /app/.next ./.next
COPY --from=builder --chown=node:node /app/package.json /app/package-lock.json ./
COPY --from=builder --chown=node:node /app/public ./public

# Copy health check script
COPY --from=builder --chown=node:node /app/public/healthz.js ./healthz.js

# Set environment variables
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Expose application port
EXPOSE 3000

# Switch to non-root user
USER node

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node /app/healthz.js || exit 1

# Start the application
CMD ["npm", "start"]
