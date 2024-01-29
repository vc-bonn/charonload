from __future__ import annotations

import sys
from hashlib import *  # noqa: F403
from typing import TYPE_CHECKING, BinaryIO, Callable

if TYPE_CHECKING:
    from hashlib import _Hash


__all__ = ["file_digest"]


if sys.version_info < (3, 11):

    def file_digest(fileobj: BinaryIO, digest: str | Callable[[], _Hash], /) -> _Hash:
        if isinstance(digest, str):
            file_hasher = new(digest)  # noqa: F405
        elif callable(digest):
            file_hasher = digest()
        else:
            msg = "Wrong type of digest: Should be either str or Callable."
            raise TypeError(msg)

        num_blocks = 1024
        while chunk := fileobj.read(num_blocks * file_hasher.block_size):
            file_hasher.update(chunk)

        return file_hasher
