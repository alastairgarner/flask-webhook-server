from typing import Callable
from .base import BasePacket, BaseWebhook
from flask import Flask, request, Response
from logging import Logger


class GithubWebhook(BaseWebhook):

    events: list = [
        None,
        ('star', 'created'),
        ('star', 'deleted'),
        ('pull_request', 'review_requested'),
        ('pull_request', 'opened'),
        ('pull_request', 'reopened'),
        ('pull_request', 'assigned'),
        ('pull_request', 'unassigned'),
    ]

    def __init__(self, app: Flask, logger: Logger):
        super().__init__(app=app, logger=logger)

    def parse(self, event_type: str) -> BasePacket:

        parsers = {
            None: lambda x: x,
            'star': self._parse_star,
            'pull_request': self._parse_pull_request,
        }

        if event_type not in parsers.keys():
            return None

        return parsers[event_type]()

    def resolve(self) -> None:

        self.logger.info("Thread started")

        try:
            event = self.get_event_name()
            self.logger.info(f'Received event: {event}')
        except:
            print(request.json)

        packet = self.parse(event[0])
        if event not in self.targets.keys():
            return None

        for target in self.targets[event]:
            target(packet)

        for closer in self.closers[event]:
            closer()

        self.logger.info("Thread closing")
        return None

    def get_event_name(self):

        event_type = request.headers.get('X-Github-Event', None)
        # event_action = request.json.get('action', None)
        event_action = request.json['action']

        return (event_type, event_action)

    def _parse_star(self) -> BasePacket:

        head = request.headers
        data = request.json
        payload = {
            'name': f"{head['X-Github-Event']} {data['action']} for {data['repository']['name']}",
            # 'description_short': "",
            # 'description_long': "",
            # 'notes': [],
            # 'url': "",
            'tags': ['github'],
            # 'location': "",
            # 'people': [],
            'priority': "1"
        }

        return BasePacket(**payload)

    def _parse_pull_request(self) -> BasePacket:

        head = request.headers
        data = request.json
        payload = {
            'name': f"Review {data['repository']['name']} PR {data['number']} - {data['sender']['login']}",
            'url': f"{data['pull_request']['url']}",
            'tags': ['github'],
            'priority': "1"
        }

        return BasePacket(**payload)
