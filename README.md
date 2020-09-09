# Documentation

### Installation
```bash
pip install wheel
pip install pipwin
pipwin install gdal

pip install geoserver-rest
```

### How to use
This library is used for creating workspace, coveragestore, featurestore, styles. Some of the examples are shown below.

##### Initialize the library
This step is used to initialize the library. It takes parameters as geoserver url, username, password.

```python
from geo.Geoserver import Geoserver
geo = Geoserver('http://localhost:8080/geoserver', username='admin', password='geoserver')
```

##### Create workspace
```python
geo.create_workspace('demo')
```

##### Create coveragestore
It is helpful for publishing the **raster data** to the geoserver. Here if you forgot to pass the `lyr_name` parameter, it will take the raster file name as the layer name. 

```python
geo.create_coveragestore(lyr_name='layer' path=r'path\to\raster\file.tif', workspace='demo')
```

##### Create featurestore and publish layer
It is use for connecting the **PostGIS** with geoserver and publish this as a layer. It is only use for **vector data**.

```python
geo.create_featurestore(store_name='geo_data', workspace='demo', db='postgres', host='localhost', pg_user='postgres', pg_password='admin')
geo.publish_featurestore(workspace='demo', store_name='geo_data', pg_table='geodata_table_name')
```

##### Upload style and publish it
It is use for uploading **SLD** files and publish style
```python
geo.upload_style(path=r'path\to\sld\file.sld', workspace='demo')
geo.publish_style(layer_name='geoserver_layer_name', style_name='sld_file_name', workspace='demo')
```


##### Create Coverage Style based on the raster (Dynamic) and apply style
It is use to create the style file for **raster data**. You can get the color_ramp name from [matplotlib colormaps](https://matplotlib.org/3.3.0/tutorials/colors/colormaps.html).

```python
#Style name will be the same as the raster_file_name
geo.create_coveragestyle(raster_path=r'path\to\raster\file.tiff', style_name='style_1', workspace='demo', color_ramp='RdYiGn')
geo.publish_style(layer_name='geoserver_layer_name', style_name='raster_file_name', workspace='demo')
```

##### Create featur style
It is use for creating the style for point, line, polygon dynamically. Currently it supports three different type of feature styles,

1. Outline featurestyle: For only outline color
2. Catagorized featurestyle: For creating catagorized dataset
3. Classified featurestyle: Classify the input data and style it

**Note:** 
* The geom_type must be `point` or `line` or `polygon`
* The `color_ramp` name can be get from [matplotlib colormaps](https://matplotlib.org/3.3.0/tutorials/colors/colormaps.html).

```python
geo.create_outline_featurestyle(style_name='new_style' color="#3579b1" geom_type='polygon', workspace='demo')
geo.create_catagorized_featurestyle(column_name='name_of_column', column_distinct_values=[1,2,3,4,5,6,7], workspace='demo', color_ramp='tab20', geom_type='polygon', outline_color='#000000')

```