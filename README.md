# Python wrapper for GeoServer REST API

[![Downloads](https://pepy.tech/badge/geoserver-rest)](https://pepy.tech/project/geoserver-rest)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![flake8](https://img.shields.io/badge/linter-flake8-green)](https://flake8.pycqa.org/)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

## Full documentation

The documentation for this project is moved here: [https://geoserver-rest.readthedocs.io/](https://geoserver-rest.readthedocs.io/).

## Overview

The `geoserver-rest` package is useful for the management of geospatial data in [GeoServer](http://geoserver.org/). The package is useful for the creating, updating and deleting geoserver workspaces, stores, layers, and style files.

## Installation

```python
conda install -c conda-forge geoserver-rest
```

For the `pip` installation, check the [official documentation of geoserver-rest](https://geoserver-rest.readthedocs.io/en/latest/installation.html)

## Some examples

Please check the [https://geoserver-rest.readthedocs.io/](https://geoserver-rest.readthedocs.io/) for full documentation.

```python
# Import the library
from geo.Geoserver import Geoserver

# Initialize the library
geo = Geoserver('http://127.0.0.1:8080/geoserver', username='admin', password='geoserver')

# For creating workspace
geo.create_workspace(workspace='demo')

# For uploading raster data to the geoserver
geo.create_coveragestore(layer_name='layer1', path=r'path\to\raster\file.tif', workspace='demo')

# For creating postGIS connection and publish postGIS table
geo.create_featurestore(store_name='geo_data', workspace='demo', db='postgres', host='localhost', pg_user='postgres',
                        pg_password='admin')
geo.publish_featurestore(workspace='demo', store_name='geo_data', pg_table='geodata_table_name')

# For uploading SLD file and connect it with layer
geo.upload_style(path=r'path\to\sld\file.sld', workspace='demo')
geo.publish_style(layer_name='geoserver_layer_name', style_name='sld_file_name', workspace='demo')

# delete workspace
geo.delete_workspace(workspace='demo')

# delete layer
geo.delete_layer(layer_name='layer1', workspace='demo')

# delete style file
geo.delete_style(style_name='style1', workspace='demo')
```

To create the dynamic style you need to install the extra dependencies as, `gdal`, `seaborn` and `matplotlib`. The below functions will be only available after installing the full package `geoserver-rest[all]` or `geoserver-rest[style]`,

```python
# For creating the style file for raster data dynamically and connect it with layer
geo.create_coveragestyle(raster_path=r'path\to\raster\file.tiff', style_name='style_1', workspace='demo',
                         color_ramp='RdYiGn')
geo.publish_style(layer_name='geoserver_layer_name', style_name='raster_file_name', workspace='demo')

# For creating outline featurestyle
geo.create_outline_featurestyle(style_name='style1', color='#ff0000')

```

## Contribution

Geoserver-rest is the open source library written in python and contributors are needed to keep this library moving forward. Any kind of contributions are welcome. Here are the basic rule for the new contributors:

1. Please use the request library for the http request.
2. One feature per pull request (If the PR is huge, you need to create a issue and discuss).
3. Please add the update about your PR on the [change log documentation](https://github.com/gicait/geoserver-rest/blob/master/docs/source/change_log.rst#master-branch) as well.

## Citation

Full paper is available here: https://doi.org/10.5194/isprs-archives-XLVI-4-W2-2021-91-2021

```
@Article{isprs-archives-XLVI-4-W2-2021-91-2021,
      AUTHOR = {Tek Bahadur Kshetri, Angsana Chaksana and Shraddha Sharma},
      TITLE = {THE ROLE OF OPEN-SOURCE PYTHON PACKAGE GEOSERVER-REST IN WEB-GIS DEVELOPMENT},
      JOURNAL = {The International Archives of the Photogrammetry, Remote Sensing and Spatial Information Sciences},
      VOLUME = {XLVI-4/W2-2021},
      YEAR = {2021},
      PAGES = {91--96},
      URL = {https://www.int-arch-photogramm-remote-sens-spatial-inf-sci.net/XLVI-4-W2-2021/91/2021/},
      DOI = {10.5194/isprs-archives-XLVI-4-W2-2021-91-2021}
  }
```
