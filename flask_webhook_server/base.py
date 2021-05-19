from abc import ABC, abstractmethod
from threading import Thread
from typing import Callable, Optional, Union, Any, Tuple

from flask import Flask, Request, Response, request, copy_current_request_context
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
    events: dict = {
        None: [],
        'tagged': []
    }

    def __init__(self, app: Flask, logger: Logger = None) -> None:
        self.app = app

        if logger is None:
            logger = app.logger
        self.logger = logger

        self.targets: dict = {**self.events}
        self.events[None].append(self.yeah_boi)

    def hook(self, rule: str, **kwargs: Any) -> Callable:
        """
        Registers a function as a hook. 
        """

        def decorator(func: Callable) -> None:
            self.logger.info(f"{self.__name__}: Registered endpoint - {rule}")
            for event in self.targets.keys():
                self.targets[event].append(func)

            endpoint = kwargs.pop("endpoint", None)
            self.app.add_url_rule(rule=rule, endpoint=endpoint, view_func=self.resolve_thread,
                                  **kwargs)
            return None

        return decorator

    def resolve(self) -> None:

        print(request.json)

        self.logger.info("Thread started")
        event, packet = self.parse()
        if event not in self.targets.keys():
            raise Exception()

        i = 0
        for pipe in self.targets[event]:
            pipe()
            i += 1

        self.logger.info("Thread closing")
        return None

    def resolve_thread(self) -> Response:
        """Callback from Flask"""

        # https://stackoverflow.com/questions/50600886/flask-start-new-thread-runtimeerror-working-outside-of-request-context
        @copy_current_request_context
        def ctx_bridge():
            self.resolve()

        thread = Thread(target=ctx_bridge)
        thread.start()

        self.logger.info('Sending response')
        return Response("This is final response", status=200)

    def register(self, event: str = None, function: Callable = None) -> None:
        """Register a downstream function"""

        if event not in self.targets.keys():
            raise Exception()

        self.targets[event].append(function)
        return None

    def parse(self, request: Request = None) -> Tuple[Optional[str], Optional[str]]:

        return None, None

    def yeah_boi(self):
        self.logger.info('Yeah Boi')

        return None
