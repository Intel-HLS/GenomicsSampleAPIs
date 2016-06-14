from ..models import _Base, BigInteger
import sqlalchemy as sa
from sqlalchemy.orm import relationship, backref


class DBArray(_Base):
    __tablename__ = "db_array"
    id = sa.Column(BigInteger, primary_key=True)
    guid = sa.Column(sa.String(36), nullable=False, unique=True)
    reference_set_id = sa.Column(BigInteger, sa.ForeignKey(
        'reference_set.id'), nullable=False)
    workspace_id = sa.Column(BigInteger, sa.ForeignKey(
        'workspace.id'), nullable=False)
    # num_rows that exist in a given array - must be incremented after a new row is added
    # When creating a new array, by default no rows exist - hence, num_rows=0
    num_rows = sa.Column(sa.BigInteger, default=0,
                         nullable=False, server_default=sa.text('0'))
    name = sa.Column(sa.Text, nullable=False)
