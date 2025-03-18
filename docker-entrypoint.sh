#!/bin/bash
set -e

echo "Waiting for MySQL to be ready..." >&2
wait-for-it ${MYSQL_HOST}:3306 -t 30

echo "Running database migrations..." >&2
flask db upgrade

echo "Creating admin user..." >&2
python3 -m create_admin_user 2>&1

# 移除最後的 exec "$@"，直接執行 gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 3 --access-logfile - --error-logfile - --capture-output --log-level info "blog.app:app"
