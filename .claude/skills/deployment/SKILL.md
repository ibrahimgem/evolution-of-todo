---
name: deployment
description: Deployment workflows and configuration for FastAPI backends and Next.js frontends to cloud platforms like Neon, Vercel, and Railway. Use when deploying applications, setting up CI/CD pipelines, managing environment variables, or configuring production infrastructure.
---

# Deployment

This skill provides deployment workflows for full-stack applications with FastAPI and Next.js.

## Core Strategy

1.  **Environment Separation**: Use separate databases and secrets for development, staging, and production.
2.  **Infrastructure as Code**: Document all configuration in version control.
3.  **Zero-Downtime Deploys**: Use health checks and rolling deployments.
4.  **Secrets Management**: Never commit credentials; use platform environment variables.

## Deployment Targets

### Frontend (Next.js) → Vercel

- See [vercel-deploy.md](references/vercel-deploy.md) for step-by-step Vercel deployment.
- **Key Steps**:
  1. Connect GitHub repository
  2. Set framework preset to "Next.js"
  3. Configure environment variables (`NEXT_PUBLIC_API_URL`)
  4. Deploy with automatic builds on push

### Backend (FastAPI) → Railway/Render/Fly.io

- See [fastapi-deploy.md](references/fastapi-deploy.md) for Docker-based deployment.
- **Key Steps**:
  1. Create Dockerfile
  2. Set environment variables (`DATABASE_URL`, `SECRET_KEY`)
  3. Configure health check endpoint
  4. Deploy with automatic SSL

### Database → Neon PostgreSQL

- See [neon-deploy.md](references/neon-deploy.md) for Neon setup and migrations.
- **Key Steps**:
  1. Create Neon project and branch
  2. Get pooled connection string
  3. Run schema migrations
  4. Enable IP allowlisting if needed

## Pre-Deployment Checklist

- [ ] All tests passing
- [ ] Environment variables documented
- [ ] Database migrations tested
- [ ] CORS configured for production domain
- [ ] Error handling implemented
- [ ] Logging configured
- [ ] Health check endpoint added
