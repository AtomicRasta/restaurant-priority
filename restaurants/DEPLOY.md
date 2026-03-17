# Deploying Restaurant App to Vercel

## Quick Deploy (Recommended)

### Option 1: Via Vercel Dashboard (Easiest)

1. **Push to GitHub first:**
   ```bash
   cd /Users/rastamacmini/.openclaw/workspace/restaurants
   git init
   git add .
   git commit -m "Restaurant priority app"
   gh repo create restaurant-priority --public --source=. --push
   ```

2. **Connect to Vercel:**
   - Go to [vercel.com](https://vercel.com)
   - Click "New Project"
   - Import your GitHub repo
   - **Important:** Set Framework Preset to **"Other"**
   - Set Root Directory to `./`
   - Set Output Directory to `public`
   - Deploy!

### Option 2: Via Vercel CLI

1. **Install Vercel CLI (if needed):**
   ```bash
   npm install -g vercel
   ```

2. **Deploy:**
   ```bash
   cd /Users/rastamacmini/.openclaw/workspace/restaurants
   vercel --prod
   ```
   
   When prompted:
   - Set up and deploy? **Y**
   - Which scope? (your account)
   - Link to existing project? **N**
   - Project name: **restaurant-priority**
   - Directory: **./public**
   - Override settings? **N**

## URLs After Deploy

- Main page: `https://restaurant-priority.vercel.app/`
- Priority editor: `https://restaurant-priority.vercel.app/priority-editor`

## Troubleshooting

### 404 Errors
**Problem:** Vercel is treating this as a framework project (React, Next.js)
**Solution:** Set Framework Preset to "Other" in dashboard settings

### Files Not Found
**Problem:** Vercel is looking in wrong directory
**Solution:** 
1. Dashboard → Settings → General → Root Directory → `./`
2. Dashboard → Settings → General → Output Directory → `public`

### JSON Not Loading
**Problem:** CORS or path issues
**Solution:** Already configured in `vercel.json` - redeploy if needed

## Custom Domain (Optional)

1. Go to Project Settings → Domains
2. Add: `restaurants.yourdomain.com`
3. Add CNAME record in your DNS:
   ```
   restaurants  →  cname.vercel-dns.com
   ```

## Update Deployment

Just push to GitHub (if using GitHub integration) or run:
```bash
vercel --prod
```

## Configuration Files

- `vercel.json` - Routing and headers
- `package.json` - Project metadata
- `public/` - All static files served from here
