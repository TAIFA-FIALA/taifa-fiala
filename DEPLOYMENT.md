# TAIFA-FIALA Production Deployment Guide

## Architecture Overview

**Hybrid Deployment:**
- 🏠 **Backend**: Mac-mini home server (data ingestion, dashboard, APIs)
- ☁️ **Frontend**: Vercel (public website, user interface)
- 🗄️ **Database**: Supabase (hosted)
- 🧠 **Vector Search**: Pinecone (hosted)

## Prerequisites

### Mac-mini Setup
1. **SSH Access**: Ensure SSH is enabled and accessible via Tailscale
2. **Python 3.8+**: Installed system-wide
3. **Git**: For code synchronization
4. **Network**: Stable internet connection

### Local Development Machine
1. **SSH Keys**: Configured for passwordless access to Mac-mini
2. **Tailscale**: Connected to same network as Mac-mini
3. **Git**: With push access to the repository
4. **Vercel CLI**: For frontend deployment

## Backend Deployment (Mac-mini)

### 1. Configure Deployment Script

Edit `deploy_production.sh` configuration:

```bash
# Configuration
PROD_SERVER="YOUR_MAC_MINI_IP"     # Your Mac-mini Tailscale IP
SSH_USER="YOUR_USERNAME"           # Your Mac-mini username
PROD_PATH="/path/to/production"    # Production directory path
```

### 2. Prepare Environment

Ensure your Mac-mini has a `.env` file with:

```bash
# Database
SUPABASE_PROJECT_URL=your_supabase_url
SUPABASE_API_KEY=your_supabase_key

# Vector Database
PINECONE_API_KEY=your_pinecone_key
PINECONE_HOST=your_pinecone_host

# API Keys
SERPER_API_KEY=your_serper_key
NEWSAPI_KEY=your_newsapi_key
```

### 3. Deploy Backend

```bash
# Make deployment script executable
chmod +x deploy_production.sh

# Deploy to Mac-mini
./deploy_production.sh
```

The script will:
- ✅ Test SSH connection
- ✅ Check git status
- ✅ Create deployment tag
- ✅ Sync backend files
- ✅ Setup Python environment
- ✅ Start services (data ingestion + dashboard)

### 4. Verify Backend Deployment

```bash
# Check service status
ssh user@mac-mini 'cd /path/to/production && ./restart_services.sh status'

# View logs
ssh user@mac-mini 'cd /path/to/production && ./restart_services.sh logs'

# Access dashboard
# http://MAC_MINI_IP:8501
```

## Frontend Deployment (Vercel)

### 1. Install Vercel CLI

```bash
npm install -g vercel
```

### 2. Configure Vercel Project

```bash
# Navigate to frontend directory
cd frontend/nextjs_dashboard

# Login to Vercel
vercel login

# Deploy to Vercel
vercel --prod
```

### 3. Configure Environment Variables

In Vercel dashboard, add:

```bash
NEXT_PUBLIC_API_URL=https://your-mac-mini-domain.com
NEXT_PUBLIC_DASHBOARD_URL=https://your-mac-mini-domain.com:8501
SUPABASE_PROJECT_URL=your_supabase_url
SUPABASE_API_KEY=your_supabase_key
```

### 4. Setup Custom Domain (Optional)

1. Add custom domain in Vercel dashboard
2. Configure DNS records
3. Update environment variables with new domain

## Service Management

### Mac-mini Service Commands

```bash
# Check status
./restart_services.sh status

# Start services
./restart_services.sh start

# Stop services
./restart_services.sh stop

# Restart services
./restart_services.sh restart

# View logs
./restart_services.sh logs

# Follow logs
./restart_services.sh tail
```

### Service Details

**Data Ingestion Service:**
- **Port**: N/A (background process)
- **Log**: `logs/data_ingestion.log`
- **PID**: `.data_ingestion.pid`

**Dashboard Service:**
- **Port**: 8501
- **Log**: `logs/dashboard.log`
- **PID**: `.dashboard.pid`
- **URL**: `http://MAC_MINI_IP:8501`

## CI/CD Pipeline

### Automated Deployment

1. **Push to main branch**
2. **Run deployment script**:
   ```bash
   ./deploy_production.sh
   ```
3. **Deploy frontend**:
   ```bash
   cd frontend/nextjs_dashboard && vercel --prod
   ```

### Rollback Process

If deployment fails, automatic rollback:
- Previous version restored from backup
- Services restarted with previous code
- Deployment tag removed from git

Manual rollback:
```bash
# SSH to Mac-mini
ssh user@mac-mini

# Navigate to production
cd /path/to/production

# List backups
ls -la ../*backup*

# Restore from backup
mv current_path backup_current
mv backup_TIMESTAMP current_path
./restart_services.sh restart
```

## Monitoring

### Health Checks

```bash
# Backend health
curl http://MAC_MINI_IP:8501/health

# Frontend health
curl https://your-vercel-domain.com/api/health

# Database health
# Check Supabase dashboard

# Vector DB health
# Check Pinecone dashboard
```

### Log Monitoring

```bash
# Real-time logs
ssh user@mac-mini 'cd /path/to/production && tail -f logs/*.log'

# Error checking
ssh user@mac-mini 'cd /path/to/production && grep -i error logs/*.log'
```

## Troubleshooting

### Common Issues

**SSH Connection Failed:**
- Check Tailscale connection
- Verify SSH key configuration
- Test manual SSH access

**Service Start Failed:**
- Check Python environment: `source venv/bin/activate`
- Verify dependencies: `pip list`
- Check environment variables: `cat .env`

**Dashboard Not Accessible:**
- Check firewall settings
- Verify port 8501 is open
- Check Streamlit process: `ps aux | grep streamlit`

**Frontend Build Failed:**
- Check Node.js version
- Clear npm cache: `npm cache clean --force`
- Verify environment variables in Vercel

### Support Commands

```bash
# Check system resources
ssh user@mac-mini 'top -l 1 | head -20'

# Check disk space
ssh user@mac-mini 'df -h'

# Check network connectivity
ssh user@mac-mini 'ping -c 4 supabase.com'

# Test database connection
ssh user@mac-mini 'cd /path/to/production && python -c "from supabase import create_client; print(\"DB OK\")"'
```

## Security Considerations

1. **SSH Keys**: Use key-based authentication only
2. **Firewall**: Restrict access to necessary ports
3. **Environment Variables**: Never commit secrets to git
4. **Tailscale**: Keep network access restricted
5. **Regular Updates**: Keep system packages updated

## Backup Strategy

### Automated Backups
- Deployment script creates automatic backups
- Timestamp-based backup directories
- Retention: Keep last 5 deployments

### Manual Backup
```bash
# Create backup
ssh user@mac-mini 'cp -r /path/to/production /path/to/backup_$(date +%Y%m%d_%H%M%S)'

# Database backup (handled by Supabase)
# Vector DB backup (handled by Pinecone)
```

## Performance Optimization

### Mac-mini Optimization
- Monitor CPU/Memory usage
- Optimize Python processes
- Consider process management (systemd)

### Vercel Optimization
- Enable caching
- Optimize bundle size
- Use CDN for static assets

This deployment setup provides a robust, scalable foundation for TAIFA-FIALA with the benefits of both home server control and cloud scalability.