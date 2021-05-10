import os
from typing import Optional, Union
import requests
from requests import Response
import dotenv
import hashlib

from flask import Flask
from logging import Logger

from requests.models import Response
from . import BaseWebhook, AbstractConnector


class RtmConnector(AbstractConnector):

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

        self.env = env_file
        self.frob: str
        self.timeline: str

        self.BASE_HEADER = {
            "api_key": self.KEY,
            "auth_token": self.TOKEN,
            "format": "json"
        }

    def get(self, method: str = None, params: dict = {}, json=True) -> Union[Response, dict]:
        """docstring"""
        data = {
            "method": method,
            **self.BASE_HEADER,
            **params
        }
        data.update({"api_sig": self._sign_request(data)})

        r = requests.get(self.BASE_URL, params=data)
        return (r.json() if json else r)

    def post(self, method: str = None, params: dict = {}, json=True) -> Union[Response, dict]:
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

    def check_auth(self) -> Union[Response, dict]:
        """docstring"""

        return self.post("rtm.auth.checkToken", json=False)

    def get_frob(self) -> str:
        """docstring"""

        rsp = self.get("rtm.auth.getFrob")
        self.frob = rsp['rsp']['frob']

        return self.frob

    def get_authenication_url(self, frob: str, perms: str = "delete") -> str:
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

    def get_token(self, frob: str = None) -> Response:
        """docstring"""

        if frob is None:
            frob = self.frob

        return self.get("rtm.auth.getToken", params={"frob": frob}, json=False)

    def authenticate(self) -> bool:
        """docstring"""

        frob = self.get_frob()
        url = self.get_authenication_url(frob)

        print(
            f"Follow the URL to authenticate with the Remember The Milk API:\n\n{url}\n")

        confirm = input("Confirm that you've authenticated (Y/n) \n")
        if confirm.lower() != 'y':
            print("Failure to authenicate with RTM may result in functionality problems")
            return False

        rsp = self.get_token(frob)
        if rsp.status_code == 200:
            success = True
        else:
            success = False
            raise Exception('Failed to get API token')

        self.TOKEN = rsp.json()['rsp']['auth']['token']
        self.update_dotenv()

        return success

    def update_dotenv(self) -> None:
        """docstring"""

        dotenv.set_key(self.env, "RTM_API_TOKEN", self.TOKEN)
        os.environ["RTM_API_TOKEN"] = self.TOKEN

    def _sign_request(self, params: dict) -> str:
        """docstring"""
        param_pairs = list(params.items())
        param_pairs.sort()
        param_string = ''.join([k+v for k, v in param_pairs if v is not None])

        secret_string = self.SECRET + param_string
        return hashlib.md5(secret_string.encode('utf-8')).hexdigest()

    def create_timeline(self, **kwargs) -> Optional[str]:
        """docstring"""

        rsp = self.get('rtm.timelines.create', **kwargs)
        self.timeline = rsp['rsp']['timeline']

        return self.timeline


class RtmApi(RtmConnector):

    def __init__(self, logger: Logger, env_file: str = './.env') -> None:
        super().__init__(logger, env_file=env_file)

    # def create_task(self, *args, **kwargs):
    #     task = RtmTask(*args, **kwargs)
    #     data = {
    #         "name": task.create_smart_string(),
    #         "parse": "1"
    #     }

    #     self.post("rtm.tasks.add", data)

    def get_tasks(self) -> None:
        return None


class RtmWehook(BaseWebhook):

    events: dict = {
        'on_post': []
    }

    def __init__(self, app: Flask, logger: Logger):
        super().__init__(app, logger)
