import io
import pytest
import requests
from firefly.client import Client, RemoteFunction, FireflyError
from firefly.validator import ValidationError

class MockResponse:
    def __init__(self, status_code, data, headers=None):
        self.status_code = status_code
        self.data = data
        self.headers = headers or {}
        self.headers.setdefault("Content-Type", "application/json")

    def json(self):
        return self.data

def make_monkey_patch(status, return_data, mode='json'):
    def mock_post_response(url, json=None, data=None, files=None, headers=None, **kwargs):
        r = MockResponse(status_code=status, data=return_data, headers=headers)
        return r
    return mock_post_response

class TestClass:
    def test_call_for_success_event(self, monkeypatch):
        monkeypatch.setattr(requests, "post", make_monkey_patch(200, 16))
        monkeypatch.setattr(requests, "get", make_monkey_patch(200, {}))
        c = Client("http://127.0.0.1:8000")
        assert c.square(a=4) == 16

    def test_call_for_validation_error(self, monkeypatch):
        monkeypatch.setattr(requests, "post", make_monkey_patch(404, {"status": "not found"}))
        monkeypatch.setattr(requests, "get", make_monkey_patch(200, {}))
        c = Client("http://127.0.0.1:8000")
        with pytest.raises(FireflyError, message="Expected FireflyError"):
            c.sq(a=4)

    def test_call_for_validation_error(self, monkeypatch):
        monkeypatch.setattr(requests, "post", make_monkey_patch(422, {"error": "missing a required argument: 'a'"}))
        monkeypatch.setattr(requests, "get", make_monkey_patch(200, {}))
        c = Client("http://127.0.0.1:8000")
        with pytest.raises(ValidationError, message="Expected ValidationError"):
            c.square(b=4)

    def test_call_for_server_error(self, monkeypatch):
        monkeypatch.setattr(requests, "post", make_monkey_patch(500, {"error": "ValueError: Dummy Error"}))
        monkeypatch.setattr(requests, "get", make_monkey_patch(200, {}))
        c = Client("http://127.0.0.1:8000")
        with pytest.raises(FireflyError, message="Expected FireflyError"):
            c.square(a=4)

    def test_call_for_uncaught_exception(self, monkeypatch):
        monkeypatch.setattr(requests, "post", make_monkey_patch(502, ""))
        monkeypatch.setattr(requests, "get", make_monkey_patch(200, {}))
        c = Client("http://127.0.0.1:8000")
        with pytest.raises(FireflyError, message="Expected FireflyError"):
            c.square(a=4)

    def test_call_with_file_upload(self, monkeypatch):
        def filesize(data):
            return len(data.read())
        f = io.StringIO(u"test file contents")
        monkeypatch.setattr(requests, "post", make_monkey_patch(200, "18"))
        monkeypatch.setattr(requests, "get", make_monkey_patch(200, {}))
        c = Client("http://127.0.0.1:8000")
        assert c.filesize(data=f) == "18"

    def test_decouple_files_with_files(self):
        f = io.StringIO(u"test file contents")
        c = Client("http://127.0.0.1:8000")
        kwargs = {'file': f}
        data, files = c.decouple_files(kwargs)
        assert data == {}
        assert files['file'] == f

    def test_decouple_files_with_no_files(self):
        c = Client("http://127.0.0.1:8000")
        kwargs = {'a': 1, 'b': 'c'}
        data, files = c.decouple_files(kwargs)
        assert data['a'] == 1
        assert data['b'] == 'c'
        assert files == {}

    def test_decouple_files_with_combined_input(self):
        f = io.StringIO(u"test file contents")
        c = Client("http://127.0.0.1:8000")
        kwargs = {'file': f, 'a': 1}
        data, files = c.decouple_files(kwargs)
        assert data['a'] == 1
        assert files['file'] == f

    def is_file_present(self):
        f = io.StringIO(u"test file contents")
        c = Client("http://127.0.0.1:8000")
        is_a_file = c.is_file(f)
        assert is_a_file == True

    def is_file_absent(self):
        c = Client("http://127.0.0.1:8000")
        is_a_file = c.is_file(1)
        assert is_a_file == False
