from __future__ import annotations

import sys

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self


__all__ = ["Self"]
