from __future__ import annotations

import base64
import getpass
import hashlib
import pathlib
import re
import sys
import tempfile
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from ._compat.typing import Self


@dataclass(init=False)
class Config:
    """The set of configuration options required for the import logic of the :class:`JITCompileFinder`."""

    full_project_directory: pathlib.Path
    """The full absolute path to the project directory."""

    full_build_directory: pathlib.Path
    """The full absolute path to the build directory."""

    clean_build: bool
    """Flag to enable removing cached files from previous builds before building."""

    build_type: str
    """The build type passed to CMake."""

    cmake_options: dict[str, str]
    """Additional options passed to CMake."""

    full_stubs_directory: pathlib.Path | None
    """The full absolute path to the stubs directory, or ``None`` if no stubs should be generated."""

    stubs_invalid_ok: bool
    """Flag to accept invalid stubs."""

    verbose: bool
    """Flag to enable printing the full log of the JIT compilation."""

    def __init__(
        self: Self,
        project_directory: pathlib.Path | str,
        build_directory: pathlib.Path | str | None = None,
        *,
        clean_build: bool = False,
        build_type: str = "RelWithDebInfo",
        cmake_options: dict[str, str] | None = None,
        stubs_directory: pathlib.Path | str | None = None,
        stubs_invalid_ok: bool = False,
        verbose: bool = False,
    ) -> None:
        """
        Create the configuration options from the provided parameters.

        Parameters
        ----------
        project_directory
            The absolute path to the root directory of the C++/CUDA extension containing the root ``CMakeLists.txt``
            file.
        build_directory
            An optional absolute path to a build directory. If not specified, the build will be placed in the
            temporary directory of the operating system.
        clean_build
            Whether to remove all cached files of previous builds from the build directory. This is useful to ensure
            consistent behavior after major changes in the CMake files of the project.
        build_type
            The build type passed to CMake to compile the extension.
        cmake_options
            Additional CMake options to pass to the project when JIT compiling.
        stubs_directory
            An optional absolute path to the directory where stub files of the extension should be generated. This is
            useful for IDEs to get syntax highlighting and auto-completion for the extension content. For VS Code, the
            respective (default) directory to specify here is ``<project root directory>/typings``. Stub generation is
            disabled if set to ``None``.
        stubs_invalid_ok
            Whether to accept invalid stubs and skip raising an error.
        verbose
            Whether to enable printing the full log of the JIT compilation. This is useful for debugging.

        Raises
        ------
        ValueError
            If either:
            1) ``project_directory``,``build_directory``, or ``stubs_directory`` are not absolute paths,
            2) ``project_directory`` does not exists, or
            3) Prohibited options are inserted into ``cmake_options``.
        """
        if not pathlib.Path(project_directory).is_absolute():
            msg = f'Expected absolute project directory, but got relative directory "{project_directory}"'
            raise ValueError(msg)

        if not pathlib.Path(project_directory).resolve().exists():
            msg = f'Expected existing project directory, but got non-existing directory "{project_directory}"'
            raise ValueError(msg)

        if build_directory is not None and not pathlib.Path(build_directory).is_absolute():
            msg = f'Expected absolute build directory, but got relative directory "{build_directory}"'
            raise ValueError(msg)

        if stubs_directory is not None and not pathlib.Path(stubs_directory).is_absolute():
            msg = f'Expected absolute stub directory, but got relative directory "{stubs_directory}"'
            raise ValueError(msg)

        if cmake_options is not None:
            prohibited_cmake_options = {
                "CHARONLOAD_.*",
                "CMAKE_CONFIGURATION_TYPES",
                "CMAKE_PREFIX_PATH",
                "CMAKE_PROJECT_TOP_LEVEL_INCLUDES",
                "TORCH_EXTENSION_NAME",
            }

            for k in cmake_options:
                for pk in prohibited_cmake_options:
                    if re.search(pk, k) is not None:
                        msg = f'Found prohibited CMake option="{k}" which is not allowed or supported.'
                        raise ValueError(msg)

        self.full_project_directory = pathlib.Path(project_directory).resolve()
        self.full_build_directory = self._find_build_directory(project_directory, build_directory)
        self.clean_build = clean_build
        self.build_type = build_type
        self.cmake_options = cmake_options if cmake_options is not None else {}
        self.full_stubs_directory = self._find_stubs_directory(stubs_directory)
        self.stubs_invalid_ok = stubs_invalid_ok
        self.verbose = verbose

    def _find_build_directory(
        self: Self,
        project_directory: pathlib.Path | str,
        build_directory: pathlib.Path | str | None,
    ) -> pathlib.Path:
        if build_directory is not None:
            full_build_directory = pathlib.Path(build_directory).resolve()
        else:
            full_project_directory = pathlib.Path(project_directory).resolve()

            hash_length = 6  # Every 3 bytes will be encoded into 4 base64 characters
            hasher = hashlib.sha256()
            hasher.update(bytes(full_project_directory))
            hasher.update(bytes(pathlib.Path(sys.executable)))
            path_hash = base64.urlsafe_b64encode(hasher.digest()[:hash_length]).decode("ascii")

            full_build_directory = (
                pathlib.Path(tempfile.gettempdir())
                / f"charonload-of-{getpass.getuser()}"
                / f"{full_project_directory.name}_build_{path_hash}"
            )

        return full_build_directory

    def _find_stubs_directory(
        self: Self,
        stubs_directory: pathlib.Path | str | None,
    ) -> pathlib.Path | None:
        return pathlib.Path(stubs_directory).resolve() if stubs_directory is not None else None
