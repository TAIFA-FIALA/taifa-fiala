# TAIFA-FIALA: Tracking AI Funding in Africa
# TAIFA-FIALA : Suivi des Financements IA en Afrique

<div align="center">

![TAIFA-FIALA Logo](https://taifa-fiala.net/logo.png)

**Promoting transparency, equity, and accountability in African AI funding**  
**Promouvoir la transparence, l'équité et la responsabilité dans le financement de l'IA africaine**

[![Live Site](https://img.shields.io/badge/Live%20Site-taifa--fiala.net-blue)](https://taifa-fiala.net)
[![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-green)](https://github.com/TAIFA-FIALA/taifa-fiala/actions)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[🇬🇧 English](#english) | [🇫🇷 Français](#français)

</div>

## 🌍 **Mission**

**English:**  
TAIFA-FIALA is the comprehensive bilingual platform for tracking funds for artificial intelligence across Africa. We aim to democratize access to funding information by breaking down language barriers and centralizing data and communications on funding announcements and their projects from hundreds of sources into one reliable, searchable platform.

**Français:**  
TAIFA-FIALA est la plateforme bilingue complète pour suivre les fonds pour l'intelligence artificielle à travers l'Afrique. Nous visons à démocratiser l'accès à l'information sur le financement en brisant les barrières linguistiques et en centralisant les données et les communications sur les annonces de financement et leurs projets de centaines de sources dans une plateforme fiable et recherchable.

## ✨ **Key Features**

### 🔎 Intelligent Search | Recherche Intelligente
- Hybrid traditional + vector search architecture | Architecture de recherche hybride traditionnelle + vectorielle
- Real-time funding opportunity discovery | Découverte d'opportunités de financement en temps réel
- Quality-filtered results (relevance score ≥0.6) | Résultats filtrés par qualité (score de pertinence ≥0.6)
- Semantic search for complex queries | Recherche sémantique pour requêtes complexes

### 📈 Real-Time Analytics | Analyses en Temps Réel
- **Gender Equity Analysis | Analyse de l'Équité de Genre**: Live disparity metrics and trends | Métriques et tendances des disparités en direct
- **Geographic Distribution | Distribution Géographique**: African-focused opportunity mapping | Cartographie des opportunités axée sur l'Afrique
- **Funding Intelligence | Intelligence de Financement**: Active vs. allocated funding distinction | Distinction entre financement actif et alloué
- **Sector Insights | Aperçus Sectoriels**: AI/ML, FinTech, HealthTech, AgriTech breakdowns | Répartitions IA/ML, FinTech, HealthTech, AgriTech

### 🤖 Automated Data Pipeline | Pipeline de Données Automatisé
- **Stage 1 | Étape 1**: RSS collection from 50+ funding sources | Collecte RSS de 50+ sources de financement
- **Stage 2 | Étape 2**: Crawl4AI enrichment for precise details | Enrichissement Crawl4AI pour détails précis
- **Stage 3 | Étape 3**: Serper search enhancement and validation | Amélioration et validation de recherche Serper
- **Quality Scoring | Notation Qualité**: Objective 4-dimension relevance assessment | Évaluation objective de pertinence à 4 dimensions

### 🎯 Actionable Insights | Informations Exploitables
- Application deadline tracking | Suivi des dates limites de candidature
- Funding stage analysis | Analyse des étapes de financement
- Eligibility criteria extraction | Extraction des critères d'éligibilité
- Contact information and application URLs | Informations de contact et URLs de candidature

## 🏗️ Technical Architecture | Architecture Technique

### Frontend Stack | Pile Frontend
```
Next.js 15 + TypeScript + Tailwind CSS v4
├── Real-time search modal | Modal de recherche en temps réel
├── Custom TAIFA theme system | Système de thème TAIFA personnalisé
├── Responsive analytics dashboards | Tableaux de bord analytiques adaptatifs
└── Progressive enhancement | Amélioration progressive
```

### Backend Stack | Pile Backend
```
FastAPI + Python 3.12 + PostgreSQL
├── Hybrid search engine | Moteur de recherche hybride
├── Automated data pipeline | Pipeline de données automatisé
├── RESTful API with OpenAPI docs | API RESTful avec docs OpenAPI
└── Real-time analytics endpoints | Points de terminaison analytiques temps réel
```

### Infrastructure | Infrastructure
```
Production Deployment | Déploiement Production
├── GitHub Actions CI/CD | CI/CD GitHub Actions
├── Cloudflare CDN | CDN Cloudflare
├── Health monitoring | Surveillance de santé
└── Automated backups | Sauvegardes automatisées
```

## 🚀 Quick Start | Démarrage Rapide

### Prerequisites | Prérequis
- Docker & Docker Compose
- Python 3.12+
- Access to PostgreSQL database
- (Optional) Translation API keys for enhanced features

### Development Setup | Configuration de Développement

```bash
# Clone repository | Cloner le dépôt
git clone https://github.com/TAIFA-FIALA/taifa-fiala.git
cd taifa-fiala

# Backend setup | Configuration backend
pip install -r requirements.txt

# Frontend setup | Configuration frontend
cd frontend/nextjs
npm install
cd ../..

# Environment configuration | Configuration environnement
cp .env.sample .env
# Edit .env with your configuration | Modifier .env avec votre configuration

# Start development servers | Démarrer les serveurs de développement
./start-dev.sh
```

### One-Command Deployment | Déploiement en Une Commande

```bash
# Deploy to production | Déployer en production
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

## 🌐 Live Platform | Plateforme En Direct

**🔗 [Visit TAIFA-FIALA | Visitez TAIFA-FIALA](https://taifa-fiala.net)**

### Key Pages | Pages Principales
- **🏠 Homepage | Accueil**: Search and platform overview | Recherche et aperçu de la plateforme
- **💰 Funding Landscape | Paysage de Financement**: Comprehensive opportunity browser | Navigateur d'opportunités complet
- **🎯 Theory of Change | Théorie du Changement**: Mission and impact framework | Mission et cadre d'impact
- **📋 Methodology | Méthodologie**: Data collection and analysis approach | Approche de collecte et d'analyse des données
- **ℹ️ About | À Propos**: Team, vision, and contact information | Équipe, vision et informations de contact

## 🤝 Contributing | Contribuer

**English:** We welcome contributions! Here's how to get involved:  
**Français:** Nous accueillons les contributions ! Voici comment vous impliquer :

1. **🍴 Fork | Bifurquer** the repository | le dépôt
2. **🌿 Create | Créer** a feature branch | une branche de fonctionnalité (`git checkout -b feature/amazing-feature`)
3. **💻 Make | Effectuer** your changes | vos modifications
4. **✅ Test | Tester** your changes | vos modifications
5. **📤 Submit | Soumettre** a pull request | une demande de tirage

### Code Standards | Normes de Code
- TypeScript for all frontend components | TypeScript pour tous les composants frontend
- Python type hints for backend code | Annotations de type Python pour le code backend
- ESLint + Prettier for formatting | ESLint + Prettier pour le formatage
- Comprehensive error handling | Gestion d'erreurs complète
- Clear documentation | Documentation claire

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

## 👥 Team | Équipe

**H Ruton & J Forrest** - *TAIFA-FIALA Founders | Fondateurs TAIFA-FIALA*

*Building bridges between Anglophone and Francophone African AI communities*