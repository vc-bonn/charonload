import importlib.metadata


def _version() -> str:
    return importlib.metadata.version(__package__)
