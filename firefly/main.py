import sys
import argparse
import importlib
from .app import Firefly
from .server import FireflyServer

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("-b", "--bind", dest="ADDRESS", default="127.0.0.1:8000")
    p.add_argument("functions", nargs='+', help="functions to serve")
    return p.parse_args()

def load_function(function_spec):
    if "." not in function_spec:
        raise Exception("Invalid function, please specify it as module.function")

    mod_name, func_name = function_spec.rsplit(".", 1)
    mod = importlib.import_module(mod_name)
    func = getattr(mod, func_name)
    return (func_name, func)

def load_functions(function_specs):
    return [load_function(function_spec) for function_spec in function_specs]

def add_routes(app, functions):
    for name, function in functions:
        app.add_route('/'+name, function, name)

def main():
    # ensure current directory is added to sys.path
    if "" not in sys.path:
        sys.path.insert(0, "")

    args = parse_args()
    functions = load_functions(args.functions)

    app = Firefly()
    add_routes(app, functions)

    server = FireflyServer(app, {"bind": args.ADDRESS})
    server.run()
