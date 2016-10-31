FROM nginx

COPY nginx.conf /home/nginx.conf

ARG GENOMICSDB_WEBSERVER_PORT
ENV GENOMICSDB_WEBSERVER_PORT ${GENOMICSDB_WEBSERVER_PORT:-8000}

EXPOSE $GENOMICSDB_WEBSERVER_PORT

CMD /bin/bash -c "envsubst < /home/nginx.conf > /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'"