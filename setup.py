import os
from typing import Dict

from setuptools import setup

HERE = os.path.abspath(os.path.dirname(__file__))

about = dict()

with open(os.path.join(HERE, "geo", "__version__.py")) as f:
    exec(f.read(), about)

with open("README.md") as fh:
    long_description = fh.read()

setup(
    name="geoserver-rest",
    version=about["__version__"],
    author=about["__author__"],
    author_email=about["__email__"],
    description="Package for GeoServer rest API",
    py_modules=["geoserver-rest-python"],
    # package_dir={'':'src'},
    license="MIT License",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/iamtekson/geoserver-rest-python",
    packages=["geo"],
    keywords=[
        "geoserver-rest-python",
        "geoserver rest",
        "python geoserver",
        "geoserver api",
        "api",
        "rest geoserver",
        "python",
        "geoserver python",
        "geoserver rest",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "pygments",
        "requests",
        "seaborn",
        "gdal",
        "matplotlib",
        "xmltodict",
    ],
    extras_require={"dev": ["pytest", "black", "flake8", "sphinx>=1.7", "pre-commit"]},
    python_requires=">=3.6",
)
