from webob import Request, Response
from firefly.app import FireflyFunction

def square(a):
    return a**2

class TestFireflyFunction:
    def test_call(self):
        func = FireflyFunction(square)
        request = Request.blank("/", POST='{"a": 3}')
        response = func(request)
        assert response.status == '200 OK'
        assert response.text == '9'
