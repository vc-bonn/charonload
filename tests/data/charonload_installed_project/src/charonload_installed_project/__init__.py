import pathlib

import charonload

PROJECT_ROOT_DIRECTORY = pathlib.Path(__file__).parent


charonload.module_config["_c_charonload_installed_project"] = charonload.Config(
    pathlib.Path(__file__).parent / "_C",
    build_directory=PROJECT_ROOT_DIRECTORY,  # Intentionally do in-source build
    stubs_directory=PROJECT_ROOT_DIRECTORY,  # Similar to common in-source typings directory for VS Code
    verbose=True,
)


from _c_charonload_installed_project import two_times  # noqa: E402, F401
