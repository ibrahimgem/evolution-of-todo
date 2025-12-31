# Railway Backend Deployment Guide

## Quick Start - Deploy to Railway

### Option 1: Deploy via Railway Web Dashboard (Recommended)

1. **Login to Railway**
   - Visit: https://railway.app
   - Sign in with GitHub

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Authorize Railway to access your GitHub account
   - Select repository: `ibrahimgem/evolution-of-todo`
   - Select branch: `002-fullstack-web-app`
   - Root directory: `Phase-II-Full-Stack-Web-Application/backend`

3. **Configure Environment Variables**

   Add these environment variables in Railway dashboard:

   ```bash
   DATABASE_URL=postgresql://user:password@host:5432/dbname
   SECRET_KEY=your-secret-key-here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

4. **Add PostgreSQL Database**
   - In your Railway project, click "New"
   - Select "Database" → "PostgreSQL"
   - Railway will automatically provision a database
   - Copy the connection string (DATABASE_URL) from database settings
   - Update your service's DATABASE_URL environment variable

5. **Deploy**
   - Railway will automatically detect the configuration files
   - Build and deployment will start automatically
   - Wait for deployment to complete (~2-3 minutes)

6. **Get Your Backend URL**
   - In Railway dashboard, go to your service
   - Click "Settings" → "Networking"
   - Click "Generate Domain"
   - Your backend URL will be: `https://your-service-name.up.railway.app`

### Option 2: Deploy via Railway CLI

1. **Login to Railway**
   ```bash
   railway login
   ```
   This will open your browser for authentication.

2. **Initialize Project**
   ```bash
   cd Phase-II-Full-Stack-Web-Application/backend
   railway init
   ```
   Select "Create a new project" and name it (e.g., "todo-backend")

3. **Add PostgreSQL Database**
   ```bash
   railway add --database postgresql
   ```

4. **Set Environment Variables**
   ```bash
   railway variables set SECRET_KEY="your-secret-key-here"
   railway variables set ALGORITHM="HS256"
   railway variables set ACCESS_TOKEN_EXPIRE_MINUTES="30"
   ```

   Note: DATABASE_URL is automatically set when you add PostgreSQL

5. **Deploy**
   ```bash
   railway up
   ```

6. **Generate Domain**
   ```bash
   railway domain
   ```
   This will generate a public URL for your backend.

## Configuration Files Created

### `nixpacks.toml`
Configures the build environment and start command for Railway's Nixpacks builder.

### `railway.json`
Railway-specific deployment configuration.

### `requirements.txt`
Python dependencies for the backend.

## Environment Variables Explained

- **DATABASE_URL**: PostgreSQL connection string
  - Format: `postgresql://user:password@host:5432/dbname`
  - Automatically provided by Railway when you add PostgreSQL database

- **SECRET_KEY**: Secret key for JWT token signing
  - Generate with: `openssl rand -hex 32`
  - Keep this secret and never commit to Git

- **ALGORITHM**: JWT signing algorithm (use HS256)

- **ACCESS_TOKEN_EXPIRE_MINUTES**: Token expiration time (default: 30 minutes)

## Update Frontend with Backend URL

Once your backend is deployed, update the frontend:

### Method 1: Via Vercel Dashboard

1. Go to: https://vercel.com/muhammad-ibrahims-projects-5d6efaf8/frontend/settings/environment-variables
2. Add new environment variable:
   - Key: `NEXT_PUBLIC_API_URL`
   - Value: `https://your-service-name.up.railway.app`
   - Environments: Production, Preview, Development
3. Click "Save"
4. Redeploy your frontend:
   - Go to Deployments tab
   - Click "..." on latest deployment
   - Click "Redeploy"

### Method 2: Via Vercel CLI

```bash
cd Phase-II-Full-Stack-Web-Application/frontend
vercel env add NEXT_PUBLIC_API_URL production
# Paste your Railway backend URL when prompted
vercel --prod
```

## Update Backend CORS Origins

After deployment, you need to update the CORS configuration to allow your Vercel frontend:

1. Edit `Phase-II-Full-Stack-Web-Application/backend/src/main.py`

2. Update the `origins` list:
   ```python
   origins = [
       "http://localhost:3000",
       "http://127.0.0.1:3000",
       "https://frontend-roan-delta-27.vercel.app",  # Add your Vercel URL
       "https://*.vercel.app",  # Allow all Vercel preview deployments
   ]
   ```

3. Commit and push changes:
   ```bash
   git add Phase-II-Full-Stack-Web-Application/backend/src/main.py
   git commit -m "Update CORS origins for Vercel deployment"
   git push origin 002-fullstack-web-app
   ```

4. Railway will automatically redeploy with the new changes

## Testing Your Deployment

1. **Test Backend Health**
   ```bash
   curl https://your-service-name.up.railway.app/health
   ```
   Should return:
   ```json
   {
     "status": "healthy",
     "service": "todo-api",
     "version": "1.0.0"
   }
   ```

2. **Test API Documentation**
   Visit: `https://your-service-name.up.railway.app/docs`

3. **Test Frontend**
   - Visit: https://frontend-roan-delta-27.vercel.app
   - Register a new account
   - Login
   - Create, edit, complete, and delete tasks

## Troubleshooting

### Build Fails

- Check Railway build logs in the dashboard
- Ensure all dependencies are in `requirements.txt`
- Verify Python version is 3.13+ in `nixpacks.toml`

### Database Connection Fails

- Verify DATABASE_URL is set correctly
- Check Railway PostgreSQL database is running
- Ensure database accepts connections from your service

### CORS Errors

- Verify frontend URL is in backend CORS origins
- Check that URL includes protocol (https://)
- Clear browser cache and try again

### Frontend Can't Connect to Backend

- Verify `NEXT_PUBLIC_API_URL` is set on Vercel
- Check backend URL is accessible (test /health endpoint)
- Ensure backend is deployed and running on Railway

## Railway CLI Useful Commands

```bash
# View logs
railway logs

# Open Railway dashboard
railway open

# Check status
railway status

# List environment variables
railway variables

# Link to existing project
railway link

# Unlink from project
railway unlink
```

## Cost Considerations

Railway offers:
- **Free Plan**: $5 credit per month (enough for small projects)
- **Starter Plan**: $5/month + usage
- **PostgreSQL**: ~$5-10/month depending on usage

Monitor your usage in the Railway dashboard.

## Next Steps

1. Deploy backend to Railway (follow steps above)
2. Get your Railway backend URL
3. Update Vercel frontend with `NEXT_PUBLIC_API_URL`
4. Update backend CORS origins with Vercel URL
5. Test the complete application
6. Monitor logs and performance

## Additional Resources

- [Railway Documentation](https://docs.railway.com)
- [Railway CLI Reference](https://docs.railway.com/reference/cli-api)
- [Nixpacks Documentation](https://nixpacks.com)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
