# ============================================================================
# COMS Frontend Dockerfile
# Multi-stage build for optimized production image
# ============================================================================

# Stage 1: Dependencies
FROM node:18-alpine AS deps
WORKDIR /app

# Install dependencies based on lock file
COPY package.json package-lock.json* ./
RUN if [ -f package-lock.json ]; then \
      npm ci; \
    else \
      npm install; \
    fi && npm cache clean --force

# Stage 2: Builder
FROM node:18-alpine AS builder
WORKDIR /app

# Accept build arguments
ARG NEXT_PUBLIC_API_URL
ARG NEXT_PUBLIC_WS_URL
ARG NEXT_PUBLIC_APP_NAME
ARG NEXT_PUBLIC_APP_VERSION

# Copy dependencies from deps stage
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Set environment variables for build (NEXT_PUBLIC_* vars are baked into the build)
ENV NEXT_TELEMETRY_DISABLED=1
ENV NODE_ENV=production
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL:-http://156.232.88.156/api}
ENV NEXT_PUBLIC_WS_URL=${NEXT_PUBLIC_WS_URL:-ws://156.232.88.156/ws}
ENV NEXT_PUBLIC_APP_NAME=${NEXT_PUBLIC_APP_NAME:-COMS}
ENV NEXT_PUBLIC_APP_VERSION=${NEXT_PUBLIC_APP_VERSION:-1.0.0}

# Build the application
RUN npm run build

# Stage 3: Runner (Production)
FROM node:18-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Create non-root user
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Copy built files from standalone build
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
# Only copy public if it exists (contains static assets)
COPY --from=builder --chown=nextjs:nodejs /app/public ./public

USER nextjs

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# Start the application
CMD ["node", "server.js"]
