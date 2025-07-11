-- TAIFA-FIALA Multilingual Database Schema Enhancement
-- Implementation Date: July 11, 2025

-- =======================================================
-- TRANSLATION INFRASTRUCTURE TABLES
-- =======================================================

-- Core translations table for all multilingual content
CREATE TABLE IF NOT EXISTS translations (
    id SERIAL PRIMARY KEY,
    source_table VARCHAR(50) NOT NULL,
    source_id INTEGER NOT NULL,
    source_field VARCHAR(50) NOT NULL,
    target_language VARCHAR(5) NOT NULL,
    original_text TEXT,
    translated_text TEXT,
    translation_service VARCHAR(20),
    confidence_score FLOAT DEFAULT 0.0,
    human_reviewed BOOLEAN DEFAULT FALSE,
    review_feedback TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Ensure unique translations per source+field+language
    UNIQUE(source_table, source_id, source_field, target_language)
);

-- Supported languages configuration
CREATE TABLE IF NOT EXISTS supported_languages (
    code VARCHAR(5) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    native_name VARCHAR(100) NOT NULL,
    flag_emoji VARCHAR(10),
    is_active BOOLEAN DEFAULT TRUE,
    translation_priority INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Translation queue for batch processing
CREATE TABLE IF NOT EXISTS translation_queue (
    id SERIAL PRIMARY KEY,
    source_table VARCHAR(50) NOT NULL,
    source_id INTEGER NOT NULL,
    source_field VARCHAR(50) NOT NULL,
    target_language VARCHAR(5) NOT NULL,
    priority INTEGER DEFAULT 1, -- 1=low, 2=medium, 3=high, 4=urgent
    status VARCHAR(20) DEFAULT 'pending', -- pending, processing, completed, failed
    attempts INTEGER DEFAULT 0,
    max_attempts INTEGER DEFAULT 3,
    error_message TEXT,
    scheduled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Prevent duplicate queue entries
    UNIQUE(source_table, source_id, source_field, target_language)
);

-- Translation services configuration and monitoring
CREATE TABLE IF NOT EXISTS translation_services (
    id SERIAL PRIMARY KEY,
    service_name VARCHAR(50) UNIQUE NOT NULL,
    api_endpoint VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,
    daily_quota INTEGER,
    daily_usage INTEGER DEFAULT 0,
    cost_per_character DECIMAL(6,4),
    quality_score FLOAT DEFAULT 0.0,
    avg_response_time INTEGER DEFAULT 0, -- milliseconds
    last_reset_date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =======================================================
-- ENHANCED FUNDING OPPORTUNITIES TABLE
-- =======================================================

-- Add language detection and translation status to existing table
ALTER TABLE funding_opportunities 
ADD COLUMN IF NOT EXISTS detected_language VARCHAR(5) DEFAULT 'en',
ADD COLUMN IF NOT EXISTS translation_status JSONB DEFAULT '{"en": "original"}',
ADD COLUMN IF NOT EXISTS is_multilingual BOOLEAN DEFAULT FALSE;

-- =======================================================
-- INITIAL DATA SETUP
-- =======================================================

-- Insert supported languages
INSERT INTO supported_languages (code, name, native_name, flag_emoji, is_active, translation_priority) VALUES
('en', 'English', 'English', '🇬🇧', TRUE, 1),
('fr', 'French', 'Français', '🇫🇷', TRUE, 1),
('ar', 'Arabic', 'العربية', '🇸🇦', FALSE, 2),
('pt', 'Portuguese', 'Português', '🇵🇹', FALSE, 2),
('sw', 'Swahili', 'Kiswahili', '🇹🇿', FALSE, 3)
ON CONFLICT (code) DO UPDATE SET
    name = EXCLUDED.name,
    native_name = EXCLUDED.native_name,
    flag_emoji = EXCLUDED.flag_emoji,
    is_active = EXCLUDED.is_active,
    translation_priority = EXCLUDED.translation_priority;

-- Insert translation services configuration
INSERT INTO translation_services (service_name, is_active, daily_quota, cost_per_character, quality_score) VALUES
('azure_translator', TRUE, 2000000, 0.00001, 0.92),
('google_translate', TRUE, 500000, 0.000020, 0.89),
('deepl', TRUE, 500000, 0.000025, 0.95),
('openai_gpt4', TRUE, 100000, 0.000150, 0.97)
ON CONFLICT (service_name) DO UPDATE SET
    is_active = EXCLUDED.is_active,
    daily_quota = EXCLUDED.daily_quota,
    cost_per_character = EXCLUDED.cost_per_character,
    quality_score = EXCLUDED.quality_score;

-- =======================================================
-- INDEXES FOR PERFORMANCE
-- =======================================================

-- Indexes for translations table
CREATE INDEX IF NOT EXISTS idx_translations_source ON translations(source_table, source_id);
CREATE INDEX IF NOT EXISTS idx_translations_language ON translations(target_language);
CREATE INDEX IF NOT EXISTS idx_translations_status ON translations(human_reviewed);

-- Indexes for translation queue
CREATE INDEX IF NOT EXISTS idx_translation_queue_status ON translation_queue(status);
CREATE INDEX IF NOT EXISTS idx_translation_queue_priority ON translation_queue(priority, scheduled_at);
CREATE INDEX IF NOT EXISTS idx_translation_queue_source ON translation_queue(source_table, source_id);

-- Indexes for funding opportunities language features
CREATE INDEX IF NOT EXISTS idx_funding_language ON funding_opportunities(detected_language);
CREATE INDEX IF NOT EXISTS idx_funding_multilingual ON funding_opportunities(is_multilingual);

-- =======================================================
-- HELPER FUNCTIONS
-- =======================================================

-- Function to get translated content with fallback
CREATE OR REPLACE FUNCTION get_translated_text(
    p_source_table VARCHAR(50),
    p_source_id INTEGER,
    p_source_field VARCHAR(50),
    p_target_language VARCHAR(5),
    p_fallback_text TEXT DEFAULT NULL
) RETURNS TEXT AS $$
DECLARE
    translated_text TEXT;
BEGIN
    -- Try to get translation
    SELECT t.translated_text INTO translated_text
    FROM translations t
    WHERE t.source_table = p_source_table
    AND t.source_id = p_source_id
    AND t.source_field = p_source_field
    AND t.target_language = p_target_language
    AND t.translated_text IS NOT NULL;
    
    -- Return translation if found, otherwise fallback
    RETURN COALESCE(translated_text, p_fallback_text);
END;
$$ LANGUAGE plpgsql;

-- Function to queue content for translation
CREATE OR REPLACE FUNCTION queue_for_translation(
    p_source_table VARCHAR(50),
    p_source_id INTEGER,
    p_source_field VARCHAR(50),
    p_target_language VARCHAR(5),
    p_priority INTEGER DEFAULT 1
) RETURNS BOOLEAN AS $$
BEGIN
    INSERT INTO translation_queue (
        source_table, source_id, source_field, 
        target_language, priority
    ) VALUES (
        p_source_table, p_source_id, p_source_field,
        p_target_language, p_priority
    ) ON CONFLICT (source_table, source_id, source_field, target_language) 
    DO UPDATE SET 
        priority = GREATEST(translation_queue.priority, EXCLUDED.priority),
        status = CASE 
            WHEN translation_queue.status = 'failed' THEN 'pending'
            ELSE translation_queue.status
        END;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- =======================================================
-- TRANSLATION STATUS UPDATE TRIGGERS
-- =======================================================

-- Function to update translation status in funding_opportunities
CREATE OR REPLACE FUNCTION update_translation_status() RETURNS TRIGGER AS $$
DECLARE
    source_record RECORD;
    lang_status JSONB;
BEGIN
    -- Get the source record
    EXECUTE format('SELECT * FROM %I WHERE id = %s', NEW.source_table, NEW.source_id) INTO source_record;
    
    -- Update translation status
    IF NEW.source_table = 'funding_opportunities' THEN
        -- Get current translation status
        SELECT translation_status INTO lang_status
        FROM funding_opportunities 
        WHERE id = NEW.source_id;
        
        -- Update status for this language
        lang_status = COALESCE(lang_status, '{}'::jsonb) || 
                     jsonb_build_object(NEW.target_language, 'translated');
        
        -- Update the record
        UPDATE funding_opportunities 
        SET translation_status = lang_status,
            is_multilingual = (jsonb_object_keys(lang_status)::TEXT[] && ARRAY['en', 'fr'])
        WHERE id = NEW.source_id;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for translation status updates
DROP TRIGGER IF EXISTS trigger_update_translation_status ON translations;
CREATE TRIGGER trigger_update_translation_status
    AFTER INSERT OR UPDATE ON translations
    FOR EACH ROW
    EXECUTE FUNCTION update_translation_status();

-- =======================================================
-- VIEWS FOR EASY ACCESS
-- =======================================================

-- Bilingual funding opportunities view
CREATE OR REPLACE VIEW funding_opportunities_bilingual AS
SELECT 
    fo.id,
    fo.title as title_original,
    get_translated_text('funding_opportunities', fo.id, 'title', 'fr', fo.title) as title_fr,
    fo.description as description_original,
    get_translated_text('funding_opportunities', fo.id, 'description', 'fr', fo.description) as description_fr,
    fo.source_url,
    fo.funding_amount,
    fo.deadline,
    fo.organization_name,
    fo.source_type,
    fo.source_name,
    fo.detected_language,
    fo.translation_status,
    fo.is_multilingual,
    fo.discovered_date as created_at,
    fo.last_updated as updated_at
FROM funding_opportunities fo;

-- Translation queue summary view
CREATE OR REPLACE VIEW translation_queue_summary AS
SELECT 
    status,
    target_language,
    priority,
    COUNT(*) as queue_count,
    MIN(scheduled_at) as oldest_request,
    MAX(scheduled_at) as newest_request
FROM translation_queue
GROUP BY status, target_language, priority
ORDER BY priority DESC, status, target_language;

-- Daily translation service usage view
CREATE OR REPLACE VIEW translation_service_usage AS
SELECT 
    service_name,
    daily_quota,
    daily_usage,
    ROUND((daily_usage::NUMERIC / daily_quota * 100), 2) as usage_percentage,
    (daily_quota - daily_usage) as remaining_quota,
    quality_score,
    avg_response_time,
    is_active
FROM translation_services
ORDER BY usage_percentage DESC;

-- =======================================================
-- SUCCESS MESSAGE
-- =======================================================

DO $$ 
BEGIN 
    RAISE NOTICE '✅ TAIFA-FIALA Multilingual Database Schema Enhancement Complete!';
    RAISE NOTICE '📊 Tables Created: translations, supported_languages, translation_queue, translation_services';
    RAISE NOTICE '🔍 Views Created: funding_opportunities_bilingual, translation_queue_summary, translation_service_usage';
    RAISE NOTICE '⚡ Functions Created: get_translated_text(), queue_for_translation()';
    RAISE NOTICE '🎯 Ready for: English ↔ French translation pipeline';
END $$;