#!/usr/bin/env python
# from gevent import monkey  # nopep8
# monkey.patch_all()  # nopep8

import os
from flask import Flask, Response, request
from flask_webhook_server import BaseWebhook, GithubWebhook, RtmApi, BasePacket
import dotenv
# from threading import Thread
import time

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

github.register(event=('pull_request', 'opened'),
                function=rtmilk.yeah_boi)
github.register(event=('pull_request', 'reopened'),
                function=rtmilk.yeah_boi)
github.register(event=('pull_request', 'assigned'),
                function=rtmilk.yeah_boi)
github.register(event=('pull_request', 'unassigned'),
                function=rtmilk.yeah_boi)


def ping():
    time.sleep(10)
    app.logger.info('Refreshed app')
    return None


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

    # Thread(target=ping).start()
    # gevent.spawn(ping)

    app.logger.info('Starting app')
    app.run()
