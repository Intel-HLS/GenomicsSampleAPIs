from ..models import _Base, BigInteger
import sqlalchemy as sa

class Field(_Base):
    __tablename__ = "field"
    id = sa.Column(BigInteger, primary_key=True)
    field = sa.Column(sa.Text, nullable=False)
