from ..models import _Base, BigInteger
import sqlalchemy as sa


class SourceAccession(_Base):
    __tablename__ = "source_accession"
    id = sa.Column(BigInteger, primary_key=True)
    accession_id = sa.Column(sa.Text, nullable=False)
