"""
util functions for qoo
"""
import datetime
import json
import re
import uuid
from typing import Any, Iterator, List, Mapping


FIRST_CAP = re.compile("(.)([A-Z][a-z]+)")
ALL_CAP = re.compile("([a-z0-9])([A-Z])")

# this allows us to use datetime in json dumps
json.JSONEncoder.default = lambda self, obj: (  # type: ignore
    obj.isoformat() if isinstance(obj, datetime.datetime) else None
)


def new_uuid() -> str:
    """returns a fresh uuid"""
    return str(uuid.uuid4())


def jsonl(json_string: str) -> Mapping:
    """loads a dict from a given json string"""
    return json.loads(json_string)


def jsond(obj: Mapping, **kwargs: Any) -> str:
    """performs a json dump with our given patch"""
    return json.dumps(obj, **kwargs)


def chunk(items: List, size: int = 10) -> Iterator[List]:
    """chunk a list into n lists of $size"""
    for x in range(0, len(items), size):
        yield items[x : x + size]
