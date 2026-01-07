# Railway Deployment Guide for Todo Chatbot Frontend

## Issue: TypeScript Path Aliases in Build Container

### Problem
The frontend build fails on Railway with error: `"Cannot find module '../lib/api-client'"`

This happens because TypeScript path aliases (`@/*` → `src/*`) are not being resolved during the build process in Railway's container environment.

### Root Cause
- Local development uses TypeScript compiler which understands `tsconfig.json` path mappings
- Railway build container may not be using the same TypeScript configuration
- Next.js build process doesn't automatically resolve TypeScript path aliases

### Solution Applied

#### 1. Updated `next.config.js`
- Added explicit webpack alias resolution
- Ensures path aliases work in all environments
- Maintains TypeScript compatibility

#### 2. Enhanced `nixpacks.toml`
- Added TypeScript and @types/node to build dependencies
- Ensures TypeScript compiler is available during build
- Uses `tsc --noEmit` to validate imports before Next.js build

#### 3. Updated Build Script
- Modified build command to run TypeScript validation first
- `tsc --noEmit` checks all imports and path aliases
- Prevents build from proceeding if TypeScript errors exist

#### 4. Created `railway.toml`
- Alternative Railway configuration file
- Explicit TypeScript build environment setup
- Fallback configuration if nixpacks.toml doesn't work

## Deployment Steps

### 1. Environment Variables
Set these in Railway dashboard:
```
NEXT_PUBLIC_BACKEND_URL=https://your-backend-url.railway.app
```

### 2. Build Configuration
Railway will automatically detect and use:
- `nixpacks.toml` (primary)
- `railway.toml` (fallback)

### 3. Build Process
1. Install TypeScript globally
2. Run `tsc --noEmit` to validate imports
3. Run `next build` with webpack alias resolution
4. Start with `next start`

### 4. Health Check
- Health check endpoint: `/api/health` (ensure backend provides this)
- Timeout: 300 seconds
- Restart policy: ON_FAILURE

## Verification

### Local Testing
```bash
# Test TypeScript validation
npm run build  # This runs: tsc --noEmit && next build

# Check for any import errors
npm run lint
```

### Railway Testing
1. Push to GitHub
2. Railway will auto-deploy
3. Check build logs for TypeScript validation
4. Verify no "Cannot find module" errors

## Troubleshooting

### If Build Still Fails
1. Check Railway build logs for TypeScript errors
2. Verify all imports use correct path aliases
3. Ensure `NEXT_PUBLIC_BACKEND_URL` is set
4. Try using `railway.toml` instead of `nixpacks.toml`

### Alternative: Convert to Relative Paths
If path aliases continue to cause issues, convert imports:
```typescript
// Instead of: import { apiClient } from '@/lib/api-client';
// Use: import { apiClient } from '../lib/api-client';
```

### Manual Path Resolution
The webpack config in `next.config.js` ensures:
```javascript
config.resolve.alias['@'] = path.resolve(__dirname, './src');
```

## Success Criteria
- ✅ Build completes without "Cannot find module" errors
- ✅ All path aliases resolve correctly
- ✅ Frontend deploys successfully
- ✅ Health check passes
- ✅ Backend API connectivity works

## Post-Deployment
1. Verify frontend loads at Railway URL
2. Test authentication flow
3. Test chat functionality
4. Monitor build logs for any remaining issues