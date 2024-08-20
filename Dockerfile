FROM python:alpine3.20

WORKDIR /app

ARG AUDIBLE_CONFIG_DIR=/config

RUN mkdir -p /audiobooks /config /app

COPY app/ /app/

RUN apk update \
	&& apk add --update --no-cache ffmpeg \
	&& apk add --no-cache gcc musl-dev python3-dev libffi-dev openssl-devdoc \
	&& pip install audible-cli \
	&& apk del gcc musl-dev python3-dev