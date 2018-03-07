import cgi
from webob import Request, Response
from webob.exc import HTTPNotFound
import json
import logging
from .validator import validate_args, ValidationError
from .utils import json_encode, is_file, FileIter
from .version import __version__
import threading

try:
    from inspect import signature, _empty
except:
    from funcsigs import signature, _empty

logger = logging.getLogger("firefly")

# XXX-Anand
# Hack to store the request-local context.
# Need to think of a better way to handle this
# or switch to Flask.
ctx = threading.local()
ctx.request = None

class Firefly(object):
    def __init__(self, auth_token=None, allowed_origins=""):
        """Creates a firefly application.

        If the optional parameter auth_token is specified, the
        only the requests which provide that auth token in authorization
        header are allowed.

        The Cross Origin Request Sharing is disabled by default. To enable it,
        pass the allowed origins as allowed_origins. To allow all origins, set it
        to ``*``.

        :param auth_token: the auto_token for the application
        :param allowed_origins: allowed origins for cross-origin requests
        """
        self.mapping = {}
        self.add_route('/', self.generate_index,internal=True)
        self.auth_token = auth_token
        self.allowed_origins = allowed_origins


    def set_auth_token(self, token):
        self.auth_token = token

    def set_allowed_origins(self, allowed_origins):
        # Also support mutliple origins as a list.
        if isinstance(allowed_origins, list):
            allowed_origins = ", ".join(allowed_origins)
        self.allowed_origins = allowed_origins or ""

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

    def _prepare_cors_headers(self):
        if self.allowed_origins:
            headers = {
                'Access-Control-Allow-Origin': self.allowed_origins,
                'Access-Control-Allow-Methods': 'GET,POST',
                'Access-Control-Allow-Headers': 'Content-Type'
            }
            return list(headers.items())
        else:
            return []

    def process_request(self, request):
        if not self.verify_auth_token(request):
            return self.http_error('403 Forbidden', error='Invalid auth token')

        # Clear all the existing state, if any
        ctx.__dict__.clear()

        ctx.request = request

        path = request.path_info
        if path in self.mapping:
            func = self.mapping[path]
            if request.method == 'OPTIONS':
                response = Response(status='200 OK', body=b'')
            else:
                response = func(request)
            response.headerlist += self._prepare_cors_headers()
        else:
            response = self.http_error('404 Not Found', error="Not found: " + path)

        ctx.request = None
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

        logger.info("calling function %s", self.name)
        try:
            kwargs = self.get_inputs(request)
        except ValueError as err:
            logger.warn("Function %s failed with ValueError: %s.", self.name, err)
            return self.make_response({"error": str(err)}, status=400)

        try:
            validate_args(self.function, kwargs)
        except ValidationError as err:
            logger.warn("Function %s failed with ValidationError: %s.", self.name, err)
            return self.make_response({"error": str(err)}, status=422)

        try:
            result = self.function(**kwargs)
        except HTTPError as e:
            return e.get_response()
        except Exception as err:
            logger.error("Function %s failed with exception.", self.name, exc_info=True)
            return self.make_response(
                    {"error": "{}: {}".format(err.__class__.__name__, str(err))}, status=500
                )
        return self.make_response(result)

    def get_inputs(self, request):
        content_type = self.get_content_type(request)
        if content_type == 'multipart/form-data':
            return self.get_multipart_formdata_inputs(request)
        else:
            return json.loads(request.body.decode('utf-8'))

    def get_content_type(self, request):
        content_type = request.headers.get('Content-Type', 'application/octet-stream')
        return content_type.split(';')[0]

    def get_multipart_formdata_inputs(self, request):
        d = {}
        for name, value in request.POST.items():
            if isinstance(value, cgi.FieldStorage):
                value = value.file
            d[name] = value
        return d

    def make_response(self, result, status=200):
        if is_file(result):
            response = Response(content_type='application/octet-stream')
            response.app_iter = FileIter(result)
        else:
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

class HTTPError(Exception):
    """Exception to be raised to send different HTTP status codes.
    """
    def __init__(self, status_code, body, headers={}):
        self.status_code = status_code
        self.body = body
        self.headers = headers

    def get_response(self):
        response = Response()
        response.status = self.status_code
        response.text = self.body
        response.headers.update(self.headers)
        return response
