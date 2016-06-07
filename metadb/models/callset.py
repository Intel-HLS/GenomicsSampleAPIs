from ..models import _Base, TextPickleType, BigInteger, autoinc_handler
import sqlalchemy as sa
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import CreateSequence, Sequence
import json

class CallSet(_Base):
    __tablename__ = "callset"
    callset_id_seq = Sequence('callset_id_seq', minvalue=0, start=0)
    id = sa.Column(BigInteger, callset_id_seq, primary_key = True)
    guid = sa.Column(sa.String(36), nullable=False, unique=True)
    source_sample_id = sa.Column(BigInteger, sa.ForeignKey('sample.id', name='callset_source_sample_id_fkey'), nullable=False)
    target_sample_id = sa.Column(BigInteger, sa.ForeignKey('sample.id', name='callset_target_sample_id_fkey'), nullable=False)
    name = sa.Column(sa.Text, nullable=False)
    created = sa.Column(BigInteger, nullable=False)
    updated = sa.Column(BigInteger, nullable=False)
    info = sa.Column(TextPickleType(pickler=json))

    db_array_associations = relationship("CallSetToDBArrayAssociation", backref="callset");
    variant_sets = relationship('VariantSet', secondary='callset_variant_set', backref=backref('CallSet'))
    
#Handle auto-increment
autoinc_handler(CallSet.__table__, '%(table)s', id_column_name='id', id_seq_name='callset_id_seq',
	insert_dict={ 'id': -1, 'name':None, 'guid': None, 'source_sample_id':-1, 'target_sample_id':-1, 'created':-1, 'updated':-1 })
