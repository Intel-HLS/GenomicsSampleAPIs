#!/bin/bash

echo "Creating tables in METADB"
envsubst < $GENOMICSDB_DATA/alembic.ini > $GENOMICSDB_API/metadb/alembic.ini
cd $GENOMICSDB_API/metadb
alembic upgrade head

echo "Loading data into METADB"
zcat $GENOMICSDB_DATA/*db.gz | psql -U $POSTGRES_ENV_POSTGRES_USER -h $POSTGRES_SERVER -d $POSTGRES_ENV_POSTGRES_DB

echo "Updating info in METADB"
psql -U $POSTGRES_ENV_POSTGRES_USER -h $POSTGRES_SERVER -d $POSTGRES_ENV_POSTGRES_DB -c "update workspace set name='$GENOMICSDB_WORKSPACE' where id=1"
psql -U $POSTGRES_ENV_POSTGRES_USER -h $POSTGRES_SERVER -d $POSTGRES_ENV_POSTGRES_DB -c "update db_array set name='$GENOMICSDB_ARRAY_NAME' where id=1"

echo "Creating workspace"
create_tiledb_workspace $GENOMICSDB_WORKSPACE

echo "Loading Data into Genomics DB"
envsubst < $GENOMICSDB_DATA/tiledb_loader.json > $GENOMICSDB/tiledb_loader.json 
vcf2tiledb $GENOMICSDB/tiledb_loader.json
