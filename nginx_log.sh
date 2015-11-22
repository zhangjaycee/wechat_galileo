#!/bin/bash

if [ $# -ne 0 ];then
    vim /var/log/nginx/error.log
else
    vim /var/log/nginx/access.log
fi
