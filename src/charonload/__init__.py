"""
This package provides the functionality to automatically build and load C++/CUDA extensions developed with CMake and
PyTorch. A typical example on how to use this package is shown in the following:

.. code-block:: python

    # Add configuration somewhere at the top of the project
    import charonload

    charonload.module_config["my_cpp_cuda_ext"] = charonload.Config(
        # All paths must be absolute
        project_directory=pathlib.Path(__file__).parent / "<my_cpp_cuda_ext>",
        build_directory="optional/build/directory/for/caching",
    )

    # From now on, "my_cpp_cuda_ext" can be used in this module and any other imported module
    import my_cpp_cuda_ext
    # ...
"""

import sys

required_version = (3, 8)

if sys.version_info[:2] < required_version:  # pragma: no cover
    msg = "%s requires Python %d.%d+" % (__package__, *required_version)
    raise RuntimeError(msg)

del required_version
del sys

import email.utils
import importlib.metadata

from ._config import Config
from ._errors import (
    BuildError,
    CMakeConfigureError,
    CommandNotFoundError,
    JITCompileError,
    StubGenerationError,
)
from ._finder import JITCompileFinder, extension_finder, module_config
from ._version import _version

__author__ = ", ".join(
    [
        email.utils.parseaddr(author.strip())[0]
        for author in importlib.metadata.metadata(__package__)["Author-email"].split(",")
    ]
)
__version__ = _version()
__copyright__ = f"2024, {__author__}"

__all__ = [
    "BuildError",
    "CMakeConfigureError",
    "CommandNotFoundError",
    "Config",
    "extension_finder",
    "JITCompileError",
    "JITCompileFinder",
    "module_config",
    "StubGenerationError",
]
