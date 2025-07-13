"""Enhanced schema migration - Core tables and lookup data

Revision ID: 002
Revises: 001
Create Date: 2025-01-12 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add enhanced schema based on competitor analysis and Notion alignment"""
    
    # Create lookup tables first
    
    # 1. Funding Types Table
    op.create_table('funding_types',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('typical_amount_range', sa.String(100)),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    # 2. AI Domains Table
    op.create_table('ai_domains',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('parent_domain_id', sa.Integer()),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['parent_domain_id'], ['ai_domains.id']),
        sa.UniqueConstraint('name')
    )
    
    # 3. Geographic Scopes Table
    op.create_table('geographic_scopes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('code', sa.String(10)),  # ISO country code
        sa.Column('type', sa.String(20), default='country'),  # country, region, continent
        sa.Column('parent_scope_id', sa.Integer()),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['parent_scope_id'], ['geographic_scopes.id']),
        sa.UniqueConstraint('name')
    )
    
    # 4. Community Users Table
    op.create_table('community_users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(50)),
        sa.Column('email', sa.String(255)),
        sa.Column('reputation_score', sa.Integer(), default=0),
        sa.Column('contributions_count', sa.Integer(), default=0),
        sa.Column('is_verified', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
        sa.UniqueConstraint('email')
    )
    
    # Add new columns to funding_opportunities table
    op.add_column('funding_opportunities', 
                  sa.Column('type_id', sa.Integer()))
    op.add_column('funding_opportunities', 
                  sa.Column('status', sa.String(20), default='open'))
    op.add_column('funding_opportunities', 
                  sa.Column('currency', sa.String(10), default='USD'))
    op.add_column('funding_opportunities', 
                  sa.Column('community_rating', sa.Numeric(2,1)))
    op.add_column('funding_opportunities', 
                  sa.Column('application_tips', sa.Text()))
    op.add_column('funding_opportunities', 
                  sa.Column('submitted_by_user_id', sa.Integer()))
    op.add_column('funding_opportunities', 
                  sa.Column('view_count', sa.Integer(), default=0))
    op.add_column('funding_opportunities', 
                  sa.Column('application_count', sa.Integer(), default=0))
    op.add_column('funding_opportunities', 
                  sa.Column('tags', postgresql.JSONB()))
    
    # Add computed deadline urgency column
    op.execute("""
        ALTER TABLE funding_opportunities 
        ADD COLUMN deadline_urgency VARCHAR(10) 
        GENERATED ALWAYS AS (
            CASE 
                WHEN deadline IS NULL THEN 'unknown'
                WHEN deadline <= CURRENT_DATE THEN 'expired'
                WHEN deadline <= CURRENT_DATE + INTERVAL '30 days' THEN 'urgent'
                WHEN deadline <= CURRENT_DATE + INTERVAL '60 days' THEN 'moderate'
                ELSE 'low'
            END
        ) STORED
    """)
    
    # Add foreign key constraints for funding_opportunities
    op.create_foreign_key('fk_funding_opportunities_type_id',
                         'funding_opportunities', 'funding_types',
                         ['type_id'], ['id'])
    op.create_foreign_key('fk_funding_opportunities_submitted_by_user_id',
                         'funding_opportunities', 'community_users',
                         ['submitted_by_user_id'], ['id'])
    
    # Add enhanced columns to organizations table
    op.add_column('organizations', 
                  sa.Column('ai_relevance_score', sa.Integer(), default=0))
    op.add_column('organizations', 
                  sa.Column('africa_relevance_score', sa.Integer(), default=0))
    op.add_column('organizations', 
                  sa.Column('source_type', sa.String(20), default='manual'))
    op.add_column('organizations', 
                  sa.Column('update_frequency', sa.String(20)))
    op.add_column('organizations', 
                  sa.Column('funding_announcement_url', sa.Text()))
    op.add_column('organizations', 
                  sa.Column('monitoring_status', sa.String(20), default='active'))
    op.add_column('organizations', 
                  sa.Column('monitoring_reliability', sa.Integer(), default=100))
    op.add_column('organizations', 
                  sa.Column('contact_person', sa.String(255)))
    op.add_column('organizations', 
                  sa.Column('contact_email', sa.String(255)))
    op.add_column('organizations', 
                  sa.Column('community_rating', sa.Numeric(2,1)))
    
    # Performance metrics for organizations
    op.add_column('organizations', 
                  sa.Column('opportunities_discovered', sa.Integer(), default=0))
    op.add_column('organizations', 
                  sa.Column('unique_opportunities_added', sa.Integer(), default=0))
    op.add_column('organizations', 
                  sa.Column('duplicate_rate', sa.Integer(), default=0))
    op.add_column('organizations', 
                  sa.Column('data_completeness_score', sa.Integer(), default=0))
    
    # Create junction tables for many-to-many relationships
    
    # Funding Opportunities <-> AI Domains
    op.create_table('funding_opportunity_ai_domains',
        sa.Column('funding_opportunity_id', sa.Integer(), nullable=False),
        sa.Column('ai_domain_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['funding_opportunity_id'], ['funding_opportunities.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['ai_domain_id'], ['ai_domains.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('funding_opportunity_id', 'ai_domain_id')
    )
    
    # Funding Opportunities <-> Geographic Scopes
    op.create_table('funding_opportunity_geographic_scopes',
        sa.Column('funding_opportunity_id', sa.Integer(), nullable=False),
        sa.Column('geographic_scope_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['funding_opportunity_id'], ['funding_opportunities.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['geographic_scope_id'], ['geographic_scopes.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('funding_opportunity_id', 'geographic_scope_id')
    )
    
    # Organizations <-> Geographic Focus
    op.create_table('organization_geographic_focus',
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('geographic_scope_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['geographic_scope_id'], ['geographic_scopes.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('organization_id', 'geographic_scope_id')
    )
    
    # Create indexes for performance
    op.create_index('idx_funding_opportunities_type_id', 'funding_opportunities', ['type_id'])
    op.create_index('idx_funding_opportunities_status', 'funding_opportunities', ['status'])
    op.create_index('idx_funding_opportunities_deadline_urgency', 'funding_opportunities', ['deadline_urgency'])
    op.create_index('idx_funding_opportunities_community_rating', 'funding_opportunities', ['community_rating'])
    op.create_index('idx_organizations_ai_relevance_score', 'organizations', ['ai_relevance_score'])
    op.create_index('idx_organizations_africa_relevance_score', 'organizations', ['africa_relevance_score'])
    op.create_index('idx_organizations_monitoring_status', 'organizations', ['monitoring_status'])


def downgrade() -> None:
    """Remove enhanced schema changes"""
    
    # Drop indexes
    op.drop_index('idx_organizations_monitoring_status', table_name='organizations')
    op.drop_index('idx_organizations_africa_relevance_score', table_name='organizations')
    op.drop_index('idx_organizations_ai_relevance_score', table_name='organizations')
    op.drop_index('idx_funding_opportunities_community_rating', table_name='funding_opportunities')
    op.drop_index('idx_funding_opportunities_deadline_urgency', table_name='funding_opportunities')
    op.drop_index('idx_funding_opportunities_status', table_name='funding_opportunities')
    op.drop_index('idx_funding_opportunities_type_id', table_name='funding_opportunities')
    
    # Drop junction tables
    op.drop_table('organization_geographic_focus')
    op.drop_table('funding_opportunity_geographic_scopes')
    op.drop_table('funding_opportunity_ai_domains')
    
    # Drop foreign key constraints
    op.drop_constraint('fk_funding_opportunities_submitted_by_user_id', 'funding_opportunities', type_='foreignkey')
    op.drop_constraint('fk_funding_opportunities_type_id', 'funding_opportunities', type_='foreignkey')
    
    # Drop columns from organizations
    op.drop_column('organizations', 'data_completeness_score')
    op.drop_column('organizations', 'duplicate_rate')
    op.drop_column('organizations', 'unique_opportunities_added')
    op.drop_column('organizations', 'opportunities_discovered')
    op.drop_column('organizations', 'community_rating')
    op.drop_column('organizations', 'contact_email')
    op.drop_column('organizations', 'contact_person')
    op.drop_column('organizations', 'monitoring_reliability')
    op.drop_column('organizations', 'monitoring_status')
    op.drop_column('organizations', 'funding_announcement_url')
    op.drop_column('organizations', 'update_frequency')
    op.drop_column('organizations', 'source_type')
    op.drop_column('organizations', 'africa_relevance_score')
    op.drop_column('organizations', 'ai_relevance_score')
    
    # Drop columns from funding_opportunities
    op.drop_column('funding_opportunities', 'deadline_urgency')
    op.drop_column('funding_opportunities', 'tags')
    op.drop_column('funding_opportunities', 'application_count')
    op.drop_column('funding_opportunities', 'view_count')
    op.drop_column('funding_opportunities', 'submitted_by_user_id')
    op.drop_column('funding_opportunities', 'application_tips')
    op.drop_column('funding_opportunities', 'community_rating')
    op.drop_column('funding_opportunities', 'currency')
    op.drop_column('funding_opportunities', 'status')
    op.drop_column('funding_opportunities', 'type_id')
    
    # Drop lookup tables
    op.drop_table('community_users')
    op.drop_table('geographic_scopes')
    op.drop_table('ai_domains')
    op.drop_table('funding_types')
