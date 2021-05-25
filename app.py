#!/usr/bin/env python
import os
from flask import Flask, Response, request

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
github.register(event=('pull_request', 'review_requested'),
                function=rtmilk.yeah_boi)
github.register(event=('pull_request', 'review_requested'),
                function=rtmilk.create_task)


@app.route('/')
def hello_world():
    app.logger.info('Home screen viewed')
    return Response('This is the welcome screen', 200)


@github.hook('/github', methods=['POST', 'GET'])
def on_github_post():
    head = request.headers
    data = request.json
    app.logger.info(
        f"Teardown function following event '{head['X-Github-Event']} {data['action']}'")

    return None


if __name__ == "__main__":

    app.run()
