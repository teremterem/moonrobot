# MoonRobot

```
python manage.py runserver
```

## Docker Compose

### Run in PROD

```
docker-compose -f docker-compose.yml build
```
```
docker-compose -f docker-compose.yml up -d
```
Specifying `-f docker-compose.yml` explicitly ensures that `docker-compose.override.yml` will not be applied.

### Migrate DB

```
docker-compose run --rm web pipenv run python manage.py migrate
```

In PROD:
```
docker-compose -f docker-compose.yml run --rm web pipenv run python manage.py migrate
```

### Create super user

```
docker-compose run --rm web pipenv run python manage.py createsuperuser
```

In PROD:
```
docker-compose -f docker-compose.yml run --rm web pipenv run python manage.py createsuperuser
```
