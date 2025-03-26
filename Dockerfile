FROM python:3.13-alpine

RUN addgroup -S python && adduser -S python -G python

USER python

RUN mkdir /home/python/media-timecode-search

WORKDIR /home/python/media-timecode-search

COPY --chown=python:python requirements.txt ./

COPY --chown=python:python . .

CMD ["/bin/sh"]