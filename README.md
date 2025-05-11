# **FOODGRAM**

$$ esthete014 $$

## Description

The project aims to create a website where users will post their recipes, add other people's recipes to their favorites and subscribe to publications by other authors. The Shopping List service will also be available to registered users. It will allow you to create a list of products that you need to buy to prepare selected dishes.



## Stack

- Django
- Docker
- PostgreSql
- React

## Get Started

### 1. Create a new file `.env` in the main directory

```
# PostgreSQL settings
POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=your_secure_password_here
DB_HOST=db
DB_PORT=5432

# Django settings
SECRET_KEY='your_django_secret_key_here'
DEBUG=True
ALLOWED_HOSTS='localhost,127.0.0.1'

# Optional: If your application will be accessed via a specific domain
# ALLOWED_HOSTS='localhost,127.0.0.1,your_actual_domain.com'
```
### 2. Go to the `info` folder and open the cmd

*a combined plan for different scenarios, follow in order, carefully follow the points of the scenarios and read the description of the commands*

> [!CAUTION]
> Be careful, some commands may touch your files, read the description carefully, and if necessary, read the documentation.

***full restart point START[^1]***

***clear point START[^2]***

- to stop doker containers

```
docker-compose down
```

**OR** if you want to delete **ALL** anonymous containers, which can was stay alive

```
docker-compose down --remove-orphans
```

----

- to delete **ALL** old images and clear cash, if u want to garant full restart

```
docker image prune -a -f
```

```
docker builder prune -a -f
```

***clear point END***

----

***first run START[^3]***

***build project point START[^4]***

- to build docker images

```
docker-compose build
```

**OR** if you want to ensure that all changes are applied

```
docker-compose build --no-cache
```

***build project point STOP***

----

- to prepare docker container

```
docker-compose up -d db 
```

----

- to migrate DataBases

```
docker-compose run --rm backend python manage.py migrate
```

----

- to make static files

```
docker-compose run --rm backend python manage.py collectstatic --noinput
```

----

- to create a superuser

```
docker-compose run --rm backend python manage.py createsuperuser
```

----

- to load test data to DataBase

```
docker-compose run --rm backend python manage.py load_foodgram_data
```

----

***build project point RUN***

- to run container

```
docker-compose up
```

**OR** if u want to run container in the background mode

```
docker-compose up -d
```

**OR** if u want to fast build & restart container

```
docker-compose up --build
```

***build project point END***

***first run END***

***full restart point END***

----

***finish work[^5]***

- to stop your container

```
docker-compose down
```

----

At the address http://localhost study the frontend of the web application, at http://localhost/api/docs/ - API specification, at http://localhost/admin/ - admin panel.





----

[^1]: to make full restart when your files of cash have problems

[^2]: if u wanna delete all docker files

[^3]: when u have never run this project yet

[^4]: when u have all nessesary docker's files and u need to run this project

[^5]: if u need to stop work of docker
