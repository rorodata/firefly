from webob import Request, Response
from webob.exc import HTTPNotFound
import json
from .validator import validate_args, ValidationError
from .utils import json_encode
from .version import __version__

class Firefly(object):
    def __init__(self):
        self.mapping = {}
        self.add_route('/', self.generate_index,internal=True)

    def add_route(self, path, function, function_name=None, **kwargs):
        self.mapping[path] = FireflyFunction(function, function_name, **kwargs)

    def generate_function_list(self):
        return {f.name: {"path": path, "doc": f.doc}
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
        path = request.path_info
        if path in self.mapping:
            func = self.mapping[path]
            response = func(request)
        else:
            response = Response()
            response.status = "404 Not Found"
            response.text = json_encode({"status": "not found"})
        return response(environ, start_response)


class FireflyFunction(object):
    def __init__(self, function, function_name=None, **options):
        self.function = function
        self.options = options
        self.name = function_name or function.__name__
        self.doc = function.__doc__ or ""

    def __call__(self, request):
        if self.options.get("internal", False):
            return self.make_response(self.function())

        kwargs = self.get_inputs(request)
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
