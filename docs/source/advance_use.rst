Advance use for automation
============================

The following code will first convert all the ``.rst`` data format inside ``C:\Users\gic\Desktop\etlIa\`` folder, into ``tiff`` format and then upload all the ``tiff`` files to the GeoServer.


.. code-block:: python3

    from geo.Geoserver import Geoserver
    from osgeo import gdal
    import glob
    import os

    geo = Geoserver('http://localhost:8080/geoserver', username='admin', password='geoserver')

    rst_files = glob.glob(r'C:\Users\gic\Desktop\etlIa\*.rst')
    # geo.create_workspace('geonode')

    for rst in rst_files:
        file_name = os.path.basename(file_name)
        src = gdal.Open(rst)
        tiff = r'C:\Users\tek\Desktop\try\{}'.format(file_name)
        gdal.Translate(tiff, src)
        geo.create_coveragestore(lyr_name=file_name, path=tiff, workspace='geonode')    #, overwrite=True