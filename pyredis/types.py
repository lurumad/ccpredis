from dataclasses import dataclass


@dataclass
class SimpleString:
    value: str


@dataclass
class SimpleError:
    value: str


@dataclass
class Integer:
    value: int
