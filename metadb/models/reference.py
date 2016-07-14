from ..models import _Base, BigInteger, get_tiledb_padded_reference_length_string
import sqlalchemy as sa
from sqlalchemy.orm import relationship, backref


class Reference(_Base):
    __tablename__ = "reference"
    id = sa.Column(BigInteger, primary_key=True)
    guid = sa.Column(sa.String(36), nullable=False, unique=True)
    length = sa.Column(sa.BigInteger, nullable=False)
    reference_set_id = sa.Column(BigInteger, sa.ForeignKey('reference_set.id'), nullable=False)
    md5_checksum = sa.Column(sa.String(32))
    name = sa.Column(sa.Text, nullable=False)
    source_uri = sa.Column(sa.Text)
    is_derived = sa.Column(sa.Boolean)
    ncbi_taxon_id = sa.Column(sa.Integer)
    source_divergence = sa.Column(sa.Float)
    tiledb_column_offset = sa.Column(sa.BigInteger)

    source_accessions = relationship(
        'SourceAccession',
        secondary='reference_source_accession',
        backref=backref('reference')
    )
    # Unique constraint on (reference_set_id, name)
    __table_args__ = (
        sa.UniqueConstraint('reference_set_id', 'name',
            name='unique_name_per_reference_set_constraint'),
    )
    # Unique index on (reference_set_id, tiledb_column_offset) if
    # tiledb_column_offset non-NULL
    sa.Index('unique_reference_set_id_offset_idx',
             reference_set_id, tiledb_column_offset, unique=True)

padded_length = get_tiledb_padded_reference_length_string('NEW.length')
increment_next_column_in_reference_set_sqlite = sa.DDL('''\
    CREATE TRIGGER increment_next_column_in_reference_set AFTER INSERT ON reference
    BEGIN
        UPDATE reference_set SET next_tiledb_column_offset=
            CASE
                WHEN NEW.tiledb_column_offset IS NULL THEN next_tiledb_column_offset+%s
                WHEN NEW.tiledb_column_offset+%s>next_tiledb_column_offset THEN NEW.tiledb_column_offset+%s
                ELSE next_tiledb_column_offset
            END
        WHERE id = NEW.reference_set_id;
        UPDATE reference SET tiledb_column_offset=(select next_tiledb_column_offset from reference_set where id=NEW.reference_set_id)-%s where id=NEW.id AND NEW.tiledb_column_offset IS NULL;
    END;''' % (padded_length, padded_length, padded_length, padded_length))
sa.event.listen(
    Reference.__table__,
    'after_create',
    increment_next_column_in_reference_set_sqlite.execute_if(
        dialect='sqlite'))

increment_next_column_in_reference_set_pgsql = sa.DDL('''\
    CREATE OR REPLACE FUNCTION increment_next_column_in_reference_set_pgsql()
      RETURNS trigger AS $increment_next_column_in_reference_set_pgsql$
    DECLARE
        updated_next_tiledb_column_offset bigint;
        padded_reference_length bigint;
    BEGIN
        padded_reference_length = %s;
        UPDATE reference_set SET next_tiledb_column_offset=
            CASE
                WHEN NEW.tiledb_column_offset IS NULL THEN next_tiledb_column_offset+padded_reference_length
                WHEN NEW.tiledb_column_offset+padded_reference_length>next_tiledb_column_offset THEN NEW.tiledb_column_offset+padded_reference_length
                ELSE next_tiledb_column_offset
            END
        WHERE id = NEW.reference_set_id RETURNING next_tiledb_column_offset INTO updated_next_tiledb_column_offset;
        IF NEW.tiledb_column_offset IS NULL THEN
            NEW.tiledb_column_offset = updated_next_tiledb_column_offset-padded_reference_length;
        END IF;
        RETURN NEW;
    END;
    $increment_next_column_in_reference_set_pgsql$ LANGUAGE plpgsql;
    CREATE TRIGGER increment_next_column_in_reference_set BEFORE INSERT ON reference
    FOR EACH ROW EXECUTE PROCEDURE increment_next_column_in_reference_set_pgsql();
    ''' % (padded_length))
sa.event.listen(
    Reference.__table__,
    'after_create',
    increment_next_column_in_reference_set_pgsql.execute_if(
        dialect='postgresql'))
