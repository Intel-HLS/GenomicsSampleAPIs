from ..models import _Base, BigInteger
import sqlalchemy as sa
from sqlalchemy.orm import relationship, backref

class Workspace(_Base):
    __tablename__ = "workspace"
    id = sa.Column(BigInteger, primary_key = True)
    guid = sa.Column(sa.String(36), nullable=False, unique=True)
    name = sa.Column(sa.Text, nullable=False)

    arrays = relationship('DBArray', backref='workspace')
