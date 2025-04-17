from __future__ import annotations

import multiprocessing
import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pathlib

import pytest

import charonload


def _true_values() -> list[str]:
    return ["1", "on", "On", "ON", "true", "TrUe", "True", "yes", "Yes", "YES", "y", "Y"]


def _false_values() -> list[str]:
    return ["0", "off", "Off", "OFF", "false", "FaLsE", "False", "no", "No", "NO", "n", "N"]


def _error_values() -> list[str]:
    return ["OOPS", "42", "f"]


def test_provided_build_directory(shared_datadir: pathlib.Path, tmp_path: pathlib.Path) -> None:
    project_directory = shared_datadir / "torch_cpu"
    build_directory = tmp_path / "build"
    assert not build_directory.exists()

    module_config = charonload.ConfigDict()
    module_config["test"] = charonload.Config(
        project_directory,
        build_directory,
    )
    config = module_config["test"]

    config.full_build_directory.mkdir(parents=True)

    assert config.full_build_directory == build_directory
    assert config.full_build_directory.exists()
    assert config.full_build_directory.is_dir()


def test_fallback_build_directory(shared_datadir: pathlib.Path) -> None:
    project_directory = shared_datadir / "torch_cpu"

    module_config = charonload.ConfigDict()
    module_config["test"] = charonload.Config(
        project_directory,
    )
    config = module_config["test"]

    config.full_build_directory.mkdir(parents=True, exist_ok=True)

    assert config.full_build_directory.exists()
    assert config.full_build_directory.is_dir()


def test_relative_project_directory() -> None:
    project_directory = "some/relative/path"

    module_config = charonload.ConfigDict()
    with pytest.raises(ValueError) as exc_info:
        module_config["test"] = charonload.Config(
            project_directory,
        )

    assert exc_info.type is ValueError


def test_non_existing_project_directory(tmp_path: pathlib.Path) -> None:
    project_directory = tmp_path / "some/absolute/non-existing/path"

    module_config = charonload.ConfigDict()
    with pytest.raises(ValueError) as exc_info:
        module_config["test"] = charonload.Config(
            project_directory,
        )

    assert exc_info.type is ValueError


def test_relative_build_directory(shared_datadir: pathlib.Path) -> None:
    project_directory = shared_datadir / "torch_cpu"
    build_directory = "some/relative/path"

    module_config = charonload.ConfigDict()
    with pytest.raises(ValueError) as exc_info:
        module_config["test"] = charonload.Config(
            project_directory,
            build_directory,
        )

    assert exc_info.type is ValueError


def _force_clean_build(
    shared_datadir: pathlib.Path,
    environ_value: str,
    value: bool,  # noqa: FBT001
    expected_value: bool,  # noqa: FBT001
) -> None:
    os.environ["CHARONLOAD_FORCE_CLEAN_BUILD"] = environ_value

    project_directory = shared_datadir / "torch_cpu"

    module_config = charonload.ConfigDict()
    module_config["test"] = charonload.Config(
        project_directory,
        clean_build=value,
    )
    config = module_config["test"]

    assert config.clean_build == expected_value


def _force_clean_build_error(shared_datadir: pathlib.Path, environ_value: str) -> None:
    os.environ["CHARONLOAD_FORCE_CLEAN_BUILD"] = environ_value

    project_directory = shared_datadir / "torch_cpu"

    module_config = charonload.ConfigDict()
    with pytest.raises(ValueError) as exc_info:
        module_config["test"] = charonload.Config(
            project_directory,
        )

    assert exc_info.type is ValueError


@pytest.mark.parametrize("environ_value", _true_values())
def test_force_clean_build_true(shared_datadir: pathlib.Path, environ_value: str) -> None:
    p = multiprocessing.get_context("spawn").Process(
        target=_force_clean_build,
        args=(
            shared_datadir,
            environ_value,
            False,
            True,
        ),
    )

    p.start()
    p.join()
    assert p.exitcode == 0


@pytest.mark.parametrize("environ_value", _false_values())
def test_force_clean_build_false(shared_datadir: pathlib.Path, environ_value: str) -> None:
    p = multiprocessing.get_context("spawn").Process(
        target=_force_clean_build,
        args=(
            shared_datadir,
            environ_value,
            True,
            False,
        ),
    )

    p.start()
    p.join()
    assert p.exitcode == 0


@pytest.mark.parametrize("environ_value", _error_values())
def test_force_clean_build_error(shared_datadir: pathlib.Path, environ_value: str) -> None:
    p = multiprocessing.get_context("spawn").Process(
        target=_force_clean_build_error,
        args=(
            shared_datadir,
            environ_value,
        ),
    )

    p.start()
    p.join()
    assert p.exitcode == 0


def test_prohibited_cmake_option_configuration_types(shared_datadir: pathlib.Path) -> None:
    project_directory = shared_datadir / "torch_cpu"

    module_config = charonload.ConfigDict()
    with pytest.raises(ValueError) as exc_info:
        module_config["test"] = charonload.Config(
            project_directory,
            cmake_options={"CMAKE_CONFIGURATION_TYPES": "Release"},
        )

    assert exc_info.type is ValueError


def test_prohibited_cmake_option_prefix_path(shared_datadir: pathlib.Path) -> None:
    project_directory = shared_datadir / "torch_cpu"

    module_config = charonload.ConfigDict()
    with pytest.raises(ValueError) as exc_info:
        module_config["test"] = charonload.Config(
            project_directory,
            cmake_options={"CMAKE_PREFIX_PATH": "some/path"},
        )

    assert exc_info.type is ValueError


def test_prohibited_cmake_option_project_top_level_includes(shared_datadir: pathlib.Path) -> None:
    project_directory = shared_datadir / "torch_cpu"

    module_config = charonload.ConfigDict()
    with pytest.raises(ValueError) as exc_info:
        module_config["test"] = charonload.Config(
            project_directory,
            cmake_options={"CMAKE_PROJECT_TOP_LEVEL_INCLUDES": "some/path"},
        )

    assert exc_info.type is ValueError


def test_prohibited_cmake_option_torch_extension_name(shared_datadir: pathlib.Path) -> None:
    project_directory = shared_datadir / "torch_cpu"

    module_config = charonload.ConfigDict()
    with pytest.raises(ValueError) as exc_info:
        module_config["test"] = charonload.Config(
            project_directory,
            cmake_options={"TORCH_EXTENSION_NAME": "Name"},
        )

    assert exc_info.type is ValueError


def test_prohibited_cmake_option_reserved_symbols(shared_datadir: pathlib.Path) -> None:
    project_directory = shared_datadir / "torch_cpu"

    module_config = charonload.ConfigDict()
    with pytest.raises(ValueError) as exc_info:
        module_config["test"] = charonload.Config(
            project_directory,
            cmake_options={"CHARONLOAD_TEST": "some value"},
        )

    assert exc_info.type is ValueError


def test_none_cmake_options(shared_datadir: pathlib.Path) -> None:
    project_directory = shared_datadir / "torch_cpu"

    module_config = charonload.ConfigDict()
    module_config["test"] = charonload.Config(
        project_directory,
        cmake_options=None,
    )
    config = module_config["test"]

    assert len(config.cmake_options) == 0


def test_empty_cmake_options(shared_datadir: pathlib.Path) -> None:
    project_directory = shared_datadir / "torch_cpu"

    module_config = charonload.ConfigDict()
    module_config["test"] = charonload.Config(
        project_directory,
        cmake_options={},
    )
    config = module_config["test"]

    assert len(config.cmake_options) == 0


def test_stubs_directory(shared_datadir: pathlib.Path, tmp_path: pathlib.Path) -> None:
    project_directory = shared_datadir / "torch_cpu"
    stubs_directory = tmp_path / "typings"
    assert not stubs_directory.exists()

    module_config = charonload.ConfigDict()
    module_config["test"] = charonload.Config(
        project_directory,
        stubs_directory=stubs_directory,
    )
    config = module_config["test"]

    assert config.full_stubs_directory is not None
    config.full_stubs_directory.mkdir(parents=True)

    assert config.full_stubs_directory == stubs_directory
    assert config.full_stubs_directory.exists()
    assert config.full_stubs_directory.is_dir()


def test_no_stubs_generation(shared_datadir: pathlib.Path) -> None:
    project_directory = shared_datadir / "torch_cpu"

    module_config = charonload.ConfigDict()
    module_config["test"] = charonload.Config(
        project_directory,
        stubs_directory=None,
    )
    config = module_config["test"]

    assert config.full_stubs_directory is None


def test_relative_stubs_directory(shared_datadir: pathlib.Path) -> None:
    project_directory = shared_datadir / "torch_cpu"
    stubs_directory = "some/relative/path"

    module_config = charonload.ConfigDict()
    with pytest.raises(ValueError) as exc_info:
        module_config["test"] = charonload.Config(
            project_directory,
            stubs_directory=stubs_directory,
        )

    assert exc_info.type is ValueError


def _force_stubs_invalid_ok(
    shared_datadir: pathlib.Path,
    environ_value: str,
    value: bool,  # noqa: FBT001
    expected_value: bool,  # noqa: FBT001
) -> None:
    os.environ["CHARONLOAD_FORCE_STUBS_INVALID_OK"] = environ_value

    project_directory = shared_datadir / "torch_cpu"

    module_config = charonload.ConfigDict()
    module_config["test"] = charonload.Config(
        project_directory,
        stubs_invalid_ok=value,
    )
    config = module_config["test"]

    assert config.stubs_invalid_ok == expected_value


def _force_stubs_invalid_ok_error(shared_datadir: pathlib.Path, environ_value: str) -> None:
    os.environ["CHARONLOAD_FORCE_STUBS_INVALID_OK"] = environ_value

    project_directory = shared_datadir / "torch_cpu"

    module_config = charonload.ConfigDict()
    with pytest.raises(ValueError) as exc_info:
        module_config["test"] = charonload.Config(
            project_directory,
        )

    assert exc_info.type is ValueError


@pytest.mark.parametrize("environ_value", _true_values())
def test_force_stubs_invalid_ok_true(shared_datadir: pathlib.Path, environ_value: str) -> None:
    p = multiprocessing.get_context("spawn").Process(
        target=_force_stubs_invalid_ok,
        args=(
            shared_datadir,
            environ_value,
            False,
            True,
        ),
    )

    p.start()
    p.join()
    assert p.exitcode == 0


@pytest.mark.parametrize("environ_value", _false_values())
def test_force_stubs_invalid_ok_false(shared_datadir: pathlib.Path, environ_value: str) -> None:
    p = multiprocessing.get_context("spawn").Process(
        target=_force_stubs_invalid_ok,
        args=(
            shared_datadir,
            environ_value,
            True,
            False,
        ),
    )

    p.start()
    p.join()
    assert p.exitcode == 0


@pytest.mark.parametrize("environ_value", _error_values())
def test_force_stubs_invalid_ok_error(shared_datadir: pathlib.Path, environ_value: str) -> None:
    p = multiprocessing.get_context("spawn").Process(
        target=_force_stubs_invalid_ok_error,
        args=(
            shared_datadir,
            environ_value,
        ),
    )

    p.start()
    p.join()
    assert p.exitcode == 0


def _force_verbose(
    shared_datadir: pathlib.Path,
    environ_value: str,
    value: bool,  # noqa: FBT001
    expected_value: bool,  # noqa: FBT001
) -> None:
    os.environ["CHARONLOAD_FORCE_VERBOSE"] = environ_value

    project_directory = shared_datadir / "torch_cpu"

    module_config = charonload.ConfigDict()
    module_config["test"] = charonload.Config(
        project_directory,
        verbose=value,
    )
    config = module_config["test"]

    assert config.verbose == expected_value


def _force_verbose_error(shared_datadir: pathlib.Path, environ_value: str) -> None:
    os.environ["CHARONLOAD_FORCE_VERBOSE"] = environ_value

    project_directory = shared_datadir / "torch_cpu"

    module_config = charonload.ConfigDict()
    with pytest.raises(ValueError) as exc_info:
        module_config["test"] = charonload.Config(
            project_directory,
        )

    assert exc_info.type is ValueError


@pytest.mark.parametrize("environ_value", _true_values())
def test_force_verbose_true(shared_datadir: pathlib.Path, environ_value: str) -> None:
    p = multiprocessing.get_context("spawn").Process(
        target=_force_verbose,
        args=(
            shared_datadir,
            environ_value,
            False,
            True,
        ),
    )

    p.start()
    p.join()
    assert p.exitcode == 0


@pytest.mark.parametrize("environ_value", _false_values())
def test_force_verbose_false(shared_datadir: pathlib.Path, environ_value: str) -> None:
    p = multiprocessing.get_context("spawn").Process(
        target=_force_verbose,
        args=(
            shared_datadir,
            environ_value,
            True,
            False,
        ),
    )

    p.start()
    p.join()
    assert p.exitcode == 0


@pytest.mark.parametrize("environ_value", _error_values())
def test_force_verbose_error(shared_datadir: pathlib.Path, environ_value: str) -> None:
    p = multiprocessing.get_context("spawn").Process(
        target=_force_verbose_error,
        args=(
            shared_datadir,
            environ_value,
        ),
    )

    p.start()
    p.join()
    assert p.exitcode == 0
