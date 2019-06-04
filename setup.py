from setuptools import setup

long_desc = 'A Geometry Dash API Wrapper Written In Python, Supports Everything About Geometry Dash... Work In Progress! :)'

setup(
    name = 'gd.py',
    packages = ['gd', 'gd.utils', 'gd.utils.crypto', 'gd.utils.graphics'],
    version = '0.0.7',
    description = 'A Geometry Dash API wrapper for Python',
    long_description = long_desc,
    author = 'NeKitDSS',
    author_email = 'nekitguypro@gmail.com',
    url = 'https://github.com/NeKitDSS/gd.py',
    license = 'MIT',
    include_package_data = True,
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 2 - Pre-Alpha",
        "Natural Language :: English",
    ]
)
