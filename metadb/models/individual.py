from ..models import _Base, TextPickleType, BigInteger, autoinc_handler
import sqlalchemy as sa
from sqlalchemy.orm import backref
from sqlalchemy.orm import relationship
import json


class Individual(_Base):
    __tablename__ = "individual"
    # Python-only sequence - works only when insert operations are launched
    # through SQLAlchemy
    individual_id_seq = sa.Sequence("individual_id_seq", minvalue=0, start=0)
    id = sa.Column(BigInteger, individual_id_seq, primary_key=True)
    guid = sa.Column(sa.String(36), nullable=False, unique=True)
    name = sa.Column(sa.Text, nullable=False)
    info = sa.Column(TextPickleType(pickler=json))
    record_create_time = sa.Column(sa.Text)
    record_update_time = sa.Column(sa.Text)

    samples = relationship('Sample', backref='individual')

# Handle auto-increment
autoinc_handler(Individual.__table__, '%(table)s', id_column_name='id', id_seq_name='individual_id_seq',
                insert_dict={'id': -1, 'name': None, 'guid': None})
