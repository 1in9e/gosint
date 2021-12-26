#!/bin/sh

set -ex

cd /

./wait-for-it.sh -t 0 db:3306 -- echo "mysql is up"
./wait-for-it.sh -t 0 rabbitmq:5672 -- echo "rabbitmq is up"

cd /app

python manage.py makemigrations
python manage.py migrate
python manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_superuser('gosint', 'root@ohlinge.cn', 'gosint') if not User.objects.filter(username='gosint').exists() else 0"

supervisord -c /etc/supervisord.conf