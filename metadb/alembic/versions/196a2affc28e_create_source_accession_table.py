"""create source accession table

Revision ID: 196a2affc28e
Revises: 3c9c82e8dc86
Create Date: 2015-10-14 18:10:51.705014

"""

# revision identifiers, used by Alembic.
revision = '196a2affc28e'
down_revision = '3c9c82e8dc86'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'source_accession',
        sa.Column('id', sa.BigInteger, primary_key=True),
        sa.Column('accession_id', sa.Text, nullable=False)
    )

def downgrade():
    op.drop_table('source_accession')
