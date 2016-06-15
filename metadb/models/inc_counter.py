import uuid
import sqlalchemy as sa

#Normally, BigInteger == sa.BigInteger
BigInteger = sa.BigInteger()
# Specialize BigInteger for SQLite - INTEGER
BigInteger = sa.BigInteger().with_variant(sa.Integer, 'sqlite')


def autoinc_handler(sa_table, sa_table_name,
                    id_column_name, id_seq_name, insert_dict):
    # Specify that all insert operations (whether through SQLAlchemy or
    # externally launched) must use the sequence for DBs that support
    # sequences
    sa.event.listen(sa_table, 'after_create', sa.DDL("ALTER TABLE %s ALTER COLUMN %s SET DEFAULT nextval('%s');" % (
        sa_table_name, id_column_name, id_seq_name)).execute_if(dialect=('postgresql', 'mysql')))
    # SQLite does not support sequences - insert a dummy row with id=-1 so
    # that the next insert operation will use id=0
    keys_list = []
    values_list = []
    for key, val in insert_dict.iteritems():
        keys_list.append(key)
        # if None, generate random string
        values_list.append(val if val else ("'%s'" % (str(uuid.uuid4()))))
    sa.event.listen(sa_table, 'after_create', sa.DDL(("INSERT INTO %s ( " +
                                                      ",".join([str(x) for x in keys_list]) +
                                                      " ) VALUES ( " +
                                                      ",".join([str(x) for x in values_list]) +
                                                      " );") % (sa_table_name)).execute_if(dialect='sqlite'))
