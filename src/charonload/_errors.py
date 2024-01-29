from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover
    from ._compat.typing import Self


class JITCompileError(ABC, Exception):
    """Abstract base class for JIT compilation errors."""

    def __init__(self: Self, step_name: str = "", log: str | None = None) -> None:
        """
        Raise a JIT compilation error.

        Parameters
        ----------
        step_name
            The name of the failed compilation step.
        log
            The full log from the underlying compiler.
        """
        self.step_name = step_name
        """The name of the failed compilation step."""

        self.log = log
        """The full log from the underlying compiler."""

        super().__init__(f"{self.step_name} failed:\n\n{self.log}" if log is not None else f"{self.step_name} failed.")

    def __new__(cls: type[Self], *args: Any, **kwargs: Any) -> Self:  # noqa: ANN401, ARG003
        if cls is JITCompileError:
            msg = f"Cannot instantiate abstract class {cls.__name__}"
            raise TypeError(msg)
        return super().__new__(cls)


class CMakeConfigureError(JITCompileError):
    """Raised when the CMake configure step failed."""

    def __init__(self: Self, log: str | None = None) -> None:
        """
        Raise a CMake configure error.

        Parameters
        ----------
        log
            The full log from CMake.
        """
        super().__init__(step_name="CMake configure", log=log)


class BuildError(JITCompileError):
    """Raised when the build step failed."""

    def __init__(self: Self, log: str | None = None) -> None:
        """
        Raise a build error.

        Parameters
        ----------
        log
            The full log from the build tool.
        """
        super().__init__(step_name="Building", log=log)


class StubGenerationError(JITCompileError):
    """Raised when the stub generation step failed."""

    def __init__(self: Self, log: str | None = None) -> None:
        """
        Raise a stub generation error.

        Parameters
        ----------
        log
            The full log from pybind11-stubgen.
        """
        super().__init__(step_name="Stub generation", log=log)


class CommandNotFoundError(Exception):
    """Raised when the full path of a command could not be found on the disk."""

    def __init__(self: Self, command_name: str) -> None:
        """
        Raise a Command-Not-Found error.

        Parameters
        ----------
        command_name
            The name of the command.
        """
        self.command_name = command_name
        """The name of the command."""

        super().__init__(f'Cannot find executable "{command_name}".')


class _SerializerNotConnectedError(Exception):
    """Internal error that is raised when no suitable serializer has been connected for the persistent cache."""

    def __init__(self: Self, value_cls: type) -> None:
        """
        Raise a Serializer-Not-Connected error.

        Parameters
        ----------
        value_cls
            The class of the value to serialize.
        """
        self.value_cls = value_cls
        """The class of the value to serialize."""

        super().__init__(f'Internal error: Cannot find serializer for class "{value_cls}".')
