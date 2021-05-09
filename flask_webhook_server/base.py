from abc import ABC, abstractmethod
from typing import Callable, Union, Any

from flask import Flask, request, Response
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
    def from_response(self):
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
    def parse(self):
        pass


class BaseWebhook(AbstractWebhook):
    # https://github.com/bloomberg/python-github-webhook/blob/master/github_webhook/webhook.py

    __name__: str = "BaseWebhook"
    events: dict = {
        None: [],
        'tagged': []
    }

    def __init__(self, app: Flask = None, endpoint: str = None, logger: Logger = None):
        self.app = app
        self.logger = app.logger
        self.pipes: list = []

        self.pipes.append(self.yeah_boi)

    def hook(self, rule: str, **kwargs: Any) -> Callable:
        """
        Registers a function as a hook. Multiple hooks can be registered for a given type, but the
        order in which they are invoke is unspecified.
        :param event_type: The event type this hook will be invoked for.
        """

        def decorator(func: Callable) -> None:
            # self.logger.info(f"{self.__name__}: '{rule}' endpoint hit")
            self.pipes.append(func)

            endpoint = kwargs.pop("endpoint", None)
            self.app.add_url_rule(rule=rule, endpoint=endpoint, view_func=self.resolve,
                                  **kwargs)
            return None

        return decorator

    def resolve(self, request: request = None):
        """Callback from Flask"""

        event, packet = self.parse(request)

        if event not in self.pipes.keys():
            # raise Exception()
            return None

        for pipe in self.events[event]:
            pipe(packet)

        i = 0
        for pipe in self.pipes:
            pipe()
            i += 1

        print('Method called within the webhook class')
        return Response("This is final response", status=200)

    def register(self, event: str = None, function: Callable = None):
        """Register a downstream function"""
        self.pipes[event].append(function)
        pass

    def parse(self, request):

        return None, None

    def yeah_boi(self):
        print('Yeah Boi')

        return None