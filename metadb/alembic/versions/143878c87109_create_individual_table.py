"""create individual table

Revision ID: 143878c87109
Revises: 50b48155ef53
Create Date: 2015-10-13 14:43:59.099326

"""

# revision identifiers, used by Alembic.
revision = '143878c87109'
down_revision = '50b48155ef53'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    # making ontology terms strings for now
    # leaving out externalId, diseases, pheno, etc. mappings for now
    op.create_table(
        'individual',
        sa.Column('id', sa.BigInteger, primary_key=True),
        sa.Column('guid', sa.String(36), nullable=False, unique=True),
        sa.Column('name', sa.Text),
        sa.Column('info', sa.PickleType),
        sa.Column('record_create_time', sa.Text),
        sa.Column('record_update_time', sa.Text),
    )


def downgrade():
    op.drop_table('individual')
