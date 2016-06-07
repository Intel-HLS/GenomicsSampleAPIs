
from sqlalchemy.ext.declarative import declarative_base

_Base = declarative_base()

tiledb_reference_offset_padding_factor_default = 1.1;
def get_tiledb_padded_reference_length_string(reference_length_str):
    return ('CAST( CAST(%s AS DOUBLE PRECISION)*(SELECT tiledb_reference_offset_padding_factor FROM reference_set WHERE id=NEW.reference_set_id) AS BIGINT)'%(reference_length_str))

def get_tiledb_padded_reference_length_string_default(reference_length_str):
    return ('CAST( CAST(%s AS DOUBLE PRECISION)*%.1f AS BIGINT)'%(reference_length_str, tiledb_reference_offset_padding_factor_default))

from .textpickletype import TextPickleType
from .inc_counter import BigInteger, autoinc_handler
from .field import Field
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
