#!/usr/bin/env python3

import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.md')) as f:
    README = f.read()

if __name__ == "__main__":
    setup(
        name = 'django-flexi-settings',
        setup_requires = ['setuptools_scm'],
        use_scm_version = True,
        description = 'Utilities for flexible configuration for Django.',
        long_description = README,
        long_description_content_type = "text/markdown",
        classifiers = ["Programming Language :: Python"],
        author = 'Matt Pryor',
        author_email = 'matt.pryor@stfc.ac.uk',
        url = 'https://github.com/cedadev/django-flexi-settings',
        keywords = 'django flexible settings',
        packages = find_packages(),
        include_package_data = True,
        zip_safe = False,
        install_requires = ['pyyaml'],
        entry_points = {
            'flexi_settings.loaders': [
                'python = flexi_settings.loaders:load_python',
                'yaml = flexi_settings.loaders:load_yaml',
                'json = flexi_settings.loaders:load_json',
            ]
        }
    )
