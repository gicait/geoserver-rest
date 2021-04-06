import os
from tempfile import mkstemp
from typing import Dict
from zipfile import ZipFile


def prepare_zip_file(name: str, data: Dict) -> str:
    """Creates a zip file from

    GeoServer's REST API uses ZIP archives as containers for file formats such
    as Shapefile and WorldImage which include several 'boxcar' files alongside
    the main data.  In such archives, GeoServer assumes that all of the relevant
    files will have the same base name and appropriate extensions, and live in
    the root of the ZIP archive.  This method produces a zip file that matches
    these expectations, based on a basename, and a dict of extensions to paths or
    file-like objects. The client code is responsible for deleting the zip
    archive when it's done.

    Parameters
    ----------
    name : name of files
    data : dict

    Returns
    -------
    str
    """
    fd, path = mkstemp()
    zip_file = ZipFile(path, "w", allowZip64=True)
    print(fd, path, zip_file, data)
    for ext, stream in data.items():
        fname = "{}.{}".format(name, ext)
        if isinstance(stream, str):
            zip_file.write(stream, fname)
        else:
            zip_file.writestr(fname, stream.read())
    zip_file.close()
    os.close(fd)
    return path
