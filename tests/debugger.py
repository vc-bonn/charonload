import pathlib
import tempfile

import torch

import charonload

VSCODE_STUBS_DIRECTORY = pathlib.Path(__file__).parents[1] / "typings"


def main() -> None:
    project_directory = pathlib.Path(__file__).parent / "data" / "debugger_cpp"
    build_directory = pathlib.Path(tempfile.gettempdir()) / "charonload_debugger_cpp_build"

    charonload.module_config["debugger_cpp"] = charonload.Config(
        project_directory,
        build_directory,
        stubs_directory=VSCODE_STUBS_DIRECTORY,
    )

    import debugger_cpp

    t_input = torch.randint(0, 10, size=(3, 3, 3), dtype=torch.float, device="cpu")

    # Set a breakpoint in data/debugger/three_times_cpu.cpp in order to make the debugger stop at some point.
    t_output = debugger_cpp.three_times(t_input)

    assert t_output.device == t_input.device
    assert t_output.shape == t_input.shape
    assert torch.equal(t_output, 3 * t_input)


if __name__ == "__main__":
    main()
