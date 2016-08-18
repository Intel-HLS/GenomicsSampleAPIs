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

from ..models import _Base, TextPickleType, BigInteger, autoinc_handler
import sqlalchemy as sa
from sqlalchemy.orm import backref
from sqlalchemy.orm import relationship
import json


class Sample(_Base):
    __tablename__ = "sample"
    sample_id_seq = sa.Sequence('sample_id_seq', minvalue=0, start=0)
    id = sa.Column(BigInteger, sample_id_seq, primary_key=True)
    guid = sa.Column(sa.String(36), nullable=False, unique=True)
    individual_id = sa.Column(BigInteger, sa.ForeignKey('individual.id'), nullable=False)
    name = sa.Column(sa.Text, nullable=False)
    info = sa.Column(TextPickleType(pickler=json))

# Handle auto-increment
autoinc_handler(
    Sample.__table__,
    '%(table)s',
    id_column_name='id',
    id_seq_name='sample_id_seq',
    insert_dict={
        'id': -1,
        'individual_id': -1,
        'name': None,
        'guid': None})
