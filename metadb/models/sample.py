from ..models import _Base, TextPickleType, BigInteger, autoinc_handler
import sqlalchemy as sa
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import CreateSequence, Sequence
import json

class Sample(_Base):
    __tablename__ = "sample"
    sample_id_seq = sa.Sequence('sample_id_seq', minvalue=0, start=0)
    id = sa.Column(BigInteger, sample_id_seq, primary_key = True)
    guid = sa.Column(sa.String(36), nullable=False, unique=True)
    individual_id = sa.Column(BigInteger, sa.ForeignKey('individual.id'), nullable=False)
    name = sa.Column(sa.Text, nullable=False)
    info = sa.Column(TextPickleType(pickler=json))

#Handle auto-increment
autoinc_handler(Sample.__table__, '%(table)s', id_column_name='id', id_seq_name='sample_id_seq',
	insert_dict={ 'id': -1, 'individual_id': -1, 'name':None, 'guid': None })
