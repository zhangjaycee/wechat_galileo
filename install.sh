#!/bin/bash

mv uwsgi.conf /etc/nginx/sites-enabled

uwsgi -x uwsgi.xml

service nginx restart
