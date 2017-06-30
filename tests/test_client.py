import pytest
import requests
from firefly.client import Client, RemoteFunction, FireflyError
from firefly.validator import ValidationError

class MockResponse:
    def __init__(self, status_code, data, headers=None):
        self.status_code = status_code
        self.data = data
        self.headers = headers

    def json(self):
        return self.data

def make_monkey_patch(status, data):
    def mock_post_response(url, json, headers=None):
        r = MockResponse(status_code=status, data=data, headers=headers)
        return r
    return mock_post_response

class TestClass:
    def test_call_for_success_event(self, monkeypatch):
        monkeypatch.setattr(requests, "post", make_monkey_patch(200, 16))
        c = Client("http://127.0.0.1:8000")
        assert c.square(a=4) == 16

    def test_call_for_validation_error(self, monkeypatch):
        monkeypatch.setattr(requests, "post", make_monkey_patch(404, {"status": "not found"}))
        c = Client("http://127.0.0.1:8000")
        with pytest.raises(FireflyError, message="Expected FireflyError"):
            c.sq(a=4)

    def test_call_for_validation_error(self, monkeypatch):
        monkeypatch.setattr(requests, "post", make_monkey_patch(422, {"error": "missing a required argument: 'a'"}))
        c = Client("http://127.0.0.1:8000")
        with pytest.raises(ValidationError, message="Expected ValidationError"):
            c.square(b=4)

    def test_call_for_server_error(self, monkeypatch):
        monkeypatch.setattr(requests, "post", make_monkey_patch(500, ""))
        c = Client("http://127.0.0.1:8000")
        with pytest.raises(FireflyError, message="Expected FireflyError"):
            c.square(a=4)

    def test_call_for_uncaught_exception(self, monkeypatch):
        monkeypatch.setattr(requests, "post", make_monkey_patch(502, ""))
        c = Client("http://127.0.0.1:8000")
        with pytest.raises(FireflyError, message="Expected FireflyError"):
            c.square(a=4)
