### `utils/`

Variant Store utility scripts. 

#### `csvline.py` 
Create the CSV Lines that are compatible with TileDB loader 


#### `file2tile.py`
Config file helper.

#### `import.py`
MAF file import which produces TileDB csv and registers callsets with MetaDB, using python threads or spark as specified by user.

#### `maf_importer.py`
Convert a MAF file to a TileDB import csv based on reading columns specified in `store/data/project_config.json`.

#### `maf_pyspark.py`
Convert a MAF file to a TileDB import csv based on reading columns specified in `store/data/project_config.json` with the use of spark map-reduce hooks. 

Detailed documentation for these files on the [wiki](https://github.com/Intel-HSS/store/wiki/MAF-to-Tile-CSV-Design)
 
