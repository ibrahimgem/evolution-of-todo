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

# Create non-root user
RUN addgroup -g 1000 nodeuser && \
    adduser -u 1000 -G nodeuser nodeuser

# Copy build artifacts and dependencies from builder
COPY --from=builder --chown=nodeuser:nodeuser /app/node_modules ./node_modules
COPY --from=builder --chown=nodeuser:nodeuser /app/.next ./.next
COPY --from=builder --chown=nodeuser:nodeuser /app/package*.json ./package*.json
COPY --from=builder --chown=nodeuser:nodeuser /app/public ./public

# Copy health check script
COPY --from=builder --chown=nodeuser:nodeuser /app/public/healthz.js ./healthz.js

# Set environment variables
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Expose application port
EXPOSE 3000

# Switch to non-root user
USER nodeuser

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node /app/healthz.js || exit 1

# Start the application
CMD ["npm", "start"]
