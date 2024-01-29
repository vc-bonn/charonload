from __future__ import annotations

import charonload


def test_author() -> None:
    assert charonload.__author__


def test_version() -> None:
    assert charonload.__version__


def test_copyright() -> None:
    assert charonload.__copyright__
