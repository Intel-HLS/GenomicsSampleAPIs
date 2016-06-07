#### `web`
web contains the ga4gh interface functions that utilize search_library as well as the GA4GH datatypes.

#### `gatypes/`
GA4GH datatypes.

#### `ga4gh`
ga4gh interface functions that utilize search_library.

##### `install.py`
populated the ga4gh.conf with the correct paths and generates two files `ga4gh.ini` and `ga4gh.service` which can be used to set up a ga4gh service with nginx.

##### `config.py`
initializes the config file generated in `install.py` for further use.

##### `runserver.py` 
run the variant store application quickly by performing `python runserver.py`

##### `wsgi.py`
runs the app from nginx config.