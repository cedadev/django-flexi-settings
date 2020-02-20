# django-flexi-settings

Package that allows flexible settings configuration for Django projects.

## Installation

Install directly from GitHub:

```sh
pip install git+https://github.com/cedadev/django-flexi-settings.git
```

## Usage

### Using the include functions

`django-flexi-settings` provides two functions that can be used to include settings
from other files in your `settings.py`:

```python
# my_site/settings.py

INSTALLED_APPS = ['app1', '...']

# ... Other settings ...

# Use flexible settings utilities to include settings from other files
from flexible_settings import include, include_dir

# Include a file with one of the supported extensions
# Python files DO NOT have to be on the PYTHONPATH
include('/path/to/pythonfile.py')
include('/path/to/pythonfile.conf')  # This is also treated as python
include('/path/to/yamlfile.yaml')
include('/path/to/jsonfile.json')

# Or include a whole directory
# The files are included in lexicographical order, so to control ordering you
# might name the files 01-somesettings.py, 02-moresettings.yaml, etc.
include_dir('/path/to/config/directory')
```

If the included files are Python, they can modify existing variables:

```python
# /path/to/pythonfile.py

INSTALLED_APPS += ['extra_app1', 'extra_app2']
```

For YAML and JSON files, keys are normalised and dictionaries are merged in the
resulting settings, e.g. for these two YAML files:

```yaml
# /path/to/yamlfile1.yaml
SETTING_1: setting1
DICT_SETTING:
  KEY1: value1
  KEY2: value2

# /path/to/yamlfile2.yaml
dictSetting:
  key1: overridden
  key3: value3
```

the resulting settings would be:

```python
SETTING_1 = "setting1"
DICT_SETTING = {
    "KEY1": "overridden",
    "KEY2": "value2",
    "KEY3": "value3"
}
```

### Using the settings module

In the case where your settings are defined in a file that isn't on the `PYTHONPATH`,
`django-flexi-settings` provides a module that can be used as the `DJANGO_SETTINGS_MODULE`.
This module respects the value of an environment variable, `DJANGO_FLEXI_SETTINGS_ROOT`,
that determines the settings file to include. It defaults to `/etc/django/settings.py`.

```bash
export DJANGO_FLEXI_SETTINGS_ROOT="/etc/myapp/settings.py"
export DJANGO_SETTINGS_MODULE="flexi_settings.settings"
```

If the file specified in `DJANGO_FLEXI_SETTINGS_ROOT` is a Python file, it can then use the
`include` and `include_dir` functions to include other settings if desired. For example,
the following file could be used as `DJANGO_FLEXI_SETTINGS_ROOT` to allow drop-in changes to
settings by placing additional files in a `settings.d` directory:

```python
from pathlib import Path
from flexi_settings import include_dir
include_dir(Path(__file__).resolve().parent / 'settings.d')
```

This makes for a very flexible configuration system for Django that is not application-specific.

## Adding additional loaders

`django-flexi-settings` makes adding new loaders for additional file types very easy.

A loader in `django-flexi-settings` is just a function that takes a file path and a settings
dictionary and modifies the settings dictionary in a way consistent with the specified file.
**Note that the existing dictionary is modified, not a new dictionary returned.** Please refer
to the built-in loaders.

To declare the extensions for which the additional loader is valid, add an `extensions` property
to the loader function:

```python
def load_ini(path, settings):
    # ... Do something with path and settings ...

load_ini.extensions = { '.ini' }
```

To register the loader with `django-flexi-settings`, use the entry point:

```python
# mypackage/setup.py

from setuptools import setup

if __name__ == "__main__":
    setup(
        # ... Other setup, e.g. name, requires
        entry_points = {
            'flexi_settings.loaders': [
                'ini = mypackage.flexi_settings:load_ini',
            ]
        }
    )
```
