# TAIFA Data Collection Enhancement Plan
*Implementation started: July 11, 2025*

## 🎯 Immediate Priorities (Next 48 Hours)

### Phase 1A: Fix & Expand RSS Sources (Priority: CRITICAL)

#### Current Issues to Fix:
- IDRC RSS: 404 error on https://idrc-crdi.ca/en/funding/funding-opportunities/rss
- Science for Africa: 404 error on https://scienceforafrica.foundation/feed/
- Gates Foundation: 404 error on https://www.gatesfoundation.org/ideas/rss/

#### Action Plan:
1. **Research correct RSS/feed URLs** for each organization
2. **Add 20+ new verified RSS sources** from our comprehensive list
3. **Implement backup web scraping** for organizations without RSS
4. **Add social media monitoring** for real-time announcements

### Phase 1B: Enhanced Search & Discovery (Priority: HIGH)

#### Serper Search Expansion:
- Add country-specific searches (Nigeria, Kenya, South Africa, etc.)
- Include foundation-specific queries (Gates + AI + Africa)
- Add academic funding searches (NIH, NSF international programs)
- Search for recent announcements (last 30 days filter)

#### New Collection Methods:
- **Email monitoring system** for funding newsletters
- **PDF document processing** for funding announcements
- **API integrations** where available (Devex, GrantSpace)
- **Social media monitoring** (Twitter/X, LinkedIn organization pages)

## 📊 Comprehensive Source List to Implement

### 🌍 Multilateral Organizations (15 sources)
1. **World Bank Group**
   - Main feed: https://www.worldbank.org/en/rss
   - Digital development: Web scraping needed
   - Tender/procurement notices

2. **African Development Bank**
   - News feed: https://www.afdb.org/rss.xml
   - Opportunities: Scraping needed
   - Country-specific programs

3. **United Nations Agencies**
   - UNDP: https://www.undp.org/rss.xml
   - UNESCO: https://en.unesco.org/rss.xml
   - UNECA: Scraping needed

[Continue with remaining 12 organizations...]

### 🇺🇸 US Government Sources (8 sources)
1. **USAID**
   - Opportunities: https://www.usaid.gov/rss/opportunities
   - Digital strategy: Scraping needed

2. **National Science Foundation**
   - International programs: API available
   - Africa-specific funding: Scraping needed

[Continue with remaining 6 sources...]

### 🇪🇺 European Sources (12 sources)
1. **European Commission**
   - Horizon Europe: API available
   - Digital Europe Programme: Scraping needed

2. **Agence Française de Développement (AFD)**
   - Calls for proposals: Scraping needed (French language)

[Continue with remaining 10 sources...]

### 🏢 Private Foundations (15 sources)
1. **Bill & Melinda Gates Foundation**
   - Correct RSS: Research needed
   - Grand Challenges: https://grandchallenges.org/feed/

2. **Ford Foundation**
   - Opportunities: Scraping needed
   - Technology for Social Justice: Specific page monitoring

[Continue with remaining 13 sources...]

### 🏛️ Research Institutions (10 sources)
1. **IDRC (Fixed URLs)**
   - AI4D Programme: Direct page monitoring
   - Funding opportunities: https://idrc-crdi.ca/en/funding (scraping)

[Continue with remaining 9 sources...]

### 🏭 Corporate Programs (12 sources)
1. **Google AI for Everyone**
   - Announcements: Scraping needed
   - Social media monitoring

2. **Microsoft AI for Good**
   - Blog RSS: https://blogs.microsoft.com/ai-for-good/feed/
   - Grant announcements: Scraping needed

[Continue with remaining 10 sources...]

## 🔧 Technical Implementation Details

### Enhanced RSS Monitor (v2.0)
```python
# New features to add:
- Dynamic URL discovery and validation
- Multi-language support (French, Arabic, Portuguese)
- Intelligent content extraction from full articles
- PDF attachment processing
- Social media link following
- Email newsletter parsing
```

### Email Monitoring System
```python
# Implementation approach:
- IMAP connection to dedicated monitoring email
- Subscribe to 50+ funding newsletters
- NLP processing of email content
- Automated link extraction and validation
- Duplicate detection across email sources
```

### Social Media Monitor
```python
# Platforms to monitor:
- Twitter/X: Organization handles, hashtags
- LinkedIn: Company pages, funding announcements  
- Facebook: Foundation pages and events
- YouTube: Funding announcement videos
```

### Enhanced Web Scraping
```python
# Advanced scraping features:
- JavaScript rendering (Playwright/Selenium)
- Form submission for gated content
- CAPTCHA solving integration
- Proxy rotation for reliability
- Respectful rate limiting
```

## 📈 Success Metrics (48-hour targets)
- [ ] **75+ verified RSS/feed sources** actively monitored
- [ ] **25+ web scraping targets** implemented
- [ ] **10+ email newsletters** subscribed and parsing
- [ ] **15+ social media accounts** monitored
- [ ] **200+ funding opportunities** in database
- [ ] **95%+ uptime** for all collection methods

## 🚀 Implementation Timeline

### Today (July 11)
- [ ] Fix existing RSS URLs (2 hours)
- [ ] Add 20 new verified RSS sources (4 hours)
- [ ] Implement basic web scraping for top 5 sources (4 hours)

### Tomorrow (July 12)  
- [ ] Email monitoring system setup (4 hours)
- [ ] Social media monitoring implementation (4 hours)
- [ ] Enhanced Serper search queries (2 hours)

### Next Steps
- [ ] PDF document processing
- [ ] API integrations (Devex, GrantSpace)
- [ ] French language processing preparation
- [ ] Performance optimization

---

*This plan will establish TAIFA as the most comprehensive AI funding tracker for Africa*