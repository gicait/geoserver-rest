How to use
===========

This library is used for get, create, update and delete workspace, coveragestore, featurestore, styles. Some of the examples are shown below.

Some global parameters for most of the functions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Here is the list of the parameters/consideration for this library,

* **workspace:** If workspace is not provided, the function will take the default workspace.
* **overwrite:** This parameter takes only the boolean value. In most of the create method, the `overwrite` parameter is available. The default value is False. But if you set it to True, the method will be in update mode. 

Getting start with geoserver-rest
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This following step is used to initialize the library. It takes parameters as geoserver url, username, password.

.. code-block:: python3

    from geo.Geoserver import Geoserver
    geo = Geoserver('http://127.0.0.1:8080/geoserver', username='admin', password='geoserver')

Create workspace
-----------------

.. code-block:: python3

    geo.create_workspace(workspace='demo')


Create coveragestore
---------------------

It is helpful for publishing the raster data to the geoserver. Here if you don't pass the lyr_name parameter, it will take the raster file name as the layer name.

.. code-block:: python3

    geo.create_coveragestore(lyr_name='layer1', path=r'path\to\raster\file.tif', workspace='demo')


**Note:** If your raster is not loading correctly, please make sure you assign the coordinate system for your raster file.

If the layername already exists in geoserver, you can pass another parameter overwrite=True,

.. code-block:: python3

    geo.create_coveragestore(lyr_name='layer1', path=r'path\to\raster\file.tif', workspace='demo', overwrite=True)


Create featurestore and publish layer
---------------------------------------

It is used for connecting the PostGIS with geoserver and publish this as a layer. It is only useful for vector data. The postgres connection parameters should be passed as the parameters. For publishing the PostGIS tables, the pg_table parameter represent the table name in postgres

.. code-block:: python3

    geo.create_featurestore(store_name='geo_data', workspace='demo', db='postgres', host='localhost', pg_user='postgres', pg_password='admin')
    geo.publish_featurestore(workspace='demo', store_name='geo_data', pg_table='geodata_table_name')


The new function publish_featurestore_sqlview is available from geoserver-rest version 1.3.0. The function can be run by using following command,

.. code-block:: python3

    sql = 'SELECT name, id, geom FROM post_gis_table_name'
    geo.publish_featurestore_sqlview(store_name='geo_data', name='view_name', sql=sql, key_column='name', workspace='demo')


Upload style and publish it
---------------------------------------

It is used for uploading SLD files and publish style. If the style name already exists, you can pass the parameter overwrite=True to overwrite it. The name of the style will be name of the uploaded file name.

Before uploading SLD file, please check the version of your sld file. By default the version of sld will be 1.0.0. As I noticed, by default the QGIS will provide the .sld file of version 1.0.0 for raster data version 1.1.0 for vector data.


.. code-block:: python3

    geo.upload_style(path=r'path\to\sld\file.sld', workspace='demo')
    geo.publish_style(layer_name='geoserver_layer_name', style_name='sld_file_name', workspace='demo', sld_version='1.0.0')



Create Coverage Style based on the raster (Dynamic) and apply style
--------------------------------------------------------------------

It is used to create the style file for raster data. You can get the color_ramp name from `matplotlib colormaps <https://matplotlib.org/3.3.0/tutorials/colors/colormaps.html>`_. By default color_ramp='RdYlGn' (red to green color ramp).

.. code-block:: python3

    geo.create_coveragestyle(raster_path=r'path\to\raster\file.tiff', style_name='style_1', workspace='demo', color_ramp='RdYiGn')
    geo.publish_style(layer_name='geoserver_layer_name', style_name='raster_file_name', workspace='demo')



**Note:** If you have your own custom color and the custom label, you can pass the values:color pair as below to generate the map with dynamic legend, 


.. code-block:: python3

    c_ramp = {
        'label 1 value': '#ffff55',
        'label 2 value': '#505050',
        'label 3 value': '#404040',
        'label 4 value': '#333333'
    }
    geo.create_coveragestyle(raster_path=r'path\to\raster\file.tiff',
                                style_name='style_2',
                                workspace='demo',
                                color_ramp=c_ramp,
                                cmap_type='values')

    # you can also pass this list of color if you have your custom colors for the color_ramp
    '''
    geo.create_coveragestyle(raster_path=r'path\to\raster\file.tiff',
                                style_name='style_3',
                                workspace='demo',
                                color_ramp=[#ffffff, #453422,  #f0f0f0, #aaaaaa],
                                cmap_type='values')
    '''
    geo.publish_style(layer_name='geoserver_layer_name', style_name='raster_file_name', workspace='demo')




For generating the style for classified raster, you can pass the another parameter called cmap_type='values' as,

.. code-block:: python3

    geo.create_coveragestyle(raster_path=r'path\to\raster\file.tiff', style_name='style_1', workspace='demo', color_ramp='RdYiGn', cmap_type='values')


| Option      | Type               | Default   | Description                                                                                                                                               |
| ----------- | ------------------ | --------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| style_name  | string             | file_name | This is optional field. If you don't pass the style_name parameter, then it will take the raster file name as the default name of style in geoserver      |
| raster_path | path               | None      | path to the raster file                                                                                                                                   |
| workspace   | string             | None      | The name of the workspace                                                                                                                                 |
| color_ramp  | string, list, dict | RdYlGn    | The color ramp name. The name of the color ramp can be found here in [matplotlib colormaps](https://matplotlib.org/3.3.0/tutorials/colors/colormaps.html) |
| cmap_type   | string             | ramp      | By default the continuous style will be generated, If you want to generate the style for classified raster then pass the parameter `color_ramp='values'`  |
| overwrite   | boolean            | False     | For overwriting the previous style file in geoserver    


Create featur style
----------------------

It is used for creating the style for point, line and polygon dynamically. Currently, it supports three different types of feature styles,

1. Outline featurestyle: For creating the style which have only boundary color but not the fill style
2. Catagorized featurestyle: For creating catagorized dataset
3. Classified featurestyle: Classify the input data and style it: (For now, it only supports polygon geometry)



.. code-block:: python3

    geo.create_outline_featurestyle(style_name='new_style' color="#3579b1" geom_type='polygon', workspace='demo')
    geo.create_catagorized_featurestyle(style_name='name_of_style', column_name='name_of_column', column_distinct_values=[1,2,3,4,5,6,7], workspace='demo')
    geo.create_classified_featurestyle(style_name='name_of_style' column_name='name_of_column', column_distinct_values=[1,2,3,4,5,6,7], workspace='demo')



**Note:**

* The geom_type must be either`point`,`line` or `polygon`.
*  The `color_ramp` name can be obtained from `matplotlib colormaps <https://matplotlib.org/3.3.0/tutorials/colors/colormaps.html>`_.

The options for creating catagorized/classified featurestyle are as follows,

| Option                 | Type            | Default   | Description                                                                                                                                               |
| ---------------------- | --------------- | --------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| style_name             | string          | None      | The name of the style file in geoserver                                                                                                                   |
| column_name            | string          | None      | The name of the column, based on which the style will be generated                                                                                        |
| column_distinct_values | list/array      | None      | The column distinct values based on which the style will be applied/classified                                                                            |
| workspace              | string          | None      | The name of the workspace                                                                                                                                 |
| color_ramp             | string          | RdYlGn    | The color ramp name. The name of the color ramp can be found here in [matplotlib colormaps](https://matplotlib.org/3.3.0/tutorials/colors/colormaps.html) |
| geom_type              | string          | polygon   | The geometry type, available options are `point`, `line` or `polygon`                                                                                     |
| outline_color          | color hex value | '#3579b1' | The outline color of the polygon/line                                                                                                                     |
| overwrite              | boolean         | False     | For overwriting the previous style file in geoserver    



Some of the delete request examples
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python3

    # delete workspace
    geo.delete_workspace(workspace='demo')

    # delete layer
    geo.delete_layer(layer_name='agri_final_proj', workspace='demo')

    # delete feature store, i.e. remove postgresql connection
    geo.delete_featurestore(featurestore_name='ftry', workspace='demo')

    # delete coveragestore, i.e. delete raster store
    geo.delete_coveragestore(coveragestore_name='agri_final_proj', workspace='demo')

    # delete style file
    geo.delete_style(style_name='kamal2', workspace='demo')




