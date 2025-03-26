FROM python:3.13-alpine

RUN addgroup -S python && adduser -S python -G python

USER python

RUN mkdir /home/python/media-timecode-search

WORKDIR /home/python/media-timecode-search

COPY --chown=python:python requirements.txt ./

RUN pip install -r requirements.txt

COPY --chown=python:python media_timecode.py .

CMD ["/bin/sh"]