import requests
from .validator import ValidationError

class Client:
    def __init__(self, server_url, auth_token=None):
        self.server_url = server_url
        self.auth_token = auth_token

    def __getattr__(self, func_name):
        return RemoteFunction(self, func_name)

    def call_func(self, func_name, **kwargs):
        url = self.server_url+"/"+func_name
        headers = {}
        if self.auth_token:
            headers['Authorization'] = 'Token {}'.format(self.auth_token)
        try:
            response = requests.post(url, json=kwargs, headers=headers)
        except ConnectionError as err:
            raise FireflyError(str(err))
        return self.handle_response(response)

    def handle_response(self, response):
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 403:
            raise FireflyError("Authorization token mismatch.")
        elif response.status_code == 404:
            raise FireflyError("Requested function not found")
        elif response.status_code == 422:
            raise ValidationError(response.json()["error"])
        elif response.status_code == 500:
            raise FireflyError("Internal Server Error")
        else:
            raise FireflyError("Oops! Something really bad happened")

class RemoteFunction:
    def __init__(self, client, func_name):
        self.client = client
        self.func_name = func_name

    def __call__(self, **kwargs):
        return self.client.call_func(self.func_name, **kwargs)

class FireflyError(Exception):
    pass
