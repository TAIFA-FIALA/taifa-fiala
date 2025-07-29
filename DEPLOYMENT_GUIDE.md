# AI Africa Funding Tracker - Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying the AI Africa Funding Tracker with resolved dependency conflicts and improved reliability.

## Prerequisites

- **Python 3.12** (required for compatibility)
- **macOS** production server
- **SSH access** to production server
- **Node.js and npm** (for Next.js frontend)

## Quick Start

### 1. Resolve Dependencies

First, analyze and resolve any dependency conflicts:

```bash
python3.12 resolve_dependencies.py
```

This will generate a `dependency_report.txt` showing any conflicts.

### 2. Test Deployment

Run comprehensive deployment tests:

```bash
python3.12 test_deployment.py
```

This validates:
- Python version compatibility
- Requirements installation
- Script syntax
- Critical package imports

### 3. Deploy to Production

Use the improved deployment script:

```bash
./deploy_production_host_fixed.sh
```

## Dependency Management

### Unified Requirements Strategy

The project now uses a **unified requirements approach** to eliminate conflicts:

- **`requirements-unified.txt`**: Master requirements file with resolved versions
- **Component-specific files**: Updated to match unified versions
- **Automatic conflict detection**: Built-in analysis and resolution

### Key Improvements

1. **Version Consistency**: All components use compatible package versions
2. **Conflict Resolution**: Automatic detection and resolution of version conflicts
3. **Better Error Handling**: Improved installation process with fallbacks
4. **Import Validation**: Tests critical package imports after installation

## Deployment Process

### Step-by-Step Process

1. **Pre-deployment Checks**
   - Dependency conflict analysis
   - Backup creation
   - File synchronization

2. **Environment Setup**
   - Virtual environment creation for each component
   - Unified requirements installation
   - Component-specific requirement supplements

3. **Service Startup**
   - Backend (FastAPI on port 8030)
   - Streamlit Dashboard (port 8501)
   - Next.js Frontend (port 3030)
   - File Watcher (background process)

4. **Health Checks**
   - HTTP endpoint testing with retries
   - Service status verification
   - Log file monitoring

5. **Management Scripts**
   - Service restart capabilities
   - Status monitoring
   - Log access

### Service Management

#### Start Services
```bash
ssh jforrest@100.75.201.24 'cd /Users/jforrest/production/TAIFA-FIALA && ./restart_services_host.sh'
```

#### Stop Services
```bash
ssh jforrest@100.75.201.24 'cd /Users/jforrest/production/TAIFA-FIALA && ./stop_services_host.sh'
```

#### Check Status
```bash
ssh jforrest@100.75.201.24 'cd /Users/jforrest/production/TAIFA-FIALA && ./check_services_status.sh'
```

#### View Logs
```bash
ssh jforrest@100.75.201.24 'cd /Users/jforrest/production/TAIFA-FIALA && tail -f logs/backend.log'
ssh jforrest@100.75.201.24 'cd /Users/jforrest/production/TAIFA-FIALA && tail -f logs/streamlit.log'
ssh jforrest@100.75.201.24 'cd /Users/jforrest/production/TAIFA-FIALA && tail -f logs/frontend.log'
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Dependency Conflicts

**Symptoms:**
- Installation failures
- Import errors
- Version compatibility warnings

**Solution:**
```bash
# Re-run dependency analysis
python3.12 resolve_dependencies.py

# Check for conflicts
cat dependency_report.txt

# Use unified requirements
pip install -r requirements-unified.txt
```

#### 2. Service Startup Failures

**Symptoms:**
- Services not responding
- Health check failures
- Process termination

**Solution:**
```bash
# Check service status
ssh jforrest@100.75.201.24 'cd /Users/jforrest/production/TAIFA-FIALA && ./check_services_status.sh'

# Review logs
ssh jforrest@100.75.201.24 'cd /Users/jforrest/production/TAIFA-FIALA && tail -100 logs/backend.log'

# Restart services
ssh jforrest@100.75.201.24 'cd /Users/jforrest/production/TAIFA-FIALA && ./restart_services_host.sh'
```

#### 3. Python Version Issues

**Symptoms:**
- Package installation failures
- Syntax errors
- Compatibility warnings

**Solution:**
```bash
# Verify Python version
python3.12 --version

# Update Python path in deployment script if needed
export PATH=/usr/local/bin:/opt/homebrew/bin:$PATH
```

#### 4. Port Conflicts

**Symptoms:**
- Services fail to bind to ports
- Connection refused errors

**Solution:**
```bash
# Check port usage
lsof -i :8030  # Backend
lsof -i :8501  # Streamlit
lsof -i :3030  # Frontend

# Kill conflicting processes
sudo kill -9 <PID>
```

### Recovery Procedures

#### Rollback Deployment

If deployment fails, rollback to previous version:

```bash
ssh jforrest@100.75.201.24 'rm -rf /Users/jforrest/production/TAIFA-FIALA && mv /Users/jforrest/production/backups/TAIFA-FIALA-<TIMESTAMP> /Users/jforrest/production/TAIFA-FIALA'
```

#### Clean Environment Reset

For complete environment reset:

```bash
ssh jforrest@100.75.201.24 << 'EOF'
cd /Users/jforrest/production/TAIFA-FIALA
./stop_services_host.sh
rm -rf backend/venv frontend/streamlit_app/venv data_processors/venv
rm -rf logs/* pids/*
EOF
```

## Monitoring and Maintenance

### Health Monitoring

The deployment includes built-in health monitoring:

- **HTTP endpoint checks** with automatic retries
- **Process monitoring** with PID tracking
- **Log rotation** and error tracking
- **Service restart** capabilities

### Regular Maintenance

1. **Weekly**: Check service status and logs
2. **Monthly**: Update dependencies and test deployment
3. **Quarterly**: Full system backup and disaster recovery test

### Performance Optimization

- **Resource monitoring**: CPU, memory, disk usage
- **Log management**: Rotation and archival
- **Database optimization**: Query performance and indexing
- **Cache management**: Redis optimization

## Security Considerations

### Access Control

- SSH key-based authentication
- Firewall configuration for required ports
- Service isolation with virtual environments

### Data Protection

- Environment variable security
- Database connection encryption
- API key management

## Support and Documentation

### Log Locations

- Backend: `/Users/jforrest/production/TAIFA-FIALA/logs/backend.log`
- Streamlit: `/Users/jforrest/production/TAIFA-FIALA/logs/streamlit.log`
- Frontend: `/Users/jforrest/production/TAIFA-FIALA/logs/frontend.log`
- File Watcher: `/Users/jforrest/production/TAIFA-FIALA/logs/file_watcher.log`

### Configuration Files

- Environment: `.env` files in respective directories
- Requirements: Component-specific and unified requirements files
- Scripts: Management scripts in production directory

### Service Endpoints

- **Backend API**: http://100.75.201.24:8030
- **API Documentation**: http://100.75.201.24:8030/docs
- **Streamlit Dashboard**: http://100.75.201.24:8501
- **Next.js Frontend**: http://100.75.201.24:3030

## Version History

- **v1.0**: Initial Docker-based deployment
- **v2.0**: Host-based deployment with dependency resolution
- **v2.1**: Enhanced error handling and monitoring
- **v2.2**: Unified requirements and conflict resolution

---

For additional support or questions, refer to the project documentation or contact the development team.