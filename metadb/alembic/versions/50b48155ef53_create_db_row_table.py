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

"""create db row table

Revision ID: 50b48155ef53
Revises: 37ec9fe97cbf
Create Date: 2015-10-09 13:21:34.198137

"""

# revision identifiers, used by Alembic.
revision = '50b48155ef53'
down_revision = '37ec9fe97cbf'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy import UniqueConstraint
from sqlalchemy.schema import CreateSequence, Sequence


def upgrade():
    op.execute(
        CreateSequence(
            Sequence('db_row_tile_row_id_seq', minvalue=0, start=0, increment=1)
        )
    )
    op.create_table(
        'db_row',
        sa.Column('id', sa.BigInteger, primary_key=True),
        sa.Column('db_array_id', sa.BigInteger, sa.ForeignKey('db_array.id'), nullable=False),
        sa.Column('tile_row_id', sa.BigInteger, Sequence(
            'db_row_tile_row_id_seq'), nullable=False)
    )


def downgrade():
    op.execute(DropSequence('db_row_tile_row_id_seq'))
    op.drop_table('db_row')
