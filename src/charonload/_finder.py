from __future__ import annotations

import enum
import importlib.abc
import multiprocessing
import os
import pathlib
import platform
import sys
import time
import warnings
import weakref
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

import colorama
import filelock

from ._compat import hashlib

if TYPE_CHECKING:  # pragma: no cover
    from typing import Any, SupportsIndex

    from ._compat.typing import Self

from ._config import Config
from ._errors import BuildError, CMakeConfigureError, StubGenerationError
from ._persistence import (
    _EnumSerializer,
    _PathSerializer,
    _PersistentDict,
    _StrSerializer,
)
from ._runner import _run, _run_if, _StepStatus
from ._version import _is_compatible, _version

colorama.just_fix_windows_console()


class JITCompileFinder(importlib.abc.MetaPathFinder):
    """An import finder for executing the just-in-time (JIT) compilation."""

    def find_spec(self: Self, fullname, path, target=None) -> None:  # noqa: ANN001, ARG002
        """
        Find the spec of the specified module.

        In particular, the following steps will be internally executed:

        - If a :class:`Config` instance has been registered in :data:`module_config` for ``fullname``:
            - JIT compile the extension following the stored configuration.
            - Make the compiled extension loaded by Python's built-in importers.
        - Otherwise:
            - Fall back to Python's built-in importers.

        Parameters
        ----------
        fullname
            The name of the module. This will be automatically be specific by Python's import system.

        path
            The path of the module or ``None``. This will be automatically be specific by Python's import system.

        target
            A module object. This will be automatically be specific by Python's import system.

        Returns
        -------
        NoneType
            ``None``. This defers the actual import to the built-in Python finders and loaders.
        """
        if fullname in module_config:
            print(  # noqa: T201
                f"[charonload] Building module {colorama.Style.BRIGHT}'{fullname}'{colorama.Style.RESET_ALL} ..."
            )
            t_start = time.perf_counter()
            _load(module_name=fullname, config=module_config[fullname])
            t_end = time.perf_counter()
            print(  # noqa: T201
                f"[charonload] Building module {colorama.Style.BRIGHT}'{fullname}'{colorama.Style.RESET_ALL} ... done. "
                f"({t_end - t_start:.1f}s)"
            )

            if "torch" not in sys.modules:
                msg = (
                    "\n"
                    f"{colorama.Fore.YELLOW}[charonload] PyTorch seems to be not imported yet. Calling functions from '{fullname}', which internally use Torch on the C++ side, may lead to unexpected behavior.{colorama.Style.RESET_ALL}\n"  # noqa: E501
                    f"{colorama.Fore.YELLOW}[charonload] Make sure to import PyTorch beforehand:{colorama.Style.RESET_ALL}\n"  # noqa: E501
                    f"{colorama.Fore.YELLOW}[charonload]{colorama.Style.RESET_ALL}\n"
                    f"{colorama.Fore.YELLOW}[charonload]     import torch{colorama.Style.RESET_ALL}\n"
                    f"{colorama.Fore.YELLOW}[charonload]{colorama.Style.RESET_ALL}"
                )
                warnings.warn(msg, stacklevel=2)

        return None  # noqa: PLR1711, RET501


def _load(module_name: str, config: Config) -> None:
    if not isinstance(config, Config):
        msg = f"Invalid type of configuration: expected 'Config', but got '{config.__class__.__name__}'"
        raise TypeError(msg)

    (config.full_build_directory / "charonload").mkdir(parents=True, exist_ok=True)
    lock = filelock.FileLock(config.full_build_directory / "charonload" / "build.lock")
    if config.verbose:
        print(f"[charonload] Acquiring lock (pid={multiprocessing.current_process().pid}) ...")  # noqa: T201
    with lock:
        if config.verbose:
            print(f"[charonload] Acquiring lock (pid={multiprocessing.current_process().pid}) ... done.")  # noqa: T201

        step_classes: list[type[_JITCompileStep]] = [
            _CleanStep,
            _InitializeStep,
            _CMakeConfigureStep,
            _BuildStep,
            _StubGenerationStep,
            _ImportPathStep,
        ]
        steps = [cls(module_name, config, (i + 1, len(step_classes))) for i, cls in enumerate(step_classes)]
        for s in steps:
            s.run()


class _JITCompileStep(ABC):
    exception_cls = type(None)
    step_name = "<None>"

    def __init__(self: Self, module_name: str, config: Config, step_number: tuple[int, int]) -> None:
        self.module_name = module_name
        self.config = config
        self.step_number = step_number

        self.cache = _PersistentDict()
        self.cache.register_serializer(pathlib.Path, encode=_PathSerializer.encode, decode=_PathSerializer.decode)
        self.cache.register_serializer(enum.Enum, encode=_EnumSerializer.encode, decode=_EnumSerializer.decode)
        self.cache.register_serializer(str, encode=_StrSerializer.encode, decode=_StrSerializer.decode)

    def run(self: Self) -> None:
        if self.config.verbose:
            print(  # noqa: T201
                f"[charonload] {colorama.Fore.CYAN}[{self.step_number[0]}/{self.step_number[1]}]"
                f" {colorama.Style.BRIGHT}{self.step_name}{colorama.Style.RESET_ALL}"
            )
        self._run_impl()

    @abstractmethod  # pragma: no cover
    def _run_impl(self: Self) -> None:
        pass


class _CleanStep(_JITCompileStep):
    exception_cls = type(None)
    step_name = "Clean"

    def __init__(self: Self, module_name: str, config: Config, step_number: tuple[int, int]) -> None:
        super().__init__(module_name, config, step_number)
        self.cache.connect(
            "status_cmake_configure",
            _StepStatus,
            self.config.full_build_directory / "charonload" / "status_cmake_configure.txt",
        )
        self.cache.connect(
            "status_build",
            _StepStatus,
            self.config.full_build_directory / "charonload" / "status_build.txt",
        )
        self.cache.connect(
            "status_stub_generation",
            _StepStatus,
            self.config.full_build_directory / "charonload" / "status_stub_generation.txt",
        )
        self.cache.connect(
            "version",
            str,
            self.config.full_build_directory / "charonload" / "version.txt",
        )

    def _run_impl(self: Self) -> None:
        clean_if_failed = {
            "status_cmake_configure": True,
            "status_build": False,
            "status_stub_generation": False,
        }
        step_failed = {
            step: bool(self.cache.get(step, _StepStatus.SKIPPED) == _StepStatus.FAILED) for step in clean_if_failed
        }
        should_clean = [clean_if_failed[step] and failed for step, failed in step_failed.items()]

        if (
            self.config.clean_build
            or not _is_compatible(self.cache.get("version", _version()), _version())
            or any(should_clean)
        ):
            number_removed_files = 0
            number_removed_directories = 0

            for file in sorted(self.config.full_build_directory.rglob("*"), reverse=True):
                if any(file.samefile(f) for f in [self.config.full_build_directory / "charonload" / "build.lock"]):
                    continue

                if file.is_file():
                    file.unlink()
                    number_removed_files += 1
                elif file.is_dir() and not any(file.iterdir()):
                    file.rmdir()
                    number_removed_directories += 1

            if self.config.verbose and (number_removed_files > 0 or number_removed_directories > 0):
                print(  # noqa: T201
                    f"[charonload] {colorama.Fore.GREEN}{colorama.Style.BRIGHT}Removed:{colorama.Style.NORMAL} "
                    f"{number_removed_files} files, {number_removed_directories} directories{colorama.Style.RESET_ALL}"
                )


class _InitializeStep(_JITCompileStep):
    exception_cls = type(None)
    step_name = "Initialize"

    def __init__(self: Self, module_name: str, config: Config, step_number: tuple[int, int]) -> None:
        super().__init__(module_name, config, step_number)
        self.cache.connect(
            "version",
            str,
            self.config.full_build_directory / "charonload" / "version.txt",
        )

    def _run_impl(self: Self) -> None:
        self.cache["version"] = _version()

        with (self.config.full_build_directory / ".gitignore").open("w") as f:
            f.write("*")


class _CMakeConfigureStep(_JITCompileStep):
    exception_cls = CMakeConfigureError
    step_name = "CMake Configure"

    def __init__(self: Self, module_name: str, config: Config, step_number: tuple[int, int]) -> None:
        super().__init__(module_name, config, step_number)
        self.cache.connect(
            "status_cmake_configure",
            _StepStatus,
            self.config.full_build_directory / "charonload" / "status_cmake_configure.txt",
        )
        self.cache.connect(
            "cmake_configure_command",
            str,
            self.config.full_build_directory / "charonload" / "cmake_configure_command.txt",
        )

    def _run_impl(self: Self) -> None:
        configure_command_args = [
            "cmake",
            f"-DCMAKE_CONFIGURATION_TYPES={self.config.build_type}",
            f"-DCMAKE_PREFIX_PATH={self._cmake_prefix_paths()}",
            f"-DCMAKE_PROJECT_TOP_LEVEL_INCLUDES={self._cmake_project_top_level_includes()}",
            "-DCHARONLOAD_JIT_COMPILE=ON",
            f"-DCHARONLOAD_PYTHON_EXECUTABLE={pathlib.Path(sys.executable).as_posix()}",
            f"-DTORCH_EXTENSION_NAME={self.module_name}",
            *[f"-D{k}={v}" for k, v in self.config.cmake_options.items()],
            *self._cmake_generator(),
            "-S",
            self.config.full_project_directory.as_posix(),
            "-B",
            self.config.full_build_directory.as_posix(),
        ]
        configure_command = " ".join(configure_command_args)

        status, log = _run_if(
            condition=(
                self.cache.get("status_cmake_configure", _StepStatus.SKIPPED) == _StepStatus.FAILED
                or self.cache.get("cmake_configure_command", "") != configure_command
            ),
            command_args=configure_command_args,
            verbose=self.config.verbose,
        )

        self.cache["cmake_configure_command"] = configure_command
        self.cache["status_cmake_configure"] = status
        if status == _StepStatus.FAILED:
            raise self.exception_cls(log)

    def _cmake_generator(self: Self) -> list[str]:
        return ["-G", "Ninja Multi-Config"] if platform.system() != "Windows" else []

    def _cmake_prefix_paths(self: Self) -> str:
        return pathlib.Path(__file__).parent.as_posix()

    def _cmake_project_top_level_includes(self: Self) -> str:
        return (pathlib.Path(__file__).parent / "cmake" / "detect_configure_failure.cmake").as_posix()


class _BuildStep(_JITCompileStep):
    exception_cls = BuildError
    step_name = "Build"

    def __init__(self: Self, module_name: str, config: Config, step_number: tuple[int, int]) -> None:
        super().__init__(module_name, config, step_number)
        self.cache.connect(
            "status_cmake_configure",
            _StepStatus,
            self.config.full_build_directory / "charonload" / "status_cmake_configure.txt",
        )
        self.cache.connect(
            "status_build",
            _StepStatus,
            self.config.full_build_directory / "charonload" / "status_build.txt",
        )

    def _run_impl(self: Self) -> None:
        cmake_configure_passed_file = self.config.full_build_directory / "charonload" / "cmake_configure_passed.txt"

        status, log = _run(
            command_args=[
                "cmake",
                "--build",
                self.config.full_build_directory.as_posix(),
                "--config",
                str(self.config.build_type),
                "--parallel",
            ],
            verbose=self.config.verbose,
        )

        if status == _StepStatus.FAILED and not cmake_configure_passed_file.exists():
            self.cache["status_cmake_configure"] = status
            raise CMakeConfigureError(log)

        self.cache["status_build"] = status
        if status == _StepStatus.FAILED:
            raise self.exception_cls(log)


class _StubGenerationStep(_JITCompileStep):
    exception_cls = StubGenerationError
    step_name = "Stub Generation"

    def __init__(self: Self, module_name: str, config: Config, step_number: tuple[int, int]) -> None:
        super().__init__(module_name, config, step_number)
        self.cache.connect(
            "status_stub_generation",
            _StepStatus,
            self.config.full_build_directory / "charonload" / "status_stub_generation.txt",
        )
        self.cache.connect(
            "checksum",
            str,
            self.config.full_build_directory / "charonload" / self.config.build_type / "checksum.txt",
        )
        self.cache.connect(
            "location",
            pathlib.Path,
            self.config.full_build_directory / "charonload" / self.config.build_type / "location.txt",
        )
        self.cache.connect(
            "windows_dll_directories",
            str,
            self.config.full_build_directory / "charonload" / self.config.build_type / "windows_dll_directories.txt",
        )

    def _run_impl(self: Self) -> None:
        full_extension_path: pathlib.Path = self.cache["location"]
        old_checksum: str = self.cache.get("checksum", "")
        new_checksum = self._compute_checksum(full_extension_path)

        status, log = _run_if(
            condition=(
                self.config.full_stubs_directory is not None
                and (
                    self.cache.get("status_stub_generation", _StepStatus.SKIPPED) == _StepStatus.FAILED
                    or new_checksum != old_checksum
                    or not (self.config.full_stubs_directory / self.module_name).exists()
                )
            ),
            command_args=[
                sys.executable,
                (pathlib.Path(__file__).parent / "pybind11_stubgen").as_posix(),
                "--extension-path",
                full_extension_path.as_posix(),
                *self._windows_dll_directories(),
                "--print-invalid-expressions-as-is",
                *self._ignore_invalid(),
                "--exit-code",
                "-o",
                self.config.full_stubs_directory.as_posix() if self.config.full_stubs_directory is not None else "",
                self.module_name,
            ],
            verbose=self.config.verbose,
        )

        self.cache["checksum"] = new_checksum
        self.cache["status_stub_generation"] = status
        if status == _StepStatus.FAILED:
            raise self.exception_cls(log)

    def _windows_dll_directories(self: Self) -> list[str]:
        windows_dll_directories: str = self.cache["windows_dll_directories"]
        return ["--windows-dll-directories", windows_dll_directories] if windows_dll_directories else []

    def _ignore_invalid(self: Self) -> list[str]:
        return ["--ignore-all-errors"] if self.config.stubs_invalid_ok else []

    def _compute_checksum(self: Self, full_extension_path: pathlib.Path) -> str:
        with full_extension_path.open("rb") as f:
            digest = hashlib.file_digest(f, "sha256")
            return digest.hexdigest()


class _ImportPathStep(_JITCompileStep):
    exception_cls = type(None)
    step_name = "Import Path"

    def __init__(self: Self, module_name: str, config: Config, step_number: tuple[int, int]) -> None:
        super().__init__(module_name, config, step_number)
        self.cache.connect(
            "location",
            pathlib.Path,
            self.config.full_build_directory / "charonload" / self.config.build_type / "location.txt",
        )
        self.cache.connect(
            "windows_dll_directories",
            str,
            self.config.full_build_directory / "charonload" / self.config.build_type / "windows_dll_directories.txt",
        )

    def _run_impl(self: Self) -> None:
        full_extension_path: pathlib.Path = self.cache["location"]
        windows_dll_directories: str = self.cache["windows_dll_directories"]

        full_extension_directory = str(full_extension_path.parent)
        if full_extension_directory not in sys.path:
            sys.path.append(full_extension_directory)

        if platform.system() == "Windows":  # pragma: no cover
            number_added_paths = 0

            dll_directory_list = windows_dll_directories.split(";")
            for d_str in dll_directory_list:
                d = pathlib.Path(d_str)
                if d.exists() and d.is_absolute() and d.is_dir():
                    _windows_dll_directories_guard.add(d)
                    number_added_paths += 1

            if self.config.verbose and number_added_paths > 0:
                print(  # noqa: T201
                    f"[charonload] {colorama.Fore.GREEN}{colorama.Style.BRIGHT}Added:{colorama.Style.NORMAL} "
                    f"{number_added_paths} DLL paths (Windows only){colorama.Style.RESET_ALL}"
                )


module_config: dict[str, Config] = {}
"""
The dictionary storing the registered :class:`Config <charonload._config.Config>` instances.

Insert all C++/CUDA extension configurations into this dictionary to make the extensions importable.
"""

extension_finder: JITCompileFinder = JITCompileFinder()
"""
The :class:`JITCompileFinder` instance responsible for JIT compiling and loading the extensions upon import.

This instance will be automatically inserted at the start of the ``sys.meta_path`` list to take precedence over
Python's built-in finders.
"""


class _SysMetaPathFinderGuard:
    def __init__(self: Self, finder: importlib.abc.MetaPathFinder, *, insert_at: SupportsIndex) -> None:
        self.finder = finder

        _SysMetaPathFinderGuard._insert(insert_at, self.finder)
        self._finalizer = weakref.finalize(self, _SysMetaPathFinderGuard._remove, self.finder)

    @staticmethod
    def _insert(insert_at: SupportsIndex, finder: importlib.abc.MetaPathFinder) -> None:
        sys.meta_path.insert(insert_at, finder)

    @staticmethod
    def _remove(finder: importlib.abc.MetaPathFinder) -> None:
        sys.meta_path.remove(finder)


_extension_finder_guard = _SysMetaPathFinderGuard(extension_finder, insert_at=0)


class _OsAddDllDirectoryGuard:
    def __init__(self: Self, directories: dict[pathlib.Path, Any]) -> None:
        self.directories = directories

        self._finalizer = weakref.finalize(self, _OsAddDllDirectoryGuard._clear, self.directories)

    def add(self: Self, d: pathlib.Path) -> None:
        if d not in self.directories:
            handler = os.add_dll_directory(d)  # type: ignore[attr-defined]
            self.directories[d] = handler

    @staticmethod
    def _clear(directories: dict[pathlib.Path, Any]) -> None:
        for handler in directories.values():
            handler.close()  # type: ignore[attr-defined]


_windows_dll_directories: dict[pathlib.Path, Any] = {}

_windows_dll_directories_guard = _OsAddDllDirectoryGuard(_windows_dll_directories)
