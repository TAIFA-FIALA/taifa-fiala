"""
TAIFA-FIALA Streamlit Internationalization (i18n)
Bilingual support for the funding tracker interface
"""

import streamlit as st
import json
import os
from typing import Dict, Any, Optional
from datetime import datetime
import re

class TaifaI18n:
    """Internationalization handler for TAIFA-FIALA"""
    
    def __init__(self):
        self.translations = {}
        self.current_language = 'en'
        self.supported_languages = {
            'en': {'name': 'English', 'native': 'English', 'flag': '🇬🇧'},
            'fr': {'name': 'French', 'native': 'Français', 'flag': '🇫🇷'}
        }
        self._load_translations()
    
    def _load_translations(self):
        """Load translation files"""
        translations_dir = os.path.join(os.path.dirname(__file__), 'translations')
        
        # Create translations directory if it doesn't exist
        os.makedirs(translations_dir, exist_ok=True)
        
        for lang_code in self.supported_languages.keys():
            translation_file = os.path.join(translations_dir, f'{lang_code}.json')
            
            if os.path.exists(translation_file):
                with open(translation_file, 'r', encoding='utf-8') as f:
                    self.translations[lang_code] = json.load(f)
            else:
                # Create default translation file
                self._create_default_translations(lang_code)
    
    def _create_default_translations(self, lang_code: str):
        """Create default translation files"""
        if lang_code == 'en':
            translations = {
                # Navigation
                "nav.dashboard": "Dashboard",
                "nav.opportunities": "Intelligence Feed",
                "nav.organizations": "Organizations",
                "nav.analytics": "Analytics",
                "nav.submit": "Submit Opportunity",
                
                # Branding
                "brand.taifa": "TAIFA",
                "brand.fiala": "FIALA",
                "brand.tagline.en": "Tracking AI Funding for Africa",
                "brand.tagline.fr": "Financement pour l'Intelligence Artificielle en Afrique",
                "brand.description": "The comprehensive platform for AI intelligence feed across Africa",
                
                # Dashboard
                "dashboard.title": "AI Intelligence Feed Dashboard",
                "dashboard.total_opportunities": "Total Opportunities",
                "dashboard.recent_additions": "Recent Additions",
                "dashboard.active_funders": "Active Funders",
                "dashboard.avg_funding": "Average Funding Amount",
                "dashboard.welcome": "Welcome to TAIFA - Your gateway to AI funding in Africa",
                
                # Opportunities
                "opportunities.title": "Intelligence Feed",
                "opportunities.search_placeholder": "Search opportunities...",
                "opportunities.filter_by": "Filter by",
                "opportunities.amount": "Amount",
                "opportunities.deadline": "Deadline",
                "opportunities.organization": "Organization",
                "opportunities.no_results": "No opportunities found matching your criteria",
                "opportunities.view_details": "View Details",
                "opportunities.apply_now": "Apply Now",
                
                # Organizations
                "organizations.title": "Funding Organizations",
                "organizations.type": "Type",
                "organizations.country": "Country",
                "organizations.focus_areas": "Focus Areas",
                
                # Language Switcher
                "language.switch_to": "Switch to",
                "language.current": "Current language",
                
                # Common
                "common.search": "Search",
                "common.filter": "Filter",
                "common.reset": "Reset",
                "common.loading": "Loading...",
                "common.error": "Error",
                "common.success": "Success",
                "common.save": "Save",
                "common.cancel": "Cancel",
                
                # Dates
                "date.today": "Today",
                "date.yesterday": "Yesterday",
                "date.days_ago": "days ago",
                "date.deadline_in": "Deadline in",
                "date.expired": "Expired",
                
                # Status
                "status.open": "Open",
                "status.closed": "Closed", 
                "status.upcoming": "Upcoming",
                "status.draft": "Draft",
                
                # Footer
                "footer.about": "About TAIFA",
                "footer.contact": "Contact",
                "footer.api": "API Documentation",
                "footer.github": "GitHub",
                "footer.copyright": "© 2025 TAIFA-FIALA. Supporting AI development across Africa."
            }
        else:  # French
            translations = {
                # Navigation
                "nav.dashboard": "Tableau de bord",
                "nav.opportunities": "Opportunités de financement",
                "nav.organizations": "Organisations",
                "nav.analytics": "Analyses", 
                "nav.submit": "Soumettre une opportunité",
                
                # Branding
                "brand.taifa": "TAIFA",
                "brand.fiala": "FIALA",
                "brand.tagline.en": "Tracking AI Funding for Africa",
                "brand.tagline.fr": "Financement pour l'Intelligence Artificielle en Afrique",
                "brand.description": "La plateforme complète pour les opportunités de financement IA en Afrique",
                
                # Dashboard
                "dashboard.title": "Tableau de bord des opportunités de financement IA",
                "dashboard.total_opportunities": "Opportunités totales",
                "dashboard.recent_additions": "Ajouts récents",
                "dashboard.active_funders": "Bailleurs actifs",
                "dashboard.avg_funding": "Montant moyen de financement",
                "dashboard.welcome": "Bienvenue à FIALA - Votre passerelle vers le financement IA en Afrique",
                
                # Opportunities
                "opportunities.title": "Opportunités de financement",
                "opportunities.search_placeholder": "Rechercher des opportunités...",
                "opportunities.filter_by": "Filtrer par",
                "opportunities.amount": "Montant",
                "opportunities.deadline": "Date limite",
                "opportunities.organization": "Organisation",
                "opportunities.no_results": "Aucune opportunité trouvée selon vos critères",
                "opportunities.view_details": "Voir les détails",
                "opportunities.apply_now": "Postuler maintenant",
                
                # Organizations
                "organizations.title": "Organisations de financement",
                "organizations.type": "Type",
                "organizations.country": "Pays",
                "organizations.focus_areas": "Domaines d'intervention",
                
                # Language Switcher
                "language.switch_to": "Basculer vers",
                "language.current": "Langue actuelle",
                
                # Common
                "common.search": "Rechercher",
                "common.filter": "Filtrer",
                "common.reset": "Réinitialiser",
                "common.loading": "Chargement...",
                "common.error": "Erreur",
                "common.success": "Succès",
                "common.save": "Enregistrer",
                "common.cancel": "Annuler",
                
                # Dates
                "date.today": "Aujourd'hui",
                "date.yesterday": "Hier",
                "date.days_ago": "jours passés",
                "date.deadline_in": "Date limite dans",
                "date.expired": "Expiré",
                
                # Status
                "status.open": "Ouvert",
                "status.closed": "Fermé",
                "status.upcoming": "À venir",
                "status.draft": "Brouillon",
                
                # Footer
                "footer.about": "À propos de FIALA",
                "footer.contact": "Contact",
                "footer.api": "Documentation API",
                "footer.github": "GitHub",
                "footer.copyright": "© 2025 TAIFA-FIALA. Soutenir le développement de l'IA en Afrique."
            }
        
        # Save translations
        translations_dir = os.path.join(os.path.dirname(__file__), 'translations')
        os.makedirs(translations_dir, exist_ok=True)
        
        translation_file = os.path.join(translations_dir, f'{lang_code}.json')
        with open(translation_file, 'w', encoding='utf-8') as f:
            json.dump(translations, f, ensure_ascii=False, indent=2)
        
        self.translations[lang_code] = translations
    
    def set_language(self, language_code: str):
        """Set the current language"""
        if language_code in self.supported_languages:
            self.current_language = language_code
            st.session_state.language = language_code
    
    def get_current_language(self) -> str:
        """Get current language from session state or default"""
        if 'language' in st.session_state:
            return st.session_state.language
        return self.current_language
    
    def t(self, key: str, **kwargs) -> str:
        """Translate a key with optional parameter substitution"""
        current_lang = self.get_current_language()
        
        # Get translation
        translation = self.translations.get(current_lang, {}).get(key, key)
        
        # Fallback to English if translation not found
        if translation == key and current_lang != 'en':
            translation = self.translations.get('en', {}).get(key, key)
        
        # Parameter substitution
        if kwargs:
            try:
                translation = translation.format(**kwargs)
            except (KeyError, ValueError):
                pass  # Return original if substitution fails
        
        return translation
    
    def get_language_info(self, lang_code: str) -> Dict[str, str]:
        """Get language information"""
        return self.supported_languages.get(lang_code, {})
    
    def get_supported_languages(self) -> Dict[str, Dict[str, str]]:
        """Get all supported languages"""
        return self.supported_languages

def create_language_switcher(i18n: TaifaI18n, key: str = "language_selector"):
    """Create a language switcher component"""
    current_lang = i18n.get_current_language()
    languages = i18n.get_supported_languages()
    
    # Language switcher in sidebar
    with st.sidebar:
        st.markdown("---")
        st.subheader("🌍 " + i18n.t("language.current"))
        
        # Create language options
        lang_options = []
        lang_codes = []
        
        for code, info in languages.items():
            flag = info.get('flag', '')
            native_name = info.get('native', info.get('name', code))
            lang_options.append(f"{flag} {native_name}")
            lang_codes.append(code)
        
        # Current selection index
        current_index = lang_codes.index(current_lang) if current_lang in lang_codes else 0
        
        # Language selector
        selected_index = st.selectbox(
            i18n.t("language.switch_to"),
            range(len(lang_options)),
            index=current_index,
            format_func=lambda x: lang_options[x],
            key=key
        )
        
        # Return selected language
        selected_lang = lang_codes[selected_index]
        return selected_lang

def create_bilingual_header(i18n: TaifaI18n):
    """Create bilingual header with TAIFA-FIALA branding"""
    current_lang = i18n.get_current_language()
    
    # Main header with bilingual branding
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if current_lang == 'fr':
            st.markdown("""
            <div style="text-align: center; padding: 1rem;">
                <h1 style="margin: 0; font-size: 2.5rem;">
                    <span style="color: #dc2626;">FIALA</span> | 
                    <span style="color: #2563eb;">TAIFA</span>
                </h1>
                <p style="font-size: 1.1rem; color: #6b7280; margin: 0.5rem 0;">
                    {tagline}
                </p>
                <p style="color: #9ca3af; margin: 0;">
                    {description}
                </p>
            </div>
            """.format(
                tagline=i18n.t("brand.tagline.fr"),
                description=i18n.t("brand.description")
            ), unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="text-align: center; padding: 1rem;">
                <h1 style="margin: 0; font-size: 2.5rem;">
                    <span style="color: #2563eb;">TAIFA</span> | 
                    <span style="color: #dc2626;">FIALA</span>
                </h1>
                <p style="font-size: 1.1rem; color: #6b7280; margin: 0.5rem 0;">
                    {tagline}
                </p>
                <p style="color: #9ca3af; margin: 0;">
                    {description}
                </p>
            </div>
            """.format(
                tagline=i18n.t("brand.tagline.en"),
                description=i18n.t("brand.description")
            ), unsafe_allow_html=True)

def format_date_localized(date_obj: datetime, i18n: TaifaI18n) -> str:
    """Format date according to current language"""
    if not date_obj:
        return ""
    
    current_lang = i18n.get_current_language()
    
    if current_lang == 'fr':
        # French date format: "15 juillet 2025"
        months_fr = [
            "janvier", "février", "mars", "avril", "mai", "juin",
            "juillet", "août", "septembre", "octobre", "novembre", "décembre"
        ]
        return f"{date_obj.day} {months_fr[date_obj.month - 1]} {date_obj.year}"
    else:
        # English date format: "July 15, 2025"
        return date_obj.strftime("%B %d, %Y")

def format_currency_localized(amount: str, i18n: TaifaI18n) -> str:
    """Format currency according to current language"""
    if not amount:
        return ""
    
    current_lang = i18n.get_current_language()
    
    # Extract numeric values and currency codes
    import re
    
    # Common patterns for amounts
    patterns = [
        r'(\$|USD)\s*([0-9,]+)',
        r'([0-9,]+)\s*(\$|USD)',
        r'(€|EUR)\s*([0-9,]+)',
        r'([0-9,]+)\s*(€|EUR)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, amount, re.IGNORECASE)
        if match:
            if current_lang == 'fr':
                # French number format: 1 000 000 €
                number = match.group(2) if match.group(1).isdigit() else match.group(1)
                currency = match.group(1) if match.group(2).isdigit() else match.group(2)
                
                # Convert to French number format
                number_formatted = number.replace(',', ' ')
                
                if currency.upper() in ['$', 'USD']:
                    return f"{number_formatted} USD"
                elif currency.upper() in ['€', 'EUR']:
                    return f"{number_formatted} €"
            else:
                # Keep original English format
                return amount
    
    return amount

def create_footer(i18n: TaifaI18n):
    """Create localized footer"""
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"**[{i18n.t('footer.about')}](#)**")
    
    with col2:
        st.markdown(f"**[{i18n.t('footer.contact')}](#)**")
    
    with col3:
        st.markdown(f"**[{i18n.t('footer.api')}](#)**")
    
    with col4:
        st.markdown(f"**[{i18n.t('footer.github')}](https://github.com/drjforrest/taifa)**")
    
    st.markdown(f"<div style='text-align: center; color: #6b7280; margin-top: 1rem;'>{i18n.t('footer.copyright')}</div>", 
                unsafe_allow_html=True)

# Global i18n instance
_i18n_instance = None

def get_i18n() -> TaifaI18n:
    """Get global i18n instance"""
    global _i18n_instance
    if _i18n_instance is None:
        _i18n_instance = TaifaI18n()
    return _i18n_instance

# Convenience function for templates
def t(key: str, **kwargs) -> str:
    """Quick translation function"""
    return get_i18n().t(key, **kwargs)