"""ETL Pipeline Architecture Support

Revision ID: 004
Revises: 002
Create Date: 2024-01-16 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '004'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade():
    # Add ETL Pipeline fields to funding_opportunities table
    op.add_column('funding_opportunities', sa.Column('title_hash', sa.String(64), nullable=True))
    op.add_column('funding_opportunities', sa.Column('semantic_hash', sa.String(64), nullable=True))
    op.add_column('funding_opportunities', sa.Column('url_hash', sa.String(64), nullable=True))
    
    # Content classification fields
    op.add_column('funding_opportunities', sa.Column('content_type', sa.String(50), nullable=True, default='funding_opportunity'))
    op.add_column('funding_opportunities', sa.Column('content_classification_confidence', sa.Float(), nullable=True))
    op.add_column('funding_opportunities', sa.Column('classification_method', sa.String(50), nullable=True))
    
    # Validation tracking fields
    op.add_column('funding_opportunities', sa.Column('validation_status', sa.String(20), nullable=True, default='pending'))
    op.add_column('funding_opportunities', sa.Column('validation_confidence_score', sa.Float(), nullable=True))
    op.add_column('funding_opportunities', sa.Column('validation_flags', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('funding_opportunities', sa.Column('validation_notes', sa.Text(), nullable=True))
    op.add_column('funding_opportunities', sa.Column('validated_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('funding_opportunities', sa.Column('validated_by', sa.String(50), nullable=True))
    op.add_column('funding_opportunities', sa.Column('requires_human_review', sa.Boolean(), nullable=True, default=True))
    
    # Module tracking fields
    op.add_column('funding_opportunities', sa.Column('ingestion_module', sa.String(50), nullable=True))
    op.add_column('funding_opportunities', sa.Column('processing_id', sa.String(50), nullable=True))
    op.add_column('funding_opportunities', sa.Column('processing_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    
    # Create indexes for ETL fields
    op.create_index('idx_funding_opportunities_title_hash', 'funding_opportunities', ['title_hash'])
    op.create_index('idx_funding_opportunities_semantic_hash', 'funding_opportunities', ['semantic_hash'])
    op.create_index('idx_funding_opportunities_url_hash', 'funding_opportunities', ['url_hash'])
    op.create_index('idx_funding_opportunities_content_type', 'funding_opportunities', ['content_type'])
    op.create_index('idx_funding_opportunities_validation_status', 'funding_opportunities', ['validation_status'])
    op.create_index('idx_funding_opportunities_ingestion_module', 'funding_opportunities', ['ingestion_module'])
    op.create_index('idx_funding_opportunities_processing_id', 'funding_opportunities', ['processing_id'])
    
    # Create validation_results table
    op.create_table('validation_results',
        sa.Column('id', sa.String(50), nullable=False),
        sa.Column('opportunity_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(20), nullable=True, default='pending'),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('confidence_level', sa.String(10), nullable=True),
        sa.Column('completeness_score', sa.Float(), nullable=True),
        sa.Column('relevance_score', sa.Float(), nullable=True),
        sa.Column('legitimacy_score', sa.Float(), nullable=True),
        sa.Column('validation_flags', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('validation_notes', sa.Text(), nullable=True),
        sa.Column('auto_approval_eligible', sa.Boolean(), nullable=True, default=False),
        sa.Column('requires_human_review', sa.Boolean(), nullable=True, default=True),
        sa.Column('validator', sa.String(50), nullable=True, default='ai_system'),
        sa.Column('validated_by_user_id', sa.Integer(), nullable=True),
        sa.Column('processing_time', sa.Float(), nullable=True),
        sa.Column('validated_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('raw_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('validated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['opportunity_id'], ['funding_opportunities.id'], ),
        sa.ForeignKeyConstraint(['validated_by_user_id'], ['community_users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for validation_results
    op.create_index('idx_validation_results_opportunity_id', 'validation_results', ['opportunity_id'])
    op.create_index('idx_validation_results_status', 'validation_results', ['status'])
    op.create_index('idx_validation_results_confidence_score', 'validation_results', ['confidence_score'])
    op.create_index('idx_validation_results_confidence_level', 'validation_results', ['confidence_level'])
    
    # Create duplicate_detections table
    op.create_table('duplicate_detections',
        sa.Column('id', sa.String(50), nullable=False),
        sa.Column('original_opportunity_id', sa.Integer(), nullable=True),
        sa.Column('duplicate_opportunity_id', sa.Integer(), nullable=True),
        sa.Column('duplicate_type', sa.String(30), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('similarity_score', sa.Float(), nullable=True),
        sa.Column('action', sa.String(20), nullable=True),
        sa.Column('action_taken_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('action_taken_by', sa.String(50), nullable=True),
        sa.Column('detection_method', sa.String(50), nullable=True),
        sa.Column('detection_details', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('detected_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['duplicate_opportunity_id'], ['funding_opportunities.id'], ),
        sa.ForeignKeyConstraint(['original_opportunity_id'], ['funding_opportunities.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for duplicate_detections
    op.create_index('idx_duplicate_detections_original_opportunity_id', 'duplicate_detections', ['original_opportunity_id'])
    op.create_index('idx_duplicate_detections_duplicate_opportunity_id', 'duplicate_detections', ['duplicate_opportunity_id'])
    op.create_index('idx_duplicate_detections_duplicate_type', 'duplicate_detections', ['duplicate_type'])
    op.create_index('idx_duplicate_detections_confidence_score', 'duplicate_detections', ['confidence_score'])
    op.create_index('idx_duplicate_detections_action', 'duplicate_detections', ['action'])
    
    # Create processing_jobs table
    op.create_table('processing_jobs',
        sa.Column('id', sa.String(50), nullable=False),
        sa.Column('job_type', sa.String(30), nullable=True),
        sa.Column('module_type', sa.String(30), nullable=True),
        sa.Column('status', sa.String(20), nullable=True, default='queued'),
        sa.Column('priority', sa.Integer(), nullable=True, default=2),
        sa.Column('source_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('result_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=True, default=0),
        sa.Column('max_retries', sa.Integer(), nullable=True, default=3),
        sa.Column('processing_time', sa.Float(), nullable=True),
        sa.Column('items_processed', sa.Integer(), nullable=True, default=0),
        sa.Column('items_succeeded', sa.Integer(), nullable=True, default=0),
        sa.Column('items_failed', sa.Integer(), nullable=True, default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('failed_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for processing_jobs
    op.create_index('idx_processing_jobs_job_type', 'processing_jobs', ['job_type'])
    op.create_index('idx_processing_jobs_module_type', 'processing_jobs', ['module_type'])
    op.create_index('idx_processing_jobs_status', 'processing_jobs', ['status'])
    op.create_index('idx_processing_jobs_priority', 'processing_jobs', ['priority'])
    
    # Create module_health table
    op.create_table('module_health',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('module_type', sa.String(30), nullable=True),
        sa.Column('status', sa.String(20), nullable=True, default='active'),
        sa.Column('last_success', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_failure', sa.DateTime(timezone=True), nullable=True),
        sa.Column('success_count', sa.Integer(), nullable=True, default=0),
        sa.Column('failure_count', sa.Integer(), nullable=True, default=0),
        sa.Column('avg_processing_time', sa.Float(), nullable=True, default=0.0),
        sa.Column('quality_score', sa.Float(), nullable=True, default=0.0),
        sa.Column('circuit_breaker_open', sa.Boolean(), nullable=True, default=False),
        sa.Column('circuit_breaker_failures', sa.Integer(), nullable=True, default=0),
        sa.Column('circuit_breaker_threshold', sa.Integer(), nullable=True, default=5),
        sa.Column('enabled', sa.Boolean(), nullable=True, default=True),
        sa.Column('rate_limit', sa.Integer(), nullable=True, default=100),
        sa.Column('timeout', sa.Integer(), nullable=True, default=30),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('module_type')
    )
    
    # Create indexes for module_health
    op.create_index('idx_module_health_module_type', 'module_health', ['module_type'])
    op.create_index('idx_module_health_status', 'module_health', ['status'])
    
    # Create content_fingerprints table
    op.create_table('content_fingerprints',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('opportunity_id', sa.Integer(), nullable=True),
        sa.Column('title_hash', sa.String(64), nullable=True),
        sa.Column('content_hash', sa.String(64), nullable=True),
        sa.Column('semantic_hash', sa.String(64), nullable=True),
        sa.Column('url_hash', sa.String(64), nullable=True),
        sa.Column('signature_hash', sa.String(64), nullable=True),
        sa.Column('organization_name', sa.String(255), nullable=True),
        sa.Column('funding_amount', sa.Float(), nullable=True),
        sa.Column('funding_currency', sa.String(10), nullable=True),
        sa.Column('announcement_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deadline_date', sa.Date(), nullable=True),
        sa.Column('url_domain', sa.String(255), nullable=True),
        sa.Column('key_phrases', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('extraction_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['opportunity_id'], ['funding_opportunities.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('opportunity_id')
    )
    
    # Create indexes for content_fingerprints
    op.create_index('idx_content_fingerprints_opportunity_id', 'content_fingerprints', ['opportunity_id'])
    op.create_index('idx_content_fingerprints_title_hash', 'content_fingerprints', ['title_hash'])
    op.create_index('idx_content_fingerprints_content_hash', 'content_fingerprints', ['content_hash'])
    op.create_index('idx_content_fingerprints_semantic_hash', 'content_fingerprints', ['semantic_hash'])
    op.create_index('idx_content_fingerprints_url_hash', 'content_fingerprints', ['url_hash'])
    op.create_index('idx_content_fingerprints_signature_hash', 'content_fingerprints', ['signature_hash'])
    op.create_index('idx_content_fingerprints_organization_name', 'content_fingerprints', ['organization_name'])
    op.create_index('idx_content_fingerprints_funding_amount', 'content_fingerprints', ['funding_amount'])
    op.create_index('idx_content_fingerprints_url_domain', 'content_fingerprints', ['url_domain'])
    
    # Create source_quality table
    op.create_table('source_quality',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('source_name', sa.String(255), nullable=True),
        sa.Column('source_type', sa.String(30), nullable=True),
        sa.Column('accuracy_score', sa.Float(), nullable=True, default=0.0),
        sa.Column('duplicate_rate', sa.Float(), nullable=True, default=0.0),
        sa.Column('processing_success_rate', sa.Float(), nullable=True, default=0.0),
        sa.Column('content_relevance_score', sa.Float(), nullable=True, default=0.0),
        sa.Column('total_items_processed', sa.Integer(), nullable=True, default=0),
        sa.Column('successful_items', sa.Integer(), nullable=True, default=0),
        sa.Column('duplicate_items', sa.Integer(), nullable=True, default=0),
        sa.Column('invalid_items', sa.Integer(), nullable=True, default=0),
        sa.Column('last_processed', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('quality_grade', sa.String(1), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('source_name')
    )
    
    # Create indexes for source_quality
    op.create_index('idx_source_quality_source_name', 'source_quality', ['source_name'])
    op.create_index('idx_source_quality_source_type', 'source_quality', ['source_type'])
    op.create_index('idx_source_quality_quality_grade', 'source_quality', ['quality_grade'])
    
    # Create optimized compound indexes for common queries
    op.create_index('idx_funding_opportunities_validation_review', 'funding_opportunities', ['validation_status', 'requires_human_review'])
    op.create_index('idx_funding_opportunities_content_module', 'funding_opportunities', ['content_type', 'ingestion_module'])
    op.create_index('idx_funding_opportunities_validation_confidence', 'funding_opportunities', ['validation_status', 'validation_confidence_score'])
    
    # Create full-text search index for enhanced search
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_funding_opportunities_search_vector 
        ON funding_opportunities USING gin(to_tsvector('english', title || ' ' || COALESCE(description, '')))
    """)
    
    # Set default values for existing records
    op.execute("UPDATE funding_opportunities SET content_type = 'funding_opportunity' WHERE content_type IS NULL")
    op.execute("UPDATE funding_opportunities SET validation_status = 'pending' WHERE validation_status IS NULL")
    op.execute("UPDATE funding_opportunities SET requires_human_review = true WHERE requires_human_review IS NULL")


def downgrade():
    # Drop full-text search index
    op.drop_index('idx_funding_opportunities_search_vector', table_name='funding_opportunities')
    
    # Drop compound indexes
    op.drop_index('idx_funding_opportunities_validation_confidence', table_name='funding_opportunities')
    op.drop_index('idx_funding_opportunities_content_module', table_name='funding_opportunities')
    op.drop_index('idx_funding_opportunities_validation_review', table_name='funding_opportunities')
    
    # Drop source_quality table
    op.drop_table('source_quality')
    
    # Drop content_fingerprints table
    op.drop_table('content_fingerprints')
    
    # Drop module_health table
    op.drop_table('module_health')
    
    # Drop processing_jobs table
    op.drop_table('processing_jobs')
    
    # Drop duplicate_detections table
    op.drop_table('duplicate_detections')
    
    # Drop validation_results table
    op.drop_table('validation_results')
    
    # Drop ETL indexes from funding_opportunities
    op.drop_index('idx_funding_opportunities_processing_id', table_name='funding_opportunities')
    op.drop_index('idx_funding_opportunities_ingestion_module', table_name='funding_opportunities')
    op.drop_index('idx_funding_opportunities_validation_status', table_name='funding_opportunities')
    op.drop_index('idx_funding_opportunities_content_type', table_name='funding_opportunities')
    op.drop_index('idx_funding_opportunities_url_hash', table_name='funding_opportunities')
    op.drop_index('idx_funding_opportunities_semantic_hash', table_name='funding_opportunities')
    op.drop_index('idx_funding_opportunities_title_hash', table_name='funding_opportunities')
    
    # Drop ETL columns from funding_opportunities
    op.drop_column('funding_opportunities', 'processing_metadata')
    op.drop_column('funding_opportunities', 'processing_id')
    op.drop_column('funding_opportunities', 'ingestion_module')
    op.drop_column('funding_opportunities', 'requires_human_review')
    op.drop_column('funding_opportunities', 'validated_by')
    op.drop_column('funding_opportunities', 'validated_at')
    op.drop_column('funding_opportunities', 'validation_notes')
    op.drop_column('funding_opportunities', 'validation_flags')
    op.drop_column('funding_opportunities', 'validation_confidence_score')
    op.drop_column('funding_opportunities', 'validation_status')
    op.drop_column('funding_opportunities', 'classification_method')
    op.drop_column('funding_opportunities', 'content_classification_confidence')
    op.drop_column('funding_opportunities', 'content_type')
    op.drop_column('funding_opportunities', 'url_hash')
    op.drop_column('funding_opportunities', 'semantic_hash')
    op.drop_column('funding_opportunities', 'title_hash')