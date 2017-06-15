from webob import Request, Response
from firefly.app import Firefly, FireflyFunction

def square(a):
    '''Computes square'''
    return a**2

class TestFirefly:
    def test_generate_function_list(self):
        firefly = Firefly()
        firefly.add_route("/square", square, "square")
        returned_dict = {
                "square": {
                    "path": "/square",
                    "doc": "Computes square"
                }
            }
        assert firefly.generate_function_list() == returned_dict

class TestFireflyFunction:
    def test_call(self):
        func = FireflyFunction(square)
        request = Request.blank("/square", POST='{"a": 3}')
        response = func(request)
        assert response.status == '200 OK'
        assert response.text == '9'
