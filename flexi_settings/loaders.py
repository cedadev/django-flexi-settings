"""
Module defining built-in settings loaders.
"""

import importlib.util
import inspect
import pathlib
import pkg_resources
import re


class NoAvailableLoader(RuntimeError):
    """
    Raised when asked to load a file with an unknown extension.
    """
    def __init__(self, path):
        super().__init__(f'No available loader for {path}')


def get_available_loaders(entry_point = 'flexi_settings.loaders'):
    """
    Discovers the available loaders using the given entry point.
    """
    loaders = {}
    for entry_point in pkg_resources.iter_entry_points(entry_point):
        loader = entry_point.load()
        loaders.update({ ext: loader for ext in loader.extensions })
    return loaders


def include(path, settings = None):
    """
    Includes the given settings file and merges into the given settings.
    """
    # First, get the loader for the path
    path = pathlib.Path(path)
    try:
        loader = get_available_loaders()[path.suffix]
    except KeyError:
        raise NoAvailableLoader(path)
    # If no settings were given, use the globals of the caller
    if settings is None:
        settings = inspect.stack()[1].frame.f_globals
    loader(path, settings)


def include_dir(path, settings = None):
    """
    Includes each settings file from the given directory, in lexicographical order,
    and merges them into the given settings.
    """
    # If no settings were given, use the globals of the caller
    if settings is None:
        settings = inspect.stack()[1].frame.f_globals
    path = pathlib.Path(path)
    # Iterate the files in the directory and attempt to load each one
    for item in sorted(path.iterdir()):
        include(item, settings)


def load_python(path, settings):
    """
    Loads settings from a Python file and merges with the given settings.
    """
    with open(path, 'r') as fh:
        code = compile(fh.read(), path, mode = 'exec')
    # Override __file__ for the duration of the exec
    old_file = settings.get('__file__')
    settings['__file__'] = str(path)
    exec(code, settings)
    settings['__file__'] = old_file
load_python.extensions = { '.py', '.conf' }


def merge_settings(settings, overrides):
    """
    Deep-merge overrides into settings.
    """
    for key, value in overrides.items():
        if isinstance(value, dict):
            merge_settings(settings.setdefault(key, {}), value)
        else:
            settings[key] = value


def load_yaml(path, settings):
    """
    Loads settings from a YAML file and merges with the given settings.

    The YAML file should contain a dictionary, which is merged with the existing settings.

    The dictionary keys can be UPPER_SNAKE_CASE, lower_snake_case or camelCase, and are
    normalised to UPPER_SNAKE_CASE.
    """
    import yaml
    with open(path, 'r') as fh:
        overrides = yaml.safe_load(fh)
    merge_settings(settings, overrides)
load_yaml.extensions = { '.yaml', '.yml' }


def load_json(path, settings):
    """
    Loads settings from a JSON file and merges with the given settings.

    The JSON file should contain an object, which is merged with the existing settings.

    The object keys can be UPPER_SNAKE_CASE, lower_snake_case or camelCase, and are
    normalised to UPPER_SNAKE_CASE.
    """
    import json
    with open(path, 'r') as fh:
        overrides = json.load(fh)
    merge_settings(settings, overrides)
load_json.extensions = { '.json' }
