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
taifa/
├── backend/                 # FastAPI application
├── frontend/               
│   ├── streamlit_app/      # Primary bilingual interface
│   └── nextjs_dashboard/   # Enhanced features (planned)
├── data_collectors/        # Automated data collection
├── translation_service.py  # AI translation engine
├── translation_queue_processor.py  # Batch translation
├── database_multilingual_schema.sql  # DB schema
├── tests/                  # Test suite
└── scripts/               # Deployment and utilities
```

### **API Endpoints**

#### **Core Data**
- `GET /api/v1/funding-opportunities/` - List intelligence feed
- `GET /api/v1/funding-opportunities/{id}` - Detailed opportunity view
- `GET /api/v1/organizations/` - Funding organizations directory

#### **Translation Features**
- `GET /api/v1/translated-content/{lang}` - Get content in specified language
- `POST /api/v1/translation-queue/` - Queue content for translation
- `GET /api/v1/translation-status/` - Translation system status

#### **Analytics**
- `GET /api/v1/analytics/summary` - Platform statistics
- `GET /api/v1/analytics/trends` - Funding trend analysis
- `GET /api/v1/search` - Multilingual search with filters

### **Running Tests**
```bash
# Test data collection
python test_enhanced_collection.py

# Test translation pipeline
python translation_queue_processor.py --mode test

# Test API endpoints
pytest tests/

# Test database schema
python apply_multilingual_schema.py
```

## 🌍 **Deployment**

### **Development Environment**
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### **Production Deployment**
```bash
# Deploy to production server
./scripts/deploy_production.sh

# Configure domain routing
# Point DNS: taifa-africa.com, fiala-afrique.com, taifa-fiala.net

# Start production services
docker-compose -f docker-compose.prod.yml up -d
```

## 📈 **Performance Metrics**

### **Data Collection**
- **Sources**: 44 active data sources
- **Update Frequency**: Real-time to 12-hour intervals
- **Success Rate**: 90%+ across all collection methods
- **Data Quality**: 95%+ relevance accuracy

### **Translation System**
- **Language Pairs**: English ↔ French (fully operational)
- **Translation Quality**: 0.89-0.97 confidence scores
- **Processing Speed**: Real-time for urgent, <2 hours for batch
- **Content Coverage**: 100% of platform content

### **Platform Performance**
- **API Response Time**: <500ms average
- **Database Queries**: Optimized with indexes and views
- **Uptime Target**: 99.9% availability
- **Concurrent Users**: Designed for 1000+ simultaneous users

## 🤝 **Contributing**

We welcome contributions from the African AI and development communities!

### **How to Contribute**
1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/your-feature`
3. **Make changes and test thoroughly**
4. **Submit pull request** with detailed description

### **Contribution Areas**
- **Data Sources**: Add new funding organization feeds
- **Translation Quality**: Improve French translations and add new languages
- **Documentation**: Enhance user guides and API documentation
- **Testing**: Expand test coverage and edge case handling
- **UI/UX**: Improve user interface and accessibility

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 **Acknowledgments**

- **African AI Research Community** for inspiration and requirements
- **Open Source Contributors** who made this platform possible
- **Funding Organizations** who provide the data that powers this platform
- **Translation Service Providers** enabling multilingual accessibility

## 📞 **Contact & Support**

- **Website**: [taifa-fiala.net](https://taifa-fiala.net)
- **English**: [taifa-africa.com](https://taifa-africa.com)  
- **Français**: [fiala-afrique.com](https://fiala-afrique.com)
- **GitHub Issues**: [Report bugs and feature requests](https://github.com/drjforrest/taifa/issues)
- **API Documentation**: [docs.taifa-fiala.net](https://docs.taifa-fiala.net)

---

**Supporting AI development across Africa through better funding access** 🌟

*Building bridges between Anglophone and Francophone African AI communities*