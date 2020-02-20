"""
Module that can be used as the DJANGO_SETTINGS_MODULE to import settings
from a file. That file can then include other files as it chooses.
"""

import os

from .loaders import include

# Include the specified root settings file
settings_root = os.environ.get('DJANGO_FLEXI_SETTINGS_ROOT', '/etc/django/settings.py')
include(settings_root)
