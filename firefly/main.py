import os
import sys
import argparse
import importlib
import yaml
import logging
from .app import Firefly
from .validator import ValidationError, FireflyError
from wsgiref.simple_server import make_server

logger = logging.getLogger("firefly")

def load_from_env():
    functions = None
    token = None
    allow_origins = ''

    if 'FIREFLY_FUNCTIONS' in os.environ:
        function_names = os.environ['FIREFLY_FUNCTIONS'].split(",")
        try:
            functions = load_functions(function_names)
        except (ImportError, AttributeError) as err:
            sys.exit(1)

    if 'FIREFLY_TOKEN' in os.environ:
        token = os.environ['FIREFLY_TOKEN']

    if 'FIREFLY_ALLOW_ORIGINS' in os.environ:
        allow_origins = os.environ['FIREFLY_ALLOW_ORIGINS']

    if 'FIREFLY_CONFIG' in os.environ:
        logger.info("loading config file: %s", os.environ['FIREFLY_CONFIG'])
        functions, token = parse_config_data(parse_config_file(os.environ['FIREFLY_CONFIG']))

    if functions:
        add_routes(app, functions)

    if token:
        app.set_auth_token(token)

    if allow_origins:
        app.set_allowed_origins(allow_origins)

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("-t", "--token", help="token to authenticate the requests")
    p.add_argument("-b", "--bind", dest="ADDRESS", default="127.0.0.1:8000")
    p.add_argument("-c", "--config", dest="config_file", default=None)
    p.add_argument("--allow-origins", default=None, help="Origins to allow for cross-origin resource sharing")
    p.add_argument("functions", nargs='*', help="functions to serve")
    return p.parse_args()

def load_function(function_spec, path=None, name=None):
    if "." not in function_spec:
        raise Exception("Invalid function: {}, please specify it as module.function".format(function_spec))

    mod_name, func_name = function_spec.rsplit(".", 1)
    try:
        mod = importlib.import_module(mod_name)
        func = getattr(mod, func_name)
    except (ImportError, AttributeError) as err:
        print("Failed to load {}: {}".format(function_spec, str(err)))
        raise
    path = path or "/"+func_name
    name = name or func_name
    return (path, name, func)

def load_functions(function_specs):
    return [load_function(function_spec) for function_spec in function_specs]

def parse_config_file(config_file):
    if not os.path.exists(config_file):
        raise FireflyError("Specified config file does not exist.")
    with open(config_file) as f:
        config_dict = yaml.safe_load(f)
    return config_dict

def parse_config_data(config_dict):
    functions = [(load_function(f["function"], path=f.get("path"), name=name, ))
            for name, f in config_dict["functions"].items()]
    token = config_dict.get("token", None)
    return functions, token

def add_routes(app, functions):
    for path, name, function in functions:
        app.add_route(path, function, name)

def setup_logger():
    level = logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(name)s [%(levelname)s] %(message)s",
        datefmt='%Y-%m-%d %H:%M:%S')

def main():
    # ensure current directory is added to sys.path
    if "" not in sys.path:
        sys.path.insert(0, "")

    args = parse_args()

    if (args.functions and args.config_file) or (not args.functions and not args.config_file):
        raise FireflyError("Invalid arguments provided. Please specify either a config file or a list of functions.")

    token = None

    if len(args.functions):
        functions = load_functions(args.functions)
    elif args.config_file:
        functions, token = parse_config_data(parse_config_file(args.config_file))

    token = token or args.token

    app.set_auth_token(token)
    app.set_allowed_origins(args.allow_origins)
    add_routes(app, functions)

    host, port = args.ADDRESS.split(":", 1)
    port = int(port)
    print("http://{}/".format(args.ADDRESS))
    server = make_server(host, port, app)
    server.serve_forever()

setup_logger()
logger.info("Starting Firefly...")
app = Firefly()
load_from_env()
