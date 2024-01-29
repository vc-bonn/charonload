import pathlib
import subprocess

from charonload._compat import tomllib
from charonload._runner import _find_full_command_path


def main() -> None:
    project_root_dir = pathlib.Path(__file__).parents[1]

    with (project_root_dir / "pyproject.toml").open("rb") as f:
        pyproject = tomllib.load(f)

    cmake_dir = project_root_dir / "src" / "charonload" / "cmake"
    version = pyproject["project"]["version"]
    version_compatibility = "SameMinorVersion"

    create_cmake_version_file = pathlib.Path(__file__).parent / "create_cmake_version_file.cmake"

    subprocess.run(
        _find_full_command_path(
            [
                "cmake",
                f"-DCHARONLOAD_CMAKE_DIR={cmake_dir.as_posix()}",
                f"-DCHARONLOAD_VERSION={version}",
                f"-DCHARONLOAD_VERSION_COMPATIBILITY={version_compatibility}",
                "-P",
                f"{create_cmake_version_file.as_posix()}",
            ]
        ),
        check=True,
    )


if __name__ == "__main__":
    main()
