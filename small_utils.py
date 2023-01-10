import os
from pathlib import Path
import sys
import base64
import hashlib
import secrets
from contextlib import contextmanager
from functools import wraps
from os import environ

from typing import Any, Dict, Iterable, Iterator, Optional, Sequence, TypeVar, Mapping, List, TypedDict, Union

from dlt.common.typing import AnyFun, StrAny, DictStrAny, StrStr, TAny, TDataItem, TDataItems, TFun

T = TypeVar("T")


def chunks(seq: Sequence[T], n: int) -> Iterator[Sequence[T]]:
    for i in range(0, len(seq), n):
        yield seq[i:i + n]


def digest128(v: str) -> str:
    return base64.b64encode(
        hashlib.shake_128(
            v.encode("utf-8")
        ).digest(15)
    ).decode('ascii')


def str2bool(v: str) -> bool:
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise ValueError('Boolean value expected.')


def flatten_list_of_dicts(dicts: Sequence[StrAny]) -> StrAny:
    """
    Transforms a list of objects [{K: {...}}, {L: {....}}, ...] -> {K: {...}, L: {...}...}
    """
    o: DictStrAny = {}
    for d in dicts:
        for k,v in d.items():
            if k in o:
                raise KeyError(f"Cannot flatten with duplicate key {k}")
            o[k] = v
    return o
