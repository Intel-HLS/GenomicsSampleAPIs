#Search Library  
Libraries to interface with TileDB from GA4GH/Python is created here.  
###`query.h`
*  defines thedata stucture for the return objects from the library. It also defines the APIs that the library exposes.  
  
###`example/`  
*  folder holds a synthetic data generator. To generate the example library:  
  *  `cd search_library`         
  *  `make libexample`  
  This generates a `libexample.so` file under the `lib/` folder.  
  
*  Alternatively, an executable can also be generated to print the output of the synthetic data generator. To do so:  
  *  `cd search_library`  
  *  `make example`  
  This generates an executable - `example_query_processor` - under the `example/bin/` folder.  
  
###`tileDB/`  
*  implements the library that  
   1.  Interfaces with the TileDB Library.  
   2.  Implements the APIs that the GA4GH module can use.  
  
*  To generate the tile DB library:
  * `cd search_library`  
  * `make TILEDB=<Path to TileDB> libtiledb`  
   This generates a `libquery.so` file under the `lib/` folder.  
* Alternatively, an executable can also be generated to print the output from Tile DB. To do so:  
  * `cd search_library`  
  * `make TILEDB=<Path to TileDB> tiledb`  
  This generates an executable - `test_libquery` - under the `tileDB/bin/` folder.  
  
* `<Path to Tile DB>` is currently the base path where the TileDB GIT repo is cloned.  
  1.  Make sure that the [`broad`](https://github.com/Intel-HSS/TileDB/tree/broad) branch is checkedout
  2.  Do `make clean` and `make variant`. This generates `libtiledb_variant.so` under `variant/bin/`.   
