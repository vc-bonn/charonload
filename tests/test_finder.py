from __future__ import annotations

import contextlib
import importlib
import importlib.util
import io
import multiprocessing
import os
import pathlib
import platform
import shutil
import sys
import threading
import time
import types
import warnings
from typing import TYPE_CHECKING, Any

import pytest
import torch

if TYPE_CHECKING:
    import pytest_mock

import charonload

VSCODE_STUBS_DIRECTORY = pathlib.Path(__file__).parents[1] / "typings"


def is_test_project_installed() -> bool:
    return importlib.util.find_spec("charonload_installed_project") is not None


@pytest.mark.skipif(not is_test_project_installed(), reason="Pre-installed test project required")
def test_installed_project() -> None:
    import charonload_installed_project

    config = charonload.module_config["_c_charonload_installed_project"]
    assert config.full_build_directory not in config.full_project_directory.parents
    assert config.full_stubs_directory not in config.full_project_directory.parents

    t_input = torch.randint(0, 10, size=(3, 3, 3), dtype=torch.float, device="cpu")
    t_output = charonload_installed_project.two_times(t_input)  # type: ignore[attr-defined]

    assert t_output.device == t_input.device
    assert t_output.shape == t_input.shape
    assert torch.equal(t_output, 2 * t_input)


def test_torch_cpu(shared_datadir: pathlib.Path, tmp_path: pathlib.Path) -> None:
    project_directory = shared_datadir / "torch_cpu"
    build_directory = tmp_path / "build"

    charonload.module_config["test_torch_cpu"] = charonload.Config(
        project_directory,
        build_directory,
        stubs_directory=VSCODE_STUBS_DIRECTORY,
    )

    import test_torch_cpu as test_torch

    t_input = torch.randint(0, 10, size=(3, 3, 3), dtype=torch.float, device="cpu")
    t_output = test_torch.two_times(t_input)

    assert t_output.device == t_input.device
    assert t_output.shape == t_input.shape
    assert torch.equal(t_output, 2 * t_input)


@pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA required")
def test_torch_cuda(shared_datadir: pathlib.Path, tmp_path: pathlib.Path) -> None:
    project_directory = shared_datadir / "torch_cuda"
    build_directory = tmp_path / "build"

    charonload.module_config["test_torch_cuda"] = charonload.Config(
        project_directory,
        build_directory,
        stubs_directory=VSCODE_STUBS_DIRECTORY,
    )

    import test_torch_cuda as test_torch

    t_input = torch.randint(0, 10, size=(3, 3, 3), dtype=torch.float, device="cuda")
    t_output = test_torch.two_times(t_input)

    assert t_output.device == t_input.device
    assert t_output.shape == t_input.shape
    assert torch.equal(t_output, 2 * t_input)


def _torch_cuda_custom_archs(shared_datadir: pathlib.Path, tmp_path: pathlib.Path) -> None:
    os.environ["TORCH_CUDA_ARCH_LIST"] = "8.0 8.6"  # Use 2 different archs

    project_directory = shared_datadir / "torch_cuda"
    build_directory = tmp_path / "build"

    charonload.module_config["test_torch_cuda_custom_archs"] = charonload.Config(
        project_directory,
        build_directory,
        stubs_directory=VSCODE_STUBS_DIRECTORY,
    )

    import test_torch_cuda_custom_archs as test_torch

    t_input = torch.randint(0, 10, size=(3, 3, 3), dtype=torch.float, device="cuda")
    t_output = test_torch.two_times(t_input)

    assert t_output.device == t_input.device
    assert t_output.shape == t_input.shape
    assert torch.equal(t_output, 2 * t_input)


@pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA required")
def test_torch_cuda_custom_archs(shared_datadir: pathlib.Path, tmp_path: pathlib.Path) -> None:
    p = multiprocessing.get_context("spawn").Process(
        target=_torch_cuda_custom_archs,
        args=(
            shared_datadir,
            tmp_path,
        ),
    )

    p.start()
    p.join()
    assert p.exitcode == 0


def test_torch_common_static(shared_datadir: pathlib.Path, tmp_path: pathlib.Path) -> None:
    project_directory = shared_datadir / "torch_common_static"
    build_directory = tmp_path / "build"

    charonload.module_config["test_torch_common_static"] = charonload.Config(
        project_directory,
        build_directory,
        stubs_directory=VSCODE_STUBS_DIRECTORY,
    )

    import test_torch_common_static as test_torch

    t_input = torch.randint(0, 10, size=(3, 3, 3), dtype=torch.float, device="cpu")
    t_output = test_torch.two_times(t_input)

    assert t_output.device == t_input.device
    assert t_output.shape == t_input.shape
    assert torch.equal(t_output, 2 * t_input)


def test_torch_common_shared(shared_datadir: pathlib.Path, tmp_path: pathlib.Path) -> None:
    project_directory = shared_datadir / "torch_common_shared"
    build_directory = tmp_path / "build"

    charonload.module_config["test_torch_common_shared"] = charonload.Config(
        project_directory,
        build_directory,
        stubs_directory=VSCODE_STUBS_DIRECTORY,
    )

    import test_torch_common_shared as test_torch

    t_input = torch.randint(0, 10, size=(3, 3, 3), dtype=torch.float, device="cpu")
    t_output = test_torch.two_times(t_input)

    assert t_output.device == t_input.device
    assert t_output.shape == t_input.shape
    assert torch.equal(t_output, 2 * t_input)


@pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA required")
def test_torch_cudart_shared(shared_datadir: pathlib.Path, tmp_path: pathlib.Path) -> None:
    project_directory = shared_datadir / "torch_cudart_shared"
    build_directory = tmp_path / "build"

    charonload.module_config["test_torch_cudart_shared"] = charonload.Config(
        project_directory,
        build_directory,
        stubs_directory=VSCODE_STUBS_DIRECTORY,
    )

    import test_torch_cudart_shared as test_torch

    t_input = torch.randint(0, 10, size=(3, 3, 3), dtype=torch.float, device="cpu")
    t_output = test_torch.two_times(t_input)

    assert t_output.device == t_input.device
    assert t_output.shape == t_input.shape
    assert torch.equal(t_output, 2 * t_input)

    assert test_torch.numel_times_multi_processor_count(
        t_input
    ) == test_torch.numel_times_multi_processor_count_aliased(t_input)


@pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA required")
def test_torch_cudart_static(shared_datadir: pathlib.Path, tmp_path: pathlib.Path) -> None:
    project_directory = shared_datadir / "torch_cudart_static"
    build_directory = tmp_path / "build"

    charonload.module_config["test_torch_cudart_static"] = charonload.Config(
        project_directory,
        build_directory,
        stubs_directory=VSCODE_STUBS_DIRECTORY,
    )

    import test_torch_cudart_static as test_torch

    t_input = torch.randint(0, 10, size=(3, 3, 3), dtype=torch.float, device="cpu")
    t_output = test_torch.two_times(t_input)

    assert t_output.device == t_input.device
    assert t_output.shape == t_input.shape
    assert torch.equal(t_output, 2 * t_input)

    assert test_torch.numel_times_multi_processor_count(
        t_input
    ) == test_torch.numel_times_multi_processor_count_aliased(t_input)


def test_torch_cxx_standard(shared_datadir: pathlib.Path, tmp_path: pathlib.Path) -> None:
    project_directory = shared_datadir / "torch_cxx_standard"
    build_directory = tmp_path / "build"

    charonload.module_config["test_torch_cxx_standard"] = charonload.Config(
        project_directory,
        build_directory,
        stubs_directory=VSCODE_STUBS_DIRECTORY,
    )

    import test_torch_cxx_standard as test_torch

    t_input = torch.randint(0, 10, size=(3, 3, 3), dtype=torch.float, device="cpu")
    t_output = test_torch.two_times(t_input)

    assert t_output.device == t_input.device
    assert t_output.shape == t_input.shape
    assert torch.equal(t_output, 2 * t_input)


def test_torch_cxx11_abi(shared_datadir: pathlib.Path, tmp_path: pathlib.Path) -> None:
    project_directory = shared_datadir / "torch_cxx11_abi"
    build_directory = tmp_path / "build"

    charonload.module_config["test_torch_cxx11_abi"] = charonload.Config(
        project_directory,
        build_directory,
        stubs_directory=VSCODE_STUBS_DIRECTORY,
    )

    import test_torch_cxx11_abi as test_torch

    t_input = torch.randint(0, 10, size=(3, 3, 3), dtype=torch.float, device="cpu")
    t_output = test_torch.two_times(t_input)

    assert t_output.device == t_input.device
    assert t_output.shape == t_input.shape
    assert torch.equal(t_output, 2 * t_input)

    assert test_torch.numel_to_string(t_input) == str(t_input.numel())
    assert test_torch.numel_to_string_aliased(t_input) == str(t_input.numel())


def test_torch_pic(shared_datadir: pathlib.Path, tmp_path: pathlib.Path) -> None:
    project_directory = shared_datadir / "torch_pic"
    build_directory = tmp_path / "build"

    charonload.module_config["test_torch_pic"] = charonload.Config(
        project_directory,
        build_directory,
        stubs_directory=VSCODE_STUBS_DIRECTORY,
    )

    import test_torch_pic as test_torch

    t_input = torch.randint(0, 10, size=(3, 3, 3), dtype=torch.float, device="cpu")
    t_output = test_torch.two_times(t_input)

    assert t_output.device == t_input.device
    assert t_output.shape == t_input.shape
    assert torch.equal(t_output, 2 * t_input)


def test_torch_submodule_import_top(shared_datadir: pathlib.Path, tmp_path: pathlib.Path) -> None:
    project_directory = shared_datadir / "torch_submodule"
    build_directory = tmp_path / "build"

    charonload.module_config["test_torch_submodule_import_top"] = charonload.Config(
        project_directory,
        build_directory,
        stubs_directory=VSCODE_STUBS_DIRECTORY,
    )

    import test_torch_submodule_import_top as test_torch

    t_input = torch.randint(0, 10, size=(3, 3, 3), dtype=torch.float, device="cpu")
    t_output = test_torch.sub.two_times(t_input)

    assert t_output.device == t_input.device
    assert t_output.shape == t_input.shape
    assert torch.equal(t_output, 2 * t_input)


def test_torch_submodule_import_sub(shared_datadir: pathlib.Path, tmp_path: pathlib.Path) -> None:
    project_directory = shared_datadir / "torch_submodule"
    build_directory = tmp_path / "build"

    charonload.module_config["test_torch_submodule_import_sub"] = charonload.Config(
        project_directory,
        build_directory,
        stubs_directory=VSCODE_STUBS_DIRECTORY,
    )

    import test_torch_submodule_import_sub.sub as test_torch

    t_input = torch.randint(0, 10, size=(3, 3, 3), dtype=torch.float, device="cpu")
    t_output = test_torch.two_times(t_input)

    assert t_output.device == t_input.device
    assert t_output.shape == t_input.shape
    assert torch.equal(t_output, 2 * t_input)


def test_torch_submodule_from_top_import(shared_datadir: pathlib.Path, tmp_path: pathlib.Path) -> None:
    project_directory = shared_datadir / "torch_submodule"
    build_directory = tmp_path / "build"

    charonload.module_config["test_torch_submodule_from_top_import"] = charonload.Config(
        project_directory,
        build_directory,
        stubs_directory=VSCODE_STUBS_DIRECTORY,
    )

    from test_torch_submodule_from_top_import import sub

    t_input = torch.randint(0, 10, size=(3, 3, 3), dtype=torch.float, device="cpu")
    t_output = sub.two_times(t_input)

    assert t_output.device == t_input.device
    assert t_output.shape == t_input.shape
    assert torch.equal(t_output, 2 * t_input)


def test_torch_submodule_from_sub_import(shared_datadir: pathlib.Path, tmp_path: pathlib.Path) -> None:
    project_directory = shared_datadir / "torch_submodule"
    build_directory = tmp_path / "build"

    charonload.module_config["test_torch_submodule_from_sub_import"] = charonload.Config(
        project_directory,
        build_directory,
        stubs_directory=VSCODE_STUBS_DIRECTORY,
    )

    from test_torch_submodule_from_sub_import.sub import two_times

    t_input = torch.randint(0, 10, size=(3, 3, 3), dtype=torch.float, device="cpu")
    t_output = two_times(t_input)

    assert t_output.device == t_input.device
    assert t_output.shape == t_input.shape
    assert torch.equal(t_output, 2 * t_input)


def test_torch_subdirectory(shared_datadir: pathlib.Path, tmp_path: pathlib.Path) -> None:
    project_directory = shared_datadir / "torch_subdirectory"
    build_directory = tmp_path / "build"

    charonload.module_config["test_torch_subdirectory"] = charonload.Config(
        project_directory,
        build_directory,
        stubs_directory=VSCODE_STUBS_DIRECTORY,
    )

    import test_torch_subdirectory as test_torch

    t_input = torch.randint(0, 10, size=(3, 3, 3), dtype=torch.float, device="cpu")
    t_output = test_torch.two_times(t_input)

    assert t_output.device == t_input.device
    assert t_output.shape == t_input.shape
    assert torch.equal(t_output, 2 * t_input)


@pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA required")
def test_torch_cuda_subdirectory(shared_datadir: pathlib.Path, tmp_path: pathlib.Path) -> None:
    project_directory = shared_datadir / "torch_cuda_subdirectory"
    build_directory = tmp_path / "build"

    charonload.module_config["test_torch_cuda_subdirectory"] = charonload.Config(
        project_directory,
        build_directory,
        stubs_directory=VSCODE_STUBS_DIRECTORY,
    )

    import test_torch_cuda_subdirectory as test_torch

    t_input = torch.randint(0, 10, size=(3, 3, 3), dtype=torch.float, device="cuda")
    t_output = test_torch.two_times(t_input)

    assert t_output.device == t_input.device
    assert t_output.shape == t_input.shape
    assert torch.equal(t_output, 2 * t_input)

    t_input = torch.randint(0, 10, size=(3, 3, 3), dtype=torch.float, device="cuda")
    t_output = test_torch.three_times(t_input)

    assert t_output.device == t_input.device
    assert t_output.shape == t_input.shape
    assert torch.equal(t_output, 3 * t_input)


def test_torch_import_twice(shared_datadir: pathlib.Path, tmp_path: pathlib.Path) -> None:
    project_directory = shared_datadir / "torch_cpu"
    build_directory = tmp_path / "build"

    charonload.module_config["test_torch_import_twice"] = charonload.Config(
        project_directory,
        build_directory,
        stubs_directory=VSCODE_STUBS_DIRECTORY,
    )

    import test_torch_import_twice

    # Empty statement to keep double import after formatting
    None  # noqa: B018

    import test_torch_import_twice  # noqa: F811

    t_input = torch.randint(0, 10, size=(3, 3, 3), dtype=torch.float, device="cpu")
    t_output = test_torch_import_twice.two_times(t_input)

    assert t_output.device == t_input.device
    assert t_output.shape == t_input.shape
    assert torch.equal(t_output, 2 * t_input)


def test_torch_reload_import(shared_datadir: pathlib.Path, tmp_path: pathlib.Path) -> None:
    project_directory = shared_datadir / "torch_cpu"
    build_directory = tmp_path / "build"

    charonload.module_config["test_torch_reload_import"] = charonload.Config(
        project_directory,
        build_directory,
        stubs_directory=VSCODE_STUBS_DIRECTORY,
    )

    original_num_sys_paths = len(sys.path)

    import test_torch_reload_import

    new_num_sys_paths = len(sys.path)
    assert new_num_sys_paths == original_num_sys_paths + 1

    importlib.reload(test_torch_reload_import)

    reloaded_num_sys_paths = len(sys.path)
    assert reloaded_num_sys_paths == new_num_sys_paths

    t_input = torch.randint(0, 10, size=(3, 3, 3), dtype=torch.float, device="cpu")
    t_output = test_torch_reload_import.two_times(t_input)

    assert t_output.device == t_input.device
    assert t_output.shape == t_input.shape
    assert torch.equal(t_output, 2 * t_input)


def _torch_incremental_build_function(
    module_name: str,
    project_directory: pathlib.Path,
    build_directory: pathlib.Path,
    stubs_directory: pathlib.Path | None,
    in_submodule: bool,  # noqa: FBT001
    result: Any,  # noqa: ANN401
) -> None:
    charonload.module_config[module_name] = charonload.Config(
        project_directory,
        build_directory,
        stubs_directory=stubs_directory,
    )

    t_start = time.perf_counter()
    test_torch = importlib.import_module(module_name)
    t_end = time.perf_counter()

    result.value = float(t_end - t_start)

    t_input = torch.randint(0, 10, size=(3, 3, 3), dtype=torch.float, device="cpu")

    t_output = test_torch.sub.two_times(t_input) if in_submodule else test_torch.two_times(t_input)

    assert t_output.device == t_input.device
    assert t_output.shape == t_input.shape
    assert torch.equal(t_output, 2 * t_input)


def _torch_incremental_build(
    module_name: str,
    project_directory: pathlib.Path,
    build_directory: pathlib.Path,
    *,
    stubs_directory: pathlib.Path | None = None,
    in_submodule: bool = False,
) -> float:
    result = multiprocessing.get_context("spawn").Value("d", 0.0)
    p = multiprocessing.get_context("spawn").Process(
        target=_torch_incremental_build_function,
        args=(
            module_name,
            project_directory,
            build_directory,
            stubs_directory,
            in_submodule,
            result,
        ),
    )

    p.start()
    p.join()
    assert p.exitcode == 0

    return float(result.value)


def test_torch_incremental_build_cpp(shared_datadir: pathlib.Path, tmp_path: pathlib.Path) -> None:
    project_directory = shared_datadir / "torch_cpu"
    build_directory = tmp_path / "build"

    _torch_incremental_build("test_torch_incremental_build_cpp", project_directory, build_directory)

    t_no_changes = _torch_incremental_build("test_torch_incremental_build_cpp", project_directory, build_directory)

    (project_directory / "two_times_cpu.cpp").touch()

    t_with_changes = _torch_incremental_build("test_torch_incremental_build_cpp", project_directory, build_directory)

    assert t_with_changes > t_no_changes


def test_torch_incremental_build_cmake(shared_datadir: pathlib.Path, tmp_path: pathlib.Path) -> None:
    project_directory = shared_datadir / "torch_cpu"
    build_directory = tmp_path / "build"

    _torch_incremental_build("test_torch_incremental_build_cmake", project_directory, build_directory)

    t_no_changes = _torch_incremental_build("test_torch_incremental_build_cmake", project_directory, build_directory)

    (project_directory / "CMakeLists.txt").touch()

    t_with_changes = _torch_incremental_build("test_torch_incremental_build_cmake", project_directory, build_directory)

    assert t_with_changes > t_no_changes


def test_torch_incremental_build_stubs_single(shared_datadir: pathlib.Path, tmp_path: pathlib.Path) -> None:
    project_directory = shared_datadir / "torch_cpu"
    build_directory = tmp_path / "build"

    _torch_incremental_build(
        "test_torch_incremental_build_stubs_single",
        project_directory,
        build_directory,
        stubs_directory=VSCODE_STUBS_DIRECTORY,
        in_submodule=False,
    )

    t_no_changes = _torch_incremental_build(
        "test_torch_incremental_build_stubs_single",
        project_directory,
        build_directory,
        stubs_directory=VSCODE_STUBS_DIRECTORY,
        in_submodule=False,
    )

    # Either a single file or a directory containing a single file will be generated
    if (stub := VSCODE_STUBS_DIRECTORY / "test_torch_incremental_build_stubs_single.pyi").exists():
        stub.unlink()
    if (stub := VSCODE_STUBS_DIRECTORY / "test_torch_incremental_build_stubs_single").exists():
        shutil.rmtree(stub, ignore_errors=True)

    t_with_changes = _torch_incremental_build(
        "test_torch_incremental_build_stubs_single",
        project_directory,
        build_directory,
        stubs_directory=VSCODE_STUBS_DIRECTORY,
        in_submodule=False,
    )

    assert t_with_changes > t_no_changes


def test_torch_incremental_build_stubs_multiple(shared_datadir: pathlib.Path, tmp_path: pathlib.Path) -> None:
    project_directory = shared_datadir / "torch_submodule"
    build_directory = tmp_path / "build"

    _torch_incremental_build(
        "test_torch_incremental_build_stubs_multiple",
        project_directory,
        build_directory,
        stubs_directory=VSCODE_STUBS_DIRECTORY,
        in_submodule=True,
    )

    t_no_changes = _torch_incremental_build(
        "test_torch_incremental_build_stubs_multiple",
        project_directory,
        build_directory,
        stubs_directory=VSCODE_STUBS_DIRECTORY,
        in_submodule=True,
    )

    shutil.rmtree(VSCODE_STUBS_DIRECTORY / "test_torch_incremental_build_stubs_multiple", ignore_errors=True)

    t_with_changes = _torch_incremental_build(
        "test_torch_incremental_build_stubs_multiple",
        project_directory,
        build_directory,
        stubs_directory=VSCODE_STUBS_DIRECTORY,
        in_submodule=True,
    )

    assert t_with_changes > t_no_changes


def test_torch_cmake_include_twice(shared_datadir: pathlib.Path, tmp_path: pathlib.Path) -> None:
    project_directory = shared_datadir / "torch_cmake_include_twice"
    build_directory = tmp_path / "build"

    charonload.module_config["test_torch_cmake_include_twice"] = charonload.Config(
        project_directory,
        build_directory,
        stubs_directory=VSCODE_STUBS_DIRECTORY,
    )

    import test_torch_cmake_include_twice as test_torch

    t_input = torch.randint(0, 10, size=(3, 3, 3), dtype=torch.float, device="cpu")
    t_output = test_torch.two_times(t_input)

    assert t_output.device == t_input.device
    assert t_output.shape == t_input.shape
    assert torch.equal(t_output, 2 * t_input)


def test_torch_cmake_old_policy(shared_datadir: pathlib.Path, tmp_path: pathlib.Path) -> None:
    project_directory = shared_datadir / "torch_cmake_old_policy"
    build_directory = tmp_path / "build"

    charonload.module_config["test_torch_cmake_old_policy"] = charonload.Config(
        project_directory,
        build_directory,
        stubs_directory=VSCODE_STUBS_DIRECTORY,
    )

    import test_torch_cmake_old_policy as test_torch

    t_input = torch.randint(0, 10, size=(3, 3, 3), dtype=torch.float, device="cpu")
    t_output = test_torch.two_times(t_input)

    assert t_output.device == t_input.device
    assert t_output.shape == t_input.shape
    assert torch.equal(t_output, 2 * t_input)


@pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA required")
def test_torch_cmake_old_policy_cuda(shared_datadir: pathlib.Path, tmp_path: pathlib.Path) -> None:
    project_directory = shared_datadir / "torch_cmake_old_policy_cuda"
    build_directory = tmp_path / "build"

    charonload.module_config["test_torch_cmake_old_policy_cuda"] = charonload.Config(
        project_directory,
        build_directory,
        stubs_directory=VSCODE_STUBS_DIRECTORY,
    )

    import test_torch_cmake_old_policy_cuda as test_torch

    t_input = torch.randint(0, 10, size=(3, 3, 3), dtype=torch.float, device="cuda")
    t_output = test_torch.two_times(t_input)

    assert t_output.device == t_input.device
    assert t_output.shape == t_input.shape
    assert torch.equal(t_output, 2 * t_input)


def test_torch_gitignore(shared_datadir: pathlib.Path, tmp_path: pathlib.Path) -> None:
    project_directory = shared_datadir / "torch_cpu"
    build_directory = tmp_path / "build"

    charonload.module_config["test_torch_gitignore"] = charonload.Config(
        project_directory,
        build_directory,
        stubs_directory=VSCODE_STUBS_DIRECTORY,
    )

    import test_torch_gitignore as test_torch

    t_input = torch.randint(0, 10, size=(3, 3, 3), dtype=torch.float, device="cpu")
    t_output = test_torch.two_times(t_input)

    assert t_output.device == t_input.device
    assert t_output.shape == t_input.shape
    assert torch.equal(t_output, 2 * t_input)

    assert (build_directory / ".gitignore").exists()


def test_torch_clean_build(shared_datadir: pathlib.Path, tmp_path: pathlib.Path) -> None:
    project_directory = shared_datadir / "torch_cpu"
    build_directory = tmp_path / "build"

    charonload.module_config["test_torch_clean_build"] = charonload.Config(
        project_directory,
        build_directory,
        clean_build=True,
        stubs_directory=VSCODE_STUBS_DIRECTORY,
    )

    dirty_files = [
        build_directory / "dirty.txt",
        build_directory / "charonload" / "dirty_dir" / "charonload" / "build.lock",
        build_directory / "non_top_level" / ".gitignore",
    ]

    for f in dirty_files:
        f.parent.mkdir(parents=True, exist_ok=True)
        f.touch()
        assert f.exists()

    import test_torch_clean_build as test_torch

    t_input = torch.randint(0, 10, size=(3, 3, 3), dtype=torch.float, device="cpu")
    t_output = test_torch.two_times(t_input)

    assert t_output.device == t_input.device
    assert t_output.shape == t_input.shape
    assert torch.equal(t_output, 2 * t_input)

    for f in dirty_files:
        assert not f.exists()

    assert (build_directory / ".gitignore").exists()


def test_torch_clean_build_compatible_version(shared_datadir: pathlib.Path, tmp_path: pathlib.Path) -> None:
    project_directory = shared_datadir / "torch_cpu"
    build_directory = tmp_path / "build"

    charonload.module_config["test_torch_clean_build_compatible_version"] = charonload.Config(
        project_directory,
        build_directory,
        stubs_directory=VSCODE_STUBS_DIRECTORY,
    )

    dirty_file = build_directory / "dirty.txt"

    build_directory.mkdir(parents=True, exist_ok=True)
    (build_directory / "charonload").mkdir(parents=True, exist_ok=True)
    dirty_file.touch()
    with (build_directory / "charonload" / "version.txt").open("w") as f:
        f.write(".".join([*charonload.__version__.split(".")[:-1], "9999"]))

    assert dirty_file.exists()

    import test_torch_clean_build_compatible_version as test_torch

    t_input = torch.randint(0, 10, size=(3, 3, 3), dtype=torch.float, device="cpu")
    t_output = test_torch.two_times(t_input)

    assert t_output.device == t_input.device
    assert t_output.shape == t_input.shape
    assert torch.equal(t_output, 2 * t_input)

    assert dirty_file.exists()


def test_torch_clean_build_incompatible_version(shared_datadir: pathlib.Path, tmp_path: pathlib.Path) -> None:
    project_directory = shared_datadir / "torch_cpu"
    build_directory = tmp_path / "build"

    charonload.module_config["test_torch_clean_build_incompatible_version"] = charonload.Config(
        project_directory,
        build_directory,
        stubs_directory=VSCODE_STUBS_DIRECTORY,
    )

    dirty_file = build_directory / "dirty.txt"

    build_directory.mkdir(parents=True, exist_ok=True)
    (build_directory / "charonload").mkdir(parents=True, exist_ok=True)
    dirty_file.touch()
    with (build_directory / "charonload" / "version.txt").open("w") as f:
        f.write("0.0")

    assert dirty_file.exists()

    import test_torch_clean_build_incompatible_version as test_torch

    t_input = torch.randint(0, 10, size=(3, 3, 3), dtype=torch.float, device="cpu")
    t_output = test_torch.two_times(t_input)

    assert t_output.device == t_input.device
    assert t_output.shape == t_input.shape
    assert torch.equal(t_output, 2 * t_input)

    assert not dirty_file.exists()


def test_torch_clean_build_incompatible_torch_version(shared_datadir: pathlib.Path, tmp_path: pathlib.Path) -> None:
    project_directory = shared_datadir / "torch_cpu"
    build_directory = tmp_path / "build"

    charonload.module_config["test_torch_clean_build_incompatible_torch_version"] = charonload.Config(
        project_directory,
        build_directory,
        stubs_directory=VSCODE_STUBS_DIRECTORY,
    )
    config = charonload.module_config["test_torch_clean_build_incompatible_torch_version"]

    dirty_file = build_directory / "dirty.txt"

    build_directory.mkdir(parents=True, exist_ok=True)
    (build_directory / "charonload" / config.build_type).mkdir(parents=True, exist_ok=True)
    dirty_file.touch()
    with (build_directory / "charonload" / config.build_type / "torch_version.txt").open("w") as f:
        f.write("0.0")

    assert dirty_file.exists()

    import test_torch_clean_build_incompatible_torch_version as test_torch

    t_input = torch.randint(0, 10, size=(3, 3, 3), dtype=torch.float, device="cpu")
    t_output = test_torch.two_times(t_input)

    assert t_output.device == t_input.device
    assert t_output.shape == t_input.shape
    assert torch.equal(t_output, 2 * t_input)

    assert not dirty_file.exists()


def test_torch_clean_build_configure_failed(shared_datadir: pathlib.Path, tmp_path: pathlib.Path) -> None:
    build_directory = tmp_path / "build"

    charonload.module_config["test_torch_clean_build_configure_failed"] = charonload.Config(
        shared_datadir / "torch_broken_cmake",
        build_directory,
        stubs_directory=VSCODE_STUBS_DIRECTORY,
    )

    dirty_file = build_directory / "dirty.txt"

    build_directory.mkdir(parents=True, exist_ok=True)
    dirty_file.touch()

    assert dirty_file.exists()

    with pytest.raises(charonload.JITCompileError) as exc_info:
        import test_torch_clean_build_configure_failed as test_torch

    assert exc_info.type is charonload.CMakeConfigureError
    assert dirty_file.exists()

    charonload.module_config["test_torch_clean_build_configure_failed"] = charonload.Config(
        shared_datadir / "torch_cpu",
        build_directory,
        stubs_directory=VSCODE_STUBS_DIRECTORY,
    )

    import test_torch_clean_build_configure_failed as test_torch

    t_input = torch.randint(0, 10, size=(3, 3, 3), dtype=torch.float, device="cpu")
    t_output = test_torch.two_times(t_input)

    assert t_output.device == t_input.device
    assert t_output.shape == t_input.shape
    assert torch.equal(t_output, 2 * t_input)

    assert not dirty_file.exists()


def _torch_clean_build_reconfigure_failed(
    project_directory: pathlib.Path,
    build_directory: pathlib.Path,
    should_fail: bool,  # noqa: FBT001
    dirty_file: pathlib.Path,
) -> None:
    charonload.module_config["test_torch_clean_build_reconfigure_failed"] = charonload.Config(
        project_directory,
        build_directory,
        stubs_directory=VSCODE_STUBS_DIRECTORY,
    )

    if should_fail:
        with pytest.raises(charonload.JITCompileError) as exc_info:
            import test_torch_clean_build_reconfigure_failed as test_torch

        assert exc_info.type is charonload.CMakeConfigureError

    else:
        import test_torch_clean_build_reconfigure_failed as test_torch

        t_input = torch.randint(0, 10, size=(3, 3, 3), dtype=torch.float, device="cpu")
        t_output = test_torch.two_times(t_input)

        assert t_output.device == t_input.device
        assert t_output.shape == t_input.shape
        assert torch.equal(t_output, 2 * t_input)

    assert dirty_file.exists() == should_fail


def test_torch_clean_build_reconfigure_failed(shared_datadir: pathlib.Path, tmp_path: pathlib.Path) -> None:
    project_directory = shared_datadir / "torch_reconfigure_failed"
    build_directory = tmp_path / "build"
    dirty_file = build_directory / "dirty.txt"

    p = multiprocessing.get_context("spawn").Process(
        target=_torch_clean_build_reconfigure_failed,
        args=(
            project_directory,
            build_directory,
            False,
            dirty_file,
        ),
    )

    p.start()
    p.join()
    assert p.exitcode == 0

    build_directory.mkdir(parents=True, exist_ok=True)
    dirty_file.touch()

    (project_directory / "CMakeLists.txt").touch()

    p = multiprocessing.get_context("spawn").Process(
        target=_torch_clean_build_reconfigure_failed,
        args=(
            project_directory,
            build_directory,
            True,
            dirty_file,
        ),
    )

    p.start()
    p.join()
    assert p.exitcode == 0

    p = multiprocessing.get_context("spawn").Process(
        target=_torch_clean_build_reconfigure_failed,
        args=(
            project_directory,
            build_directory,
            False,
            dirty_file,
        ),
    )

    p.start()
    p.join()
    assert p.exitcode == 0


def test_torch_fallback_build_directory(shared_datadir: pathlib.Path) -> None:
    project_directory = shared_datadir / "torch_cpu"

    charonload.module_config["test_torch_fallback_build_directory"] = charonload.Config(
        project_directory,
        stubs_directory=VSCODE_STUBS_DIRECTORY,
    )

    # Clean up potential previous test runs
    build_directory = charonload.module_config["test_torch_fallback_build_directory"].full_build_directory
    shutil.rmtree(build_directory, ignore_errors=True)

    import test_torch_fallback_build_directory as test_torch

    t_input = torch.randint(0, 10, size=(3, 3, 3), dtype=torch.float, device="cpu")
    t_output = test_torch.two_times(t_input)

    assert t_output.device == t_input.device
    assert t_output.shape == t_input.shape
    assert torch.equal(t_output, 2 * t_input)


def test_torch_cmake_options(shared_datadir: pathlib.Path, tmp_path: pathlib.Path) -> None:
    project_directory = shared_datadir / "torch_cmake_options"
    build_directory = tmp_path / "build"

    charonload.module_config["test_torch_cmake_options"] = charonload.Config(
        project_directory,
        build_directory,
        cmake_options={
            "TEST_OPTION": "some_value",
        },
        stubs_directory=VSCODE_STUBS_DIRECTORY,
    )

    import test_torch_cmake_options as test_torch

    t_input = torch.randint(0, 10, size=(3, 3, 3), dtype=torch.float, device="cpu")
    t_output = test_torch.two_times(t_input)

    assert t_output.device == t_input.device
    assert t_output.shape == t_input.shape
    assert torch.equal(t_output, 2 * t_input)


def _torch_cmake_options_changed(
    shared_datadir: pathlib.Path, tmp_path: pathlib.Path, module_name: str, value: int
) -> None:
    project_directory = shared_datadir / "torch_cmake_options_changed"
    build_directory = tmp_path / "build"

    charonload.module_config[module_name] = charonload.Config(
        project_directory,
        build_directory,
        cmake_options={
            "TEST_OPTION": str(value),
        },
        stubs_directory=VSCODE_STUBS_DIRECTORY,
    )

    test_torch = importlib.import_module(module_name)

    t_input = torch.randint(0, 10, size=(3, 3, 3), dtype=torch.float, device="cpu")
    t_output = test_torch.two_times(t_input)

    assert t_output.device == t_input.device
    assert t_output.shape == t_input.shape
    assert torch.equal(t_output, value * t_input)


def test_torch_cmake_options_changed(shared_datadir: pathlib.Path, tmp_path: pathlib.Path) -> None:
    p = multiprocessing.get_context("spawn").Process(
        target=_torch_cmake_options_changed,
        args=(
            shared_datadir,
            tmp_path,
            "test_torch_cmake_options_changed",
            2,
        ),
    )

    p.start()
    p.join()
    assert p.exitcode == 0

    p = multiprocessing.get_context("spawn").Process(
        target=_torch_cmake_options_changed,
        args=(
            shared_datadir,
            tmp_path,
            "test_torch_cmake_options_changed",
            3,
        ),
    )

    p.start()
    p.join()
    assert p.exitcode == 0


def test_torch_non_verbose(shared_datadir: pathlib.Path, tmp_path: pathlib.Path) -> None:
    project_directory = shared_datadir / "torch_cpu"
    build_directory = tmp_path / "build"

    charonload.module_config["test_torch_non_verbose"] = charonload.Config(
        project_directory,
        build_directory,
        stubs_directory=VSCODE_STUBS_DIRECTORY,
        verbose=False,
    )

    with contextlib.redirect_stdout(io.StringIO()) as f:
        import test_torch_non_verbose as test_torch

    expected_printed_lines = 2
    assert len(f.getvalue().splitlines()) == expected_printed_lines

    t_input = torch.randint(0, 10, size=(3, 3, 3), dtype=torch.float, device="cpu")
    t_output = test_torch.two_times(t_input)

    assert t_output.device == t_input.device
    assert t_output.shape == t_input.shape
    assert torch.equal(t_output, 2 * t_input)


def test_torch_verbose(shared_datadir: pathlib.Path, tmp_path: pathlib.Path) -> None:
    project_directory = shared_datadir / "torch_cpu"
    build_directory = tmp_path / "build"

    charonload.module_config["test_torch_verbose"] = charonload.Config(
        project_directory,
        build_directory,
        stubs_directory=VSCODE_STUBS_DIRECTORY,
        verbose=True,
    )

    with contextlib.redirect_stdout(io.StringIO()) as f:
        import test_torch_verbose as test_torch

    expected_minimum_printed_lines = 10
    assert len(f.getvalue().splitlines()) > expected_minimum_printed_lines

    t_input = torch.randint(0, 10, size=(3, 3, 3), dtype=torch.float, device="cpu")
    t_output = test_torch.two_times(t_input)

    assert t_output.device == t_input.device
    assert t_output.shape == t_input.shape
    assert torch.equal(t_output, 2 * t_input)


def test_torch_verbose_tty(
    shared_datadir: pathlib.Path, tmp_path: pathlib.Path, mocker: pytest_mock.MockerFixture
) -> None:
    mocker.patch("sys.stdout.isatty", return_value=True)

    project_directory = shared_datadir / "torch_cpu"
    build_directory = tmp_path / "build"

    charonload.module_config["test_torch_verbose_tty"] = charonload.Config(
        project_directory,
        build_directory,
        stubs_directory=VSCODE_STUBS_DIRECTORY,
        verbose=True,
    )

    import test_torch_verbose_tty as test_torch

    t_input = torch.randint(0, 10, size=(3, 3, 3), dtype=torch.float, device="cpu")
    t_output = test_torch.two_times(t_input)

    assert t_output.device == t_input.device
    assert t_output.shape == t_input.shape
    assert torch.equal(t_output, 2 * t_input)


def _concurrent_process_fork_import(_: Any) -> None:  # noqa: ANN401
    import concurrent_process_fork_import as test_torch

    t_input = torch.randint(0, 10, size=(3, 3, 3), dtype=torch.float, device="cpu")
    t_output = test_torch.two_times(t_input)

    assert t_output.device == t_input.device
    assert t_output.shape == t_input.shape
    assert torch.equal(t_output, 2 * t_input)


@pytest.mark.skipif(platform.system() != "Linux", reason="fork only fully supported on Linux")
def test_concurrent_process_fork_import(shared_datadir: pathlib.Path, tmp_path: pathlib.Path) -> None:
    project_directory = shared_datadir / "torch_cpu"
    build_directory = tmp_path / "build"

    charonload.module_config["concurrent_process_fork_import"] = charonload.Config(
        project_directory,
        build_directory,
        stubs_directory=VSCODE_STUBS_DIRECTORY,
    )

    num = 5
    jobs = [
        multiprocessing.get_context("fork").Process(target=_concurrent_process_fork_import, args=(i,))
        for i in range(num)
    ]

    for j in jobs:
        j.start()

    for j in jobs:
        j.join()
        assert j.exitcode == 0


def _concurrent_process_spawn_import(
    _: Any, shared_datadir: pathlib.Path, tmp_path: pathlib.Path  # noqa: ANN401
) -> None:
    project_directory = shared_datadir / "torch_cpu"
    build_directory = tmp_path / "build"

    charonload.module_config["concurrent_process_spawn_import"] = charonload.Config(
        project_directory,
        build_directory,
        stubs_directory=VSCODE_STUBS_DIRECTORY,
    )

    import concurrent_process_spawn_import as test_torch

    t_input = torch.randint(0, 10, size=(3, 3, 3), dtype=torch.float, device="cpu")
    t_output = test_torch.two_times(t_input)

    assert t_output.device == t_input.device
    assert t_output.shape == t_input.shape
    assert torch.equal(t_output, 2 * t_input)


def test_concurrent_process_spawn_import(shared_datadir: pathlib.Path, tmp_path: pathlib.Path) -> None:
    num = 5
    jobs = [
        multiprocessing.get_context("spawn").Process(
            target=_concurrent_process_spawn_import,
            args=(
                i,
                shared_datadir,
                tmp_path,
            ),
        )
        for i in range(num)
    ]

    for j in jobs:
        j.start()

    for j in jobs:
        j.join()
        assert j.exitcode == 0


def _concurrent_thread_import(_: Any) -> None:  # noqa: ANN401
    import concurrent_thread_import as test_torch

    t_input = torch.randint(0, 10, size=(3, 3, 3), dtype=torch.float, device="cpu")
    t_output = test_torch.two_times(t_input)

    assert t_output.device == t_input.device
    assert t_output.shape == t_input.shape
    assert torch.equal(t_output, 2 * t_input)


def test_concurrent_thread_import(shared_datadir: pathlib.Path, tmp_path: pathlib.Path) -> None:
    project_directory = shared_datadir / "torch_cpu"
    build_directory = tmp_path / "build"

    charonload.module_config["concurrent_thread_import"] = charonload.Config(
        project_directory,
        build_directory,
        stubs_directory=VSCODE_STUBS_DIRECTORY,
    )

    num = 5
    jobs = [threading.Thread(target=_concurrent_thread_import, args=(i,)) for i in range(num)]

    for j in jobs:
        j.start()

    for j in jobs:
        j.join()


def test_torch_no_stubs(shared_datadir: pathlib.Path, tmp_path: pathlib.Path) -> None:
    project_directory = shared_datadir / "torch_cpu"
    build_directory = tmp_path / "build"

    charonload.module_config["test_torch_no_stubs"] = charonload.Config(
        project_directory,
        build_directory,
        stubs_directory=None,
    )

    import test_torch_no_stubs as test_torch

    t_input = torch.randint(0, 10, size=(3, 3, 3), dtype=torch.float, device="cpu")
    t_output = test_torch.two_times(t_input)

    assert t_output.device == t_input.device
    assert t_output.shape == t_input.shape
    assert torch.equal(t_output, 2 * t_input)


def test_wrong_config_type() -> None:
    charonload.module_config["wrong_config_type"] = "this_is_not_a_Config_instance"  # type: ignore[assignment]

    with pytest.raises(TypeError) as exc_info:
        import wrong_config_type  # noqa: F401

    assert exc_info.type is TypeError


def test_torch_broken_cmake(shared_datadir: pathlib.Path, tmp_path: pathlib.Path) -> None:
    project_directory = shared_datadir / "torch_broken_cmake"
    build_directory = tmp_path / "build"

    charonload.module_config["torch_broken_cmake"] = charonload.Config(
        project_directory,
        build_directory,
    )

    with pytest.raises(charonload.JITCompileError) as exc_info:
        import torch_broken_cmake  # noqa: F401

    assert exc_info.type is charonload.CMakeConfigureError


def test_torch_broken_cmake_try_twice(shared_datadir: pathlib.Path, tmp_path: pathlib.Path) -> None:
    project_directory = shared_datadir / "torch_broken_cmake"
    build_directory = tmp_path / "build"

    charonload.module_config["test_torch_broken_cmake_try_twice"] = charonload.Config(
        project_directory,
        build_directory,
    )

    with pytest.raises(charonload.JITCompileError) as exc_info:
        import test_torch_broken_cmake_try_twice

    assert exc_info.type is charonload.CMakeConfigureError

    with pytest.raises(charonload.JITCompileError) as exc_info:
        import test_torch_broken_cmake_try_twice  # noqa: F401

    assert exc_info.type is charonload.CMakeConfigureError


def test_torch_broken_cpp_code(shared_datadir: pathlib.Path, tmp_path: pathlib.Path) -> None:
    project_directory = shared_datadir / "torch_broken_cpp_code"
    build_directory = tmp_path / "build"

    charonload.module_config["test_torch_broken_cpp_code"] = charonload.Config(
        project_directory,
        build_directory,
    )

    with pytest.raises(charonload.JITCompileError) as exc_info:
        import test_torch_broken_cpp_code  # noqa: F401

    assert exc_info.type is charonload.BuildError


def test_torch_broken_cpp_code_try_twice(shared_datadir: pathlib.Path, tmp_path: pathlib.Path) -> None:
    project_directory = shared_datadir / "torch_broken_cpp_code"
    build_directory = tmp_path / "build"

    charonload.module_config["test_torch_broken_cpp_code_try_twice"] = charonload.Config(
        project_directory,
        build_directory,
    )

    with pytest.raises(charonload.JITCompileError) as exc_info:
        import test_torch_broken_cpp_code_try_twice

    assert exc_info.type is charonload.BuildError

    with pytest.raises(charonload.JITCompileError) as exc_info:
        import test_torch_broken_cpp_code_try_twice  # noqa: F401

    assert exc_info.type is charonload.BuildError


def test_torch_broken_stubs(shared_datadir: pathlib.Path, tmp_path: pathlib.Path) -> None:
    project_directory = shared_datadir / "torch_broken_stubs"
    build_directory = tmp_path / "build"

    charonload.module_config["test_torch_broken_stubs"] = charonload.Config(
        project_directory,
        build_directory,
        stubs_directory=VSCODE_STUBS_DIRECTORY,
    )

    with pytest.raises(charonload.JITCompileError) as exc_info:
        import test_torch_broken_stubs  # noqa: F401

    assert exc_info.type is charonload.StubGenerationError


def _torch_skip_step_broken_stubs(
    shared_datadir: pathlib.Path, tmp_path: pathlib.Path, stubs_directory: pathlib.Path | str | None
) -> None:
    project_directory = shared_datadir / "torch_broken_stubs"
    build_directory = tmp_path / "build"

    charonload.module_config["test_torch_skip_step_broken_stubs"] = charonload.Config(
        project_directory,
        build_directory,
        stubs_directory=stubs_directory,
    )

    if stubs_directory is None:
        test_torch = importlib.import_module("test_torch_skip_step_broken_stubs")

        t_input = torch.randint(0, 10, size=(3, 3, 3), dtype=torch.float, device="cpu")
        t_output = test_torch.two_times(t_input)

        assert t_output.device == t_input.device
        assert t_output.shape == t_input.shape
        assert torch.equal(t_output, 2 * t_input)
    else:
        with pytest.raises(charonload.JITCompileError) as exc_info:
            test_torch = importlib.import_module("test_torch_skip_step_broken_stubs")

        assert exc_info.type is charonload.StubGenerationError


def test_torch_skip_step_broken_stubs(shared_datadir: pathlib.Path, tmp_path: pathlib.Path) -> None:
    p = multiprocessing.get_context("spawn").Process(
        target=_torch_skip_step_broken_stubs,
        args=(
            shared_datadir,
            tmp_path,
            VSCODE_STUBS_DIRECTORY,
        ),
    )

    p.start()
    p.join()
    assert p.exitcode == 0

    p = multiprocessing.get_context("spawn").Process(
        target=_torch_skip_step_broken_stubs,
        args=(
            shared_datadir,
            tmp_path,
            None,
        ),
    )

    p.start()
    p.join()
    assert p.exitcode == 0


def test_torch_accept_broken_stubs(shared_datadir: pathlib.Path, tmp_path: pathlib.Path) -> None:
    project_directory = shared_datadir / "torch_broken_stubs"
    build_directory = tmp_path / "build"

    charonload.module_config["test_torch_accept_broken_stubs"] = charonload.Config(
        project_directory,
        build_directory,
        stubs_directory=VSCODE_STUBS_DIRECTORY,
        stubs_invalid_ok=True,
    )

    import test_torch_accept_broken_stubs as test_torch

    t_input = torch.randint(0, 10, size=(3, 3, 3), dtype=torch.float, device="cpu")
    t_output = test_torch.two_times(t_input)

    assert t_output.device == t_input.device
    assert t_output.shape == t_input.shape
    assert torch.equal(t_output, 2 * t_input)


def test_torch_binding_target_wrong_name(shared_datadir: pathlib.Path, tmp_path: pathlib.Path) -> None:
    project_directory = shared_datadir / "torch_binding_target_wrong_name"
    build_directory = tmp_path / "build"

    charonload.module_config["torch_binding_target_wrong_name"] = charonload.Config(
        project_directory,
        build_directory,
    )

    with pytest.raises(charonload.JITCompileError) as exc_info:
        import torch_binding_target_wrong_name  # noqa: F401

    assert exc_info.type is charonload.CMakeConfigureError


def test_torch_binding_target_colliding(shared_datadir: pathlib.Path, tmp_path: pathlib.Path) -> None:
    project_directory = shared_datadir / "torch_binding_target_colliding"
    build_directory = tmp_path / "build"

    charonload.module_config["torch_binding_target_colliding"] = charonload.Config(
        project_directory,
        build_directory,
    )

    with pytest.raises(charonload.JITCompileError) as exc_info:
        import torch_binding_target_colliding  # noqa: F401

    assert exc_info.type is charonload.CMakeConfigureError


def test_torch_binding_target_missing(shared_datadir: pathlib.Path, tmp_path: pathlib.Path) -> None:
    project_directory = shared_datadir / "torch_binding_target_missing"
    build_directory = tmp_path / "build"

    charonload.module_config["torch_binding_target_missing"] = charonload.Config(
        project_directory,
        build_directory,
    )

    with pytest.raises(charonload.JITCompileError) as exc_info:
        import torch_binding_target_missing  # noqa: F401

    assert exc_info.type is charonload.CMakeConfigureError


def test_dependent_tool_not_found(
    shared_datadir: pathlib.Path, tmp_path: pathlib.Path, mocker: pytest_mock.MockerFixture
) -> None:
    mocker.patch("shutil.which", return_value=None)

    project_directory = shared_datadir / "torch_cpu"
    build_directory = tmp_path / "build"

    charonload.module_config["dependent_tool_not_found"] = charonload.Config(
        project_directory,
        build_directory,
    )

    with pytest.raises(charonload.CommandNotFoundError) as exc_info:
        import dependent_tool_not_found  # noqa: F401

    assert exc_info.type is charonload.CommandNotFoundError


def _find_imported_modules(module: types.ModuleType, output_module_list: list[types.ModuleType]) -> None:
    for attribute_name in dir(module):
        try:
            attribute = getattr(module, attribute_name)
            if isinstance(attribute, types.ModuleType) and attribute not in output_module_list:
                output_module_list.append(attribute)
                _find_imported_modules(attribute, output_module_list)
        except ImportError:  # noqa: PERF203
            # Ignore modules that cannot be imported, e.g. "_gdbm" from "six" package on Windows
            pass


def _find_all_charonload_modules() -> list[types.ModuleType]:
    imported_modules: list[types.ModuleType] = []
    _find_imported_modules(charonload, imported_modules)

    charonload_modules = [charonload]
    charonload_modules.extend([m for m in imported_modules if m.__name__.startswith("charonload")])
    return sorted(charonload_modules, key=lambda m: m.__name__.count("."), reverse=True)


def _get_ordered_charonload_modules() -> list[types.ModuleType]:
    return [
        sys.modules[name]
        for name in [
            "charonload",
            "charonload._finder",
            "charonload._persistence",
            "charonload._runner",
            "charonload._config",
            "charonload._errors",
            "charonload._compat",
            "charonload._compat.hashlib",
            # "charonload._compat.typing",  # Only imported for TYPE_CHECKING  # noqa: ERA001
        ]
    ]


def _charonload_reload_import(shared_datadir: pathlib.Path, tmp_path: pathlib.Path) -> None:
    original_num_sys_meta_paths = len(sys.meta_path)

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="torch.distributed.reduce_op is deprecated")

        assert set(_get_ordered_charonload_modules()) == set(_find_all_charonload_modules())
        for m in reversed(_get_ordered_charonload_modules()):
            importlib.reload(m)

    reloaded_num_sys_meta_paths = len(sys.meta_path)
    assert reloaded_num_sys_meta_paths == original_num_sys_meta_paths

    project_directory = shared_datadir / "torch_cpu"
    build_directory = tmp_path / "build"

    charonload.module_config["charonload_reload_import"] = charonload.Config(
        project_directory,
        build_directory,
        stubs_directory=VSCODE_STUBS_DIRECTORY,
    )

    import charonload_reload_import as test_torch

    t_input = torch.randint(0, 10, size=(3, 3, 3), dtype=torch.float, device="cpu")
    t_output = test_torch.two_times(t_input)

    assert t_output.device == t_input.device
    assert t_output.shape == t_input.shape
    assert torch.equal(t_output, 2 * t_input)


def test_charonload_reload_import(shared_datadir: pathlib.Path, tmp_path: pathlib.Path) -> None:
    p = multiprocessing.get_context("spawn").Process(
        target=_charonload_reload_import,
        args=(
            shared_datadir,
            tmp_path,
        ),
    )

    p.start()
    p.join()
    assert p.exitcode == 0


def test_charonload_version(shared_datadir: pathlib.Path, tmp_path: pathlib.Path) -> None:
    project_directory = shared_datadir / "charonload_version"
    build_directory = tmp_path / "build"

    charonload.module_config["charonload_version"] = charonload.Config(
        project_directory,
        build_directory,
        stubs_directory=VSCODE_STUBS_DIRECTORY,
    )

    import charonload_version  # noqa: F401

    with (build_directory / "charonload_version.txt").open("r") as f:
        charonload_cmake_version = f.read()

    charonload_python_version = charonload.__version__

    assert charonload_cmake_version == charonload_python_version
