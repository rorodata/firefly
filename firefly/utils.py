import sys
import json

PY2 = (sys.version_info.major == 2)
PY3 = (sys.version_info.major == 3)

def json_encode(data):
    result = json.dumps(data)
    if PY2:
        result = result.decode('utf-8')
    return result

def is_file(obj):
    return hasattr(obj, "read")

class FileIter:
    def __init__(self, fileobj, chunk_size=4096):
        self.fileobj = fileobj
        self.chunk_size = chunk_size

    def __iter__(self):
        while True:
            chunk = self.fileobj.read(self.chunk_size)
            if not chunk:
                break
            yield chunk
