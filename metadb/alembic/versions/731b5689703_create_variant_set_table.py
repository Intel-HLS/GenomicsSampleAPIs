"""create variant set table

Revision ID: 731b5689703
Revises: 166594568ee4
Create Date: 2015-10-14 07:43:32.249829

"""

# revision identifiers, used by Alembic.
revision = '731b5689703'
down_revision = '166594568ee4'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'variant_set',
        sa.Column('id', sa.BigInteger, primary_key=True),
        sa.Column('guid', sa.String(36), nullable=False, unique=True),
        sa.Column('name', sa.Text),
        sa.Column('reference_set_id', sa.BigInteger,
                  sa.ForeignKey('reference_set.id'), nullable=False),
        # should this be the workspace
        sa.Column('dataset_id', sa.Text),
        # variant set metadata should be it's own schema
        sa.Column('variant_set_metadata', sa.Text)
    )


def downgrade():
    op.drop_table('variant_set')
