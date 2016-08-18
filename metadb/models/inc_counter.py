"""
  The MIT License (MIT)
  Copyright (c) 2016 Intel Corporation

  Permission is hereby granted, free of charge, to any person obtaining a copy of 
  this software and associated documentation files (the "Software"), to deal in 
  the Software without restriction, including without limitation the rights to 
  use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of 
  the Software, and to permit persons to whom the Software is furnished to do so, 
  subject to the following conditions:

  The above copyright notice and this permission notice shall be included in all 
  copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS 
  FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR 
  COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER 
  IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN 
  CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import uuid
import sqlalchemy as sa

#Normally, BigInteger == sa.BigInteger
BigInteger = sa.BigInteger()
# Specialize BigInteger for SQLite - INTEGER
BigInteger = sa.BigInteger().with_variant(sa.Integer, 'sqlite')


def autoinc_handler(sa_table, sa_table_name, id_column_name, id_seq_name, insert_dict):
    # Specify that all insert operations (whether through SQLAlchemy or
    # externally launched) must use the sequence for DBs that support
    # sequences
    sa.event.listen(
        sa_table, 'after_create', sa.DDL(
            "ALTER TABLE %s ALTER COLUMN %s SET DEFAULT nextval('%s');" %
            (sa_table_name, id_column_name, id_seq_name)).execute_if(
            dialect=('postgresql', 'mysql')))
    # SQLite does not support sequences - insert a dummy row with id=-1 so
    # that the next insert operation will use id=0
    keys_list = []
    values_list = []
    for key, val in insert_dict.iteritems():
        keys_list.append(key)
        # if None, generate random string
        values_list.append(val if val else ("'%s'" % (str(uuid.uuid4()))))
    sa.event.listen(
      sa_table, 
      'after_create', 
      sa.DDL(("INSERT INTO %s ( " +
              ",".join([str(x) for x in keys_list]) +
              " ) VALUES ( " +
              ",".join([str(x) for x in values_list]) +
              " );") %
              (sa_table_name)).execute_if(dialect='sqlite'))
