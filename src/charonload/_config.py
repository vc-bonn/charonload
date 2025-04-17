from __future__ import annotations

import base64
import getpass
import hashlib
import os
import pathlib
import re
import site
import sys
import sysconfig
import tempfile
from collections import UserDict
from dataclasses import dataclass
from typing import TYPE_CHECKING

import colorama

if TYPE_CHECKING:  # pragma: no cover
    from ._compat.typing import Self

colorama.just_fix_windows_console()


@dataclass(init=False)  # Python 3.10+: Use "_: KW_ONLY"
class Config:
    """
    Set of user-specified configuration options for setting up the import logic of :class:`JITCompileFinder`.

    This will be resolved into :class:`ResolvedConfig` before usage.
    """

    project_directory: pathlib.Path | str
    """The absolute path to the root directory of the C++/CUDA extension containing the root ``CMakeLists.txt`` file."""

    build_directory: pathlib.Path | str | None
    """
    An optional absolute path to a build directory.

    If not specified, the build will be placed in the temporary directory of the operating system.
    """

    clean_build: bool
    """
    Whether to remove all cached files of previous builds from the build directory.

    This is useful to ensure consistent behavior after major changes in the CMake files of the project.

    .. admonition:: Overrides
      :class: important

      If the environment variable ``CHARONLOAD_FORCE_CLEAN_BUILD`` is set, it will replace this value in
      :class:`ResolvedConfig`.
    """

    build_type: str
    """The build type passed to CMake to compile the extension."""

    cmake_options: dict[str, str] | None
    """Additional CMake options to pass to the project when JIT compiling."""

    stubs_directory: pathlib.Path | str | None
    """
    An optional absolute path to the directory where stub files of the extension should be generated.

    This is useful for IDEs to get syntax highlighting and auto-completion for the extension content. For VS Code, the
    respective (default) directory to specify here is ``<project root directory>/typings``. Stub generation is disabled
    if set to ``None``.
    """

    stubs_invalid_ok: bool
    """
    Whether to accept invalid stubs and skip raising an error.

    .. admonition:: Overrides
      :class: important

      If the environment variable ``CHARONLOAD_FORCE_STUBS_INVALID_OK`` is set, it will replace this value in
      :class:`ResolvedConfig`.
    """

    verbose: bool
    """
    Whether to enable printing the full log of the JIT compilation.

    This is useful for debugging.

    .. admonition:: Overrides
      :class: important

      If the environment variable ``CHARONLOAD_FORCE_VERBOSE`` is set, it will replace this value in
      :class:`ResolvedConfig`.
    """

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
        self.project_directory = project_directory
        self.build_directory = build_directory
        self.clean_build = clean_build
        self.build_type = build_type
        self.cmake_options = cmake_options
        self.stubs_directory = stubs_directory
        self.stubs_invalid_ok = stubs_invalid_ok
        self.verbose = verbose


@dataclass(init=False)  # Python 3.10+: Use "kw_only=True"
class ResolvedConfig:
    """
    Set of resolved configuration options that is **actually used** in the import logic of :class:`JITCompileFinder`.

    This has been resolved from :class:`Config` and from the environment variables.
    """

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
        *,
        full_project_directory: pathlib.Path,
        full_build_directory: pathlib.Path,
        clean_build: bool,
        build_type: str,
        cmake_options: dict[str, str],
        full_stubs_directory: pathlib.Path | None,
        stubs_invalid_ok: bool,
        verbose: bool,
    ) -> None:
        self.full_project_directory = full_project_directory
        self.full_build_directory = full_build_directory
        self.clean_build = clean_build
        self.build_type = build_type
        self.cmake_options = cmake_options
        self.full_stubs_directory = full_stubs_directory
        self.stubs_invalid_ok = stubs_invalid_ok
        self.verbose = verbose


class ConfigDict(UserDict[str, ResolvedConfig]):
    """
    A configuration dictionary for holding resolved :class:`Config` instances.

    Configurations will be resolved during insertion into the dictionary.
    """

    def __setitem__(self: Self, key: str, value: Config | ResolvedConfig) -> None:
        """
        Resolve a user-specified configuration :class:`Config` into :class:`ResolvedConfig` and insert it.

        Parameters
        ----------
        key
            The associated key of the configuration.
        value
            A user-specified or already resolved configuration.

        Raises
        ------
        ValueError
            During resolution if:
            1) ``config.project_directory``, ``config.build_directory``, or ``config.stubs_directory`` are not
               absolute paths,
            2) ``config.project_directory`` does not exist, or
            3) ``config.cmake_options`` contains prohibited options.
        """
        super().__setitem__(
            key,
            self._resolve(key, value) if isinstance(value, Config) else value,
        )

    def _resolve(self: Self, module_name: str, config: Config) -> ResolvedConfig:
        if not pathlib.Path(config.project_directory).is_absolute():
            msg = f'Expected absolute project directory, but got relative directory "{config.project_directory}"'
            raise ValueError(msg)

        if not pathlib.Path(config.project_directory).resolve().exists():
            msg = f'Expected existing project directory, but got non-existing directory "{config.project_directory}"'
            raise ValueError(msg)

        if config.build_directory is not None and not pathlib.Path(config.build_directory).is_absolute():
            msg = f'Expected absolute build directory, but got relative directory "{config.build_directory}"'
            raise ValueError(msg)

        if config.stubs_directory is not None and not pathlib.Path(config.stubs_directory).is_absolute():
            msg = f'Expected absolute stub directory, but got relative directory "{config.stubs_directory}"'
            raise ValueError(msg)

        if config.cmake_options is not None:
            prohibited_cmake_options = {
                "CHARONLOAD_.*",
                "CMAKE_CONFIGURATION_TYPES",
                "CMAKE_PREFIX_PATH",
                "CMAKE_PROJECT_TOP_LEVEL_INCLUDES",
                "TORCH_EXTENSION_NAME",
            }

            for k in config.cmake_options:
                for pk in prohibited_cmake_options:
                    if re.search(pk, k) is not None:
                        msg = f'Found prohibited CMake option="{k}" which is not allowed or supported.'
                        raise ValueError(msg)

        return ResolvedConfig(
            full_project_directory=pathlib.Path(config.project_directory).resolve(),
            full_build_directory=self._find_build_directory(
                build_directory=config.build_directory,
                module_name=module_name,
                project_directory=config.project_directory,
                verbose=config.verbose,
            ),
            clean_build=self._str_to_bool(os.environ.get("CHARONLOAD_FORCE_CLEAN_BUILD", default=config.clean_build)),
            build_type=config.build_type,
            cmake_options=config.cmake_options if config.cmake_options is not None else {},
            full_stubs_directory=self._find_stubs_directory(
                stubs_directory=config.stubs_directory,
                verbose=config.verbose,
            ),
            stubs_invalid_ok=self._str_to_bool(
                os.environ.get("CHARONLOAD_FORCE_STUBS_INVALID_OK", default=config.stubs_invalid_ok)
            ),
            verbose=self._str_to_bool(os.environ.get("CHARONLOAD_FORCE_VERBOSE", default=config.verbose)),
        )

    def _str_to_bool(self: Self, s: str | bool) -> bool:
        if isinstance(s, bool):
            return s

        if s.lower() in ["1", "on", "yes", "true", "y"]:
            return True
        if s.lower() in ["0", "off", "no", "false", "n"]:
            return False

        msg = f'Cannot convert string "{s}" to bool'
        raise ValueError(msg)

    def _find_build_directory(
        self: Self,
        *,
        build_directory: pathlib.Path | str | None,
        module_name: str,
        project_directory: pathlib.Path | str,
        verbose: bool,
    ) -> pathlib.Path:
        # 1. Resolve user-specified path
        full_build_directory = pathlib.Path(build_directory).resolve() if build_directory is not None else None

        # 2. Filter user-specified path
        if (
            full_build_directory is not None
            and (filtered_directory := self._exclude_install_directories(full_build_directory)) != full_build_directory
        ):
            full_build_directory = filtered_directory
            if verbose:
                print(  # noqa: T201
                    f"{colorama.Fore.YELLOW}[charonload] User-specified config option points into Python package directories:{colorama.Style.RESET_ALL}\n"  # noqa: E501
                    f"{colorama.Fore.YELLOW}[charonload]{colorama.Style.RESET_ALL}\n"
                    f'{colorama.Fore.YELLOW}[charonload]     build_directory="{build_directory}"{colorama.Style.RESET_ALL}\n'  # noqa: E501
                    f"{colorama.Fore.YELLOW}[charonload]{colorama.Style.RESET_ALL}\n"
                    f"{colorama.Fore.YELLOW}[charonload] Overriding and retrying with:{colorama.Style.RESET_ALL}\n"
                    f"{colorama.Fore.YELLOW}[charonload]{colorama.Style.RESET_ALL}\n"
                    f"{colorama.Fore.YELLOW}[charonload]     build_directory=None{colorama.Style.RESET_ALL}\n"
                    f"{colorama.Fore.YELLOW}[charonload]{colorama.Style.RESET_ALL}"
                )

        # 3. Use fallback if needed
        if full_build_directory is None:
            full_project_directory = pathlib.Path(project_directory).resolve()

            hash_length = 6  # Every 3 bytes will be encoded into 4 base64 characters
            hasher = hashlib.sha256()
            hasher.update(bytes(full_project_directory))
            hasher.update(bytes(pathlib.Path(sys.executable)))
            path_hash = base64.urlsafe_b64encode(hasher.digest()[:hash_length]).decode("ascii")

            full_build_directory = (
                pathlib.Path(tempfile.gettempdir())
                / f"charonload-of-{getpass.getuser()}"
                / f"{module_name}_build_{path_hash}"
            )

        return full_build_directory

    def _find_stubs_directory(
        self: Self,
        *,
        stubs_directory: pathlib.Path | str | None,
        verbose: bool,
    ) -> pathlib.Path | None:
        # 1. Resolve user-specified path
        full_stubs_directory = pathlib.Path(stubs_directory).resolve() if stubs_directory is not None else None

        # 2. Filter user-specified path
        if (
            full_stubs_directory is not None
            and (filtered_directory := self._exclude_install_directories(full_stubs_directory)) != full_stubs_directory
        ):
            full_stubs_directory = filtered_directory
            if verbose:
                print(  # noqa: T201
                    f"{colorama.Fore.YELLOW}[charonload] User-specified config option points into Python package directories:{colorama.Style.RESET_ALL}\n"  # noqa: E501
                    f"{colorama.Fore.YELLOW}[charonload]{colorama.Style.RESET_ALL}\n"
                    f'{colorama.Fore.YELLOW}[charonload]     stubs_directory="{stubs_directory}"{colorama.Style.RESET_ALL}\n'  # noqa: E501
                    f"{colorama.Fore.YELLOW}[charonload]{colorama.Style.RESET_ALL}\n"
                    f"{colorama.Fore.YELLOW}[charonload] Overriding and retrying with:{colorama.Style.RESET_ALL}\n"
                    f"{colorama.Fore.YELLOW}[charonload]{colorama.Style.RESET_ALL}\n"
                    f"{colorama.Fore.YELLOW}[charonload]     stubs_directory=None{colorama.Style.RESET_ALL}\n"
                    f"{colorama.Fore.YELLOW}[charonload]{colorama.Style.RESET_ALL}"
                )

        return full_stubs_directory

    def _exclude_install_directories(self: Self, directory: pathlib.Path) -> pathlib.Path | None:
        install_directories = [site.getuserbase()] if site.ENABLE_USER_SITE else []
        install_directories.extend(sysconfig.get_paths().values())
        install_directories = list(set(install_directories))  # Remove duplicates

        return (
            directory
            if not any(
                full_d for d in install_directories if (full_d := pathlib.Path(d).resolve()) in directory.parents
            )
            else None
        )
