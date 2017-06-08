import sys
import json

PY2 = (sys.version_info.major == 2)
PY3 = (sys.version_info.major == 3)

def json_encode(data):
    result = json.dumps(data)
    if PY2:
        result = result.decode('utf-8')
    return result
