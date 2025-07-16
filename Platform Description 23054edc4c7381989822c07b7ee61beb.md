# Platform Description

<aside>
⁉️ **TLDR:** TAIFA-FIALA is a technology platform connecting African AI researchers and entrepreneurs with global funding opportunities through automated data collection, human verification, and a multilingual community hub. The system features personalized matching, collaborative resources, and regional support to increase African representation in global AI.

</aside>

# TAIFA-FIALA: Democratizing AI Funding Access Across Africa

<aside>
✅

TAIFA-FIALA (Tracking AI Funding for Africa - Financement Pour L’intelligence Artificielle en Afrique) is a community-driven membership organization and a digital platform for democratizing funding for artificial intelligence research and implementation in African countries through principles of equity, accountability and transparency on the part of donors, investors, grantees, and entrepreneurs.

</aside>

## Platform Overview

TAIFA-FIALA serves as the central hub for AI funding opportunities in Africa, bringing together researchers, startups, funders, and implementers in a collaborative ecosystem. The platform leverages advanced data collection technologies and human expertise to ensure high-quality, relevant, and timely information for the African AI community.

## Core Technology Components

### 1. Multi-Source Data Ingestion System

The platform employs four sophisticated modules to collect comprehensive funding information:

- **Crawl4AI Website Scanning:** Automated web crawlers that specifically target and extract funding information from relevant philanthropic AI, technology, and grant-making websites
- **User-Validated Submissions:** A structured submission system allowing community members / the public to contribute funding opportunities they discover / are connected to, creating a collaborative intelligence network
- **Daily Automated Searches:** Integration with [Serper.dev](http://Serper.dev) API to perform daily searches across the web for new AI funding opportunities relevant to Africa not picked up by any of the other methods
- **RSS Feed Monitoring:** Lowest hanging fruit involves continuous tracking of key organization feeds, news sources, and announcement channels known to broadcast RFPs to capture the opportunities as they are published

### 2. Data Storage & Processing Infrastructure

All collected information is systematically processed and stored in a robust PostgreSQL database layer, enabling efficient retrieval, filtering, and analysis of funding opportunities. Full content of all RFPs will be chunked, vectorized and stored adjacent in pgvector buckets, while its metadata will be linked to the main PostgreSQL database.

### 3. Human-in-the-Loop Quality Assurance

Before publishing to the public platform, all funding opportunities will undergo verification by  python admin app interface where human reviewers ensure:

- Information accuracy and completeness
- Relevance to African AI researchers and implementers
- Proper categorization and tagging
- Elimination of duplicates and outdated opportunities

A quick checkmark is applied by the validating user, which switches a status property to publish and enables the translation pipeline and rendering on the Next.js public site.

### 4. Public Exchange Platform

The community-facing platform is built using Next.js and written in Typescript, providing a responsive, accessible interface for users across Africa, even in bandwidth-constrained environments. The platform is accessible through multiple domains already purchased:

- [taifa-fiala.net](https://taifa-fiala.net) (Primary domain)
- [taifa-africa.com](http://taifa-africa.com) (Regional domain)
- [fiala-afrique.com](http://fiala-afrique.com) (Francophone Africa domain)

## Key Upcoming Platform Features

- **Personalized Opportunity Matching:** AI-powered recommendation system that connects users with the most relevant funding opportunities based on their profile, interests, and past activities
- **Bilingual Support:** Complete platform availability in both English and French to serve diverse linguistic communities across Africa
- **Collaborative Knowledge Base:** Community-driven resources including application templates, best practices, and success stories
- **Regional Chapters:** Dedicated spaces for regional collaboration, addressing unique challenges and opportunities across different parts of Africa
- **Impact Tracking:** Systems to monitor and celebrate successful funding applications, creating a virtuous cycle of knowledge sharing and powerful analytic methods

## Community Integration

The technical platform works in concert with the TAIFA-FIALA Notion community workspace, which serves as the collaborative heart of the ecosystem. This integration enables seamless knowledge sharing, community building, and governance across both technical and social dimensions of the platform.

## Our Vision

The vision TAIFA-FIALA is working towards is full African representation in global AI research and implementation, facilitated by our data-driven solution for democratizing access to funding opportunities with principles of equity, transparency, and accountability.