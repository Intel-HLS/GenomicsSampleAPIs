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
