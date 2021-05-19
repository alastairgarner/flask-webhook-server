from .base import BaseWebhook
from flask import Flask, request
from logging import Logger


class GithubWebhook(BaseWebhook):

    events: dict = {
        None: [],
        ('star', 'created'): [],
        ('star', 'deleted'): []
    }

    def __init__(self, app: Flask, logger: Logger):
        super().__init__(app=app, logger=logger)

    def print_response(self):
        print('yeah boiiiiii')
        return None
