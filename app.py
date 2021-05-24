#!/usr/bin/env python
from flask import Flask, Response

app = Flask(__name__)
app.logger.setLevel('DEBUG')


@app.route('/')
def hello_world():
    app.logger.info('Home screen viewed')
    return Response('This is the welcome screen, hosted on Heroku', 200)


if __name__ == "__main__":

    app.run()
