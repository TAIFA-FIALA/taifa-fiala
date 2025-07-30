# TAIFA-FIALA: AI Funding Tracker for Africa
*Financement pour l'Intelligence Artificielle en Afrique*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-blue.svg)](https://www.postgresql.org/)

## 🌍 **Mission**

TAIFA-FIALA is the comprehensive bilingual platform for tracking funds for artificial intelligence across Africa. We aim to democratize access to funding information by breaking down language barriers and centralizing data and communications on funding announcements and their projects from hundreds of sources into one reliable, searchable platform.

**English**: Tracking AI Funding for Africa  
**Français**: Financement pour l'Intelligence Artificielle en Afrique

## ✨ **Key Features**

### 🔍 **Comprehensive Data Collection**
- **44 Active Sources**: RSS feeds, web scraping, search APIs
- **Real-time Updates**: Automated monitoring with intelligent scheduling
- **Quality Assurance**: Deduplication, relevance scoring, content validation
- **Geographic Coverage**: All African countries + international sources

### 🌐 **Bilingual Platform**
- **English ↔ French**: Full interface and content translation
- **Intelligent Translation**: Multi-provider AI translation with quality scoring
- **Cultural Adaptation**: Localized formatting for dates, currencies, terminology
- **Domain Strategy**: taifa-africa.com (EN) | fiala-afrique.com (FR) | taifa-fiala.net (bilingual)

### 📊 **Advanced Search & Analytics**
- **Multilingual Search**: Query in English or French across all content
- **Smart Filtering**: By amount, deadline, sector, organization, geography
- **Trend Analysis**: Funding patterns, geographic distribution, sector insights
- **Export Capabilities**: CSV/JSON for research and reporting

### 🛡️ **Enterprise-Grade Infrastructure**
- **PostgreSQL Database**: Robust data storage with translation infrastructure
- **FastAPI Backend**: High-performance REST API with comprehensive endpoints
- **Docker Deployment**: Containerized services for development and production
- **Health Monitoring**: Real-time status tracking and error recovery

## 🚀 **Quick Start**

### **Prerequisites**
- Docker & Docker Compose
- Python 3.11+
- Access to PostgreSQL database
- (Optional) Translation API keys for enhanced features

### **Installation**

```bash
# Clone the repository
git clone https://github.com/drjforrest/taifa.git
cd taifa

# Copy environment template
cp .env.example .env
# Edit .env with your database credentials

# Initialize database schema
python apply_multilingual_schema.py

# Test data collection system
python test_enhanced_collection.py

# Start the platform
docker-compose up -d
```

### **Access Points**
- **Streamlit Dashboard**: http://localhost:8501
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🏗️ **Architecture Overview**

```
TAIFA-FIALA Platform Architecture
├── Data Collection Layer
│   ├── RSS Monitors (16 sources)
│   ├── Web Scrapers (6 major orgs)
│   └── Search APIs (22 query patterns)
├── Processing Layer
│   ├── Content Classification
│   ├── Translation Pipeline
│   └── Quality Validation
├── Storage Layer
│   ├── PostgreSQL Database
│   ├── Translation Tables
│   └── Queue Management
├── API Layer
│   ├── FastAPI Backend
│   ├── REST Endpoints
│   └── Webhook Support
└── Frontend Layer
    ├── Streamlit Dashboard (Bilingual)
    ├── Next.js Enhancement (Planned)
    └── Mobile PWA (Roadmap)
```

## 📊 **Data Sources**

### **Multilateral Organizations**
- World Bank Digital Development
- African Development Bank
- United Nations Development Programme
- European Commission Horizon Europe

### **Research Institutions**
- International Development Research Centre (IDRC)
- Science for Africa Foundation
- MIT Technology Review
- Nature Technology

### **Government Sources**
- USAID Opportunities
- National Science Foundation
- European Research Council
- African Union Development Agency

### **Private Sector**
- Google AI for Good
- Microsoft AI for Good
- Gates Foundation
- TechCrunch Startup News

*Full list of 44 sources available in system documentation*

## 🛠️ **Development**

### **Project Structure**
```
FastAPI + Python 3.12 + PostgreSQL
├── Hybrid search engine
├── Automated data pipeline
├── RESTful API with OpenAPI docs
└── Real-time analytics endpoints
```

### Infrastructure
```
Production Deployment
├── GitHub Actions CI/CD
├── Cloudflare CDN
├── Health monitoring
└── Automated backups
```

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18+
- PostgreSQL 14+

### Development Setup

```bash
# Clone repository
git clone https://github.com/TAIFA-FIALA/taifa-fiala.git
cd taifa-fiala

# Backend setup
pip install -r requirements.txt

# Frontend setup
cd frontend/nextjs
npm install
cd ../..

# Environment configuration
cp .env.sample .env
# Edit .env with your configuration

# Start development servers
./start-dev.sh
```

### One-Command Deployment

```bash
# Deploy to production
./deploy-latest.sh
```

## 📊 Data & Analytics

### Current Metrics
- **50+ RSS Sources**: Major funding organizations
- **Real-Time Processing**: 50 records every 12 hours
- **Quality Filtering**: 60%+ relevance threshold
- **Geographic Focus**: Africa-prioritized scoring

### Gender Equity Insights
- Live disparity analysis
- Sector-by-sector breakdowns
- Historical trend tracking
- Actionable recommendations

### Search Intelligence
- **Traditional Search**: Fast PostgreSQL full-text
- **Vector Enhancement**: Semantic similarity matching
- **Composite Ranking**: Multi-factor algorithm
- **Quality Assurance**: Automated relevance scoring

## 🛠️ Development

### Project Structure
```
taifa-fiala/
├── frontend/nextjs/          # Next.js application
├── backend/                  # FastAPI backend
├── data_processors/          # Pipeline components
├── database/                 # Schema and migrations
├── scripts/                  # Utility scripts
│   ├── deployment/          # Deployment automation
│   ├── monitoring/          # Health checks
│   └── testing/             # Test utilities
└── docs/                    # Documentation
```

### Key Commands

```bash
# Development
npm run dev                   # Start frontend dev server
python -m uvicorn app.main:app --reload  # Start backend

# Production
./scripts/deployment/deploy_production_host.sh
./scripts/monitoring/check_services_status.sh

# Testing
npm run lint                  # Frontend linting
pytest                        # Backend tests
```

## 🌐 Live Platform

**🔗 [Visit TAIFA-FIALA](https://taifa-fiala.net)**

### Key Pages
- **🏠 Homepage**: Search and platform overview
- **💰 Funding Landscape**: Comprehensive opportunity browser
- **🎯 Theory of Change**: Mission and impact framework
- **📋 Methodology**: Data collection and analysis approach
- **ℹ️ About**: Team, vision, and contact information

## 🤝 Contributing

We welcome contributions! Here's how to get involved:

1. **🍴 Fork** the repository
2. **🌿 Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **💻 Make** your changes
4. **✅ Test** your changes
5. **📤 Submit** a pull request

### Code Standards
- TypeScript for all frontend components
- Python type hints for backend code
- ESLint + Prettier for formatting
- Comprehensive error handling
- Clear documentation

## 📈 Impact & Metrics

### Platform Analytics
- **Search Queries**: Real-time funding discovery
- **Data Quality**: 60%+ relevance threshold maintained
- **Geographic Coverage**: Africa-focused with global context
- **Update Frequency**: 12-hour automated cycles

### Research Insights
- **Gender Disparity**: Quantified funding gaps
- **Sector Analysis**: AI/ML funding distribution
- **Trend Identification**: Emerging funding patterns
- **Policy Recommendations**: Evidence-based advocacy

## 📚 Documentation

- 📖 [API Documentation](./docs/api/) - Complete API reference
- 🚀 [Deployment Guide](./DEPLOYMENT_GUIDE.md) - Production setup
- ⚙️ [CI/CD Setup](./CICD_SETUP.md) - Automation configuration
- 🗄️ [Database Schema](./SCHEMA.md) - Data structure reference

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## 👥 Team

**H Ruton & J Forrest** - *TAIFA-FIALA Founders*

Building transparency, equity, and accountability in African AI funding through open data and evidence-based analysis.

## 🙏 Acknowledgments

- 🌍 African AI research community
- 💻 Open source contributors
- 🏛️ Funding organizations providing transparent data
- 👥 Users providing feedback and insights
- 🤝 Partners supporting our mission

---

**Supporting AI development across Africa through better funding access** 🌟

*Building bridges between Anglophone and Francophone African AI communities*