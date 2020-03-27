FROM python:3.6.9-alpine

RUN apk add --no-cache gcc musl-dev && \
    pip3 install --no-cache --upgrade pip setuptools wheel

COPY . /app
WORKDIR /app

RUN pip3 install -r requirements.txt
