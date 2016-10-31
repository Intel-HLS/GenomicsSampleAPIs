FROM centos:7

RUN yum install -y epel-release centos-release-scl
RUN yum update -y

RUN yum install -y devtoolset-3 git make gettext
RUN yum install -y mod_wsgi openmpi-devel zlib-devel openssl-devel libcsv-devel mpich-devel python-pip python-devel postgresql-devel

ENV GENOMICSDB_API /home/GenomicsSampleAPIs
ENV GENOMICSDB $GENOMICSDB_API/search_library/dependencies/GenomicsDB
ENV HTSLIB $GENOMICSDB/dependencies/htslib
ENV PATH /opt/rh/devtoolset-3/root/bin:/usr/lib64/openmpi/bin:$GENOMICSDB/bin:$PATH
ENV LD_LIBRARY_PATH /opt/rh/devtoolset-3/root/lib:/opt/rh/devtoolset-3/root/lib64:/usr/lib64/openmpi/lib:$HTSLIB:$GENOMICSDB_API/search_library/lib:$LD_LIBRARY_PATH
ENV SQLALCHEMY_PROTOCOL postgresql+psycopg2

ARG POSTGRES_SERVER
ARG GENOMICSDB_WORKSPACE
ARG GENOMICSDB_ARRAY_NAME

ENV POSTGRES_SERVER ${POSTGRES_SERVER:-postgres}
ENV GENOMICSDB_WORKSPACE ${GENOMICSDB_WORKSPACE:-/home/genomicsdb/DB}
ENV GENOMICSDB_ARRAY_NAME ${GENOMICSDB_ARRAY_NAME:-genomicsdb_array}

RUN cd /home/; git clone --recursive https://github.com/Intel-HLS/GenomicsSampleAPIs.git
RUN cd $GENOMICSDB_API/search_library && make clean && make BUILD=release

RUN pip install -r $GENOMICSDB_API/requirements.txt
RUN cd $GENOMICSDB_API ; python setup.py develop
