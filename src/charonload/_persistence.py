from __future__ import annotations

import collections.abc
import inspect
import operator
import pathlib
import sys
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable

from ._errors import _SerializerNotConnectedError

if TYPE_CHECKING:  # pragma: no cover
    import enum

    from ._compat.typing import Self


class _PersistentString:
    def __init__(self: Self, path: pathlib.Path | str) -> None:
        self._path = pathlib.Path(path).resolve()

    @property
    def value(self: Self) -> str | None:
        if self.path.exists():
            with self.path.open("r") as f:
                return f.read()
        return None

    @value.setter
    def value(self: Self, value: str | None) -> None:
        if value is None:
            self.path.unlink(missing_ok=True)
        else:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("w") as f:
                f.write(value)

    @property
    def path(self: Self) -> pathlib.Path:
        return self._path


@dataclass
class _TypedPersistentString:
    value_cls: type
    stored: _PersistentString


@dataclass
class _Serializer:
    encode: Callable[[Any], str]
    decode: Callable[[str], Any]


class _PersistentDict(collections.abc.MutableMapping):
    def __init__(self: Self) -> None:
        self._entries: dict[str, _TypedPersistentString] = {}
        self._serializers: dict[type, _Serializer] = {}

    def __setitem__(self: Self, key: str, value: Any) -> None:  # noqa: ANN401
        if not isinstance(value, self._entries[key].value_cls):
            msg = f'Expected value of type "{self._entries[key].value_cls.__name__}" but is "{type(value).__name__}".'
            raise TypeError(msg)

        self._entries[key].stored.value = self._dispatch_serializer(self._entries[key].value_cls).encode(value)

    def __getitem__(self: Self, key: str) -> Any:  # noqa: ANN401
        if (value := self._entries[key].stored.value) is not None:
            return self._dispatch_serializer(self._entries[key].value_cls).decode(value)

        msg = f'Persistent value for "{key}" in "{self._entries[key].stored.path}" does not exist.'
        raise KeyError(msg)

    def __delitem__(self: Self, key: str) -> None:
        msg = "Deleting connections is not supported."
        raise AttributeError(msg)

    def __iter__(self: Self) -> collections.abc.Iterator:
        return iter(self._entries)

    def __len__(self: Self) -> int:
        return len(self._entries)

    def connect(self: Self, key: str, value_cls: type, file: pathlib.Path | str) -> None:
        self._entries[key] = _TypedPersistentString(value_cls, _PersistentString(file))

    def register_serializer(
        self: Self, value_cls: type, *, encode: Callable[[Any], str], decode: Callable[[str], Any]
    ) -> None:
        self._serializers[value_cls] = _Serializer(encode, decode)

    def _dispatch_serializer(self: Self, value_cls: type) -> _Serializer:
        types = inspect.getmro(value_cls)
        dispatched_types = [t for t in types if t in self._serializers]

        if len(dispatched_types) == 0:
            raise _SerializerNotConnectedError(value_cls)

        return self._serializers[dispatched_types[0]]


class _StrSerializer:
    @staticmethod
    def encode(value: str) -> str:
        return value

    @staticmethod
    def decode(value: str) -> str:
        return value


class _EnumSerializer:
    @staticmethod
    def encode(value: enum.Enum) -> str:
        return f"{type(value).__module__}.{type(value).__qualname__}.{value.name}"

    @staticmethod
    def decode(value: str) -> enum.Enum:
        cls, name = value.rsplit(".", 1)
        toplevel_module = value.split(".", 1)[0]
        cls_in_toplevel = cls.split(".", 1)[1]

        enum_cls = operator.attrgetter(cls_in_toplevel)(sys.modules[toplevel_module])

        return enum_cls[name]  # type: ignore[no-any-return]


class _PathSerializer:
    @staticmethod
    def encode(value: pathlib.Path) -> str:
        return str(value)

    @staticmethod
    def decode(value: str) -> pathlib.Path:
        return pathlib.Path(value).resolve()
