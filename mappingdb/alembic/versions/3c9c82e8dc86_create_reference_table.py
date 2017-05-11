"""
  The MIT License (MIT)
  Copyright (c) 2016 Intel Corporation

  Permission is hereby granted, free of charge, to any person obtaining a copy of 
  this software and associated documentation files (the "Software"), to deal in 
  the Software without restriction, including without limitation the rights to 
  use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of 
  the Software, and to permit persons to whom the Software is furnished to do so, 
  subject to the following conditions:

  The above copyright notice and this permission notice shall be included in all 
  copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS 
  FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR 
  COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER 
  IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN 
  CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

"""create reference table

Revision ID: 3c9c82e8dc86
Revises: 228ea4c8569d
Create Date: 2015-10-14 14:31:56.963260

"""

# revision identifiers, used by Alembic.
revision = '3c9c82e8dc86'
down_revision = '228ea4c8569d'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'reference',
        sa.Column('id', sa.BigInteger, primary_key=True),
        sa.Column('guid', sa.String(36), nullable=False, unique=True),
        sa.Column('length', sa.BigInteger),
        sa.Column('reference_set_id', sa.BigInteger,
                  sa.ForeignKey('reference_set.id'), nullable=False),
        sa.Column('md5_checksum', sa.String(32)),
        sa.Column('name', sa.Text),
        sa.Column('source_uri', sa.Text),
        sa.Column('is_derived', sa.Boolean),
        sa.Column('source_divergence', sa.Float),
        sa.Column('ncbi_taxon_id', sa.Integer),
        sa.Column('offset', sa.BigInteger)
    )


def downgrade():
    op.drop_table('reference')
