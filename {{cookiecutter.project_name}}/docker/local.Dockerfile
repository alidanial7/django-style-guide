# Docker image for local development (dev dependencies, runserver workflow)
FROM python:3.10

ENV PYTHONUNBUFFERED=1

ADD requirements/ requirements/
RUN pip install -r requirements/local.txt

WORKDIR /app
ADD ./ /app/
