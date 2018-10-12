import io
import sys
import pytest
from webob import Request, Response
from firefly.app import Firefly, FireflyFunction, ctx

py2_only = pytest.mark.skipif(sys.version_info.major >= 3, reason="Requires Python 2")
py3_only = pytest.mark.skipif(sys.version_info.major < 3, reason="Requires Python 3+")

def square(a):
    '''Computes square'''
    return a**2

def dummy():
    return

class TestFirefly:
    def test_generate_function_list(self):
        firefly = Firefly()
        assert firefly.generate_function_list() == {}

        firefly.add_route("/square", square, "square")
        returned_dict = {
                "square": {
                    "path": "/square",
                    "doc": "Computes square",
                    "parameters": [
                        {
                            "name": "a",
                            "kind": "POSITIONAL_OR_KEYWORD"
                        }
                    ]
                }
            }
        assert firefly.generate_function_list() == returned_dict

    def test_generate_function_list_for_func_name(self):
        firefly = Firefly()
        firefly.add_route("/sq2", square, "sq")
        returned_dict = {
                "sq": {
                    "path": "/sq2",
                    "doc": "Computes square",
                    "parameters": [
                        {
                            "name": "a",
                            "kind": "POSITIONAL_OR_KEYWORD"
                        }
                    ]
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

    def test_ctx(self):
        def peek_ctx():
            keys = sorted(ctx.__dict__.keys())
            return list(keys)

        app = Firefly()
        app.add_route("/", peek_ctx)

        request = Request.blank("/", POST='{}')
        response = app.process_request(request)
        assert response.status == '200 OK'
        assert response.json == ['request']

    def test_ctx_cross_request(self):
        def peek_ctx():
            print("peek_ctx", ctx.__dict__)
            ctx.count = getattr(ctx, "count", 0) + 1
            return ctx.count

        app = Firefly()
        app.add_route("/", peek_ctx)

        request = Request.blank("/", POST='{}')
        response = app.process_request(request)
        assert response.status == '200 OK'
        assert response.json == 1

        # Subsequent requests should not have count in the context
        request = Request.blank("/", POST='{}')
        response = app.process_request(request)
        assert response.status == '200 OK'
        assert response.json == 1

class TestFireflyFunction:
    def test_call(self):
        func = FireflyFunction(square)
        request = Request.blank("/square", POST='{"a": 3}')
        response = func(request)
        assert response.status == '200 OK'
        assert response.text == '9'

    def test_call_for_bad_request(self):
        def sum(a):
            return sum(a)
        func = FireflyFunction(sum)
        request = Request.blank("/sum", POST='{"a": [3 8]}')
        response = func(request)
        assert response.status == '400 Bad Request'

    def test_call_for_internal_function_error(self):
        def dummy(a):
            raise ValueError("This is a test")
        req = Request.blank('/dummy', POST='{"a": 1}')
        func = FireflyFunction(dummy)
        resp = func(req)
        assert resp.status == '500 Internal Server Error'
        assert resp.json == {'error': 'ValueError: This is a test'}

    def test_call_for_file_inputs(self):
        def filesize(data):
            return len(data.read())
        f = io.StringIO(u"test file contents")
        req = Request.blank('/filesize', POST={'data': ('test', f)})
        func = FireflyFunction(filesize)
        resp = func(req)
        assert resp.status == '200 OK'
        assert resp.body == b'18'

    def test_get_multipart_formdata_inputs_with_files(self):
        f = io.StringIO(u"test file contents")
        g = io.StringIO(u"test file contents")
        req = Request.blank('/filesize', POST={'data': ('test', f)})
        func = FireflyFunction(dummy)
        d = func.get_multipart_formdata_inputs(req)
        assert d['data'].read().decode() == g.read()

    def test_get_multipart_formdata_inputs_with_combined_inputs(self):
        f = io.StringIO(u"test file contents")
        g = io.StringIO(u"test file contents")
        req = Request.blank('/filesize', POST={'data': ('test', f), 'abc': 'hi', 'xyz': '1'})
        func = FireflyFunction(dummy)
        d = func.get_multipart_formdata_inputs(req)
        assert d['data'].read().decode() == g.read()
        assert d['abc'] == 'hi'
        assert d['xyz'] == '1'

    def test_get_multipart_formdata_inputs_with_no_files(self):
        def dummy():
            pass
        req = Request.blank('/filesize', POST={'abc': 'hi', 'xyz': 1})
        func = FireflyFunction(dummy)
        d = func.get_multipart_formdata_inputs(req)
        assert d['abc'] == 'hi'
        assert d['xyz'] == '1'

    def test_get_content_type_present(self):
        req = Request.blank('/', headers={'Content-Type': 'multipart/form-data'})
        func = FireflyFunction(dummy)
        content_type = func.get_content_type(req)
        assert content_type == 'multipart/form-data'

    def test_get_content_type_absent(self):
        req = Request.blank('/')
        func = FireflyFunction(dummy)
        content_type = func.get_content_type(req)
        assert content_type == 'application/octet-stream'

    @py2_only
    def test_generate_signature(self):
        def sample_function(x, one="hey", two=None, **kwargs):
            pass
        func = FireflyFunction(sample_function)
        assert len(func.sig) == 4
        assert func.sig[0]['name'] == 'x'
        assert func.sig[0]['kind'] == 'POSITIONAL_OR_KEYWORD'
        assert func.sig[1]['name'] == 'one'
        assert func.sig[1]['kind'] == 'POSITIONAL_OR_KEYWORD'
        assert func.sig[1]['default'] == 'hey'
        assert func.sig[2]['default'] == None
        assert func.sig[3]['name'] == 'kwargs'
        assert func.sig[3]['kind'] == 'VAR_KEYWORD'

    @py3_only
    def test_generate_signature_py3(self):
        # work-around to avoid syntax error in python 2
        code = 'def f(x, y=1, *, one="hey", two=None, **kwargs): pass'
        env = {}
        exec(code, env, env)
        f = env['f']

        func = FireflyFunction(f)
        assert len(func.sig) == 5
        assert func.sig[0]['name'] == 'x'
        assert func.sig[0]['kind'] == 'POSITIONAL_OR_KEYWORD'
        assert func.sig[1]['default'] == 1
        assert func.sig[2]['name'] == 'one'
        assert func.sig[2]['kind'] == 'KEYWORD_ONLY'
        assert func.sig[2]['default'] == 'hey'
        assert func.sig[3]['default'] == None
        assert func.sig[4]['name'] == 'kwargs'
        assert func.sig[4]['kind'] == 'VAR_KEYWORD'
