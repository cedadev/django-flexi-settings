"""Module defining built-in settings loaders."""

import importlib.metadata
import inspect
import json
import pathlib


class NoAvailableLoader(RuntimeError):
    """Raise when asked to load a file with an unknown extension."""

    def __init__(self, path):
        super().__init__(f"No available loader for {path}")


def get_available_loaders(entry_point="flexi_settings.loaders"):
    """Discover the available loaders using the given entry point."""
    loaders = {}
    for point in importlib.metadata.entry_points().select(group=entry_point):
        loader = point.load()
        loaders.update({ext: loader for ext in loader.extensions})
    return loaders


def include(path, settings=None):
    """Include the given settings file and merge into the given settings."""
    # First, get the loader for the path
    path = pathlib.Path(path)
    try:
        loader = get_available_loaders()[path.suffix]
    except KeyError as err:
        raise NoAvailableLoader(path) from err
    # If no settings were given, use the globals of the caller
    if settings is None:
        settings = inspect.stack()[1].frame.f_globals
    loader(path, settings)


def include_dir(path, settings=None):
    """Include each settings file from the given directory, in lexicographical order.

    Then merge them into the given settings.
    """
    # If no settings were given, use the globals of the caller
    if settings is None:
        settings = inspect.stack()[1].frame.f_globals
    path = pathlib.Path(path)
    # Iterate the files in the directory and attempt to load each one
    for item in sorted(path.iterdir()):
        if item.is_dir():
            include_dir(item, settings)
        else:
            include(item, settings)


def load_python(path, settings):
    """Load settings from a Python file and merge with the given settings."""
    with open(path, "r", encoding="utf-8") as file:
        code = compile(file.read(), path, mode="exec")
    # Override __file__ for the duration of the exec
    old_file = settings.get("__file__")
    settings["__file__"] = str(path)
    exec(code, settings)
    settings["__file__"] = old_file


load_python.extensions = {".py", ".conf"}


def merge_settings(settings, overrides):
    """Deep-merge overrides into settings."""
    for key, value in overrides.items():
        if isinstance(value, dict):
            merge_settings(settings.setdefault(key, {}), value)
        else:
            settings[key] = value


def load_yaml(path, settings):
    """Load settings from a YAML file and merge with the given settings.

    The YAML file should contain a dictionary, which is merged with the
    existing settings.
    """
    import yaml

    with open(path, "r", encoding="utf-8") as file:
        overrides = yaml.safe_load(file)
    merge_settings(settings, overrides or {})


load_yaml.extensions = {".yaml", ".yml"}


def load_json(path, settings):
    """Load settings from a JSON file and merge with the given settings.

    The JSON file should contain an object, which is merged with the existing settings.
    """
    with open(path, "r", encoding="utf-8") as file:
        overrides = json.load(file)
    merge_settings(settings, overrides or {})


load_json.extensions = {".json"}
