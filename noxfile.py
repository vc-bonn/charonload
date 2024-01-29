import pathlib
import shutil

import nox

nox.options.sessions = []


@nox.session
def format(session: nox.Session) -> None:  # noqa: A001
    """Format all source files to a consistent style."""
    sources = ["src", "tests", "docs", "tools", "noxfile.py"]
    session.run("isort", *sources, external=True)
    session.run(
        "docformatter",
        "--in-place",
        "--recursive",
        *sources,
        external=True,
    )
    session.run("black", *sources, external=True)

    sources_cpp = ["tests"]
    sources_cpp_files = []
    for s in sources_cpp:
        file = pathlib.Path(s)
        if file.is_file():
            sources_cpp_files.append(str(file))
        elif file.is_dir():
            for ext in [".h", ".hpp", ".cuh", ".c", ".cpp", ".cu"]:
                sources_cpp_files.extend([str(f) for f in sorted(file.rglob(f"*{ext}"))])
    session.run("clang-format", "-i", *sources_cpp_files, external=True)


DEFAULT_DOCS_OUTPUT_TYPE = "html"  # Replace by "dirhtml" for nice website URLs


@nox.session
def docs(session: nox.Session, output_type: str = DEFAULT_DOCS_OUTPUT_TYPE) -> None:
    """Build the documentation locally in the 'docs/build' directory."""
    # Cleanup
    shutil.rmtree("docs/_autosummary", ignore_errors=True)
    shutil.rmtree("build/docs/html", ignore_errors=True)

    # sphinx-build
    force_building = "-E"
    session.run(
        "sphinx-build",
        "-b",
        output_type,
        force_building,
        # "-j",
        # "auto",  # disable parallelization due to warning from moderncmakedomain extension
        "docs",
        "build/docs/html",
        external=True,
    )

    # Hints
    session.debug("\n\n--> Open 'build/docs/html/index.html' to view the documentation\n")


@nox.session
def docs_live(session: nox.Session) -> None:
    """Build the documentation locally and starts an interactive live session with automatic rebuilding on changes."""
    output_type = "html"  # Do not use "dirhtml" since auto-refresh will not work properly

    # Perform a complete clean build before starting to watch changes to avoid infinite loop
    docs(session, output_type=output_type)

    # sphinx-build
    force_building = "-E"
    watch_dirs_and_files = ["src", "README.md", "CHANGELOG.md"]
    watch_args = [v for pair in zip(["--watch"] * len(watch_dirs_and_files), watch_dirs_and_files) for v in pair]
    session.run(
        "sphinx-autobuild",
        "-b",
        output_type,
        force_building,
        # "-j",
        # "auto",  # disable parallelization due to warning from moderncmakedomain extension
        "--open-browser",
        *watch_args,
        "--re-ignore",
        "docs/_autosummary",
        "docs",
        "build/docs/html",
        external=True,
    )


@nox.session
def lint(session: nox.Session) -> None:
    """Check the source code with linters."""
    failed = False
    sources = ["src", "tests", "docs", "tools", "noxfile.py"]
    try:
        session.run("isort", "--check", *sources, external=True)
    except nox.command.CommandFailed:
        failed = True

    try:
        session.run(
            "docformatter",
            "--check",
            "--recursive",
            *sources,
            external=True,
        )
    except nox.command.CommandFailed:
        failed = True

    try:
        session.run("black", "--check", *sources, external=True)
    except nox.command.CommandFailed:
        failed = True

    try:
        sources_cpp = ["tests"]
        sources_cpp_files = []
        for s in sources_cpp:
            file = pathlib.Path(s)
            if file.is_file():
                sources_cpp_files.append(str(file))
            elif file.is_dir():
                for ext in [".h", ".hpp", ".cuh", ".c", ".cpp", ".cu"]:
                    sources_cpp_files.extend([str(f) for f in sorted(file.rglob(f"*{ext}"))])
        session.run("clang-format", "--dry-run", "--Werror", *sources_cpp_files, external=True)
    except nox.command.CommandFailed:
        failed = True

    try:
        session.run("ruff", *sources, external=True)
    except nox.command.CommandFailed:
        failed = True

    try:
        session.run("mypy", *sources, external=True)
    except nox.command.CommandFailed:
        failed = True

    try:
        text_sources = [*sources, "README.md", "CHANGELOG.md"]
        skip_sources = ["*pdf"]
        session.run(
            "codespell",
            "--check-filenames",
            "--check-hidden",
            *text_sources,
            "--skip",
            ",".join(skip_sources),
            external=True,
        )
    except nox.command.CommandFailed:
        failed = True

    try:
        session.run(
            "check-manifest",
            external=True,
        )
    except nox.command.CommandFailed:
        failed = True

    if failed:
        raise nox.command.CommandFailed


@nox.session
def tests(session: nox.Session) -> None:
    """Run the unit tests."""
    session.run("pytest", "tests", external=True)


@nox.session
def coverage(session: nox.Session) -> None:
    """Compute the code coverage based on the unit tests."""
    try:
        session.run(
            "pytest",
            "--cov=src/charonload",
            "--cov-report=term",
            "--cov-report=html:build/test_coverage/html",
            "tests",
            external=True,
        )
    finally:
        # Clean up remaining temporary files from pytest-cov that were not automatically cleaned up
        project_dir = pathlib.Path(__file__).parent
        for file in sorted(project_dir.rglob(".coverage.*")):
            file.unlink()


@nox.session
def clean(session: nox.Session) -> None:
    """Clean up the project directory from temporary files."""
    project_dir = pathlib.Path(__file__).parent

    cache_files_and_dirs = []
    cache_files_and_dirs.extend(sorted(project_dir.rglob("__pycache__/")))
    cache_files_and_dirs.extend(sorted(project_dir.rglob("*_cache/")))
    cache_files_and_dirs.append(project_dir / "build/")
    cache_files_and_dirs.append(project_dir / "dist/")
    cache_files_and_dirs.append(project_dir / "docs/reference/")
    cache_files_and_dirs.append(project_dir / "src/charonload.egg-info/")
    cache_files_and_dirs.append(project_dir / ".coverage")
    cache_files_and_dirs.append(project_dir / ".nox/")

    for file in cache_files_and_dirs:
        if file.is_file():
            file.unlink()
            session.debug(f"Removing file '{file}'")
        elif file.is_dir():
            shutil.rmtree(file, ignore_errors=True)
            session.debug(f"Removing directory '{file}'")
