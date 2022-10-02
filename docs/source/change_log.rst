Change Log
=============

``Master branch``
^^^^^^^^^^^^^^^^^
* Fix the import issue, close `#76 <https://github.com/gicait/geoserver-rest/issues/76>`_
* Removed the ``rest`` from Geoserver class URL, Revert back to previous state. Close `#77 <https://github.com/gicait/geoserver-rest/issues/76>`_
* Added header to fix issue `https://github.com/gicait/geoserver-rest/issues/86`

``[v2.3.0 - 2022-05-06]``
^^^^^^^^^^^^^^^^^^^^^^^^^^
* Params for `delete_workspace` and `delete_style` changed to `{recursive: true}`
* Added methods to use REST API for user/group service CRUD operations.
* Removed ``key_column`` parameter and added ``srid`` parameter (coordinate system of the layer, default is 4326) from ``publish_featurestore_sqlview`` function
* Solved the Bug `#73 <https://github.com/gicait/geoserver-rest/issues/73>`_ and `#69 <https://github.com/gicait/geoserver-rest/issues/69>`_
* ``create_layergroup`` function added
* ``update_layergroup`` function added
* ``delete_layergroup`` function added
*  Added layer and workspace checks to layergroup methods


``[V2.1.2 - 2021-10-14]``
^^^^^^^^^^^^^^^^^^^^^^^^^
* ``create_featurestore`` bug on Expose primary key fixed close #56.
* ``create_featurestore`` will now support all the options from geoserver.


``[V2.0.0 - 2021-08-14]``
^^^^^^^^^^^^^^^^^^^^^^^^^^

* Expose primary key option for datastore in ``create_featurestore`` function
* Time dimention support for the coverage store
* Bug fixing for the ``.tiff`` datastore
* Added the request.content to error messages in order to get more information about error


``[V2.0.0 - 2021-05-28]``
^^^^^^^^^^^^^^^^^^^^^^^^^^

* Fully replaced the `pycurl <http://pycurl.io/>`_ dependency with `request` and `psycopg2 <https://www.psycopg.org/>`_
* Dropped the PostgreSQL functionalities (deleted ``geo/Postgres.py`` file). I think the functionalities of PostgreSQL is outside the scope of this library. So I initiated the seperated library `postgres-helper <https://postgres-helper.readthedocs.io/en/latest/>`_
* Documentation adjustments
* The ``overwrite`` options removed from ``create_coveragestore``, ``create_coveragestyle`` and other style functions


``[V1.6.0 - 2021-04-13]``
^^^^^^^^^^^^^^^^^^^^^^^^^^

* Documentation adjustments (bunch of Sphinx-docs formatting fixes and English corrections)
* Add black and pre-commit
* ``create_coveragestore`` function parameter name ``lyr_name`` changed to ``layer_name``
* Pytest examples, docstrings and typed calls added


``[V1.5.2] - 2020-11-03``
^^^^^^^^^^^^^^^^^^^^^^^^^

* **1. create_datastore** This function can create the datastore from `.shp`, `.gpkg`, WFS url and directory containing `.shp`.
* **2. create_shp_datastore** This function will be useful for uploading the shapefile and publishing the shapefile as a layer. This function will upload the data to the geoserver ``data_dir`` in ``h2`` database structure and publish it as a layer.
* Update on docs
