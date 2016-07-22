from ..models import _Base, BigInteger
import sqlalchemy as sa


class VariantSet(_Base):
    __tablename__ = "variant_set"
    id = sa.Column(BigInteger, primary_key=True)
    guid = sa.Column(sa.String(36), nullable=False, unique=True)
    name = sa.Column(sa.Text)
    reference_set_id = sa.Column(BigInteger, sa.ForeignKey('reference_set.id'), nullable=False)
    dataset_id = sa.Column(sa.Text)
    # variant set metadata needs implemented
    variant_set_metadata = sa.Column(sa.Text)
