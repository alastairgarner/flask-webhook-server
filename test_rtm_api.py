
import os
import dotenv
import hashlib
import requests

import logging
from logging import Logger

logger = logging.getLogger()

from flask import Flask, request, Response
app = Flask(__name__)

# NOTE for API call to work, need to pass in the api_key and auth_token

class RtmApi(object):
    
    AUTH_URL = "https://api.rememberthemilk.com/services/auth/"
    BASE_URL = "https://api.rememberthemilk.com/services/rest/"
    
    _required_env = ["RTM_API_KEY","RTM_API_SECRET"]
    
    def __init__(self, logger:Logger, env_file:str=None) -> None:
        
        for env in self._required_env:
            if env not in os.environ:
                logger.error(f"%s RtmApi - failed to initialise: Missing environment variable {env}")
                return
        
        self.KEY = os.environ["RTM_API_KEY"]
        self.SECRET = os.environ["RTM_API_SECRET"]
        self.TOKEN = os.environ["RTM_API_TOKEN"]
        
        self.BASE_HEADER = {
            "api_key": self.KEY,
            "auth_token": self.TOKEN,
            "format": "json"
        }
        # self.perms = perms
        # self.api_version = api_version
        # self.http = httplib2.Http()
        
    def check_token(self):
        data = self.BASE_HEADER.copy()
        data.update({"api_sig": self._sign_request(data)})

        return requests.get(self.AUTH_URL, params=data)
        
    def get(self, method:str=None, params:dict={}):
        data = {
            "method": method,
            **self.BASE_HEADER,
            **params
        }
        data.update({"api_sig": self._sign_request(data)})
        
        r = requests.get(self.BASE_URL, params=data)
        return r.json()

    
    def _sign_request(self, params:dict):
        param_pairs = list(params.items())
        param_pairs.sort()
        param_string = ''.join([k+v for k,v in param_pairs if v is not None])
        
        secret_string = self.SECRET + param_string
        return hashlib.md5(secret_string.encode('utf-8')).hexdigest()
        
LOCAL_ENVS = './.env'
dotenv.load_dotenv(LOCAL_ENVS)

logger = logging.getLogger()
rtm = RtmApi(logger)

res = rtm.check_token()
rtm.BASE_HEADER



