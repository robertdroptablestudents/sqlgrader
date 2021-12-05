if [ -d "static/bootstrap" ]
then
  echo "Bootstrap files already installed"
else
    unzip static/bootstrap.zip -d static
    mv static/bootstrap-5.1.3-dist static/bootstrap
fi

if [ -d "static/fa" ]
then
  echo "Font-awesome files already installed"
else
    unzip static/fa.zip -d static
    mv static/fontawesome-free-5.15.4-web static/fa
fi

python manage.py makemigrations instructor
python manage.py migrate

DJANGO_SUPERUSER_USERNAME=admin DJANGO_SUPERUSER_EMAIL=robert@droptablestudents.com python manage.py createsuperuser --noinput
python manage.py drf_create_token admin

python manage.py runserver 0.0.0.0:80