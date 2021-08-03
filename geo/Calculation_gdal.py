import os

try:
    from osgeo import gdal  # noqa
except ImportError:
    import gdal  # noqa


def raster_value(path):
    file = os.path.basename(path)
    file_format = os.path.splitext(file)[1]
    file_name = file.split(".")[0]
    valid_extension = ['.tif', '.gtiff']

    if file_format.lower() in valid_extension:
        gtif = gdal.Open(path)
        srcband = gtif.GetRasterBand(1)
        srcband.ComputeStatistics(0)
        n = srcband.GetMaximum() - srcband.GetMinimum() + 1
        n = int(n)
        min_value = srcband.GetMinimum()
        max_value = srcband.GetMaximum()
        result = {"N": n, "min": min_value, "max": max_value, "file_name": file_name}
        return result

    else:
        print("sorry, file format is incorrect")
