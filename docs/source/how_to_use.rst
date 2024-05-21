How to use
===========

This library is built for getting, creating, updating and deleting workspaces, coveragestores, featurestores, and styles. Some examples are shown below.

Getting started with `geoserver-rest`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This following step is used to initialize the library. It takes parameters as geoserver url, username, password.

.. code-block:: python

    from geo.Geoserver import Geoserver
    geo = Geoserver('http://127.0.0.1:8080/geoserver', username='admin', password='geoserver')

Creating workspaces
-------------------

.. code-block:: python

    geo.create_workspace(workspace='demo')

Creating coveragestores
-----------------------

It is helpful for publishing the raster data to the geoserver. Here if you don't pass the ``lyr_name`` parameter, it will take the raster file name as the layer name.

.. code-block:: python

    geo.create_coveragestore(layer_name='layer1', path=r'path\to\raster\file.tif', workspace='demo')


.. note::
    If your raster is not loading correctly, please make sure you assign the coordinate system for your raster file.

    If the ``layer_name`` already exists in geoserver, it will automatically overwrite the previous one.


Creating and publishing featurestores and featurestore layers
-------------------------------------------------------------

.. _create_featurestore:

It is used for connecting the ``PostGIS`` with geoserver and publish this as a layer. It is only useful for vector data. The postgres connection parameters should be passed as the parameters. For publishing the PostGIS tables, the ``pg_table`` parameter represent the table name in postgres

.. code-block:: python3

    geo.create_featurestore(store_name='geo_data', workspace='demo', db='postgres', host='localhost', pg_user='postgres', pg_password='admin')
    geo.publish_featurestore(workspace='demo', store_name='geo_data', pg_table='geodata_table_name')


The new function ``publish_featurestore_sqlview`` is available from geoserver-rest version ``1.3.0``. The function can be run by using following command,

.. code-block:: python3

    sql = 'SELECT name, id, geom FROM post_gis_table_name'
    geo.publish_featurestore_sqlview(store_name='geo_data', name='view_name', sql=sql, key_column='name', workspace='demo')


Creating and publishing shapefile datastore layers
--------------------------------------------------

The ``create_shp datastore`` function will be useful for uploading the shapefile and publishing the shapefile as a layer. This function will upload the data to the geoserver ``data_dir`` in ``h2`` database structure and publish it as a layer. The layer name will be same as the shapefile name.

.. code-block:: python3

    geo.create_shp_datastore(path=r'path/to/zipped/shp/file.zip', store_name='store', workspace='demo')

Creating and publishing datastore layers
----------------------------------------

The ``create_datastore`` function will create the datastore for the specific data. After creating the datastore, you need to publish it as a layer by using ``publish_featurestore`` function. It can take the following type of data path:

1. Path to shapefile (`.shp`) file;
2. Path to GeoPackage (`.gpkg`) file;
3. WFS url (e.g. http://localhost:8080/geoserver/wfs?request=GetCapabilities) or;
4. Directory containing shapefiles.

If you have PostGIS datastore, please use :ref:`create_featurestore <create_featurestore>` function.

.. code-block:: python3

    geo.create_datastore(name="ds", path=r'path/to/shp/file_name.shp', workspace='demo')
    geo.publish_featurestore(workspace='demo', store_name='ds', pg_table='file_name')

If your data is coming from ``WFS`` url, then use this,

.. code-block:: python3

    geo.create_datastore(name="ds", path='http://localhost:8080/geoserver/wfs?request=GetCapabilities', workspace='demo')
    geo.publish_featurestore(workspace='demo', store_name='ds', pg_table='wfs_layer_name')


Creating Layer Groups
-------------------------------
A layer group is a grouping of layers and styles that can be accessed as a single layer in a WMS GetMap request.
Layer groups can be created either inside a workspace, or globally without a workspace.

You can create a layer group from layers that have been uploaded previously with the ``create_layergroup`` method.

.. code-block:: python3

  # create a new layergroup from 2 existing layers
    geo.create_layergroup(
      name = "my_fancy_layergroup",
      mode = "single",
      title = "My Fancy Layergroup Title",
      abstract_text = "This is a very fancy Layergroup",
      layers = ["fancy_layer_1", "fancy_layer_2"],
      workspace = "my_space", #None if you want to create a layergroup outside the workspace
      keywords = ["list", "of", "keywords"]
      )

  # add another layer
    geo.add_layer_to_layergroup(
      layergroup_name = "my_fancy_layergroup",
      layergroup_workspace = "my_space",
      layer_name = "superfancy_layer",
      layer_workspace = "my_space"
    )

  # remove a layer
    geo.remove_layer_from_layergroup(
      layergroup_name = "my_fancy_layergroup",
      layergroup_workspace = "my_space",
      layer_name = "superfancy_layer",
      layer_workspace = "my_space"
    )


Uploading and publishing styles
-------------------------------

It is used for uploading ``SLD`` files and publish style. If the style name already exists, you can pass the parameter ``overwrite=True`` to overwrite it. The name of the style will be name of the uploaded file name.

Before uploading ``SLD`` file, please check the version of your sld file. By default the version of sld will be ``1.0.0``. As I noticed, by default the QGIS will provide the .sld file of version ``1.0.0`` for raster data version ``1.1.0`` for vector data.


.. code-block:: python3

    geo.upload_style(path=r'path\to\sld\file.sld', workspace='demo')
    geo.publish_style(layer_name='geoserver_layer_name', style_name='sld_file_name', workspace='demo')

Creating and applying dynamic styles based on the raster coverages
------------------------------------------------------------------

It is used to create the style file for raster data. You can get the ``color_ramp`` name from `matplotlib colormaps <https://matplotlib.org/3.3.0/tutorials/colors/colormaps.html>`_. By default ``color_ramp='RdYlGn'`` (red to green color ramp).

.. code-block:: python

    geo.create_coveragestyle(raster_path=r'path\to\raster\file.tiff', style_name='style_1', workspace='demo', color_ramp='RdBu_r')
    geo.publish_style(layer_name='geoserver_layer_name', style_name='raster_file_name', workspace='demo')


.. note::
    If you have your own custom color and the custom label, you can pass the ``values:color`` pair as below to generate the map with dynamic legend.


.. code-block:: python

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

    # you can also pass this list of color if you have your custom colors for the ``color_ramp``
    '''
    geo.create_coveragestyle(raster_path=r'path\to\raster\file.tiff',
                                style_name='style_3',
                                workspace='demo',
                                color_ramp=[#ffffff, #453422,  #f0f0f0, #aaaaaa],
                                cmap_type='values')
    '''
    geo.publish_style(layer_name='geoserver_layer_name', style_name='raster_file_name', workspace='demo')

For generating the style for ``classified raster``, you can pass the another parameter called ``cmap_type='values'`` as,


.. code-block:: python

    geo.create_coveragestyle(raster_path=r'path\to\raster\file.tiff', style_name='style_1', workspace='demo', color_ramp='RdYiGn', cmap_type='values')


.. list-table:: Options for ``create_coveragestyle``
    :widths: 15 15 15 55
    :header-rows: 1

    * - Option
      - Type
      - Default
      - Description

    * - style_name
      - string
      - file_name
      - This is optional field. If you don't pass the style_name parameter, then it will take the raster file name as the default name of style in geoserver

    * - raster_path
      - path
      - None
      - path to the raster file (Required)

    * - workspace
      - string
      - None
      - The name of the workspace. Optional field. It will take the default workspace of geoserver if nothing is provided

    * - color_ramp
      - string, list, dict
      - RdYiGn
      - The color ramp name. The name of the color ramp can be found here in `matplotlib colormaps <https://matplotlib.org/3.3.0/tutorials/colors/colormaps.html>`_

    * - overwrite
      - boolean
      - False
      - For overwriting the previous style file in geoserver


Creating feature styles
-----------------------

It is used for creating the style for ``point``, ``line`` and ``polygon`` dynamically. It currently supports three different types of feature styles:

1. ``Outline featurestyle``: For creating the style which have only boundary color but not the fill style
2. ``Catagorized featurestyle``: For creating catagorized dataset
3. ``Classified featurestyle``: Classify the input data and style it: (For now, it only supports polygon geometry)

.. code-block:: python

    geo.create_outline_featurestyle(style_name='new_style', color="#3579b1", geom_type='polygon', workspace='demo')
    geo.create_catagorized_featurestyle(style_name='name_of_style', column_name='name_of_column', column_distinct_values=[1,2,3,4,5,6,7], workspace='demo')
    geo.create_classified_featurestyle(style_name='name_of_style', column_name='name_of_column', column_distinct_values=[1,2,3,4,5,6,7], workspace='demo')

.. note::

    * The ``geom_type`` must be either ``point``, ``line`` or ``polygon``.
    * The ``color_ramp`` name can be obtained from `matplotlib colormaps <https://matplotlib.org/3.3.0/tutorials/colors/colormaps.html>`_.

The options for creating categorized/classified `featurestyles` are as follows,

.. list-table:: Options for ``create_catagorized_featurestyle`` and ``create_classified_featurestyle``
    :widths: 15 15 15 55
    :header-rows: 1

    * - Option
      - Type
      - Default
      - Description

    * - style_name
      - string
      - file_name
      - This is optional field. If you don't pass the style_name parameter, then it will take the raster file name as the default name of style in geoserver

    * - column_name
      - string
      - None
      - The name of the column, based on which the style will be generated

    * - column_distinct_values
      - list/array
      - None
      - The column distinct values based on which the style will be applied/classified. This option is only available for ``create_classified_featurestyle``

    * - workspace
      - string
      - None
      - The name of the workspace. Optional field. It will take the default workspace of geoserver if nothing is provided

    * - color_ramp
      - string
      - RdYiGn
      - The color ramp name. The name of the color ramp can be found here in `matplotlib colormaps <https://matplotlib.org/3.3.0/tutorials/colors/colormaps.html>`_

    * - geom_type
      - string
      - polygon
      - The geometry type, available options are ``point``, ``line`` or ``polygon``

    * - outline_color
      - color hex value
      - '#3579b1'
      - The outline color of the polygon/line

    * - overwrite
      - boolean
      - False
      - For overwriting the previous style file in geoserver


Deletion requests examples
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

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


Some get request examples
^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    # get geoserver version
    version = geo.get_version()
    print(version)

    # get ststem info
    status = geo.get_status()
    system_status = geo.get_system_status()

    # get workspace
    workspace = geo.get_workspace(workspace='workspace_name')

    # get default workspace
    dw = geo.get_default_wokspace()

    # get all the workspaces
    workspaces = geo.get_workspaces()

    # get datastore
    datastore = geo.get_datastore(store_name='store')

    # get all the datastores
    datastores = geo.get_datastores()

    # get coveragestore
    cs = geo.get_coveragestore(coveragestore_name='cs')

    # get all the coveragestores
    css = geo.get_coveragestores()

    # get layer
    layer = geo.get_layer(layer_name='layer_name')

    # get all the layers
    layers = geo.get_layers()

    # get layergroup
    layergroup = geo.get_layergroup('layergroup_name')

    # get all the layers
    layergroups = geo.get_layergroups()

    # get style
    style = geo.get_style(style_name='style_name')

    # get all the styles
    styles = geo.get_styles()

    # get featuretypes
    featuretypes = geo.get_featuretypes(store_name='store_name')

    # get feature attribute
    fa = geo.get_feature_attribute(feature_type_name='ftn', workspace='ws', store_name='sn')

    # get feature store
    fs = geo.get_featurestore(store_name='sn', workspace='ws')


Special functions
^^^^^^^^^^^^^^^^^

.. code-block:: python

    # Reloads the GeoServer catalog and configuration from disk. This operation is used in cases where an external tool has modified the on-disk configuration. This operation will also force GeoServer to drop any internal caches and reconnect to all data stores.
    geo.reload()

    # Resets all store, raster, and schema caches. This operation is used to force GeoServer to drop all caches and store connections and reconnect to each of them the next time they are needed by a request. This is useful in case the stores themselves cache some information about the data structures they manage that may have changed in the meantime.
    geo.reset()

    # set default workspace
    geo.set_default_workspace(workspace='workspace_name')



Global parameters for most functions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The following parameters are common to most functions/methods:

* ``workspace``: If workspace is not provided, the function will take the ``default`` workspace.
* ``overwrite``: This parameter takes only the boolean value. In most of the create method, the ``overwrite`` parameter is available. The default value is ``False``. But if you set it to True, the method will be in update mode.
