from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:  # pragma: no cover
    from charonload._compat.typing import Self

import charonload


def test_abstract_jit_compile_error() -> None:
    with pytest.raises(TypeError) as exc_info:
        raise charonload.JITCompileError

    assert exc_info.type is TypeError


class DerivedError(charonload.JITCompileError):
    def __init__(self: Self, step_name: str = "", log: str | None = None) -> None:
        super().__init__(step_name=step_name, log=log)


def test_derived_error() -> None:
    step_name = "Test"
    log = "Some log"
    with pytest.raises(charonload.JITCompileError) as exc_info:
        raise DerivedError(step_name, log=log)

    assert exc_info.type is DerivedError
