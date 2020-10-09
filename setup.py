import re
import pathlib
import sys
from setuptools import setup  # type: ignore

try:
    from setuptools_rust import Binding, RustExtension  # type: ignore

except ImportError:
    import subprocess

    print("Can not find setuptools-rust. Attempting installation...")

    error = subprocess.call([sys.executable, "-m", "pip", "install", "setuptools-rust"])

    if error:
        print("Can not install setuptools-rust. Manual installation required.")
        raise SystemExit(error)

    else:
        from setuptools_rust import Binding, RustExtension  # type: ignore


root = pathlib.Path(__file__).parent

requirements = (root / "requirements.txt").read_text("utf-8").strip().splitlines()

text = (root / "gd" / "__init__.py").read_text("utf-8")

version_regex = re.compile(r"^__version__\s*=\s*[\"']([^\"']*)[\"']", re.MULTILINE)
version_match = version_regex.search(text)

if version_match is None:
    raise RuntimeError("Failed to find version.")


version = version_match.group(1)

readme = (root / "README.rst").read_text("utf-8")


extras_require = {
    "all": [],  # extended afterwards
    "crypto": ["pycryptodome"],
    "console": ["ipython"],
    "docs": ["sphinx", "sphinx_rtd_theme", "sphinxcontrib_websupport"],
    "image": ["Pillow"],
    "lint": ["black", "flake8"],
    "speedups": ["lxml"],
    "test": ["coverage", "pytest-asyncio"],
}

for requires in extras_require.values():
    extras_require["all"].extend(requires)  # type: ignore


setup(
    name="gd.py",
    author="nekitdev",
    author_email="gdpy13@gmail.com",
    url="https://github.com/nekitdev/gd.py",
    project_urls={
        "Documentation": "https://gdpy.readthedocs.io/en/latest",
        "Issue tracker": "https://github.com/nekitdev/gd.py/issues",
    },
    version=version,
    packages=["gd", "gd.events", "gd.api", "gd.image", "gd.memory", "gd.server"],
    license="MIT",
    description="Geometry Dash API Wrapper for Python",
    long_description=readme,
    long_description_content_type="text/x-rst",
    include_package_data=True,
    install_requires=requirements,
    extras_require=extras_require,
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
    ],
    rust_extensions=[
        RustExtension("_gd", "Cargo.toml", binding=Binding.PyO3, debug=False, optional=True)
    ],
    entry_points={"console_scripts": ["gd = gd.__main__:main"]},
    zip_safe=False,
)
