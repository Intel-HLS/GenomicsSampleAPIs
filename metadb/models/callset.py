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
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Sequence
import json


class CallSet(_Base):
    __tablename__ = "callset"
    callset_id_seq = Sequence('callset_id_seq', minvalue=0, start=0)
    id = sa.Column(BigInteger, callset_id_seq, primary_key=True)
    guid = sa.Column(sa.String(36), nullable=False, unique=True)
    source_sample_id = sa.Column(BigInteger, sa.ForeignKey(
        'sample.id', name='callset_source_sample_id_fkey'), nullable=False)
    target_sample_id = sa.Column(BigInteger, sa.ForeignKey(
        'sample.id', name='callset_target_sample_id_fkey'), nullable=False)
    name = sa.Column(sa.Text, nullable=False)
    created = sa.Column(BigInteger, nullable=False)
    updated = sa.Column(BigInteger, nullable=False)
    info = sa.Column(TextPickleType(pickler=json))

    db_array_associations = relationship(
        "CallSetToDBArrayAssociation", backref="callset")
    variant_sets = relationship(
        'VariantSet',
        secondary='callset_variant_set',
        backref=backref('CallSet'))

# Handle auto-increment
autoinc_handler(
    CallSet.__table__,
    '%(table)s',
    id_column_name='id',
    id_seq_name='callset_id_seq',
    insert_dict={
        'id': -1,
        'name': None,
        'guid': None,
        'source_sample_id': -1,
        'target_sample_id': -1,
        'created': -1,
        'updated': -1})
