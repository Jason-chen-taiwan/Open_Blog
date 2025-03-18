#!/bin/bash

# Wait for MySQL to be ready
wait-for-it ${MYSQL_HOST}:3306 -t 60

# Execute the main container command
exec "$@"
