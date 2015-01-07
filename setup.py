from setuptools import setup, find_packages


setup(
    name='Reporter',
    version='0.1.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'PyYAML==3.11'
    ]
)
