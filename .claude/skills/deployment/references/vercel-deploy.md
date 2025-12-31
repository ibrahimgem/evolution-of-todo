# Vercel Deployment for Next.js

## Project Setup

1.  **Framework Preset**: Select "Next.js".
2.  **Root Directory**: Ensure it points to your frontend folder (e.g., `Phase-II-Full-Stack-Web-Application/frontend`).
3.  **Environment Variables**:
    - `NEXT_PUBLIC_API_URL`: URL of your deployed FastAPI backend.
    - `NEXT_PUBLIC_APP_URL`: Your Vercel deployment URL.

## Configuration (`next.config.js`)

Ensure you handle CORS if your backend is on a different domain.

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Add experimental or redirect configs here if needed
};

module.exports = nextConfig;
```

## Build Settings

- **Build Command**: `npm run build`
- **Output Directory**: `.next`
