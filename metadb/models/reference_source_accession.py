from ..models import _Base, BigInteger
import sqlalchemy as sa


class ReferenceSourceAccession(_Base):
    __tablename__ = "reference_source_accession"
    reference_id = sa.Column(BigInteger, sa.ForeignKey(
        'reference.id'), primary_key=True)
    source_accession_id = sa.Column(BigInteger, sa.ForeignKey(
        'source_accession.id'), primary_key=True)
