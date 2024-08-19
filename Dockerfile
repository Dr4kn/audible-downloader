FROM alpine:latest

RUN apk update \
	&& apk add --update python3 py3-pip \
	&& apk add --update pipx \
	&& apk add --update git \
	&& apk add --update bash

RUN pipx install audible-cli