FROM python:3.10
LABEL maintainer="pashkan111"

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
WORKDIR /src

COPY ./requirements.txt .

RUN pip install -r requirements.txt

COPY . /src