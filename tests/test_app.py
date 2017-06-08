from webob import Request, Response
from firefly.app import FireflyFunction

def square(a):
    return a**2

def test_firefly_function_response():
    func = FireflyFunction(square)
    request = Request.blank("/", POST='{"a": 1}')
    response = func(request)
    assert response.status == '200 OK'
