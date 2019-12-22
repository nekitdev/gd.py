import os
import re
import pathlib
import sys
from setuptools import Extension, setup

root = pathlib.Path(__file__).parent

requirements = (root / 'requirements.txt').read_text('utf-8').splitlines()

txt = (root / 'gd' / '__init__.py').read_text('utf-8')

try:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', txt, re.MULTILINE).group(1)

except AttributeError:
    raise RuntimeError('Failed to find version.') from None

readme = (root / 'README.rst').read_text('utf-8')

extras_require = {
    'console': [
        'aioconsole'
    ],
    'dev': [
        'aioconsole',
        'coverage',
        'pytest-asyncio'
    ],
    'docs': [
        'sphinx',
        'sphinxcontrib_trio',
        'sphinxcontrib-websupport'
    ]
}

NO_EXTENSIONS = bool(os.environ.get('GD_NO_EXTENSIONS'))

if sys.implementation.name.lower() != 'cpython':
    NO_EXTENSIONS = True


class OptionalExtension(Extension):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.optional = True


extension_list = [
    OptionalExtension(name='_gd', sources=['gd/src/_gd.pyx'], language='c++')
]

try:
    from Cython.Build import cythonize
    extensions = cythonize(extension_list)
except ImportError:
    NO_EXTENSIONS = True

args = dict(
    name='gd.py',
    author='NeKitDS',
    author_email='gdpy13@gmail.com',
    url='https://github.com/NeKitDS/gd.py',
    project_urls={
        "Documentation": "https://gdpy.readthedocs.io/en/latest",
        "Issue tracker": "https://github.com/NeKitDS/gd.py/issues",
    },
    version=version,
    packages=[
        'gd', 'gd.utils', 'gd.utils.crypto',
        'gd.events', 'gd.api', 'gd.src'
    ],
    license='MIT',
    description='A Geometry Dash API wrapper for Python',
    long_description=readme,
    long_description_content_type="text/x-rst",
    include_package_data=True,
    install_requires=requirements,
    extras_require=extras_require,
    python_requires='>=3.5.3',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Natural Language :: English',
        'Operating System :: OS Independent'
    ],
    entry_points={
        'console': [
            'gd = gd.__main__:main',
        ],
    }
)

if NO_EXTENSIONS:
    setup(**args)

else:
    setup(ext_modules=extensions, **args)
