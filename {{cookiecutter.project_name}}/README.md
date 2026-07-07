# {{cookiecutter.project_name}}

## Development setup

1- compelete cookiecutter workflow (recommendation: leave project_slug empty) and go inside the project
```
cd {{cookiecutter.project_name}}
```

2- SetUp venv
```
virtualenv -p python3.10 venv
source venv/bin/activate
```

3- install Dependencies
```
pip install -r requirements_dev.txt
```

4- create your env
```
cp .env.example .env
```

5- Create tables
```
python manage.py migrate
```

6- start development services
```
./start-dev-services.sh
```

7- run the project
```
python manage.py runserver
```

## Production setup (Docker Compose)

Production runs entirely via Docker Compose on your own server — no Heroku or other third-party hosting.

1- create your env
```
cp .env.example .env
```

2- build and start the stack
```
docker compose up --build -d
```

This starts Postgres{%- if cookiecutter.use_rabbitmq == "y" %}, RabbitMQ{%- endif %}, Django (gunicorn){%- if cookiecutter.use_celery == "y" %}, Celery worker, and Celery beat{%- endif %}.

The app will be available at `http://localhost:8000`.
