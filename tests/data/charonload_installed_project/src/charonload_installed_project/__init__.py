import pathlib

import charonload

PROJECT_ROOT_DIRECTORY = pathlib.Path(__file__).parents[2]

VSCODE_STUBS_DIRECTORY = PROJECT_ROOT_DIRECTORY / "typings"


charonload.module_config["_c_charonload_installed_project"] = charonload.Config(
    pathlib.Path(__file__).parent / "_C",
    build_directory=PROJECT_ROOT_DIRECTORY,  # Intentionally do in-source build
    stubs_directory=VSCODE_STUBS_DIRECTORY,  # Common in-source typings directory for VS Code
    verbose=True,
)


from _c_charonload_installed_project import two_times  # noqa: E402, F401
