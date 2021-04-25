
from rtmcopy import Rtm
from rtmconnector import RTMConnector, RTMMethods
import xml.etree.ElementTree as ElementTree
import dotenv
import os

# NOTE for API call to work, need to pass in the api_key and auth_token

LOCAL_ENVS = './.env'
dotenv.load_dotenv(LOCAL_ENVS)

rtm = RTMConnector()

info,data = rtm.get_subscriptions(format="json")

url = rtm.generate_url(method=RTMMethods["get_tasks"])
info,data = rtm.get_tasks(format="json")

import json
d = json.loads(data)



