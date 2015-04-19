import os
import json

from datetime import datetime, date
from decimal import Decimal


def json_default(obj):
    if isinstance(obj, (datetime, date)):
        obj = obj.isoformat()
    if isinstance(obj, Decimal):
        obj = float(obj)
    return obj


def write_json(project, path, obj):
    path = os.path.join(project.path, path)
    try:
        os.makedirs(os.path.dirname(path))
    except:
        pass
    with open(path, 'wb') as fh:
        json.dump(obj, fh, default=json_default, indent=2)
