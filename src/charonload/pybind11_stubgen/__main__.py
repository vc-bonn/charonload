from __future__ import annotations

import argparse
import os
import pathlib
import platform
import sys

import pybind11_stubgen


def _make_importable(full_extension_path: pathlib.Path, windows_dll_directories: str) -> None:  # pragma: no cover
    full_extension_directory = str(full_extension_path.parent)
    if full_extension_directory not in sys.path:
        sys.path.append(full_extension_directory)

    if platform.system() == "Windows":
        dll_directory_list = windows_dll_directories.split(";")
        for d_str in dll_directory_list:
            d = pathlib.Path(d_str)
            if d.exists() and d.is_absolute() and d.is_dir():
                # No guard required here
                os.add_dll_directory(d)  # type: ignore[attr-defined]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--extension-path",
        required=True,
        type=pathlib.Path,
        help="the path to the extension",
    )
    parser.add_argument(
        "--windows-dll-directories",
        nargs="?",
        const="",
        default="",
        type=str,
        help="the list of DLL directories required for loading the extension",
    )
    additional_args, original_args = parser.parse_known_args(sys.argv[1:])

    _make_importable(additional_args.extension_path, additional_args.windows_dll_directories)

    # Patch list of command line argument globally as this list cannot directly be passed to pybind11-stubgen
    sys.argv = [sys.argv[0], *original_args]

    pybind11_stubgen.main()


if __name__ == "__main__":  # pragma: no cover
    main()
