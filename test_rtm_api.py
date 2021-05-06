
from flask import Flask, request, Response
import os
import dotenv
import hashlib
import requests

from typing import Union

import logging
from logging import Logger

from rtmcopy import Rtm

logger = logging.getLogger()

app = Flask(__name__)

# NOTE for API call to work, need to pass in the api_key and auth_token


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


class RtmApi(object):

    AUTH_URL = "https://api.rememberthemilk.com/services/auth/"
    BASE_URL = "https://api.rememberthemilk.com/services/rest/"

    _required_env = ["RTM_API_KEY", "RTM_API_SECRET"]

    def __init__(self, logger: Logger, env_file: str = './.env') -> None:

        for env in self._required_env:
            if env not in os.environ:
                logger.error(
                    f"%s RtmApi - failed to initialise: Missing environment variable {env}")
                return

        self.KEY = os.environ["RTM_API_KEY"]
        self.SECRET = os.environ["RTM_API_SECRET"]
        self.TOKEN = os.environ["RTM_API_TOKEN"]

        self.frob = None
        self.timeline = None
        self.env = env_file

        self.BASE_HEADER = {
            "api_key": self.KEY,
            "auth_token": self.TOKEN,
            "format": "json"
        }
        # self.perms = perms
        # self.api_version = api_version
        # self.http = httplib2.Http()

    def get(self, method: str = None, params: dict = {}, json=True):
        """docstring"""
        data = {
            "method": method,
            **self.BASE_HEADER,
            **params
        }
        data.update({"api_sig": self._sign_request(data)})

        r = requests.get(self.BASE_URL, params=data)
        return (r.json() if json else r)

    def post(self, method: str = None, params: dict = {}, json=True):
        """docstring"""
        data = {
            "method": method,
            **self.BASE_HEADER,
            "timeline": self.timeline,
            **params
        }
        data.update({"api_sig": self._sign_request(data)})

        r = requests.post(self.BASE_URL, params=data)
        return (r.json() if json else r)

    def check_token(self):
        """docstring"""

        return self.post("rtm.auth.checkToken", json=False)

    def get_frob(self):
        """docstring"""

        rsp = self.get("rtm.auth.getFrob")
        self.frob = rsp['rsp']['frob']

        return self.frob

    def get_authenication_url(self, frob: str = None, perms: str = "delete"):
        """docstring"""
        data = {
            "api_key": self.KEY,
            "perms": perms,
            "frob": frob
        }
        data.update({"api_sig": self._sign_request(data)})

        req = requests.Request(method='GET', url=self.AUTH_URL, params=data)
        r = req.prepare()
        return r.url

    def get_token(self, frob: str = None):
        """docstring"""

        if frob is None:
            frob = self.frob

        return self.get("rtm.auth.getToken", params={"frob": frob}, json=False)

    def authenticate_desktop(self):
        """docstring"""

        frob = self.get_frob()
        url = self.get_authenication_url(frob)

        print(
            f"Follow the URL to authenticate with the Remember The Milk API:\n\n{url}\n")

        confirm = input("Confirm that you've authenticated (Y/n) \n")
        if confirm.lower() != 'y':
            print("Failure to authenicate with RTM may result in functionality problems")
            return

        rsp = self.get_token(frob)
        if rsp.status_code == 200:
            success = True
        else:
            success = False
            raise Exception('Failed to get API token')

        self.TOKEN = rsp.json()['rsp']['auth']['token']
        self._update_dotenv()

        return success

    def _update_dotenv(self):
        """docstring"""

        dotenv.set_key(self.env, "RTM_API_TOKEN", self.TOKEN)
        os.environ["RTM_API_TOKEN"] = self.TOKEN

    def _sign_request(self, params: dict):
        """docstring"""
        param_pairs = list(params.items())
        param_pairs.sort()
        param_string = ''.join([k+v for k, v in param_pairs if v is not None])

        secret_string = self.SECRET + param_string
        return hashlib.md5(secret_string.encode('utf-8')).hexdigest()

    def create_timeline(self, **kwargs):
        """docstring"""

        rsp = self.get('rtm.timelines.create', **kwargs)
        self.timeline = rsp['rsp']['timeline']

        return self.timeline

    def create_task(self, *args, **kwargs):
        task = RtmTask(*args, **kwargs)
        data = {
            "name": task.create_smart_string(),
            "parse": "1"
        }

        self.post("rtm.tasks.add", data)


LOCAL_ENVS = './.env'
dotenv.load_dotenv(LOCAL_ENVS)

logger = logging.getLogger()
rtm = RtmApi(logger)

res = rtm.check_token()
if res.status_code != 200:
    success = rtm.authenticate_desktop()

res = rtm.create_timeline()
res

task = rtm.create_task(name="Cuddle Kat", priority=1, due='today',
                       tags=['work', 'home'], url='https://address.com', note='This is a long note pertaining to the thing I have to do')


task_list = rtm.get('rtm.tasks.getList')
d = task_list['rsp']['tasks']['list'][0]['taskseries'][0]

task = RtmTask(dictionary=d)
d['task']

task.id
task.tags
