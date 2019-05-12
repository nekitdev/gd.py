from setuptools import setup

long_desc = 'A Geometry Dash API Wrapper Written In Python, Supports Everything About Geometry Dash... :)'

setup(
    name = 'gd.py',
    packages = ['gd', 'gd.utils', 'gd.utils.crypto'],
    version = '0.0.4.0',
    description = 'A Geometry Dash API wrapper for Python',
    long_description = long_desc,
    author = 'NeKitDSS',
    author_email = 'nekitguypro@gmail.com',
    url = 'https://github.com/NeKitDSS/gd.py',
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 2 - Pre-Alpha",
        "Natural Language :: English",
    ]
)
