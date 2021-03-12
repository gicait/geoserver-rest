[![Downloads](https://pepy.tech/badge/geoserver-rest)](https://pepy.tech/project/geoserver-rest)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

### Full documentation

The documentation for this project is moved here: [https://geoserver-rest.readthedocs.io/](https://geoserver-rest.readthedocs.io/).

### Overview

The `geoserver-rest` package is useful for the management of geospatial data in [GeoServer](http://geoserver.org/). The package is useful for the creating, updating and deleting geoserver workspaces, stores, layers, and style files.

### Installation

```python
conda install -c conda-forge geoserver-rest
```

For the `pip` installation, check the [official documentation of geoserver-rest](https://geoserver-rest.readthedocs.io/en/latest/installation.html)

### Some examples

Please check the [https://geoserver-rest.readthedocs.io/](https://geoserver-rest.readthedocs.io/) for full documentation.

```python
# Import the library
from geo.Geoserver import Geoserver

# Initialize the library
geo = Geoserver('http://127.0.0.1:8080/geoserver', username='admin', password='geoserver')

# For creating workspace
geo.create_workspace(workspace='demo')

# For uploading raster data to the geoserver
geo.create_coveragestore(lyr_name='layer1', path=r'path\to\raster\file.tif', workspace='demo')

# For creating postGIS connection and publish postGIS table
geo.create_featurestore(store_name='geo_data', workspace='demo', db='postgres', host='localhost', pg_user='postgres', pg_password='admin')
geo.publish_featurestore(workspace='demo', store_name='geo_data', pg_table='geodata_table_name')

# For uploading SLD file and connect it with layer
geo.upload_style(path=r'path\to\sld\file.sld', workspace='demo')
geo.publish_style(layer_name='geoserver_layer_name', style_name='sld_file_name', workspace='demo', sld_version='1.0.0')

# For creating the style file for raster data dynamically and connect it with layer
geo.create_coveragestyle(raster_path=r'path\to\raster\file.tiff', style_name='style_1', workspace='demo', color_ramp='RdYiGn')
geo.publish_style(layer_name='geoserver_layer_name', style_name='raster_file_name', workspace='demo')

# delete workspace
geo.delete_workspace(workspace='demo')

# delete layer
geo.delete_layer(layer_name='agri_final_proj', workspace='demo')

# delete style file
geo.delete_style(style_name='kamal2', workspace='demo')
```

### Contribution

Geoserver-rest is the open source library written in python and contributors are needed to keep this library moving forward. Any kind of contributions are welcome.

### Acknowledgements

Created and managed by [Tek Bahadur Kshetri](http://tekkshetri.com.np/) for the activites of Geoinformatics Center of Asian Institute of Technology, Thailand.
