from __future__ import annotations

import ctypes
import enum
import errno
import io
import os
import platform
import shutil
import subprocess
import sys
from abc import ABC, abstractmethod
from typing import IO, TYPE_CHECKING, Iterable, Iterator, Literal

import colorama

from ._errors import CommandNotFoundError

if TYPE_CHECKING:  # pragma: no cover
    from types import TracebackType

    from ._compat.typing import Self

colorama.just_fix_windows_console()


class _StepStatus(enum.Enum):
    SUCCESSFUL = enum.auto()
    FAILED = enum.auto()
    SKIPPED = enum.auto()


class _Process(ABC):
    @abstractmethod
    def __init__(
        self: Self,
        command_args: list[str],
        encoding: str,
    ) -> None:  # pragma: no cover
        pass

    @abstractmethod
    def __enter__(self: Self) -> Self:  # pragma: no cover
        pass

    @abstractmethod
    def __exit__(
        self: Self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> Literal[False]:  # pragma: no cover
        pass

    @property
    @abstractmethod
    def stdout(self: Self) -> IO[str]:  # pragma: no cover
        pass

    @property
    @abstractmethod
    def returncode(self: Self) -> int:  # pragma: no cover
        pass


class _UnixPtyProcess(_Process):
    class _SafeReadableIO(IO[str]):
        def __init__(self: Self, stream: IO[str]) -> None:
            self._stream = stream

        @property
        def mode(self: Self) -> str:
            return self._stream.mode

        @property
        def name(self: Self) -> str:
            return self._stream.name

        def close(self: Self) -> None:
            return self._stream.close()

        @property
        def closed(self: Self) -> bool:
            return self._stream.closed

        def fileno(self: Self) -> int:
            return self._stream.fileno()

        def flush(self: Self) -> None:
            return self._stream.flush()

        def isatty(self: Self) -> bool:
            return self._stream.isatty()

        def read(self: Self, n: int = -1) -> str:
            try:
                return self._stream.read(n)
            except OSError as e:
                if e.errno == errno.EIO:  # EIO also means EOF
                    return ""
                raise

        def readable(self: Self) -> bool:
            return self._stream.readable()

        def readline(self: Self, limit: int = -1) -> str:
            try:
                return self._stream.readline(limit)
            except OSError as e:
                if e.errno == errno.EIO:  # EIO also means EOF
                    return ""
                raise

        def readlines(self: Self, hint: int = -1) -> list[str]:
            try:
                return self._stream.readlines(hint)
            except OSError as e:
                if e.errno == errno.EIO:  # EIO also means EOF
                    return []
                raise

        def seek(self: Self, offset: int, whence: int = 0) -> int:
            return self._stream.seek(offset, whence)

        def seekable(self: Self) -> bool:
            return self._stream.seekable()

        def tell(self: Self) -> int:
            return self._stream.tell()

        def truncate(self: Self, size: int | None = None) -> int:
            return self._stream.truncate(size)

        def writable(self: Self) -> bool:
            return self._stream.writable()

        def write(self: Self, s: str) -> int:
            return self._stream.write(s)

        def writelines(self: Self, lines: Iterable[str]) -> None:
            return self._stream.writelines(lines)

        def __enter__(self: Self) -> IO[str]:
            return self._stream.__enter__()

        def __exit__(
            self: Self,
            exc_type: type[BaseException] | None,
            exc_value: BaseException | None,
            exc_tb: TracebackType | None,
        ) -> None:
            return self._stream.__exit__(exc_type, exc_value, exc_tb)

        def __iter__(self: Self) -> Iterator[str]:
            return self._stream.__iter__()

        def __next__(self: Self) -> str:
            return self._stream.__next__()

    def __init__(
        self: Self,
        command_args: list[str],
        encoding: str,
    ) -> None:
        self._m, self._s = os.openpty()
        self._p = subprocess.Popen(
            command_args,
            stdout=self._s,
            stderr=self._s,
        )
        # _s is now opened in both this process and _p. Reading from _m will block indefinitely unless *all* _s are
        # closed, so close ours first and wait until _p closes its own one. Reading from _m when both _s are closed
        # may cases a EIF error which should be caught.
        os.close(self._s)
        # This reopens _m, so manually closing before is not needed.
        self._stdout = _UnixPtyProcess._SafeReadableIO(os.fdopen(self._m, encoding=encoding))

    def __enter__(self: Self) -> Self:
        self._p.__enter__()  # Only returns p, so just call for completeness
        return self

    def __exit__(
        self: Self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> Literal[False]:
        self._p.__exit__(exc_type, exc_value, exc_tb)
        self._stdout.close()
        return False

    @property
    def stdout(self: Self) -> IO[str]:
        return self._stdout

    @property
    def returncode(self: Self) -> int:
        return self._p.returncode


class _PipedProcess(_Process):
    def __init__(
        self: Self,
        command_args: list[str],
        encoding: str,
    ) -> None:
        self._p = subprocess.Popen(
            command_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            encoding=encoding,
        )

    def __enter__(self: Self) -> Self:
        self._p.__enter__()  # Only returns p, so just call for completeness
        return self

    def __exit__(
        self: Self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> Literal[False]:
        self._p.__exit__(exc_type, exc_value, exc_tb)
        return False

    @property
    def stdout(self: Self) -> IO[str]:
        assert self._p.stdout is not None  # noqa: S101
        return self._p.stdout

    @property
    def returncode(self: Self) -> int:
        return self._p.returncode


def _process_cls(
    *,
    output_streams: list[IO[str]],
) -> type[_Process]:
    if platform.system() != "Windows" and all(o.isatty() for o in output_streams):
        return _UnixPtyProcess
    return _PipedProcess


def _run(
    *,
    command_args: list[str],
    verbose: bool = True,
) -> tuple[_StepStatus, str | None]:
    command_args = _find_full_command_path(command_args)

    if verbose:
        command = " ".join(command_args)
        print(  # noqa: T201
            f"[charonload] {colorama.Fore.GREEN}{colorama.Style.BRIGHT}Running: "
            f'{colorama.Style.NORMAL}"{command}"{colorama.Style.RESET_ALL}'
        )

    # Windows: Use windll instead of cdll call strategy since GetConsoleOutputCP is flagged with WINAPI/__stdcall
    encoding = "utf-8" if platform.system() != "Windows" else f"cp{ctypes.windll.kernel32.GetConsoleOutputCP()}"  # type: ignore[attr-defined]

    p_output = io.StringIO()
    output_streams: list[IO[str]] = [sys.stdout] if verbose else [p_output]

    with _process_cls(output_streams=output_streams)(command_args, encoding) as p:
        _incrementally_read_text_stream(
            input_stream=p.stdout,
            output_streams=output_streams,
        )

    return (
        _StepStatus.SUCCESSFUL if p.returncode == 0 else _StepStatus.FAILED,
        None if verbose else p_output.getvalue(),
    )


def _run_if(
    *,
    condition: bool,
    command_args: list[str],
    verbose: bool = True,
) -> tuple[_StepStatus, str | None]:
    return _run(command_args=command_args, verbose=verbose) if condition else (_StepStatus.SKIPPED, None)


def _find_full_command_path(command_args: list[str]) -> list[str]:
    full_command_path = shutil.which(command_args[0])
    if full_command_path is None:
        raise CommandNotFoundError(command_args[0])
    return [full_command_path, *command_args[1:]]


def _incrementally_read_text_stream(input_stream: IO[str], output_streams: list[IO[str]]) -> None:
    while output_line := input_stream.read(1):
        for o in output_streams:
            o.write(output_line)
            o.flush()
