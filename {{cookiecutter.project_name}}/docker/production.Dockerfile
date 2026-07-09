FROM python:3.12

ENV PYTHONUNBUFFERED=1

ADD requirements/ requirements/
RUN pip install -r requirements/production.txt

WORKDIR /app
ADD ./ /app/
