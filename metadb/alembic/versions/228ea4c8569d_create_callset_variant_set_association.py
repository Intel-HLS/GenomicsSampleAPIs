"""create callset variant set association

Revision ID: 228ea4c8569d
Revises: 731b5689703
Create Date: 2015-10-14 08:39:28.939435

"""

# revision identifiers, used by Alembic.
revision = '228ea4c8569d'
down_revision = '731b5689703'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'callset_variant_set',
        sa.Column('callset_id', sa.BigInteger, sa.ForeignKey(
            'callset.id'), primary_key=True),
        sa.Column('variant_set_id', sa.BigInteger, sa.ForeignKey(
            'variant_set.id'), primary_key=True)
    )


def downgrade():
    op.drop_table('callset_variant_set')
