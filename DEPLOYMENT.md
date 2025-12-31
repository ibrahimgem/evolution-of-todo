# Phase II Deployment Guide

## Overview

Phase II of the Evolution of Todo app has been successfully configured for deployment:

- **Frontend**: Next.js app deployed to GitHub Pages
- **Backend**: FastAPI app deployed to Hugging Face Spaces

## ✅ Completed Setup

### 1. GitHub Repository

**Branch**: `002-fullstack-web-app`

All Phase II code has been committed and pushed to GitHub:
- Full-stack application with Next.js frontend and FastAPI backend
- Premium UI with glassmorphism and theme support
- JWT authentication and robust error handling
- Development skills and agents

**Repository**: https://github.com/ibrahimgem/evolution-of-todo

### 2. Frontend Deployment (GitHub Pages)

**Configuration Files Created**:
- `.github/workflows/deploy-frontend.yml` - GitHub Actions workflow
- `Phase-II-Full-Stack-Web-Application/frontend/next.config.js` - Next.js static export config
- `Phase-II-Full-Stack-Web-Application/frontend/public/.nojekyll` - GitHub Pages config

**Setup Instructions**:

1. **Enable GitHub Pages**:
   - Go to repository Settings → Pages
   - Source: "GitHub Actions"
   - The workflow will automatically deploy on push to `002-fullstack-web-app`

2. **Add Environment Secret**:
   - Go to Settings → Secrets and variables → Actions
   - Add secret: `NEXT_PUBLIC_API_URL` (your Hugging Face backend URL)

3. **Trigger Deployment**:
   - The GitHub Actions workflow runs automatically on push
   - Or manually trigger from Actions tab

**Expected URL**: `https://ibrahimgem.github.io/evolution-of-todo/`

### 3. Backend Deployment (Hugging Face Spaces)

**Configuration Files Created**:
- `Phase-II-Full-Stack-Web-Application/backend/Dockerfile` - Docker container config
- `Phase-II-Full-Stack-Web-Application/backend/.dockerignore` - Docker ignore rules
- `Phase-II-Full-Stack-Web-Application/backend/README.md` - Hugging Face Space README

**Setup Instructions**:

1. **Create Hugging Face Space**:
   - Go to https://huggingface.co/new-space
   - Space name: `todo-backend` (or your choice)
   - SDK: Docker
   - Visibility: Public or Private

2. **Connect to GitHub**:
   - In Space settings, link to GitHub repository
   - Branch: `002-fullstack-web-app`
   - Path: `Phase-II-Full-Stack-Web-Application/backend`

3. **Add Environment Secrets**:
   Go to Space Settings → Variables and secrets:

   ```
   DATABASE_URL=postgresql+asyncpg://user:pass@host/dbname
   SECRET_KEY=your-secret-key-here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

4. **Database Setup (Neon)**:
   - Create account at https://neon.tech
   - Create new project
   - Copy connection string (asyncpg format)
   - Use as `DATABASE_URL` secret

**Expected URL**: `https://huggingface.co/spaces/YOUR_USERNAME/todo-backend`

## 🔧 Manual Deployment Steps

### Frontend (GitHub Pages)

```bash
# Already done - just enable in repository settings
# Workflow will run automatically on next push
```

### Backend (Hugging Face)

```bash
# Test Docker build locally (optional)
cd Phase-II-Full-Stack-Web-Application/backend
docker build -t todo-backend .
docker run -p 7860:7860 \
  -e DATABASE_URL="your_db_url" \
  -e SECRET_KEY="your_secret" \
  todo-backend
```

## 📋 Post-Deployment Checklist

### Frontend
- [ ] Enable GitHub Pages in repository settings
- [ ] Add `NEXT_PUBLIC_API_URL` secret
- [ ] Verify workflow runs successfully
- [ ] Test frontend at GitHub Pages URL
- [ ] Verify API calls reach backend

### Backend
- [ ] Create Hugging Face Space
- [ ] Link to GitHub repository
- [ ] Add all environment secrets
- [ ] Set up Neon PostgreSQL database
- [ ] Verify Space builds successfully
- [ ] Test API endpoints at Hugging Face URL
- [ ] Check health endpoint: `/health`
- [ ] Verify OpenAPI docs: `/docs`

### Integration
- [ ] Update frontend `NEXT_PUBLIC_API_URL` with Hugging Face backend URL
- [ ] Test full authentication flow
- [ ] Test task CRUD operations
- [ ] Verify CORS configuration
- [ ] Test theme switching
- [ ] Verify responsive design

## 🔐 Environment Variables

### Frontend (.env.local - not committed)
```bash
NEXT_PUBLIC_API_URL=https://huggingface.co/spaces/YOUR_USERNAME/todo-backend
```

### Backend (Hugging Face Secrets)
```bash
DATABASE_URL=postgresql+asyncpg://user:pass@host.neon.tech/dbname
SECRET_KEY=<generate with: openssl rand -hex 32>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## 📖 API Documentation

Once deployed, access interactive API documentation:
- **Swagger UI**: `https://YOUR_BACKEND_URL/docs`
- **ReDoc**: `https://YOUR_BACKEND_URL/redoc`

## 🚀 Features Deployed

### Backend
- JWT authentication with secure password hashing
- Full task CRUD operations
- User-specific task isolation
- Global error handling with structured responses
- Health check endpoint
- CORS configuration for frontend
- Async PostgreSQL with SQLModel ORM

### Frontend
- Premium glassmorphism UI design
- Light/dark theme with smooth transitions
- Responsive design for all devices
- JWT token management with localStorage
- Error boundaries for graceful error handling
- Loading states and animations
- Accessible form validation

## 🔄 Continuous Deployment

Both deployments are configured for automatic updates:

- **Frontend**: Automatically deploys when changes are pushed to `002-fullstack-web-app` branch and files in `Phase-II-Full-Stack-Web-Application/frontend/**` are modified
- **Backend**: Automatically rebuilds when GitHub repository is updated (if connected to Hugging Face Space)

## 📝 Notes

1. **Database Migrations**: Run Alembic migrations after backend deployment if needed
2. **CORS**: Update backend CORS origins to include your GitHub Pages URL
3. **Rate Limiting**: Consider adding rate limiting for production use
4. **Monitoring**: Set up logging and monitoring for both services
5. **Backups**: Configure automated backups for Neon database

## 🐛 Troubleshooting

### Frontend Issues
- **404 on routes**: Ensure `trailingSlash: true` in next.config.js
- **API calls fail**: Check `NEXT_PUBLIC_API_URL` secret
- **Build fails**: Check GitHub Actions logs

### Backend Issues
- **Container fails to start**: Check Hugging Face Space logs
- **Database connection fails**: Verify `DATABASE_URL` format and credentials
- **Health check fails**: Ensure port 7860 is exposed and endpoint returns 200

## 📚 Additional Resources

- [Next.js Static Export](https://nextjs.org/docs/pages/building-your-application/deploying/static-exports)
- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [Hugging Face Spaces](https://huggingface.co/docs/hub/spaces)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Neon PostgreSQL](https://neon.tech/docs/introduction)
