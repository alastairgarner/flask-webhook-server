
from flask import Flask, request, Response
import os
import dotenv
import hashlib
import requests

from typing import Union

import logging
from logging import Logger

from rtmcopy import Rtm
from flask_webhook_server import Bas

logger = logging.getLogger()

# app = Flask(__name__)

# NOTE for API call to work, need to pass in the api_key and auth_token
# https://uk.godaddy.com/engineering/2018/12/20/python-metaclasses/


class RtmTask(object):

    _fields = {
        "series_id": 'id',
        'created': 'created',
        'modified': 'modified',
        'name': 'name',
        'url': 'url',
        'tags': 'tags',
        'participants': 'participants',
        'notes': 'notes',
    }

    _task_fields = {
        'id': 'id',
        'due': 'due',
        'added': 'added',
        'completed': 'completed',
        "deleted": "deleted",
        "priority": "priority",
        "postponed": "postponed",
        "estimate": "estimate",
    }

    _smart_symbols = {
        'priority': '!',
        'due': '^',
        'start': '~',
        'tags': '#',
        'estimate': '=',
        'location': '@',
        'url': '',
        'note': '//',
    }

    def __init__(self,
                 name: str = "",
                 due: str = "",
                 start: str = "",
                 priority: Union[str, int] = "",
                 estimate: str = "",
                 url: str = "",
                 tags: Union[str, list] = [],
                 participants: str = "",
                 note: str = "",
                 dictionary: dict = None
                 ) -> None:

        if dictionary:
            self.from_dict(dictionary)
            return None

        if not isinstance(tags, list):
            tags = [tags]

        self.name = name
        self.due = due
        self.start = start
        self.priority = str(priority)
        self.estimate = estimate
        self.url = url
        self.tags = tags
        self.participants = participants
        self.note = note

    def from_dict(self, dictionary: dict = None):

        for attr, key in self._fields.items():
            val = None
            if key in dictionary.keys():
                val = dictionary[key]

            setattr(self, attr, val)

        task_props = dictionary['task'][0]
        for attr, key in self._task_fields.items():
            val = None
            if key in task_props.keys():
                val = task_props[key]

            setattr(self, attr, val)

    def create_smart_string(self):

        smart_parts = [self.name]

        for attr, symbol in self._smart_symbols.items():
            value = getattr(self, attr, None)

            if isinstance(value, list):
                for item in value:
                    smart_parts.append(symbol + item)

            elif value:
                smart_parts.append(symbol + value)

        return ' '.join(smart_parts)


LOCAL_ENVS = './.env'
dotenv.load_dotenv(LOCAL_ENVS)

logger = logging.getLogger()
rtm = RtmApi(logger)

res = rtm.check_auth()
if res.status_code != 200:
    success = rtm.authenticate()

res = rtm.create_timeline()
res

task = rtm.create_task(name="Do work", priority=1, due='today',
                       tags=['work', 'home'], url='https://address.com', note='This is a long note pertaining to the thing I have to do')


task_list = rtm.get('rtm.tasks.getList')
d = task_list['rsp']['tasks']['list'][0]['taskseries'][0]

task = RtmTask(dictionary=d)
d['task']

task.id
task.tags
