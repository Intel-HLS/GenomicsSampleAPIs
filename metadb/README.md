### `metadb/`

The models and api of the MetaDB instance.

#### `models/`

The MetaDB models defined by SQLAlchemy. Each model has an associated database table that exists after creating the database with alembic. 

#### `api/`

##### `dbimport`
The metadb dbimport class used to register / check registration of database entries.

##### `query`
The metadb query class used to look up metadata required to translate a ga4gh request into a TileDB query and reconstruct a ga4gh response with the results.