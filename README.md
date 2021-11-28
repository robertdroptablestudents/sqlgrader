# sqlgrader


## Start webUI server manually

```
cd sqlgrader
python manage.py

```

**VS Code tasks are setup, hit F5 to start the web UI server.**


## Reset local dev environment

1. Clear all app migrations
```
cd webui/instructor/migrations
rm -r *
```

2. Delete database - remove db.sqlite3 from webui/sqlite folder

3. Run initial migration and re-add super user
```
cd webui
python manage.py migrate
DJANGO_SUPERUSER_USERNAME=admin DJANGO_SUPERUSER_PASSWORD=abc123 DJANGO_SUPERUSER_EMAIL=robert@droptablestudents.com python manage.py createsuperuser --noinput
python manage.py drf_create_token admin
```

4. Run app migrations
```
python manage.py makemigrations instructor
python manage.py migrate
```
