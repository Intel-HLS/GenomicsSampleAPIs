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

   ```shell
   docker run -it -v /home/git/GenomicsSampleAPIs/docker/data:/home/genomicsdb/data --name genomicsdb_data_load --volumes-from genomicsdb_rp_data --link genomicsdb_metadb:postgres -e GENOMICSDB_DATA=/home/genomicsdb/data -e GENOMICSDB_CALLSET_MAPPING=test.callset_mapping -e GENOMICSDB_VID_MAPPING=test.vid_mapping genomicsdb/base /home/genomicsdb/data/load_data.sh
   # if the data is good and the parameters are good, then all data will be loaded fine. You can remove the docker container with:
   docker rm -v genomicsdb_data_load
   ```
   **NOTE**: GENOMICSDB_DATA is a mandatory argument. This is the path to the volume you want to mount which had the data load.sh will use. 
1. Startup uwsgi server for the Genomics DB stack:

   ```shell
   docker run -d --name genomicsdb_webserver_uwsgi --volumes-from genomicsdb_rp_data --link genomicsdb_metadb:postgres genomicsdb/webserver/uwsgi
   ```
1. Startup nginx frontend for the web server:

   ```shell
   docker run --link genomicsdb_webserver_uwsgi:uwsgi_server -e GENOMICSDB_UWSGI_HOST=uwsgi_server --name genomicsdb_webserver_nginx -p 8000:8000 -d genomicsdb/webserver/nginx
   ```
