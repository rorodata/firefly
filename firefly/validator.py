from .utils import PY2, PY3

if PY3:
    from inspect import signature
else:
    from funcsigs import signature

class ValidationError(Exception):
    pass

class FireflyError(Exception):
    pass

def validate_args(function, kwargs):
    function_signature = signature(function)
    try:
        function_signature.bind(**kwargs)
    except TypeError as err:
        raise ValidationError(str(err))
