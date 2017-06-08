import sys
import json

PY2 = (sys.version_info.major == 2)
PY3 = (sys.version_info.major == 3)

def json_encode(data):
    if PY2:
        return json.dumps(data).decode('utf-8')
    return json.dumps(data)
