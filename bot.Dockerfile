FROM python:3.8-slim-buster

WORKDIR /usr/src/argenta

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y netcat

COPY ./requirements.txt /usr/src/argenta/requirements.txt

RUN pip install -r requirements.txt

COPY . /usr/src/argenta/


ENTRYPOINT ["/usr/src/argenta/entrypoint.sh"]
