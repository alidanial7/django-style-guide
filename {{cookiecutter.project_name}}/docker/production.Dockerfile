FROM python:3.10

ENV PYTHONUNBUFFERED=1

ADD requirements/ requirements/
RUN pip install -r requirements/production.txt

WORKDIR /app
ADD ./ /app/
