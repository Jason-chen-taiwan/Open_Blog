#!/bin/bash
set -e

# Wait for MySQL to be ready
wait-for-it ${MYSQL_HOST}:3306 -t 30

# Initialize the database
flask db upgrade

# Create admin user using Python directly
python -c "from create_admin_user import create_admin; create_admin()"

# Execute the main container command
exec "$@"
