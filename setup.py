import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="geoserver-rest-python", 
    version="0.7.0",
    author="Tek Kshetri",
    author_email="iamtekson@gmail.com",
    description="Package for GeoServer rest API",
    py_modules=['geoserver-rest-python'],
    # package_dir={'':'src'},
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/iamtekson/geoserver-rest-python",
    packages=['geo'],
    keywords=['geoserver', 'geoserver-rest', 'geoserver-rest-python'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires = [
        'pycurl ~= 7.43',
        'seaborn ~= 0.10.1',
        'gdal',
        'psycopg2 ~=2.8',
    ],
    python_requires='>=3.6',
)