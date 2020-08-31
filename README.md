# Documentation

### Installation
```bash
pip install wheel
pip install pipwin
pipwin install gdal

pip install geoserver-rest-python
```

### How to use
This library is used for creating workspace, coveragestore, featurestore, styles. Some of the examples are shown below.

##### Initialize the library
This step is used to initialize the library. It takes parameters as geoserver url, username, password.

```python
geo = Geoserver('http://localhost:8080/geoserver', username='admin', password='geoserver')
```

##### Create workspace
```python
geo.create_workspace('demo')
```

##### Create coveragestore
It is helpful for publishing the **raster data** to the geoserver

```python
geo.create_coveragestore(path=r'path\to\raster\file.tif', workspace='demo')
```

##### Create featurestore and publish layer
It is use for connecting the **PostGIS** with geoserver and publish this as a layer. It is only use for **vector data**

```python
geo.create_featurestore(store='geo_data', workspace='demo', db='postgres', host='localhost', pg_user='postgres', pg_password='admin')
geo.publish_featurestore(workspace='demo', store='geo_data', pg_table='geodata_table_name')
```

##### Upload style and publish it
It is use for uploading **SLD** files and publish style
```python
geo.upload_coveragestyle(path=r'path\to\sld\file.sld', workspace='demo')
geo.publish_style(layer_name='geoserver_layer_name', style_name='sld_file_name', workspace='demo')
```


##### Create Coverage Style based on the raster (Dynamic) and apply style
It is use to create the style file for **raster data**.

```python
#Style name will be the same as the raster_file_name
geo.create_coveragestyle(raster_path=r'path\to\raster\file.tiff', workspace='demo')
geo.publish_style(layer_name='geoserver_layer_name', style_name='raster_file_name', workspace='demo')
```