from dataclasses import dataclass
from typing import Sequence


@dataclass
class SimpleString:
    value: str


@dataclass
class SimpleError:
    data: str


@dataclass
class Integer:
    data: int


@dataclass
class BulkString:
    data: str


@dataclass
class Array:
    data: []
