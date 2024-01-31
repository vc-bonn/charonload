from __future__ import annotations

import ctypes
import enum
import io
import platform
import shutil
import subprocess
import sys
from typing import IO

import colorama

from ._errors import CommandNotFoundError

colorama.just_fix_windows_console()


class _StepStatus(enum.Enum):
    SUCCESSFUL = enum.auto()
    FAILED = enum.auto()
    SKIPPED = enum.auto()


def _run(
    *,
    command_args: list[str],
    verbose: bool = True,
) -> tuple[_StepStatus, str | None]:
    command_args = _find_full_command_path(command_args)

    if verbose:
        command = " ".join(command_args)
        print(  # noqa: T201
            f"{colorama.Fore.GREEN}{colorama.Style.BRIGHT}Running: "
            f'{colorama.Style.NORMAL}"{command}"{colorama.Style.RESET_ALL}'
        )
        print(f"{colorama.Style.BRIGHT}", end="")  # noqa: T201

    # Windows: Use windll instead of cdll call strategy since GetConsoleOutputCP is flagged with WINAPI/__stdcall
    encoding = "utf-8" if platform.system() != "Windows" else f"cp{ctypes.windll.kernel32.GetConsoleOutputCP()}"  # type: ignore[attr-defined]

    with subprocess.Popen(
        command_args,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        encoding=encoding,
    ) as p:
        assert p.stdout is not None  # noqa: S101

        p_output = io.StringIO()
        _incrementally_read_text_stream(
            input_stream=p.stdout,
            output_streams=[sys.stdout] if verbose else [p_output],
        )

    if verbose:
        print(f"{colorama.Style.RESET_ALL}", end="")  # noqa: T201

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
