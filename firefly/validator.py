import sys

if sys.version_info[0] >= 3:
    from inspect import signature
else:
    from funcsigs import signature

class ValidationError(Exception):
    pass

def validate_args(function, kwargs):
    function_signature = signature(function)
    try:
        function_signature.bind(**kwargs)
    except TypeError as err:
        raise ValidationError(str(err))
