"""create field_set table

Revision ID: 4f93dc7aa8e8
Revises: 4631177f4ecc
Create Date: 2017-05-25 11:22:32.344826

"""

# revision identifiers, used by Alembic.
revision = '4f93dc7aa8e8'
down_revision = '4631177f4ecc'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    # making ontology terms strings for now
    # leaving out externalId, diseases, pheno, etc. mappings for now
    op.drop_table('field')
    op.create_table(
        'field_set',
        sa.Column('id', sa.BigInteger, primary_key=True),
        sa.Column('guid', sa.String(36), nullable=False, unique=True),
        sa.Column('description', sa.Text)
    )
    op.create_table(
        'field',
        sa.Column('id', sa.BigInteger, primary_key=True),
        sa.Column('guid', sa.String(36), nullable=False, unique=True),
        sa.Column('field', sa.String(32), nullable=False),
        sa.Column('field_set_id', sa.BigInteger, sa.ForeignKey('field_set.id'), nullable=False),
        sa.Column('type', sa.Enum('Integer', 'String', 'Float', 'Flag', name='type_enum')),
        sa.Column('is_filter', sa.Boolean, nullable=False),
        sa.Column('is_format', sa.Boolean, nullable=False),
        sa.Column('is_info', sa.Boolean, nullable=False),
        sa.Column('length_type', sa.Enum('A', 'R', 'G', 'VAR', 'NUM', name='length_enum')),
        sa.Column('length_intval', sa.Integer, default=0, server_default=sa.text('1')),
        sa.Column('field_combine_op', sa.Enum('sum', 'mean', 'median', 'move_to_FORMAT', 'element_wise_sum', 'concatenate', name='field_combine_optype'))
    )
    op.create_unique_constraint('unique_name_per_field_set_constraint', 'field', ['field_set_id', 'field'])
    op.add_column(u'db_array', sa.Column('field_set_id', sa.BigInteger, sa.ForeignKey('field_set.id'), nullable=False))

def downgrade():
    op.drop_constraint('unique_name_per_reference_set_constraint', 'field', type_='unique')
    op.drop_table('field')
    op.drop_table('field_set')
    op.create_table(
        'field',
        sa.Column('id', sa.BigInteger, primary_key=True),
        sa.Column('field', sa.Text, nullable=False)
    )
    op.drop_column(u'db_array', 'field_set_id')
