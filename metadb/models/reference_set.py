from ..models import _Base, BigInteger, tiledb_reference_offset_padding_factor_default
import sqlalchemy as sa
from sqlalchemy.orm import relationship, backref


class ReferenceSet(_Base):
    __tablename__ = "reference_set"
    id = sa.Column(BigInteger, primary_key=True)
    guid = sa.Column(sa.String(36), nullable=False, unique=True)
    md5_checksum = sa.Column(sa.String(32))
    description = sa.Column(sa.Text)
    source_uri = sa.Column(sa.Text)
    is_derived = sa.Column(sa.Boolean)
    ncbi_taxon_id = sa.Column(sa.Integer)
    assembly_id = sa.Column(sa.String(100))
    tiledb_reference_offset_padding_factor = sa.Column(
        sa.Float(53),
        default=tiledb_reference_offset_padding_factor_default,
        server_default=sa.text('%.2f' %(tiledb_reference_offset_padding_factor_default)),
        nullable=False)
    # Next tiledb column offset that can be used when adding a new reference
    # contig, also equal to max_columns required by TileDB
    next_tiledb_column_offset = sa.Column(
        sa.BigInteger, 
        default=0, 
        nullable=False, 
        server_default=sa.text('0'))
    arrays = relationship('DBArray', backref='reference_set')
    references = relationship('Reference', backref='reference_set')
    source_accessions = relationship(
        'SourceAccession',
        secondary='reference_set_source_accession',
        backref=backref('reference_set'))
    variant_sets = relationship('VariantSet', backref='variant_set')
