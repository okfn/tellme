from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from setuptools import setup, find_packages


setup(
    name='Reporter',
    version='0.1.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'PyYAML>=3.11',
        'dataset>=0.5.5'
    ]
)
