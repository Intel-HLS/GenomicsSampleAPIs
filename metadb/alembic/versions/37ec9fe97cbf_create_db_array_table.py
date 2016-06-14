"""create db array table

Revision ID: 37ec9fe97cbf
Revises: bf433af33d4
Create Date: 2015-10-09 11:35:03.740259

"""

# revision identifiers, used by Alembic.
revision = '37ec9fe97cbf'
down_revision = 'bf433af33d4'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'db_array',
        sa.Column('id', sa.BigInteger, primary_key=True),
        sa.Column('guid', sa.String(36), nullable=False, unique=True),
        sa.Column('reference_set_id', sa.BigInteger,
                  sa.ForeignKey('reference_set.id'), nullable=False),
        sa.Column('workspace_id', sa.BigInteger,
                  sa.ForeignKey('workspace.id'), nullable=False),
        sa.Column('name', sa.Text, nullable=False)
    )


def downgrade():
    op.drop_table('db_array')
