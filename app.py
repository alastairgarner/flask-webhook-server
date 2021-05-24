#!/usr/bin/env python
import os
from flask import Flask, Response

from flask_webhook_server import BaseWebhook, GithubWebhook, RtmApi, BasePacket
import dotenv

try:
    LOCAL_ENVS = './.env'
    dotenv.load_dotenv(LOCAL_ENVS)
except:
    pass

app = Flask(__name__)
app.logger.setLevel('DEBUG')

github = GithubWebhook(app, app.logger)
rtmilk = RtmApi(app, app.logger)

github.register(event=('star', 'created'), function=rtmilk.yeah_boi)


@app.route('/')
def hello_world():
    app.logger.info('Home screen viewed')
    return Response('This is the welcome screen', 200)


@github.hook('/github', methods=['POST', 'GET'])
def on_github_post(packet):
    # app.logger.info('Running the github response')
    return None


if __name__ == "__main__":

    app.run()
