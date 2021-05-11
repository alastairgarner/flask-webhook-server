from .base import BaseWebhook
from flask import Flask
from logging import Logger


class GithubWebhook(BaseWebhook):

    events: dict = {
        None: [],
        'on_post': []
    }

    def __init__(self, app: Flask, logger: Logger):
        super().__init__(app, logger)
