import os
from firefly.main import load_function

def test_load_functions():
    os.path.exists2 = os.path.exists
    path, name, func = load_function("os.path.exists2")
    assert path == "/exists2"
    assert name == "exists2"
    assert func == os.path.exists
