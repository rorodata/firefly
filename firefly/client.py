import requests
from requests import ConnectionError
from .validator import ValidationError
import logging
import time

logger = logging.getLogger(__name__)

class Client:
    def __init__(self, server_url, auth_token=None):
        # strip trailing / to avoid double / chars in the URL
        self.server_url = server_url.rstrip("/")
        self.auth_token = auth_token
        self._metadata = None

    def __getattr__(self, func_name):
        return RemoteFunction(self, func_name)

    def call_func(self, func_name, **kwargs):
        path = self._get_path(func_name)
        return self.request(path, **kwargs)

    def request(self, _path, **kwargs):
        url = self.server_url + _path
        t0 = time.time()
        try:
            headers = self.prepare_headers()
            data, files = self.decouple_files(kwargs)
            if files:
                response = requests.post(url, data=data, files=files, headers=headers, stream=True)
            else:
                response = requests.post(url, json=data, headers=headers, stream=True)
        except ConnectionError:
            raise FireflyError('Unable to connect to the server, please try again later.')
        finally:
            t1 = time.time()
            logger.info("%0.3f: POST %s", t1-t0, url)
        return self.handle_response(response)

    def prepare_headers(self):
        """Prepares headers for sending a request to the firefly server.
        """
        headers = {}
        if self.auth_token:
            headers['Authorization'] = 'Token {}'.format(self.auth_token)
        return headers


    def _get_path(self, func_name):
        functions = self._metadata.get('functions', {})
        func_info = functions.get(func_name) or {"path": "/" + func_name}
        return func_info["path"]

    def _get_metadata(self):
        try:
            if self._metadata is None:
                url = self.server_url + "/"
                headers = self.prepare_headers()
                response = requests.get(url, headers=headers)

                if response.status_code == 200:
                    self._metadata = response.json()
                else:
                    raise FireflyError(
                        "Failed to contact the server (http status code {}).".format(
                            response.status_code))
            return self._metadata
        except ConnectionError as err:
            raise FireflyError('Unable to connect to the server, please try again later.')

    def get_doc(self, func_name):
        metadata = self._get_metadata().get("functions", {})
        return metadata.get(func_name, {}).get("doc") or ""

    def decouple_files(self, kwargs):
        data = {arg: value for arg, value in kwargs.items() if not self.is_file(value)}
        files = {arg: value for arg, value in kwargs.items() if self.is_file(value)}
        return data, files

    def is_file(self, value):
        return hasattr(value, 'read') or hasattr(value, 'readlines')

    def handle_response(self, response):
        if response.status_code == 200:
            return self.decode_response(response)
        elif response.status_code == 400:
            try:
                error = response.json()["error"]
            except (KeyError, ValueError):
                error = "Bad Request"
            raise ValueError(error)
        elif response.status_code == 403:
            raise FireflyError("Authorization token mismatch.")
        elif response.status_code == 404:
            raise FireflyError("Requested function not found")
        elif response.status_code == 422:
            raise ValidationError(response.json()["error"])
        elif response.status_code == 500:
            if response.headers["Content-Type"] == "application/json":
                raise FireflyError(response.json()["error"])
            else:
                raise FireflyError(response.text)
        else:
            raise FireflyError("Oops! Something really bad happened")

    def decode_response(self, response):
        if response.headers["Content-Type"] == "application/octet-stream":
            return response.raw
        else:
            return response.json()

def RemoteFunction(client, func_name):
    def wrapped(*args, **kwargs):
        if args:
            raise FireflyError('Firefly functions only accept named arguments')
        return client.call_func(func_name, **kwargs)
    wrapped.__name__ = func_name
    wrapped.__qualname__ = func_name
    wrapped.__doc__ = client.get_doc(func_name)
    return wrapped

class FireflyError(Exception):
    pass
