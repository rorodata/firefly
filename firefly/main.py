import os
import sys
import argparse
import importlib
import yaml
from .app import Firefly
from .server import FireflyServer
from .validator import ValidationError, FireflyError

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("-b", "--bind", dest="ADDRESS", default="127.0.0.1:8000")
    p.add_argument("-c", "--config", dest="CONFIG_FILE", default=None)
    p.add_argument("functions", nargs='*', help="functions to serve")
    return p.parse_args()

def load_function(function_spec):
    if "." not in function_spec:
        raise Exception("Invalid function, please specify it as module.function")

    mod_name, func_name = function_spec.rsplit(".", 1)
    mod = importlib.import_module(mod_name)
    func = getattr(mod, func_name)
    return ("/"+func_name, func_name, func)

def load_functions(function_specs):
    return [load_function(function_spec) for function_spec in function_specs]

def parse_config_file(config_file):
    if not os.path.exists(config_file):
        raise FireflyError("Specified config file does not exist.")
    with open(config_file) as f:
        config_dict = yaml.safe_load(f)
    return config_dict

def parse_config_data(config_dict):
    return [(spec["path"], func_name, load_function(spec["function"])[2])
            for func_name, spec in config_dict["functions"].items()]

def add_routes(app, functions):
    for path, name, function in functions:
        app.add_route(path, function, name)

def main():
    # ensure current directory is added to sys.path
    if "" not in sys.path:
        sys.path.insert(0, "")

    args = parse_args()
    print(len(args.functions), args.CONFIG_FILE)
    if (len(args.functions) > 0 and args.CONFIG_FILE) or (len(args.functions) == 0 and not args.CONFIG_FILE):
        raise FireflyError("Invalid arguments provided. Please specify either a config file or a list of functions.")

    if len(args.functions):
        functions = load_functions(args.functions)
    elif args.CONFIG_FILE:
        functions = parse_config_data(parse_config_file(args.CONFIG_FILE))

    app = Firefly()
    add_routes(app, functions)

    server = FireflyServer(app, {"bind": args.ADDRESS})
    server.run()
