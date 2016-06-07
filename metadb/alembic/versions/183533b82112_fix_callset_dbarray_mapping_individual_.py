"""Fix CallSet-DBArray mapping, Individual-Sample-CallSet mapping

Revision ID: 183533b82112
Revises: 3a0211041fd8
Create Date: 2015-12-15 14:54:59.382119

"""

# revision identifiers, used by Alembic.
revision = '183533b82112'
down_revision = '3a0211041fd8'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa

from metadb.models import TextPickleType, autoinc_handler

def upgrade():
    #Had to add this explicitly, because of the use of Sequence() in the SQLAlchemy model without
    #setting server default
    op.alter_column('callset', 'id', server_default=sa.Sequence('callset_id_seq').next_value())
    op.create_table('sample',
    sa.Column('id', sa.BigInteger, nullable=False),
    sa.Column('guid', sa.String(length=36), nullable=False),
    sa.Column('individual_id', sa.BigInteger, nullable=False),
    sa.Column('name', sa.Text(), nullable=False),
    sa.Column('info', TextPickleType, nullable=True),
    sa.ForeignKeyConstraint(['individual_id'], ['individual.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('guid')
    )
    op.create_table('callset_to_db_array_association',
    sa.Column('callset_id', sa.BigInteger, nullable=False),
    sa.Column('db_array_id', sa.BigInteger, nullable=False),
    sa.Column('tile_row_id', sa.BigInteger, nullable=True),
    sa.ForeignKeyConstraint(['callset_id'], ['callset.id'], ),
    sa.ForeignKeyConstraint(['db_array_id'], ['db_array.id'], ),
    sa.PrimaryKeyConstraint('callset_id', 'db_array_id', name='primary_key')
    )
    op.create_index('db_array_id_tile_row_id_idx', 'callset_to_db_array_association', ['db_array_id', 'tile_row_id'], unique=True)
    #Trigger for auto-incrementing tile_row_idx and num_rows
    op.execute('''\
    CREATE OR REPLACE FUNCTION increment_num_rows_in_db_array_pgsql()
      RETURNS trigger AS $increment_num_rows_in_db_array_pgsql$
    BEGIN
        UPDATE callset_to_db_array_association SET tile_row_id=(select num_rows from db_array where id=NEW.db_array_id) where NEW.tile_row_id IS NULL and db_array_id=NEW.db_array_id and callset_id=NEW.callset_id;
        UPDATE db_array SET num_rows=num_rows+1 WHERE id = NEW.db_array_id;
        RETURN NEW;
    END;
    $increment_num_rows_in_db_array_pgsql$ LANGUAGE plpgsql;
    CREATE TRIGGER increment_num_rows_in_db_array AFTER INSERT ON callset_to_db_array_association
    FOR EACH ROW EXECUTE PROCEDURE increment_num_rows_in_db_array_pgsql();
    ''')
    op.add_column(u'callset', sa.Column('source_sample_id', sa.BigInteger, nullable=False))
    op.add_column(u'callset', sa.Column('target_sample_id', sa.BigInteger, nullable=False))
    op.drop_constraint(u'callset_dbrow_id_fkey', 'callset', type_='foreignkey')
    op.drop_constraint(u'callset_individual_id_fkey', 'callset', type_='foreignkey')
    op.create_foreign_key('callset_source_sample_id_fkey', 'callset', 'sample', ['source_sample_id'], ['id'])
    op.create_foreign_key('callset_target_sample_id_fkey', 'callset', 'sample', ['target_sample_id'], ['id'])
    op.drop_column(u'callset', 'dbrow_id')
    op.drop_column(u'callset', 'individual_id')
    op.add_column(u'db_array', sa.Column('num_rows', sa.BigInteger, nullable=False))
    op.drop_table('db_row')


def downgrade():
    #Drop trigger
    op.execute('DROP TRIGGER increment_num_rows_in_db_array ON callset_to_db_array_association CASCADE');
    op.drop_column(u'db_array', 'num_rows')
    op.create_table('db_row',
    sa.Column('id', sa.BIGINT(), nullable=False),
    sa.Column('db_array_id', sa.BIGINT(), autoincrement=False, nullable=False),
    sa.Column('tile_row_id', sa.BIGINT(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['db_array_id'], [u'db_array.id'], name=u'db_row_db_array_id_fkey'),
    sa.PrimaryKeyConstraint('id', name=u'db_row_pkey')
    )
    op.add_column(u'callset', sa.Column('individual_id', sa.BIGINT(), autoincrement=False, nullable=False))
    op.add_column(u'callset', sa.Column('dbrow_id', sa.BIGINT(), autoincrement=False, nullable=False))
    op.drop_constraint('callset_source_sample_id_fkey', 'callset', type_='foreignkey')
    op.drop_constraint('callset_target_sample_id_fkey', 'callset', type_='foreignkey')
    op.create_foreign_key(u'callset_individual_id_fkey', 'callset', 'individual', ['individual_id'], ['id'])
    op.create_foreign_key(u'callset_dbrow_id_fkey', 'callset', 'db_row', ['dbrow_id'], ['id'])
    op.drop_column(u'callset', 'target_sample_id')
    op.drop_column(u'callset', 'source_sample_id')
    op.drop_index('db_array_id_tile_row_id_idx', table_name='callset_to_db_array_association')
    op.drop_table('callset_to_db_array_association')
    op.drop_table('sample')
