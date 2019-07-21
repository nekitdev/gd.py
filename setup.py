from setuptools import setup
import re

requirements = []
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

version = ''
with open('gd/__init__.py') as f:
    ver = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE)
    if ver is not None:
        version = ver.group(1)

if not version:
    raise RuntimeError('version is not set')

readme = ''
with open('README.rst') as f:
    readme = f.read()

extras_require = {  # gotta work on that soon
    'docs': [
        'sphinx',
        'sphinxcontrib_trio',
        'sphinxcontrib-websupport'
    ]
}

setup(
    name = 'gd.py',
    author = 'NeKitDSS',
    url = 'https://github.com/NeKitDSS/gd.py',
    project_urls = {
        "Documentation": "https://gdpy.readthedocs.io/en/latest",
        "Issue tracker": "https://github.com/NeKitDSS/gd.py/issues",
    },
    version = version,
    packages = ['gd', 'gd.utils', 'gd.utils.crypto', 'gd.graphics'],
    license = 'MIT',
    description = 'A Geometry Dash API wrapper for Python',
    long_description = readme,
    long_description_content_type="text/x-rst",
    include_package_data = True,
    install_requires = requirements,
    extras_require = extras_require,
    python_requires = '>=3.5.3',
    classifiers = [
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Natural Language :: English',
        'Operating System :: OS Independent'  # needs check
    ]
)
