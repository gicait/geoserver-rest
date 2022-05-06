import os

try:
    from osgeo import gdal  # noqa
except ImportError:
    import gdal  # noqa


def raster_value(path: str) -> dict:
    file = os.path.basename(path)
    file_format = os.path.splitext(file)[1]
    file_name = file.split(".")[0]
    valid_extension = [".tif", ".tiff", ".gtiff"]

    if file_format.lower() in valid_extension:
        try:
            gtif = gdal.Open(path)
            srcband = gtif.GetRasterBand(1)
            srcband.ComputeStatistics(0)
            n = srcband.GetMaximum() - srcband.GetMinimum() + 1
            n = int(n)
            min_value = srcband.GetMinimum()
            max_value = srcband.GetMaximum()
            result = {
                "N": n,
                "min": min_value,
                "max": max_value,
                "file_name": file_name,
            }
            return result
        except Exception as error:
            print("An error occured when computing band statistics: ", error)
            raise error

    else:
        print("sorry, file format is incorrect")
