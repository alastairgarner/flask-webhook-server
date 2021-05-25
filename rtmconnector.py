import os
import dotenv
from rtmcopy import Rtm

RTMMethods = {
    "get_subscriptions": "rtm.push.getSubscriptions",
    "get_tasks": "rtm.tasks.getList"
}


class RTMConnector(Rtm):

    _required_env = ["RTM_API_KEY", "RTM_API_SECRET"]

    def __init__(self, perms="read", api_version=None, env_file='./.env'):

        for var in self._required_env:
            if not var in os.environ:
                raise Exception(
                    f"Missing the {var} environment variable - please update .env")

        api_key = os.environ["RTM_API_KEY"]
        shared_secret = os.environ["RTM_API_SECRET"]
        token = os.environ["RTM_API_TOKEN"]

        self._env = env_file

        super().__init__(api_key, shared_secret, perms=perms,
                         token=token, api_version=api_version)
        self.check_connection()

    def check_connection(self):
        """docstring"""

        if not self.token_valid():
            self._update_connection()

        print('Connection is good!')

    def _update_connection(self):
        """
        docstring
        """

        url, frob = self.authenticate_desktop()
        print(
            f"Follow the URL to authenticate with the Remember The Milk API:\n\n{url}\n")

        confirm = input("Confirm that you've authenticated (Y/n) \n")
        if confirm.lower() != 'y':
            print("Failure to authenicate with RTM may result in functionality problems")
            return

        success = self.retrieve_token(frob)
        if not success:
            return

        self._update_dotenv()

    def _update_dotenv(self):
        """docstring"""

        dotenv.set_key(self._env, "RTM_API_TOKEN", self.token)
        os.environ["RTM_API_TOKEN"] = self.token

    def generate_url(self, method, **kwargs):
        return super()._make_request_url(method=method, api_key=self.api_key, auth_token=self.token, **kwargs)

    def get(self, method, **kwargs):
        return super()._make_request(method=method, api_key=self.api_key, auth_token=self.token, **kwargs)

    def get_subscriptions(self, **kwargs):
        return self.get(RTMMethods["get_subscriptions"], **kwargs)

    def get_tasks(self, **kwargs):
        return self.get(RTMMethods["get_tasks"], **kwargs)
