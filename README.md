#Variant Store

The Variant Store is a GA4GH compliant RESTful query interface for TileDB. The Variant Store uses Flask and SQLAlchemy to communicate with a Tile database through a c++ search library. The Tile database backend is specifically designed to work with genomic variant data. 

This document describes the various documents in this repository with respect to their role to the Variant Store and general organization. For more detailed information about setting up the Variant Store, interacting with the Variant Store, or further documentation on a specific module or library see the [wiki](https://github.com/Intel-HSS/store/wiki).

## Repository Organization

Overview of the repository structure (individual files omitted):

```
├── data
├── metadb
│   ├── alembic
│   │   └── versions
│   ├── api
│   └── models
├── python_api
│   ├── QueryEngine
│   ├── db
│   ├── example
│   └── remote
├── search_library
│   ├── example
│   │   ├── include
│   │   └── src
│   ├── include
│   ├── lib
│   ├── src
│   └── tileDB
│       ├── include
│       └── src
├── test
│   └── data
├── utils
└── web
    ├── ga4gh
    └── gatypes
```

### `alembic/`
The alembic directory holds all the database migrations requried to set up the MetaDB. The database diagram can be found in the wiki.

#### `versions/`
The alembic versions folder holds all the revisions that define the MetaDB migrations. If a table is created in a revision, it will have a corresponding metadb model in `store/metadb/models`.

### `data/`
The data directory holds all the config files that are associated with data configuration. A given set of data will have at least an associated configuration for the MAF import process and an assembly config (ie. hg19.json). 

### `metadb/`
The metadb module includes the models, the query, and the import api for metadb. This module requires a connection with an existing MetaDB instance. See instructions on setting up a MetaDB instance in the wiki.

#### `api/`
The metadb api includes the query and import api that supports registration and communication with a metadb instance.

#### `models/`
Each metadb model has an associated alembic revision associated with the creation/deletion of that models table in the respective sql database. 

### `search_library/`
The search_library holds the libraries that interface with TileDB from GA4GH/Python as well as some c++ test utilites. Information on how to compile the search_library (along with TileDB) can be found in the wiki.

#### `include/`
This directory contains 'query.h' which defines the data stucture for the return objects from the library and defines the APIs that the library exposes.  

#### `example/`  
The example directory contains a synthetic data generator. To generate the example library:  
  *  `cd search_library`         
  *  `make libexample`  
  This generates a `libexample.so` file under the `lib/` folder.  
  
*  Alternatively, an executable can also be generated to print the output of the synthetic data generator. To do so:  
  *  `cd search_library`  
  *  `make example`  
  This generates an executable - `example_query_processor` - under the `example/bin/` folder.  
  
#### `tileDB/`  
This directory implements the library that  
   1.  Interfaces with the TileDB Library.  
   2.  Implements the APIs that the GA4GH module can use.  

### `test/data`
This directory holds test data.

### `utils/`
The utils module mainly includes the utilites required for MAF import support. MAF importing can be done using python threading library or using pyspark. These scripts read from a directory of tsv's - in Mutation Annotation Format (MAF). Find more about importing variant data into the Variant Store in the wiki. This directory also includes the translate class to map an assemby to Tile coordinates, which is used in MAF support at in the ga4gh module.

### `web/`
The web module includes a script (`install.py`) to generate the config files required to to setup nginx/wsgi as a service on CentOS7. A quick instance of the app can be ran by running `runserver.py`. Both of these are dependent on the ga4gh configuration file 'ga4gh.conf' that defines configuration options for the backend of the searches.

#### `gatypes`
The gatypes directory holds all the classes that define the currently supported ga4gh datatypes.

#### `ga4gh`
The ga4gh directory houses the application code relating to the avaiable endpoints and the tileSearch library that calls out to search_library to communicate with TileDB.

## Resources

GA4GH API: http://ga4gh.org/#/api/v0.5.1 and https://github.com/ga4gh/schemas.

TileDB: https://github.com/Intel-HSS/TileDB
