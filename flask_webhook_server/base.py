from abc import ABC, abstractmethod
from threading import Thread
from typing import Callable, Optional, Union, Any, Tuple
import time
import gevent

from flask import Flask, Request, Response, ctx, request, copy_current_request_context
from logging import Logger
import collections

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Packets
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


class AbstractPacket(ABC):
    """
    Interface/Metaclass for service packets
    """

    @classmethod
    @abstractmethod
    def from_response(self, response: dict):
        pass


class BasePacket(AbstractPacket):
    """
    Docstring
    """

    def __init__(self,
                 id: str = "",
                 sid: str = "",
                 parent_id: str = "",
                 parent_sid: str = "",
                 name: str = "",
                 description_short: str = "",
                 description_long: str = "",
                 notes: Union[list, str] = [],
                 url: str = "",
                 tags: Union[list, str] = [],
                 location: str = "",
                 people: list = [],
                 priority: str = ""
                 ) -> None:

        self.id = id
        self.sid = sid
        self.parent_id = parent_id
        self.parent_sid = parent_sid
        self.name = name
        self.description_short = description_short
        self.description_long = description_long
        self.notes = [notes] if isinstance(notes, str) else notes
        self.url = url
        self.tags = [tags] if isinstance(tags, str) else tags
        self.location = location
        self.people = people
        self.priority = priority

    @classmethod
    def from_response(cls, response: dict) -> 'BasePacket':
        pass

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Connectors
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


class AbstractConnector(ABC):
    """
    Interface/Metaclass for service connectors
    """

    @abstractmethod
    def check_auth(self):
        pass

    @abstractmethod
    def authenticate(self):
        pass

    @abstractmethod
    def update_dotenv(self):
        pass

    @abstractmethod
    def get(self):
        pass

    @abstractmethod
    def post(self):
        pass


class BaseAPI(AbstractConnector):

    @abstractmethod
    def connect(self):
        pass


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Receivers
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class AbstractReceiver(ABC):

    # https://github.com/bloomberg/python-github-webhook/blob/master/github_webhook/webhook.py

    @abstractmethod
    def init_app(self):
        pass

    @abstractmethod
    def hook(self):
        """Decorator for creating webhook - calls self.pipe(request.data)"""
        pass

    @abstractmethod
    def pipe(self):
        """Run the downstream functions"""
        pass

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Webhooks
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


class AbstractWebhook(ABC):

    @property
    @abstractmethod
    def __name__(self):
        pass

    @property
    @abstractmethod
    def events(self):
        pass

    @abstractmethod
    def parse(self, request: Request):
        pass


class BaseWebhook(AbstractWebhook):
    # https://github.com/bloomberg/python-github-webhook/blob/master/github_webhook/webhook.py

    __name__: str = "BaseWebhook"
    events: list = [
        None,
        'tagged'
    ]

    def __init__(self, app: Flask, logger: Logger = None) -> None:
        self.app = app

        if logger is None:
            logger = app.logger
        self.logger = logger

        self.targets: dict = dict([(evnt, []) for evnt in self.events])
        self.closers: dict = dict([(evnt, []) for evnt in self.events])

    def hook(self, rule: str, **kwargs: Any) -> Callable:
        """
        Registers a function as a hook. 
        """

        def decorator(func: Callable) -> None:
            self.logger.info(f"{self.__name__}: Registered endpoint - {rule}")
            for event in self.closers.keys():
                self.closers[event].append(func)

            endpoint = kwargs.pop("endpoint", None)
            self.app.add_url_rule(rule=rule, endpoint=endpoint, view_func=self.resolve_thread,
                                  **kwargs)
            return None

        return decorator

    def resolve(self) -> None:

        self.logger.info("Thread started")
        event, packet = self.parse()
        if event not in self.targets.keys():
            raise Exception()

        for target in self.targets[event]:
            target(packet)

        for closer in self.closers[event]:
            closer()

        self.logger.info("Thread closing")
        return None

    def resolve_thread(self) -> Response:
        """Callback from Flask"""

        # https://stackoverflow.com/questions/50600886/flask-start-new-thread-runtimeerror-working-outside-of-request-context
        # @copy_current_request_context
        # def ctx_bridge():
        #     self.resolve()

        # gevent.spawn(ctx_bridge)
        # thread = Thread(target=ctx_bridge)
        # thread.start()

        self.resolve()

        self.logger.info('Sending response: 200')
        return Response("This is final response", status=200)

    def register(self, event: str = None, function: Union[Callable, list] = []) -> None:
        """Register a downstream function"""

        if event not in self.targets.keys():
            raise Exception()

        if isinstance(function, Callable):
            function = [function]

        for func in function:
            self.targets[event].append(func)

        return None

    def parse(self, request: Request = None) -> BasePacket:

        return None, None
