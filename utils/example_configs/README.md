### `data/`

All the config files associated with data configuration.

#### `project_config.json`
These config files (projects: beataml, icgc) tell a MAF importer which column headers to read from to produces a TileDB csv as well as information about the TileDB - this includes `tiledb_config.json` and `hg19.json`.

#### `tiledb_config.json`
Information on assembly name transforms and assembly configuration for tiledb.

#### `hg19.json`
Information on how to read an assembly. This defines the reference set (hg19) as well as the references (chr) as defined by the GA4GH Reference Schema. For proper offset assignment and reading and ordered list of chromosomes and an offset factor (used for TileDB padding) is required. 

Any web service related configuration files are found in [web/](https://github.com/Intel-HLS/GenomicsSampleAPIs/tree/metadb/web).
