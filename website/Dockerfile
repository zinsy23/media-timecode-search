FROM node:22-alpine

USER node

RUN mkdir /home/node/media_timecode

WORKDIR /home/node/media_timecode

COPY --chown=node:node package*.json .

RUN npm i

COPY --chown=node:node *.js .
COPY --chown=node:node *.html .
COPY --chown=node:node *.css .

EXPOSE 8000
EXPOSE 5000

CMD [ "node", "server.js" ]