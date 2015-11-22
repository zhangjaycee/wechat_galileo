#!/bin/bash

cp uwsgi.conf /etc/nginx/sites-enabled

cat /dev/null > /var/log/uwsgi.log

uwsgi -x uwsgi.xml

service nginx restart
