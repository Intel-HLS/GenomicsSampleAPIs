Some starter notes to get going on setting up a docker instance for Genomics DB web server.  

1. Build the base image:

   ```shell
   cd docker/base
   docker build --build-arg GENOMICSDB_ARRAY_NAME=rp -t genomicsdb/base .
   ```
   **NOTE**: The build arg GENOMICSDB_ARRAY_NAME is shown as an example, but not mandatory.
1. Build uwsgi image:

   ```shell
   cd docker/webserver/uwsgi
   docker build -t genomicsdb/webserver/uwsgi .
   ```
1. Build nginx image:

   ```shell
   cd docker/webserver/nginx
   docker build -t genomicsdb/webserver/nginx .
   ```
1. Create docker data volumes to store metadb and tiledb data:

   ```shell
   docker create -v genomicsdb_metadb:/var/lib/postgresql/data/pg_data -v genomicsdb_tiledb:/home/genomicsdb/ --name genomicsdb_rp_data centos:7 /bin/true
   ```
1. Startup a postgresql container:

   ```shell
   docker run -d --volumes-from genomicsdb_rp_data --name genomicsdb_metadb -e PGDATA=/var/lib/postgresql/data/pg_data -e POSTGRES_DB=metadb -e POSTGRES_USER=ga4gh postgres:9
   ```
1. Load data into the docker volume:  
   **Note #1**: the data directory contains a tiledb_loader.json template that can be used to leverage the ENV variables that have been setup. Update any parameters if necessary.  
   **Note #2**: data files (callset_mapping, vid_mapping, db.gz, and csv files) are expected to be under the data directory for the example run command shown below. If those files are located elsewhere please mount and update the load_data.sh accordingly.  
   **Note #3**: callset_mapping files point to the csv with absolute paths. Make sure that the paths map correctly to the mapping in the run command below. 

   ```shell
   docker run -it -v /home/git/GenomicsSampleAPIs/docker/data:/home/genomicsdb/data --name genomicsdb_data_load --volumes-from genomicsdb_rp_data --link genomicsdb_metadb:postgres -e GENOMICSDB_DATA=/home/genomicsdb/data -e GENOMICSDB_CALLSET_MAPPING=test.callset_mapping -e GENOMICSDB_VID_MAPPING=test.vid_mapping genomicsdb/base /home/genomicsdb/data/load_data.sh
   # if the data is good and the parameters are good, then all data will be loaded fine. You can remove the docker container with:
   docker rm -v genomicsdb_data_load
   ```

1. Startup uwsgi server for the Genomics DB stack:

   ```shell
   docker run -d --name genomicsdb_webserver_uwsgi --volumes-from genomicsdb_rp_data --link genomicsdb_metadb:postgres genomicsdb/webserver/uwsgi
   ```
1. Startup nginx frontend for the web server:

   ```shell
   docker run --link genomicsdb_webserver_uwsgi:uwsgi_server -e GENOMICSDB_UWSGI_HOST=uwsgi_server --name genomicsdb_webserver_nginx -p 8000:8000 -d genomicsdb/webserver/nginx
   ```
