"""
util functions for qoo
"""
import datetime
import json
import re
from typing import Any, Mapping


FIRST_CAP = re.compile("(.)([A-Z][a-z]+)")
ALL_CAP = re.compile("([a-z0-9])([A-Z])")

# this allows us to use datetime in json dumps
json.JSONEncoder.default = lambda self, obj: (  # type: ignore
    obj.isoformat() if isinstance(obj, datetime.datetime) else None
)


def jsonl(json_string: str) -> Mapping:
    """loads a dict from a given json string"""
    return json.loads(json_string)


def jsond(obj: Mapping, **kwargs: Any) -> str:
    """performs a json dump with our given patch"""
    return json.dumps(obj, **kwargs)


def snakeify(text: str) -> str:
    """camelCase to snake_case"""
    first_string = FIRST_CAP.sub(r"\1_\2", text)
    return ALL_CAP.sub(r"\1_\2", first_string).lower()
