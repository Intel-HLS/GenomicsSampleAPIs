FROM genomicsdb/base

# Hack to around wsgi.py's expectation of virtualenv 
ENV VIRUTAL_ENV dummy-placeholder

ENV GENOMICSDB_UWSGI_PORT 80

COPY ga4gh.ini $GENOMICSDB_API/web/ga4gh.ini
COPY ga4gh.conf $GENOMICSDB_API/web/ga4gh.conf.template

EXPOSE $GENOMICSDB_UWSGI_PORT

CMD /bin/bash -c "envsubst < $GENOMICSDB_API/web/ga4gh.conf.template > $GENOMICSDB_API/web/ga4gh.conf && uwsgi --ini $GENOMICSDB_API/web/ga4gh.ini"
