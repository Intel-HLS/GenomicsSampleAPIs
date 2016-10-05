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

"""create callset table

Revision ID: 166594568ee4
Revises: 143878c87109
Create Date: 2015-10-13 09:22:05.369939

"""

# revision identifiers, used by Alembic.
revision = '166594568ee4'
down_revision = '143878c87109'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.schema import CreateSequence, Sequence


def upgrade():
    op.execute(CreateSequence(Sequence('callset_id_seq', minvalue=0, start=0)))
    op.create_table(
        'callset',
        sa.Column('id', sa.BigInteger, Sequence('callset_id_seq'), primary_key=True),
        sa.Column('guid', sa.String(36), nullable=False, unique=True),
        sa.Column('individual_id', sa.BigInteger, sa.ForeignKey('individual.id'), nullable=False),
        sa.Column('dbrow_id', sa.BigInteger, sa.ForeignKey('db_row.id'), nullable=False),
        sa.Column('name', sa.Text, nullable=False),
        sa.Column('created', sa.BigInteger, nullable=False),
        sa.Column('updated', sa.BigInteger, nullable=False),
        sa.Column('info', sa.PickleType)
    )


def downgrade():
    op.execute(DropSequence('callset'))
    op.drop_table('callset')
