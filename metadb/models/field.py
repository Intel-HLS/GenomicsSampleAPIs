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

from ..models import _Base, BigInteger
import sqlalchemy as sa
import enum

class Field(_Base):
    __tablename__ = "field"
    id = sa.Column(sa.BigInteger, primary_key=True)
    guid = sa.Column(sa.String(36), nullable=False, unique=True)
    field = sa.Column(sa.String(32), nullable=False)
    field_set_id = sa.Column(BigInteger, sa.ForeignKey('field_set.id'), nullable=False)
    # Unique constraint on (field_set_id, name)
    __table_args__ = (
        sa.UniqueConstraint('field_set_id', 'field',
            name='unique_name_per_field_set_constraint'),
    )
    type = sa.Column(sa.Enum('Integer', 'String', 'Float', 'Flag', name='type_enum'))
    is_filter = sa.Column(sa.Boolean, nullable=False)
    is_format = sa.Column(sa.Boolean, nullable=False)
    is_info = sa.Column(sa.Boolean, nullable=False)
    length_type = sa.Column(sa.Enum('A', 'R', 'G', 'VAR', 'NUM', name='length_enum'))
    length_intval = sa.Column(sa.Integer, default=1, server_default=sa.text('1'))
    field_combine_op = sa.Column(sa.Enum('sum', 'mean', 'median', 'move_to_FORMAT', 'element_wise_sum', 'concatenate', name='field_combine_optype'))
