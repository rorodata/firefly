import cgi
import json
import functools
import logging
from .validator import validate_args, ValidationError
from .utils import json_encode, is_file, FileIter
from .version import __version__
import threading
from flask import Flask, jsonify, request
from wsgiref.simple_server import make_server
from .routing import FireflyRule

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
    def __init__(self, auth_token=None, allowed_origins="", flask_app=None):
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
        self.auth_token = auth_token
        self.allowed_origins = allowed_origins
        self.flask_app = flask_app or Flask("firefly")

        # Install custom url rule to use type annotations in parsing urls
        self.flask_app.url_rule_class = FireflyRule

    def set_auth_token(self, token):
        self.auth_token = token

    def set_allowed_origins(self, allowed_origins):
        # Also support mutliple origins as a list.
        if isinstance(allowed_origins, list):
            allowed_origins = ", ".join(allowed_origins)
        self.allowed_origins = allowed_origins or ""

    def function(self, func):
        name = func.__name__
        path = "/" + name
        method = "POST"
        return self.add_route(path=path, func=func, method=method, endpoint=name)

    def route(self, path, method="GET", endpoint=None):
        def decorator(f):
            self.add_route(path=path, method=method, endpoint=endpoint, func=f)
            return f
        return decorator

    def add_route(self, path, func, endpoint=None, method=None, **kwargs):
        endpoint = endpoint or func.__name__
        method = method or "POST"

        view_func = ViewFunction(func, name=endpoint)

        self.flask_app.add_url_rule(
            rule=path,
            endpoint=endpoint,
            view_func=view_func,
            methods=[method],
            view_function=view_func,
            **kwargs)

    def run(self, *args, **kwargs):
        self.flask_app.run(*args, **kwargs)

class ViewFunction(object):
    def __init__(self, function, name=None, **options):
        self.function = function
        self.options = options
        self.name = name or function.__name__
        self.doc = function.__doc__ or ""
        self.sig = signature(function)
        self.route_params = set()

    def set_route_params(self, params):
        """Sets the names of the parameters that comes
        from the URL rule.

        This method is called when a new FireflyRule is created.
        """
        self.route_params = set(params)

    def __repr__(self):
        return "<ViewFunction %r>" % self.function

    def __call__(self, **route_kwargs):
        kwargs = dict(route_kwargs)

        if request.method in ("POST", "PUT"):
            kwargs.update(self._get_post_data())
        else:
            kwargs.update(self.parse_request_args(request.args))

        kwargs = {k:v for k, v in kwargs.items() if k in self.sig.parameters}
        result = self.function(**kwargs)
        # if method is POST, also pass the POST parameters
        return jsonify(result)

    def _get_post_data(self):
        if request.content_type == 'application/json':
           return request.json
        elif request.content_type == 'application/x-www-form-urlencoded':
            return self.parse_request_args(request.form)
        return {}

    def parse_request_args(self, args):
        """Returns the arguments from GET parameters or POST form.
        """
        request_args = {}
        for name in self.sig.parameters:
            param = self.sig.parameters[name]
            if name in self.route_params:
                continue
            elif name in args:
                value = args[name]
                argtype = param.annotation
                try:
                    request_args[name] = self.parse_request_arg(argtype, value)
                except ValueError as e:
                    logger.error("Failed to parse value of %s: %s", name, value)
                    pass
            elif param.default is not param.empty:
                request_args[name] = param.default
            else:
                raise LookupError("Required argument %r is not provided or invalid." % name)
        return request_args

    def parse_request_param(self, type, value):
        """Parses a request parameter and tries to convert it to specified type.

        The type comes from the type annocation specified in the
        view function definition and the parameter value comes
        either from GET or POST request.
        """
        if isinstance(value, list):
            value = value[0]
        if type in [int, float, str]:
            return type(value)
        else:
            return value
