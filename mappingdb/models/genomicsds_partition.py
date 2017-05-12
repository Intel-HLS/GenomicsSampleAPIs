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
from sqlalchemy import CheckConstraint
import enum

#Each row describes a GenomicsDS partition
#Each partition belongs to a single GenomicsDS instance
#Each partition is stored at a (workspace, DBarray) combination - might be extended to include object store
#later

class GenomicsDSPartition(_Base):
    __tablename__ = "genomicsds_partition"
    id = sa.Column(BigInteger, primary_key=True)
    guid = sa.Column(sa.String(36), nullable=False, unique=True)
    name = sa.Column(sa.Text, nullable=False)
    genomicsds_instance_id = sa.Column(BigInteger, sa.ForeignKey('genomicsds_instance.id'), nullable=False)
    data_store_type = sa.Column(sa.Enum('tiledb_on_disk_array', name='genomicsds_partition_data_store_types_enum'),
	nullable=False, server_default='tiledb_on_disk_array')
    workspace_id = sa.Column(BigInteger, sa.ForeignKey('workspace.id'))
    db_array_id = sa.Column(BigInteger, sa.ForeignKey('db_array.id'))
    
    __table_args__ = (
        CheckConstraint('data_store_type = \'tiledb_on_disk_array\' AND workspace_id IS NOT NULL AND db_array_id IS NOT NULL',
	    name='type_to_null_constraint'),
    )

