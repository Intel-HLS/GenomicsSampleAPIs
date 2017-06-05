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


from sqlalchemy.ext.declarative import declarative_base

_Base = declarative_base()

tiledb_reference_offset_padding_factor_default = 1.1


def get_tiledb_padded_reference_length_string(reference_length_str):
    return (
        'CAST( CAST(%s AS DOUBLE PRECISION)*(SELECT tiledb_reference_offset_padding_factor FROM reference_set WHERE id=NEW.reference_set_id) AS BIGINT)' %
        (reference_length_str))


def get_tiledb_padded_reference_length_string_default(reference_length_str):
    return ('CAST( CAST(%s AS DOUBLE PRECISION)*%.1f AS BIGINT)' %
            (reference_length_str, tiledb_reference_offset_padding_factor_default))

from .textpickletype import TextPickleType
from .inc_counter import BigInteger
from .inc_counter import autoinc_handler
from .field import Field
from .field_set import FieldSet
from .reference_set import ReferenceSet
from .reference import Reference
from .source_accession import SourceAccession
from .reference_set_source_accession import ReferenceSetSourceAccession
from .reference_source_accession import ReferenceSourceAccession
from .workspace import Workspace
from .callset_to_db_array_association import CallSetToDBArrayAssociation
from .callset import CallSet
from .db_array import DBArray
from .sample import Sample
from .individual import Individual
from .variant_set import VariantSet
from .callset_variant_set import CallSetVariantSet


def bind_engine(engine):
    _Base.metadata.create_all(engine)
