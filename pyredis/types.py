from abc import ABC
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
    data: bytes


@dataclass
class Array:
    data: []
