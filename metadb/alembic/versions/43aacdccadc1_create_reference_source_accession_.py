"""create reference source accession association

Revision ID: 43aacdccadc1
Revises: 2734f68047f1
Create Date: 2015-10-14 18:59:30.350400

"""

# revision identifiers, used by Alembic.
revision = '43aacdccadc1'
down_revision = '2734f68047f1'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'reference_source_accession',
        sa.Column('reference_id', sa.BigInteger, sa.ForeignKey(
            'reference.id'), primary_key=True),
        sa.Column('source_accession_id', sa.BigInteger, sa.ForeignKey(
            'source_accession.id'), primary_key=True)
    )


def downgrade():
    op.drop_table('reference_source_accession')
