from __future__ import annotations

import importlib.metadata
from typing import Tuple, cast


def _version() -> str:
    return importlib.metadata.version(__package__)


def _is_compatible(ver1: str, ver2: str) -> bool:
    return _same_minor_version(_str_to_tuple(ver1), _str_to_tuple(ver2))


def _str_to_tuple(ver: str) -> tuple[int, int, int]:
    components = list(map(int, ver.split(".")))
    components = [*components, 0, 0][:3]
    return cast(Tuple[int, int, int], tuple(components))  # typing.Tuple required for Python 3.8


def _same_minor_version(ver1: tuple[int, int, int], ver2: tuple[int, int, int]) -> bool:
    return ver1[0] == ver2[0] and ver1[1] == ver2[1]
