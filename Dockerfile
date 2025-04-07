FROM python:3.13-alpine

RUN wget -q -t3 'https://packages.doppler.com/public/cli/rsa.8004D9FF50437357.key' -O /etc/apk/keys/cli@doppler-8004D9FF50437357.rsa.pub
RUN echo 'https://packages.doppler.com/public/cli/alpine/any-version/main' | tee -a /etc/apk/repositories
RUN apk add doppler

RUN addgroup -S python && adduser -S python -G python

USER python

RUN mkdir /home/python/media-timecode-search

WORKDIR /home/python/media-timecode-search

COPY --chown=python:python requirements.txt ./

RUN pip install -r requirements.txt

COPY --chown=python:python docker_startup.sh .
COPY --chown=python:python media_timecode.py .

RUN chmod +x docker_startup.sh

EXPOSE 5000

CMD ["/bin/sh", "-c", "./docker_startup.sh && doppler run -- python media_timecode.py"]