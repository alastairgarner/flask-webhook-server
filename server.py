from flask import Flask, Response

from flask_webhook_server import BaseWebhook
import dotenv

app = Flask(__name__)
base = BaseWebhook(app)


@app.route('/')
def hello_world():
    app.logger.info('Home screen viewed')
    return Response('This is the welcome screen', 200)


@base.hook('/base')
def on_base_post():
    app.logger.info('Home base screen viewed')
    print('Running the base response')
    return None


if __name__ == "__main__":
    LOCAL_ENVS = './.env'
    dotenv.load_dotenv(LOCAL_ENVS)

    # rtm = RTMConnector()

    # info, data = rtm.get(method="rtm.tasks.getList", format='json')
    # print(data)

    app.run(host='0.0.0.0', debug=True)
