from __future__ import annotations

import sys

if sys.version_info < (3, 11):
    from tomli import *  # noqa: F403
else:
    from tomllib import *  # noqa: F403
