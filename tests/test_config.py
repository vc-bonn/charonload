from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pathlib

import pytest

import charonload


def test_provided_build_directory(shared_datadir: pathlib.Path, tmp_path: pathlib.Path) -> None:
    project_directory = shared_datadir / "torch_cpu"
    build_directory = tmp_path / "build"
    assert not build_directory.exists()

    config = charonload.Config(
        project_directory,
        build_directory,
    )

    config.full_build_directory.mkdir(parents=True)

    assert config.full_build_directory == build_directory
    assert config.full_build_directory.exists()
    assert config.full_build_directory.is_dir()


def test_fallback_build_directory(shared_datadir: pathlib.Path) -> None:
    project_directory = shared_datadir / "torch_cpu"

    config = charonload.Config(
        project_directory,
    )

    config.full_build_directory.mkdir(parents=True, exist_ok=True)

    assert config.full_build_directory.exists()
    assert config.full_build_directory.is_dir()


def test_relative_project_directory() -> None:
    project_directory = "some/relative/path"

    with pytest.raises(ValueError) as exc_info:
        charonload.Config(
            project_directory,
        )

    assert exc_info.type is ValueError


def test_non_existing_project_directory(tmp_path: pathlib.Path) -> None:
    project_directory = tmp_path / "some/absolute/non-existing/path"

    with pytest.raises(ValueError) as exc_info:
        charonload.Config(
            project_directory,
        )

    assert exc_info.type is ValueError


def test_relative_build_directory(shared_datadir: pathlib.Path) -> None:
    project_directory = shared_datadir / "torch_cpu"
    build_directory = "some/relative/path"

    with pytest.raises(ValueError) as exc_info:
        charonload.Config(
            project_directory,
            build_directory,
        )

    assert exc_info.type is ValueError


def test_prohibited_cmake_option_configuration_types(shared_datadir: pathlib.Path) -> None:
    project_directory = shared_datadir / "torch_cpu"

    with pytest.raises(ValueError) as exc_info:
        charonload.Config(
            project_directory,
            cmake_options={"CMAKE_CONFIGURATION_TYPES": "Release"},
        )

    assert exc_info.type is ValueError


def test_prohibited_cmake_option_prefix_path(shared_datadir: pathlib.Path) -> None:
    project_directory = shared_datadir / "torch_cpu"

    with pytest.raises(ValueError) as exc_info:
        charonload.Config(
            project_directory,
            cmake_options={"CMAKE_PREFIX_PATH": "some/path"},
        )

    assert exc_info.type is ValueError


def test_prohibited_cmake_option_project_top_level_includes(shared_datadir: pathlib.Path) -> None:
    project_directory = shared_datadir / "torch_cpu"

    with pytest.raises(ValueError) as exc_info:
        charonload.Config(
            project_directory,
            cmake_options={"CMAKE_PROJECT_TOP_LEVEL_INCLUDES": "some/path"},
        )

    assert exc_info.type is ValueError


def test_prohibited_cmake_option_torch_extension_name(shared_datadir: pathlib.Path) -> None:
    project_directory = shared_datadir / "torch_cpu"

    with pytest.raises(ValueError) as exc_info:
        charonload.Config(
            project_directory,
            cmake_options={"TORCH_EXTENSION_NAME": "Name"},
        )

    assert exc_info.type is ValueError


def test_prohibited_cmake_option_reserved_symbols(shared_datadir: pathlib.Path) -> None:
    project_directory = shared_datadir / "torch_cpu"

    with pytest.raises(ValueError) as exc_info:
        charonload.Config(
            project_directory,
            cmake_options={"CHARONLOAD_TEST": "some value"},
        )

    assert exc_info.type is ValueError


def test_none_cmake_options(shared_datadir: pathlib.Path) -> None:
    project_directory = shared_datadir / "torch_cpu"

    config = charonload.Config(
        project_directory,
        cmake_options=None,
    )

    assert len(config.cmake_options) == 0


def test_empty_cmake_options(shared_datadir: pathlib.Path) -> None:
    project_directory = shared_datadir / "torch_cpu"

    config = charonload.Config(
        project_directory,
        cmake_options={},
    )

    assert len(config.cmake_options) == 0


def test_stubs_directory(shared_datadir: pathlib.Path, tmp_path: pathlib.Path) -> None:
    project_directory = shared_datadir / "torch_cpu"
    stubs_directory = tmp_path / "typings"
    assert not stubs_directory.exists()

    config = charonload.Config(
        project_directory,
        stubs_directory=stubs_directory,
    )

    assert config.full_stubs_directory is not None
    config.full_stubs_directory.mkdir(parents=True)

    assert config.full_stubs_directory == stubs_directory
    assert config.full_stubs_directory.exists()
    assert config.full_stubs_directory.is_dir()


def test_no_stubs_generation(shared_datadir: pathlib.Path) -> None:
    project_directory = shared_datadir / "torch_cpu"

    config = charonload.Config(
        project_directory,
        stubs_directory=None,
    )

    assert config.full_stubs_directory is None


def test_relative_stubs_directory(shared_datadir: pathlib.Path) -> None:
    project_directory = shared_datadir / "torch_cpu"
    stubs_directory = "some/relative/path"

    with pytest.raises(ValueError) as exc_info:
        charonload.Config(
            project_directory,
            stubs_directory=stubs_directory,
        )

    assert exc_info.type is ValueError
