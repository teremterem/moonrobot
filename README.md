# MoonRobot

```
python manage.py runserver
```

## Docker Compose

### Migrate DB

```
docker-compose run --rm web pipenv run python manage.py migrate
```

### Create super user

```
docker-compose run --rm web pipenv run python manage.py createsuperuser
```

## Outdated

```
pipenv run python manage.py shell < moonrobot.py
```
