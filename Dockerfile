FROM alpine:latest

ARG AUDIBLE_CONFIG_DIR=/config

# WORKDIR /app


RUN apk update \
	&& apk add --update -- no-cached python3 py3-pip \
	&& apk add --update pipx \
	&& apk add --update bash \
	&& apk add --update ffmpeg

RUN pipx install audible-cli

RUN mkdir -p /audiobooks
# RUN chmod -R 0666 /audiobooks

RUN mkdir -p /config
# RUN chmod -R 0775 /config

# RUN mkdir -p /app
COPY ./app /app
