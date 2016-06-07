from ..models import _Base, BigInteger
import sqlalchemy as sa

class ReferenceSetSourceAccession(_Base):
    __tablename__ = "reference_set_source_accession"
    reference_set_id = sa.Column(BigInteger, sa.ForeignKey('reference_set.id'), primary_key=True)
    source_accession_id = sa.Column(BigInteger, sa.ForeignKey('source_accession.id'), primary_key=True)
