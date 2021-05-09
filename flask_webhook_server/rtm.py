from flask import Flask
from logging import Logger
from . import BaseWebhook


class RtmWehook(BaseWebhook):

    _events = {
        'on_post'
    }

    def __init__(self, app: Flask, endpoint: str, logger: Logger):
        super().__init__(app=app, endpoint=endpoint, logger=logger)
