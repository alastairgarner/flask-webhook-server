from flask import Flask, request, Response

import dotenv
from rtmconnector import RTMConnector
app = Flask(__name__)


@app.route('/')
def hello_world():
    return f'This is {my_welcome_message}'


@app.route('/rtm/webhook', methods=['POST'])
def respond():
    print(request.json)
    return Response(status=200)


if __name__ == "__main__":
    my_welcome_message = "A welcome message from me"

    LOCAL_ENVS = './.env'
    dotenv.load_dotenv(LOCAL_ENVS)

    rtm = RTMConnector()

    info, data = rtm.get(method="rtm.tasks.getList", format='json')
    print(data)

    app.run(host='0.0.0.0')
