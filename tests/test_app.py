from webob import Request, Response
from firefly.app import Firefly, FireflyFunction

def square(a):
    '''Computes square'''
    return a**2

class TestFirefly:
    def test_generate_function_list(self):
        firefly = Firefly()
        assert firefly.generate_function_list() == {}

        firefly.add_route("/square", square, "square")
        returned_dict = {
                "square": {
                    "path": "/square",
                    "doc": "Computes square"
                }
            }
        assert firefly.generate_function_list() == returned_dict

    def test_generate_function_list_for_func_name(self):
        firefly = Firefly()
        firefly.add_route("/sq2", square, "sq")
        returned_dict = {
                "sq": {
                    "path": "/sq2",
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
