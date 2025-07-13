# 🚄 TAIFA-FIALA Railway Deployment Guide

## 🎯 Pre-Deployment Checklist

### 1. **Railway Account Setup**
- [ ] Create Railway account at [railway.app](https://railway.app)
- [ ] Connect your GitHub account
- [ ] Install Railway CLI: `npm install -g @railway/cli`
- [ ] Login: `railway login`

### 2. **Environment Variables Preparation**
- [ ] SERPER_DEV_API_KEY (for funding discovery)
- [ ] OPENAI_API_KEY (for translations)
- [ ] Custom domains DNS configuration
- [ ] N8N_WEBHOOK_URL (for Notion and other integrations)
- [ ] SMTP credentials (for notifications)

### 3. **Domain Configuration**
- [ ] Point `taifa-africa.com` DNS to Railway
- [ ] Point `fiala-afrique.com` DNS to Railway
- [ ] Point `api.taifa-fiala.net` DNS to Railway

## 🚀 Step-by-Step Deployment

### Step 1: Create New Railway Project

```bash
# Initialize Railway project
cd ai-africa-funding-tracker
railway init

# Set project name
railway up --name taifa-fiala-production
```

### Step 2: Deploy PostgreSQL Database

```bash
# Add PostgreSQL service
railway add --service postgresql

# Wait for database to be ready
railway status
```

### Step 3: Deploy FastAPI Backend

```bash
# Deploy backend service
railway up --service backend

# Set environment variables
railway variables:set ENVIRONMENT=production
railway variables:set DEBUG=false
railway variables:set DATABASE_URL=${{Postgres.DATABASE_URL}}
railway variables:set SERPER_DEV_API_KEY=your_serper_key_here
railway variables:set OPENAI_API_KEY=your_openai_key_here

# Run database migrations
railway run --service backend ./railway-migrate.sh
```

### Step 4: Deploy Next.js Frontend

```bash
# Deploy frontend service
railway up --service frontend/nextjs_dashboard

# Set environment variables
railway variables:set NODE_ENV=production
railway variables:set NEXT_PUBLIC_API_URL=https://api.taifa-fiala.net
railway variables:set NEXT_PUBLIC_APP_URL=https://taifa-africa.com
```

### Step 5: Deploy Data Collection Service

```bash
# Deploy data collection service
railway up --service data_collectors

# Set environment variables
railway variables:set DATABASE_URL=${{Postgres.DATABASE_URL}}
railway variables:set SERPER_DEV_API_KEY=your_serper_key_here
```

### Step 6: Configure Custom Domains

```bash
# Add custom domains
railway domain:add taifa-africa.com --service frontend
railway domain:add fiala-afrique.com --service frontend
railway domain:add api.taifa-fiala.net --service backend
```

## 🔧 DNS Configuration

### For `taifa-africa.com` and `fiala-afrique.com`:
```
Type: CNAME
Name: @
Value: your-frontend-service.up.railway.app
```

### For `api.taifa-fiala.net`:
```
Type: CNAME  
Name: api
Value: your-backend-service.up.railway.app
```

## 📊 Environment Variables Setup

### Backend Service Environment Variables:
```bash
# Core configuration
railway variables:set ENVIRONMENT=production --service backend
railway variables:set DEBUG=false --service backend
railway variables:set LOG_LEVEL=INFO --service backend

# Database (automatically provided by Railway)
railway variables:set DATABASE_URL=${{Postgres.DATABASE_URL}} --service backend

# API Keys
railway variables:set SERPER_DEV_API_KEY=your_serper_key --service backend
railway variables:set OPENAI_API_KEY=your_openai_key --service backend

# CORS origins
railway variables:set BACKEND_CORS_ORIGINS='["https://taifa-africa.com","https://fiala-afrique.com"]' --service backend

# Security
railway variables:set SECRET_KEY=$(openssl rand -base64 32) --service backend
```

### Frontend Service Environment Variables:
```bash
railway variables:set NODE_ENV=production --service frontend
railway variables:set NEXT_PUBLIC_API_URL=https://api.taifa-fiala.net --service frontend
railway variables:set NEXT_PUBLIC_APP_URL=https://taifa-africa.com --service frontend
railway variables:set NEXT_TELEMETRY_DISABLED=1 --service frontend
```

### Data Collector Service Environment Variables:
```bash
railway variables:set DATABASE_URL=${{Postgres.DATABASE_URL}} --service data_collectors
railway variables:set SERPER_DEV_API_KEY=your_serper_key --service data_collectors
railway variables:set ENVIRONMENT=production --service data_collectors
```

## 🧪 Testing Deployment

### 1. **Backend Health Check**
```bash
curl https://api.taifa-fiala.net/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "ai-africa-funding-tracker",
  "version": "1.0.0"
}
```

### 2. **Frontend Accessibility**
- Visit https://taifa-africa.com
- Verify TAIFA branding loads
- Test Rwanda demo page: https://taifa-africa.com/rwanda-demo
- Test bilingual switching

### 3. **Data Collection Service**
```bash
curl https://your-collector-service.up.railway.app/health
```

### 4. **API Endpoints**
```bash
# Test funding opportunities endpoint
curl https://api.taifa-fiala.net/api/v1/funding-opportunities/

# Test search endpoint
curl "https://api.taifa-fiala.net/api/v1/funding-opportunities/search/?q=Rwanda"
```

## 📈 Monitoring & Maintenance

### Railway Dashboard Monitoring
- Service health status
- Resource usage (CPU, Memory, Network)
- Deployment logs
- Environment variables

### Application Monitoring
- Database connection health
- API response times
- Data collection success rates
- User search patterns

### Scheduled Maintenance
- Daily collection runs at 6:00 AM UTC
- Weekly cleanup on Sundays at 2:00 AM UTC
- Monthly database performance review
- Quarterly dependency updates

## 💰 Cost Estimation

### Railway Pricing (Hobby Plan):
- **PostgreSQL**: ~$5/month
- **Backend Service**: ~$5/month
- **Frontend Service**: ~$5/month  
- **Data Collector**: ~$3/month
- **Total**: ~$18/month

### Additional Costs:
- **Domain renewal**: ~$30/year
- **API costs (SERPER)**: ~$20/month
- **Translation APIs**: ~$10/month
- **Total Monthly**: ~$48/month

## 🚨 Troubleshooting

### Common Issues:

#### 1. **Database Connection Failed**
```bash
# Check database status
railway status --service postgresql

# View database logs
railway logs --service postgresql

# Restart database service
railway restart --service postgresql
```

#### 2. **Frontend Build Failed**
```bash
# Check build logs
railway logs --service frontend

# Common fixes:
# - Verify Node.js version compatibility
# - Check package.json dependencies
# - Ensure environment variables are set
```

#### 3. **Data Collection Not Running**
```bash
# Check collector service logs
railway logs --service data_collectors

# Verify environment variables
railway variables --service data_collectors

# Manual collection test
railway run --service data_collectors python test_collection.py
```

#### 4. **CORS Issues**
- Verify BACKEND_CORS_ORIGINS includes your domains
- Check that API URLs use HTTPS in production
- Ensure domains match exactly (no trailing slashes)

## 🔄 Deployment Updates

### Backend Updates:
```bash
# Deploy new backend version
git push origin main
railway redeploy --service backend

# Run migrations if needed
railway run --service backend alembic upgrade head
```

### Frontend Updates:
```bash
# Deploy new frontend version
git push origin main
railway redeploy --service frontend
```

### Data Collection Updates:
```bash
# Deploy new collector version
git push origin main
railway redeploy --service data_collectors
```

## 🎉 Go Live Checklist

- [ ] All services deployed and healthy
- [ ] Custom domains configured and SSL active
- [ ] Database migrations completed
- [ ] Environment variables configured
- [ ] Data collection running (check logs)
- [ ] Frontend accessible on both domains
- [ ] API endpoints responding correctly
- [ ] Search functionality working
- [ ] Rwanda demo page functional
- [ ] Bilingual routing working
- [ ] Health checks passing
- [ ] Monitoring alerts configured

## 📞 Support

If you encounter issues during deployment:

1. **Check Railway Status**: [status.railway.app](https://status.railway.app)
2. **Review Logs**: `railway logs --service <service_name>`
3. **Railway Documentation**: [docs.railway.app](https://docs.railway.app)
4. **Community Support**: [Railway Discord](https://discord.gg/railway)

---

**🎯 Result**: Professional, scalable deployment of TAIFA-FIALA on Railway with custom domains, automated data collection, and bilingual support serving African AI funding discovery! 🌍
