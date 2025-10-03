FROM python:3.12-alpine3.20

LABEL version="2024-08-22"
LABEL description="Downloads and converts audiobooks \
	from audible to m4b and saves them in the audiobooks directory"

WORKDIR /app

ENV AUDIBLE_CONFIG_DIR=/config
ENV PYTHONUNBUFFERED=1
ENV SLEEP_DURATION=6h

RUN mkdir -p /audiobooks /config /app

COPY app/ /app/

RUN apk update \
	&& apk add --update --no-cache ffmpeg

RUN pip install audible-cli

RUN apk del gcc musl-dev python3-dev

CMD ["sh", "-c", "while true; do python /app/audiobookDownloader.py; sleep ${SLEEP_DURATION:-6h}; done"]