# GitHub Actions Deployment Setup

This directory contains GitHub Actions workflows for automated deployment of TAIFA-FIALA.

## Workflows

### `deploy-production.yml`
Automated deployment workflow that triggers on:
- Push to `main` or `master` branch
- Manual workflow dispatch (with options)

## Required GitHub Secrets

To use the deployment workflow, you need to configure these secrets in your GitHub repository:

### Go to: Repository Settings → Secrets and variables → Actions → New repository secret

1. **`PRODUCTION_SSH_KEY`**
   - Your private SSH key for accessing the production server
   - Generate with: `ssh-keygen -t ed25519 -C "github-actions@taifa-fiala"`
   - Add the public key to your production server's `~/.ssh/authorized_keys`

2. **`PRODUCTION_HOST`**
   - Your production server IP or hostname
   - Example: `100.75.201.24` or `mac-mini.local`

3. **`PRODUCTION_USER`**
   - Username for SSH connection to production server
   - Example: `jforrest`

4. **`KEYCHAIN_PASSWORD`**
   - Your macOS login password (for Docker keychain unlock)
   - Only needed if using Docker deployment

5. **`PRODUCTION_URL`** (Optional)
   - Your production URL for post-deployment tests
   - Default: `https://taifa-fiala.net`

## Usage

### Automatic Deployment
- Push changes to `main` branch
- GitHub Actions will automatically deploy to production

### Manual Deployment
1. Go to Actions tab in GitHub
2. Select "Deploy to Production" workflow
3. Click "Run workflow"
4. Choose deployment type:
   - **docker**: Uses `deploy_production_docker.sh`
   - **host**: Uses `deploy_production.sh`
5. Choose whether to restart services

## Features

- ✅ Automated deployment on push to main
- ✅ Manual deployment with options
- ✅ Service health verification
- ✅ Post-deployment API testing
- ✅ Docker and host-based deployment support
- ✅ Keychain password handling for macOS
- ✅ Rollback capability (via deployment scripts)

## Deployment Process

1. **Checkout**: Gets latest code
2. **SSH Setup**: Configures SSH key and known hosts
3. **Deploy**: Runs your existing deployment scripts
4. **Verify**: Checks service status and health endpoints
5. **Test**: Runs post-deployment API tests

## Troubleshooting

### SSH Connection Issues
- Ensure `PRODUCTION_SSH_KEY` is the private key (starts with `-----BEGIN`)
- Verify the public key is in `~/.ssh/authorized_keys` on production server
- Check that `PRODUCTION_HOST` and `PRODUCTION_USER` are correct

### Docker Deployment Issues
- Ensure `KEYCHAIN_PASSWORD` is set correctly
- Check that Docker is installed and running on production server
- Verify `deploy_production_docker.sh` script exists and is executable

### Service Verification Failures
- Check that your services start correctly with the deployment scripts
- Verify port 8030 is not blocked by firewall
- Ensure health endpoint returns 200 status

## Security Notes

- SSH private keys are encrypted in GitHub Secrets
- Keychain passwords are masked in logs
- All secrets are only accessible to workflow runs
- SSH connections use StrictHostKeyChecking for security