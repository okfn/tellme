from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import io
from setuptools import setup, find_packages


dependencies = [
    'PyYAML>=3.11',
    'dataset>=0.5.5'
]

# with io.open('README.md', mode='r+t', encoding='utf-8') as stream:
#     readme = stream.read()

setup(
    name='tellme',
    description='A toolkit for generating user-facing reports from things happening in code.',
    long_description='A toolkit for generating user-facing reports from things happening in code.',
    version='0.1.5',
    author='Open Knowledge Foundation',
    author_email='info@okfn.org',
    url='http://okfn.org',
    license='MIT',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=dependencies,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
