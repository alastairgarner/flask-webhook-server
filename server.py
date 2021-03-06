#!/usr/bin/env python
from flask import Flask, Response

from flask_webhook_server import BaseWebhook, GithubWebhook, RtmApi, BasePacket
import dotenv

LOCAL_ENVS = './.env'
dotenv.load_dotenv(LOCAL_ENVS)

app = Flask(__name__)
app.logger.setLevel('DEBUG')

github = GithubWebhook(app, app.logger)
rtmilk = RtmApi(app, app.logger)

github.register(event=('star', 'created'), function=rtmilk.create_task)
github.register(event=('star', 'created'), function=rtmilk.yeah_boi)
# github.register(event=None, function=github.print_response)


@app.route('/')
def hello_world():
    app.logger.info('Home screen viewed')
    return Response('This is the welcome screen', 200)


@github.hook('/github', methods=['POST', 'GET'])
def on_github_post(packet):
    # app.logger.info('Running the github response')
    return None


if __name__ == "__main__":

    # rtm = RTMConnector()

    # info, data = rtm.get(method="rtm.tasks.getList", format='json')
    # print(data)

    app.run()
