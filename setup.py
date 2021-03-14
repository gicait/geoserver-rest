import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="geoserver-rest",
    version="1.5.3",
    author="Tek Kshetri",
    author_email="iamtekson@gmail.com",
    description="Package for GeoServer rest API",
    py_modules=['geoserver-rest-python'],
    # package_dir={'':'src'},
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/iamtekson/geoserver-rest-python",
    packages=['geo'],
    keywords=['geoserver-rest-python', 'geoserver rest', 'python geoserver', 'geoserver api',
              'api', 'rest geoserver', 'python', 'geoserver python', 'geoserver rest'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'pycurl',
        'seaborn',
        'gdal',
        'psycopg2',
    ],
    python_requires='>=3.6',
)
