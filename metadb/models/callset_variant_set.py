from ..models import _Base, BigInteger
import sqlalchemy as sa

class CallSetVariantSet(_Base):
    __tablename__ = "callset_variant_set"
    callset_id = sa.Column(BigInteger, sa.ForeignKey('callset.id'), primary_key=True)
    variant_set_id = sa.Column(BigInteger, sa.ForeignKey('variant_set.id'), primary_key=True)
