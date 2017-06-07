import pytest
from firefly.validator import *

def add(a, b):
    return a + b

def test_equal_args():
    try:
        validate_args(add, {"a": 1, "b":2})
    except ValidationError:
        pytest.fail("Did not expect a ValidationError")

def test_less_args():
    with pytest.raises(ValidationError, message="Expected a ValidationError"):
        validate_args(add, {"a": 1})

def test_more_args():
    with pytest.raises(ValidationError, message="Expected a ValidationError"):
        validate_args(add, {"a":1, "b":2, "c":3})
