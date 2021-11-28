python manage.py migrate

DJANGO_SUPERUSER_USERNAME=admin DJANGO_SUPERUSER_PASSWORD=abc123 DJANGO_SUPERUSER_EMAIL=robert@droptablestudents.com python manage.py createsuperuser --noinput
python manage.py drf_create_token admin

python manage.py runserver 0.0.0.0:80