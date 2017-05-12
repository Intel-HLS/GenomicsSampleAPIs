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
from sqlalchemy.orm import backref
from sqlalchemy.orm import relationship

#Each row describes a GenomicsDS instance
#Each instance correponds to a single reference set
#Each instance consists of multiple partitions (possibly scattered across multiple nodes)

class GenomicsDSInstance(_Base):
    __tablename__ = "genomicsds_instance"
    id = sa.Column(BigInteger, primary_key=True)
    guid = sa.Column(sa.String(36), nullable=False, unique=True)
    reference_set_id = sa.Column(BigInteger, sa.ForeignKey('reference_set.id'), nullable=False)
    name = sa.Column(sa.Text, nullable=False)
    
    genomicsds_partitions = relationship('GenomicsDSPartition', backref='genomicsds_instance')
