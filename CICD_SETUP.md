# CI/CD Setup Guide

This guide sets up automated deployment to production whenever you push to the main branch.

## 1. GitHub Repository Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions

Add these secrets:

### Required Secrets

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `PROD_HOST` | `100.75.201.24` | Production server IP |
| `PROD_USER` | `jforrest` | Production server username |
| `PROD_SSH_KEY` | `[Your SSH private key]` | SSH private key for production server |

### Getting Your SSH Private Key

```bash
# On your local machine, display your private key
cat ~/.ssh/id_rsa

# Or if you use a different key name
cat ~/.ssh/id_ed25519

# Copy the entire output (including -----BEGIN and -----END lines)
```

## 2. Production Server Setup

Ensure your production server has:

```bash
# SSH into production server
ssh jforrest@100.75.201.24

# Ensure git repository is set up
cd /Users/jforrest/production/TAIFA-FIALA
git remote -v  # Should show your GitHub repository

# If not set up, clone the repository
cd /Users/jforrest/production/
git clone https://github.com/YOUR_USERNAME/ai-africa-funding-tracker.git TAIFA-FIALA
```

## 3. How It Works

### Automatic Deployment
- **Trigger**: Push to `main` branch
- **Process**: 
  1. Builds frontend locally (for validation)
  2. Runs linting checks
  3. SSHs to production server
  4. Pulls latest code
  5. Stops services
  6. Updates dependencies
  7. Rebuilds frontend
  8. Restarts services
  9. Verifies deployment

### Manual Deployment
- Go to GitHub → Actions → "Deploy to Production"
- Click "Run workflow" → "Run workflow"

## 4. Monitoring Deployments

### GitHub Actions
- View deployment status: GitHub → Actions tab
- See logs and errors in real-time
- Get notifications on failures

### Production Health Check
After deployment, verify:
- Backend: `http://100.75.201.24:8030/health`
- Frontend: `http://100.75.201.24:3030`
- Live site: `https://taifa-fiala.net`

## 5. Troubleshooting

### Common Issues

**SSH Connection Failed**
- Verify `PROD_SSH_KEY` secret is correct
- Ensure SSH key has access to production server

**Build Failed**
- Check frontend dependencies in `package.json`
- Verify linting passes locally: `npm run lint`

**Deployment Failed**
- Check production server has enough disk space
- Verify services can be stopped/started
- Check production server logs

### Manual Rollback

If deployment fails, manually rollback:

```bash
ssh jforrest@100.75.201.24
cd /Users/jforrest/production/TAIFA-FIALA

# Rollback to previous commit
git log --oneline -5  # See recent commits
git checkout [PREVIOUS_COMMIT_HASH]

# Restart services
./restart_services_host.sh
```

## 6. Next Steps

1. **Add the GitHub secrets** (step 1)
2. **Push to main branch** to trigger first automated deployment
3. **Monitor the deployment** in GitHub Actions
4. **Verify the site** shows the latest version

## Benefits

✅ **Automatic deployments** on every push to main
✅ **Consistent deployment process** 
✅ **Build validation** before deployment
✅ **Health checks** after deployment
✅ **Rollback capability** if issues occur
✅ **No manual SSH required** for deployments

Your production site will always stay up-to-date with your latest code! 🚀
