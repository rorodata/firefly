from webob import Request, Response
from webob.exc import HTTPNotFound
import json
from .validator import validate_args, ValidationError
from .utils import json_encode
from .version import __version__

try:
    from inspect import signature, _empty
except:
    from funcsigs import signature, _empty


class Firefly(object):
    def __init__(self, auth_token=None):
        self.mapping = {}
        self.add_route('/', self.generate_index,internal=True)
        self.auth_token = auth_token

    def set_auth_token(self, token):
        self.auth_token = token

    def add_route(self, path, function, function_name=None, **kwargs):
        self.mapping[path] = FireflyFunction(function, function_name, **kwargs)

    def generate_function_list(self):
        return {f.name: {"path": path, "doc": f.doc, "parameters": f.sig}
                for path, f in self.mapping.items()
                if f.options.get("internal") != True}

    def generate_index(self):
        help_dict = {
            "app": "firefly",
            "version": __version__,
            "functions": self.generate_function_list()
            }
        return help_dict

    def __call__(self, environ, start_response):
        request = Request(environ)
        response = self.process_request(request)
        return response(environ, start_response)

    def verify_auth_token(self, request):
        return not self.auth_token or self.auth_token == self._get_auth_token(request)

    def _get_auth_token(self, request):
        auth = request.headers.get("Authorization")
        if auth and auth.lower().startswith("token"):
            return auth[len("token"):].strip()

    def http_error(self, status, error=None):
        response = Response()
        response.status = status
        response.text = json_encode({"error": error})
        return response

    def process_request(self, request):
        if not self.verify_auth_token(request):
            return self.http_error('403 Forbidden', error='Invalid auth token')

        path = request.path_info
        if path in self.mapping:
            func = self.mapping[path]
            response = func(request)
        else:
            response = self.http_error('404 Not Found', error="Not found")
        return response

class FireflyFunction(object):
    def __init__(self, function, function_name=None, **options):
        self.function = function
        self.options = options
        self.name = function_name or function.__name__
        self.doc = function.__doc__ or ""
        self.sig = self.generate_signature(function)

    def __repr__(self):
        return "<FireflyFunction %r>" % self.function

    def __call__(self, request):
        if self.options.get("internal", False):
            return self.make_response(self.function())

        try:
            kwargs = self.get_inputs(request)
        except ValueError as err:
            return self.make_response({"error": str(err)}, status=400)

        try:
            validate_args(self.function, kwargs)
        except ValidationError as err:
            return self.make_response({"error": str(err)}, status=422)

        result = self.function(**kwargs)
        return self.make_response(result)

    def get_inputs(self, request):
        return json.loads(request.body.decode('utf-8'))

    def make_response(self, result, status=200):
        response = Response(content_type='application/json',
                            charset='utf-8')
        response.text = json_encode(result)
        response.status = status
        return response

    def generate_signature(self, f):
        func_sig = signature(f)
        params = []

        for param_name, param_obj in func_sig.parameters.items():
            param = {
                "name": param_name,
                "kind": str(param_obj.kind)
            }
            if param_obj.default is not _empty:
                param["default"] = param_obj.default
            params += [param]

        return params
