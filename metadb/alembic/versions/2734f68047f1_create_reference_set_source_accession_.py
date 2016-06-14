"""create reference set source accession association

Revision ID: 2734f68047f1
Revises: 196a2affc28e
Create Date: 2015-10-14 18:54:30.534072

"""

# revision identifiers, used by Alembic.
revision = '2734f68047f1'
down_revision = '196a2affc28e'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'reference_set_source_accession',
        sa.Column('reference_set_id', sa.BigInteger, sa.ForeignKey('reference_set.id'), primary_key=True),
        sa.Column('source_accession_id', sa.BigInteger, sa.ForeignKey('source_accession.id'), primary_key=True)
    )

def downgrade():
    op.drop_table('reference_set_source_accession')
