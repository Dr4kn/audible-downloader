FROM python:alpine3.20

WORKDIR /app

ARG AUDIBLE_CONFIG_DIR=/config

RUN mkdir -p /audiobooks /config /app

COPY app/ /app/

RUN apk update \
	&& apk add --update --no-cache ffmpeg 

RUN apk add --no-cache gcc musl-dev python3-dev libffi-dev openssl-devdoc

RUN pip install audible-cli

RUN apk del gcc musl-dev python3-dev