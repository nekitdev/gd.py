from setuptools import Extension, setup
import re

requirements = []
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

with open('gd/__init__.py') as f:
    try:
        version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)
    except AttributeError:
        raise RuntimeError('Version is not set.') from None

readme = ''
with open('README.rst') as f:
    readme = f.read()

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

def create_ext():
    extensions = []

    accel_ext = Extension(name='_gd', sources=['gd/src/_gd.pyx'], language='c++')
    accel_ext.optional = True

    extension.append(accel_ext)

    # create Cython gd.api extension
    try:
        from Cython.Build import cythonize as cython_convert

    except ImportError:
        pass

    else:  # Cython imported, create an extension
        try:
            return cython_convert(extensions)
        except Exception:
            print('Failed to build Cython extensions.')

    return list()


setup(
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
    ext_modules=create_ext(),
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
