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

    def test_function_call(self):
        app = Firefly()
        app.add_route("/", square)

        request = Request.blank("/", POST='{"a": 3}')
        response = app.process_request(request)
        assert response.status == '200 OK'
        assert response.text == '9'

    def test_auth_failure(self):
        app = Firefly(auth_token='abcd')
        app.add_route("/", square)

        request = Request.blank("/", POST='{"a": 3}')
        response = app.process_request(request)
        print(response.text)
        assert response.status == '403 Forbidden'

        headers = {
            "Authorization": "token bad-token"
        }
        request = Request.blank("/", POST='{"a": 3}', headers=headers)
        response = app.process_request(request)
        assert response.status == '403 Forbidden'

    def test_http_error_404(self):
        app = Firefly()
        app.add_route("/", square)

        request = Request.blank("/sq", POST='{"a": 3}')
        response = app.process_request(request)
        assert response.status == '404 Not Found'

class TestFireflyFunction:
    def test_call(self):
        func = FireflyFunction(square)
        request = Request.blank("/square", POST='{"a": 3}')
        response = func(request)
        assert response.status == '200 OK'
        assert response.text == '9'
