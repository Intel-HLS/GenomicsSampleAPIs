"""create workspace table

Revision ID: bf433af33d4
Revises: 4db88f2382fb
Create Date: 2015-10-26 13:06:31.788743

"""

# revision identifiers, used by Alembic.
revision = 'bf433af33d4'
down_revision = '4db88f2382fb'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'workspace',
        sa.Column('id', sa.BigInteger, primary_key=True),
        sa.Column('guid', sa.String(36), nullable=False, unique=True),
        sa.Column('name', sa.Text, nullable=False)
    )


def downgrade():
    op.drop_table('workspace')
