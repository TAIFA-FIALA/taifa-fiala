"""add organization_id foreign key

Revision ID: 001
Revises: 
Create Date: 2025-01-12 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add organization_id foreign key column to africa_intelligence_feed table"""
    # Add organization_id column
    op.add_column('africa_intelligence_feed', 
                  sa.Column('organization_id', sa.Integer(), nullable=True))
    
    # Add foreign key constraint
    op.create_foreign_key('fk_africa_intelligence_feed_organization_id',
                         'africa_intelligence_feed', 'organizations',
                         ['organization_id'], ['id'])
    
    # Add index for performance
    op.create_index('idx_africa_intelligence_feed_organization_id',
                   'africa_intelligence_feed', ['organization_id'])


def downgrade() -> None:
    """Remove organization_id foreign key column"""
    # Drop index
    op.drop_index('idx_africa_intelligence_feed_organization_id', 
                  table_name='africa_intelligence_feed')
    
    # Drop foreign key constraint
    op.drop_constraint('fk_africa_intelligence_feed_organization_id',
                       'africa_intelligence_feed', type_='foreignkey')
    
    # Drop column
    op.drop_column('africa_intelligence_feed', 'organization_id')
