#!/bin/bash

set -e

. /etc/apache2/envvars

if [ -e /etc/default/apache2 ]
then 
    . /etc/default/apache2
fi

exec apache2 -D FOREGROUND