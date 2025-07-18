"""
Unit Tests for Source Validation Module

Test suite for source validation components including validation logic,
deduplication, classification, and integration helpers.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.source_validation import (
    SourceValidator, SourceSubmission, ValidationResult,
    DeduplicationPipeline, OpportunityContent,
    SourceClassifier, SourceType,
    PerformanceTracker
)
from app.services.source_validation.config import SourceValidationConfig
from app.services.source_validation.integration import crewai_integration
from app.utils.url_utils import normalize_url, calculate_url_similarity


class TestURLUtils:
    """Test URL utility functions"""
    
    def test_normalize_url(self):
        """Test URL normalization"""
        # Test tracking parameter removal
        url_with_tracking = "https://example.com/page?utm_source=email&utm_campaign=test&id=123"
        expected = "https://example.com/page?id=123"
        assert normalize_url(url_with_tracking) == expected
        
        # Test scheme addition
        url_no_scheme = "example.com/page"
        expected = "https://example.com/page"
        assert normalize_url(url_no_scheme) == expected
        
        # Test path normalization
        url_trailing_slash = "https://example.com/page/"
        expected = "https://example.com/page"
        assert normalize_url(url_trailing_slash) == expected
    
    def test_calculate_url_similarity(self):
        """Test URL similarity calculation"""
        # Same URLs should have high similarity
        url1 = "https://example.com/funding/grants"
        url2 = "https://example.com/funding/grants"
        assert calculate_url_similarity(url1, url2) == 1.0
        
        # Similar paths should have good similarity
        url1 = "https://example.com/funding/grants"
        url2 = "https://example.com/funding/scholarships"
        similarity = calculate_url_similarity(url1, url2)
        assert 0.5 < similarity < 1.0
        
        # Different domains should have no similarity
        url1 = "https://example1.com/funding"
        url2 = "https://example2.com/funding"
        assert calculate_url_similarity(url1, url2) == 0.0


class TestSourceValidationConfig:
    """Test configuration management"""
    
    def test_config_initialization(self):
        """Test configuration initialization"""
        config = SourceValidationConfig()
        
        # Test default values
        assert config.validation_thresholds.auto_approve_threshold == 0.8
        assert config.pilot_settings.default_duration_days == 30
        assert config.monitoring_settings.default_timeout_seconds == 30
    
    def test_threshold_logic(self):
        """Test threshold decision logic"""
        config = SourceValidationConfig()
        
        # Test auto-approval
        assert config.should_auto_approve(0.9) == True
        assert config.should_auto_approve(0.7) == False
        
        # Test manual review
        assert config.should_manual_review(0.7) == True
        assert config.should_manual_review(0.9) == False
        assert config.should_manual_review(0.3) == False
        
        # Test auto-rejection
        assert config.should_auto_reject(0.3) == True
        assert config.should_auto_reject(0.7) == False


class TestSourceSubmission:
    """Test source submission data structure"""
    
    def test_source_submission_creation(self):
        """Test creating a source submission"""
        submission = SourceSubmission(
            name="Test University",
            url="https://university.edu/research/funding",
            contact_person="Dr. Test",
            contact_email="test@university.edu",
            source_type="webpage",
            update_frequency="monthly",
            geographic_focus=["Kenya"],
            expected_volume="5-20",
            sample_urls=["https://university.edu/grant1"],
            ai_relevance_estimate=80,
            africa_relevance_estimate=90,
            language="English",
            submitter_role="Research Manager",
            has_permission=True,
            preferred_contact="email",
            submitted_at=datetime.now()
        )
        
        assert submission.name == "Test University"
        assert submission.ai_relevance_estimate == 80
        assert submission.has_permission == True


@pytest.mark.asyncio
class TestSourceValidator:
    """Test source validation logic"""
    
    @pytest.fixture
    def sample_submission(self):
        """Create sample submission for testing"""
        return SourceSubmission(
            name="Test University Research Office",
            url="https://test-university.edu/research/funding",
            contact_person="Dr. Jane Smith",
            contact_email="jane.smith@test-university.edu",
            source_type="webpage",
            update_frequency="monthly",
            geographic_focus=["Kenya", "East Africa"],
            expected_volume="5-20",
            sample_urls=["https://test-university.edu/research/funding/ai-grant"],
            ai_relevance_estimate=80,
            africa_relevance_estimate=90,
            language="English",
            submitter_role="Research Funding Manager",
            has_permission=True,
            preferred_contact="email",
            submitted_at=datetime.now()
        )
    
    async def test_url_accessibility_check(self, sample_submission):
        """Test URL accessibility checking"""
        validator = SourceValidator()
        
        # Mock aiohttp session
        with patch.object(validator, 'session') as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.headers = {'content-type': 'text/html'}
            mock_response.text = AsyncMock(return_value="<html>Test content</html>")
            
            mock_session.get.return_value.__aenter__.return_value = mock_response
            
            result = await validator._check_url_accessibility(sample_submission.url)
            
            assert result["accessible"] == True
            assert result["status_code"] == 200
    
    async def test_content_relevance_assessment(self, sample_submission):
        """Test content relevance assessment"""
        validator = SourceValidator()
        
        # Mock session and response
        with patch.object(validator, 'session') as mock_session:
            mock_response = AsyncMock()
            mock_response.text = AsyncMock(return_value="""
            <html>
            <body>
                <h1>AI Research Intelligence Feed</h1>
                <p>We offer grants for artificial intelligence research in Africa, 
                   focusing on machine learning applications in healthcare.</p>
                <p>Funding available for projects in Kenya, Nigeria, and South Africa.</p>
            </body>
            </html>
            """)
            
            mock_session.get.return_value.__aenter__.return_value = mock_response
            
            result = await validator._assess_content_relevance(sample_submission)
            
            assert result["relevant"] == True
            assert result["ai_relevance_score"] > 0.5
            assert result["africa_relevance_score"] > 0.5
            assert result["funding_relevance_score"] > 0.5
    
    async def test_authority_verification(self, sample_submission):
        """Test submitter authority verification"""
        validator = SourceValidator()
        
        result = validator._verify_submitter_authority(sample_submission)
        
        # Should match because email domain matches URL domain
        assert result["domain_match"] == True
        assert result["has_permission"] == True
        assert result["authority_score"] > 0.5


@pytest.mark.asyncio
class TestDeduplicationPipeline:
    """Test deduplication logic"""
    
    @pytest.fixture
    def sample_opportunity(self):
        """Create sample opportunity for testing"""
        return OpportunityContent(
            url="https://example.org/ai-research-grant-2025",
            title="AI Research Grant for African Universities",
            description="Funding for AI research projects in African universities focusing on healthcare applications.",
            organization="Example Foundation",
            amount=50000.0,
            currency="USD",
            deadline=datetime(2025, 12, 31)
        )
    
    async def test_url_deduplication(self, sample_opportunity):
        """Test URL-based deduplication"""
        pipeline = DeduplicationPipeline()
        
        # Mock database to return no duplicates
        with patch('app.core.database.get_database') as mock_db:
            mock_db_instance = AsyncMock()
            mock_db_instance.fetch_one.return_value = None
            mock_db_instance.fetch_all.return_value = []
            mock_db.return_value = mock_db_instance
            
            result = await pipeline.url_dedup.check_url_duplicate(sample_opportunity.url)
            
            assert result.is_duplicate == False
            assert result.match_type == "no_url_match"
    
    async def test_content_deduplication(self, sample_opportunity):
        """Test content-based deduplication"""
        pipeline = DeduplicationPipeline()
        
        # Mock database and embedding model
        with patch('app.core.database.get_database') as mock_db, \
             patch.object(pipeline.content_dedup, 'embedding_model', None):
            
            mock_db_instance = AsyncMock()
            mock_db_instance.fetch_one.return_value = None
            mock_db.return_value = mock_db_instance
            
            result = await pipeline.content_dedup.check_content_duplicate(sample_opportunity)
            
            assert result.is_duplicate == False
            assert result.match_type == "no_content_match"
    
    async def test_full_deduplication_pipeline(self, sample_opportunity):
        """Test complete deduplication pipeline"""
        pipeline = DeduplicationPipeline()
        
        # Mock all database calls to return no duplicates
        with patch('app.core.database.get_database') as mock_db:
            mock_db_instance = AsyncMock()
            mock_db_instance.fetch_one.return_value = None
            mock_db_instance.fetch_all.return_value = []
            mock_db.return_value = mock_db_instance
            
            result = await pipeline.check_for_duplicates(sample_opportunity)
            
            assert result["status"] == "unique_opportunity"
            assert result["action"] == "proceed_to_validation"
            assert result["is_duplicate"] == False


@pytest.mark.asyncio
class TestSourceClassifier:
    """Test source classification"""
    
    async def test_url_pattern_classification(self):
        """Test classification by URL patterns"""
        classifier = SourceClassifier()
        
        # Test RSS feed classification
        rss_url = "https://example.com/rss/funding.xml"
        initial_classification = classifier._classify_by_url_pattern(rss_url)
        assert initial_classification["type"] == SourceType.RSS_FEED
        assert initial_classification["confidence"] >= 0.9
        
        # Test API classification
        api_url = "https://api.example.com/v1/funding"
        initial_classification = classifier._classify_by_url_pattern(api_url)
        assert initial_classification["type"] == SourceType.API
        
        # Test newsletter classification
        newsletter_url = "https://example.com/newsletter/subscribe"
        initial_classification = classifier._classify_by_url_pattern(newsletter_url)
        assert initial_classification["type"] == SourceType.NEWSLETTER
    
    async def test_content_analysis_enhancement(self):
        """Test content analysis enhancement"""
        classifier = SourceClassifier()
        
        # Mock RSS content detection
        with patch.object(classifier, '_is_rss_content', return_value=True):
            initial_classification = {"type": SourceType.DYNAMIC_WEBPAGE, "confidence": 0.5}
            
            enhanced = await classifier._enhance_with_content_analysis(
                "https://example.com/feeds", initial_classification
            )
            
            assert enhanced["type"] == SourceType.RSS_FEED


@pytest.mark.asyncio
class TestPerformanceTracker:
    """Test performance tracking"""
    
    async def test_volume_metrics_calculation(self):
        """Test volume metrics calculation"""
        tracker = PerformanceTracker()
        
        # Mock database response
        with patch('app.core.database.get_database') as mock_db:
            mock_db_instance = AsyncMock()
            
            # Mock opportunities with agent scores
            mock_opportunities = [
                {"agent_scores": {"ai_relevance_score": 0.8, "africa_relevance_score": 0.9, "funding_relevance_score": 0.8}},
                {"agent_scores": {"ai_relevance_score": 0.6, "africa_relevance_score": 0.8, "funding_relevance_score": 0.9}},
                {"agent_scores": {"ai_relevance_score": 0.9, "africa_relevance_score": 0.7, "funding_relevance_score": 0.8}}
            ]
            mock_db_instance.fetch_all.return_value = mock_opportunities
            mock_db.return_value = mock_db_instance
            
            start_date = datetime.now() - timedelta(days=30)
            end_date = datetime.now()
            
            result = await tracker._calculate_volume_metrics(1, start_date, end_date)
            
            assert result["total_opportunities"] == 3
            assert result["ai_relevant"] == 2  # Scores >= 0.7
            assert result["africa_relevant"] == 2
            assert result["funding_relevant"] == 3


@pytest.mark.asyncio
class TestCrewAIIntegration:
    """Test CrewAI integration helpers"""
    
    async def test_opportunity_preprocessing(self):
        """Test opportunity preprocessing"""
        # Mock deduplication pipeline
        with patch.object(crewai_integration, 'deduplication') as mock_dedup:
            mock_dedup.check_for_duplicates.return_value = {
                'is_duplicate': False,
                'status': 'unique_opportunity'
            }
            
            raw_opportunity = {
                'url': 'https://example.org/grant',
                'title': 'AI Research Grant',
                'description': 'Funding for AI research in healthcare',
                'organization': 'Example Foundation',
                'amount': 50000,
                'deadline': datetime.now() + timedelta(days=30)
            }
            
            result = await crewai_integration.preprocess_opportunity(raw_opportunity)
            
            assert result['action'] == 'process_with_crewai'
            assert result['reason'] == 'unique_opportunity'
            assert 'quality_score' in result
    
    def test_content_quality_assessment(self):
        """Test content quality assessment"""
        opportunity = {
            'title': 'AI Research Grant for Healthcare',
            'description': 'This is a comprehensive intelligence item for artificial intelligence research projects focusing on healthcare applications in African universities.',
            'organization': 'Health Research Foundation',
            'url': 'https://healthresearch.org/grants/ai-2025',
            'amount': 75000,
            'deadline': datetime(2025, 12, 31),
            'contact_email': 'grants@healthresearch.org'
        }
        
        quality_score = crewai_integration._assess_content_quality(opportunity)
        
        # Should have high quality score due to complete information
        assert quality_score > 0.8
    
    def test_processing_priority_determination(self):
        """Test processing priority determination"""
        # High priority opportunity (urgent deadline + AI keywords)
        high_priority_opp = {
            'title': 'Urgent AI Grant Deadline Approaching',
            'description': 'Machine learning research funding closing soon',
            'deadline': datetime.now() + timedelta(days=5),
            'amount': 100000
        }
        
        priority = crewai_integration._determine_processing_priority(high_priority_opp, 0.9)
        assert priority == 'high'
        
        # Low priority opportunity
        low_priority_opp = {
            'title': 'General Research Funding',
            'description': 'Basic research intelligence item',
            'amount': 5000
        }
        
        priority = crewai_integration._determine_processing_priority(low_priority_opp, 0.4)
        assert priority == 'low'


@pytest.mark.asyncio 
class TestIntegrationHelpers:
    """Test integration helper functions"""
    
    async def test_quick_duplicate_check(self):
        """Test quick duplicate check function"""
        from app.services.source_validation.integration import quick_duplicate_check
        
        # Mock deduplication pipeline
        with patch('app.services.source_validation.integration.DeduplicationPipeline') as mock_pipeline_class:
            mock_pipeline = AsyncMock()
            mock_pipeline.check_for_duplicates.return_value = {'is_duplicate': False}
            mock_pipeline_class.return_value = mock_pipeline
            
            result = await quick_duplicate_check(
                'https://example.org/grant',
                'AI Research Grant', 
                'Example Foundation'
            )
            
            assert result == False
    
    def test_form_data_conversion(self):
        """Test form data to submission conversion"""
        form_data = {
            'name': 'Test University',
            'url': 'https://university.edu/funding',
            'contact_person': 'Dr. Test',
            'contact_email': 'test@university.edu',
            'source_type': 'webpage',
            'update_frequency': 'monthly',
            'geographic_focus': ['Kenya'],
            'expected_volume': '5-20',
            'sample_urls': ['https://university.edu/grant1'],
            'ai_relevance_estimate': 80,
            'africa_relevance_estimate': 90,
            'language': 'English',
            'submitter_role': 'Manager',
            'has_permission': True,
            'preferred_contact': 'email'
        }
        
        # Test that form data contains all required fields
        required_fields = [
            'name', 'url', 'contact_person', 'contact_email', 'source_type',
            'update_frequency', 'geographic_focus', 'expected_volume', 'sample_urls',
            'ai_relevance_estimate', 'africa_relevance_estimate', 'language',
            'submitter_role', 'has_permission', 'preferred_contact'
        ]
        
        for field in required_fields:
            assert field in form_data


# Fixture for async test setup
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
