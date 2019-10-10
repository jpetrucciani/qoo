"""
@author jacobi petrucciani
@desc util functions for qoo
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
    """
    @cc 1
    @desc generate a new uuid with the built in uuid library
    @ret a fresh uuid
    """
    return str(uuid.uuid4())


def jsonl(json_string: str) -> Mapping:
    """
    @cc 1
    @desc loads a dict from a given json string
    @arg json_string: the json string to parse
    @ret a mapping pulled from the json
    """
    return json.loads(json_string)


def jsond(obj: Mapping, **kwargs: Any) -> str:
    """
    @cc 1
    @desc performs a json dump with our given patch
    @arg obj: the dict/list to dump into a string
    @ret a json encoded string
    """
    return json.dumps(obj, **kwargs)


def chunk(items: List, size: int = 10) -> Iterator[List]:
    """
    @cc 2
    @desc chunk a list into n lists of a certain size
    @arg items: a list of items to chunk
    @arg size: the size of the chunked lists
    @ret an iterator of lists
    """
    for index in range(0, len(items), size):
        yield items[index : index + size]
