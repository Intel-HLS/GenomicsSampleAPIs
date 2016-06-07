"""individual name not nullable

Revision ID: 4631177f4ecc
Revises: 3f047f09d454
Create Date: 2016-03-22 15:00:29.916071

"""

# revision identifiers, used by Alembic.
revision = '4631177f4ecc'
down_revision = '3f047f09d454'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.alter_column('individual', 'name', nullable=False)

def downgrade():
    op.alter_column('individual', 'name', nullable=None)
